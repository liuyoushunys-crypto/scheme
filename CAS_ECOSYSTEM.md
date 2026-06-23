# PyPI 数学生态 — 已验证集成手册

## 已安装生态总览 (16 包)

```
数值计算      | 符号计算       | 数据科学       | 图论
numpy 2.4.3   | sympy 1.14.0   | pandas 3.0.3   | networkx
scipy 1.17.1  | symengine      | statsmodels     |
numba         | mpmath 1.3.0   | scikit-learn    |

优化          | 有限域         | 物理单位       | 误差传播
cvxpy         | galois         | pint           | uncertainties
pulp          |                |                |
ortools       |                |                |

绘图          | 计算机视觉
matplotlib 3.10.9 | opencv-python 4.13.0
```

## 集成模式

### 导入
```scheme
(import numpy)                       → import numpy
(import numpy as np)                 → import numpy as np
(import scipy.optimize)              → 自动绑定父包 scipy
```

### 级联调用
```scheme
np.linspace                          → numpy.linspace
(np.linalg.solve A b)                → numpy.linalg.solve(A, b)
(networkx.shortest_path G 'A 'D)     → nx.shortest_path(G, 'A', 'D')
```

### 关键词参数
```scheme
(pandas.Series data :name 'scores)   → pd.Series(data, name='scores')
(scipy.optimize.minimize f x0 :method 'Nelder-Mead)
```

### 算术代理 (+ - * / expt sin cos 自动分发)
```scheme
(+ u v)          → uncertainties: 自动误差传播
(sin u)          → uncertainties.umath.sin(u) 自动
(+ x 1)          → sympy: x + 1
(sin x)          → sympy.sin(x)
```

### Scheme 闭包 → Python 回调
```scheme
(scipy.optimize.minimize (lambda (x) (expt (- x 2) 2)) 0)
```

### symengine 加速 (符号计算)
symengine 提供与 sympy 兼容的 API，但速度更快：
```scheme
(import symengine)
(symengine.expand (expt (+ a b) 4))
```

### galois 有限域
```scheme
(import galois)
(define GF (galois.GF 2 8))          → GF(2^8)
GF.primitive_element
```

## CAS 函数 (60+)

```
微积分        | 向量微积分     | 代数           | 三角/对数
integrate      | grad           | expand         | trigexpand
diff           | div            | factor         | trigsimp
limit          | curl           | simplify       | powsimp
series/taylor  | hessian        | apart          | logcombine
summation      | jacobian       | together       | radsimp
product        |                | collect        |
                                  | coeff          |
                                  | normal         |
                                  | resultant      |
                                  | discriminant   |
                                  | compose        |

方程          | 线性代数       | ODE            | 积分变换
solve          | matrix         | dsolve         | laplace
subs           | det/inv        |                | inverse-laplace
               | transpose      |                | fourier
               | eigenvals/vects|                | inverse-fourier
               | eye/zeros/ones |                |

数论          | 集合           | 统计           | 特殊函数
prime?         | set            | mean           | LambertW
factorint      | union          | median         | polylog
nextprime      | intersection   | variance       | stirling
prevprime      | set-difference | std            | bernoulli
primerange     | symmetric-diff | correlation    | euler
divisors       | subset?        | regression     | fibonacci
totient        | element?       |                |
mobius         |                |                |
diophantine    |                |                |

输出          | 绘图           | 帮助
pretty         | plot           | describe
latex          |                |
```

## pip install 新包

任何 PyPI 包安装后可直接 import 使用：
```scheme
; 1. pip install <pkg>
; 2. Scheme 中直接导入
(import <pkg>)
; 3. 级联调用
(<pkg>.func ...)
; 4. 关键词参数
(<pkg>.func ... :key val)
```

无需额外适配代码 — 自动桥接层处理类型转换、
回调包装、关键词参数、算术代理。