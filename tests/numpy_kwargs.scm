; numpy 完整调用 — 含关键词参数

(import numpy)

; 1. 基础数组
(display "array with dtype: ")
(display (numpy.array '(1 2 3) :dtype numpy.float64))
(newline)

; 2. arange with dtype
(display "arange with dtype: ")
(display (numpy.arange 0 5 :dtype numpy.float32))
(newline)

; 3. random 带分布参数
(display "poisson: ")
(display (numpy.random.poisson 3.0 '(2 5)))
(newline)

; 4. axis 关键词
(define X (numpy.reshape (numpy.arange 12) '(3 4)))
(display "X: ")
(display X)
(newline)

(display "sum axis=0: ")
(display (numpy.sum X :axis 0))
(newline)

(display "sum axis=1: ")
(display (numpy.sum X :axis 1))
(newline)

; 5. 高级索引
(display "argsort: ")
(define vals (numpy.array '(3 1 4 1 5 9 2 6)))
(display (numpy.argsort vals))
(newline)

; 6. 数组操作
(display "concatenate: ")
(display (numpy.concatenate (list (numpy.array '(1 2)) (numpy.array '(3 4))) :axis 0))
(newline)

; 7. 矩阵乘法风格
(define A (numpy.reshape (numpy.arange 6) '(2 3)))
(define B (numpy.reshape (numpy.arange 6) '(3 2)))
(display "matmul: ")
(display (numpy.matmul A B))
(newline)

; 8. 随机种子
(numpy.random.seed 42)
(display "seeded random: ")
(display (numpy.random.rand 3))
(newline)

(display "All keyword + numpy tests passed!")