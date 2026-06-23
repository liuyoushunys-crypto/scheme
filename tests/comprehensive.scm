; === 全面覆盖测试：痛点和流畅度 ===

; 自动导入父包验证
(import sympy)
(import numpy as np)
(import scipy.optimize scipy.integrate scipy.special scipy.linalg)

; === 1. defsym 宏——便捷符号创建 ===
(defsym x y z)
(display "x + y + z: ")
(display (+ x y z))
(newline)

; sympy.abc 内置符号
(display "sympy.abc.x: ")
(display sympy.abc.x)
(newline)

; === 2. sympy ↔ str ↔ Scheme 三向自由转换 ===
(define expr (+ (* 2 (expt x 2)) (* 3 x) 1))

; sympy → str
(display "py-str: ")
(display (py-str expr))
(newline)

; sympy → srepr (Python 表达式字符串，可 eval 重建)
(display "srepr: ")
(display (py-str (sympy.srepr expr)))
(newline)

; sympy → latex
(display "latex: ")
(display (py-str (sympy.latex expr)))
(newline)

; sympy → pretty
(display "pretty: ")
(display (py-str (sympy.printing.pretty expr)))
(newline)

; str → sympy via sympify
(display "sympify str -> sympy: ")
(display (sympy.sympify "x**2 + 2*x + 1"))
(newline)

; 三向转换完成。
; Scheme expr → str: 引用显示
(display "scheme -> str: ")
(display '(+ x 1))
(newline)

; === 3. sympy 数值与微积分 ===
(display "expr.subs x 2: ")
(display (expr.subs x 2))
(newline)

(display "expr.evalf 10: ")
(display (expr.evalf 10))
(newline)

(display "diff sin(x) -> cos(x): ")
(display (sympy.diff (sin x) x))
(newline)

(display "integrate x^2: ")
(display (sympy.integrate (expt x 2) x))
(newline)

; === 4. scipy 集成（父包自动导入验证）===
(display "minimize rosen: ")
(define rosen (lambda (x) (scipy.optimize.rosen x)))
(display (scipy.optimize.minimize rosen '#(-1.5 1.5) :method 'Nelder-Mead))
(newline)

(display "quad exp(-x^2): ")
(display (scipy.integrate.quad (lambda (x) (exp (- (expt x 2)))) 0 np.inf))
(newline)

(display "gamma 5: ")
(display (scipy.special.gamma 5))
(newline)

(display "eigvals: ")
(display (scipy.linalg.eigvals '#(#(3 1) #(1 2))))
(newline)

; === 5. statsmodels ===
(import statsmodels.api as sm)
(define Xmat (sm.add_constant '#(1 2 3 4 5)))
(define yvec '#(2 4 5 4 5))
(define model (sm.OLS yvec Xmat))
(define results (model.fit))
(display "params: ")
(display results.params)
(newline)
(display "rsquared: ")
(display results.rsquared)
(newline)

; === 6. mpmath ===
(import mpmath)
(set! mpmath.mp.dps 50)
(display "mpmath.pi (50 digits): ")
(display mpmath.pi)
(newline)

; === 7. sympy 方程 ===
(display "solve x^2 + x - 1: ")
(display (sympy.solve (+ (expt x 2) x -1) x))
(newline)

; === 8. 矩阵运算 ===
(display "np.linalg.solve: ")
(display (np.linalg.solve '#(#(3 1) #(1 2)) '#(9 8)))
(newline)

(display "=== 全面覆盖测试通过 ===")
(newline)