# assume — 假设系统

对标 Maxima 的 assume/refine/ask。

## 基本假设

```scheme
(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))

(assume (> x 0))                    ; 假设 x > 0
(assume (symbol-property x 'real))  ; 假设 x 为实数

(refine (sqrt (* x x)))             →  x  (基于 x > 0 简化为 x)
```

## 定义域性质

```scheme
(declare-positive x)    ; 声明 x 为正数
(declare-negative x)    ; 声明 x 为负数
(declare-nonzero x)     ; 声明 x 非零
(declare-real x)        ; 声明 x 为实数
```
