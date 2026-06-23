; 验证 Python 互操作使用 Vector

(import numpy as np)

; 1. py-eval 返回 Python list 现在变成 Vector
(display "py-eval list: ")
(display (py-eval "[1, 2, 3, 4, 5]"))
(newline)

; 2. 用 Vector 字面量直接传给 numpy
(display "np.array with vector: ")
(display (np.array '#(1 2 3 4 5)))
(newline)

; 3. 嵌套 Vector → 二维数组
(display "np.array 2D with vector: ")
(display (np.array '#(#(1 2) #(3 4) #(5 6))))
(newline)

; 4. sympy 矩阵用 Vector
(import sympy)
(define A (sympy.Matrix '#(#(1 2) #(3 4))))
(display "sympy.Matrix with vector: ")
(display A.det)
(newline)

; 5. numpy 操作返回 Vector
(display "arange as vector: ")
(display (np.arange 0 5))
(newline)

; 6. Vector 作为参数传给 Python（unwrap 自动转 list）
(display "concatenate with vectors: ")
(display (np.concatenate '#(#(1 2) #(3 4))))
(newline)

; 7. (list ...) 仍然可用（向后兼容）
(display "np.array with list (compat): ")
(display (np.array (list 1 2 3)))
(newline)

(display "All vector interop tests passed!")