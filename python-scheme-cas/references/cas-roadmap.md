# Scheme CAS 发展路线图

## 当前状态

**完成度 ≈ Maxima 的 60%**。当前本质是"Python API 的 Scheme 语法糖封装"，以下 7 个 Phase 指向真正的"Scheme 风格 CAS"。

## Phase 1 — 中缀表达式 reader macro（已完成 ✅）

`#{...}` infix reader macro 已完整实现于 `parser/infix.py`（Pratt 解析器）+ 两条解析路径的集成（tokenizer 和 reader）。

详见 `references/infix-parser.md` 和 SKILL.md 的 Phase 1 小节。

```scheme
#{x^2 - 4*x = 0}  →  (eqn (- (expt x 2) (* 4 x)) 0)
#{sin(x) + cos(x)}  →  (+ (sin x) (cos x))
#{(x+1)(x+2)}  →  (* (+ x 1) (+ x 2))
```

## Phase 2 — 可视化后端 + 帮助系统（已完成 ✅）

### 可视化 (matplotlib 后端)

三个绘图函数，全部支持关键词参数：`:title :xlabel :ylabel :grid :legend :save :show :size :xlim :ylim`。

```scheme
;; 2D 单/多迹线
(plot #{x^2} x -5 5 :title "Parabola" :grid #t)
(plot (list #{sin(x)} #{cos(x)}) x 0 6.28 :legend #t :show #f)

;; 2D 参数曲线
(plot-param #{cos(t)} #{sin(t)} t 0 6.28 :title "Circle")

;; 3D 曲面
(plot3d #{x^2 + y^2} x -2 2 y -2 2 :title "Paraboloid")
```

**实现**：`eval/eval_py_viz.py`。使用 `matplotlib.use('Agg')` 非交互后端（WSL 兼容），`matplotlib.pyplot` 渲染。plot3d 使用 `mpl_toolkits.mplot3d.Axes3D`。关键词参数在 Prim 函数内部手动解析（`Prim` 不自动分离 `:key val` — 匹配 `Syms` 的 `:xxx` 前缀手动解析）。

### 帮助系统

```scheme
(help)                 → 按 16 个分类列出全部 82 个 CAS 函数
(help 'integrate)      → 显示语法、说明、示例
(help "方程")          → 搜索包含关键词的函数
```

**实现**：`eval/eval_py_help.py`。包含 `_CAS_FUNCTIONS` 字典数据库（82 条，16 分类）。`Prim("help", cas_help)` 注册。

### 新增文件

| 文件 | 内容 |
|------|------|
| `eval/eval_py_viz.py` | 可视化后端 — matplotlib 2D/参数/3D 绘图 |
| `eval/eval_py_help.py` | 帮助系统 — 82 函数结构化文档数据库 |

### 注册

在 `primitives/primitives.py` 中加入 `from eval.eval_py_viz import register_viz_primitives` 和 `from eval.eval_py_help import register_help_primitives`，并在 `register_all()` 中调用。同时从 `eval/eval_py_cas.py` 的注册表中移除旧的 `plot`（原基于 sympy.plot，被新 matplotlib 版取代）。

## Phase 3 — symengine 引擎切换 + 惰性导入（已完成 ✅）

```scheme
(use-engine 'auto)           → symengine 优先，不支持时自动 fallback 到 sympy（默认）
(use-engine 'symengine)      → 强制使用 symengine（10-100x 更快）
(use-engine 'sympy)          → 强制使用 sympy（完整功能）
(engine-info)                → 显示当前引擎 + 可用引擎版本
```

### 架构

`eval/eval_cas_engine.py` 提供了 `get_engine()` 统一接口，替代 `_sympy()` 中的直接 `import sympy`：

```
用户 → (use-engine 'symengine)
        → eval_cas_engine._current_engine = 'symengine'
        → 所有 CAS 原语通过 _sympy() → get_engine() → symengine 模块
        → 不可用时自动 fallback 到 sympy
```

### 惰性导入

- 两个引擎均在首次 `get_engine()` 调用时惰性导入
- 结果缓存于 `_engine_cache` 字典
- 不用的引擎不消耗导入时间

### 交叉兼容性

symengine 和 sympy 类型可混合使用，引擎切换可在运行时任意进行：

```python
symengine.expand((sympy.Symbol('x') + 1)**2)  # ✅
sympy.factor(symengine.Symbol('x')**4 - 1)     # ✅
```

### 能力矩阵

| 操作 | symengine | sympy |
|------|:---------:|:-----:|
| diff/expand/series/sin/sqrt/Matrix/Eq | ✅ | ✅ |
| factor/integrate/solve/limit/det/inv/dsolve | ❌ | ✅ |

### 修复的问题

- `math.sin(symengine.Symbol('x'))` 抛 `RuntimeError` 而非 `TypeError`，`try_py_unary_math`/`try_py_atan`/`log` 已添加 `RuntimeError` 捕获
- `eval_python_import.py` 被截断为 5 行 — 从 `.pyc` 恢复完整源码（390 行）

### 实现文件

| 文件 | 内容 |
|------|------|
| `eval/eval_cas_engine.py` | 引擎管理器（新建） |
| `eval/eval_py_arithmetic.py` | `RuntimeError` 捕获修复 |
| `primitives/primitives.py` | `register_engine_primitives` 注册 |

## Phase 4 — 假设系统 + 代数完备

### 假设系统
```scheme
(assume x > 0)
(assume y 'real)
(simplify (sqrt (expt x 2)))  ; → x (因为 x > 0)
```

**实现**: `assume` 宏调用 `sympy.assumptions.assume.global_assumptions.add`。

### 缺失 sympy 功能覆盖

| 功能 | sympy API | 建议原语 |
|------|-----------|---------|
| 有理数 | `Rational(n, d)` | `(rational n d)` |
| 分段函数 | `Piecewise` | `(piecewise expr condition)` |
| 不等式求解 | `reduce_inequalities` | `(solve-ineq expr)` |
| 张量 | `tensor` | `(tensor ...)` |
| 群论 | `Permutation` | `(permutation ...)` |
| 几何 | `Point, Line, Circle` | `(point x y)` |
| 逻辑 | `And, Or, Implies` | `(logical-and ...)` |

### 用户自定义数学函数
```scheme
(define f (cas-function f (x) (+ (* a x) b)))  ; 同时定义 Scheme 闭包和 sympy.Function
(diff (f x) x)                                   ; → a
```

## Phase 5 — numpy 共享内存 + numba JIT

### 零拷贝数组
当前 numpy 数组 ↔ Scheme Vector 全量拷贝。目标：Python 缓冲区共享。

```scheme
(define arr (py-buffer 1000000))  ; 预分配共享内存
[arr 0]                           ; 不拷贝直接访问
(arr.__setitem__ 0 42)            ; 就地修改
```

**实现**: 添加 `py-buffer` 原语，用 `memoryview` + `__array_interface__` 共享 numpy 缓冲区。

### Numba JIT
```scheme
(define f (py-numba-lambda (x y) (+ (* x x) (* y y))))
; → @numba.njit 编译的 Python 函数，直接从 Scheme 调用
```

## Phase 6 — 教程笔记本 + 项目打包

### 教程文件 (10 个)

创建 `tutorial/` 目录：

| 文件 | 内容 |
|------|------|
| `01_basic_arithmetic.scm` | 基础算术、导入、类型转换 |
| `02_symbolic_arithmetic.scm` | defsym、算术透明度、sympy 基本操作 |
| `03_calculus.scm` | integrate、diff、limit、series |
| `04_algebra.scm` | expand、factor、simplify、solve |
| `05_linear_algebra.scm` | matrix、det、inv、eigenvals |
| `06_odes.scm` | dsolve、laplace、fourier |
| `07_numerical.scm` | numpy 数组、scipy 数值计算 |
| `08_plotting.scm` | plot、pretty、latex |
| `09_optimization.scm` | scipy.optimize、cvxpy、pulp |
| `10_number_theory.scm` | 数论、集合、统计、特殊函数 |

每个教程文件可被 `python3 main.py tutorial/01_*.scm` 执行，输出可见结果。

### 项目打包

创建 `pyproject.toml` 让 `pip install .` 可安装，包括 entry-point:

```python
[project.scripts]
scheme-cas = "main:main"
```

## Phase 7 — 生态扩展

### R 语言桥接 (rpy2)
```scheme
(import rpy2.robjects as ro)
(ro.r['lm'] "y ~ x" :data df)  ; R 统计模型
```

### 数据库集成
```scheme
(import sqlalchemy)
;; 查询结果 → Scheme 数据处理 → pandas → matplotlib
```

### 符号回归 (PySR)
```scheme
(import pysr)
(pysr.pysr x y)                             ; y = f(x) 找到解析表达式
```

## 实现优先级路线图

```
Phase 1 (2-3 天):  中缀 reader macro + 方程 DSL    ← 最大用户体验提升
Phase 2 (1-2 天):  可视化后端 (plot → 文件) + help 系统
Phase 3 (2-3 天):  symengine 引擎切换 + 惰性导入      ← 性能
Phase 4 (3-5 天):  假设系统 + 代数完备 (不等式/分段/张量)
Phase 5 (2-3 天):  numpy 共享内存 + numba JIT
Phase 6 (3-5 天):  教程笔记本 + 项目打包 + 包注册表
Phase 7 (持续):    生态扩展 (rpy2/sqlalchemy/PySR)
```

### 依赖关系

```
Phase 1 → Phase 4 (中缀使方程 DSL 自然)
Phase 2 → Phase 6 (可视化是教程的关键)
Phase 3 → 独立（仅影响 eval_py_cas.py）
Phase 5 → 独立（仅影响 eval_python_import.py）
Phase 6 → Phase 2 (教程需要绘图输出)
Phase 7 → Phase 3 (生态扩展需要稳定的引擎抽象)
```