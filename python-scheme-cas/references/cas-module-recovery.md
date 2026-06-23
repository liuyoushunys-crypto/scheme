# CAS 模块恢复 — 从 .md 重建 cas_* 函数

当 CAS 核心模块被破坏（替换为占位符 `"unknown"` docstring），从 `.md` 规范文件恢复的标准化流程。

## 信号
- 模块文件含 `"""unknown"""` docstring
- `register_primitives = register_unknown`
- 函数体缺失或 NameError

## 恢复步骤

### 1. 识别被破坏的模块

```bash
grep -l '"unknown"' eval/cas/**/*.py
grep -l 'register_primitives = register_unknown' eval/cas/**/*.py
```

常见：`core/calculus.py`, `core/output.py`（完整实现丢失）；`core/special.py`（仅 `register_unknown` 需改名）

### 2. 读取对应 .md 规范

每个模块同级有 `.md` 文件（`calculus.md`, `output.md`），包含完整 API 定义 + Scheme 示例。

### 3. 参考已实现的模块作为模板

使用一致的函数签名：
- 导入：`from typing import List; from core.schemevalue import *; from eval.eval_python_import import unwrap_python_value, wrap_python_value`
- 工具函数：`_sympy()`, `_unwrap1(args)`, `_unwrap(args)`
- 每个函数：`def cas_xxx(args: List[SchemeValue]) -> SchemeValue:`
- `sp = _sympy(); py_args = _unwrap(args); expr = sp.sympify(py_args[0]); result = sp.xxx(expr); return wrap_python_value(result)`

### 4. 注册函数 + 末尾行（关键！）

```python
def register_<module>_primitives(env):
    prims = [("xxx", cas_xxx), ...]
    for name, func in prims:
        env.define(name, Prim(name, func))

register_primitives = register_<module>_primitives  # ← 聚合器扫描此
```

### 5. 验证

```bash
python3 -c "from eval.cas.{mod} import register_primitives; print('OK')"
python3 -c "from eval.cas.core import register_core_primitives; print('aggregator OK')"
python3 tests/phase14_comprehensive.py
```

## 陷阱

### 缺少 `register_primitives =` 行

模块有完整函数但无末尾行 → `ImportError: cannot import name 'register_primitives'`。

`_rebuild_final.py` 用 `re.search(r'register_primitives\\s*=\\s*(\\w+)', content)` 扫描。缺失此行使模块不可发现。

### `register_unknown` 未改名

自动生成脚本留下 `register_unknown`。聚合器用 `register_{mod}_primitives` 命名导入时报错。

### 引擎 `auto` 模式丢失

被重写的 `engine.py` 可能只支持 `sympy`/`symengine`，缺少 `auto`。补丁：
```python
elif name == 'auto':
    try: import symengine; _engine = symengine
    except ImportError: import sympy; _engine = sympy
```

### 测试文件中的过时导入路径

`eval.eval_cas_engine` → `eval.cas.engine`（重构后路径变）。搜索：`grep -r 'eval\\.eval_cas_engine' tests/`

### Str 查询处理

`Str(list("方程"))` 中 `str(arg)` → `"Str(value=['方', '程'])"`（repr），`arg.get_str()` → `"方程"`（实际字符串）。帮助搜索必须用 `get_str()`。

### 帮助数据库 ≥ 80 条

`_CAS_FUNCTIONS` 在重构后可能缩水。确保涵盖所有模块的函数。