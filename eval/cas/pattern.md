# pattern — 模式匹配与重写

CAS 模式匹配系统，对标 Maxima 的 defrule/match/rewrite。

## match — 模式匹配

```scheme
(use-cas)
(import sympy)
(define x (sympy.Symbol 'x))

(match (+ x 1) (+ x 1))    →  #t   ; 匹配成功
(match (+ x 1) (* x 1))    →  #f   ; 不匹配
```

## defrule / rewrite — 规则定义与重写

```scheme
; 定义 sin² + cos² → 1 的规约规则
(defrule trig-id (* (+ (expt (sin ?a) 2) (expt (cos ?a) 2))) 1)

; 应用规则
(rewrite (+ (expt (sin x) 2) (expt (cos x) 2)) trig-id)
  →  1
```
