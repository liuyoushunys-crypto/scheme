# 宏 / Prim / 特殊形式 三选一决策指南

CAS 系统中选择哪种机制实现新功能，取决于是否需要延迟求值、符号操作、和环境访问。

## 决策树

```
需要延迟求值（body 在特定条件下执行）？
  ├── 是 → 需要环境访问？
  │   ├── 是 → 特殊形式（eval_scheme.py 加 case）
  │   └── 否 → macro (define-macro)
  └── 否 → Prim（最简单，参数已求值）

需要对用户符号进行操作（quote/模式匹配）？
  ├── 是 → macro（参数未求值）
  └── 否 → Prim

需要在多步间保持状态？
  ├── 是 → Prim（Python closure 持有状态）
  └── 否 → 任意
```

## 三种机制对比

| 特性 | Prim | define-macro | 特殊形式 |
|------|------|-------------|----------|
| 参数求值时机 | **前**（调用前已求值） | **后**（宏展开时仍为源码） | **后**（eval_scheme 控制） |
| 环境访问 | 通过 closure 传入 | 展开时 implicit env | eval_scheme 直接传递 |
| 可实现的功能 | 函数调用、状态持有 | 源码变换、DSL | 控制流、绑定构造 |
| 修改位置 | `eval/cas/*.py` | `eval/cas/sugar/core.py` | `eval/eval_scheme.py` |
| 实现复杂度 | 最低 | 中等（非卫生陷阱） | 高（需理解求值器） |
| 可维护性 | 最好 | 一般（符号泄漏风险） | 好 |

## 陷阱

### parse() 只返回第一个表达式

`parse()` 调用 `parse_program()` 但只返回 **第一个** 表达式。多表达式字符串必须用 `(begin ...)` 包裹：

```python
# ❌ 只注册了 +=，-= *= /= 丢失
_P2 = """(define-macro (+= v val) ...)
(define-macro (-= v val) ...)"""

# ✅ 全部注册
_P2 = """(begin
  (define-macro (+= v val) ...)
  (define-macro (-= v val) ...))"""
```

这是 `eval/cas/sugar/core.py` 中最常见的宏注册 bug。所有多表达式宏定义字符串必须检查：实际注册了几个？用 `(begin ...)` 包裹。

### define-macro 无 gensym / 无字符串函数

此 Scheme 的 define-macro 环境中 **没有 `gensym`、`string->symbol`、`string-append` 等函数**。这意味着：

- **不能动态构造符号名**：`(string-append "make-" (symbol->string name))` 不可用
- **不能生成唯一变量**：用 `%` 前缀约定（`%v`, `%saved`, `%e`）避免与用户变量冲突
- **`(quote x)` vs 变量引用**：宏参数是 `Sym` 对象。`(list 'quote engine)` 生成 `(quote Sym(name='symengine'))` — 这是字面量，不是变量引用。要生成变量引用，直接用 `engine`（不带 quote）。

### Prim 的「参数已求值」陷阱

Prim 是最直观的实现方式，但**所有参数在 Prim 运行前已经被求值**。这意味着：

```scheme
;; (with-eng 'symengine (body...)) — body 已在当前引擎下求值完毕!
;; Prim 收到的是求值后的值，不是表达式
```

**解决方案**：要求用户 quote body → `(with-eng 'symengine '(body...))`，Prim 内部用 `eval_scheme` 重新求值。

### define-macro 的「非卫生」陷阱

define-macro 生成的代码中，所有符号都在**用户环境**中查找：

```scheme
(define-macro (with-eng engine . body)
  (list 'use-engine engine))  ;; engine 是 Sym 对象，插入代码后是字面量
```

生成 `(use-engine Sym('symengine'))` → Sym 对象作为字面量被 eval，查找到 symengine 模块（而非用名字切换引擎）。

**符号泄漏**：宏内生成的临时变量名可能与用户变量冲突：

```scheme
(define-macro (my-let val . body)
  `(let ((x ,val)) ,@body))  ;; x 会捕获用户环境的 x！
```

**解决方案**：用 `%` 前缀（`%v`, `%saved`）做内部变量名，极低概率与用户代码冲突。

### parse() 只返回第一个表达式

`eval/cas/sugar/core.py` 用 `eval_scheme(parse(code), env)` 注册宏代码。但 `parse()` 只返回**第一个**表达式。多表达式必须用 `(begin ...)` 包裹：

```python
# ❌ 只注册了 +=
_P2_AUGMENT = """
(define-macro (+= var val) ...)
(define-macro (-= var val) ...)
"""

# ✅ 全部注册
_P2_AUGMENT = """
(begin
  (define-macro (+= var val) ...)
  (define-macro (-= var val) ...))
"""
```

### 宏递归扩展

define-macro 的结果会被重新输入求值器。如果结果也以宏开头，会产生**无限递归**：

```scheme
(define-macro (.. obj . steps)
  (list '.. transformed steps))  ;; ❌ .. 再次被展开
```

**解决方案**：在一次展开中完成整个变换（迭代而非递归）。

```scheme
(define-macro (.. obj . steps)
  (if (null? steps)
      obj
      (let loop ((expr obj) (remaining steps))
        (if (null? remaining)
            expr
            (let ((step (car remaining)))
              (loop
                (cons 'py-call
                  (cons (list 'py-get expr (list 'quote (car step)))
                    (cdr step)))
                (cdr remaining)))))))  ;; ✅ 一次展开全部步骤
```

### `register_primitives` vs `register_xxx_primitives` 导出约定

内部 CAS 模块有两种注册函数导出模式：

**包模块**（有 `__init__.py` + `core.py`）：  
`__init__.py` 必须同时导出命名函数（供 `primitives.py` 使用）和 `register_primitives`（供聚合器使用）：

```python
"""tensor"""
from .core import register_tensor_primitives
from .core import register_primitives
```

**扁平文件**（无子目录）：  
直接导出命名函数和 `register_primitives` 别名：

```python
def register_engine_primitives(env):
    ...
register_primitives = register_engine_primitives
```

`primitives.py` 中统一使用命名导入：`from eval.cas.engine import register_engine_primitives`。包模块通过 `__init__.py` 重导出实现相同效果。

## 已知用例

| 功能 | 选择 | 理由 |
|------|------|------|
| `with-eng` | Prim + quote body | 需要环境访问+延迟求值，但不如特殊形式侵入 |
| `with` | macro | 简单源码变换，无环境需求 |
| `+= -= *= /=` | macro | 极简变换，无陷阱 |
| `pmatch` | macro | 需要在展开时生成 cond+let 树 |
| `define-data` | macro | 简单的构造器生成 |
| `sym` | macro | 自动插入 `(import sympy)` |
| `try` | 特殊形式 | 需要延迟求值+环境访问，宏的非卫生性无法优雅处理 |
| `match` | 特殊形式 | `?x` 模式变量需要自求值（eval_scheme 的 Sym case） |

## 总结

1. **能 Prim 且够用 → Prim**（最简单，最好维护）
2. **需要简单的源码变换 → macro**（注意非卫生陷阱）
3. **需要延迟求值 + 环境访问 → 特殊形式**（最强大，但需改求值器）
4. **延迟求值 + 不需要环境访问 → Prim + quote body**（实用折中）
