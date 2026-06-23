# CAS 入口系统 — `eval/cas/entry/core.py`

## 命令

```scheme
(use-cas)          → 加载核心: sympy + 数值 + 假设 + 语法糖
(use-cas 'all)     → 含 scikit-learn + 图论 + 物理单位 + 张量
(use-cas 'min)     → 仅符号计算 + numpy
(list-all)         → 列出环境全部 500+ 函数
```

## 注册链

```python
# primitives/primitives.py
from eval.cas.entry import register_entry_primitives

def register_all(env):
    ...
    register_entry_primitives(env)
```
