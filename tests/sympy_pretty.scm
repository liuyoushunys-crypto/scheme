; sympy 漂亮打印

(import sympy)

(define x (sympy.Symbol 'x))

; 使用 sympy.pprint 获得更漂亮的输出
(display "=== sympy.pprint ===")
(newline)
(sympy.pprint (+ (expt x 2) (* 2 x) 1))
(newline)

(display "=== sympy.pretty_print ===")
(newline)
(sympy.pretty_print (sin x))
(newline)

(display "=== sympy.printing.pretty ===")
(newline)
(display (sympy.printing.pretty (sympy.integrate (sin x) x)))
(newline)

(display "=== latex ===")
(newline)
(display (sympy.latex (sympy.integrate (sin x) x)))
(newline)

(display "Done!")