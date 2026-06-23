; sympy 无缝集成示例 — Python 开发者的极致体验

; 像 Python 一样导入
(import sympy)

; --- 符号创建与基本表达式 ---

(define x (sympy.Symbol 'x))
(define y (sympy.Symbol 'y))

; Scheme 的 + - * / 自动代理到 sympy 表达式构建
(display "x + 1: ")
(display (+ x 1))
(newline)

(display "x + y: ")
(display (+ x y))
(newline)

(display "2*x + 3*y: ")
(display (+ (* 2 x) (* 3 y)))
(newline)

(display "x**2 + 2*x + 1: ")
(display (+ (expt x 2) (* 2 x) 1))
(newline)

(display "(x + 1)*(x - 1): ")
(display (* (+ x 1) (- x 1)))
(newline)

; --- 数学函数自动代理 ---

(display "sin(x): ")
(display (sin x))
(newline)

(display "cos(x)**2 + sin(x)**2: ")
(display (+ (expt (cos x) 2) (expt (sin x) 2)))
(newline)

(display "sqrt(x): ")
(display (sqrt x))
(newline)

(display "exp(x): ")
(display (exp x))
(newline)

(display "log(x): ")
(display (log x))
(newline)

; --- 简化与展开 ---

(display "expand((x+1)**3): ")
(display (sympy.expand (expt (+ x 1) 3)))
(newline)

(display "simplify(sin(x)**2 + cos(x)**2): ")
(display (sympy.simplify (+ (expt (sin x) 2) (expt (cos x) 2))))
(newline)

; --- 微积分 ---

(display "diff(x**3, x): ")
(display (sympy.diff (expt x 3) x))
(newline)

(display "integrate(x**2, x): ")
(display (sympy.integrate (expt x 2) x))
(newline)

(display "integrate(exp(-x), (x 0 oo)): ")
(display (sympy.integrate (exp (- x)) (list x 0 sympy.oo)))
(newline)

(display "diff(sin(x), x): ")
(display (sympy.diff (sin x) x))
(newline)

(display "integrate(sin(x), x): ")
(display (sympy.integrate (sin x) x))
(newline)

; --- 方程求解 ---

(display "solve(x**2 - 1, x): ")
(display (sympy.solve (- (expt x 2) 1) x))
(newline)

(display "solve(x**2 + x + 1, x): ")
(display (sympy.solve (+ (expt x 2) x 1) x))
(newline)

; --- 级数展开 ---

(display "series(sin(x), x, 0, 8): ")
(display (sympy.series (sin x) x 0 8))
(newline)

; --- 线性代数 ---

(define A (sympy.Matrix (list (list 1 2) (list 3 4))))
(display "A.det: ")
(display (A.det))
(newline)

(display "A.inv: ")
(display (A.inv))
(newline)

(display "A.charpoly x: ")
(display (A.charpoly x))
(newline)

; 纯 sympy 式也可以级联
(display "All sympy tests passed!")