# CAS 模块恢复与命名对齐（2026-06-23 会话）

## 背景
之前的生成脚本损坏了 `eval/cas/` 下的多个模块。本次会话完成了恢复、实现补齐和文档 API 名对齐。

## `\n` 字面量损坏修复

**症状：** 文件内容出现字面 `\n` 字符串而非真实换行。
**诊断：** `cat -A file.py` 显示每行末尾 `\n$` 而非 `$`。
**原因：** 生成脚本用 `'\\n'.join(lines)` 写入文件时逃逸处理不当。

**修复命令：**
```python
with open(path) as f:
    raw = f.read()
fixed = raw.replace('\\n', '\n')  # 字面反斜杠-n → 真实换行
with open(path, 'w') as f:
    f.write(fixed)
```

**受影响文件：** `core/__init__.py`, `core/core.py`, `info/__init__.py`, `info/core.py`

## 空 `__init__.py` 修复

**症状：** 多个模块的 `__init__.py` 仅含一个换行符，无内容。
**标准内容：**
```python
"""模块名"""
from .core import register_模块名_primitives
```

**受影响目录：** `assume/`, `sugar/`, `numerical/`, `info/catalog/`, `info/ecosystem/`

## `register_unknown` → 正确函数名

**症状：** 生成脚本留下的默认函数名 `register_unknown` 不匹配模块名。
**修复模式：**
```python
# 改前
def register_unknown(env):
    """Register {scheme_name}."""
    
# 改后
def register_模块名_primitives(env):
    """Register 模块名 primitives."""
```

**受影响文件：** `bridge.py`, `engine.py`, `parse.py`, `pattern.py`, `tensor.py`, `viz.py`, `info/help.py`, `info/nav.py`

## `primitives.py` import 名修复

生成脚本留下错误 import 名：
- `register_cas_primitives` → `register_core_primitives`
- `register_cas_entry_primitives` → `register_entry_primitives`
- `numpy`/`learn` 桥接模块改为可选导入（`try/except ModuleNotFoundError`）

## 聚合器 import 通配修复

`core/core.py` 和 `info/core.py` 使用 `register_unknown` 作为 import 目标。修复后改为：
```python
from .algebra import register_primitives as register_algebra
```

## Flat → Package 转换的双重导出

当扁平 `.py` 文件被子代理转为 `name/` 包时，`__init__.py` 必须同时导出：
```python
"""tensor"""
from .core import register_tensor_primitives
from .core import register_primitives  # 供聚合器别名导入
```

## `engine.py` get_engine() 返回模块而非字符串

子代理改写了 `engine.py`，使 `get_engine()` 返回实际 `sympy` 模块对象而非字符串 `"auto"`。
- `_set_engine('auto')` 尝试导入 symengine，失败则回退 sympy
- `cas_use_engine` 处理 Sym 对象：`args[0].name if hasattr(args[0], 'name') else str(args[0])`
- 其他模块仍使用独立 `_sympy()` 辅助函数直接 `import sympy`，不依赖 `engine.get_engine()`

## core 模块实现补齐

| 模块 | 函数数 | 实现方式 |
|------|--------|----------|
| `core/algebra.py` | 26 | 子代理，通过 `_sympy()` → `sympy.xxx()` |
| `core/calculus.py` | 12 | 子代理（超时），手动修复注册名 |
| `core/linear.py` | 17 | 子代理 |
| `core/special.py` | 40+ | 子代理（限流失败前已完成） |
| `core/output.py` | 7 | 直接实现 + 子代理修复 |

## 文档 API 名对齐

| 文档名 | 原名 | 改后 | 文件 |
|--------|------|------|------|
| `euler` | `euler_fn` | `euler` | `special.py` 注册表 |
| `plot` / `plot-param` / `plot3d` | `visualize` / `plot-2d` / `plot-3d` | `plot` / `plot-param` / `plot3d` | `viz/core.py` |
| `eqn` | 未注册 | 新增 `cas_eqn` | `algebra.py` |

## 验证命令

```bash
# 语法检查
find eval/cas -name '*.py' -not -path '*/__pycache__/*' | while read f; do
    python3 -c "compile(open('$f').read(), '$f', 'exec')" 2>&1 || echo "FAIL: $f"
done

# 核心导入验证
python3 -c "
from primitives.primitives import register_all
from core.env import Env
global_env = Env()
register_all(global_env)
from eval.eval_scheme import eval_scheme
from parser.parse_program import parse
result = eval_scheme(parse('(import sympy)'), global_env)
result = eval_scheme(parse(\"(define x (sympy.Symbol 'x))\"), global_env)
result = eval_scheme(parse('(diff (expt x 3) x)'), global_env)
print('diff =', result)
"
```