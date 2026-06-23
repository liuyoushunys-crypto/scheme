; 测试 Python 互操作 — Python 风格语法

; 1. (py-import sym) 风格
(py-import math)
(display "pi = ")
(display (py-get math 'pi))
(newline)

; 2. py-call 符号属性
(display "sqrt(16) = ")
(display (py-call (py-get math 'sqrt) 16))
(newline)

; 3. (from module import name) 原生 Python 风格语法
(from math import sin cos)
(display "sin(0) = ")
(display (py-call sin 0))
(newline)
(display "cos(0) = ")
(display (py-call cos 0))
(newline)

; 4. from module import *
(from math import *)
(display "pi = ")
(display pi)
(newline)
(display "e = ")
(display e)
(newline)

; 5. from submodule import name
(from os.path import join)
(display "join(/a, b, c) = ")
(display (py-call join "/a" "b" "c"))
(newline)

; 6. py-import multiple
(py-import json os)
(display "json: ")
(display (py-get json 'dumps))
(newline)

; 7. py-eval
(display "42 + 1 = ")
(display (py-eval "42 + 1"))
(newline)

; 8. py-get with string also works
(display "pi (via string) = ")
(display (py-get math "pi"))
(newline)

; 9. chain
(display "factorial(5) = ")
(display (py-call (py-get math 'factorial) 5))
(newline)

(display "All Python interop tests passed!")