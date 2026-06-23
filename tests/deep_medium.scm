; ============================================================
; 深度测试 3/5: mpmath + uncertainties + pint + galois + symengine
; ============================================================

(display "=== Medium Packages Depth Test ===\n")

; ----- 3.1 mpmath 高精度 -----
(display "\n--- 3.1 mpmath ---")
(newline)

(import mpmath)

; 精度控制
(set! mpmath.mp.dps 100)
(display "dps: ")
(display mpmath.mp.dps)
(newline)

; 基础常数
(display "pi (100): ")
(display mpmath.pi)
(newline)

(display "e (100): ")
(display mpmath.e)
(newline)

; 特殊函数
(display "zeta(2): ")
(display (mpmath.zeta 2))
(newline)

(display "gamma(5): ")
(display (mpmath.gamma 5))
(newline)

(display "ellipk(0.5): ")
(display (mpmath.ellipk 0.5))
(newline)

(display "hyp2f1(1,2,3,0.5): ")
(display (mpmath.hyp2f1 1 2 3 0.5))
(newline)

; 矩阵运算
(display "mp.matrix: ")
(define A (mpmath.mp.matrix '#(#(1 2) #(3 4))))
(display A)
(newline)

(display "mp.det: ")
(display (mpmath.mp.det A))
(newline)

; 求根
(display "findroot: ")
(display (mpmath.findroot (lambda (x) (- (expt x 2) 2)) 1.5))
(newline)

; ----- 3.2 uncertainties -----
(display "\n--- 3.2 uncertainties ---")
(newline)

(import uncertainties)
(import uncertainties.umath)

(define u (uncertainties.ufloat 10.0 0.5))
(define v (uncertainties.ufloat 3.0 0.1))

(display "u: ")
(display u)
(newline)

; 算术代理自动工作
(display "u + v: ")
(display (+ u v))
(newline)

(display "u * v: ")
(display (* u v))
(newline)

(display "u / v: ")
(display (/ u v))
(newline)

(display "u**2: ")
(display (expt u 2))
(newline)

; 函数代理
(display "sin(u): ")
(display (uncertainties.umath.sin u))
(newline)

(display "cos(u): ")
(display (uncertainties.umath.cos u))
(newline)

; 相关性
(define w (+ (* 2 u) v))
(display "w = 2u+v: ")
(display w)
(newline)

; ----- 3.3 pint 物理单位 -----
(display "\n--- 3.3 pint ---")
(newline)

(import pint)

(define ureg (pint.UnitRegistry))

; 创建量
(define dist (ureg.Quantity 5.0 'meter))
(define time (ureg.Quantity 2.0 'second))
(define mass (ureg.Quantity 10.0 'kilogram))

(display "dist: ")
(display dist)
(newline)

; 算术
(display "speed: ")
(display (/ dist time))
(newline)

(display "force: ")
(display (* mass (/ dist (expt time 2))))
(newline)

; 转换
(display "dist to km: ")
(display (dist.to 'kilometer))
(newline)

(display "dist to miles: ")
(display (dist.to 'mile))
(newline)

; 兼容性检查
(display "compatible?: ")
(display (dist.is_compatible_with (ureg.Quantity 1 'mile)))
(newline)

; 上下文转换 — 用中间变量避免 ).
(display "watt to horsepower: ")
(define watt_q (ureg.Quantity 1000 'watt))
(display (watt_q.to 'horsepower))
(newline)

; ----- 3.4 galois 有限域 -----
(display "\n--- 3.4 galois ---")
(newline)

(import galois)

(define GF256 (galois.GF 2 8))
(display "GF(2^8): ")
(display GF256)
(newline)

; 域元素
(define a GF256.primitive_element)
(display "primitive: ")
(display a)
(newline)

(display "a**2: ")
(display (expt a 2))
(newline)

(display "a + a**2: ")
(display (+ a (expt a 2)))
(newline)

(display "a * a: ")
(display (* a a))
(newline)

; 多项式
(display "poly: ")
(display (galois.Poly (list 1 2 3) :field GF256))
(newline)

; ----- 3.5 symengine 快速符号 -----
(display "\n--- 3.5 symengine ---")
(newline)

(import symengine)

(define sa (symengine.Symbol 'a))
(define sb (symengine.Symbol 'b))

(display "expand: ")
(display (symengine.expand (expt (+ sa sb) 10)))
(newline)

(display "diff: ")
(display (symengine.diff (symengine.sin sa) sa))
(newline)

(display "=== Medium Packages Depth Complete ===\n")
(newline)