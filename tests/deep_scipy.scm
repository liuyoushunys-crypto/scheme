; ============================================================
; 深度测试 2/5: scipy — 全子模块覆盖
; ============================================================

(import scipy)
(import numpy as np)

(display "=== scipy 1.17.1 深度测试 ===\n")

; ----- 2.1 optimize -----
(display "\n--- 2.1 optimize ---")
(newline)

(import scipy.optimize)

; 无约束
(display "minimize scalar: ")
(display (scipy.optimize.minimize (lambda (x) (expt (- x 3) 2)) 0))
(newline)

; 带约束 — 用 py-dict 创建 Python 字典
(display "minimize with constraint: ")
(display (scipy.optimize.minimize (lambda (x) (expt (- (py-get x 0) 2) 2)) '#(0) :constraints (list (py-dict :type "eq" :fun (lambda (x) (- (py-get x 0) 1))))))
(newline)

; 曲线拟合 — 多参数 lambda
(display "curve_fit: ")
(define xd (np.array '#(0 1 2 3 4)))
(define yd (np.array '#(1 3 5 7 9)))
(display (scipy.optimize.curve_fit (lambda (x a b) (+ (* a x) b)) xd yd))
(newline)

; 根求解
(display "root: ")
(display (scipy.optimize.root (lambda (x) (- (expt x 2) 2)) 1.5))
(newline)

; ----- 2.2 stats -----
(display "\n--- 2.2 stats ---")
(newline)

(import scipy.stats)

; 分布
(display "norm.pdf: ")
(display (scipy.stats.norm.pdf 0))
(newline)

(display "norm.cdf: ")
(display (scipy.stats.norm.cdf 1.96))
(newline)

(display "norm.ppf 0.975: ")
(display (scipy.stats.norm.ppf 0.975))
(newline)

(display "norm.rvs size=5: ")
(scipy.stats.norm.rvs :size 5 :random_state 42)
(newline)

; 分布参数
(display "t.ppf 0.95 10: ")
(display (scipy.stats.t.ppf 0.95 10))
(newline)

(display "chi2.ppf: ")
(display (scipy.stats.chi2.ppf 0.95 5))
(newline)

; 假设检验
(display "ttest_ind: ")
(display (scipy.stats.ttest_ind '#(1 2 3 4 5) '#(2 3 4 5 6)))
(newline)

(display "kstest: ")
(display (scipy.stats.kstest '#(1 2 3 4 5) 'norm))
(newline)

; 描述统计
(display "describe: ")
(display (scipy.stats.describe '#(1 2 3 4 5 6 7 8 9 10)))
(newline)

; ----- 2.3 signal -----
(display "\n--- 2.3 signal ---")
(newline)

(import scipy.signal)

; 滤波器设计
(display "butter: ")
(display (scipy.signal.butter 4 0.2))
(newline)

(display "freqz: ")
(display (scipy.signal.freqz '#(0.1 0.2 0.1)))
(newline)

; 卷积
(display "convolve: ")
(display (scipy.signal.convolve '#(1 2 3) '#(0 1 0.5)))
(newline)

; ----- 2.4 linalg -----
(display "\n--- 2.4 linalg ---")
(newline)

(import scipy.linalg)

(define M (np.array '#(#(3 1) #(1 2))))
(display "inv: ")
(display (scipy.linalg.inv M))
(newline)

(display "det: ")
(display (scipy.linalg.det M))
(newline)

(display "eig: ")
(display (scipy.linalg.eig M))
(newline)

(display "svd: ")
(display (scipy.linalg.svd M))
(newline)

(display "lu: ")
(display (scipy.linalg.lu M))
(newline)

(display "qr: ")
(display (scipy.linalg.qr M))
(newline)

(display "cholesky: ")
(define pos (np.array '#(#(4 2) #(2 3))))
(display (scipy.linalg.cholesky pos))
(newline)

(display "solve: ")
(display (scipy.linalg.solve M '#(9 8)))
(newline)

; ----- 2.5 integrate -----
(display "\n--- 2.5 integrate ---")
(newline)

(import scipy.integrate)

(display "quad: ")
(display (scipy.integrate.quad (lambda (x) (exp (- (expt x 2)))) 0 np.inf))
(newline)

(display "dblquad: ")
(display (scipy.integrate.dblquad (lambda (x y) (* x y)) 0 1 (lambda (x) 0) (lambda (x) 1)))
(newline)

; ----- 2.6 interpolate -----
(display "\n--- 2.6 interpolate ---")
(newline)

(import scipy.interpolate)

(define xpts (np.array '#(0 1 2 3 4)))
(define ypts (np.array '#(0 2 4 6 8)))
(define spl (scipy.interpolate.CubicSpline xpts ypts))
(display "CubicSpline(2.5): ")
(display (py-str (spl 2.5)))
(newline)

; ----- 2.7 special -----
(display "\n--- 2.7 special ---")
(newline)

(import scipy.special)

(display "gamma: ")
(display (scipy.special.gamma 5))
(newline)

(display "erf: ")
(display (scipy.special.erf 1))
(newline)

(display "bessel jv: ")
(display (scipy.special.jv 0 1))
(newline)

(display "airy: ")
(display (scipy.special.airy 0))
(newline)

(display "=== scipy 深度测试完成 ===\n")
(newline)