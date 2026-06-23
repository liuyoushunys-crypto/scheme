# Flat File → Package Conversion Pitfalls

## 场景

CAS 模块最初以扁平 `.py` 文件存在（如 `tensor.py`, `viz.py`, `bridge.py`, `engine.py`, `parse.py`），后因框架拆分或子代理生成被转换为 `name/` 目录包。

## 核心陷阱

**转换后的 `__init__.py` 必须导出两种名称**，否则不同导入路径会断裂：

| 必须导出 | 用途 |
|----------|------|
| `register_{name}_primitives` | `primitives.py` 中的显式命名导入 `from eval.cas.{name} import register_{name}_primitives` |
| `register_primitives` | 聚合器 `core.py` 中的通用导入 `from .{name} import register_primitives as register_{name}` |

### 错误示范

子代理自动生成 `tensor/` 包时只写了一个导出：
```python
# tensor/__init__.py (错误!)
"""tensor"""
from .core import register_tensor_primitives
```

这导致 `primitives.py` 中 `from eval.cas.tensor import register_tensor_primitives` 正常工作，但 `core/core.py` 中的 `from .tensor import register_primitives` 断裂。

### 正确写法

```python
# tensor/__init__.py (正确)
"""tensor"""
from .core import register_tensor_primitives
from .core import register_primitives
```

`core.py` 内：
```python
# tensor/core.py
register_primitives = register_tensor_primitives  # 必须有此别名
```

## 受影响文件清单

| 文件 | 状态 | 修复内容 |
|------|------|---------|
| `tensor/__init__.py` | 子代理生成 | 添加 `from .core import register_primitives` |
| `viz/__init__.py` | 子代理生成 | 添加 `from .core import register_primitives` |
| `bridge.py` | 仍为扁平文件 | `register_primitives = register_bridge_primitives` ✓ |
| `engine.py` | 仍为扁平文件 | `register_primitives = register_engine_primitives` ✓ |
| `parse.py` | 仍为扁平文件 | `register_primitives = register_parse_primitives` ✓ |
| `pattern.py` | 仍为扁平文件 | `register_primitives = register_pattern_primitives` ✓ |

## 验证命令

转换后运行：
```bash
cd /workspace/99
python3 -c "import sys; sys.path.insert(0, '.'); from eval.cas.{name} import register_primitives; print('OK')"
python3 -c "import sys; sys.path.insert(0, '.'); from eval.cas.{name} import register_{name}_primitives; print('OK')"
```

两者都必须通过。

## 根因

`primitives.py` 使用两种不同的 import 模式：
1. 显式命名（`from eval.cas.tensor import register_tensor_primitives`）
2. 别名导入（`from .tensor import register_primitives as register_tensor` 在聚合器中）

确保子代理或生成脚本在创建 `__init__.py` 时同时导出这两种名称。
