# Scheme-Python 互操作 — 完整语法速查

## 导入

```scheme
(import numpy)                              → import numpy
(import numpy as np)                        → import numpy as np
(import numpy scipy sympy)                  → import numpy, scipy, sympy
(import scipy.linalg)                       → import scipy.linalg (+ 自动绑定 scipy)
(from numpy import array zeros)             → from numpy import array, zeros
(from numpy import *)                       → from numpy import *
```

## 级联调用

```scheme
np.array                                   → numpy 模块对象
(np.linspace 0 1 5)                        → numpy.linspace(0, 1, 5)
(np.linalg.solve A b)                      → numpy.linalg.solve(A, b)
(arr.reshape 3 4)                          → arr.reshape(3, 4)
(networkx.shortest_path G 'A 'D)           → nx.shortest_path(G, 'A', 'D')
(import os.path) (os.path.join a b)        → os.path.join(a, b)
```

## 关键词参数

```scheme
(np.array '#(1 2 3) :dtype np.float64)     → np.array([1,2,3], dtype=np.float64)
(np.mean arr :axis 0)                       → np.mean(arr, axis=0)
(np.random.normal 0 1 '(2 3))              → np.random.normal(0, 1, (2,3))
(pandas.Series data :name 'scores)         → pd.Series(data, name='scores')
```

## 方括号索引与切片

```scheme
[arr 5]                                     → arr[5]
[a (list 1 3)]                              → a[1:3]          ← 自然切片语法
[a (list 1 7 2)]                            → a[1:7:2]        ← 含步长
[m 0 (list 1 3)]                            → m[0, 1:3]       ← 混合索引
[m (list 0 2) (list 1 3)]                   → m[0:2, 1:3]     ← 多维切片
```

## 管道操作

```scheme
(-> 5 (* 2) (+ 1))                          ;; → 11  (thread-first: 前步结果作首参)
(-> (np.array '#(1 2 3)) np.sum)           → sum(np.array([1,2,3]))
(-> arr .T)                                 → arr.T
(->> (list 3 1 4 1 5) reverse)              ;; → (5 1 4 1 3)  (thread-last: 前步结果作尾参)
```

## 语法糖

`λ` — lambda 简写：
```scheme
(map (λ (x) (* x x)) (list 1 2 3))         ;; → (1 4 9)
(filter (λ (x) (> x 2)) (list 1 5 2 3))    ;; → (5 3)
```

`for` — 列表推导：
```scheme
(for (x (list 1 2 3 4 5)) (* x x))          ;; → (1 4 9 16 25)
(for (x (range 0 10 2)) (expt x 2))         ;; → (0 4 16 36 64)
```

`str` — 字符串插值：
```scheme
(str "value = " 42)                         ;; → "value = 42"
```

## 运行时工具

```scheme
(py-get obj 'attr)                          → getattr(obj, "attr")
(py-get obj 0)                              → obj[0]
(py-get obj slice_obj)                      → obj[slice_obj]
(py-str obj)                                → str(obj)
(py-repr obj)                               → repr(obj)
(py-len obj)                                → len(obj)
(py-eval "expr" :var val)                   → eval("expr", globals(), {"var": val})
(py-exec "code")                            → exec("code")
(py-dict :key val :k2 v2)                   → {"key": val, "k2": v2}
(py-slice 1 10 2)                           → slice(1, 10, 2)
(py-for-each proc iterable)                 → for item in iterable: proc(item)
```

## 方法调用

```scheme
(. obj method arg1 arg2)                    → obj.method(arg1, arg2)  ; 安全形式
(arr.sort)                                  → arr.sort()              ; in-place
(df.groupby 'group).sum                     → df.groupby('group').sum ; 链式
```

## Python 互操作设置

```scheme
(set! mpmath.mp.dps 100)                    → mpmath.mp.dps = 100
```

## 闭包桥接

```scheme
; Scheme lambda 自动包装为 Python 回调
(scipy.optimize.minimize (lambda (x) (expt (- x 3) 2)) 0)
(scipy.integrate.quad (lambda (x) (exp (- (expt x 2)))) 0 np.inf)

; 多参数 lambda 自动暴露 __code__/__signature__
(scipy.optimize.curve_fit (lambda (x a b) (+ (* a x) b)) xd yd)
```

## 算术透明度

```scheme
; 所有 PythonObject 操作数自动代理到 Python
(+ u v)            ; uncertainties: 误差传播
(sin u)            ; uncertainties.umath.sin(u)
(+ x 1)            ; sympy: x + 1  (当 x 是 sympy Symbol)
(* 2 x)            ; sympy: 2*x
(sin x)            ; sympy.sin(x)
(> x 0)            ; sympy: Gt(x, 0) (关系表达式，非 bool)
```

## 类型转换

| Scheme | Python | 方向 |
|--------|--------|------|
| `Nil()` | `None` | 双向 |
| `Bool(#t)` | `True` | 双向 |
| `Integer(42)` | `42` | 双向 |
| `Num(3.14)` | `3.14` | 双向 |
| `Complex(1, 2)` | `1+2j` | 双向 |
| `Str(list("hello"))` | `"hello"` | 双向 |
| `Sym("x")` | `"x"` | → Python  |
| `#(1 2 3)` | `[1, 2, 3]` | 双向 |
| `Bytevector(...)` | `b"..."` | 双向 |
| `PythonObject(obj)` | `obj` | 双向 |

## pip 扩展

```scheme
; 任何 PyPI 包安装后直接可用
; $ pip install <package>
(import <package>)
(<package>.func :key val)
```

## 中缀表达式 `#{...}`

所有 Scheme 表达式中可嵌入 `#{...}` 书写类数学中缀语法，自动转为 S-表达式：

```scheme
#{x^2 - 4 = 0}          ; → (eqn (- (expt x 2) 4) 0)
#{sin(x) + cos(x)}      ; → (+ (sin x) (cos x))
#{2x + 1}               ; → (+ (* 2 x) 1)
#{(x+1)(x+2)}           ; → (* (+ x 1) (+ x 2))
#{-x}                   ; → (- x)
#{integrate(sin(x), x)} ; → (integrate (sin x) x)

; 与普通 Scheme 混合
(+ #{x + 1} #{y^2})     ; → (+ (+ x 1) (expt y 2))
(define f #{2x + 3y})   ; → (define f (+ (* 2 x) (* 3 y)))
```

完整参考见 `references/infix-parser.md`。