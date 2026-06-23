---
name: python-scheme-cas
description: Python-Scheme 互操作层 + CAS (Computer Algebra System) — 让 Scheme 无缝调用整个 PyPI 数学生态。覆盖导入桥接、级联调用、关键词参数、算术透明度、闭包回调、方括号索引。内部 CAS 核心模块位于 eval/cas/，提供 90+ 数学原语。PyPI 包通过通用导入桥接直接使用，无需预包装器。
category: software-development
triggers:
  - Scheme/Python 互操作
  - CAS 数学计算 (integrate, diff, solve, dsolve 等)
  - PyPI 包集成
  - 构建 Scheme 中的符号/数值计算系统
  - 设计跨语言调用桥接
  - sympy/numpy/scipy/pandas/sklearn/cvxpy 集成
  - 需要 Maxima 级 CAS 的替代方案
  - numpy/sklearn/statsmodels/scipy 的 Scheme 友好 API
  - 构建科学计算包层级浏览目录系统
  - 语法糖增强 (λ/->/->>/for/str 宏)
  - 非参数模型与 ML 工作流 (CV/GridSearch/Pipeline)
  - CAS 系统评估与差距分析
  - (nav) 分级导航系统设计
  - try/catch 异常处理特殊形式
  - 引擎自动降级代理模式
  - LaTeX/MathML/Mathematica 数学表达式解析
---

# Python-Scheme CAS 系统设计指南

> **更新 2026-06-26 (多轮补齐)**: 覆盖率的正确度量必须以 **site-packages**（真实 Python API）为基准。经过多轮批量生成，总 `env.define` 从 1226 → 1909 (+683)，demo.md 从 1200 → 2001 (+801)。详见 `references/site-packages-audit.md`。重点：补齐 gap 的正确方法是批量自动生成包装器 + demo，非人工逐一手写。

## 覆盖审计规则（2026-06-23 新增）

**倒果为因陷阱**：之前在包装层（`eval/cas/`）里数 `env.define`，声称 "100% 覆盖"。这是错的。正确方法：

```
site-packages 真实 API → eval/cas 包装层 → demo.md 文档
         ↑ 本源           ↑ 桥梁             ↑ 用户可见
```

### 正确计数法

```python
# ✅ AST 解析找到所有 env.define 注册名
# ✅ 对比 dir(numpy) 中真实可调用函数
# 缺口 = site_packages_API - eval_cas_wrappers
```

### 真实覆盖率（2026-06-23）

| 包 | 真实 API | 已包装 | 真实覆盖率 |
|:---|:--------:|:------:|:----------:|
| numpy | 496 | 352 | 71% |
| scipy | 21子包(~1000函数) | 77 | ~5% |
| pandas | 119 | 16 | 13% |
| networkx | 944 | 12 | 1% |

**结论**：`env.define` 数 ≠ 覆盖完成。缺口分析必须以 site-packages 为基准。

### 三周期精炼法

用户反复纠正"模块分级很不细致"后确立的迭代模式：

```
周期1: 拆大平摊类别       (numpy/math 144→12子类, statsmodels 24→5类)
周期2: 拆新建模块子分类   (11个模块 47 subcategory)
周期3: 修复导入链         (__init__.py→core.py 每级验证)
```

每轮修复后运行 `python3 -c "from eval.cas.{mod} import register_{mod}_primitives"` 验证不断裂。

详见 `references/site-packages-audit.md`。

## 核心理念

**代码组织偏好**：多级目录结构，不接受扁平。大文件必须持续拆分直到单一职责。重构必须 0 断裂（shim 模式 → 最后删除所有 shim）。

## 极端粒度拆分模式

当用户要求"拆分到单例级别"时，每个函数/类/原语一个独立子目录：

```
模块/
├── core.py              ← 聚合器 (导入所有单例目录)
├── __init__.py          ← 重新导出聚合器
├── func_1/
│   ├── core.py          ← register_func_1(env) — 注册 1 个原语，必须自导入 Sym/Prim/...！
│   ├── __init__.py      ← 导出 register_func_1
│   └── demo.md          ← 该原语的完整使用文档
├── func_2/ ...
```

**聚合器模板**（parent/core.py）：
```python
from eval.cas.mymod.func_1.core import register_func_1
from eval.cas.mymod.func_2.core import register_func_2

def register_mymod(env):
    register_func_1(env)
    register_func_2(env)
```

**单例 core.py 模板**：
```python
\"\"\"mymod/func_1 — 说明\"\"\"
from core.schemevalue import Sym, Prim, PythonObject  # 必须自导入！
from eval.eval_python_import import wrap_python_value, unwrap_python_value

def register_func_1(env):
    ...  # 注册单一原语
```

**类名→目录名转换**（camel_to_snake）：
```python
import re
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()  # LinearRegression→linear_regression, SVC→svc
```

## demo.md 编写标准（2026-06-22 更新）

每个单例目录的 demo.md 必须"丰满"（傻瓜教材式）：

1. **用实参演示，不用形参** — 不要写抽象的参数表（`| a | 数组 | 输入数组 |`），直接写带真实值的调用示例。
2. **多组代码示例** — 每组示例 = 输入 + 预期输出。输出在代码下一行，缩进 + `→` 前缀。每个参数的实际用法通过具体实例展示。
3. **注意事项** — 边界情况、常见陷阱、类型限制
4. **适用场景** — 什么时候用这个函数/类
5. **同类对比** — 与其他方法的差异对照表
6. **最佳实践** — 推荐参数设置和使用模式
7. **代码注释** — 每行 Scheme 代码带 `;` 注释。Python core.py 必须带模块 docstring + register 注释 + getattr 注释 + env.define 注释。
8. **实际应用场景** — 核心函数用真实场景演示（FFT→信号分析, 图像滤波→频域处理, 分类→完整 ML 流程）。

**输出格式**：
```scheme
; FFT 频谱分析
(np.random.seed 42)                          ; 固定随机种子
(define sig (* 0.7 (np.sin (* 2 pi 50 t)))) ; 50Hz 正弦信号
(np.fft sig)                                 ; FFT → 频域复数
```

**绝对禁止**：把示例放在 Python docstring 中 — 编辑意外破坏语法结构。始终坚持 `demo.md` 独立文件模式。

**core.py 注释模式**：
```python
# 注册 np.fft 原语
def register_fft(env):
    """注册 np.fft 到 Scheme 环境。"""
    fn = getattr(_np, "fft", None)           # 从 NumPy 获取 fft 函数
    if fn is None:
        return
    env.define(Sym("np.fft"), Prim("np.fft", # 注册为 Prim 原语
        lambda args: wrap_python_value(fn(*[unwrap_python_value(a) for a in args]))))
```

**目录名称规则**：禁止中文作为目录或文件名。所有包名、文件名为英文 kebab-case 或 ASCII。\n\n**子模块导入独立性**：每个子模块的 `core.py` 是独立加载的（通过 `subpkg/__init__.py` 暴露），不是通过父模块的 import 传递的。因此每个 `subpkg/core.py` 必须**自己导入**它需要的所有符号（`Sym`, `Prim`, `wrap_python_value`, `unwrap_python_value`, `PythonObject`, `call_metrics` 等）。绝不能依赖调用方（`__init__.py` 或父级 `core.py`）的 import 传递作用域。详见 `references/learn-module-pattern.md`。\n\n**目录名称规则**：Python 包目录名不能含连字符 `-`。`model-selection/` 会导致 `ModuleNotFoundError`。必须用下划线：`model_selection/`。这是 Python import 系统硬限制。\n\n**Scheme + Python 数学生态 = Maxima 级 CAS**。Scheme 提供语法糖和宏（DSL 能力），Python（sympy/numpy/scipy/mpmath）提供计算引擎。任意 `pip install <pkg>` 后直接可用，无需适配代码。\n\n## demo.md 编写标准（2026-06-26 更新）\n\n每个单例目录的 demo.md 必须"丰满"（傻瓜教材式）：\n\n1. **绝对禁止形参！只许用实参** — 不要写抽象的参数说明（`| a | 数组 | 输入数组 |`）。**参数演示的唯一方式是具体调用示例**，每个参数的实际效果通过带真实值的代码行展示。可以保留参数表（`| 参数 | 默认 | 说明 |`）作为快速参考，但**代码示例必须全部使用具体数值**。\n\n2. **最少 2-3 个调用示例** — 覆盖不同参数场景。每组示例 = 代码行 + `→` 预期输出。输出在代码下一行，缩进对齐。\n\n3. **三节标配** — 每个 demo.md 必须包含以下节：\n   - `## 参数` — 参数表格（`| 参数 | 默认 | 说明 |`）\n   - `\\`\\`\\`scheme` — 2-3 个实参调用示例 + `;` 注释\n   - `## 注意` — 陷阱、边界情况、调参建议\n\n   可选但推荐：`## 何时用`（适用场景）、`## 对比`（同类方法对照表）\n\n4. **不同原语类型的模板**:\n\n   **数学函数** (numpy math): 3-5 个不同输入的调用示例。\n   ```scheme\n   ; 定长序列\n   (np.sin 0)                                            ; → 0.0\n   (np.sin (/ pi 2))                                     ; → 1.0\n   ; 数组输入\n   (np.sin (np.array '(0 (/ pi 2) pi)))                  ; → [0. 1. 0.]\n   ```\n\n   **模型类** (learn/models): 参数表 + 创建/拟合/预测/属性 四步，展示具体参数值。\n   ```scheme\n   ; 创建模型（具体参数）\n   (define model (RandomForestClassifier :n-estimators 200 :max-depth 10 :random-state 42))\n   (model-fit model X y)\n   (model-predict model X-new)\n   (feature-importances model)\n   ```\n   \n   不要写形参 `(define model (ModelClass :param value))` 这种占位——写具体数值。\n\n   **CV 分割器** (model_selection): 加 `## 何时用` 节。\n   ```scheme\n   (define cv (KFold :n-splits 5 :shuffle #t :random-state 42))\n   (cross-val-score model X y :cv cv)\n   ```\n\n   **子类聚合 demo** (models/{subcat}/demo.md): 综述表格 + 选型指南，不重复单个参数。\n\n5. **每行代码带 `;` 注释** — Scheme 代码行必须解释"在做什么"。Python core.py 必须带模块 docstring + register 注释 + getattr 注释 + env.define 注释。\n\n6. **实际应用场景** — 核心函数用真实场景演示（FFT→信号分析, 分类→完整 ML 流程）。\n\n7. **最低行数要求**: 单原语 demo ≥ 20 行，模型类 demo ≥ 20 行，CV 分割器 ≥ 20 行，子类聚合 demo ≥ 10 行。\n\n详见 `references/demo-concrete-pattern.md`。\n\n## 架构

```
┌─────────────────────────────────────────┐
│  Scheme 用户层                          │
│  (integrate f x), (expand expr),        │
│  [arr 5], (-> x f1 f2), (. obj m args)  │
├─────────────────────────────────────────┤
│  核心求值器 (eval/eval_scheme.py)        │
├─────────────────┬───────────────────────┤
│  CAS 子系统      │  Python 桥接层        │
│  (eval/cas/)     │  (eval/py/)          │
│  core/           │  convert/            │
│  ├ algebra       │  closure/            │
│  ├ calculus      │  attr/               │
│  ├ linear        │  runtime/            │
│  ├ special       │  register/           │
│  └ output        │  import_forms/       │
│  info/           │                      │
│  ├ help          │                      │
│  ├ nav           │                      │
│  ├ catalog       │                      │
│  └ ecosystem     │                      │
│  bridge/ / viz/ / parse/ / tensor/      │
│  assume/ / numerical/ / sugar/ / entry/  │
│  engine/ / pattern/                      │
├─────────────────┴───────────────────────┤
│  PyPI 数学生态                          │
│  sympy, numpy, scipy, mpmath,           │
│  pandas, statsmodels, sklearn, cvxpy…   │
│  + pip install 任意包                    │
└─────────────────────────────────────────┘
```

> **注意**: PyPI 包通过通用导入桥接 `(import numpy)` 直接使用，无需 `eval/cas/<pkg>/` 下的预包装器。`eval/cas/` 仅包含内部 CAS 核心模块。详见 `references/cas-restoration-session.md`。

## 模块文件与重构模式

### 核心原则

**代码组织偏好**：多级目录结构，不接受扁平。大文件必须持续拆分直到单一职责。重构必须 0 断裂（shim 模式 → 最后删除所有 shim）。

## 极端粒度拆分模式

当用户要求"拆分到单例级别"时，每个函数/类/原语一个独立子目录：

```
模块/
├── core.py              ← 聚合器 (导入所有单例目录)
├── __init__.py          ← 重新导出聚合器
├── func_1/
│   ├── core.py          ← register_func_1(env) — 注册 1 个原语，必须自导入 Sym/Prim/...！
│   ├── __init__.py      ← 导出 register_func_1
│   └── demo.md          ← 该原语的完整使用文档
├── func_2/ ...
```

**聚合器模板**（parent/core.py）：
```python
from eval.cas.mymod.func_1.core import register_func_1
from eval.cas.mymod.func_2.core import register_func_2

def register_mymod(env):
    register_func_1(env)
    register_func_2(env)
```

**单例 core.py 模板**：
```python
\"\"\"mymod/func_1 — 说明\"\"\"
from core.schemevalue import Sym, Prim, PythonObject  # 必须自导入！
from eval.eval_python_import import wrap_python_value, unwrap_python_value

def register_func_1(env):
    ...  # 注册单一原语
```

**类名→目录名转换**（camel_to_snake）：
```python
import re
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()  # LinearRegression→linear_regression, SVC→svc
```

## demo.md 编写标准（2026-06-22 更新）

每个单例目录的 demo.md 必须"丰满"（傻瓜教材式）：

1. **用实参演示，不用形参** — 不要写抽象的参数表（`| a | 数组 | 输入数组 |`），直接写带真实值的调用示例。
2. **多组代码示例** — 每组示例 = 输入 + 预期输出。输出在代码下一行，缩进 + `→` 前缀。每个参数的实际用法通过具体实例展示。
3. **注意事项** — 边界情况、常见陷阱、类型限制
4. **适用场景** — 什么时候用这个函数/类
5. **同类对比** — 与其他方法的差异对照表
6. **最佳实践** — 推荐参数设置和使用模式
7. **代码注释** — 每行 Scheme 代码带 `;` 注释。Python core.py 必须带模块 docstring + register 注释 + getattr 注释 + env.define 注释。
8. **实际应用场景** — 核心函数用真实场景演示（FFT→信号分析, 图像滤波→频域处理, 分类→完整 ML 流程）。

**输出格式**：
```scheme
; FFT 频谱分析
(np.random.seed 42)                          ; 固定随机种子
(define sig (* 0.7 (np.sin (* 2 pi 50 t)))) ; 50Hz 正弦信号
(np.fft sig)                                 ; FFT → 频域复数
```

**绝对禁止**：把示例放在 Python docstring 中 — 编辑意外破坏语法结构。始终坚持 `demo.md` 独立文件模式。

**core.py 注释模式**：
```python
# 注册 np.fft 原语
def register_fft(env):
    """注册 np.fft 到 Scheme 环境。"""
    fn = getattr(_np, "fft", None)           # 从 NumPy 获取 fft 函数
    if fn is None:
        return
    env.define(Sym("np.fft"), Prim("np.fft", # 注册为 Prim 原语
        lambda args: wrap_python_value(fn(*[unwrap_python_value(a) for a in args]))))
```

**目录名称规则**：禁止中文作为目录或文件名。所有包名、文件名为英文 kebab-case 或 ASCII。

**子模块导入独立性**：每个子模块的 `core.py` 是独立加载的（通过 `subpkg/__init__.py` 暴露），不是通过父模块的 import 传递的。因此每个 `subpkg/core.py` 必须**自己导入**它需要的所有符号（`Sym`, `Prim`, `wrap_python_value`, `unwrap_python_value`, `PythonObject`, `call_metrics` 等）。绝不能依赖调用方（`__init__.py` 或父级 `core.py`）的 import 传递作用域。详见 `references/learn-module-pattern.md`。

**目录名称规则**：Python 包目录名不能含连字符 `-`。`model-selection/` 会导致 `ModuleNotFoundError`。必须用下划线：`model_selection/`。这是 Python import 系统硬限制。

**重构周期**：(1) 大文件→目录 (2) `core.py`+`__init__.py` (short reexport) (3) 原文件保留为 shim。验证交叉引用的内部符号（`get_engine`、`_declare_indices`）必须在 `__init__.py` 中显式导出。

#### 聚合器分包模式（core.py + aggregator.py）

当将单体 `core.py` 拆分为独立原语子目录时，**不把原文件替换掉**，而是保留原 `core.py`（包含所有函数具体实现），新建 `aggregator.py` 作为注册入口：

```
模块/
├── core.py              ← 原文件保留！包含全部函数实现
├── aggregator.py        ← 新建：从各单例目录 import 注册函数
├── __init__.py
├── func1/               ← 新增单例目录
│   ├── core.py          ← 代理到 from ..core import cas_func1 as _impl
│   ├── __init__.py
│   └── demo.md
└── func2/ ...
```

**单例代理 core.py 模板**：
```python
\"\"\"core/subdir/func — 说明\"\"\"
from typing import List
from core.schemevalue import SchemeValue, Prim
from eval.cas.core.subdir.core import cas_func as _impl
def _run(args: List[SchemeValue]) -> SchemeValue:
    return _impl(args)
def register(env):
    \"\"\"注册 func 到 Scheme 环境。\"\"\"
    env.define("func", Prim("func", _run))
```

**聚合器 aggregator.py 模板**：
```python
\"\"\"subdir - 原语聚合\"\"\"
from .func1.core import register as register_func1
from .func2.core import register as register_func2
def register_subdir(env):
    register_func1(env)
    register_func2(env)
```

**父级 __init__.py 必须从 aggregator.py 导入**：
```python
from eval.cas.core.subdir.aggregator import register_subdir as _reg
```

**为什么保留原 core.py**：其他模块的 `from .core import cas_func` 导入不会被破坏，且函数实现在原位可追溯。

这个模式在 2026-06-23 会话中用于 `eval/cas/core/` 5 子模块（algebra/calculus/linear/special/output），将 88 个原语从 5 个聚合文件成功拆分为 88 个单例目录 + 5 个 aggregator.py，导入链 0 断裂。

详见 `references/aggregator-proxy-pattern.md`。

## 重构技巧 — 安全拆分大文件

**Shim 模式**（适用于被 10+ 处 import 引用的文件）：
1. 提取功能到新文件（如 `eval/py/convert.py`）
2. 原文件变成纯重导出 shim：`from eval.py.convert import wrap_python_value, unwrap_python_value`
3. 在 `__init__.py` 中定义 `__all__` 白名单，确保 `_sym_name` 等私有名称也被 `import *` 导出
4. 0 处既有 import 断裂，新代码可直接导入子模块

**Continue 哨兵模式**（从蹦床循环中提取函数）：
```python
class _Continue:
    __slots__ = ('expr',)
    def __init__(self, expr): self.expr = expr

def eval_and(cdr, env):
    ...
    return _Continue(curr.car)

result = eval_and(cons.cdr, env)
if is_cont(result):
    exp = result.expr
    continue
return result
```

**延迟导入解决循环依赖**（提取文件需回调求值器时）：
```python
# ✅ 函数体内（仅在调用时才导入）
def eval_try(cdr, env):
    from eval.eval_scheme import eval_scheme
    return eval_scheme(body_form, env)
```

**File-to-directory 迁移**（扁平→子目录）：
1. 创建目标子目录和 `__init__.py`
2. 复制文件到新位置，同时更新内部 cross-ref import 路径
3. 验证新位置可独立 import
4. 原位置文件改成 shim（`from eval.py import *`）
5. 删除旧文件
6. 验证全系统

**Model-to-directory 迁移**（每模型一个子目录）：详见 `references/learn-module-pattern.md`。
1. 对每个模型类名，用 `camel_to_snake()` 生成目录名（LinearRegression → linear_regression, SVC → svc）
2. 每个目录创建 `core.py`（注册 1 个类）、`__init__.py`、`demo.md`
3. 父级聚合器从所有单模型子目录 import 并依次调用 register 函数
4. 验证：`python3 -c "from eval.cas.learn.models.linear_model.linear_regression.core import register_linear_regression"`
5. 本工程中一次创建 118 个模型子目录，每个含独立 demo.md

**Per-model demo.md 模板**：详见 `references/learn-module-pattern.md`。

**大型库自动生成模式（vision/scipy/statsmodels 方案）**：当需要包装 OpenCV/SciPy/Statsmodels 等有 50+ 函数的大型库时，不要手写每个原语目录——用一个 generator 脚本从数据元组自动生成全部 core.py + demo.md + __init__.py + category 聚合器。详见 `references/vision-autogen-pattern.md`、`references/library-autogen-pattern.md` 和 `references/mass-generation-pattern.md`。

**模块精细化分级（2026-06-23 新增）**：用户对"模块分级很不细致"的反馈表明，一旦发现大平摊类别（单分类 > 30 原语、所有原语在根级、分类名太泛）就必须拆分为子分类。详见 `references/module-refinement-pattern.md`。

具体操作步骤：
1. 建立原语→子分类映射表（按功能聚类）
2. 用 `shutil.move()` 移动原语目录到子分类下
3. 重新生成聚合器 `core.py`——用 `os.walk` + `re.search` 扫描实际 register 函数名，不能用固定命名假设
4. 修复 `__init__.py` 链：每层必须 `from .core import register_xxx`
5. 清理被移动原语的过时 `__init__.py`
6. 递归验证：`python3 -c "from eval.cas.{mod} import register_{mod}_primitives"`

至少迭代 3 轮：第 1 轮拆大平摊，第 2 轮拆新建模块，第 3 轮修复导入链。见 `references/module-refinement-pattern.md` 的「三周期精炼法」。

**Statsmodels/类API模型特殊处理**：不同于 numpy/scipy 的函数式 API，statsmodels 模型（OLS/Logit/ARIMA）是类，构造函数参数顺序不同于 sklearn 的 `.fit(X, y)` 约定。例如 `sm.OLS(y, X)` 的 `y` 在前、`X` 在后。demo.md 必须展示完整工作流：`model → .fit() → results.summary() → params/rsquared/predict`。用 `py-call`/`py-get` 访问结果属性。

**Matplotlib pyplot 子模块处理**：matplotlib 的绘图函数位于 `matplotlib.pyplot`，不直接在顶层模块。生成 core.py 时必须 `import matplotlib.pyplot as _plt` + `getattr(_plt, "plot")` 而非 `import matplotlib as _mod` + `getattr(_mod, "plot")`。否则 `plot`/`scatter`/`hist` 等全部不可用。

**PyPI 包**：通过通用导入桥接直接使用。`eval/cas/` 下没有 PyPI 桥接包装器。详见 `references/cas-restoration-session.md`。

## `register_primitives` vs `register_xxx_primitives` 约定

内部 CAS 模块有两种注册函数导出的兼容模式：

### 包模块（有 `__init__.py` + `core.py`）
`__init__.py` 必须同时导出 `register_xxx_primitives`（供 `primitives.py` 命名导入）和 `register_primitives`（供聚合器别名导入）：

```python
"""tensor"""
from .core import register_tensor_primitives
from .core import register_primitives
```

### 扁平文件（无子目录）
直接导出 `register_primitives` 和命名函数：

```python
def register_engine_primitives(env):
    ...
register_primitives = register_engine_primitives
```

`primitives.py` 对包模块用 `from eval.cas.tensor import register_tensor_primitives`，对扁平文件用 `from eval.cas.engine import register_primitives as register_engine_primitives`。
- `eval/cas/` 全部 12 个扁平文件 → 目录（engine, entry, parse, pattern, tensor, assume, sugar + info/{help, nav, catalog, ecosystem}）
- `eval/cas/info/*.py` → `info/*/` 子目录
- `eval/cas/numpy.py` → `numpy/` 包（11 子目录, ~322 原语, 对齐 NumPy 源码结构: create/manipulate/math + fft/linalg/polynomial/random/io/strings/testing/transform/distutils）
- `eval/cas/learn/numerical/bridge/viz` 已目录化的进一步重构
- `eval/cas/` 全部 22 个扁平 shim 文件已于 2026-06-22 会话中删除，所有 import 路径直接指向 `subpkg/core.py`
- `eval/cas/learn/` 从 5 模块 (16 原语) 扩展为 8 模块 (118 模型 + 57 指标 + 19 预处理类 + 10 预处理函数 + CV/搜索 + Pipeline + 分析)。每个子目录含 `core.py` + `__init__.py` + `demo.md`。模块间依赖关系完整独立：每个 subpackage 的 `core.py` 单独导入所有需要的 `Sym`/`Prim`/`wrap_python_value`/`unwrap_python_value` 等，绝不依赖调用方作用域传递。
- `eval/cas/core/` 5 子模块 (calculus/algebra/linear/special/output) 从 `.py` 文件转为子目录，各含 `core.py` + `__init__.py` + `demo.md`，并在 math/core.py 中修复了 145 个函数中 ~80 个被 docstring 截断破坏的函数定义
- 拆分陷阱验证命令: `python3 -c "from eval.cas.learn.XXXX.core import register_XXXX"` — 若失败则缺少顶层符号导入
- `eval/cas/core/` 5 子模块已从 `.py` 文件转为子目录（calculus, algebra, linear, special, output），各含 `core.py` + `__init__.py` + `demo.md`

**注册函数对齐陷阱**：拆分 `core.py` 时，函数定义按自然段分裂到新文件，但注册函数中的 `(name, func)` 对必须与定义位置一一对应。
- `cas_roots`/`cas_nroots` 卡在 `linear.py`（因位于线性代数和微分方程段之间）但注册在 `special.py` → 运行时 NameError
- 修复方案：将函数定义移动到注册所属的文件，或调整注册块的分配
- 验证方式：`grep "^def cas_"` 在每个 split 文件中确认 + `grep` 在对应注册列表中确认关联

**文档注释含示例模式（⚠️ 已迁移为 demo.md 模式）**：最初每个 core.py 头部包含按类别分组、带 Scheme 调用示例的文档注释。但 2026-06-22 会话中因 docstring 替换脚本 bug 导致多处 core.py 被截断破坏，修复耗时巨大。**结论：用例示例不应该放在 Python 代码的 docstring 中** — 任何 docstring 编辑都可能意外破坏 Python 语法结构（unterminated string literal、indentation error）。

```
对应: numpy.xxx (子包名)
原语: N

  [类别1]
    (np.func1 args)     →  说明
    (np.func2 args)     →  说明
```

**__all__ 白名单模式**：from package import * 默认不导出以下划线开头的名称。在 __init__.py 中定义 __all__ 以显式包含。

**定义但未注册函数陷阱**：8 个 numpy core.py 中定义了大量 `pnp_xxx` 函数但部分未在 `register_*` 中添加。系统级扫描修复方案：
1. 扫描所有 `def pnp_xxx` 函数名
2. 扫描所有 `("np.xxx", pnp_xxx)` 注册项
3. 计算差值 → 自动生成缺失的注册条目
4. 通过 `pnp_to_np_name()` 映射表确保命名一致性
5. 总计修复 124 个（170→301 原语）

**`_sym_name` 丢失陷阱**：`_sym_name` 定义在 `eval_python_import.py` 的第一段（imports 之后、第一个注释段标记之前），自动按段拆分时被遗漏。所有依赖 `_sym_name` 的文件必须显式 import `from eval.eval_py_attr import _sym_name`（原始定义已移至 `eval/py/attr.py`）。

**内部符号导出陷阱**：将 `.py` 转为 `name/` 目录后，`__init__.py` 必须导出内部交叉引用符号（`get_engine`, `engine_call`, `_declare_indices`, `_eval_match`, `_define_rule`, `_apply_rules`, `cas_help`, `cas_catalog`, `cas_nav`），否则 `from eval.cas.engine import get_engine` 等已有导入会断裂。
- 修复方法：在 `__init__.py` 中 `from eval.cas.engine.core import register_engine_primitives, get_engine, engine_call`
- 全部 `__init__.py` 都必须同时导出 register 函数 + 内部符号 + `__all__`

**`__init__.py` 的内部符号导出清单**（所有 `name/__init__.py` 必须包含）：

| 文件 | 用途 |
|------|------|
| `eval/eval_python_import.py` | **shim** → `eval/py/__init__.py` (原 486 行 → shim + 6 文件) |
| `eval/cas/core.py` | CAS 原语 60+ (integrate/diff/solve/matrix/...) |
| `eval/eval_py_arithmetic.py` | 算术/比较代理调度 |
| `eval/eval_scheme.py` | 核心求值器 (345行) — 22 个特殊形式分派到 6 个提取文件 + 3 个内置特殊形式 + 宏展开/应用回退 |
| `eval/eval_special_forms.py` | quote/if/define/lambda/begin/set! (~80行, 从 eval_scheme.py 提取) |
| `eval/eval_short_circuit.py` | and/or 短路逻辑 (~50行) |
| `eval/eval_import_forms.py` | import/define-library/py-import/py-from/from (~40行) |
| `eval/eval_bracket.py` | `[obj key ...]` 切片/索引 (~140行, 从 eval_scheme.py 提取) |
| `eval/eval_try.py` | `(try body handler)` 异常捕获 (~15行, 从 eval_scheme.py 提取) |
| `eval/eval_macro_forms.py` | define-syntax/macro/case-lambda/syntax/quasisyntax/with-syntax (~110行) |
| `eval/eval_cas_dispatch.py` | match/defrule/rewrite → cas.pattern; tensor → cas.tensor (~130行) |
| `eval/eval_python_import.py` | **shim** → `eval/py/__init__.py` (原 486 行 → 37 行 shim + 6 文件) |
| `eval/eval_py_arithmetic.py` | **shim** → `eval/py/arithmetic.py` (算术代理调度) |
| `eval/eval_scheme.py` | 核心求值器 (345行) — 22 个特殊形式分派到 6 个提取文件 + 3 个内置特殊形式 + 宏展开/应用回退 |
| `core/schemevalue.py` | PythonObject 类型定义 + scheme_format 分支 |
| `core/tail_call.py` | PythonObject callable + 关键词参数分离 |
| `primitives/primitives.py` | 注册入口 + defsym/with-symbols 宏 |
| `primitives/primitives_arith.py` | 算术原语 + Python 检测代理 |
| `primitives/primitives_eq.py` | 比较原语 + Python 检测代理 + `eqn` primitive |
| `eval/cas/viz.py` | 可视化后端 — matplotlib **17 种图表类型** + 图管理 + 标注 |
| `eval/cas/help.py` | 帮助系统 — 82 CAS 函数结构化文档数据库 |
| `eval/cas/engine.py` | 引擎管理器 — symengine/sympy 统一抽象 + 惰性导入 + 智能调度 |
| `eval/cas/assume.py` | 假设系统 — assume/refine/ask/unassume/assuming |
| `eval/cas/numerical.py` | 数值方法 — find-root/numerical-integrate/numerical-derivative |
| `eval/cas/bridge.py` | 桥接模块 — use-graph/use-units/use-tensor |
| `eval/cas/numpy.py` | NumPy 增强 — `(use-numpy)` (np 别名 + 40+ 快捷函数 + 自然切片 `:`) |
| `eval/cas/learn/` | scikit-learn 增强 — `(use-learn)` (118 模型 + 57 指标 + 预处理 + CV/GridSearch + Pipeline + 分析) |
| `eval/cas/ecosystem.py` | 生态展示 — ecosystem (19 包分类浏览) |
| `eval/cas/catalog.py` | 科学计算包目录 — `(catalog)` 层级浏览 **29 包 × 9 领域** (含 curated 数据库 ~200 条) |
| `eval/cas/nav.py` | 分级导航 — `(nav)` 三级浏览 7 领域 × 185+ 函数 |
| `eval/cas/pattern.py` | 模式匹配 — `(match)`/`(defrule)`/`(rewrite)`/`(rules)` |
| `eval/cas/tensor.py` | 张量代数 — `(index)`/`(tensor)`/`(contract)`/`(raise-index)`/`(lower-index)` |
| `eval/cas/parse.py` | 数学解析器 — `(parse)`/`(parse-latex)`/`(parse-mathml)`/`(parse-mathematica)` → sympy |
| `eval/cas/entry.py` | CAS 入口 — `(use-cas)` + `?`/`??`/`apropos`/`list-all` |
| `eval/cas/sugar.py` | 语法糖宏: λ/->/->>/for/str + ∞ 绑定 |
| `tests/cas_demo.scm` | 综合功能演示（12 章） | 批处理运行 |
| `eval/cas/sugar.py` | 语法糖: λ / `->` / `->>` / `for` / `str` 宏 |
| `eval/cas/numerical.py` | 数值方法 — find-root/numerical-integrate/numerical-derivative |
## 导入系统

```scheme
(import numpy)                              → import numpy
(import numpy as np)                        → import numpy as np
(import numpy scipy sympy)                  → import numpy, scipy, sympy
(import scipy.optimize scipy.stats)         → 自动绑定父包 scipy
(import statsmodels.api as sm)              → import statsmodels.api as sm
(from numpy import array zeros)             → from numpy import array, zeros
(from numpy import * )                      → from numpy import *
(import os.path)                            → import os.path (+ 自动绑定 os)
```

### 设计细节

- **父包自动导入**: 导入 `scipy.optimize` 时自动 `import scipy` 并绑定 `scipy`
- **子模块自动导入**: `sympy.abc.x` 在级联解析中自动 `importlib.import_module("sympy.abc")`
- **裸导入检测**: `(import numpy)` — 当 cdr 首项是 Sym 时走 Python 路径，否则走 R7RS

## 级联属性/方法调用（`.` 自动解析）

裸符号含 `.` 自动走 Python 属性链（`eval_scheme` 的 `Sym` case fallback）：

```scheme
math.pi                                 → math.pi
(math.sqrt 16)                          → math.sqrt(16)
(os.path.join "/a" "b")                 → os.path.join("/a", "/b")
(arr.T)                                 → arr.T
(arr.reshape 3 4)                       → arr.reshape(3, 4)
(numpy.random.normal 0 1 '(5 5))        → numpy.random.normal(0, 1, (5,5))
(np.linalg.solve A b)                   → numpy.linalg.solve(A, b)
(networkx.shortest_path G 'A 'D)        → nx.shortest_path(G, 'A', 'D')
```

### 实现

```python
# eval/eval_scheme.py: 裸符号求值 fallback
case Sym() as sym:
    if sym.name.startswith(":"):
        return sym  # keyword literal
    try: return env.lookup(sym)
    except Exception:
        if "." in sym.name:
            result = resolve_python_attr_chain(sym.name, env)
            if result is not None: return result
        raise
```

## 关键词参数

Scheme 的 `:xxx` 符号自求值，`apply_tail` 自动分离位置参数和关键词参数：

```scheme
(np.array '#(1 2 3) :dtype np.float64)      → np.array([1,2,3], dtype=np.float64)
(np.mean arr :axis 0)                         → np.mean(arr, axis=0)
(pandas.Series '#(10 20) :name 'scores)      → pd.Series([10,20], name='scores')
(scipy.optimize.minimize f x0 :method 'Nelder-Mead)
(py-eval "arr[2:8:2]" :arr arr)              → eval with locals
```

### 实现

```python
# core/tail_call.py: PythonObject 可调用 case
case PythonObject(obj=py_obj) if callable(py_obj):
    py_args = []
    py_kwargs = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if isinstance(arg, Sym) and arg.name.startswith(":"):
            kw_name = arg.name[1:]
            py_kwargs[kw_name] = unwrap_python_value(args[i + 1])
            i += 2
        else:
            py_args.append(unwrap_python_value(arg))
            i += 1
    result = py_obj(*py_args, **py_kwargs)
    return wrap_python_value(result)
```

## 方括号索引/切片

`[obj key ...]` 被 parser 解析为 `(bracket obj key ...)`：

```scheme
[a 5]                                → a[5]               # 单索引
[a 1 : 3]                            → a[1:3]             # 切片 (: 分隔)
[a 1 : 7 : 2]                        → a[1:7:2]           # 步长切片
[a : 5]                              → a[:5]              # 开头到 5
[a 5 :]                              → a[5:]              # 5 到结尾
[a :]                                → a[:]               # 全部
[m 0 : 2 1 : 3]                      → m[0:2, 1:3]        # 2D 切片
[m 0 1 : 3]                          → m[0, 1:3]          # 混合标量+切片
[m (list 1 3)]                       → m[1:3]             # 列表式切片
[m 2 8 2]                            → m[2:8:2]           # 三元组切片
[m2 1 2]                             → m2[1, 2]           # 多维索引
```

### 实现

parser 中 `[` → `(bracket ...)`。eval 中 `case Sym("bracket")` 特殊形式处理。支持 `:` 作为切片分隔符：`Sym(":")` 在 eval 中因 `name.startswith(":")` 自动返回自身，bracket 内检测 `Sym(":")` 的出现，将前后值配为 `slice(start, stop, step)`。多个维度按原始书写顺序排列。

**设计关键：**
- `:` 在 Scheme 中是无害的自求值符号（`Sym(":")` → `:name` pattern）
- `has_colon = any(isinstance(a, Sym) and a.name == ':' for a in indices)`
- 用 `py_entries = {}` 字典 + `dim_pos` 记录每个维度在原始参数中的位置
- 最后通过 `sorted(py_entries.items())` 恢复正确维度顺序
- 无 `:` 时保留原有 2/4/3+ 参数逻辑（向后兼容）

**陷阱：顺序恢复** — 先收集 `:` 配对的 slice，再收集剩余标量时，必须用 `(position, value)` 对并按位置排序，否则 `[m 0 1 : 3]` 会错误地变成 `m[1:3, 0]` 而非 `m[0, 1:3]`。

## `.` 特殊形式（避免点对语法冲突）

当 `((obj).method ...)` 被 Scheme reader 误读为点对语法时：

```scheme
(. (np.arange 12) reshape 3 4)          → np.arange(12).reshape(3,4)
(. (np.zeros '(100 100 3)) fill 255)    → np.zeros((100,100,3)).fill(255)
(. (np.arange 1000) reshape 100 10)     → np.arange(1000).reshape(100, 10)
```

## 数学表达式解析（本轮新增）

4 种解析器将外部格式转换为 CAS 表达式，与现有 diff/integrate/solve 等无缝集成。详见 `references/math-parsers.md`。

| 命令 | 输入格式 | 示例 |
|------|---------|------|
| `(parse str)` | Python/sympy | `(parse "x**2 + 1")` → x²+1 |
| `(parse-latex str)` | LaTeX | `(parse-latex "x^2 + 1")` → x²+1 |
| `(parse-mathml str)` | MathML XML | `(parse-mathml "<math>...</math>")` → x²+1 |
| `(parse-mathematica str)` | Mathematica | `(parse-mathematica "x^2 + 2*x + 1")` → x²+2x+1 |

双向流程：`LaTeX/MathML → parse → CAS (diff/integrate/…) → latex → LaTeX`

## 中缀语法增强（本轮新增）

在 `#{...}` 中支持更多自然数学表达。详见 `references/infix-parser.md`。

| 表达 | `#{...}` 写法 | 展开 |
|------|-------------|------|
| 绝对值 | `#{ \|x\| }` | `(abs x)` → `Abs(x)` |
| | `#{ \|x-1\| }` | `(abs (- x 1))` → `Abs(x-1)` |
| 阶乘 | `#{5!}` | `(factorial 5)` → `120` |
| 范围 | `#{1..10}` | `(range 1 10)` |
| 下标 | `x_y` / `a_{n+1}` | `(ref x y)` / `(ref a (+ n 1))` |
| 矩阵 | `#{ [1 2; 3 4] }` | `(matrix (list 1 2) (list 3 4))` |

通过 `define-macro` 在 `primitives.py` 启动时注册（`eval/eval_py_sugar.py`），编译期展开：

| 宏 | 展开 | 示例 |
|----|------|------|
| `λ` | `lambda` | `(λ (x) (* x 2))` → `(lambda (x) (* x 2))` |
| `->` | thread-first | `(-> 5 (* 2) (+ 1))` → `(+ (* 5 2) 1)` → **11** |
| `->>` | thread-last | `(->> (list 3 1 4) reverse)` → `(reverse (list 3 1 4))` |
| `for` | list comprehension | `(for (x xs) (* x x))` → `(map (λ (x) (* x x)) xs)` |
| `str` | string interpolation | `(str "x = " 42)` → `"x = 42"` |

### 实现模式

注册时直接 `eval_scheme(parse(macro_code), env)` 注入。`->` 和 `->>` 的旧 runtime 实现已从 `eval_scheme.py` 移除（会被宏拦截前短路），改为 compile-time 宏展开。

```scheme
; -> 宏展开逻辑
(define-macro (-> x . forms)
  (if (null? forms) x
    (let ((form (car forms)) (rest (cdr forms)))
      (if (pair? form)
        (let ((result (append (list (car form) x) (cdr form))))
          (if (null? rest) result
            (cons '-> (cons result (cdr forms)))))
        (if (null? rest) (list form x)
          (cons '-> (cons (list form x) (cdr forms))))))))
```

### CAS pipeline 应用

```scheme
(-> #{x^2 + 2*x + 1} (factor x) expand)
;; → x² + 2x + 1

(for (x (range 0 10 2)) (expt x 2))
;; → (0 4 16 36 64)

(map (λ (x) (* x x)) (list 1 2 3))
;; → (1 4 9)


## 算术透明度

Scheme 原生运算符在检测到 PythonObject 操作数时自动代理到 Python：

```scheme
(+ x 1)     → sympy.Add(x, 1)   / numpy.add(x, 1)
(* 2 x)     → sympy.Mul(2, x)   / numpy.multiply(2, x)
(expt x 2)  → sympy.Pow(x, 2)   / numpy.power(x, 2)
(sin x)     → sympy.sin(x)      / numpy.sin(x)
(log x)     → sympy.log(x)      / numpy.log(x)
(> x 0)     → sympy.Gt(x, 0)    / (x > 0)
```

### 代理流程

1. 检测 `_has_py_object(args)` → 任何参数含 PythonObject
2. 全部 Scheme 参数解包为 Python 值
3. 通过 `operator.add`, `operator.mul`, `math.sin` 等执行
4. 若 `math.xxx` 抛 `TypeError`（如对 sympy Symbol 调用 `math.sin`），自动 fallback 到 `sympy.xxx`
5. 结果用 `wrap_python_value` 包装回 Scheme 值

**覆盖**: 二元运算符 `+ - * / expt modulo quotient`；一元函数 `sin cos tan asin acos atan sinh cosh tanh sqrt log exp abs`；比较 `= < > <= >=`。

## Scheme 闭包作 Python 回调

`Closure` 自动包装为 `SchemeClosureWrapper`（Python callable），含 `__code__`/`__signature__` 内省支持：

```scheme
(scipy.optimize.minimize (lambda (x) (expt x 2)) 0)
(scipy.integrate.quad (lambda (x) (exp (- (expt x 2)))) 0 np.inf)
(scipy.optimize.curve_fit (lambda (x a b) (+ (* a x) b)) xdata ydata)
```

### 实现

```python
class SchemeClosureWrapper:
    def __init__(self, closure, env):
        self.closure = closure
        self.env = env
        self.__code__ = self._make_code()
        self.__signature__ = self._make_signature()

    def __call__(self, *args):
        scheme_args = [wrap_python_value(arg) for arg in args]
        result = invoke_closure(self.closure, scheme_args)
        is_tc, expr, new_env = unwrap_tail(result)
        if is_tc:
            result = eval_scheme(expr, new_env)
        return unwrap_python_value(result)
;; → (1 4 9 16 25)

```

## try 特殊形式（异常捕获）

`(try body handler)` 在 `eval_scheme.py` 中注册为特殊形式（非 Prim 非宏），
捕获包括未绑定变量在内的**全部 Python 级异常**：

```scheme
(try (non-existent) (λ (e) "caught!"))   → "caught!"
(try (/ 1 0) (λ (e) "div/0"))            → "div/0"
```

### 为什么不能是 Prim 或宏

- **Prim**: 参数已求值 → body 中的错误在 Prim 运行前就已抛出
- **MacroClosure**: `invoke_macro_closure` 给参数加额外 `quote` 层，展开中需 `(cadr catcher)` 剥去引用
- **特殊形式**: 直接收到未求值的 body 和 handler，`try/except` 包裹 `eval_scheme(body_form, env)`

### 实现

```python
case Sym("try"):
    match cons.cdr:
        case Cons(body_form, Cons(handler_form, Nil())):
            try:
                return eval_scheme(body_form, env)
            except Exception as exc:
                handler_proc = eval_scheme(handler_form, env)
                return apply_tail(handler_proc, [Str(list(str(exc)))], env)
```

## ∞ 符号（无穷大）

在 `register_sugar_primitives` 中绑定：

```python
env.define(Sym('∞'), wrap_python_value(sympy.oo))
```

典型用例：

```scheme
(integrate #{exp(-x)} x 0 ∞)   → 1
```

## CAS 子系统模块（`eval/cas/`）

**命名约定**：PyPI 包遵循 `env.define` 名称镜像文件路径规则。**内部 CAS 模块不适用此规则**（保持扁平 Scheme 名，见 `references/naming-convention-distinction.md`）。

| 模块 | 注册函数 | 说明 |
|------|---------|------|
| `engine.py` | `register_primitives` | 引擎管理 — use-engine, engine-info |
| `parse.py` | `register_primitives` | 5 格式数学解析器 |
| `bridge.py` | `register_primitives` | 桥接 — Graph/DiGraph/Array/use-graph/use-tensor/use-units |
| `pattern.py` | `register_primitives` | 模式匹配 (存根) |
| `tensor/` | `register_tensor_primitives` | 张量代数 (子代理创建为包) |
| `viz/` | `register_viz_primitives` | 可视化 — plot/plot-param/plot3d |
| `core/` | `register_core_primitives` | 聚合器 |
| `core/algebra.py` | `register_primitives` | 代数 + 三角 + 方程 (26 原语) |
| `core/calculus.py` | `register_primitives` | 微积分 (12 原语) |
| `core/linear.py` | `register_primitives` | 线性代数 (17 原语) |
| `core/special.py` | `register_primitives` | 特殊/数论/集合/统计 (40+ 原语) |
| `core/output.py` | `register_primitives` | 输出格式 (7 原语) |
| `info/` | `register_info_primitives` | 聚合器 |
| `info/help.py` | `register_primitives` | 帮助系统 — help/?/??/apropos |
| `info/nav.py` | `register_primitives` | 导航 — nav |
| `info/catalog/` | `register_catalog_primitives` | 科学计算包目录 |
| `info/ecosystem/` | `register_ecosystem_primitives` | 生态展示 |
| `sugar/` | `register_sugar_primitives` | 语法糖 — λ/->/->>/for/str/∞ |
| `assume/` | `register_assume_primitives` | 假设系统 |
| `numerical/` | `register_numerical_primitives` | 数值方法 |
| `entry/` | `register_entry_primitives` | CAS 入口 — use-cas |
| `viz/` | 可视化 — 17 种图表 | `register_viz_primitives` |

### 核心求值器 (`eval/`, 平级)

| 文件 | 用途 |
|------|------|
| `eval/eval_scheme.py` | 核心求值器 (345行) — 22 case 特殊形式 + 蹦床 |
| `eval/eval_special_forms.py` | quote/if/define/lambda/begin/set! (~80行) |
| `eval/eval_short_circuit.py` | and/or 短路逻辑 (~50行) |
| `eval/eval_import_forms.py` | import/define-library/py-import/py-from/from (~40行) |
| `eval/eval_bracket.py` | [obj key ...] 切片/索引 (~140行) |
| `eval/eval_try.py` | (try body handler) 异常捕获 (~15行) |
| `eval/eval_macro_forms.py` | define-syntax/macro/case-lambda/syntax/quasisyntax/with-syntax (~110行) |
| `eval/eval_cas_dispatch.py` | match/defrule/rewrite → cas.pattern; tensor → cas.tensor (~130行) |
| `eval/eval_python_import.py` | **shim** → `eval/py/__init__.py` (原 486 行 → shim + 6 文件) |
| `eval/eval_let.py` / `eval_cond.py` / `eval_case.py` / ... | 已抽取特殊形式 |

### Python 桥接子目录 (`eval/py/`)

| 文件 | 用途 |
|------|------|
| `eval/py/__init__.py` | 包初始化 + `__all__` 白名单 (确保 `_sym_name` 等被 `import *` 导出) |
| `eval/py/convert.py` | `wrap_python_value` / `unwrap_python_value` — 值转换 |
| `eval/py/closure.py` | `SchemeClosureWrapper` — Scheme closure → Python callable |
| `eval/py/attr.py` | `_sym_name` / 属性链解析 / `py-set!` 工具 |
| `eval/py/import_forms.py` | `(import ...)` / `(py-from ...)` / `(from ... import ...)` |
| `eval/py/runtime.py` | `py-get` / `py-call` / `py-eval` 运行时工具 |
| `eval/py/register.py` | 5 桥接原语 (`unwrap-python`/`wrap-python`/`py-str`/`py-eq`/`py-type`) + register |
| `eval/py/arithmetic.py` | 算术/比较代理调度 (`try_py_binary_op` 等) |

### `__all__` 白名单模式

在 `eval/py/__init__.py` 中定义 `__all__`，确保 `_sym_name` 等下划线前缀名称被 `from eval.py import *` 导出：

```python
__all__ = [
    'wrap_python_value', 'unwrap_python_value',
    'SchemeClosureWrapper',
    '_sym_name', 'resolve_python_attr_chain',
    ...
]
```

\`\`\`
642→397→345行 eval_scheme.py (-45%) + 486→37行 eval_python_import.py shim + 6 文件
\`\`\`

### 数据处理 (`eval/data/`)

| 文件 | 用途 | 注册函数 |
|------|------|---------|
| `eval/data/json.py` | JSON 一等公民 — 18 原语 (parse/dumps/merge/get/set) | `register_json_primitives` |
| `eval/data/csv.py` | CSV 处理 — 7 原语 (read/write/rows/col/headers) | `register_csv_primitives` |
| `eval/data/serialize.py` | 序列化 — 8 原语 (pickle/json/pprint) | `register_serialize_primitives` |

### 文本处理 (`eval/text/`)

| 文件 | 用途 | 注册函数 |
|------|------|---------|
| `eval/text/re.py` | 正则表达式 — 20 原语 (match/search/findall/split/sub) | `register_re_primitives` |

### I/O 操作 (`eval/io/`)

| 文件 | 用途 | 注册函数 |
|------|------|---------|
| `eval/io/path.py` | pathlib 路径操作 — 30+ 原语 | `register_path_primitives` |
| `eval/io/http.py` | HTTP 客户端 — 26 原语 (get/post/put/delete/session) | `register_http_primitives` |
| `eval/io/image.py` | 图像处理 (Pillow) — 40 原语 | `register_image_primitives` |
| `eval/io/compress.py` | 压缩归档 — 16 原语 (gzip/bz2/lzma/zip/tar) | `register_compress_primitives` |
| `eval/io/db.py` | SQLite3 数据库 — 22 原语 | `register_db_primitives` |

### 加密 (`eval/crypto/`)

| 文件 | 用途 | 注册函数 |
|------|------|---------|
| `eval/crypto/crypto.py` | 加密/Hash — 22 原语 (sha256/md5/hmac/base64/uuid) | `register_crypto_primitives` |

### 系统 (`eval/system/`)

| 文件 | 用途 | 注册函数 |
|------|------|---------|
| `eval/system/system.py` | 系统信息 — 30+ 原语 (os/process/env/memory/disk) | `register_system_primitives` |
| `eval/system/datetime.py` | 日期时间 — 28 原语 (now/date/format/arithmetic) | `register_datetime_primitives` |

### REGISTRATION PATTERN

All modules follow the same pattern:
1. Define `register_xxx_primitives(env)` in the module file
2. Import and call it in `primitives/primitives.py`
3. Import path: `from eval.<subdir>.<module> import register_xxx_primitives`
4. Registration order in `register_all()`: CAS modules first, then data/text/io/crypto/system

Pitfall: `eval_py_serialize.py` (now `eval/data/serialize.py`) imports from `eval/data/json.py` — need `from eval.data.json import scheme_to_json, json_to_scheme` (absolute path, not relative).

Pitfall (cross-module import): Files extracted from eval_scheme.py that need to call back into `eval_scheme` (eval_try, eval_bracket_args, eval_special_forms, eval_cas_dispatch, eval_macro_forms) use LAZY imports inside function bodies (`from eval.eval_scheme import eval_scheme`) — this avoids circular import at module load time.

Pitfall (registration consistency): When splitting `core.py` into submodules, function definitions and registration `(name, func)` pairs can drift apart. Fix: scan all `def cas_xxx` in a file, cross-reference against the register function's `(name, cas_xxx)` entries, and add missing ones. Automated in numpy expansion — `pnp_to_np_name()` mapping + programmatic insertion. Verify with `grep "^def cas_"` vs grep in register block.

Pitfall (Cons iteration): Scheme Cons chains don't support Python `len()`/`__getitem__`. Converting a Cons list to Python list must use `while isinstance(val, Cons): items.append(unwrap_python_value(val.car)); val = val.cdr` — never `for i in range(len(cons_val))`.

See `references/cas-restructure-pattern.md` for the directory restructuring approach used in the 2026-06-22 reorganization.

## 模式匹配系统 — `match`/`defrule`/`rewrite`
最终: eval_scheme.py     628 → 345行 (-45%), 7 提取文件
      eval_python_import.py 486 → 37行 shim + 6 文件
```

## 模式匹配系统 — `match`/`defrule`/`rewrite`

所有命令在 `eval_scheme.py` 中注册为**特殊形式**（不是 Prim，不是宏），因为 `?x` 等模式变量必须保持未求值状态。

```scheme
(match (* ?a x) #{3*x})           → ((a 3))        ;; ?a 绑定到 3
(match (expt (sin ?x) 2) #{sin(x)^2}) → ((x x))

(defrule sin-squared (expt (sin ?x) 2) (- 1 (expt (cos ?x) 2)))
(rewrite #{sin(x)^2} sin-squared)  → 1 - cos²(x)

(defrule expand-square (expt (+ ?a ?b) 2) 
    (+ (expt ?a 2) (* 2 ?a ?b) (expt ?b 2)))
(rewrite #{(x+1)^2} expand-square) → x² + 2x + 1

(rules)                            ;; 列出全部
(clear-rules)                      ;; 清除全部
```

**关键实现：**
- `_match_pattern(pat, expr, bindings)` — 递归模式匹配，返回绑定 dict 或 None
- `?x`/`?a`/`?b` 匹配任意子表达式；`?n`/`?m` 仅匹配数字；`_` 通配符；`?x+` 匹配一个或多个
- `_subst(pattern, bindings)` — 将绑定代入替换模板
- `_expr_to_scheme(sympy_expr)` — 将 sympy 表达式递归转为 Scheme Cons 树（`Add`→`+`, `Mul`→`*`, `Pow`→`expt` 等）

## 张量代数 — `index`/`tensor`/`contract`/`raise-index`/`lower-index`

全部在 `eval_scheme.py` 中注册为**特殊形式**，因为 `i`, `j`, `k` 等指标在环境中未绑定（Prim 会抛 Unbound variable）。

```scheme
(index i j k l)                    ;; 声明指标
(define R (tensor "R" (i j k l) ()))  ;; Riemann 张量 R_ijkl
(define Ric (contract R i k))      ;; 缩并 → Ricci 张量
(define RT (raise-index R l))      ;; 升指标
(define RL (lower-index R k))      ;; 降指标
```

## 数学表达式解析器 — 5 种输入格式

**统一** `parse-xxx` API，全部输出 sympy 表达式，可与现有 diff/integrate/solve/plot 无缝集成。

```scheme
;; 1. Python/sympy 风格
(parse "x**2 + 1")                  → x² + 1
(parse "integrate(x**2, (x, 0, 1))") → 1/3

;; 2. LaTeX (需要 antlr4-python3-runtime)
(parse-latex "x^2 + 1")             → x² + 1
(parse-latex "\\int_0^1 x^2 dx")    → 1/3

;; 3. MathML XML
(parse-mathml "<math><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>1</mn></mrow></math>") 
→ x² + 1

;; 4. Mathematica/Wolfram
(parse-mathematica "x^2 + 2*x + 1") → x² + 2x + 1
(parse-mathematica "Sin[x]^2 + Cos[x]^2") → 1

;; 5. Maxima/WxMaxima (本轮新增)
(parse-maxima "diff(x^3, x)")       → 3x²
(parse-maxima "integrate(x^2, x, 0, 1)") → 1/3
(parse-maxima "factor(x^4 - 1)")    → (x-1)(x+1)(x²+1)
(parse-maxima "x^2 - 4 = 0")        → Eq(x²-4, 0)  ;; 方程
(parse-maxima "limit(sin(x)/x, x, 0)") → 1
```

**实现要点：**
- `parse-maxima` 通过 `sympy.parsing.maxima.parse_maxima` 加正则预处理处理定积分、高阶导数、极限和方程
- `parse-mathml` 用 `xml.etree.ElementTree` 原生解析 MathML 元素树（无需 antlr4）
- `parse-latex` 依赖 antlr4-python3-runtime 4.11+
- 统一工作流：`LaTeX/MathML/Maxima → parse → CAS (diff/integrate) → latex → LaTeX`

## 四向往返映射（桥接原语）

str <-> S-expr <-> sympy <-> symengine 四向闭环依赖 5 个桥接原语：
`unwrap-python`, `wrap-python`, `py-str`, `py-eq`, `py-type`。
详见 `references/roundtrip-bridge.md`。

### srepr 闭环

`sympy.srepr()` 输出 Python 表达式字符串，`parse` 函数支持 `eval` 回退：

```scheme
(define e (parse "x + y"))
(define s (py-str (sympy.srepr (unwrap-python e))))
(define e2 (parse s))                    ; eval fallback
(py-eq (unwrap-python e) (unwrap-python e2))  ; #t
```

8/8 测试通过：1+2, x+y, x*y, sin(x), xi2+2x+1, sqrt(x), 1/(x+1), cos2+sin2。

## symengine <-> sympy 双向转换

```scheme
(import symengine)
(define se-e (+ (* 2 (symengine.Symbol 'x)) (expt (symengine.Symbol 'x) 2)))
(define sp-e (sympy.sympify se-e))       ; symengine -> sympy
(define se-back (symengine.sympify sp-e)) ; sympy -> symengine
(py-eq (unwrap-python se-e) (unwrap-python (sympy.sympify se-back)))  ; #t
```

**实现要点：** `eval/eval_python_import.py` 中注册 5 个原语：
```python
env.define("unwrap-python", Prim("unwrap-python", py_unwrap_prim))
env.define("wrap-python", Prim("wrap-python", py_wrap_prim))
env.define("py-str", Prim("py-str", py_str_prim))
env.define("py-eq", Prim("py-eq", py_eq_prim))
env.define("py-type", Prim("py-type", py_type_prim))
```

## parse 的 srepr 回退实现

`_py_parse` 失败后自动 fallback 到安全 `eval`（在 `eval/cas/parse.py` 中）：

```python
SAFE_DICT = {'Symbol': sp.Symbol, 'Integer': sp.Integer, 'Float': sp.Float,
             'Rational': sp.Rational, 'Mul': sp.Mul, 'Add': sp.Add,
             'Pow': sp.Pow, 'sin': sp.sin, 'cos': sp.cos,
             'sqrt': sp.sqrt, 'exp': sp.exp, 'log': sp.log,
             'pi': sp.pi, 'E': sp.E, 'oo': sp.oo}
eval(expr_str, {"__builtins__": {}}, SAFE_DICT)
```

**陷阱：** `sympy.srepr()` 输出格式是 `Add(Symbol('x'), Integer(2))`，无法被 `parse_expr` 解析，必须走 `eval` 回退。

## `set!` 修改 Python 属性
(set! model.alpha 0.5)                   → model.alpha = 0.5
```

### 实现

`eval_scheme` 的 `case Sym("set!")` 中检测符号名含 `.` → 通过 `resolve_python_attr_chain_parent` 获取父对象 → `setattr(parent.obj, attr_name, py_val)`。

## 运行时工具原语

| 原语 | 等价 Python | 示例 |
|------|------------|------|
| `(py-get obj 'attr)` | `getattr(obj, "attr")` | 属性/字典/数字索引 |
| `(py-get obj 0)` | `obj[0]` | 整数索引 |
| `(py-get obj slice_obj)` | `obj[slice_obj]` | PythonObject 索引 |
| `(py-call fn arg1 arg2)` | `fn(arg1, arg2)` | 显式调用 |
| `(py-eval "expr" :var val)` | `eval("expr", locals={"var": val})` | 变量注入的 eval |
| `(py-exec "code")` | `exec("code")` | 多语句执行 |
| `(py-str obj)` | `str(obj)` | 字符串化 |
| `(py-repr obj)` | `repr(obj)` | 精准表示 |
| `(py-len obj)` | `len(obj)` | 长度 |
| `(py-dict :k1 v1 :k2 v2)` | `{"k1": v1, "k2": v2}` | 字典创建 |
| `(py-slice start stop step)` | `slice(start, stop, step)` | 切片对象 |
| `(py-set! obj key val)` | `obj[key] = val` 或 `setattr(obj, key, val)` | 赋值 |
| `(py-for-each proc iter)` | `for item in iter: proc(item)` | 迭代遍历 |

## 数据双方向自动转换

### Python → Scheme

| Python | Scheme |
|--------|--------|
| `None` | `Nil()` |
| `bool` | `Bool` |
| `int` | `Integer` |
| `float` | `Num` |
| `complex` | `Complex` |
| `str` | `Str` |
| `list`/`tuple` | **`Vector`**（连续内存，适合数值计算） |
| `set` | **`Vector`**（有序化） |
| `dict` | `PythonObject`（SchemeValue 不可哈希） |
| `bytes` | `Bytevector` |
| 其他 | `PythonObject` |
| `Closure` (Scheme) | **`SchemeClosureWrapper`**（自动包装为 Python callable） |

### Scheme → Python

| Scheme | Python |
|--------|--------|
| `Integer` | `int` |
| `Num` | `float` |
| `Str` | `str` |
| `Bool` | `bool` |
| `Sym` | `str`（符号名） |
| `Vector` | `list` |
| `eval/cas/engine.py` | 引擎管理器 — symengine/sympy 统一抽象 + 惰性导入 + 智能调度 |
| `eval/eval_python_import.py` | 导入桥 + 值转换 + 链解析 + 5 个桥接原语 (unwrap/wrap-py/str/eq/type) |
| `eval/eval_scheme.py` | 特殊形式 + 模式匹配/张量注册 + 点链解析 |
| `eval/cas/pattern.py` | 代数模式匹配 — `match`/`defrule`/`rewrite` → sympy 树重写 |
| `eval/cas/tensor.py` | 张量代数 — `index`/`tensor`/`contract`/`raise-index`/`lower-index` |
| `eval/cas/parse.py` | 数学表达式解析 — `parse`/`parse-latex`/`parse-mathml`/`parse-mathematica`/`parse-maxima` |
| `eval/cas/entry.py` | CAS 一键入口 — `(use-cas)` + `?`/`??`/`apropos`/`list-all` |
| `eval/data/json.py` | JSON 一等公民 — 18 原语 (parse/dumps/merge/get/set) |
| `eval/text/re.py` | 正则表达式 — 20 原语 (match/search/findall/split/sub) |
| `eval/io/path.py` | pathlib 路径操作 — 30+ 原语 |
| `eval/io/http.py` | HTTP 客户端 — 26 原语 (get/post/put/delete/session) |
| `eval/system/datetime.py` | 日期时间 — 28 原语 |
| `eval/system/system.py` | 系统信息 — 30+ 原语 (os/process/env/memory/disk) |
| `eval/crypto/crypto.py` | 加密/Hash — 22 原语 |
| `eval/data/csv.py` | CSV 处理 — 7 原语 |
| `eval/io/compress.py` | 压缩归档 — 16 原语 (gzip/bz2/lzma/zip/tar) |
| `eval/data/serialize.py` | 序列化 — 8 原语 (pickle/json/pprint) |
| `eval/io/db.py` | SQLite3 数据库 — 22 原语 |
| `eval/io/image.py` | 图像处理 (Pillow) — 40 原语 |
| `eval/cas/bridge.py` | 桥接模块 — use-graph/use-units/use-tensor |

# CAS 函数 API（60+，延迟绑定 sympy）

所有原语在 `eval/cas/core.py` 中定义，通过 `register_cas_primitives(env)` 注册。采用**延迟绑定**策略——Prim 内部在首次调用时 `import sympy`。

### 注册模板

```python
def _sympy():
    try:
        import sympy; return sympy
    except ImportError:
        raise Exception("CAS 需要 sympy。请先执行 (import sympy)")

def _unwrap(args):
    return [unwrap_python_value(a) for a in args]

def cas_integrate(args):
    sp = _sympy()
    f, x = _unwrap(args[:2])
    if len(args) == 2:
        return wrap_python_value(sp.integrate(f, x))
    if len(args) == 4:
        a, b = _unwrap(args[2:4])
        return wrap_python_value(sp.integrate(f, (x, a, b)))
    raise Exception("integrate: 需要 2(不定)或 4(定积分)参数")
```

### 微积分
| Scheme | 功能 |
|--------|------|
| `(integrate f x)` | 不定积分 |
| `(integrate f x a b)` | 定积分 ∫ₐᵇ f dx |
| `(diff f x)` | 一阶导数 |
| `(diff f x n)` | n 阶导数 |
| `(limit f x pt)` | 极限 |
| `(limit f x pt dir)` | 单侧极限 |
| `(series f x pt n)` | 泰勒展开到 n 阶 |
| `(taylor f x pt n)` | 泰勒展开别名 |
| `(summation expr (var lo hi))` | 求和 Σ |
| `(product expr (var lo hi))` | 求积 Π |

### 向量微积分
| Scheme | 功能 |
|--------|------|
| `(grad f x y ...)` | 梯度向量 ∇f |
| `(div F x y ...)` | 散度 ∇·F |
| `(curl F x y z)` | 旋度 ∇×F (3D) |
| `(hessian f x y ...)` | 海森矩阵 H(f) |
| `(jacobian F x y ...)` | 雅可比矩阵 J(F) |

### 代数
| Scheme | 功能 |
|--------|------|
| `(expand expr)` | 展开 |
| `(factor expr)` | 因式分解 |
| `(simplify expr)` | 化简 |
| `(apart expr var)` | 部分分式分解 |
| `(together expr)` | 通分合并 |
| `(collect expr var)` | 按变量合并同类项 |
| `(coeff expr var n)` | 提取 xⁿ 系数 |
| `(normal expr)` | 有理式化简 |
| `(resultant p1 p2 var)` | 结式 Res(p₁,p₂) |
| `(discriminant p var)` | 判别式 Δ(p) |
| `(compose f g x)` | 函数复合 f(g(x)) |
| `(num expr)` | 取分子 |
| `(denom expr)` | 取分母 |
| `(part expr n)` | 取第 n 个子部件（1-indexed） |
| `(pickapart expr)` | 展示表达式结构树 |

### 三角/对数/幂简化
| Scheme | 功能 |
|--------|------|
| `(trigexpand expr)` | 三角展开（如 sin(x+y)） |
| `(trigsimp expr)` | 三角恒等式简化 |
| `(powsimp expr)` | 幂合并 xᵃ·xᵇ→xᵃ⁺ᵇ |
| `(logcombine expr)` | 对数合并 log a + log b → log(ab) |
| `(radsimp expr)` | 根式简化 |

### 方程
| Scheme | 功能 |
|--------|------|
| `(solve eq var)` | 解方程/方程组 |
| `(subs expr old new)` | 代入替换 |
| `(lhs eq)` | 取方程左边 |
| `(rhs eq)` | 取方程右边 |
| `(isolate eq var)` | 从方程中隔离变量（调用 sympy.solve） |
| `(lhs eq)` | 取方程左边 |
| `(rhs eq)` | 取方程右边 |
| `(isolate eq var)` | 从方程中隔离变量（调用 sympy.solve） |

### 线性代数
| Scheme | 功能 |
|--------|------|
| `(matrix rows)` | 创建矩阵 |
| `(det M)` | 行列式 |
| `(inv M)` | 逆矩阵 |
| `(transpose M)` | 转置 |
| `(eigenvals M)` | 特征值 |
| `(eigenvects M)` | 特征向量 |
| `(eye n)` | n×n 单位矩阵 |
| `(zeros n m)` | n×m 零矩阵 |
| `(ones n m)` | n×m 全1矩阵 |
| `(lu-decomp M)` | LU 分解 → (L U perm) |
| `(qr-decomp M)` | QR 分解 → (Q R) |
| `(svd M)` | 奇异值 |
| `(norm M)` | 矩阵/向量范数 |
| `(rank M)` | 矩阵秩 |
| `(nullspace M)` | 零空间基向量 |
| `(col M i)` | 取第 i 列 |
| `(row M i)` | 取第 i 行 |

### 微分方程与积分变换
| Scheme | 功能 |
|--------|------|
| `(dsolve eq y_func x)` | 解常微分方程 |
| `(laplace f t s)` | 拉普拉斯变换 L{f}(s) |
| `(inverse-laplace F s t)` | 逆拉普拉斯变换 |
| `(fourier f x k)` | 傅里叶变换 F{f}(k) |
| `(inverse-fourier F k x)` | 逆傅里叶变换 |

### 多项式
| Scheme | 功能 |
|--------|------|
| `(roots p var)` | 符号根 |
| `(nroots p)` | 数值根 |

### 数论
| Scheme | 功能 |
|--------|------|
| `(prime? n)` | 素数判定 |
| `(factorint n)` | 整数因数分解 |
| `(nextprime n)` | 下一个素数 |
| `(prevprime n)` | 上一个素数 |
| `(primerange a b)` | 素数区间 |
| `(divisors n)` | 所有正因数 |
| `(totient n)` | 欧拉函数 φ(n) |
| `(mobius n)` | 莫比乌斯函数 μ(n) |
| `(continued-fraction n)` | 连分数展开 |
| `(diophantine eq)` | 解丢番图方程 |
| `(chinese mods rems)` | 中国剩余定理 (CRT) |
| `(jacobi-symbol a n)` | Jacobi 符号 |
| `(power-mod base exp mod)` | 模幂运算 pow(base, exp, mod) |

### 集合
| Scheme | 功能 |
|--------|------|
| `(set x y z)` | 创建有限集合 |
| `(union s1 s2)` | 并集 |
| `(intersection s1 s2)` | 交集 |
| `(set-difference s1 s2)` | 差集 |
| `(symmetric-difference s1 s2)` | 对称差 |
| `(subset? s1 s2)` | 子集判定 |
| `(element? x s)` | 元素判定 |

### 统计
| Scheme | 功能 |
|--------|------|
| `(mean data)` | 算术平均 |
| `(median data)` | 中位数 |
| `(variance data)` | 方差 |
| `(std data)` | 标准差 |
| `(correlation x y)` | 皮尔逊相关系数 |
| `(regression x y)` | 线性回归 → (slope intercept r²) |

### 特殊函数
| Scheme | 功能 |
|--------|------|
| `(lambertw x)` | Lambert W 函数 W(x) |
| `(lambertw x k)` | Lambert W 第 k 分支 |
| `(polylog n x)` | 多重对数 Liₙ(x) |
| `(stirling n k)` | 第二类斯特林数 S(n,k) |
| `(bernoulli n)` | 伯努利数 Bₙ |
| `(euler_fn n)` | 欧拉数 Eₙ |
| `(fibonacci n)` | 斐波那契数 Fₙ |

### 假设系统
| Scheme | 功能 | 说明 |
|--------|------|------|
| `(assume '(positive x))` | 声明全局假设 | 谓词: positive/negative/zero/integer/real/rational/even/odd/prime 等；运算符: `> < >= <= = !=` |
| `(assume '(integer n)` ` `(assume '(> x 0))` | 多条假设同时声明 | |
| `(unassume)` | 清除全部假设 | |
| `(unassume 'x)` | 清除关于 x 的假设 | |
| `(refine expr)` | 在当前假设下化简 | 基于 sympy.refine |
| `(refine expr '(positive x))` | 给定假设下化简 | 不污染全局假设 |
| `(assuming facts expr ...)` | 临时假设下求值 | facts 是列表的列表: `'((positive x) (integer n))` |
| `(ask '(positive x))` | 查询性质 | 返回 `#t` / `#f` / `unknown` |

### 数值方法
| Scheme | 功能 | 后端 |
|--------|------|------|
| `(find-root f a b :method 'brentq)` | 数值求根 | scipy.optimize (brentq/bisect/newton/ridder) |
| `(numerical-integrate f a b)` | 数值积分 | scipy.integrate.quad |
| `(numerical-derivative f x)` | 数值微分 | scipy.misc.derivative |

### 输出与文档
| Scheme | 功能 |
|--------|------|
| `(pretty expr)` | Unicode 漂亮打印 |
| `(latex expr)` | LaTeX 输出 |
| `(ratsimp expr)` | 有理式化简（通分+展开+约分） |
| `(ccode expr)` | C 代码生成 |
| `(fcode expr)` | Fortran 代码生成 |
| `(mathml expr)` | MathML 生成 |
| `(plot expr var lo hi :kw ...)` | 2D 折线图（numpy 数据或 CAS 表达式，支持多迹线） |
| `(scatter x y :color 'red :s 20)` | 散点图 |
| `(bar x height :width 0.8)` | 柱状图 |
| `(barh y width)` | 水平柱状图 |
| `(hist data :bins 30)` | 直方图 |
| `(boxplot data :notch #f)` | 箱线图 |
| `(violin data :showmeans #t)` | 小提琴图 |
| `(errorbar x y yerr :fmt 'o)` | 误差棒图 |
| `(contour X Y Z :levels 20 :fill #f)` | 等高线/填充等高线 |
| `(imshow data :cmap 'viridis)` | 热力图/图像 |
| `(stem x y)` | 茎叶图 |
| `(pie sizes :labels ...)` | 饼图 |
| `(fill-between x y1 y2)` | 填充区域 |
| `(plot-param fx fy var lo hi :kw ...)` | 2D 参数曲线图 |
| `(plot3d expr var1 lo1 hi1 var2 lo2 hi2 :kw ...)` | 3D 曲面图 |
| `(figure :size (list 10 6) :dpi 100)` | 创建/切换图 |
| `(subplot rows cols index)` | 创建子图 |
| `(savefig "path.png" :dpi 150)` | 保存当前图 |
| `(clf)` / `(close)` | 清空/关闭图 |
| `(text x y "str" :fontsize 12 :color 'red)` | 文字标注 |
| `(axvline x :color 'red :linestyle '--)` | 竖线标注 |
| `(axhline y :color 'gray)` | 横线标注 |
| `(title "text")` / `(xlabel "text")` / `(ylabel "text")` | 快捷标签 |
| `(legend)` / `(grid)` | 图例/网格 |
| `(describe obj)` | Python 文档字符串 |
| `(use-numpy)` | NumPy 一键导入: np 别名 + 40+ 快捷函数 + 自动广播 |
| `(use-learn)` | scikit-learn 一键导入: 30+ 模型 + 数据集 + CV + GridSearch + Pipeline |
| `(use-graph)` | 图论: Graph/DiGraph + shortest-path + pagerank + betweenness |
| `(use-units)` | 物理单位: meter/second/c + kilo/milli + convert-to |
| `(use-tensor)` | 张量: Array + tensor-product + tensor-contraction |
| `(help)` | 按 16 分类列出全部 82 CAS 函数 |
| `(help 'sym)` | 函数详情（语法+说明+示例） |
| `(help "keyword")` | 搜索函数 |
| `(ecosystem)` | 按分类浏览全部 19 个 PyPI 数学包及用法 |
| `(ecosystem 'numpy)` | 查看 numpy 详情 + 示例 |
| `(ecosystem "绘图")` | 搜索包 |
| `(catalog)` | 层级浏览 **29 包 × 9 领域** — scipy/statsmodels/cvxpy/pandas/transformers 等 |
| `(catalog 'scipy.optimize)` | 子模块函数列表（~150 条 curated 函数） |
| `(catalog "最小二乘")` | 跨包搜索（覆盖全部 curated 数据库） |

### 科学计算包目录

`(catalog)` 提供层级化的大包浏览系统（`eval/eval_py_catalog.py`，含 29 包 × 9 领域的 curated 数据库 ~200 条核心函数）：

```scheme
(catalog)                          → 9 领域 × 29 包的顶级目录
(catalog 'scipy)                   → scipy 的 9 子模块 + 核心函数
(catalog 'scipy.optimize)          → 13 个函数 + 说明（curated）
(catalog 'statsmodels)             → 23 项核心功能
(catalog 'cvxpy)                   → 14 项
(catalog 'pandas)                  → 16 项
(catalog 'transformers)            → 10 项（pipeline/AutoTokenizer/AutoModelFor*）
(catalog "最小二乘")               → 跨包搜索
```

搜索覆盖 curated 数据库的函数名、说明和来源包名。未知包自动 fallback 到 `importlib` + `dir()` 动态列出。参考 `references/catalog-system.md`、`references/syntax-sugar-slices.md`。

## 语法宏

### `defsym` — 批量创建 sympy 符号

```scheme
(defsym x y z)
; → (begin (define x (sympy.Symbol 'x))
;          (define y (sympy.Symbol 'y))
;          (define z (sympy.Symbol 'z)))
```

用 `define-macro`（非卫生宏）实现。必须非卫生，因为需要引用用户环境中的 `sympy.Symbol`。

```python
defsym_code = """(define-macro (defsym . symbols)
  (cons 'begin (map (lambda (s)
    (list 'define s (list 'sympy.Symbol (list 'quote s))))
    symbols)))"""
eval_scheme(parse(defsym_code), env)
```

### `with-symbols` — 临时符号作用域

```scheme
(with-symbols (a b)
  (expand (expt (+ a b) 3)))
; → (let ((a (sympy.Symbol 'a))
;         (b (sympy.Symbol 'b)))
;     (expand (expt (+ a b) 3)))
; a 和 b 不泄漏到外部作用域
```

### 注意事项

1. `defsym` 和 `with-symbols` 都需要用户先 `(import sympy)`
2. 在 `primitives.py` 中使用 `eval_scheme(parse(code), env)` 注册
3. `define-macro` 在 `when/unless` 宏注册之后

## PyPI 生态集成（17 已验证）

任意 `pip install <pkg>` 后直接 `(import <pkg>)` 使用，无需适配代码：

```scheme
; 数值计算
(import numpy as np)           ; numpy 2.4.3
(import scipy)                 ; scipy 1.17.1

; 符号计算
(import sympy)                 ; sympy 1.14.0   (60+ CAS 函数)
(import symengine)             ; symengine (sympy 兼容, 10-100x 快)
(import mpmath)                ; mpmath 1.3.0  (高精度 1000+ 位)

; 数据科学
(import pandas)                ; pandas 3.0.3
(import statsmodels.api as sm) ; statsmodels 0.14.6
(import sklearn)               ; scikit-learn

; 优化
(import cvxpy)                 ; 凸优化
(import pulp)                  ; 线性/整数规划
(import ortools)               ; 约束规划

; 其他
(import networkx as nx)        ; 图论
(import galois)                ; 有限域
(import pint)                  ; 物理单位
(import uncertainties)         ; 误差传播
(import matplotlib.pyplot as plt) ; 绘图
(import numba)                 ; JIT 编译
```

### opencv-python

```scheme
(import cv2)
(define img (cv2.imread "photo.jpg"))
(define gray (cv2.cvtColor img cv2.COLOR_BGR2GRAY))
(define edges (cv2.Canny gray 50 150))
(define (ret thresh) (cv2.threshold gray 127 255 cv2.THRESH_BINARY))
(display (py-get thresh 0))  ; 取 retval
```

## `eval_python_import.py` 截断恢复

详见 `references/engine-switching.md`。
详见 `references/help-system.md`（帮助系统设计指南）。
详见 `references/roundtrip-bridge.md`（四向往返映射 + 桥接原语 + 模块注册 + 陷阱）。

## 引擎切换 — symengine/sympy 统一抽象

### 命令

```scheme
(use-engine 'auto)           → symengine 优先，不支持时自动 fallback 到 sympy（默认）
(use-engine 'symengine)      → 强制使用 symengine（更快，适合 diff/expand/series/sin 等核心操作）
(use-engine 'sympy)          → 强制使用 sympy（完整功能，适合 integrate/factor/solve/limit）
(engine-info)                → 显示当前引擎 + 可用引擎版本
```

### 架构

所有 CAS 原语通过 `_sympy()` 获取引擎模块，不再直接 `import sympy`：

```python
def _sympy():
    from eval.eval_cas_engine import get_engine
    return get_engine()
```

`get_engine()` 的调度逻辑：
1. `auto` 模式 → `symengine`（如果可用），否则 `sympy`
2. `symengine` 模式 → `symengine`，不可用时报错
3. `sympy` 模式 → `sympy`，不可用时报错

每个引擎仅首次调用时导入（惰性），结果缓存于 `_engine_cache` 字典。

### 交叉兼容性

symengine 和 sympy 的类型可以**混合使用**，因此引擎切换可在运行时任意进行：

```python
symengine.expand((sympy.Symbol('x') + 1)**2)  # ✅ 跨引擎操作
sympy.factor(symengine.Symbol('x')**4 - 1)     # ✅ 反向跨引擎
```

### 能力矩阵

| 操作               | symengine | sympy |
|--------------------|:---------:|:-----:|
| Symbol/算术/diff/expand/series | ✅ | ✅ |
| sin/cos/sqrt/Matrix/Eq | ✅ | ✅ |
| factor/simplify/subs/solve | ❌ | ✅ |
| integrate/limit/det/inv | ❌ | ✅ |
| dsolve/laplace/fourier | ❌ | ✅ |

### 注册

```python
from eval.eval_cas_engine import register_engine_primitives
register_engine_primitives(env)  # 在 CAS primitives 之后
```

### 已知限制

1. `call()` 智能调度尚未整合到全部 60+ CAS 原语 — 当前每个原语仍通过 `_sympy()` 直接获取引擎后调用 `sp.xxx()`，symengine 不支持的操作会抛 `AttributeError`
2. 请先 `(import symengine)` 再 `(define x (symengine.Symbol 'x'))` — `use-engine` 仅影响原语调度，不影响已创建的符号类型

## 模式匹配系统（P1, 本轮新增）

`match`/`defrule`/`rewrite`/`rules`/`clear-rules` — 对标 Maxima 的代数重写系统。

在 `eval_scheme.py` 中注册为特殊形式（非 Prim），因为 `?x` 等模式变量须保持未求值状态。详见 `references/pattern-matching.md`。

关键实现：
- `eval/eval_py_pattern.py`: `_match_pattern`, `_subst`, `_define_rule`, `_apply_rules`, `_eval_match`
- `eval/eval_scheme.py`: `case Sym("match"/"defrule"/"rewrite"):` — 从 `cons.cdr` 取未求值的模式形式
- `?x` 符号在 `eval_scheme.py` 的 `Sym` case 中添加了 `sym.name.startswith("?")` 自求值逻辑

```scheme
(match (* ?a x) #{3*x})           → ((a 3))
(defrule sin-squared (expt (sin ?x) 2) (- 1 (expt (cos ?x) 2)))
(rewrite #{sin(x)^2} sin-squared)  → 1 - cos²(x)
(rules)
```

## 张量代数（P1, 本轮新增）

`index`/`tensor`/`contract`/`raise-index`/`lower-index`/`tensor-show` — 指标符号张量运算。

全部在 `eval_scheme.py` 中注册为特殊形式（`i`, `j`, `k` 等指标在环境中未绑定，Prim 会抛出 Unbound variable）。详见 `references/tensor-algebra.md`。

```scheme
(index i j k l)
(define R (tensor "R" (i j k l) ()))    ;; Riemann 张量 R_ijkl
(contract R i k)                          ;; → Ricci 张量 R_jl
```

## REPL 增强（P1, 本轮新增）

`eval/eval_repl.py` 提供 readline TAB 补全和历史记录：

```python
from eval.eval_repl import install_repl
install_repl(lambda: global_env)  # 在 main.py 中调用
```

## 惰性导入框架（P1, 本轮新增）

`main.py` 中的 `_LazyPrimitiveModules` 机制：非核心模块延后到首次调用时才 `importlib.import_module`，加速启动时间。

## 引擎自动降级代理（2026-06-23 新增）

`_EngineProxy` 通过 `__getattr__` 实现透明 symengine→sympy 降级。详见 `references/cas-module-restoration-pattern.md`。

## 文档驱动重构（2026-06-23 新增）

`doc/*.md` 是代码的设计规范。当代码与文档不一致时优先修正代码，包括 API 名称对齐和缺失功能补齐。详见 `references/cas-module-restoration-pattern.md`。

## 模块恢复模式（2026-06-23 新增）

字面 `\n` 修复、空 `__init__.py` 修复、子代理超时恢复、Flat→Package 双重导出。详见 `references/cas-module-restoration-pattern.md`。


  
## 增强中缀语法（本轮新增）

在原有 infix parser 基础上新增常见数学表达的自然映射，全部通过 `#{...}` 中缀表示：

| 数学表达 | `#{...}` 写法 | 展开 | 求值 |
|---------|--------------|------|------|
| **绝对值** | `#{ \|x\| }` | `(abs x)` | `Abs(x)` |
| | `#{ \|x-1\| }` | `(abs (- x 1))` | `Abs(x-1)` |
| **阶乘** | `#{5!}` | `(factorial 5)` | `120` |
| | `#{3! * 2}` | `(* (factorial 3) 2)` | `12` |
| **范围** | `#{1..10}` | `(range 1 10)` | `[1 2...10]` |
| **下标** | `x_y` | `(ref x y)` | `x[y]` |
| | `a_{n+1}` | `(ref a (+ n 1))` | `a[n+1]` |
| **矩阵字面量** | `#{ [1 2; 3 4] }` | `(matrix (list 1 2) (list 3 4))` | `[[1,2],[3,4]]` |

实现要点：
- `|` 作为分组构造，在 `_prefix` 中处理（非运算符）
- `!` 在隐式乘法之前检测，支持数字和表达式后缀
- `..` 二元运算符（BP=35），数字遇到 `..` 提前停止
- `_` 二元运算符（BP=55，右结合），tokenizer 中视为分隔符
- `;` 在 infix tokenizer 中不视为注释（矩阵行分隔）
- `{...}` 作为分组表达式（非 set），用于下标复合表达式
- CAS-aware `abs` 对 PythonObject 用 `sympy.Abs`
- `factorial`/`ref`/`range` 注册为 Prim（`eval/eval_py_sugar.py`）

详见 `references/infix-parser.md`。

### `parse()` 只返回首个表达式

`parser.parse_program.parse(input_str)` 返回所有解析形式的列表，但 `parse()` 只返回 `parsed[0]`。

**影响**：多表达式的宏定义字符串（如多个 `define-macro`）必须用 `(begin ...)` 包裹，否则只有第一个表达式被注册。已在 `_P2_AUGMENT` 等宏定义中发现并修复。

**修复写法**：
```python
_P2_AUGMENT = """
(begin
  (define-macro (+= var val) (list 'set! var (list '+ var val)))
  (define-macro (-= var val) (list 'set! var (list '- var val)))
  (define-macro (*= var val) (list 'set! var (list '* var val)))
  (define-macro (/= var val) (list 'set! var (list '/ var val))))
"""
```

### `define-macro` 非卫生特性与 Sym 对象

`define-macro` 的参数是已解析的 `Sym` 对象，而非源码符号。这导致 `(list 'quote engine)` 产生 `(quote Sym('sympy'))` 而非期望的 `(quote sympy)`。

**影响**：需要生成符号引用的宏（如 `with-eng` 的 `(use-engine engine)`）无法直接使用 `(list 'use-engine (list 'quote engine))`，因为 `engine` 是 `Sym('sympy')` 而非源码符号 `sympy`。

**解决方案**：
- **Prim + quote body 模式**：将宏改为 Prim，要求用户用 quote 阻止 body 提前求值：
  ```scheme
  (with-eng 'sympy '(expand (expt x 3)))  ; body 被 quote
  ```
- **避免在宏中构造符号引用**：如果宏需要生成 `(use-engine sympy)`，直接传递 `engine` 参数（它是 `Sym('sympy')`），因为 `Sym` 在任何位置都是有效的符号引用。

### `with-eng` 的 Prim + quote body 模式

由于宏无法正确处理引擎名符号，`with-eng` 实现为 Prim，要求 body 被 quote：

```scheme
;; 用法
(with-eng 'symengine '(expand (expt (+ x 1) 3)))
;; 等价于：
;; (let ((%saved (engine-name)))
;;   (use-engine 'symengine)
;;   (let ((%result (expand (expt (+ x 1) 3))))
;;     (use-engine %saved)
;;     %result))
```

### Prim vs Macro vs Special Form 选择指南

| 特性 | Prim | define-macro | Special Form |
|------|------|-------------|--------------|
| 参数求值 | 先求值后传入 | 未求值（Sym/Cons 对象） | 未求值（原始 Cons） |
| 执行上下文 | Python | Scheme 宏展开时 | Scheme 求值器 |
| 适用场景 | 纯计算、需要 Python 库 | 代码变换、语法糖 | 控制流、非求值上下文 |
| 限制 | 无法接收未求值表达式 | 非卫生、Sym 对象陷阱 | 需修改 eval_scheme.py |
| 示例 | `py`, `py-f`, `with-eng` | `+=`, `for`, `->`, `define-data` | `match`, `rewrite`, `try` |

**经验法则**：
- 需要 Python 库支持 → Prim
- 需要阻止参数求值 → Special Form（或 Prim + quote body 模式）
- 简单的语法糖 → define-macro
- 需要访问环境变量（env）→ Prim（捕获 env 闭包）或 Special Form

### Python 多行字符串 `"""..."""` 支持

在 tokenizer 和 parser 中添加：

- **tokenizer** (`parser/tokenize.py`)：检测 `"""` 开头，收集至闭合 `"""`，跳过首行换行，处理 `\` 转义。
- **parser** (`parser/parse_form.py`)：在常规字符串处理前添加 `case _ if token.startswith('"""')`，剥离三引号后构造 `Str`。

```scheme
(py "np.array([
    [1, 2, 3],
    [4, 5, 6]
])")

(py-f """Values:
a = {a}
x = {x}
""")
```

### Python 互操作扩展

新增 `eval/cas/py.py` 注册三个原语和一个宏：

| 名称 | 类型 | 功能 |
|------|------|------|
| `(py "expr")` | Prim | Python eval，自动注入 Scheme 环境变量和常见模块（np/sp/math） |
| `(py-f "fmt")` | Prim | Python f-string 格式化，`{var}` 自动注入 Scheme 变量 |
| `..` | define-macro | 方法链展开：`(.. obj (method1 args) (method2 args))` |
| `"""..."""` | tokenizer/parser | 多行字符串字面量 |

`py` Prim 的变量注入逻辑：从表达式字符串提取标识符，过滤 Python 关键字和内置函数，在 Scheme 环境中查找并解包为 Python 值。自动注入 `np`、`sp`、`math`、`numpy`、`sympy` 等常见模块。

### 定义宏与 Prim 注册的去重

**原则**：`define-macro` 和 `defin-syntax` 形式的宏应注册在 `sugar/core.py` 中，通过 `eval_scheme(parse(code), env)` 注册。Prim 注册在同一文件的 Python 函数中。

**陷阱**：`entry/core.py` 中的 `cas_use_cas` 曾包含重复的 `define-macro` 定义（λ/→/→>/for/str），这些宏已在 `sugar/core.py` 注册。删除后避免每次 `(use-cas)` 时重复定义。

### 循环导入修复：`core/env.py ↔ core/schemevalue.py`

**根因**：`schemevalue.py:512` 的 `from core.env import Env, CORE_KEYWORDS` 用于回导出，但在 `env.py` 导入 `schemevalue.py` 时形成循环。

**修复**：
1. 移除 `schemevalue.py` 中的回导出语句
2. 在所有使用 `Env` 类型注解的文件中添加 `from core.env import Env`
3. 在 `core/tail_call.py` 中添加缺失的 `from core.env import Env`

**影响文件**：约 15 个 eval/ 和 macro/ 文件需要添加 `from core.env import Env`。

## 已知限制与解决方案

### 执行模式陷阱

**当用户给出明确的存储/命名原则时，不要问 3+ 个确认问题。** 直接应用原则并展示一个具体示例，让用户看效果后确认，再批量执行。

错误示范：用户说「env.define 名称应该是 xxx.yyy.zzz」，你列出 3 个「请问 A？B？C？」。
正确反应：直接写一个 `env.define("core.algebra.expand", ...)` 示例，运行验证，然后问「是这个意思吗？」。

| 问题 | 影响 | 解决方案 |
|------|------|---------|
| `).method` 被读作点对 | 链式方法调用被破坏 | 用 `(. obj method args...)` 或中间变量 |
| Python 切片 `arr[2:8]` | 无法直接表达 | `[arr 2 8 2]` → `arr[2:8:2]` |
| 多维索引 `m2[1:3,2:5]` | 无法直接表达 | `[m2 (py-slice 1 3) (py-slice 2 5)]` |
| Python `+=` 运算符 | 不可用 | `obj.__iadd__(x)` |
| 属性值误调用 | `(reg.intercept_)` 报错 | 属性无括号，方法有括号 |
| 0-arg 不可调用属性 | 返回自身 | 自动推断（不抛出异常） |
| Python 异常桥接 | guard 无法捕获 Python 错误 | 当前不支持 |
| `py-eval` 变量隔离 | eval 不知 Scheme 变量 | `(py-eval "expr" :var1 val1 :var2 val2)` |
| sympy ODE 参数类型 | `dsolve` 需 `Function` | 用 `(sympy.Function 'y)` 而非 `(sympy.Symbol 'y)` |

## 完整测试架构

```bash
cd /workspace/99
for f in tests/*.scm; do python3 main.py "$f"; done
```

### 测试文件清单 (33 个)

| 文件 | 覆盖范围 |
|------|---------|
| `python_interop.scm` | 基础 import/from/py-eval |
| `python_cascade.scm` | 级联调用 `(math.sqrt 16)`、`a.T` |
| `numpy_demo.scm` | numpy 全套 |
| `numpy_kwargs.scm` | 关键词参数 |
| `as_alias.scm` | `(import numpy as np)` |
| `sympy_seamless.scm` | sympy 算术透明 + 微积分 |
| `sympy_pretty.scm` | sympy.pprint / latex |
| `sympy_full.scm` | sympy 11 模块全量覆盖 (50+ 测试项) |
| `vector_interop.scm` | Vector 数据传递 |
| `scipy_stats.scm` | scipy/statsmodels/mpmath |
| `cas_demo.scm` | CAS 原语演示 |
| `cas_sugar.scm` | with-symbols 宏、describe 文档 |
| `cas_enriched.scm` | 向量微积分/三角简化/数论/集合/统计/特殊函数 |
| `opencv_test.scm` | opencv-python 12 项测试 |
| `comprehensive.scm` | 综合：defsym、三向转换、全库覆盖 |
| `pypi_ecosystem.scm` | PyPI 17 包集成验证 |
| `package_registry.scm` | 包注册表文档化 |
| `deep_numpy.scm` | numpy 10 子模块深度测试 |
| `deep_scipy.scm` | scipy 7 子模块深度测试 |
| `deep_medium.scm` | mpmath/uncertainties/pint/galois/symengine |
| `deep_ds_opt.scm` | pandas/sklearn/cvxpy/pulp |
| `deep_report.scm` | 基础设施缺失报告 |
| `test_bracket.scm` / `test_dot.scm` | 方括号 / `.` 特殊形式 |
| `r1_types.scm` ~ `r10_final.scm` | 10 轮深度回归测试 |

## 设计陷阱

1. **大文件拆分的 Shim 模式**: 拆分像 `eval_python_import.py`（40 处 import 引用) 这样被广泛导入的文件时，不要直接改所有调用方。改为：提取功能到新文件（`eval_py_convert.py` 等），原文件变成纯重导出 shim（`from eval.eval_py_convert import ...`）。0 处 import 断裂，新代码可直接导入子模块。

2. **循环依赖的延迟导入**: 从 `eval_scheme.py` 提取函数到新文件时，如果新文件需要回调求值器（如 `eval_try.py` 需 `eval_scheme(body_form, env)`），在函数体内用 `from eval.eval_scheme import eval_scheme` 延迟导入。不要放在模块级 — 那会导致 `eval_scheme → 新文件 → eval_scheme` 循环。同理适用于 `eval_bracket_args`, `eval_special_forms`, `eval_cas_dispatch`, `eval_macro_forms`。

3. **提取函数的控制流通信**: 从蹦床循环中提取函数时（如 `if`/`begin` 需要 `exp=...; continue`），函数不能直接 `continue`。用 `_Continue(expr)` 哨兵对象（定义在提取文件中）返回给调用方，调用方检查 `is_cont(result)` → `exp=result.expr; continue`。`eval/eval_short_circuit.py` 展示了这个模式。**: `_sympy()` 在 Prim 函数内部调用而非模块级，允许用户选择导入时机。import 失败时给出明确提示。

2. **sympy ODE 需要 Function**:
```scheme
(define y_func (sympy.Function 'y))
(dsolve (+ (diff (y_func x) x) (* -2 (y_func x))) (y_func x) x)
```

3. **`define-macro` 非卫生**: defsym/with-symbols 展开中的 `sympy.Symbol` 在用户环境中查找，注册顺序须在 python-import 之后。

4. **算术透明度的 math→sympy fallback 链**: 先试 `math.xxx`，`TypeError`→试 `sympy.xxx`。这确保普通 float 走 math（更快），sympy Symbol 自动 fallback。
   - **RuntimeError 陷阱**: `math.sin(symengine.Symbol('x'))` 抛 `RuntimeError("Symbol cannot be evaluated.")` 而非 `TypeError`。所有 `try_py_*` 函数的 `except` 子句中都必须包含 `RuntimeError`。修复文件: `eval/eval_py_arithmetic.py`（`try_py_unary_math`、`try_py_atan`、`log` 特殊处理）。**添加新算术函数时务必包含 `RuntimeError`**。

5. **Cons 不可迭代**: Scheme 的 `Cons` 链（`(a b c)` 表示为 `Cons('a', Cons('b', Cons('c', Nil())))`）不支持 Python 的 `__len__`/`__getitem__`。用 `for i in range(len(cons))` 会抛 `TypeError`。**固定模式：用 `while isinstance(cons, Cons)` 遍历。** 需要收集全部元素时，用 `from_lisp_list(cons)`（定义在 `core/schemevalue.py`）或手写：

6. **系统级 omission 扫描**: 扩展模块时，"定义但未注册"的函数不会自动报错 — 直到运行时调用才抛 NameError。预防方法：每次添加一批新函数后，用扫描脚本 diff 定义集与注册集：
```python
# 扫描所有 def pnp_xxx / def cas_xxx
defined = {fn for line in content if line.startswith('def pnp_')}
# 扫描所有 ("np.xxx", pnp_xxx) 注册条目  
registered = {fn_part for line in register_block if '("np.' in line}
# 计算差值
for fn in sorted(defined - registered):
    print(f"MISSING: {fn}")
```
本工程中一次性修复了 124 个缺失（numpy 原语 170→322）。

7. **`__init__.py` 内部符号导出清单**: 将扁平 `.py` 转为 `name/` 目录时，`__init__.py` 不能只导出 `register_*` 函数。必须同时导出所有被其他模块 import 的内部符号：
   - `engine/`: `register_engine_primitives`, `get_engine`, `engine_call`
   - `tensor/`: `register_tensor_primitives`, `_declare_indices`, `_make_tensor`, `_do_contract`, `_do_raise`, `_do_lower`
   - `pattern/`: `register_pattern_primitives`, `_eval_match`, `_define_rule`, `_apply_rules`
   - `info/help/`: `register_help_primitives`, `cas_help`
   - `info/catalog/`: `register_catalog_primitives`, `cas_catalog`
   - `info/nav/`: `register_nav_primitives`, `cas_nav`

8. **`Str()` 构造要求**: Python `str` → Scheme `Str` 必须用 `Str(list(py_str))`，不可直接 `Str(py_str)`。推荐辅助函数：
```python
def _s(val: str) -> Str:
    return Str(list(str(val)))
```

9. **`\n` 字面量损坏修复**：当生成脚本使用 `'\\n'.join(lines)` 写入文件时，如果 escapes 处理不当会导致文件中出现字面 `\n` 字符串而非真实换行。

   诊断：`cat -A file.py` 显示每行末尾有 `\n$` 而非 `$`。或者 `grep -rl $"\\n" --include='*.py' .`

   修复：
   ```python
   with open(path) as f:
       raw = f.read()
   fixed = raw.replace('\\n', '\n')
   with open(path, 'w') as f:
       f.write(fixed)
   ```

   修复后必须逐文件验证：`python3 -c "compile(open(path).read(), path, 'exec')"`

10. **`register_unknown` 函数名修复 + 模块恢复（2026-06-23 补充）**：生成脚本留下 `register_unknown` 作为默认函数名。修复方法见 `references/cas-module-recovery.md`。

    其他已知的模块破损恢复模式：：生成脚本或文件损坏可能遗留空 `__init__.py`（仅一个换行）。修复：`write_file` 写入标准内容：
    ```python
    """{mod_name}"""
    from .core import register_{mod_name}_primitives
    ```

    常见受影响目录：`assume/`, `sugar/`, `numerical/`, `info/catalog/`, `info/ecosystem/`

12. **修复后系统验证命令**：执行完上述修复后，运行全面检查：
    ```bash
    # 语法检查
    python3 -c "
    import os
    errors = []
    for root, dirs, files in os.walk('eval/cas'):
        if '__pycache__' in root: continue
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                try:
                    compile(open(path).read(), path, 'exec')
                except SyntaxError as e:
                    errors.append((path, str(e)))
    print('PASS' if not errors else 'FAIL: ' + str(errors))
    "

    # 全部 __init__ 导出验证
    python3 -c "
    from primitives.primitives import register_all
    print('primitives OK')
    "
    ```

13. **Flat → Package 转换的 `__init__.py` 双重导出**：当扁平 `.py` 文件被子代理或生成脚本转为 `name/` 包目录时，`__init__.py` 必须同时导出 `register_{name}_primitives`（供 `primitives.py` 命名导入）和 `register_primitives`（供聚合器别名导入）。详见 `references/flat-file-to-package-pitfall.md`。
    ```\n```python\nitems = []\nwhile isinstance(val, Cons):\n    items.append(unwrap_python_value(val.car))\n    val = val.cdr\n```

```python
def cas_refine(args):
    import sympy  # 直接导入 sympy
    py_expr = sympy.sympify(...)
    result = sympy.refine(py_expr)  # symengine 没有 refine
    return wrap_python_value(result)
```

6. **REPL %**: 上一步计算结果存储在环境变量 `%` 中。在 `main.py` 的 REPL 循环中，每轮解析并求值全部表达式后，将最后一个非 undefined 结果绑定到 `Sym("%")`。批处理模式（`python3 main.py file.scm`）不设置 `%`。

## 已修复的基础设施缺失

| 修复 | 功能 | 文件 |
|------|------|------|
| `py-dict` | Python dict 创建 `(:key val)` | `eval/eval_python_import.py` |
| `py-get` 整数索引 | `(py-get tup 0)` = `tup[0]` | 同上 |
| `py-get` PythonObject 索引 | `(py-get arr slice_obj)` = `arr[s]` | 同上 |
| `py-len` | `(py-len obj)` = `len(obj)` | `eval/eval_py_cas.py` |
| `__code__`/`__signature__` | scipy.curve_fit 多参数 lambda | `SchemeClosureWrapper` |
| 方括号语法 `[arr 5]` | `[a b]`→`a[b]`, `[a s e step]`→`a[s:e:step]` | parser + eval |
| `py-eval` 变量注入 | `(py-eval "expr" :var val)` | `eval_python_import.py` |
| `.` 特殊形式 | `(. obj method args...)` | `eval/eval_scheme.py` |
| **Bridge prims (unwrap/wrap/py-str/eq/type)** | 4方向往返闭环 (2026-06-22) | `eval/eval_python_import.py` |
| **eval/ 目录重构** | 扁平→6子目录 (cas/data/text/io/crypto/system) | 全部 eval_py_* |
| **srepr eval fallback** | `parse(srepr_str)` + `eval` 安全沙箱 | `eval/cas/parse.py` |
| **引擎管理器** | symengine/sympy 统一抽象 + 惰性导入 + 智能调度 | `eval/cas/engine.py` |
| **`(eqn ...)` CAS 方程原语** | `#{x = 0}` → `sympy.Eq(x, 0)` | `primitives/primitives_eq.py` |
| **中缀表达式 reader macro** | `#{x^2 - 4 = 0}` 自动解析 | `parser/infix.py` + 两条集成路径 |
| **一元负号 `(- x)`** | 原 `(negate x)` 导致 Unbound variable，改用标准 `(- x)` | `parser/infix.py` |
| **可视化后端** | matplotlib 2D/参数/3D 绘图 | `eval/eval_py_viz.py` |
| **帮助系统** | 82 CAS 函数结构化文档 | `eval/eval_py_help.py` |
| **引擎管理器** | symengine/sympy 统一抽象 + 惰性导入 + 智能调度 | `eval/eval_cas_engine.py` |
| `RuntimeError` 算术代理修复 | symengine Symbol → `math.sin()` 抛 RuntimeError | `eval/eval_py_arithmetic.py` |
| **Bytevector `.data` 而非 `.value`** | Bytevector 用 `data`（bytearray）非 `value` | 所有 eval 模块 |
| **`Stream` 名称冲突** | `core/stream.py` 可能被 `pandas` 等 Python 包的 `stream` 库遮蔽 | 修复中 |
| **桥接模块** | use-graph/use-units/use-tensor — 图论/物理单位/张量 | `eval/eval_py_bridge.py` |
| **方程/数值/输出工具** | lhs/rhs/num/denom/isolate/part/pickapart + find-root/numerical-integrate + ratsimp/ccode/fcode/mathml | `eval/eval_py_cas.py` + `eval/eval_py_numerical.py` |
| **`(from ... import ...)` 解析修复** | `eval_from_form` 使用 `from_lisp_list(cdr)` 替代 `list(cdr)`（Cons 不可迭代） | `eval/eval_python_import.py` |
| **`. obj 'method` 引号支持** | `.` 特殊形式同时接受 `'method` 和 `method`（检查 `car == Sym('quote')` 后 unwrap） | `eval/eval_scheme.py` |
| **Bunch `load-digits` 保持 PythonObject** | `load-digits` 等返回 `PythonObject(ds)` 而非 `wrap_python_value(ds)`（后者将 Bunch 转为 alist，丢失 `.data`/`.target` 属性） | `eval/eval_py_learn.py` |
| **`train-test-split` 返回值可索引** | 返回 `PythonObject(result)` 而非 `wrap_python_value(list(result))`（后者转 Cons，`py-get` 无法索引） | `eval/eval_py_learn.py` |
| **`py-get` 处理 Cons 失败** | `py-get` 要求 PythonObject；`train-test-split` 等返回的 tuple 必须包 PythonObject | `eval/eval_py_learn.py` + `eval/eval_python_import.py` |
| **科学计算包目录 (`catalog`)** | 层级浏览 scipy/statsmodels/cvxpy/pandas 的核心函数，含跨包中文搜索 | `eval/eval_py_catalog.py` |
| **`. obj 'method` 引号支持** | `.` 特殊形式可接受 `'method` 和 `method` 两种写法 | `eval/eval_scheme.py` |
| **`. obj 'attr` 属性访问** | Bunch 对象通过 `PythonObject(ds)` 强制保持 PythonObject 以支持 `.` 属性访问 | `eval/eval_py_learn.py` |

## 下一步路线图（从本会话产出）

**当前 CAS 完成度 ≈ Maxima 的 60%**。本质是"Python API 的 Scheme 语法糖封装"，以下 7 个 Phase 指向真正"Scheme 风格 CAS"。

### Phase 1 — 中缀表达式 reader macro + eqn 方程 DSL（已完成 ✅）

```scheme
#{x^2 - 4*x = 0}  →  (eqn (- (expt x 2) (* 4 x)) 0)
(eqn x 0)          →  sympy.Eq(x, 0)  ← 求值后
```

参考 `references/viz-enhancement.md`（完整图表类型、关键词参数、图管理、标注）。
| `references/module-registry.md` | 完整模块目录 + 新增模块步骤 + 陷阱清单 |
| `references/learn-module-pattern.md` | **learn 模块设计模式 (新增)**: 大库层次分解(118单模型目录)、聚合器模式、子模块导入独立性陷阱、demo.md文档模板与傻瓜式教学要求、示例输出标注 |]
参考 `references/cas-entry-system.md`、`references/infix-parser.md`、`references/syntax-sugar-slices.md`。
- 优先级：`=<>!=` (10) < `+-` (30) < `*/` (40) < 隐式乘法 (45) < `^` (60) < `f(...)` (70)
- 隐式乘法：`2x`, `(x+1)(x+2)`, `2(x+1)`
- `name(...)` 函数调用，`(expr)(expr)` 隐式乘法
- 一元负号 `-x` → `(- x)`（Scheme 标准，避免自创 `(negate x)` 导致 Unbound variable））
- `^` 右结合：`a^b^c` → `(expt a (expt b c))`
- `=` 映射到 `(eqn ...)` 而非 Scheme 的 `=`
- 一元负号 `-x` → `(- x)`（Scheme 标准，避免自创 `(negate x)` 导致 Unbound variable）
- Unicode 别名：`π→pi`, `√→sqrt`, `∫→integrate` 等 20+
- 两条解析路径均支持：Tokenizer 路径 + Reader 路径
- 可嵌入 Scheme：`(+ #{x + 1} #{y^2})`

**`eqn` primitive**（`primitives/primitives_eq.py`）:
```scheme
(eqn x 0)  →  sympy.Eq(x, 0)   ← 双参数，自动 sympify
(eqn 1 1)  →  sympy.true       ← 无 sympy 时降级为 ==
```

实现细节：
- 2 参数 Prim，用 `unwrap_python_value` + `wrap_python_value` 桥接
- `try: import sympy; sympy.Eq(a, b)` 创建符号方程
- 无 sympy 时回退 `Bool(a == b)`
- 注册在 `register_comparison(env)` 中，紧接 Scheme 标准比较运算符

实现文件：`parser/infix.py` (Pratt 解析器) + `parser/tokenize.py` / `parser/parse_form.py` / `reader/reader.py` 集成 + `primitives/primitives_eq.py` (eqn primitive)。

### Phase 2 — 可视化后端 + 帮助系统（已完成 ✅）

- `(plot expr var lo hi :title ...)` — matplotlib 2D 多迹线图
- `(plot-param fx fy var lo hi ...)` — 2D 参数曲线
- `(plot3d expr var1 lo1 hi1 var2 lo2 hi2 ...)` — 3D 曲面
- `(help)` / `(help 'sym)` / `(help "keyword")` — 82 函数结构化帮助系统
- 实现文件：`eval/cas/viz.py`, `eval/cas/help.py`
- 注册在 `primitives/primitives.py` 的 `register_viz_primitives` / `register_help_primitives`
- 旧 sympy 版 `plot` 已从 `eval/eval_py_cas.py` 移除，由 matplotlib 版取代

### Phase 3 — symengine 引擎切换 + 惰性导入（已完成 ✅）

```scheme
(use-engine 'auto)           → symengine 优先，fallback 到 sympy
(use-engine 'symengine)      → 强制 symengine（10-100x 更快）
(use-engine 'sympy)          → 强制 sympy（完整功能）
(engine-info)                → 显示引擎状态
```

详见 `references/engine-switching.md`。
详见 `references/help-system.md`（帮助系统设计指南）。
详见 `references/roundtrip-bridge.md`（四向往返映射 + 桥接原语 + 模块注册 + 陷阱）。

### Phase 4 — 假设系统 + 代数完备（已完成 ✅）

```scheme
(assume '(positive x))
(refine (sqrt (expt x 2)))  → x
```

详见 `references/assumptions-numerical.md`。实现文件：`eval/cas/assume.py`，注册在 `register_assume_primitives`。额外工具：`lhs/rhs/num/denom/isolate`（方程/表达式工具），`ratsimp/ccode/fcode/mathml`（输出格式），`find-root/numerical-integrate/numerical-derivative`（数值方法，`eval/cas/numerical.py`），`%`（REPL 上步结果），`part/pickapart`（表达式子部件），`chinese/jacobi-symbol/power-mod`（数论扩展），`lu-decomp/qr-decomp/svd/norm/rank/nullspace/col/row`（矩阵分解，`eval/cas/core.py`）。

### Phase 5 — 桥接模块: 图论 / 物理单位 / 张量（已完成 ✅）

```scheme
(use-graph)   → networkx 自动导入: Graph, DiGraph, add-edge, shortest-path, pagerank
(use-units)   → sympy.physics.units: meter, second, c, h, G, kilo, convert-to
(use-tensor)  → sympy.tensor.array: Array, tensor-product, tensor-contraction
```

详见 `eval/cas/bridge.py`。注册在 `register_bridge_primitives`。

### Phase 6 — numpy/scikit-learn/生态系统增强（已完成 ✅）

```scheme
(use-numpy)                    → np 别名 + 40+ 快捷函数 + 自然切片 `:` 语法 + 负索引兼容
(use-learn)                    → 30+ 模型 + 数据集 + CV + GridSearch + Pipeline + 非参模型
(ecosystem)                    → 19 包分类浏览
(catalog)                      → 29 包 × 9 领域层级浏览 + 跨包搜索
```

详见 `references/numpy-source-alignment.md`（NumPy 源码目录对齐 + 全覆盖方法）。详见 `references/numpy-enhancement.md`、`references/sklearn-enhancement.md`、`references/ecosystem-display.md`、`references/catalog-system.md`。

### Phase 7 — 语法糖 + 一键加载 + 可视化增强（本轮新增 ✅）

```scheme
(use-cas)                      → 一键加载全部 CAS 能力
(? 'diff)                      → 快捷帮助
(?? "微积分")                  → 快捷搜索
(λ (x) (* x 2))               → lambda 缩写
(-> 5 (* 2) (+ 1))            → 管道 → 11
(for (x xs) (* x x))          → 列表推导
(str "x=" 42)                  → 字符串插值
plot/scatter/hist/bar/boxplot/violin/contour/imshow/stem/pie/…
figure/subplot/savefig/clf/close
title/xlabel/ylabel/legend/grid
text/axvline/axhline

;; CAS 入口系统
(use-cas 'all)                 → 含 sklearn + 图论 + 物理单位
(list-all)                     → 列出全部 500+ 函数
```

详见 `references/cas-entry-system.md`、`references/syntax-sugar-slices.md`、`references/viz-enhancement.md`。

### Phase 7 — numpy 共享内存 + numba JIT
```scheme
(define arr (py-buffer 1000000))  ; 预分配共享内存，无拷贝
```

### Phase 6 — 教程笔记本 + 项目打包
- 10 个 `.scm` 教程文件（基础算术~数论）
- `pyproject.toml` 让 `pip install .` 可安装

### Phase 7 — 生态扩展
rpy2 (R 语言桥接)、sqlalchemy (数据库)、PySR (符号回归)