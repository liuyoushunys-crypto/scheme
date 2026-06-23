# 模块精细化分级方法论

## 信号：何时需要细化

用户说以下话时，当前颗粒度不够，需要立即拆分：

- "模块分级很不细致" / "不够细致"
- "请反复复盘,精准细化"
- "还有大量遗漏"（指分类遗漏）
- "循环3次"（要求多轮迭代）

## 三级结构标准

每个模块最终必须是三级或以上深度：

```
eval/cas/{模块}/
├── {子分类1}/               ← 二级：按功能/领域分组
│   ├── {原语1}/             ← 三级：单例原语
│   │   ├── core.py          ← register 函数
│   │   ├── __init__.py      ← 空文件
│   │   └── demo.md          ← 参数表+实参示例+注意事项
│   └── {原语2}/
├── {子分类2}/
│   └── ...
└── core.py                  ← 聚合器：从所有子分类/原语 import
└── __init__.py              ← 从 core.py 导出 register 函数
```

## 大平摊类别拆分清单

遇到以下情况必须拆分子分类：

| 信号 | 示例 | 方案 |
|------|------|------|
| 单分类 > 30 原语 | numpy/math 144 原语 | 拆为 trig/hyperbolic/exp_log/rounding/comparison/bitwise/float_ops/nan_ops/sum_stats/complex_ops/linear_algebra/special (12 个子类) |
| 单分类 > 20 条目但功能混杂 | learn/metrics 58 原语 | 拆为 classification/regression/clustering/pairwise |
| 所有原语都在模块根级 | statsmodels 24 个平铺 | 拆为 regression/discrete/tsa/stats_tests/utils |
| 分类名太泛 | "math" 包含不相关函数 | 按 numpy 源码组织拆分为数学子域 |

## 三周期精炼法

### Cycle 1: 拆分大平摊

1. 列出所有平铺原语 → 按功能聚类 → 建立映射表
2. 创建子分类目录 → `shutil.move(src, dst)` 移动原语目录
3. 重新生成聚合器 `core.py`：扫描实际 register 函数名（不能用固定命名假设）
4. 修复 `__init__.py` 链：每层 `__init__.py` 必须 `from .core import register_xxx`
5. 验证：`python3 -c "from eval.cas.{mod} import register_{mod}_primitives; print('OK')"`

### Cycle 2: 新建模块子分类

对新建模块（< 30 原语），确保每模块有 3-6 个子分类，每个子分类 2-5 个原语。

### Cycle 3: 修复导入链

移动目录后常见问题：
- 被移动的原语 `__init__.py` 包含过时的 `from eval.cas.{mod}.{old_path} import ...`
  → 修复：将过时 `__init__.py` 清空
- 聚合器 `core.py` 的 import 路径不匹配
  → 修复：用扫描脚本重新生成（`os.walk` + `re.search(r'def (register_\w+)\(', content)`）
- `__init__.py` 没有从 `core.py` 导出 register 函数
  → 修复：`__init__.py` 加一行 `from .core import register_xxx`

## 十周期精炼法（扩展版）

基础三周期 + 七轮精益求精填漏，适用于大规模模块（>50 原语）或多模块同时重构。

### Cycle 1-3（基础三周期）

同上方"三周期精炼法"章节。

### Cycle 4-6（添加聚合层demo）

对每个模块的 category 级目录（如 `vision/`, `scipy/`, `statsmodels/`）及子分类级（如 `scipy/linalg/`, `vision/basic/`）添加概述 demo.md。这些概述 demo 不是原语而是目录索引：

```markdown
# {category} — 模块名

## 子模块

| 模块 | 原语数 | 功能 |
|------|:------:|------|
| basic | 15 | 图像读写/缩放/色彩/绘制 |
| imgproc | 18 | 滤波/边缘/形态学 |
```

保持 5-15 行。不重复原语的参数细节。

### Cycle 7-8（增薄demo）

扫描 <10 行的 demo.md，确认是叶原语（有 core.py + register 函数）后增强到 15+ 行：

```python
thin_demos = []
for root, dirs, files in os.walk(cas_dir):
    if '__pycache__' in root: continue
    for f in files:
        if f == 'demo.md':
            fp = os.path.join(root, f)
            lines = open(fp).read().count('\\n') + 1
            if lines < 10:
                core_fp = os.path.join(root, 'core.py')
                if os.path.exists(core_fp):
                    with open(core_fp) as fh:
                        if re.search(r'def register_\\w+\\(', fh.read()):
                            thin_demos.append((fp, lines))
```

对每个薄 demo 加参数表（`## 参数`）、2-3 实参示例（代码块）、注意事项（`## 注意`）。

### Cycle 9-10（全量验证+修复）

1. **模块顶层 demo** — 确保每个模块根目录有 demo.md 概述该模块（numpy, scipy, vision 等）
2. **批量导入验证** — 对所有模块循环执行：

```bash
ok=0; fail=0
for mod in numpy scipy learn vision statsmodels pandas networkx mpmath uncertainties pint cvxpy galois numba pulp ortools matplotlib; do
  r=$(python3 -c "from eval.cas.${mod}.core import register_${mod}_primitives; print('OK')" 2>&1)
  if [ "$r" = "OK" ]; then ok=$((ok+1)); else fail=$((fail+1)); fi
done
echo "Pass: $ok, Fail: $fail"
```

3. **demo 覆盖率检查** — 确保无遗漏：

```python
missing = []
for root, dirs, files in os.walk(cas_dir):
    if '__pycache__' in root: continue
    if 'core.py' in files and 'demo.md' not in files:
        with open(os.path.join(root, 'core.py')) as f:
            c = f.read()
        if re.search(r'def register_\\w+\\(', c) or 'def register(' in c:
            missing.append(os.path.relpath(root, cas_dir))
```

4. **最终统计** — 打印覆盖率百分比 = demos/prims × 100。目标：100%。

## 递归遍历计数法

需要准确知道原语总数时，用递归扫描（不能估或猜）：

```python
import os, re

def count_primitives(start_dir):
    count = 0
    demos = 0
    for root, dirs, files in os.walk(start_dir):
        if '__pycache__' in root:
            continue
        if 'core.py' in files:
            with open(os.path.join(root, 'core.py')) as f:
                content = f.read()
            if re.search(r'def register_\w+\(', content) or 'def register(' in content:
                count += 1
                if os.path.exists(os.path.join(root, 'demo.md')):
                    demos += 1
    return count, demos
```

## 子分类命名约定

| 分类 | 命名 | 示例 |
|------|------|------|
| 三角函数 | `trig/` | sin, cos, tan, arcsin... |
| 双曲函数 | `hyperbolic/` | sinh, cosh, tanh... |
| 指数对数 | `exp_log/` | exp, log, sqrt, power... |
| 取整 | `rounding/` | round, floor, ceil, trunc... |
| 比较逻辑 | `comparison/` | greater, less, equal, logical_and... |
| 位运算 | `bitwise/` | bitwise_and, bitwise_or, invert... |
| 浮点 | `float_ops/` | isnan, isinf, copysign, fmax... |
| NaN 安全 | `nan_ops/` | nansum, nanmean, nanprod... |
| 聚合统计 | `sum_stats/` | sum, mean, std, var, cumsum... |
| 复数 | `complex_ops/` | real, imag, conj, angle... |
| 线性代数 | `linear_algebra/` | dot, matmul, einsum, cross... |
| 回归 | `regression/` | OLS, WLS, GLM |
| 离散选择 | `discrete/` | Logit, Probit, Poisson, MNLogit |
| 时间序列 | `tsa/` | ARIMA, SARIMAX, adfuller, acf |
| 统计检验 | `stats_tests/` | anova_lm, multipletests, mcnemar |
| IO | `io/` | read_csv, read_excel, to_csv |
| 变形 | `reshape/` | pivot_table, melt, cut, get_dummies |
| 连接 | `join/` | merge, concat |
| 时间序列 | `time_series/` | to_datetime, date_range |
| 工具 | `utils/` | factorize, unique, add_constant |
