; ============================================================
; R1: 类型转换边缘情况 — 深度测试
; ============================================================

(import numpy as np)

(display "=== Round 1: Type Conversion Edge Cases ===\n")

; ----- 1.1 超大整数 -----
(display "\n--- 1.1 Large Integers ---")
(newline)

(display "2^63: ")
(display (py-eval "2**63"))
(newline)

(display "2^100: ")
(display (py-eval "2**100"))
(newline)

(display "-(2^100): ")
(display (py-eval "-(2**100)"))
(newline)

; ----- 1.2 NaN/Inf -----
(display "\n--- 1.2 NaN/Inf ---")
(newline)

(display "inf: ")
(display (py-eval "float('inf')"))
(newline)

(display "-inf: ")
(display (py-eval "-float('inf')"))
(newline)

(display "nan: ")
(display (py-eval "float('nan')"))
(newline)

; ----- 1.3 空容器 -----
(display "\n--- 1.3 Empty Containers ---")
(newline)

(display "empty list: ")
(display (py-eval "[]"))
(newline)

(display "empty tuple: ")
(display (py-eval "()"))
(newline)

(display "empty dict: ")
(display (py-eval "{}"))
(newline)

(display "empty set: ")
(display (py-eval "set()"))
(newline)

; ----- 1.4 深度嵌套 -----
(display "\n--- 1.4 Deep Nesting ---")
(newline)

(define nested (py-eval "[[[[1, 2], [3, 4]], [[5, 6], [7, 8]]], [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]]"))
(display "nested 4D: ")
(display nested)
(newline)

; 转换回
(display "nested unwrap: ")
(display (py-str (py-eval "str(nested)")))
(newline)

; ----- 1.5 Unicode -----
(display "\n--- 1.5 Unicode ---")
(newline)

(display "chinese: ")
(display (py-eval "'数学公式系统'"))
(newline)

(display "greek: ")
(display (py-eval "'αβγδεζηθ'"))
(newline)

(display "emoji: ")
(display (py-eval "'🎯🔬🧮📊'"))
(newline)

; ----- 1.6 None ↔ Nil 双向 -----
(display "\n--- 1.6 None/Nil ---")
(newline)

(display "None from py-eval: ")
(display (py-eval "None"))
(newline)

(display "type Scheme nil: ")
(display (py-str (py-eval "type(None).__name__")))
(newline)

; ----- 1.7 复数 -----
(display "\n--- 1.7 Complex Numbers ---")
(newline)

(display "complex from py-eval: ")
(display (py-eval "1+2j"))
(newline)

(display "py-eval complex op: ")
(display (py-eval "(1+2j)*(3-4j)"))
(newline)

(display "Scheme complex op: ")
(display (* 1+2i 3-4i))
(newline)

; ----- 1.8 Generator -----
(display "\n--- 1.8 Generator ---")
(newline)

(define gen (py-eval "(x**2 for x in range(5))"))
(display "generator type: ")
(display (py-str (py-eval "type(gen).__name__")))
(newline)

; 消费 generator
(display "list from gen: ")
(display (py-eval "list(gen)"))
(newline)

; ----- 1.9 Bytes -----
(display "\n--- 1.9 Bytes ---")
(newline)

(display "bytes: ")
(display (py-eval "b'hello'"))
(newline)

(display "bytearray: ")
(display (py-eval "bytearray(b'hello')"))
(newline)

; ----- 1.10 布尔值双向 -----
(display "\n--- 1.10 Boolean Roundtrip ---")
(newline)

(display "py True: ")
(display (py-eval "True"))
(newline)

(display "py False: ")
(display (py-eval "False"))
(newline)

(display "scheme #t -> py: ")
(display (py-str (py-eval "str(True)")))
(newline)

; ----- 1.11 类型检查 -----
(display "\n--- 1.11 Type Checks ---")
(newline)

(display "py-int: ")
(display (py-eval "isinstance(42, int)"))
(newline)

(display "py-float: ")
(display (py-eval "isinstance(3.14, float)"))
(newline)

(display "py-complex: ")
(display (py-eval "isinstance(1+2j, complex)"))
(newline)

(display "=== Round 1 Complete ===\n")
(newline)