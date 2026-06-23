# core/calculus — 微积分与向量微积分

```scheme
(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))
```

## 微分

```scheme
(diff (* x x x) x)                →  3*x**2
(diff (sin x) x)                   →  cos(x)
(diff (* x (exp x)) x)             →  x*exp(x) + exp(x)
```

## 积分

```scheme
; 不定积分
(integrate (* x x) x)              →  x**3/3
(integrate (sin x) x)              →  -cos(x)

; 定积分
(integrate (* x x) x 0 1)          →  1/3
(integrate (exp (- x)) x 0 (inf))  →  1
```

## 极限

```scheme
(limit (/ (sin x) x) x 0)          →  1
(limit (/ 1 x) x (inf))            →  0
(limit (/ 1 x) x 0 'plus)         →  oo
(limit (/ 1 x) x 0 'minus)        →  -oo
```

## 级数展开

```scheme
(series (sin x) x 0 5)             →  x - x**3/6 + O(x**5)
(series (exp x) x 0 4)             →  1 + x + x**2/2 + x**3/6 + O(x**4)
(taylor (sin x) x 0 5)            →  x - x**3/6 + O(x**5)  ; taylor = series 别名
```

## 求和/求积

```scheme
(summation (/ 1 (** x 2)) (list x 1 (inf)))  →  pi**2/6
(product x (list x 1 5))         →  120
```

## 向量微积分

```scheme
(grad (* x x) x)                   →  [2*x]
(hessian (* x x) (list x))         →  [[2]]
(jacobian (list (* x x) (* x x x)) (list x))
  → Matrix([[2*x], [3*x**2]])
```