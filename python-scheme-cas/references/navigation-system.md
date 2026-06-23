# 分级导航系统 (`(nav)`)

## 模块

`eval/eval_py_nav.py` — `register_nav_primitives(env)`

## 命令

```scheme
(nav)              → 7 领域: 符号计算/数论/数值计算/数据科学/可视化/统计/系统工具
(nav '符号计算)     → 10 分类: 微积分/代数/方程/线性代数/三角/向量微积分/…
(nav 'diff)        → 函数详情: 领域/分类/语法/说明
(nav "特征值")     → 跨分类搜索
```

## 层级结构

```
7 领域 → 20+ 分类 → 185+ 函数

(nav)
├─ 符号计算 (72 函数)
│  ├─ 微积分 (7)     diff, integrate, limit, series, summation…
│  ├─ 代数 (13)      expand, factor, simplify, ratsimp…
│  ├─ 方程 (8)       solve, isolate, lhs, rhs, dsolve…
│  ├─ 线性代数 (17)  matrix, det, inv, svd, lu-decomp…
│  └─ … 6 更多分类
├─ 数论 (14)
├─ 数值计算 (7)
├─ 数据科学 (34)
├─ 可视化 (29)
├─ 统计 (6)
└─ 系统工具 (29)
```

## 配套命令

```scheme
(? 'diff)        → help 快捷别名
(?? "微积分")    → catalog 搜索
(apropos "方程") → 搜索别名
(list-all)       → 504 个全部注册函数
(help)           → 分类列出 88 CAS 函数（含示例）
(catalog)        → 29 包 × 9 领域 Python 包浏览
```

## 数据来源

导航数据库 (`NAV_DB`) 是手工 curated 的字典，结构为 `{领域: {分类: [(函数名, 语法, 说明), ...]}}`。
搜索覆盖函数名、说明、分类名和领域名。未匹配时提示 `(nav)` 或 `(nav "关键词")`。

## 相关文件

- `eval/eval_py_nav.py` — 导航主逻辑
- `eval/eval_cas_entry.py` — `(use-cas)` 入口
- `eval/eval_py_help.py` — 帮助系统（含示例）
- `eval/eval_py_catalog.py` — 科学计算包目录
