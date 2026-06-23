; ============================================================
; 增强型 CAS 全功能演示
; ============================================================

(import sympy)
(import sympy.abc)
(defsym x y z t s n k a b)

; ===================== 1. 向量微积分 =====================
(display "=== Vector Calculus ===")
(newline)

(display "grad x**2 + y**2: ")
(display (grad (+ (expt x 2) (expt y 2)) x y))
(newline)

(display "hessian: ")
(display (hessian (+ (* 3 (expt x 2)) (* 2 x y) (expt y 2)) x y))
(newline)

(display "jacobian: ")
(display (jacobian (list (+ x y) (- x y)) x y))
(newline)

; ===================== 2. 三角/对数简化 =====================
(display "=== Trig & Log Simplification ===")
(newline)

(display "trigexpand: ")
(display (trigexpand (sin (+ x y))))
(newline)

(display "trigsimp: ")
(display (trigsimp (sin (+ x y))))
(newline)

(display "trigsimp identity: ")
(display (trigsimp (+ (expt (sin x) 2) (expt (cos x) 2))))
(newline)

(display "logcombine: ")
(display (logcombine (+ (log x) (log y))))
(newline)

(display "powsimp: ")
(display (powsimp (* (expt x a) (expt x b))))
(newline)

; ===================== 3. 部分分式 =====================
(display "=== Partial Fractions ===")
(newline)

(display "apart: ")
(display (apart (/ 1 (+ (expt x 2) (* -5 x) 6)) x))
(newline)

(display "together: ")
(display (together (+ (/ 1 (+ x 1)) (/ 2 (+ x 2)))))
(newline)

; ===================== 4. 代数进阶 =====================
(display "=== Advanced Algebra ===")
(newline)

(display "collect: ")
(display (collect (+ (* 2 (expt x 2)) (* 3 x) (expt x 2)) x))
(newline)

(display "coeff: ")
(display (coeff (+ (* 3 (expt x 2)) (* 2 x) 1) x 2))
(newline)

(display "resultant: ")
(display (resultant (+ (expt x 2) 1) (expt x 5) x))
(newline)

(display "discriminant: ")
(display (discriminant (+ (expt x 2) (* -4 x) 4) x))
(newline)

; ===================== 5. 傅里叶变换 =====================
(display "=== Fourier Transform ===")
(newline)

(display "fourier: ")
(display (fourier (exp (- (expt x 2))) x k))
(newline)

; ===================== 6. 数论 =====================
(display "=== Number Theory ===")
(newline)

(display "prime? 17: ")
(display (prime? 17))
(newline)

(display "factorint 84: ")
(display (factorint 84))
(newline)

(display "divisors 12: ")
(display (divisors 12))
(newline)

(display "totient 10: ")
(display (totient 10))
(newline)

(display "primerange 10 30: ")
(display (primerange 10 30))
(newline)

; ===================== 7. 集合 =====================
(display "=== Sets ===")
(newline)

(define s1 (set 1 2 3 4))
(define s2 (set 3 4 5 6))
(display "s1: ")
(display s1)
(newline)

(display "union: ")
(display (union s1 s2))
(newline)

(display "intersection: ")
(display (intersection s1 s2))
(newline)

(display "subset?: ")
(display (subset? s1 s2))
(newline)

(display "element? 3 in s1: ")
(display (element? 3 s1))
(newline)

; ===================== 8. 统计 =====================
(display "=== Statistics ===")
(newline)

(display "mean: ")
(display (mean '#(1 2 3 4 5)))
(newline)

(display "std: ")
(display (std '#(1 2 3 4 5)))
(newline)

(display "correlation: ")
(display (correlation '#(1 2 3 4 5) '#(2 4 6 8 10)))
(newline)

; ===================== 9. 特殊函数 =====================
(display "=== Special Functions ===")
(newline)

(display "lambertw: ")
(display (lambertw 1))
(newline)

(display "stirling 5 2: ")
(display (stirling 5 2))
(newline)

(display "bernoulli 10: ")
(display (bernoulli 10))
(newline)

(display "fibonacci 20: ")
(display (fibonacci 20))
(newline)

(display "=== Enriched CAS Demo Complete ===")
(newline)