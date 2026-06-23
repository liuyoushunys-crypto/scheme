# parse — 多格式数学解析器

将各种格式的数学表达式解析为 sympy 对象。

```scheme
(use-cas)
(import sympy)
```

## Python/标准格式

```scheme
(parse "1 + 2")           →  3
(parse "x**2 + 2*x + 1")  →  x**2 + 2*x + 1
(parse "sin(pi/2)")       →  1
```

## LaTeX

```scheme
(parse-latex "x^2 + 1")           →  x**2 + 1
(parse-latex "\\frac{1}{x+1}")   →  1/(x + 1)
(parse-latex "\\int x^2 dx")     →  integral
```

## Maxima 格式

```scheme
(parse-maxima "x^2 + 2*x + 1")    →  x**2 + 2*x + 1
(parse-maxima "diff(x^3, x)")     →  3*x**2
```

## Mathematica 格式

```scheme
(parse-mathematica "x^2 + 2*x + 1")  →  x**2 + 2*x + 1
(parse-mathematica "Sin[x]")         →  sin(x)
```

## MathML

```scheme
(parse-mathml "<math><mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>1</mn></mrow></math>")
  →  x**2 + 1
```

## 格式转换

```scheme
(pretty (parse "x**2 + 1"))        →  x**2 + 1
(latex (parse "x**2 + 1"))         →  x^{2} + 1
(ccode (parse "x**2 + 1"))         →  pow(x, 2) + 1
```
