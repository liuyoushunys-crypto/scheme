# CAS 帮助系统设计指南

## 架构

三层入口：
```
(help)             → 15 分类 × 140+ 函数，分类列表浏览
(? 'diff)          → 快捷函数详情
(?? "微积分")      → 跨分类搜索
```

实现文件：`eval/eval_py_help.py`

## 帮助数据库结构

```python
_CAS_FUNCTIONS: Dict[str, dict] = {
    "function-name": {
        "cat": "分类名",                    # 必填，对应 _CATEGORY_ORDER
        "args": "(语法签名)",               # 必填，显示完整签名
        "desc": "说明文字",                  # 必填，中文说明
        "ex": [                             # 可选，可运行示例列表
            "(示例代码)  → 期望结果",         # 示例必须可直接复制运行
        ],
        "kw": ":关键词1, :关键词2",          # 可选，仅绘图函数
        "see": "关联函数1, 关联函数2",       # 可选，用逗号分隔
    },
}
```

## 分类排序

```python
_CATEGORY_ORDER = [
    "微积分", "向量微积分", "代数", "方程",
    "线性代数", "数论", "特殊函数", "积分变换",
    "输出", "绘图", "CAS 系统", "语法糖",
    "模式匹配", "张量代数", "导航",
]
```

每个分类的函数在 `(help)` 输出中按此顺序排列。总覆盖约 140 个函数。

## 格式化

`_fmt_help(name, info)` 产生如下格式：

```
╔══ function-name ══╗
  📂 分类名
  📝 (语法签名)
  说明文字

  📖 示例:
    (示例代码1)  → 期望结果1
    (示例代码2)  → 期望结果2
    (示例代码3)  → 期望结果3  ← 每函数 3-4 个示例

  🔑 关键词参数: :key1, :key2    ← 仅绘图函数

  🔗 关联函数: see1, see2
```

设计要点：
- 每个函数至少 1 个示例，复杂函数 3-4 个（覆盖不同参数模式）
- 示例均为**可直接复制运行**的完整代码
- 中文说明，避免专业术语缩写
- 关联函数帮助用户发现相关能力

## 搜索实现

搜索覆盖函数名、分类名、说明文字和示例文本：

```python
if isinstance(first, Str):
    keyword = first.get_str().lower()
    matches = []
    for n, i in _CAS_FUNCTIONS.items():
        text = f"{n} {i.get('cat','')} {i.get('desc','')} {' '.join(i.get('ex',[]))}"
        if keyword in text.lower():
            matches.append((n, i))
```

搜索结果的 `(?? "关键词")` 输出格式：
```
搜索 "微积分" 找到 12 个结果：

  diff                       [微积分]  求导数。2 参数为一阶导数…
  integrate                  [微积分]  积分运算。3 参数为不定积分…
  limit                      [微积分]  求极限。可选 :dir 指定方向…
  ...
```

## 快捷入口

`?` 和 `??` 在 `eval_cas_entry.py` 中注册为 Prim，分别调用 `cas_help`：

```python
def cas_help_short(args):
    from eval.eval_py_help import cas_help
    return cas_help(args)

def cas_search_short(args):
    from eval.eval_py_help import cas_help
    return cas_help(args)
```

`?` 和 `??` 能在 eval 中查找的前提：`eval_scheme.py` 的 `Sym` case 中
`?`（单字符）不视为自求值模式变量——仅 `?x`, `?a` 等长度 >1 且不以 `??` 开头的符号才自求值。

## 覆盖的函数分类

| 分类 | 函数数 | 说明 |
|------|--------|------|
| 微积分 | 7 | diff, integrate, limit, series, taylor, summation, product |
| 向量微积分 | 5 | grad, div, curl, hessian, jacobian |
| 代数 | 18 | expand, factor, simplify, ratsimp, apart, together, collect, coeff, resultant, discriminant, normal, compose, subs, trigexpand, trigsimp, powsimp, logcombine, radsimp |
| 方程 | 8 | solve, isolate, lhs, rhs, roots, nroots, diophantine, dsolve |
| 线性代数 | 17 | matrix, det, inv, transpose, eigenvals, eigenvects, svd, lu-decomp, qr-decomp, norm, rank, nullspace, row, col, eye, zeros, ones |
| 数论 | 9 | prime?, factorint, nextprime, prevprime, primerange, divisors, totient, mobius, continued-fraction |
| 特殊函数 | 6 | lambertw, polylog, stirling, bernoulli, euler_fn, fibonacci |
| 积分变换 | 4 | laplace, inverse-laplace, fourier, inverse-fourier |
| 输出 | 5 | pretty, latex, ccode, fcode, mathml |
| 绘图 | 28 | plot, scatter, bar, barh, hist, boxplot, violin, errorbar, contour, imshow, stem, pie, fill-between, plot-param, plot3d, figure, subplot, savefig, title, xlabel, ylabel, text, axvline, axhline, legend, grid, clf, close |
| CAS 系统 | 10 | use-cas, use-numpy, use-engine, use-learn, assume, unassume, refine, ask, eqn, try |
| 语法糖 | 7 | λ, ->, ->>, for, str, #{...}, [a :] |
| 模式匹配 | 4 | match, defrule, rewrite, rules |
| 张量代数 | 5 | index, tensor, contract, raise-index, lower-index |
| 导航 | 6 | nav, help, catalog, list-all, ecosystem, engine-info |

## 添加新函数的步骤

1. 在 `_CAS_FUNCTIONS` dict 中添加条目
2. 指定 `cat` 为已有分类（如需新分类，加到 `_CATEGORY_ORDER`）
3. 至少提供 `args` 和 `desc`
4. 添加 `ex` 示例（确保可复制运行）
5. 配置 `see` 关联函数（以逗号分隔的字符串）
6. 重启验证：`(? 'new-func)` 和 `(?? "关键词")`
7. 检查 `(help)` 分类列表中的对齐和截断
