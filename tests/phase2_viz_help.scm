;; Phase 2 测试 — 可视化后端 + Help 系统
(import sympy)
(define x (sympy.Symbol 'x))

;; ======== 1. Help 系统测试 ========

(display "=== 1. (help) 无参数 — 列出所有函数 ===")
(newline)
(help)

(display "=== 2. (help 'integrate) — 函数详情 ===")
(newline)
(help 'integrate)

(display "=== 3. (help \"方程\") — 搜索关键词 ===")
(newline)
(help "方程")

(display "=== 4. (help \"solve\") — 搜索 ===")
(newline)
(help "solve")

;; ======== 2. 可视化测试 ========

(display "=== 5. plot 基本使用 ===")
(newline)
(display "  (plot #{x^2} x -3 3 :show #f :title \"Test\" :grid #t)")
(newline)
(define fig1 (plot #{x^2} x -3 3 :show #f :title "Parabola" :grid #t))
(display "  Result: ")
(display fig1)
(newline)

(display "=== 6. plot 多迹线 ===")
(newline)
(display "  (plot (list #{sin(x)} #{cos(x)}) x 0 6.28 :show #f :legend #t)")
(newline)
(define fig2 (plot (list #{sin(x)} #{cos(x)}) x 0 6.28 :show #f :legend #t))
(display "  Result: ")
(display fig2)
(newline)

(display "=== 7. plot-param 参数曲线 ===")
(newline)
(define t (sympy.Symbol 't))
(display "  (plot-param #{cos(t)} #{sin(t)} t 0 6.28 :show #f :title \"Circle\")")
(newline)
(define fig3 (plot-param #{cos(t)} #{sin(t)} t 0 6.28 :show #f :title "Circle"))
(display "  Result: ")
(display fig3)
(newline)

(display "=== 8. plot3d 曲面 ===")
(newline)
(define y (sympy.Symbol 'y))
(display "  (plot3d #{x^2 + y^2} x -2 2 y -2 2 :show #f :title \"Paraboloid\")")
(newline)
(define fig4 (plot3d #{x^2 + y^2} x -2 2 y -2 2 :show #f :title "Paraboloid"))
(display "  Result: ")
(display fig4)
(newline)

;; ======== 3. #{...} 中缀 + plot 集成 ========

(display "=== 9. #{...} + plot ===")
(newline)
(display "  (plot #{sin(x)/x} x -20 20 :show #f :title \"sinc(x)\" :grid #t)")
(newline)
(define fig5 (plot #{sin(x)/x} x -20 20 :show #f :title "sinc(x)" :grid #t))
(display "  Result: ")
(display fig5)
(newline)

(display "=== Phase 2 全部测试完成 ===")
(newline)
