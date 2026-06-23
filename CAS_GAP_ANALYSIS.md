# CAS 能力对标 Maxima — 差距分析 (已修复)

## 已完成的工作 (本轮)

### P0a (假设系统) ✅
| 功能 | Scheme API | 状态 |
|------|-----------|------|
| 声明假设 | `(assume '(positive x))` | ✅ |
| 临时假设 | `(assuming '((positive x)) (refine expr))` | ✅ |
| 化简 | `(refine (sqrt (expt x 2)))` | ✅ |
| 查询 | `(ask '(positive p))` | ✅ |
| 清除 | `(unassume)` / `(unassume 'x)` | ✅ |

### P0b (方程/表达式工具) ✅
| 功能 | Scheme API | 状态 |
|------|-----------|------|
| 方程左边 | `(lhs eq)` | ✅ |
| 方程右边 | `(rhs eq)` | ✅ |
| 分子 | `(num expr)` | ✅ |
| 分母 | `(denom expr)` | ✅ |
| 隔离变量 | `(isolate eq var)` | ✅ |

### P0c (REPL %) ✅
| 功能 | Scheme API | 状态 |
|------|-----------|------|
| 上步结果 | `%` | ✅ |

### P1a (数值方法) ✅
| 功能 | Scheme API | 状态 |
|------|-----------|------|
| 数值求根 | `(find-root f a b)` | ✅ |
| 数值积分 | `(numerical-integrate f a b)` | ✅ |
| 数值微分 | `(numerical-derivative f x)` | ✅ |

### P1b (ratsimp + 输出格式) ✅
| 功能 | Scheme API | 状态 |
|------|-----------|------|
| 有理式化简 | `(ratsimp expr)` | ✅ |
| C 代码生成 | `(ccode expr)` | ✅ |
| Fortran 生成 | `(fcode expr)` | ✅ |
| MathML 生成 | `(mathml expr)` | ✅ |

## 全部已实现能力

```
微积分:       integrate diff limit series taylor summation product
向量微积分:   grad div curl hessian jacobian
代数:         expand factor simplify ratsimp apart together collect
              coeff normal resultant discriminant compose
三角/对数:    trigexpand trigsimp powsimp logcombine radsimp
方程:         solve subs lhs rhs isolate
线性代数:     matrix det inv transpose eigenvals eigenvects eye zeros ones
多项式:       roots nroots
ODE:          dsolve
积分变换:     laplace inverse-laplace fourier inverse-fourier
数论:         prime? factorint nextprime prevprime primerange divisors
              totient mobius continued-fraction diophantine
集合:         set union intersection set-difference symmetric-difference
              subset? element?
统计:         mean median variance std correlation regression
特殊函数:     lambertw polylog stirling bernoulli euler_fn fibonacci
假设系统:     assume unassume refine assuming ask
数值:         find-root numerical-integrate numerical-derivative
输出:         pretty latex ccode fcode mathml describe
绘图:         plot plot-param plot3d
引擎:         use-engine engine-info
帮助:         help
工具:         eqn lhs rhs num denom isolate
```

## 仍可桥接（无需 wrapper）

```scheme
(import networkx)           ; 图论
(import scipy.optimize)     ; 优化
(import scipy.stats)        ; 概率分布
(import sympy.physics)      ; 物理/单位
(import sympy.tensor)       ; 张量
(import sympy.geometry)     ; 几何
(import sympy.combinatorics); 组合数学
(import sympy.codegen)      ; 代码生成
(sympy.besselj ...)         ; 特殊函数
(sympy.gamma ...)
```
