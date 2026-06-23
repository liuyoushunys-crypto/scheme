# 特殊形式 vs Prim vs 宏 — 本轮经验总结

## 决策矩阵

| 需求 | 最佳选择 | 原因 |
|------|---------|------|
| 参数需要求值，会调用 Python | **Prim** | 最简单，注册一行 `env.define(...)` |
| 需要未求值的语法形式（模式、变量名） | **特殊形式** | Prim 参数已求值，宏有 quoting 问题 |
| 编译期变换，无需运行时 | **宏** (define-macro) | λ/->/for/str 等语法糖 |

## 本轮新增的特殊形式（参数必须未求值）

### 1. try （异常捕获）
- 不能是 Prim：body 中的错误在 Prim 运行前就已抛出
- 不能是宏（define-macro）：`invoke_macro_closure` 给参数加额外 `quote` 层，展开中需先剥去引用
- 实现：`case Sym("try")` → `try: eval_scheme(body_form, env)` → `except: handler_proc(e)`

### 2. match / defrule / rewrite（模式匹配）
- `?x` 必须保持为符号，不能被求值为 "Unbound variable"
- 例如 `(match (* ?a x) #{3*x})` 中 `?a` 是模式变量
- 实现：`case Sym("match")` → 取未求值的 `pat_form`，传入 `_eval_match`

### 3. index / tensor / contract / raise-index / lower-index（张量代数）
- `(index i j k)` 中 `i`, `j`, `k` 在环境中未绑定
- Prim 会抛 `Unbound variable`
- 实现：`case Sym("index")` → 遍历 `cons.cdr` 取 `a.name` 作为指标名

### 4. `?` 和 `??` 的符号自求值
- `?x` 类符号（`?` 后跟字母）应自求值（如 `:` 关键字）
- 但 `?` 和 `??` 应作为函数名被正常查找
- 规则：`sym.name.startswith("?") and len(sym.name) > 1 and not sym.name.startswith("??")`
