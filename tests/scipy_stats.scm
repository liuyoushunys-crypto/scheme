; === scipy 全面测试 ===

(import scipy)
(import scipy.optimize)
(import scipy.stats)
(import scipy.linalg)
(import numpy as np)

(display "=== scipy.optimize ===")
(newline)

; 定义目标函数 (Rosenbrock)
(define rosen (lambda args (scipy.optimize.rosen (car args))))
(display "minimize rosen: ")
(display (scipy.optimize.minimize rosen '#(1.3 0.7) :method 'Nelder-Mead))
(newline)
(newline)

(display "=== scipy.stats ===")
(newline)

(display "norm.ppf 0.95: ")
(display (scipy.stats.norm.ppf 0.95))
(newline)

(display "norm.pdf 0: ")
(display (scipy.stats.norm.pdf 0))
(newline)

(display "norm.rvs size=5: ")
(scipy.stats.norm.rvs :size 5)
(newline)

(display "ttest_ind: ")
(display (scipy.stats.ttest_ind '#(1 2 3 4 5) '#(2 3 4 5 6)))
(newline)
(newline)

(display "=== scipy.linalg ===")
(newline)

(define A (np.array '#(#(1 2) #(3 4))))
(display "inv: ")
(display (scipy.linalg.inv A))
(newline)

(display "det: ")
(display (scipy.linalg.det A))
(newline)

(display "eigvals: ")
(display (scipy.linalg.eigvals A))
(newline)
(newline)

(display "=== statsmodels ===")
(newline)

(import statsmodels.api as sm)

; 简单 OLS
(define X (sm.add_constant '#(1 2 3 4 5)))
(define y '#(2 4 5 4 5))
(define model (sm.OLS y X))
(define results (model.fit))
(display "params: ")
(display results.params)
(newline)

(display "rsquared: ")
(display results.rsquared)
(newline)

(display "pvalues: ")
(display results.pvalues)
(newline)

(display "summary: ")
(results.summary)
(newline)

(display "=== mpmath ===")
; --- mpmath 高精度计算 ---

(import mpmath)

; 设置精度（Python 风格）
(set! mpmath.mp.dps 50)
(display "mpmath.mp.dps: ")
(display mpmath.mp.dps)
(newline)

(display "mpmath.pi (50 digits): ")
(display mpmath.pi)
(newline)

(display "mpmath.ellipe 0.5: ")
(display (mpmath.ellipe 0.5))
(newline)

(display "mpmath.zeta 2: ")
(display (mpmath.zeta 2))
(newline)

(display "mpmath.hyp2f1 1 2 3 0.5: ")
(display (mpmath.hyp2f1 1 2 3 0.5))
(newline)

(display "All tests passed!")