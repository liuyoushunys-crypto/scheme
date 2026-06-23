# core/output — 输出格式

## 数学显示

```scheme
(use-cas)
(import sympy)
(define x (sympy.Symbol 'x'))

(pretty (integrate (* x x) x))      →   3
                                       x
                                       --
                                       3

(latex (integrate (* x x) x))        →  \frac{x^{3}}{3}
```

## 代码生成

```scheme
(ccode (integrate (* x x) x))        →  pow(x, 3)/3
(fcode (integrate (* x x) x))        →  x**3/3
```

## 描述/格式

```scheme
(describe (integrate (* x x) x))     →  返回积分结果的字符串描述
(mathml (integrate (* x x) x))       →  <math>...</math>
```

## 元操作

```scheme
(py-len (list 1 2 3))                →  3
```
