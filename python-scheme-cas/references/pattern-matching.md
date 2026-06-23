# 代数模式匹配系统

对标 Maxima 的 `defrule`/`tellsimp`。在 Scheme 表达式的数据结构层进行模式匹配和重写。

## 特殊形式（在 eval_scheme.py 中注册，非 Prim）

这些命令收到**未求值的模式形式**，避免 `?x` 等模式变量被环境提前解析：

```scheme
(match (* ?a x) #{3*x})                        → ((a 3))
(defrule sin-squared (expt (sin ?x) 2) (- 1 (expt (cos ?x) 2)))
(rewrite #{sin(x)^2} sin-squared)              → 1 - cos²(x)
(rules)                                          → 列出全部规则
(clear-rules)                                    → 清除规则
```

## 为什么不是 Prim

- `match`/`defrule`/`rewrite` 的模式参数必须保持**原始 S 表达式形式**不被求值
- `?x` 等符号在 eval_scheme 中因 `name.startswith("?")` 自动返回自身，但在 Prim 参数求值路径中仍可能被异常捕获
- 因此在 `eval_scheme.py` 中注册为特殊形式（`case Sym("match"):` 等），直接访问 `cons.cdr` 获取未求值的模式

## 模式变量

| 语法 | 类型 | 说明 |
|------|------|------|
| `?x`, `?y`, `?z` | any | 匹配任意子表达式 |
| `?a`, `?b`, `?c` | any | 匹配任意子表达式（常用于代数规则） |
| `?n`, `?m` | number | 仅匹配数字（Integer/Num） |
| `_` | wildcard | 匹配任意但不绑定 |
| `?x+` | repeat | 匹配一个或多个连续子表达式 |

## 模式语法

模式使用 **Scheme 前缀形式**（非 `#{...}` 中缀）：

正确：`(match (+ ?a (* ?b x)) #{3 + 5*x})`
错误：`(match (?a + ?b * x) #{3 + 5*x})`

这是因为 `defrule`/`match` 直接接收原始 S 表达式，`(* ?a ?b)` 是标准 Scheme 列表，`(?a * ?b)` 被解析为三元素列表。

## 匹配算法

`_match_pattern(pat, expr, bindings)`:
1. `Sym("?x")` → 未绑定则绑定，已绑定则检查相等
2. `Sym("_")` → 通配符通过
3. `Sym("sin")`, `Sym("x")` 等 → 仅当 expr 也是同名的 Sym 时通过
4. `Integer(3)`/`Num(1.5)`/`Str(...)` → 值相等检查
5. `Cons` → 展平为列表后递归匹配每个元素（长度必须相等，除非有 `?x+`）
6. `Nil()` → 仅匹配 `Nil()`
7. 兜底：`_equal(pat, expr)` 值检查

## 重写引擎

`_apply_rules(expr_val, rule_names)`:
1. 将 sympy PythonObject 通过 `_expr_to_scheme` 转换为 Scheme S 表达式
2. 反复应用规则（最多 100 次迭代），直到不动点
3. 每次应用第一条匹配的规则（break 后重新扫描）
4. 结果尝试用 `eval_scheme` 转换回 sympy PythonObject

## 规则存储

`_rules_db = {}` 字典（`eval/eval_py_pattern.py`），key 为规则名（字符串），value 为 `(pattern, replacement)` 元组。

## 实现文件

- `eval/eval_py_pattern.py` — 匹配/替换/规则管理/注册
- `eval/eval_scheme.py` — `case Sym("match"/"defrule"/"rewrite"):` 特殊形式

## 陷阱

1. **`?` 符号自求值**: 在 `eval_scheme.py` 的 `Sym` case 中添加 `sym.name.startswith("?")` 自求值逻辑。没有则 `?x` 查找时抛出 `Unbound variable`。

2. **`cos` 等不在 Scheme 环境**: 替换结果 `(- 1 (expt (cos ?x) 2))` 代入后为 Scheme S 表达式。若 `cos` 未在 Scheme 中注册，`eval_scheme` 转换回 sympy 会失败，返回原始 Cons。确保相关 sympy 函数名在算术代理层注册。
