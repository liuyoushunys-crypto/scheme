# CAS 目录重组模式

## 核心模式：扁平 .py → 子目录包

将大 .py 文件变成子目录结构以保证可扩展性。

### File-to-directory 迁移步骤

1. 创建目标子目录
2. 写 `__init__.py` 做 re-export
3. 复制原 `.py` 内容到子目录 `core.py`
4. 更新原 `.py` 为 shim: `from eval.py import *`
5. 删除原 `.py` (或保留 shim 做向后兼容)
6. 更新所有 import 路径

### 层级化模式 (submodule → subdir)

将包中子模块进一步拆成目录:
```
numpy.py → numpy/core.py + numpy/__init__.py
  → numpy/create/core.py + numpy/create/__init__.py
  → numpy/math/core.py + numpy/math/__init__.py
  ...
```

## CAS 目录重组执行记录

| 文件 | 操作 | 结果 |
|------|------|------|
| `eval/cas/core.py` (682行) | 拆成 `core/` 子目录 | calculus/algebra/linear/special/output 5文件 |
| `eval/cas/help.py` | 移到 `info/` | info/help.py + __init__.py |
| `eval/cas/nav.py` | 移到 `info/` | info/nav.py |
| `eval/cas/catalog.py` | 移到 `info/` | info/catalog.py |
| `eval/cas/ecosystem.py` | 移到 `info/` | info/ecosystem.py |
| `eval/cas/numpy.py` | 拆成 `numpy/` | core + create/manipulate/math/linalg/transform/random/io |
| `eval/cas/learn.py` | 拆成 `learn/` | core.py + __init__.py |
| `eval/cas/numerical.py` | 拆成 `numerical/` | core.py + __init__.py |
| `eval/cas/bridge.py` | 拆成 `bridge/` | core.py + __init__.py |
| `eval/cas/viz.py` | 拆成 `viz/` | core.py + __init__.py |

## `eval_scheme.py` 提取记录

| 阶段 | 提取文件 | 行数变化 |
|------|---------|---------|
| 初始 | — | 628行 |
| bracket | `eval_bracket.py` (~130行) | 628→498 (-130) |
| try | `eval_try.py` (~15行) | 498→496 |
| macro_forms | `eval_macro_forms.py` (~110行) | 496→397 |
| cas_dispatch | `eval_cas_dispatch.py` (~130行) | 397→ |
| special_forms | `eval_special_forms.py` (~80行) | 345 |
| short_circuit | `eval_short_circuit.py` (~50行) | |
| import_forms | `eval_import_forms.py` (~40行) | |
| **最终** | **7 提取文件** | **628→345行 (-45%)** |

## `eval_python_import.py` 提取记录

| 初始 | 486行, 1 文件, 40 处 import 引用 |
|------|------|
| 策略 | Shim 模式 — 原文件保留为 re-export 入口 |
| 提取文件 | `eval/py/convert/closure/attr/import_forms/runtime/register/arithmetic` |
| Shim | `eval/eval_python_import.py`: `from eval.py import *` |

## 注册一致性验证

拆分 `core.py` 时函数定义按段分裂但注册函数仍在一起 → `cas_roots`/`cas_nroots` 卡在 `linear.py` 但注册在 `special.py` → NameError。  
修复：将函数定义移动到注册所属文件，或调整注册块分配。  
验证：`grep "^def cas_"` 确认函数存在 + grep 注册列表中名称对应。

## 内部符号导出陷阱

将 `.py` 转为 `name/` 目录后，`__init__.py` 不能只导出 `register_*` 函数，还必须导出所有被其他模块 import 的内部符号。

例如 `core/*.py` 中 `from eval.cas.engine import get_engine, engine_call`，而 `engine/__init__.py` 只做了 `from eval.cas.engine.core import register_engine_primitives` → 全系统断裂。

修复方案：**逐一扫描**所有 `from eval.cas.XXX import YYY` 语句，收集 YYY，在 `XXX/__init__.py` 中显式导出：

```python
# engine/__init__.py — 必须导出内部符号！
from eval.cas.engine.core import register_engine_primitives, get_engine, engine_call

# tensor/__init__.py
from eval.cas.tensor.core import register_tensor_primitives
from eval.cas.tensor.core import _declare_indices, _make_tensor, _do_contract, _do_raise, _do_lower  # ← 私有符号也要导出

# pattern/__init__.py
from eval.cas.pattern.core import register_pattern_primitives
from eval.cas.pattern.core import _eval_match, _define_rule, _apply_rules  # ← 被 eval_cas_dispatch 引用
```

这种方法虽然让 `__init__.py` 不那么"干净"，但换来「0 处 import 断裂」的向后兼容性。  
可用 `grep -rn "from eval.cas.XXX import"` 扫描全部依赖方。

## `eval_python_import.py` 提取记录

当文件中函数定义数量和注册数量不匹配时：
1. 用脚本扫描所有 `def pnp_xxx` 函数
2. 扫描 `register_xxx_primitives` 函数中的 `("np.xxx", pnp_xxx)` 注册
3. 计算差值 → 自动生成缺失注册行
4. 插入到 `register` 函数结尾的 `]` 之前
