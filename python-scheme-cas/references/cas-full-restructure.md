# CAS 全面多级目录化重构 (2026-06-22)

## 目标

将 eval/cas/ 下全部扁平 `.py` 文件转为 `name/` 目录结构，实现"0 个扁平文件"。

## 改造清单

| 轮次 | 文件 | 转为 | 备注 |
|------|------|------|------|
| 1 | `core.py` (682行) | `core/` 5 子文件 | calculus/algebra/linear/special/output |
| 2 | `info/*.py` (4 files) | `info/*/` 子目录 | help/catalog/nav/ecosystem |
| 3 | `numpy.py` (182行) | `numpy/` 8 子目录 | 含 301 原语扩充 |
| 4 | `learn/bridge/numerical/viz` (4 dir already) | 完成目录化 | 每个已有 __init__+core |
| 5 | `engine/entry/parse/tensor/pattern/assume/sugar` (7 files) | `xxx/` 子目录 | 最后一批扁平文件 |
| 6 | `info/help/catalog/nav/ecosystem` (4 files already shims) | `info/xxx/` 子目录 | 原 shim→真正子目录 |

## 模式

每个 `xxx.py` → `xxx/` 目录结构:

```
xxx.py           →  shim (from eval.cas.xxx import register_xxx_primitives)
xxx/__init__.py  →  re-exports register func + internal symbols
xxx/core.py      →  original code
```

**关键规则**:
- `__init__.py` 必须导出内部交叉引用符号（如 `get_engine`, `_declare_indices`, `cas_help`, `_eval_match`），否则 `from eval.cas.xxx import yyy` 断裂
- `name.py` shim 保留用于向后兼容（`from eval.cas.xxx import register_xxx_primitives` 仍可工作）
- 修改 `primitives.py` 或 `eval_scheme.py` 中的 import 路径（`eval.cas.engine`→`eval.cas.engine` 不变因为 shim → `__init__` 链）

## 修复的 import 断裂

转换后暴露的交叉引用断裂:

| 来源 | 导入目标 | 修复 |
|------|---------|------|
| `core/*.py`, `assume/`, `viz/` | `from eval.cas.engine import get_engine` | `engine/__init__.py` 显式导出 |
| `eval_cas_dispatch.py` | `from eval.cas.tensor import _declare_indices` | `tensor/__init__.py` 显式导出 |
| `eval_cas_dispatch.py` | `from eval.cas.pattern import _eval_match` | `pattern/__init__.py` 显式导出 |
| `entry/core.py` | `from eval.cas.info.help import cas_help` | `info/help/__init__.py` 显式导出 |
| `entry/core.py` | `from eval.cas.info.catalog import cas_catalog` | `info/catalog/__init__.py` 显式导出 |

## 验证

```bash
cd /workspace/99 && python3 -c "
from eval.cas.engine import get_engine, register_engine_primitives
from eval.cas.tensor import _declare_indices, register_tensor_primitives
from eval.cas.pattern import _eval_match, register_pattern_primitives
from eval.cas.info.help import cas_help, register_help_primitives
print('All cross-refs OK')
"
```

## 最终状态

- `eval/cas/` 下: **0 个扁平 .py 文件** (全部是 shim)
- **18 个子目录** (engine/entry/parse/tensor/pattern/assume/sugar/core/numpy/learn/numerical/bridge/viz + info/*)
- 每个子目录统一模式: `core.py` + `__init__.py` + 顶层 shim
