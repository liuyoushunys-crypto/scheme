# Python 表达式求值 — `py` / `py-f` / `..` 方法链

## `(py "expr")` — 自动注入变量的 Python eval

在 Scheme 环境中执行任意 Python 表达式，自动注入已绑定的 Scheme 变量。

```scheme
(import sympy as sp)
(sym x)

(py "sp.expand((x + 1)**5)")
;; → x⁵ + 5x⁴ + 10x³ + 10x² + 5x + 1

(py "1 + 2 + 3")
;; → 6

(import numpy as np)
(py "np.linspace(0, 1, 5)")
;; → [0.   0.25 0.5  0.75 1. ]
```

自动注入 `numpy` 为 `np`、`sympy` 为 `sp`、以及所有 `sym` 创建的符号。

## `(py-f "fmt")` — Python f-string 格式化

```scheme
(define a 42)
(define s "hello")
(py-f "a={a}, s={s}")
;; → "a=42, s=hello"
```

## `(.. obj (method args...) ...)` — 方法链

```scheme
(.. (sp.Matrix [[1 2; 3 4]]) (det))
;; → -2

(.. (sp.Matrix [[1 2; 3 4]]) (inv) (det))
;; → -1/2

(.. (np.array (list 1 2 3 4 5)) (reshape 5 1))
;; → [[1]
;;     [2]
;;     [3]
;;     [4]
;;     [5]]
```

等价于 Python：`sp.Matrix([[1,2],[3,4]]).inv().det()`

## 多行支持

```scheme
(py "np.array([
    [1, 2, 3],
    [4, 5, 6]
])")

(py-f """Values:
a = {a}
x = {x}
""")
```
