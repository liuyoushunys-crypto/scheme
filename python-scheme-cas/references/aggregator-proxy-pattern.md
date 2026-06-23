# Aggregator Proxy Pattern

When splitting a monolithic `core.py` (which registers N primitives) into individual primitive directories, **do NOT delete the old file**. Use the **aggregator proxy** pattern:

## Structure

```
模块/
├── core.py              ← 保留原文件！内含全部函数具体实现
├── aggregator.py        ← 新建文件：从各单例目录 import register 并聚合
├── __init__.py
├── func1/               ← 新建单例目录
│   ├── core.py          ← 代理到 from ..core import cas_func1 as _impl
│   ├── __init__.py
│   └── demo.md
└── func2/ ...
```

## 单例代理 core.py 模板

```python
"""core/subdir/func — 说明"""
from typing import List
from core.schemevalue import SchemeValue, Prim
from eval.cas.core.subdir.core import cas_func as _impl

def _run(args: List[SchemeValue]) -> SchemeValue:
    return _impl(args)

def register(env):
    """注册 func 到 Scheme 环境。"""
    env.define("func", Prim("func", _run))
```

## 聚合器 aggregator.py 模板

```python
"""subdir - 原语聚合"""
from .func1.core import register as register_func1
from .func2.core import register as register_func2

def register_subdir(env):
    register_func1(env)
    register_func2(env)
```

## 父级 __init__.py

必须从 `aggregator.py` 导入（不是从 `core.py` 导入旧的聚合函数名）：

```python
from eval.cas.core.subdir.aggregator import register_subdir as _reg
```

## 为什么保留原 core.py

1. 其他模块的 `from .core import cas_func` 导入不会被破坏
2. 函数实现在原位可追溯
3. 增量迁移：不影响现有测试

## 实际案例

2026-06-23 会话中用于 `eval/cas/core/` 5 子模块：

| 子模块 | 原文件 | 拆分数 |
|--------|--------|:------:|
| algebra | core.py → 26 个单例 | 26 |
| calculus | core.py → 12 个单例 | 12 |
| linear | core.py → 15 个单例 | 15 |
| special | core.py → 29 个单例 | 29 |
| output | core.py → 6 个单例 | 6 |

共 88 个原语从 5 个聚合文件拆分为 88 个单例目录 + 5 个 aggregator.py，导入链 0 断裂。

验证方式：
```bash
python3 -c "from eval.cas.core import register_cas_primitives; print('OK')"
```
