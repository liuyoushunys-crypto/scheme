# core/special — 特殊函数与方程求解

(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))
(define t (sympy.Symbol 't))

## 方程/多项式

(roots (+ (* x x) (* -3 x) 2))          →  [1, 2]
(roots (+ (* x x) 1))                   →  [-I, I]

(nroots (+ (* x x) (* -3 x) 2))         →  [1.0, 2.0]
(nroots (+ (* x x x) -1))               →  [1.0, -0.5+0.866i, -0.5-0.866i]

## 微分方程

(dsolve (+ (diff (y x) x 2) y))          →  y(x) = C₁·sin(x) + C₂·cos(x)
(dsolve (* (diff (y x) x) -2 (diff (y x) x 2)))  →  y(x) = C₁ + C₂·exp(-2x)

## 拉普拉斯/傅里叶变换

(laplace (sin t) t s)                   →  1/(s**2 + 1)
(laplace (exp (* 2 t)) t s)             →  1/(s - 2)

(inverse-laplace (/ 1 (+ (* s s) 1)) s t)  →  sin(t)

(fourier (exp (- (* x x))) x k)          →  sqrt(pi)*exp(-pi**2*k**2)

## 数论

(factorint 123456789)                   →  {3: 2, 3607: 1, 3803: 1}
(prime? 17)                             →  True
(nextprime 17)                          →  19
(prevprime 17)                          →  13
(phi 12)                                →  4        ; Euler totient
(totient 12)                            →  4
(sigma 6)                               →  12       ; divisor sum
(mobius 6)                              →  1

## 统计

(fibonacci 10)                          →  55
(bell 5)                                →  52
(binomial 5 2)                          →  10
(factorial 5)                           →  120

(mean (list 1 2 3 4 5))                →  3.0
(median (list 1 2 3 4 5))              →  3.0
</parameter>
<｜DSML｜parameter name="path" string="true">/workspace/99/eval/cas/core/special/demo.md