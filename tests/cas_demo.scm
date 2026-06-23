;; ==========================================================
;; CAS 系统 — 完整功能演示
;; 运行: python3 main.py tests/cas_demo.scm
;; ==========================================================

(display "╔════════════════════════════════════════════════════╗")
(newline)
(display "║         CAS 系统 — 完整功能演示                   ║")
(newline)
(display "╚════════════════════════════════════════════════════╝")
(newline)

;; ==================== 1. 一键加载 ====================
(display "\\n=== 1. (use-cas) 一键加载 ===\\n")
(use-cas)

;; ==================== 2. #{...} 中缀表达式 ====================
(display "\\n=== 2. #{...} 中缀语法 ===\\n")

(import sympy)
(define x (sympy.Symbol 'x))
(define y (sympy.Symbol 'y))

(display "  #{x^2 + 2*x + 1}             → ")
(display #{x^2 + 2*x + 1})
(newline)

(display "  #{sin(x)^2 + cos(x)^2}       → ")
(display #{sin(x)^2 + cos(x)^2})
(newline)

(display "  #{ √(x^2 + y^2) }            → ")
(display #{ √(x^2 + y^2) })
(newline)

(display "  #{ 1/(x-1) + 1/(x+1) }      → ")
(display #{ 1/(x-1) + 1/(x+1) })
(newline)

;; ==================== 3. 微积分 ====================
(display "\\n=== 3. 微积分 ===\\n")

(display "  (diff #{x^3} x)              → ")
(display (diff #{x^3} x))
(newline)

(display "  (integrate #{x^2} x)         → ")
(display (integrate #{x^2} x))
(newline)

(display "  (integrate #{x^2} x 0 1)     → ")
(display (integrate #{x^2} x 0 1))
(newline)

(display "  (limit #{sin(x)/x} x 0)      → ")
(display (limit #{sin(x)/x} x 0))
(newline)

(display "  (series #{exp(x)} x 0 5)     → ")
(display (series #{exp(x)} x 0 5))
(newline)

;; ==================== 4. 代数 ====================
(display "\\n=== 4. 代数 ===\\n")

(display "  (expand #{ (x+1)^5 })        → ")
(display (expand #{ (x+1)^5 }))
(newline)

(display "  (factor #{x^4 - 1})          → ")
(display (factor #{x^4 - 1}))
(newline)

(display "  (simplify #{ (x^2-1)/(x-1) }) → ")
(display (simplify #{ (x^2-1)/(x-1) }))
(newline)

(display "  (ratsimp #{ 1/(x-1) + 1/(x+1) }) → ")
(display (ratsimp #{ 1/(x-1) + 1/(x+1) }))
(newline)

;; ==================== 5. 方程 ====================
(display "\\n=== 5. 方程 ===\\n")

(display "  (solve #{x^2 - 4 = 0} x)     → ")
(display (solve #{x^2 - 4 = 0} x))
(newline)

(display "  (lhs #{x^2 - 4 = 0})         → ")
(display (lhs #{x^2 - 4 = 0}))
(newline)

(display "  (rhs #{x^2 - 4 = 0})         → ")
(display (rhs #{x^2 - 4 = 0}))
(newline)

(display "  (isolate #{a*x + b = 0} x)   → ")
(display (isolate #{a*x + b = 0} x))
(newline)

;; ==================== 6. 线性代数 ====================
(display "\\n=== 6. 线性代数 ===\\n")

(define M (sympy.Matrix (list (list 1 2) (list 3 4))))
(display "  (lu-decomp M)                → ")
(display (lu-decomp M))
(newline)

(display "  (svd M)                      → ")
(display (svd M))
(newline)

(display "  (eigenvals M)                → ")
(display (eigenvals M))
(newline)

;; ==================== 7. 假设系统 ====================
(display "\\n=== 7. 假设系统 ===\\n")

(assume '(positive x))
(display "  (assume '(positive x))")
(newline)
(display "  (refine (sqrt (expt x 2)))   → ")
(display (refine (sqrt (expt x 2))))
(newline)
(display "  (ask '(positive x))          → ")
(display (ask '(positive x)))
(newline)
(unassume)

;; ==================== 8. 语法糖 ====================
(display "\\n=== 8. 语法糖 ===\\n")

(display "  ((λ (x) (* x 2)) 21)         → ")
(display ((λ (x) (* x 2)) 21))
(newline)

(display "  (-> 5 (* 2) (+ 1))           → ")
(display (-> 5 (* 2) (+ 1)))
(newline)

(display "  (->> (list 3 1 4 1) reverse) → ")
(display (->> (list 3 1 4 1) reverse))
(newline)

(display "  (for (x (list 1 2 3)) (* x x)) → ")
(display (for (x (list 1 2 3)) (* x x)))
(newline)

(display "  (str \"answer = \" 42)        → ")
(display (str "answer = " 42))
(newline)

;; ==================== 9. numpy ====================
(display "\\n=== 9. numpy 集成 ===\\n")

(define a (np.array (range 10)))
(display "  a = ") (display a) (newline)
(display "  [a 2 : 7 : 2]               → ")
(display [a 2 : 7 : 2])
(newline)
(display "  (+ a 10)                     → ")
(display (+ a 10))
(newline)
(display "  (np.mean a)                  → ")
(display (np.mean a))
(newline)

;; ==================== 10. 输出 ====================
(display "\\n=== 10. 输出格式 ===\\n")

(display "  (latex #{ ∫(x^2) dx })       → ")
(display (latex #{ ∫(x^2) dx }))
(newline)

(display "  (ccode #{ (x+1)^2 })         → ")
(display (ccode #{ (x+1)^2 }))
(newline)

(display "  (mathml #{ (x+1)^2 })        → ")
(display (mathml #{ (x+1)^2 }))
(newline)

;; ==================== 11. 帮助系统 ====================
(display "\\n=== 11. 帮助系统 ===\\n")

(display "  (? 'diff)                    → 显示 diff 帮助")
(newline)
(display "  (?? \"微积分\")               → 搜索微积分相关")
(newline)
(display "  (apropos \"方程\")            → 搜索方程相关")
(newline)

;; ==================== 12. 引擎信息 ====================
(display "\\n=== 12. 引擎信息 ===\\n")
(engine-info)

(display "\\n╔════════════════════════════════════════════════════╗")
(newline)
(display "║  演示完成!  输入 (help) 浏览全部 90+ 函数        ║")
(newline)
(display "║  输入 (catalog) 浏览 29+ Python 包               ║")
(newline)
(display "╚════════════════════════════════════════════════════╝")
(newline)
