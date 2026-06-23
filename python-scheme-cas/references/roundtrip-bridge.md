# 四向往返映射 — 桥接原语设计

## 映射链

```
str -> S-表达式 -> sympy -> symengine
 |        |          |        |
 parse  wrap     sympify   |
   |        |          |        |
 +- srepr -> parse  unwrap  sympify
                         (eval fallback)
```

## 5 个桥接原语

| 原语 | 签名 | 用途 |
|------|------|------|
| `unwrap-python` | `(unwrap-python val) -> Python原生` | 解包为 Python 值 |
| `wrap-python` | `(wrap-python val) -> Scheme值` | 包装为 Scheme 值 |
| `py-str` | `(py-str val) -> Scheme字符串` | Python str() 表示 |
| `py-eq` | `(py-eq a b) -> #t/#f` | Python == 比较 |
| `py-type` | `(py-type val) -> 类型名字符串` | Python type().__name__ |

## srepr 闭环

`sympy.srepr()` 输出 Python 表达式（如 `Add(Symbol('x'), Integer(2))`），
`parse` 用 `eval()` 回退解析：

```python
SAFE_DICT = {
    'Symbol': sp.Symbol, 'Integer': sp.Integer, 'Float': sp.Float,
    'Rational': sp.Rational, 'Mul': sp.Mul, 'Add': sp.Add,
    'Pow': sp.Pow, 'sin': sp.sin, 'cos': sp.cos,
    'sqrt': sp.sqrt, 'exp': sp.exp, 'log': sp.log,
    'pi': sp.pi, 'E': sp.E, 'oo': sp.oo,
}
eval(srepr_str, {"__builtins__": {}}, SAFE_DICT)
```

`parse_expr` 失败 -> 自动 fallback 到 eval（安全沙箱）

## symengine <-> sympy 互操作

```scheme
(import symengine)
(define se-x (symengine.Symbol 'x))
; 双向转换：
(sympy.sympify se-expr)          -> sympy 对象
(symengine.sympify sp-expr)      -> symengine 对象
```

类型兼容：symengine 和 sympy 类型可混合运算，+/*/- 等自动代理。

## 引擎自动调度

| 操作 | symengine | sympy 降级 |
|------|:---------:|:----------:|
| diff/expand/sin/Eq | ✅ | - |
| integrate/factor/simplify | ❌ | ✅ 自动 |
| solve/limit/dsolve | ❌ | ✅ 自动 |

## 注册位置

桥接原语注册在 `eval/eval_python_import.py` 的 `register_python_import_primitives` 中：

```python
env.define("unwrap-python", Prim("unwrap-python", py_unwrap_prim))
env.define("wrap-python", Prim("wrap-python", py_wrap_prim))
env.define("py-str", Prim("py-str", py_str_prim))
env.define("py-eq", Prim("py-eq", py_eq_prim))
env.define("py-type", Prim("py-type", py_type_prim))
```

## 新增模块注册模式（2026-06 目录重组后）

自 2026-06 起，`eval/` 目录按功能分为子目录：

```
eval/
├── cas/       # CAS 子系统 (17 文件)
│   ├── core.py, parse.py, tensor.py, pattern.py, engine.py ...
├── data/      # 数据处理
│   ├── json.py, csv.py, serialize.py
├── text/      # 文本处理
│   ├── re.py
├── io/        # I/O 操作
│   ├── path.py, http.py, image.py, compress.py, db.py
├── crypto/    # 加密
│   ├── crypto.py
└── system/    # 系统信息
    ├── system.py, datetime.py
```

注册模式不变：`from eval.<subdir>.<module> import register_XXX_primitives`

## 已知陷阱

### Bytevector 使用 .data 而非 .value

```python
# 错误：
val.value            # Bytevector 没有 .value 属性
# 正确：
val.data             # Bytevector 存储 bytearray
bytes(val.data)      # 转为 Python bytes
```

### scheme_format 自定义类型显示

在 `core/schemevalue.py` 的 `scheme_format` 函数默认分支添加：

```python
case _:
    s = str(val)
    if s != "unknown":
        return s
    return "unknown"
```
