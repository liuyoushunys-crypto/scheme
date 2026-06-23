# 语法糖与多维切片 — 参考

## 语法糖宏 (eval/eval_py_sugar.py)

通过 `define-macro` 在 `register_all` 启动时注册。

| 宏 | 展开 | 注册代码 |
|----|------|---------|
| `λ` | `lambda` | `(define-macro (λ . rest) (cons 'lambda rest))` |
| `->` | thread-first | 递归展开为嵌套调用，参数为第一个位置的 `x` |
| `->>` | thread-last | 同 `->` 但参数在末尾 |
| `for` | list comp | `(define-macro (for bindings . body) (list 'map (cons 'lambda (cons (list (car bindings)) body)) (cadr bindings)))` |
| `str` | concat | 字符串自动保留，其他转 `number->string` 后 `string-append` |

### `->` 宏精义

```
(define-macro (-> x . forms)
  (if (null? forms) x
    (let ((form (car forms)) (rest (cdr forms)))
      (if (pair? form)
        (let ((result (append (list (car form) x) (cdr form))))
          (if (null? rest) result
            (cons '-> (cons result (cdr forms)))))
        (if (null? rest) (list form x)
          (cons '-> (cons (list form x) (cdr forms))))))))
```

## Bracket `:` 切片语法 (eval/eval_scheme.py `Sym("bracket")` 特殊形式)

### 原理

`:` 在 Scheme 中是无害的自求值符号：
```python
# eval_scheme.py Sym case
case Sym() as sym:
    if sym.name.startswith(":"):
        return sym  # 不查 env，直接返回自身
```

在 bracket 参数列表中检查 `Sym(":")` 出现：
```python
has_colon = any(isinstance(a, Sym) and a.name == ':' for a in indices)
```

### 顺序恢复（关键陷阱）

```python
# 用字典按位置存储
py_entries = {}
consumed = set()

for cp in colon_pos:
    # 配对 : 前后的值为 slice
    dim_pos = (cp - 1) if has_left else cp  # 第一个值的位置
    py_entries[dim_pos] = slice(left_val, right_val, step_val)

# 未配对的标量
for i, a in enumerate(indices):
    if i not in consumed:
        py_entries[i] = unwrap_python_value(a)

# 按位置排序恢复正确顺序
py_indices = [v for _, v in sorted(py_entries.items())]
```

不加 `sorted()` 时 `[m 0 1 : 3]` 错误地变成 `m[1:3, 0]` 而非 `m[0, 1:3]`。

### 向后兼容

无 `:` 时走原有 2/4/3+ 参数分支：
- 2 参数: `[a 5]` → `a[5]`（单索引）
- 4 参数: `[a 2 8 2]` → `a[2:8:2]`（旧三元组切片）
- 3+ 参数: `[m 0 1]` → `m[0, 1]`（多维）
