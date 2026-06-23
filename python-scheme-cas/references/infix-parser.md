# 中缀表达式解析器 (`parser/infix.py`) 参考

## 架构

基于 Pratt 绑力的递归下降解析器。三条主线：

1. **`tokenize_infix(text: str) → List[str]`** — 中缀专用 tokenizer
2. **`_Parser(tokens)`** — Pratt 解析器主循环（`parse(min_bp)`）
3. **`parse_infix(text: str) → str`** — 公共入口，返回 Scheme S-表达式字符串

## 优先级表

| 绑定力 | 类别 | 运算符 | 结合性 | 产出 |
|--------|------|--------|--------|------|
| 10 | compare | `= < > <= >= !=` | 左 | `(eqn ...)`, `(< ...)`, `(!= ...)` |
| 30 | term | `+ -` | 左 | `(+ a b)`, `(- a b)` |
| 35 | range | `..` | 左 | `(range a b)` |
| 40 | factor | `* /` | 左 | `(* a b)`, `(/ a b)` |
| 45 | 隐式乘法 | `(相邻操作数)` | 左 | `(* a b)` |
| 50 | 绝对值 | `\|...\|` | 分组 | `(abs ...)` |
| 55 | subscript | `_` | **右结合** | `(ref a b)` |
| 60 | power | `^` | **右结合** | `(expt a b)` |
| 70 | call | `f(...)`, `!` | 后缀 | `(f x y)`, `(factorial n)` |

## 增强数学表达支持

### 绝对值 `|...|`

`|` 作为分组构造，在 `_prefix` 中处理：

```python
if tok == '|':
    inner = self.parse(0)
    if self.peek() == '|': self.advance()
    return f"(abs {inner})"
```

- `|x|` → `(abs x)` → `Abs(x)` (CAS-aware)
- `|x-1|` → `(abs (- x 1))` → `Abs(x-1)`
- `|x| + |y|` → `(+ (abs x) (abs y))` → `Abs(x)+Abs(y)`
- `|x^2 + y^2|` → `(abs (+ (expt x 2) (expt y 2)))` → `Abs(x²+y²)`

实现注意：`|` 在 main loop 中遇到时 `break`（由前缀处理），避免双重 `(abs (abs ...))`。

### 阶乘 `n!`

`!` 在隐式乘法**之前**检测：

```python
# main loop: 在 implicit_mul 之前
if peek == '!':
    self.advance()
    left = f"(factorial {left})"
    continue
```

- `5!` → `(factorial 5)` → `120`
- `3! * 2` → `(* (factorial 3) 2)` → `12`
- `n!` → `(factorial n)` → `sympy.factorial(n)`

注意：`_is_implicit_mul` 中显式排除 `peek == '!'` 返回 `False`，避免隐式乘法抢先。

### 范围 `a..b`

`..` 作为二元运算符（BP=35）：

```python
if op == '..':
    left = f"(range {left} {right})"
```

- `1..10` → `(range 1 10)` → numpy `[1 2 ... 10]`
- `0..1` → `(range 0 1)` → numpy `[0]`
- `2..n` → `(range 2 n)` → numpy `[2 3 ... n-1]`

tokenizer 中数字遇到 `..` 时停止（不把 `..` 吞入数字 token）。

### 下标 `a_b`

`_` 作为二元运算符（BP=55，右结合）：

```python
elif op == '_':
    left = f"(ref {left} {right})"
```

- `x_y` → `(ref x y)` → `x[y]`
- `a_{n+1}` → `(ref a (+ n 1))` → `a[n+1]`

`_` 在 tokenizer 中被列为分隔符（`if c in '()[]{}|;,_'`），标识符 tokenizer 遇到 `_` 时停止。

`{...}` 在 `_` 之后被解析为分组表达式（而非 set），因此 `a_{n+1}` 正确展开为 `(ref a (+ n 1))`。

### 矩阵字面量 `[1 2; 3 4]`

检测 `[` 后 token 流中是否含 `;`：

```python
if tok == '[' and ';' in self.toks[self.pos:]:
    return self._parse_matrix_rows()
```

`_parse_matrix_rows`：
- 用 `self.parse(46)` 解析每个元素（46 > 45 隐式乘法，防止 `1 2` 被理解为 `(* 1 2)`）
- `;` 分隔行，每行收集为 `(list ...)`
- 结果如 `(matrix (list 1 2) (list 3 4))`
- 消耗 `]`

示例：
- `[1 2; 3 4]` → `(matrix (list 1 2) (list 3 4))` → sympy Matrix `[[1,2],[3,4]]`
- `[1; 2; 3]` → `(matrix (list 1) (list 2) (list 3))` → 列向量
- `[1 0 0; 0 1 0; 0 0 1]` → 3×3 单位矩阵

### 花括号 `{...}` 作为分组

`{...}` 在 `_prefix` 中处理为分组，而非集合字面量：

```python
if tok == '{':
    inner = self.parse(0)
    self._expect('}')
    return inner
```

主要用于下标中的复合表达式：`a_{n+1}` → `(ref a (+ n 1))`。集合请用 `(set 1 2 3)`。

## 设计决策

### 1. `name(...)` → 函数调用

`_is_name_expr(left)` 判断左值是否为裸名称（不含空格/parens 的标识符）。是 → 函数调用；否 → 隐式乘法。

```python
# parser/infix.py:134-141
if peek == '(' and _is_name_expr(left):
    args = self._parse_args(')')
    left = f"({left} {' '.join(args)})" if args else f"({left})"
    continue
```

关键效果：
- `f(x)` → `(f x)`（函数调用）
- `x(x+1)` → `(x (+ x 1))`（函数调用 — x 作为函数）
- `(x+1)(x+2)` → `(* (+ x 1) (+ x 2))`（隐式乘法 — 左端不是裸名称）

### 2. 一元负号用 Scheme 标准 `(- x)`

从 `_prefix` 调用 `self.parse(31)`，比二元 `+`/`-` 的 30 高 1：

```python
# parser/infix.py:184-186
if tok == '-':
    right = self.parse(31)
    return f"(- {right})"
```

效果：`-x + y` → `(+ (- x) y)`（不 capture `+` 到 negate 内）。

⚠️ **历史教训**: 最初用 `(negate x)` 但 `negate` 非 Scheme 标准符号，
导致求值时 `Unbound variable`。改用 `(- x)` 后直接复用现有 `prim_sub` 一元处理，
且对 sympy PythonObject 自动走 `try_py_unary_op("negate", args)` 代理。

### 3. `^` 右结合

```python
next_bp = bp if op == '^' else bp + 1
```

`a^b^c` → `(expt a (expt b c))`，而非 `(expt (expt a b) c)`。

### 4. 隐式乘法优先级 45

介于 `*`(40) 和 `^`(60) 之间：

```
2x^2    →  (* 2 (expt x 2))    ✅  隐式乘低于幂
2x*y    →  (* (* 2 x) y)       ✅  隐式乘左结合
x^2y    →  (* (expt x 2) y)    ✅  幂高于隐式乘
```

### 5. 比较运算符语义

`=` 映射到 `(eqn ...)` 而非 `(= ...)`，因为 Scheme 的 `=` 只用于数值相等比较。`(eqn ...)` 在 CAS 上下文中构造 `sympy.Eq`。

## 集成点

### Tokenizer 路径

`tokenize.py` 中 `#` 处理分支新增：

```python
if input_str[i+1] == '{':
    start = i; i += 2  # skip ' #{'
    depth = 1
    while i < span_len and depth > 0:
        if input_str[i] == '{': depth += 1
        elif input_str[i] == '}': depth -= 1
        i += 1
    tokens.append(input_str[start:i])
```

`parse_form.py` 中：

```python
case _ if token.startswith('#{') and token.endswith('}'):
    content = token[2:-1].strip()
    expr_str = parse_infix(content)
    inner_tokens = tokenize(expr_str)
    inner_idx = [0]
    result = parse_form(inner_tokens, inner_idx)
    return result
```

### Reader 路径

`reader.py` 的 `read_datum` 中，`#` case 新增：

```python
if next_c == '{':
    port.read_char()  # consume '{'
    # read from port until '}', handle nesting
    infix_content = ''.join(chars).strip()
    expr_str = parse_infix(infix_content)
    return read_datum(InputStringPort(expr_str))
```

## Tokenizer 细节

`tokenize_infix` 与主 tokenizer 不同，独立于 `parser/tokenize.py`：

- `;` 在 infix tokenizer 中是普通运算符 token（矩阵行分隔），**不**视为注释
- 新增 `|`、`_`、`!` 单字符 token
- `..` 作为复合 token（在 `.` 处理前检测）
- 数字遇到 `..` 提前停止（避免 `1..10` 被吞为 `1.` + `.10`）
- 标识符在遇到 `_` 时停止（分隔符列表包含 `_`）

## Unicode 别名表

定义在 `_UNICODE_ALIASES` 字典（约 24 个映射）。仅在中缀解析器内生效，不影响 Scheme reader 的 `#\` 字符字面量。

## 测试验收标准

全部通过 25+ 测试用例：

| 特性 | 输入 | 输出 |
|------|------|------|
| 绝对值 | `\|x\|` | `(abs x)` |
| 绝对值复合 | `\|x-1\|` | `(abs (- x 1))` |
| 绝对值嵌套 | `\|sin(x)\|` | `(abs (sin x))` |
| 绝对值+运算 | `\|x\| + \|y\|` | `(+ (abs x) (abs y))` |
| 阶乘 | `5!` | `(factorial 5)` |
| 阶乘+运算 | `3! * 2` | `(* (factorial 3) 2)` |
| 范围 | `1..10` | `(range 1 10)` |
| 范围(变量) | `2..n` | `(range 2 n)` |
| 下标 | `x_y` | `(ref x y)` |
| 下标+分组 | `a_{n+1}` | `(ref a (+ n 1))` |
| 矩阵 2×2 | `[1 2; 3 4]` | `(matrix (list 1 2) (list 3 4))` |
| 矩阵 3×3 | `[1 2 3; 4 5 6; 7 8 9]` | `(matrix ...)` |
| 矩阵列向量 | `[1; 2; 3]` | `(matrix (list 1) (list 2) (list 3))` |
| 矩阵单位阵 | `[1 0 0; 0 1 0; 0 0 1]` | `(matrix (list 1 0 0) ...)` |

全部原有功能（优先级/隐式乘法/函数调用/一元负号/comparison）向后兼容。

## 已知限制

1. `xy` 是单标识符，不是 `(* x y)`
2. `[...]` Reader 路径无 `(bracket ...)` 包装（既有差异，非 infix 问题）
3. 不支持中缀内的 Scheme 特殊形式（如 `lambda`、`define`）
4. 矩阵元素中不能用复杂表达式包含 `;` 或 `]`（解析器按 token 扫描 `]` 结尾）
5. `x . 5` 的 `.` 被数字 tokenizer 吞入（应使用 `1..5` 范围语法）
