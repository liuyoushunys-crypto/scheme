; 测试括号语法
(import numpy as np)

(display "bracket test 1: ")
(define arr (np.arange 12))
(display [arr 5])
(newline)

(display "bracket slice: ")
(display [arr 2 8 2])
(newline)

(display "bracket multi-dim: ")
(define m (. (np.arange 24) reshape 4 6))
(display [m 1 2])
(newline)

(display "bracket 2-index slice: ")
(display [m (py-slice 1 3) (py-slice 2 5)])
(newline)

(display "ALL bracket tests passed!")
(newline)