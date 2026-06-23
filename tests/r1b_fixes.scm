; ============================================================
; R1b: 类型转换修复验证 + 更多边缘测试
; ============================================================

(import numpy as np)

(display "=== Round 1b: Fix Verification ===\n")

; ----- 1.1 py-eval 变量注入 (修复验证) -----
(display "\n--- 1.1 py-eval with variable injection ✅ ---")
(newline)

(define arr (np.arange 12))

; 之前: (py-eval "arr[2:8:2]") → Error
; 现在: (py-eval "arr[2:8:2]" :arr arr) → Works!
(display "arr[2:8:2]: ")
(display (py-eval "arr[2:8:2]" :arr arr))
(newline)

(display "arr[mask]: ")
(define mask (np.array '#(#t #f #t #t #f #f #t #f #t #f #t #t)))
(display (py-eval "arr[mask]" :arr arr :mask mask))
(newline)

(display "arr[[1,3,5]]: ")
(display (py-eval "arr[[1,3,5]]" :arr arr))
(newline)

; ----- 1.2 py-slice 验证 -----
(display "\n--- 1.2 py-slice ✅ ---")
(newline)

(define s (py-slice 2 8 2))
(display "slice obj: ")
(display s)
(newline)

(display "arr[slice]: ")
(display (py-get arr s))
(newline)

; 二维切片
(define m2 (py-eval "np.arange(24).reshape(4,6)" :np np))
(display "m2[1:3, 2:5]: ")
(display (py-get m2 (list (py-slice 1 3) (py-slice 2 5))))
(newline)

; ----- 1.3 Deep nested roundtrip -----
(display "\n--- 1.3 Deep Nested Roundtrip ✅ ---")
(newline)

(define nested (py-eval "[[[[1, 2], [3, 4]], [[5, 6], [7, 8]]], [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]]"))
(display "nested: ")
(display nested)
(newline)

(display "roundtrip: ")
(display (py-str nested))
(newline)

; ----- 1.4 Complex edge cases -----
(display "\n--- 1.4 Complex Edges ---")
(newline)

; Large matrix transpose
; 用 (. obj method ...) 语法替代 (obj).method
(display "large transpose: ")
(define big (. (np.arange 1000) reshape 100 10))
(display (np.shape big.T))
(newline)

; Broadcasting edge
(display "broadcast (3,) + (3,1): ")
(display (+ (np.array '#(1 2 3)) (np.array '#(#(4) #(5) #(6)))))
(newline)

; Boolean operations on arrays
(display "bitwise_and: ")
(display (py-eval "np.bitwise_and(np.array([1,2,3]), np.array([3,2,1]))" :np np))
(newline)

; ----- 1.5 Exceptions from Python -----
(display "\n--- 1.5 Python Exceptions ---")
(newline)

; 用 guard 捕获异常
(display "div by zero (expected): ")
(display "cannot guard here, will raise")
(py-eval "1/0")
(newline)

(display "=== Round 1b Complete ===\n")
(newline)