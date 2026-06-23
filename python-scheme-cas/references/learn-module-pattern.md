# learn 模块设计模式 — 模型目录分解 + 子模块丰富文档

从 `eval/cas/learn/` 的重构中提炼的模式。

## 一、大库的目录分解策略

### 层次分解（sklearn → learn/）

第 1 层：包 → 子模块
```
learn/
├── core.py           (聚合器)
├── helpers/          (辅助函数)
├── datasets/         (数据集)
├── models/           (模型)
├── preprocessing/    (预处理)
├── metrics/          (指标)
├── model_selection/  (模型选择)
├── pipeline/         (Pipeline)
└── analysis/         (分析)
```

第 2 层：子模块 → 单个类目录（learn/models 的 118 个模型）
```
learn/models/linear_model/
├── core.py            (聚合器: 导入 35 个单模型子目录)
├── linear_regression/
│   ├── core.py        (注册 1 个类: LinearRegression)
│   ├── __init__.py
│   └── demo.md
├── ridge/
│   ├── core.py        (注册 1 个类: Ridge)
│   ├── __init__.py
│   └── demo.md
...
```

### 目录命名

Python 包目录名必须是有效标识符：
- **不能含连字符 `-`**：`model-selection/` → `ModuleNotFoundError`。必须用 `model_selection/`
- **CamelCase→snake_case 转换**：
  ```python
  import re
  def camel_to_snake(name):
      s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
      s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
      return s2.lower()  # LinearRegression→linear_regression
  ```
- 纯大写缩写类名（SVC/SVR/PCA/NMF）→ 全小写（svc/svr/pca/nmf）

### 聚合器模式

每层有一个 `core.py` 作为聚合器：

```python
# models/linear_model/core.py (第 1 级)
from eval.cas.learn.models.linear_model.linear_regression.core import register_linear_regression
from eval.cas.learn.models.linear_model.ridge.core import register_ridge
# ... 35 个

REGISTER_FUNCS = [register_linear_regression, register_ridge, ...]

def register_linear_model(env):
    for fn in REGISTER_FUNCS:
        fn(env)
```

```python
# models/core.py (第 2 级)
from eval.cas.learn.models.linear_model.core import register_linear_model
from eval.cas.learn.models.svm.core import register_svm
# ... 11 个

def register_models(env):
    for fn in REGISTER_FUNCS:
        fn(env)
```

## 二、子模块导入独立性（关键陷阱）

每个 `subpkg/core.py` 独立加载，**必须自己 import 所有需要的符号**：

```python
# ✅ 正确：每个 core.py 自己导入
from core.schemevalue import Sym, Prim, Str, PythonObject
from eval.eval_python_import import wrap_python_value, unwrap_python_value
from eval.cas.learn.helpers import call_metrics, parse_kwargs_pos

# ❌ 错误：依赖调用方的 import 传递作用域
```

验证：`python3 -c "from eval.cas.learn.XXXX.core import register_XXXX"` — 失败则缺导入。

本工程中所有子模块（datasets/models/preprocessing/metrics/model_selection/pipeline/analysis）和 118 个单模型目录均遵守此规则。

## 三、demo.md 文档模式

### 分离原则

**用例示例放 demo.md，不放 Python docstring**。docstring 编辑可能意外破坏 Python 语法。

### 每级分解都配 demo.md

```
learn/
├── demo.md              # 顶级教程 (824 行, 完整 ML 流程)
├── datasets/demo.md     # 子模块级 (196 行)
├── models/
│   ├── demo.md          # 子模块概览
│   ├── linear_model/
│   │   ├── demo.md      # 子模块级
│   │   ├── linear_regression/demo.md  # 单模型级
│   │   └── ...
│   └── ...
```

### 单模型 demo.md 模板

```markdown
# models/linear_model — LogisticRegression

逻辑回归（分类模型）。

## 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `:C` | `1.0` | 正则化倒数。越小越强 |
| `:penalty` | `'l2` | l1/l2/elasticnet |

## 用法

```scheme
(define model (LogisticRegression :C 1.0 :solver 'lbfgs))
(model-fit model X y)
```
```

### 傻瓜式教学要求

| 模块 | 内容要求 |
|------|---------|
| 顶级 | 完整 ML 流程教程 |
| 预处理 | 公式+参数+何时用/不用+对比 |
| 指标 | 公式+速查+不同任务分类 |
| 模型选择 | CV 详解+搜索对比+学习曲线 |
| Pipeline | 数据泄露+step命名+调参 |
| 单模型 | 参数表+用法+最佳实践 |

### 示例输出标注

```scheme
(feature-importances model)
  →  [0.12 0.05 0.35 0.48]

(confusion-matrix y-test y-pred)
  →  [[10  0  0]
      [ 0  9  1]
      [ 0  0 10]]
```

---

## 四、函数级单例分解（metrics/preprocessing 模式）

当需要极致粒度时，对子模块内的每个函数/类也拆成独立目录。

### 目录结构

```
learn/metrics/
├── core.py              (聚合器: 导入 58 个单指标目录)
├── accuracy_score/      (注意: 目录名用下划线, 连字符 → 下划线)
│   ├── core.py          (注册 1 个函数: accuracy-score)
│   ├── __init__.py
│   └── demo.md
├── precision_score/
│   └── ...
├── r2_score/
│   └── ...
...
```

### 连字符→下划线陷阱

Scheme 名 `accuracy-score` 含连字符，Python 标识符不能含连字符。目录名必须用下划线：

```python
def sanitize(scheme_name: str) -> str:
    """Scheme 'accuracy-score' → Python 'accuracy_score'"""
    return scheme_name.replace('-', '_')
```

所有 import 路径、register 函数名都用 sanitized 版本：

```python
# metrics/accuracy_score/core.py
def register_accuracy_score(env):
    fn = getattr(sklearn.metrics, 'accuracy_score', None)
    env.define(Sym('accuracy-score'),  # ← Scheme 名保留连字符
               Prim('accuracy-score', lambda args, f=fn: call_metrics(f, args)))
```

### 子模块级聚合器

每个函数级目录存在后，子模块 `core.py` 变成纯聚合器：

```python
# metrics/core.py — 聚合器
from eval.cas.learn.metrics.accuracy_score.core import register_accuracy_score
from eval.cas.learn.metrics.precision_score.core import register_precision_score
# ... 58 个 import

def register_metrics(env):
    register_accuracy_score(env)
    register_precision_score(env)
    # ... 58 个调用
```

### 验证

```bash
python3 -c "from eval.cas.learn.metrics.accuracy_score.core import register_accuracy_score; print('OK')"
python3 -c "from eval.cas.learn.metrics.core import register_metrics; print('ALL OK')"
```

## 五、demo.md 傻瓜式教学标准

用户明确要求"傻瓜教材式"文档。每个单例 demo.md 必须包含以下要素：

### 单指标 demo.md 模板

```
# metrics/accuracy_score — accuracy-score

分类评估指标。衡量分类模型的预测质量。

## 用法

```scheme
(accuracy-score y_true y_pred)
(accuracy-score y_true y_pred :sample-weight weights)
```

## 参数

- `y_true`: 真实标签数组
- `y_pred`: 预测标签数组
- `:sample-weight`: 可选样本权重
- `:average` (多分类): macro/weighted/micro/binary

## 应用场景

- 二分类、多分类模型评估
- 模型选择中的评分函数

## 注意事项

1. 多分类必须指定 `:average` 参数
2. 不平衡数据上 accuracy 可能误导
3. 与同类指标对比使用更全面

## 对比表

| 指标 | 侧重点 | 不平衡鲁棒 |
|------|--------|:---------:|
| accuracy-score | 整体正确率 | ✗ |
| f1-score | 精确率+召回率平衡 | ✓(需average) |
| balanced-accuracy-score | 每类平均 | ✓ |

## 最佳实践

```scheme
; 二分类: 默认 binary
(accuracy-score y-test y-pred)

; 多分类: 用宏平均
(accuracy-score y-test y-pred :average 'macro)
```
```

### 单预处理 demo.md 模板

```
# preprocessing — StandardScaler

z-score 标准化。(x - mean) / std → 均值 0, 方差 1。

## 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `:with-mean` | `#t` | 是否中心化 |
| `:with-std` | `#t` | 是否缩放 |

## 用法

```scheme
(define scaler (StandardScaler))
(fit scaler X)
(define X-scaled (transform-fn scaler X))

(py-get scaler 'mean_)       → [5.84 3.06 ...]
(py-get scaler 'scale_)      → [0.83 0.43 ...]
```

## 何时用 / 何时不用

| 适用模型 | 不适用模型 |
|---------|-----------|
| SVM, KNN, PCA, MLP | 决策树, 随机森林, GBDT |
| LogisticRegression | 朴素贝叶斯 |
| 线性回归(非强制) | - |

## 对比

| Scaler | 公式 | 离群点影响 |
|--------|------|:---------:|
| StandardScaler | (x-μ)/σ | 大 |
| RobustScaler | (x-中位数)/IQR | 小 |
| MinMaxScaler | (x-min)/(max-min) | 大 |
| MaxAbsScaler | x/max\|x\| | 大 |
```

### 输出标注规范

代码示例后的预期输出用 `→` 标注，缩进 2 空格：

```scheme
(accuracy-score y-test y-pred)
  →  0.9667

(confusion-matrix y-test y-pred)
  →  [[10  0  0]
      [ 0  9  1]
      [ 0  0 10]]
```

多行结果保持缩进一致，矩阵/数组用 Scheme 数组写法。

### 单例 demo 必备要素检查清单

每个单例 demo.md 必须包含以下至少 3 项：

- [ ] **基本用法** — 最简可运行代码
- [ ] **参数说明** — 关键参数的作用和默认值
- [ ] **适用场景** — 什么情况下使用
- [ ] **注意事项** — 坑/限制/前提条件
- [ ] **对比表** — 与同类指标的优劣势比较
- [ ] **最佳实践** — 推荐用法/参数选择
