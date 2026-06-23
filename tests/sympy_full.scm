; === sympy 全模块覆盖测试 ===

(import sympy)
(import sympy.abc)
(defsym x y z n)

(display "=== 1. 核心运算 ===")
(newline)

; 符号运算
(display "x + y - z: ")
(display (+ x y (- z)))
(newline)

(display "2*x**3 + 3*x**2 - 5: ")
(display (+ (* 2 (expt x 3)) (* 3 (expt x 2)) -5))
(newline)

; 分数
(display "Rational(1,3) + Rational(1,6): ")
(display (+ (sympy.Rational 1 3) (sympy.Rational 1 6)))
(newline)

; 特殊常数
(display "sympy.pi: ")
(display sympy.pi)
(newline)

(display "sympy.E: ")
(display sympy.E)
(newline)

(display "sympy.I: ")
(display sympy.I)
(newline)

(display "sympy.oo: ")
(display sympy.oo)
(newline)

; === 2. 微积分 ===
(display "=== 2. Calculus ===")
(newline)

(display "diff(x**3, x): ")
(display (sympy.diff (expt x 3) x))
(newline)

(display "integrate(x**2, (x 0 1)): ")
(display (sympy.integrate (expt x 2) (list x 0 1)))
(newline)

(display "limit(sin(x)/x, x, 0): ")
(display (sympy.limit (/ (sin x) x) x 0))
(newline)

(display "series(exp(x), x, 0, 5): ")
(display (sympy.series (exp x) x 0 5))
(newline)

(display "Sum(x**n, (n 1 10)): ")
(display (sympy.Sum (expt x n) (list n 1 10)))
(newline)

(display "summation(x**n, (n 1 10)): ")
(display (sympy.summation (expt x n) (list n 1 10)))
(newline)

(display "Product(n, (n 1 5)): ")
(display (sympy.Product n (list n 1 5)))
(newline)

; === 3. 代数和方程 ===
(display "=== 3. Algebra ===")
(newline)

(display "expand((x+1)**5): ")
(display (sympy.expand (expt (+ x 1) 5)))
(newline)

(display "factor(x**4 - 1): ")
(display (sympy.factor (- (expt x 4) 1)))
(newline)

(display "simplify((x**2 - 1)/(x - 1)): ")
(display (sympy.simplify (/ (- (expt x 2) 1) (- x 1))))
(newline)

(display "solve(x**2 - 2, x): ")
(display (sympy.solve (- (expt x 2) 2) x))
(newline)

(display "solve([x + y - 2, x - y], [x, y]): ")
(display (sympy.solve (list (+ x y -2) (- x y)) (list x y)))
(newline)

; === 4. 矩阵 ===
(display "=== 4. Matrices ===")
(newline)

(define M (sympy.Matrix (list (list 1 2) (list 3 4))))
(display "M.det: ")
(display (M.det))
(newline)

(display "M.inv: ")
(display (M.inv))
(newline)

(display "M.eigenvals: ")
(display (M.eigenvals))
(newline)

(display "M.eigenvects: ")
(display (M.eigenvects))
(newline)

(display "M.charpoly: ")
(display (M.charpoly x))
(newline)

(display "eye(3): ")
(display (sympy.eye 3))
(newline)

(display "zeros(2,3): ")
(display (sympy.zeros 2 3))
(newline)

(display "M.T: ")
(display M.T)
(newline)

(display "M**2: ")
(display (expt M 2))
(newline)

; === 5. 多项式 ===
(display "=== 5. Polynomials ===")
(newline)

(define poly (sympy.Poly (+ (expt x 2) (* 2 x) 1) x))
(display "Poly.coeffs: ")
(display (poly.coeffs))
(newline)

(display "Poly.roots (via sympy.roots): ")
(display (sympy.roots poly x))
(newline)

(display "Poly.degree: ")
(display (poly.degree))
(newline)

(display "Poly.nroots: ")
(display (poly.nroots))
(newline)

(display "groebner: ")
(display (sympy.groebner (list (+ (expt x 2) (expt y 2) -1) (- x y))))
(newline)

; === 6. 特殊函数 ===
(display "=== 6. Special Functions ===")
(newline)

(display "gamma(5): ")
(display (sympy.gamma 5))
(newline)

(display "besselj(0, x): ")
(display (sympy.besselj 0 x))
(newline)

(display "zeta(2): ")
(display (sympy.zeta 2))
(newline)

(display "Ei(x): ")
(display (sympy.Ei x))
(newline)

(display "Si(x): ")
(display (sympy.Si x))
(newline)

; === 7. 数论 ===
(display "=== 7. Number Theory ===")
(newline)

(display "isprime(17): ")
(display (sympy.isprime 17))
(newline)

(display "factorint(84): ")
(display (sympy.factorint 84))
(newline)

(display "nextprime(100): ")
(display (sympy.nextprime 100))
(newline)

(display "primerange(10, 30): ")
(display (sympy.primerange 10 30))
(newline)

(display "primepi(100): ")
(display (sympy.primepi 100))
(newline)

; === 8. 逻辑与集合 ===
(display "=== 8. Logic & Sets ===")
(newline)

(display "sympy.true: ")
(display sympy.true)
(newline)

(display "sympy.And(x > 0, x < 1): ")
(display (sympy.And (> x 0) (< x 1)))
(newline)

(display "sympy.Interval(0, 1): ")
(display (sympy.Interval 0 1))
(newline)

(display "FiniteSet(1, 2, 3): ")
(display (sympy.FiniteSet 1 2 3))
(newline)

; === 9. 几何 ===
(display "=== 9. Geometry ===")
(newline)

(define pt (sympy.Point 0 0))
(define line (sympy.Line pt (sympy.Point 1 1)))
(display "Line: ")
(display line)
(newline)

(display "Line.coefficients: ")
(display line.coefficients)
(newline)

(display "distance: ")
(display (pt.distance (sympy.Point 3 4)))
(newline)

; === 10. 物理 ===
(display "=== 10. Physics ===")
(newline)

(display "sympy.physics.units.m: ")
(display sympy.physics.units.m)
(newline)

(display "sympy.physics.units.s: ")
(display sympy.physics.units.s)
(newline)

; === 11. 解析与打印 ===
(display "=== 11. Parsing & Printing ===")
(newline)

(display "parsing: ")
(display (sympy.parsing.sympy_parser.parse_expr "x**2 + 3*x"))
(newline)

(display "ccode: ")
(display (py-str (sympy.printing.ccode (+ (expt x 2) (* 3 x) 1))))
(newline)

(display "fcode: ")
(display (py-str (sympy.printing.fcode (+ (expt x 2) (* 3 x) 1))))
(newline)

(display "mathml: ")
(display (py-str (sympy.printing.mathml (+ (expt x 2) (* 3 x) 1))))
(newline)

(display "All sympy full tests passed!")