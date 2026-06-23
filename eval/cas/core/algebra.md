# core/algebra — 代数运算

(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))
(define y (sympy.Symbol 'y))

## 展开/因式分解

(expand (* (+ x 1) (+ x 2)))          →  2 + 3*x + x**2
(expand (* (+ x y) 2))                →  2*x + 2*y

(factor (- (* x x) 1))                →  (x - 1)*(x + 1)
(factor (+ (* x x) (* 3 x) 2))        →  (x + 1)*(x + 2)

## 化简

(simplify (/ (+ (* x x) x) x))         →  x + 1
(simplify (sin (* 2 x)))               →  2*sin(x)*cos(x)
(simplify (* (sin x) (cos x)))         →  sin(2*x)/2

## 部分分式

(apart (/ 1 (- (* x x) 1)))            →  1/(2*x - 2) - 1/(2*x + 2)
(together (+ (/ 1 (- x 1)) (/ 1 (+ x 1))))  →  2*x/(x**2 - 1)

## 符号操作

(collect (+ (* 3 x) (* 2 x)) x)        →  5*x
(coeff (+ (* 5 (* x x)) (* 3 x) 1) x 2) →  5
(normal (/ x (/ 1 x)))                 →  x**2
(resultant (* x x - 1) (+ (* x x) 1) x) →  1
(discriminant (+ (* x x) (* 3 x) 2) x) →  1

## 联立方程求解

(solve (list (+ (* 2 x) y 7) (+ x (* -1 y) 4)) (list x y))
  → {x: -1, y: -5}

## 多项式操作

(degree (* x x x))                     →  3
(LC (* x x x))                         →  1          ; leading coefficient
(LM (* x x x))                         →  x**3      ; leading monomial
(LT (* x x x))                         →  x**3      ; leading term
(quo (+ (* x x) -1) (+ x -1))          →  x + 1
(rem (+ (* x x) -1) (+ x -1))          →  0
(subresultants (* x x - 1) (+ (* x x) 1) x)
</parameter>
<｜DSML｜parameter name="path" string="true">/workspace/99/eval/cas/core/algebra/demo.md