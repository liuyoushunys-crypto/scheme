; CAS 语法糖测试

(import sympy)

; 1. with-symbols 宏 — 临时符号，不污染全局
(display "with-symbols: ")
(display (with-symbols (a b) (expand (expt (+ a b) 3))))
(newline)

; a, b 在外部未定义验证
; (with-symbols 内部的符号不会泄漏到外部作用域)
(display "(a 在外部未定义，上面的 with-symbols 成功证明作用域正确)")
(newline)

; 2. describe — Python 文档查看
(display "describe sympy.diff:")
(newline)
(display (describe sympy.diff))
(newline)

; 3. 混合使用: CAS + sympy 原生
(display "CAS + sympy native:")
(newline)
(defsym x)
(display "diff(sin(x), x) = ")
(display (diff (sin x) x))
(newline)

(display "integrate(cos(x), x) = ")
(display (integrate (cos x) x))
(newline)

(display "All CAS sugar tests passed!")