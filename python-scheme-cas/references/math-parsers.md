# 数学表达式解析器系统

## 模块：`eval/eval_py_parse.py`

4 种解析模式，全部返回 sympy 表达式（PythonObject）：

### 1. `(parse str)` — Python/sympy 风格

使用 `sympy.parsing.sympy_parser.parse_expr`，支持隐式乘法。

```scheme
(parse "x**2 + 1")                    → x² + 1
(parse "sin(x)**2 + cos(x)**2")       → 1
(parse "integrate(x**2, (x, 0, 1))")  → 1/3
(parse "sqrt(x**2 + y**2)")           → √(x²+y²)
(parse "1/(x-1) + 1/(x+1)")          → 1/(x-1) + 1/(x+1)
```

**注意**：sympy 中用 `**` 表示幂，`^` 是 XOR 运算符。

### 2. `(parse-latex str)` — LaTeX 公式

使用 `sympy.parsing.latex.parse_latex`（需要 antlr4-python3-runtime）。

```scheme
(parse-latex "x^2 + 1")               → x² + 1
(parse-latex "1/x")                   → x⁻¹
(parse-latex "sin(x)^2 + cos(x)^2")   → 1
(parse-latex "\\int_0^1 x^2 dx")      → 1/3
```

**限制**：sympy 的 LaTeX 解析器覆盖常见 LaTeX 命令。复杂格式（`\sqrt`, `\frac` 嵌套等）部分支持。

### 3. `(parse-mathml str)` — MathML XML

原生实现（`xml.etree.ElementTree` + 递归 `_mml()` 转换器），无需外部依赖。

```scheme
;; x² + 1
(parse-mathml "<math><mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>1</mn></mrow></math>")
→ x² + 1

;; 1/(x-1)
(parse-mathml "<math><mfrac><mn>1</mn><mrow><mi>x</mi><mo>-</mo><mn>1</mn></mrow></mfrac></math>")
→ 1/(x-1)

;; √x
(parse-mathml "<math><msqrt><mi>x</mi></msqrt></math>")
→ √x
```

支持的元素：`math`, `mrow`, `mi`, `mn`, `mo`, `msup`, `msub`, `msqrt`, `mroot`, `mfrac`, `mfenced`, `merror`, `mphantom`。

### 4. `(parse-mathematica str)` — Mathematica/Wolfram 语法

```scheme
(parse-mathematica "x^2 + 2*x + 1")          → x² + 2x + 1
(parse-mathematica "Sin[x]^2 + Cos[x]^2")    → 1
```

### 双向转换

```scheme
;; CAS → LaTeX 导出
(latex #{1/(x-1)})                 → \frac{1}{x - 1}
(latex (parse "integrate(x**2, x)")) → \frac{x^{3}}{3}

;; LaTeX → CAS → 运算 → LaTeX
(define expr (parse-latex "x^2 + 1"))
(latex (integrate expr x))         → \frac{x^{3}}{3} + x
```
