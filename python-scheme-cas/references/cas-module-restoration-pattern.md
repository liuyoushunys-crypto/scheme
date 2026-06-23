# CAS 模块修复模式 (2026-06-23)

## 文件损坏修复

### 字面 `\n` 修复

当生成脚本使用 `'\\n'.join(lines)` 写入文件时，若 escapes 处理不当会导致文件中出现字面 `\n` 字符串而非真实换行。

诊断：`cat -A file.py` 显示每行末尾有 `\n$` 而非 `$`

修复：
```python
with open(path) as f:
    raw = f.read()
fixed = raw.replace('\\n', '\n')
with open(path, 'w') as f:
    f.write(fixed)
```

### 空 `__init__.py` 修复
当 `__init__.py` 仅含一个换行时需写入标准内容：
```python
"""{mod_name}"""
from .core import register_{mod_name}_primitives
```

### Flat → Package 的双重导出
当扁平 `.py` 被子代理转为包时，`__init__.py` 必须同时导出命名函数和 `register_primitives`：
```python
"""tensor"""
from .core import register_tensor_primitives
from .core import register_primitives
```

## 子代理超时恢复

子代理可能部分写入文件后超时。恢复步骤：
1. 检查文件是否被写入（`wc -l file.py` 比原始大 → 有内容）
2. 检查语法（`python3 -c "compile(open('path').read(), ...)"`）
3. 检查注册函数名 — 子代理可能保留 `register_unknown`
4. 修复函数名 + 更新 `_sympy()` 使用引擎代理

## 引擎代理模式

`_EngineProxy` 通过 `__getattr__` 实现透明 symengine→sympy 降级：

```python
class _EngineProxy:
    def __getattr__(self, name):
        if engine_name == 'auto':
            se = _get_symengine()
            if se and hasattr(se, name):
                return getattr(se, name)
            sp = _get_sympy()
            if hasattr(sp, name):
                return getattr(sp, name)
        ...
```

所有 37 处 `_sympy().xxx(...)` 调用零改动享受自动降级。

## 文档驱动重构

当有设计文档（`doc/*.md`）与代码不一致时：

1. **API 命名对齐** — 文档中指定的函数名应优先于代码中的别名
   - `euler_fn` → `euler`（文档写 `euler`）
   - `visualize`/`plot-2d`/`plot-3d` → `plot`/`plot-param`/`plot3d`（文档指定）

2. **缺失功能补齐** — 文档列出但未实现的功能需添加
   - `(use-cas 'all)` / `(use-cas 'min)` 模式
   - `(list-all)` 列出全部绑定
   - `(eqn lhs rhs)` 方程构造函数

3. **引擎代理** — 文档描述 `_EngineProxy` + `call()` 需实现

## `_sympy()` 统一改造

5 个模块有 `_sympy()` 辅助函数，修改为使用引擎代理：
```python
def _sympy():
    from eval.cas.engine import get_engine
    return get_engine()
```

`linear.py` 额外需要将 `import sympy as _sympy` 改为函数调用 + `_sympy().XXX` 引用。

## `primitives.py` 导入修复

`primitives.py` 中以下导入名需修正：
- `register_cas_primitives` → `register_core_primitives`
- `register_cas_entry_primitives` → `register_entry_primitives`
- numpy/learn 桥接模块设为可选：（`try/except ModuleNotFoundError`）primitives` → `register_core_primitives`\n- `register_cas_entry_primitives` → `register_entry_primitives`\n- numpy/learn 桥接模块设为可选：（`try/except ModuleNotFoundError`）\n