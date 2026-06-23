# 数学表达式解析器系统 — `eval/cas/parse.py`

## 4 种解析模式

### 1. `(parse str)` — Python/sympy 风格
使用 `sympy.parsing.sympy_parser.parse_expr`，支持隐式乘法。

### 2. `(parse-latex str)` — LaTeX 公式
使用 `sympy.parsing.latex.parse_latex`。

### 3. `(parse-mathml str)` — MathML XML
原生实现（`xml.etree.ElementTree` + 递归转换器）。

### 4. `(parse-mathematica str)` — Mathematica/Wolfram 语法
使用 `sympy.parsing.mathematica.parse_mathematica`。
