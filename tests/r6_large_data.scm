; ============================================================
; R6: 大数据/性能边缘测试
; ============================================================

(import numpy as np scipy)
(import scipy.linalg scipy.sparse)

(display "=== R6: Large Data & Performance ===\\n")

; ----- 6.1 大数组 -----
(display "\\n--- 6.1 Large Arrays ---")
(newline)

(display "big zeros 1000x1000: ")
(define big (np.zeros '(1000 1000)))
(display (np.shape big))
(newline)

(display "big ones: ")
(define big_one (np.ones '(500 500)))
(display (np.shape big_one))
(newline)

; ----- 6.2 大矩阵运算 -----
(display "\\n--- 6.2 Large Matrix Ops ---")
(newline)

(define A (np.random.rand 200 200))
(define B (np.random.rand 200 200))
(display "200x200 dot: ")
(define C (np.dot A B))
(display (np.shape C))
(newline)

(display "200x200 svd: ")
(define SVD (scipy.linalg.svd A))(define U (py-get SVD 0))(display (np.shape U))
(display (np.shape U))
(newline)

; ----- 6.3 稀疏线性系统 -----
(display "\\n--- 6.3 Sparse Linear Systems ---")
(newline)

(define n 500)
(define diag_vals (np.ones n))
(define off_vals (np.full (- n 1) -0.5))
(define A_sp (scipy.sparse.diags (list diag_vals off_vals off_vals) '#(0 -1 1)))
(define b_sp (np.ones n))
(display "solve sparse: ")
(define x_sp (scipy.sparse.linalg.spsolve A_sp b_sp))
(display (np.shape x_sp))
(newline)

; ----- 6.4 numba JIT -----
(display "\\n--- 6.4 Numba JIT ---")
(newline)

(import numba)
(define @njit (numba.njit))
; 用闭包绕行
(display "numba njit decorator: ")
(display (py-str @njit))
(newline)

; ----- 6.5 内存视图和切片 -----
(display "\\n--- 6.5 Memory Views ---")
(newline)

(define huge (np.arange 10000))
(define view (huge.reshape 100 100))
(display "view (100,100): ")
(display (np.shape view))
(newline)

(define sliced (py-get view (py-slice 10 20)))
(display "sliced (10,100): ")
(display (np.shape sliced))
(newline)

(display "=== R6 Complete ===\\n")
(newline)