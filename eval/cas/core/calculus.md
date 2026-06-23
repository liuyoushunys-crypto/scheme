# core/calculus — 微积分与向量微积分

```scheme
(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))
```

## 微分

```scheme
(diff (* x x x) x)                  →  3*x**2
(diff (sin x) x)                    →  cos(x)
(diff (log x) x)                    →  1/x
(diff (exp x) x)                    →  exp(x)
(diff (* x (exp x)) x)              →  x*exp(x) + exp(x)
```

## 积分

```scheme
; 不定积分
(integrate (* x x) x)               →  x**3/3
(integrate (sin x) x)               →  -cos(x)
(integrate (exp (- x)) x)           →  -exp(-x)

; 定积分
(integrate (* x x) x 0 1)           →  1/3
(integrate (sin x) x 0 (/ pi 2))    →  1
(integrate (exp (- x)) x 0 (inf))   →  1
```

## 极限

```scheme
(limit (/ (sin x) x) x 0)           →  1
(limit (/ 1 x) x (inf))             →  0
(limit (/ 1 x) x 0 'plus)          →  oo
(limit (/ 1 x) x 0 'minus)         →  -oo
(limit (exp x) x '-inf)            →  0
```

## 级数展开

```scheme
(series (sin x) x 0 5)              →  x - x**3/6 + O(x**5)
(series (cos x) x 0 5)              →  1 - x**2/2 + x**4/24 + O(x**5)
(series (exp x) x 0 4)              →  1 + x + x**2/2 + x**3/6 + O(x**4)
(series (log (+ 1 x)) x 0 4)        →  x - x**2/2 + x**3/3 + O(x**4)

(taylor (sin x) x 0 5)             →  x - x**3/6 + O(x**5)
```

## 求和/求积

```scheme
(summation (/ 1 (** x 2)) (list x 1 (inf)))  →  pi**2/6
(product x (list x 1 5))           →  120
(summation x (list x 1 100))       →  5050
```

## 向量微积分

```scheme
; 梯度
(grad (* x x) x)                   →  [2*x]

; Hessian 矩阵
(hessian (* x x) (list x))          →  [[2]]

; Jacobian 矩阵
(define y (sympy.Symbol 'y'))
(jacobian (list (* x x) (* x x x)) (list x))
  → Matrix([[2*x], [3*x**2]])

(jacobian (list (* x y) (+ x y)) (list x y))
  → Matrix([[y, x], [1, 1]])
```