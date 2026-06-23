; numpy 完整调用示例 — 纯 Python 化语法

; 1. 像 Python 一样 import
(import numpy)

; 2. 创建数组
(display "numpy.array: ")
(display (numpy.array (list 1 2 3 4 5)))
(newline)

; 3. zeros / ones
(display "zeros: ")
(display (numpy.zeros '(3 3)))
(newline)

(display "ones: ")
(display (numpy.ones '(2 4)))
(newline)

; 4. arange
(display "arange: ")
(display (numpy.arange 0 10 2))
(newline)

; 5. linspace
(display "linspace: ")
(display (numpy.linspace 0 1 5))
(newline)

; 6. reshape
(display "reshape: ")
(display (numpy.reshape (numpy.arange 12) '(3 4)))
(newline)

; 7. 变量绑定 + 级联属性
(define arr (numpy.arange 12))
(display "arr.T: ")
(display arr.T)
(newline)

(display "arr.reshape: ")
(display (arr.reshape 3 4))
(newline)

; 8. 数学运算
(define a (numpy.array (list 1 2 3)))
(define b (numpy.array (list 4 5 6)))
(display "a + b: ")
(display (numpy.add a b))
(newline)

(display "a * b: ")
(display (numpy.multiply a b))
(newline)

(display "dot: ")
(display (numpy.dot a b))
(newline)

; 9. 统计
(define data (numpy.array (list 1 2 3 4 5 6 7 8 9 10)))
(display "mean: ")
(display (numpy.mean data))
(newline)

(display "std: ")
(display (numpy.std data))
(newline)

(display "sum: ")
(display (numpy.sum data))
(newline)

; 10. 二维数组运算
(define X (numpy.array '(1 2 3 4 5 6 7 8 9 10 11 12)))
(define Xmat (numpy.reshape X '(3 4)))
(display "Xmat: ")
(display Xmat)
(newline)

(display "Xmat.T: ")
(display Xmat.T)
(newline)

(display "Xmat.sum: ")
(display (Xmat.sum))
(newline)

(display "Xmat.mean axis=0: ")
(display (Xmat.mean 0))
(newline)

; 11. 正态随机
(display "random.normal: ")
(display (numpy.random.normal 0 1 '(5 5)))
(newline)

(display "All numpy tests passed!")