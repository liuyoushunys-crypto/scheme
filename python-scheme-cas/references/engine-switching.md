# CAS 引擎管理器 (`eval/eval_cas_engine.py`) 参考

## 架构

```
用户层:  (use-engine 'auto|'symengine|'sympy)
                   │
                   ▼
         eval_cas_engine.py
         ┌─────────────────────────┐
         │  _current_engine        │  ← 'auto', 'symengine', 'sympy'
         │  _engine_cache = {}     │  ← 惰性缓存
         │                         │
         │  get_engine() → module  │  ← 返回当前引擎（统一接口）
         │  call(name, *args)      │  ← 智能调度
         └─────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    symengine 0.14.1    sympy 1.14.0
    (fast C++ core)     (full CAS)
```

## 引擎能力矩阵

| 操作               | symengine | sympy |
|--------------------|:---------:|:-----:|
| Symbol/算术        | ✅        | ✅    |
| diff / expand / series | ✅    | ✅    |
| sin/cos/tan/sqrt/log/exp | ✅  | ✅    |
| Matrix/zeros/ones/eye | ✅    | ✅    |
| Eq/Ne/Lt/Le/Gt/Ge  | ✅        | ✅    |
| lambdify           | ✅        | ✅    |
| **factor/simplify** | ❌       | ✅    |
| **subs/solve**     | ❌        | ✅    |
| **integrate/limit** | ❌       | ✅    |
| **det/inv**        | ❌        | ✅    |
| **dsolve/laplace/fourier** | ❌ | ✅    |

## `get_engine()` 实现

```python
def get_engine():
    if _current_engine == 'auto':
        se = _get_symengine()
        if se is not None:
            return se                           # symengine 优先
    elif _current_engine == 'symengine':
        eng = _get_symengine()
        if eng is not None:
            return eng
    eng = _get_sympy()                          # fallback 到 sympy
    if eng is None:
        raise Exception("无 CAS 引擎可用")
    return eng
```

每个引擎只导入一次（`_engine_cache` 字典缓存）。

## 交叉兼容性

symengine 和 sympy 的类型**可以混合使用**：

```python
import symengine, sympy
x_se = symengine.Symbol('x')
x_sp = sympy.Symbol('x')

symengine.expand((x_sp + 1)**2)   # ✅ sympy Symbol → symengine 操作
sympy.factor(x_se**4 - 1)          # ✅ symengine Symbol → sympy 操作
x_se + x_sp                        # ✅ 混合算术 → 2*x (Add 类型)
sympy.sin(x_se)                    # ✅ symengine Symbol → sympy 函数
symengine.series(sympy.sin(x_se), x_se, 0, 5)  # ✅ 混合链
```

因此引擎切换可以在运行时任意进行，无需重启。

## `call(name, *args)` — 智能调度

```python
def call(name, *args):
    # auto/symengine 模式：先试 symengine
    if _current_engine in ('auto', 'symengine'):
        result = _try_symengine(name, *args)
        if result is not None:
            return result
        if _current_engine == 'symengine':
            raise Exception(f"symengine 不支持 '{name}'")
        # auto: symengine 失败 → fallthrough
    sp = _get_sympy()
    func = getattr(sp, name, None)
    return func(*args, **kwargs)
```

目前 `call()` 是预留 API，尚未整合到所有 60+ CAS 原语中。CAS 原语仍通过 `_sympy() → get_engine()` 获取引擎，然后直接调用 `sp.xxx(...)`。

## `RuntimeError` — symengine 陷阱

`math.sin(symengine.Symbol('x'))` 抛 `RuntimeError("Symbol cannot be evaluated.")` **而非** `TypeError`。这会影响 `eval/eval_py_arithmetic.py` 中的算术代理函数。

修复：在 `try_py_unary_math`、`try_py_atan`、以及 `log` 特殊处理的 `except` 子句中添加 `RuntimeError`：

```python
except (TypeError, ValueError, RuntimeError):
    # → fallback to sympy.xxx
```

## `eval_python_import.py` 截断恢复

**问题**: `eval/eval_python_import.py` 被截断为 5 行，模块级代码缩进错误，无法 import。但 `.pyc` 缓存保留完整代码。

**恢复方法**:
1. 从 `__pycache__/eval_python_import.cpython-311.pyc` 用 `marshal.load()` 反编译
2. 通过 `dis` 反汇编提取所有函数签名和 docstring
3. 手写重建完整源代码（390 行）
4. 清理 `__pycache__` 让新 `.py` 生效

**预防**: 该文件是自动编辑的常见目标（其他 agent 可能截断过）。定期 `git status` 检查 `.py` 与 `.pyc` 大小差异可提前发现类似问题。

## 注册链

```python
# primitives/primitives.py
from eval.eval_cas_engine import register_engine_primitives

def register_all(env):
    ...
    register_engine_primitives(env)  # 在 CAS primitives 之后
```

`register_engine_primitives` 注册两个函数：
- `use-engine` — 引擎切换
- `engine-info` — 引擎状态

## 使用示例

```scheme
(engine-info)
;; → "当前引擎: auto
;;    symengine: symengine 0.14.1 ✅
;;    sympy:     sympy 1.14.0 ✅
;;    调度策略: symengine 优先，不支持的操作 → sympy"

(use-engine 'symengine)   → 切换到 symengine
(expand #{(x+1)^2})        → 1 + 2*x + x**2  (symengine type, ~10x faster)

(use-engine 'sympy)        → 切换到 sympy
(factor #{x^4 - 1})        → (x-1)(x+1)(x**2+1)  (sympy type, full CAS)
(solve #{x^2 - 4 = 0} x)  → (-2, 2)
```

### 引擎自动降级代理（本轮新增）

`_EngineProxy` 类（`eval/eval_cas_engine.py`）：auto 模式下使用 `__getattr__` 代理，
symengine 优先，缺失属性自动 fallback 到 sympy。

```python
class _EngineProxy:
    def __getattr__(self, name):
        if _current_engine == 'symengine':
            se = _get_symengine()
            if hasattr(se, name): return getattr(se, name)
            raise AttributeError(...)
        # auto: symengine 优先
        se = _get_symengine()
        if hasattr(se, name): return getattr(se, name)
        # fallback
        sp = _get_sympy()
        if hasattr(sp, name): return getattr(sp, name)
        raise AttributeError(...)
```

优势：37 处 `_sympy().xxx(...)` 调用点零改动，全部享受自动降级。

### 已知限制

1. `call()` 智能调度尚未整合到全部 60+ CAS 原语 — 目前 `eval_py_cas.py` 中每个原语仍通过 `_sympy()` 直接获取引擎，然后调用 `sp.xxx()`。如果引擎不支持某函数（如 symengine+factor），原语会抛 `AttributeError` 而非优雅降级。
2. `(engine-info)` 返回 `Str` 而非 `display` 到 stdout — 需要用 `(display (engine-info))` 查看。
