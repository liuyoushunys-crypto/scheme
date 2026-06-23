# 特殊形式实现指南

## 什么时候需要特殊形式（而非 Prim 或宏）

| 机制 | 参数求值时机 | 适用场景 |
|------|-------------|---------|
| **Prim** | 调用前全部求值 | 函数调用，所有参数都需要值 |
| **宏 (define-macro)** | 编译期展开，参数被 `quote` 包裹 | 语法转换，参数在展开时无需值 |
| **宏 (syntax-rules)** | 编译期模式匹配 | 卫生宏，需遵守宏 hygiene |
| **特殊形式 (eval_scheme.py case)** | 可控：可选择性求值或完全不求值 | 接收未求值参数；需要 `try/except` 包裹 |

## 实现模式

在 `eval/eval_scheme.py` 的 `match exp` 块中添加 `case`：

```python
case Sym("my-form"):
    match cons.cdr:
        case Cons(arg1, Cons(arg2, Nil())):
            val1 = eval_scheme(arg1, env)    # 有选择地求值 arg1
            return _process(arg2, val1, env)  # arg2 保持未求值
    raise Exception("my-form: 语法错误")
```

## 现有特殊形式清单

| 形式 | 原因 |
|------|------|
| `try` | 需要 `try/except` 捕获 Python 级异常 |
| `match` | `?x` 等模式变量须保持未求值 |
| `defrule` | pattern 和 replacement 都是代码模板 |
| `rewrite` | rule-name 是符号而非已求值变量 |
| `index` | `i`, `j`, `k` 未在环境中绑定 |
| `tensor` | 指标符号是语法形式 |
| `contract` / `raise-index` / `lower-index` | 指标名未求值 |

## 关键陷阱

1. **`try` 必须捕获 `Exception`（基类）**：Python 级错误（未绑定变量、类型错误等）穿透 Scheme 的 `with-exception-handler`
2. **`?x` 自求值规则**：`?` 单独和 `??` 是正常调用，`?x`/`?a`/`?name` 自求值
3. **延迟导入**：特殊形式中引用其他模块时用函数内部 `from module import func` 避免循环导入
4. **`cons.cdr` 可能是 `Nil`**：零参数情况须处理
