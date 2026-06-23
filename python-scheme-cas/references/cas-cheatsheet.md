## CAS 语法速查

### 导入 (Python 风格)
```scheme
(import sympy)
(import numpy as np)
(import scipy.optimize)         ; 自动绑定 scipy
(import statsmodels.api as sm)
```

### 符号创建
```scheme
(defsym x y z)                  ; 批量创建
(sympy.abc.x)                    ; 预定义符号
(sympy.Function 'y)              ; 函数（用于 ODE）
(with-symbols (a b) (expand (expt (+ a b) 3)))  ; 临时符号
```

### 代数
```scheme
(expand (expt (+ x 1) 6))       ; 展开
(factor (+ (* 2 (expt x 2)) (* 4 x) 2))  ; 因式分解
(simplify (/ (+ (expt x 2) (* 3 x) 2) (+ x 1)))  ; 化简
(solve (+ (expt x 2) (* -3 x) 1) x)  ; 解方程
(solve (list (+ x y -2) (- x y)) (list x y))  ; 解方程组
```

### 微积分
```scheme
(integrate (expt x 2) x)        ; 不定积分 ∫ x² dx
(integrate (expt x 2) x 0 1)    ; 定积分 ∫₀¹ x² dx
(diff (expt x 3) x)             ; 一阶导数
(diff (sin x) x 3)              ; 三阶导数
(limit (/ (sin x) x) x 0)       ; 极限 lim(x→0) sin(x)/x
(series (exp x) x 0 6)          ; 泰勒展开
(summation (expt x n) (list n 1 5))  ; 求和 Σ
```

### 微分方程
```scheme
(define y_func (sympy.Function 'y))
(dsolve (+ (diff (y_func x) x) (* -2 (y_func x))) (y_func x) x)
```

### 积分变换
```scheme
(laplace (expt t 2) t s)        ; ℒ{t²} = 2/s³
(inverse-laplace (/ 2 (expt s 3)) s t)  ; ℒ⁻¹{2/s³} = t²
```

### 线性代数
```scheme
(define A (matrix (list (list 1 2) (list 3 4))))
(det A)
(inv A)
(transpose A)
(eigenvals A)
(eigenvects A)
(eye 3)
(zeros 2 4)
```

### 多项式
```scheme
(define p (sympy.Poly (+ (* 2 (expt x 2)) (* -4 x) 2) x))
(roots p x)
(nroots p)
```

### 输出
```scheme
(py-str expr)          ; Python str()
(py-repr expr)         ; Python repr()
(latex expr)           ; LaTeX: "x^{2} - 4 x + 4"
(describe sympy.diff)  ; Python 文档
```

### 代入
```scheme
(define e (+ (* 2 (expt x 2)) (* 3 x) 1))
(subs e x 2)           ; → 15
```

### 常用 sympy 原生函数
```scheme
(sympy.srepr expr)      ; srepr 字符串
(sympy.sympify "x**2") ; 字符串→sympy
(sympy.pprint expr)     ; 漂亮打印
(sympy.printing.pretty expr)
(sympy.latex expr)      ; LaTeX
(sympy.printing.ccode expr)  ; C 代码
(sympy.printing.fcode expr)  ; Fortran 代码
(sympy.printing.mathml expr) ; MathML
(sympy.refine expr (sympy.Q.positive x)) ; 基于假设置换
```

### 级联属性/方法
```scheme
sympy.pi               ; π
sympy.E                 ; e
sympy.I                 ; 虚数单位 i
sympy.oo                ; ∞
M.T                     ; 转置
M.det                   ; 行列式（属性）
(M.inv)                 ; 逆矩阵（方法）
(M.charpoly x)          ; 特征多项式
(M.eigenvals)           ; 特征值
poly.coeffs             ; 多项式系数（方法）
poly.degree              ; 多项式次数（属性）
```

### 数值计算
```scheme
(set! mpmath.mp.dps 100)  ; 100 位精度
mpmath.pi                 ; 高精度 π
(mpmath.zeta 2)           ; ζ(2) = π²/6
```

### 统计
```scheme
(import statsmodels.api as sm)
(define results (sm.OLS y (sm.add_constant X)).fit)
results.params
results.rsquared
results.summary
```