; ============================================================
; 深度测试 1/5: numpy — 全功能覆盖
; ============================================================

(import numpy as np)

(display "=== numpy 2.4.3 深度测试 ===\n")

; ----- 1.1 数组创建 -----
(display "\n--- 1.1 Creation ---")
(newline)

(display "array: ")
(display (np.array '#(1 2 3)))
(newline)

(display "array dtype: ")
(display (np.array '#(1 2 3) :dtype np.float64))
(newline)

(display "zeros: ")
(display (np.zeros '(3 4)))
(newline)

(display "ones: ")
(display (np.ones '(2 3)))
(newline)

(display "full: ")
(display (np.full '(2 3) 7))
(newline)

(display "eye: ")
(display (np.eye 4))
(newline)

(display "identity: ")
(display (np.identity 3))
(newline)

(display "arange: ")
(display (np.arange 0 10 2))
(newline)

(display "linspace: ")
(display (np.linspace 0 1 5))
(newline)

(display "logspace: ")
(display (np.logspace 0 2 5))
(newline)

(display "random.rand: ")
(display (np.random.rand 2 3))
(newline)

(display "random.randint: ")
(display (np.random.randint 0 10 '(3 4)))
(newline)

(display "random.normal: ")
(display (np.random.normal 0 1 '(2 3)))
(newline)

; ----- 1.2 形状操作 -----
(display "\n--- 1.2 Shape Operations ---")
(newline)

(define a (np.arange 12))
(display "reshape: ")
(display (a.reshape 3 4))
(newline)

(display "reshape -1: ")
(display (a.reshape 2 -1))
(newline)

(display "flatten: ")
(display (a.flatten))
(newline)

(display "ravel: ")
(display (np.ravel a))
(newline)

; transpose: 先用变量接
(define ar (a.reshape 3 4))
(display "transpose: ")
(display ar.T)
(newline)

; swapaxes: 用中间变量避免 ).
(define flat24 (np.arange 24))
(define ar3d (flat24.reshape 2 3 4))
(display "swapaxes: ")
(display (ar3d.swapaxes 0 1))
(newline)

(display "expand_dims: ")
(display (np.expand_dims a 0))
(newline)

(display "squeeze: ")
(define sq (np.array '#(#(1) #(2) #(3))))
(display (sq.squeeze))
(newline)

; ----- 1.3 索引与切片 (方括号语法) -----
(display "\n--- 1.3 Indexing & Slicing ---")
(newline)

(define arr (np.arange 12))

(display "arr[5]: ")
(display [arr 5])
(newline)

(display "slice [2:8:2]: ")
(display [arr 2 8 2])
(newline)

(display "2D slice [1:3, 2:5]: ")
(define flat24b (np.arange 24))
(define m2 (flat24b.reshape 4 6))
(display [m2 (py-slice 1 3) (py-slice 2 5)])
(newline)

(display "boolean mask: ")
(define mask (np.array '#(#t #f #t #t #f #f #t #f #t #f #t #t)))
(display (py-eval "arr[mask]" :arr arr :mask mask))
(newline)

; ----- 1.4 数学运算 -----
(display "\n--- 1.4 Math Operations ---")
(newline)

(define A (np.array '#(1 2 3)))
(define B (np.array '#(4 5 6)))

(display "A + B: ")
(display (+ A B))
(newline)

(display "A * B: ")
(display (* A B))
(newline)

(display "A dot B: ")
(display (np.dot A B))
(newline)

(display "broadcast A + 10: ")
(display (+ A 10))
(newline)

(display "sum: ")
(display (np.sum A))
(newline)

(display "mean axis=0: ")
(display (np.mean (np.array '#(#(1 2) #(3 4))) :axis 0))
(newline)

(display "std: ")
(display (np.std A))
(newline)

(display "cumsum: ")
(display (np.cumsum A))
(newline)

; ----- 1.5 linalg -----
(display "\n--- 1.5 linalg ---")
(newline)

(define M (np.array '#(#(3 1) #(1 2))))
(display "det: ")
(display (np.linalg.det M))
(newline)

(display "inv: ")
(display (np.linalg.inv M))
(newline)

(display "eig: ")
(display (np.linalg.eig M))
(newline)

(display "svd: ")
(display (np.linalg.svd M))
(newline)

; ----- 1.6 fft -----
(display "\n--- 1.6 fft ---")
(newline)

(display "fft: ")
(display (np.fft.fft '#(1 0 1 0)))
(newline)

; ----- 1.7 polynomial -----
(display "\n--- 1.7 polynomial ---")
(newline)

(define xp (np.array '#(0 1 2 3 4)))
(define yp (np.array '#(0 1 4 9 16)))
(display "polyfit: ")
(display (np.polyfit xp yp 2))
(newline)

; ----- 1.8 Sort & Search -----
(display "\n--- 1.8 Sorting & Searching ---")
(newline)

(define unsorted (np.array '#(3 1 4 1 5 9 2 6)))
(display "sort: ")
(display (np.sort unsorted))
(newline)

(display "argsort: ")
(display (np.argsort unsorted))
(newline)

; ----- 1.9 Set Operations -----
(display "\n--- 1.9 Set Operations ---")
(newline)

(display "unique: ")
(display (np.unique '#(1 2 2 3 3 3 4)))
(newline)

(display "intersect1d: ")
(display (np.intersect1d '#(1 2 3) '#(2 3 4)))
(newline)

; ----- 1.10 char -----
(display "\n--- 1.10 char ---")
(newline)

(display "char.upper: ")
(display (np.char.upper '#("hello" "world")))
(newline)

(display "=== numpy 深度测试完成 ===\n")
(newline)