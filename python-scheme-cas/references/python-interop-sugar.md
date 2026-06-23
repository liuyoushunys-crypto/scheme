# Python 互操作糖 — `py` / `py-f` / `..`

此会话新增三个简化 Python ↔ Scheme 互操作的扩展。

## `(py "expr")` — 自动注入 eval

```scheme
;; 之前：手动列出每个变量
(py-eval "sp.diff(x**3, x)" :x x)

;; 之后：自动注入 env 变量
(py "sp.diff(x**3, x)")
```

**实现**：Prim 用 `re.findall` 提取表达式中的标识符，在 env 中查找并组装 locals dict。

**陷阱**：
- 不注入 Python 关键字（`True`, `None`, `import` 等）和常见内置函数
- 自动注入 `np`(numpy)、`sp`(sympy)、`math` 模块
- 属性链（`np.linalg.solve`）只提取顶级名（`np`）
- 如果变量不在 env 中，跳过（不报错）

## `(py-f "fmt")` — Python f-string 格式化

```scheme
;; Python 风格 f-string，变量从 Scheme env 注入
(py-f "det = {m.det()}")
(py-f """Values:
a = {a}
x = {x}
""")
```

**实现**：用 Python 的 `eval(f"""...""")` 执行 f-string，变量从 env 注入。

**陷阱**：注入的变量是 Python 原生类型，不是 Scheme 值。sympy Symbols 可直接使用。

## `(.. obj (method args)...)` — 方法链

```scheme
;; 嵌套写法
(det (inv (sp.Matrix [[1 2; 3 4]])))

;; 链式写法  
(.. (sp.Matrix [[1 2; 3 4]]) (inv) (det))
```

**实现**：define-macro，在一次展开中完成全部步骤迭代（非递归展开，避免宏无限循环）。每个 step 展开为 `(py-call (py-get obj 'method) args...)`。

**陷阱**：
- `..` **不能**用递归 `(list '.. ...)` 展开（宏重复展开导致无限循环）
- 必须用 `let loop` 在一次展开中完成所有步骤
- 第一步的 obj 是未求值的 Scheme 表达式，后续步骤的 obj 是前一步 `py-call` 的结果

## `"""..."""` 多行字符串

Python 风格三重引号字符串，已在 tokenizer 和 parser 中支持。

```scheme
(py "np.array([
    [1, 2, 3],
    [4, 5, 6]
])")
```

**实现**：
- `parser/tokenize.py`：检测 `"""`，收集至闭合 `"""，跳过紧跟换行（Python习惯），支持 `\` 转义
- `parser/parse_form.py`：检测 `"""..."""` token，剥离外层三引号

**注意**：不支持 `f"""..."""` 前缀语法 — 用 `(py-f """...""")` 替代。
