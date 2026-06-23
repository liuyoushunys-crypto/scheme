# CAS 入口系统

## 模块

`eval/eval_cas_entry.py` — `register_cas_entry_primitives(env)`

## 命令

```scheme
(use-cas)          → 加载核心: sympy + numpy + 绘图 + 假设 + 数值 + 语法糖
(use-cas 'all)     → 含 scikit-learn + 图论 + 物理单位 + 张量
(use-cas 'min)     → 仅符号计算 + numpy
```

## 加载的内容

### normal 模式
- sympy/symengine（符号计算引擎）
- numpy（数组/矩阵 + 40 快捷函数）
- plot/scatter/hist/bar/imshow...（17 种图）
- assume/refine/ask（假设系统）
- find-root/numerical-integrate（数值方法）
- λ/->/->>/for/str（语法糖）
- ∞（无穷大符号）
- try（异常捕获特殊形式）

### 'all 模式（额外加载）
- scikit-learn（30+ 模型 + CV + 调参 + Pipeline）
- networkx（图论算法）
- sympy.units（物理单位 + 常数）
- sympy.tensor（张量运算）

## 注册

```python
from eval.eval_cas_entry import register_cas_entry_primitives
register_cas_entry_primitives(env)  # primitives.py register_all() 中
```

## 配套

```scheme
(? 'diff)       → 函数帮助
(?? "微积分")   → catalog 搜索
(apropos "方程") → 搜索
(list-all)       → 全部 504 函数
```

## 实现细节

`use-cas` 通过 `eval_scheme(parse("(use-numpy)"), env)` 注入已有 `use-*` 命令。
`?` 和 `??` 是 Prim 别名，分别转发到 `cas_help` 和 `cas_catalog`。`list-all` 遍历
env 的 `_bindings` 并过滤 Prim/Closure/MacroClosure。
