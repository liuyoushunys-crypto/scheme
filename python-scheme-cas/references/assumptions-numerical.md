# 假设系统 + 数值方法 参考

## 假设系统

### 谓词表 (Q 属性)

| 谓词 | Scheme 写法 | 含义 |
|------|-----------|------|
| `Q.positive(x)` | `(assume '(positive x))` | x > 0 |
| `Q.negative(x)` | `(assume '(negative x))` | x < 0 |
| `Q.nonnegative(x)` | `(assume '(nonnegative x))` | x ≥ 0 |
| `Q.nonpositive(x)` | `(assume '(nonpositive x))` | x ≤ 0 |
| `Q.zero(x)` | `(assume '(zero x))` | x = 0 |
| `Q.nonzero(x)` | `(assume '(nonzero x))` | x ≠ 0 |
| `Q.integer(x)` | `(assume '(integer x))` | x ∈ ℤ |
| `Q.real(x)` | `(assume '(real x))` | x ∈ ℝ |
| `Q.rational(x)` | `(assume '(rational x))` | x ∈ ℚ |
| `Q.even(x)` | `(assume '(even x))` | x 偶数 |
| `Q.odd(x)` | `(assume '(odd x))` | x 奇数 |
| `Q.prime(x)` | `(assume '(prime x))` | x 素数 |
| `Q.imaginary(x)` | `(assume '(imaginary x))` | x 纯虚数 |

### 比较运算符谓词

| 写法 | sympy 等价 | 说明 |
|------|-----------|------|
| `(assume '(> x 0))` | `Q.gt(x, 0)` | x > 0 |
| `(assume '(< x 0))` | `Q.lt(x, 0)` | x < 0 |
| `(assume '(>= x 0))` | `Q.ge(x, 0)` | x ≥ 0 |
| `(assume '(<= x 0))` | `Q.le(x, 0)` | x ≤ 0 |
| `(assume '(= x 0))` | `Q.eq(x, 0)` | x = 0 |

### 已知限制

1. `Q.gt(x, 0)` **不隐含** `Q.positive(x)` — sympy 假设系统将关系谓词和性质谓词视为独立的。若需 `refine(sqrt(x^2))` → `x`，请用 `(assume '(positive x))` 而非 `(assume '(> x 0))`。

2. `refine(sin(n*pi), integer(n))` → `sin(pi*n)`（未化简）— sympy 的 `refine` 对整数+三角的推理能力有限。

3. 全部假设底层基于 `sympy.assumptions.assume.global_assumptions`（全局）和 `sympy.assumptions.assuming`（临时上下文），
   `refine` 使用 `sympy.refine`。

## 数值方法

### find-root

```scheme
(find-root expr_or_fn a b :method 'brentq)
```

- 后端: `scipy.optimize.brentq` (默认), `bisect`, `newton`, `ridder`
- 支持 sympy 表达式、Scheme closure、Python callable
- sympy 表达式自动 `lambdify` → numpy callable

### numerical-integrate

```scheme
(numerical-integrate expr_or_fn a b)
```

- 后端: `scipy.integrate.quad`
- 返回积分值的近似浮点数

### 关键实现细节

```python
def _to_callable(f):
    """将 Scheme 值转为 Python 可调用对象"""
    py_obj = f.obj if isinstance(f, PythonObject) else f
    if callable(py_obj):
        return py_obj
    # sympy 表达式 → lambdify
    if hasattr(py_obj, 'free_symbols'):
        symbols = list(py_obj.free_symbols)
        if symbols:
            f_lambda = sympy.lambdify(symbols, py_obj, 'numpy')
            ...
    # Scheme Closure → 包装
    if isinstance(f, Closure):
        def wrapped(x):
            result = apply_tail(f, [wrap_python_value(float(x))], f.env)
            ...
```

### 陷阱

1. **sympy 表达式不是 callable** — 不能 `callable(expr)` 判断。要用 `hasattr(expr, 'free_symbols')` 检测。
2. **lambdify 多变量**: `(find-root f 0 1)` 时若 `f` 有多个自由变量会失败（取了第一个符号）。
