; ============================================================
; R9+R10: 宏系统扩展 + 最终清扫
; ============================================================

(display "=== R9+R10: Macro DSL & Final Sweep ===\\n")

; ----- 9.1 自动导入宏 -----
(display "\\n--- 9.1 Auto-import macro ---")
(newline)

(define-macro (use . names)
  (cons 'begin
    (map (lambda (n) (list 'import n))
         names)))

; 直接测试宏展开
(display "macro defined: ")
(display )
(newline)

; ----- 9.2 py-> 便捷宏 -----
(display "\\n--- 9.2 py-> macro ---")
(newline)

(define-macro (py-> expr . kwargs)
  (cons 'py-eval (cons (py-str (list 'quote expr)) kwargs)))

; ----- 9.3 for-each 遍历 Python 容器 -----
(display "\\n--- 9.3 Python container iteration ---")
(newline)

(import numpy as np)
(define arr (np.array '#(10 20 30)))
(for-each
  (lambda (v) (display v) (display " "))
  (list (py-get arr 0) (py-get arr 1) (py-get arr 2)))
(newline)

; ----- 9.4 Python 迭代器 -----
(display "\\n--- 9.4 Python iterator interface ---")
(newline)

(define py_iter (py-eval "iter([1,2,3])"))
(display "next: ")
(display (py-eval "next(it)" :it py_iter))
(newline)

(display "next: ")
(display (py-eval "next(it)" :it py_iter))
(newline)

; ----- 9.5 最终回归验证 -----
(display "\\n--- 9.5 Final smoke tests ---")
(newline)

(define smoke1 (np.array '#(1 2 3)))
(display "numpy works: ")
(display (np.sum smoke1))
(newline)

(import sympy)
(defsym x)
(display "sympy works: ")
(display (integrate (sin x) x))
(newline)

(display "=== R9+R10 Complete ===\\n")
(newline)