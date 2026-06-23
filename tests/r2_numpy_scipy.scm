; ============================================================
; R2: numpy/scipy 深层边缘情况
; ============================================================

(import numpy as np)
(import scipy)
(import scipy.sparse scipy.ndimage scipy.cluster)

(display "=== Round 2: numpy/scipy Deep Edge Cases ===\n")

; ----- 2.1 In-place 操作 (返回 None) -----
(display "\n--- 2.1 In-place Operations ---")
(newline)

(define a (np.array '#(3 1 4 1 5 9)))

; arr.sort() modifies in place, returns None
(a.sort)
(display "after sort: ")
(display a)
(newline)

; arr.resize() also in-place
(define b (np.array '#(1 2 3 4 5 6)))
(b.resize 2 3)
(display "after resize: ")
(display b)
(newline)

; ----- 2.2 视图 vs 副本 -----
(display "\n--- 2.2 Views vs Copies ---")
(newline)

(define base (. (np.arange 12) reshape 3 4))
(define view (base.T))
(display "view T: ")
(display view)
(newline)

; 修改视图影响原数组
(view.__setitem__ 0 999)
(display "base after view mod: ")
(display (py-get base 0))
(newline)

; ----- 2.3 稀疏矩阵 -----
(display "\n--- 2.3 Sparse Matrices ---")
(newline)

(define dense (np.array '#(#(1 0 0) #(0 2 0) #(0 0 3))))
(display "dense: ")
(display dense)
(newline)

(define sparse (scipy.sparse.csr_matrix dense))
(display "sparse CSR: ")
(display sparse)
(newline)

(define back (sparse.toarray))
(display "back to dense: ")
(display back)
(newline)

; 稀疏矩阵运算
(display "sparse * 2: ")
(display (scipy.sparse.csr_matrix (* dense 2)))
(newline)

; ----- 2.4 scipy.ndimage -----
(display "\n--- 2.4 scipy.ndimage ---")
(newline)

(define img (np.array '#(#(1 2 3) #(4 5 6) #(7 8 9))))
(display "sobel: ")
(display (scipy.ndimage.sobel img))
(newline)

(display "gaussian_filter: ")
(display (scipy.ndimage.gaussian_filter img 1.0))
(newline)

; ----- 2.5 scipy.cluster -----
(display "\n--- 2.5 scipy.cluster ---")
(newline)

(define pts (np.array '#(#(1 2) #(3 4) #(5 6) #(7 8) #(9 10))))
(display "vq: ")
(define codebook (np.array '#(#(1 2) #(9 10))))
(display (scipy.cluster.vq.vq pts codebook))
(newline)

; ----- 2.6 numpy 类型系统 -----
(display "\n--- 2.6 numpy dtype system ---")
(newline)

(define i32arr (np.array '#(1 2 3) :dtype np.int32))
(define f64arr (np.array '#(1 2 3) :dtype np.float64))

(display "int32: ")
(display i32arr.dtype)
(newline)

(display "float64: ")
(display f64arr.dtype)
(newline)

; 类型提升
(display "int32 + float64: ")
(display (+ i32arr f64arr))
(newline)

; 结构化数组 — 用 py-eval 创建 dtype
(display "\n--- 2.7 Structured Arrays ---")
(newline)

(define st (py-eval "np.array([(1, 2.0), (3, 4.0)], dtype=[('x', np.int32), ('y', np.float64)])" :np np))
(display "structured: ")
(display st)
(newline)

(display "x field: ")
(display (py-eval "st['x']" :st st))
(newline)

; ----- 2.8 FFT 边缘 -----
(display "\n--- 2.8 FFT Edge Cases ---")
(newline)

(display "fft2: ")
(display (np.fft.fft2 '#(#(1 2) #(3 4))))
(newline)

(display "fftshift: ")
(display (np.fft.fftshift (np.fft.fft '#(1 0 0 0 0 0 0 0))))
(newline)

(display "=== Round 2 Complete ===\n")
(newline)