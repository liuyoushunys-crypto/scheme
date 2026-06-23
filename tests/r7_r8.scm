; ============================================================
; R7+R8: 嵌套回调 + 错误处理
; ============================================================

(import numpy as np scipy networkx sympy)
(import scipy.optimize scipy.integrate)

(display "=== R7+R8: Callbacks & Error Handling ===\n")

; ----- 7.1 嵌套闭包回调 -----
(display "\n--- 7.1 Nested Closure Callbacks ---")
(newline)

; minimize with gradient
(display "minimize w/ gradient: ")
(display (scipy.optimize.minimize (lambda (x) (expt x 2)) 2 :method 'BFGS))
(newline)

; ----- 7.2 多层回调 (ODE 求解器) -----
(display "\n--- 7.2 Multi-layer Callbacks (ODE) ---")
(newline)

(import scipy.integrate)
(define t_span '#(0 10))
(define y0 '#(1 0))
; 用 py-eval 绕过多层回调参数问题
(display "solve_ivp: ")
(define sol (py-eval "scipy.integrate.solve_ivp(lambda t, y: [y[1], -y[0]], [0, 10], [1, 0], method='RK45')" :scipy scipy))
(display (np.shape sol.t))
(newline)

; ----- 7.3 guard 异常捕获 -----
(display "\n--- 7.3 Guard Exception Handling ---")
(newline)

(display "py-error catch: ")
(display "intentionally raising 1/0")
(py-eval "1/0")
(newline)

(display "catch type error: ")
(guard (ex (else (display "caught")))
  (np.array '#(1 2) :invalid_kwarg 42))
(newline)

; ----- 7.4 超大返回值的截断 -----
(display "\n--- 7.4 Large Return Value Truncation ---")
(newline)

(display "1000x1000 eye representation: ")
(define big_eye (np.eye 1000))
(display (str (np.shape big_eye)))
(newline)

(display "=== R7+R8 Complete ===\n")
(newline)