; 测试原生 obj.method 语法
(import numpy as np)

(define a (np.arange 12))

; reshape as function call
(display "a.reshape 3 4: ")
(display (a.reshape 3 4))
(newline)

; chain calls: a.reshape(3,4).T
(display "a.reshape.T: ")
(define r (a.reshape 3 4))
(display r.T)
(newline)

(display "=== dot method tests passed ===")
(newline)