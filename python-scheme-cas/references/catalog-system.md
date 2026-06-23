# 科学计算包目录系统 (eval/eval_py_catalog.py)

## 架构

`(catalog)` 提供三层级浏览系统，覆盖 29 包 × 9 领域。

## 数据库结构

### TOP_CATALOG — 29 个已收录包

每个条目: `(显示名, 导入名, 一句话简介)`

涵盖:
- 科学计算: scipy, numpy, mpmath, galois
- 统计/建模: statsmodels, patsy, scikit-learn, pandas
- 优化: cvxpy, osqp, scs, highspy, ortools
- 符号数学: sympy
- NLP/ML: transformers, onnxruntime, faster-whisper
- 绘图/视觉: matplotlib, Pillow, opencv
- 图论: networkx
- 物理/单位: pint, uncertainties
- 数据/工具: SQLAlchemy, beautifulsoup4, lxml, joblib, pydantic, sounddevice

### curated 数据库

每个大包有精选函数列表（名称 + 中文说明）:
- scipy: 9 子模块 × 8-27 函数 = ~150 条
- statsmodels: 23 项
- cvxpy: 14 项
- pandas: 14 项
- transformers: 10 项
- patsy: 2 项
- joblib: 5 项
- SQLAlchemy: 4 项

### 显示逻辑

```
(catalog)                    → 顶级（9 领域）
(catalog 'scipy)             → 包级（子模块概览）
(catalog 'scipy.optimize)    → 子模块级（精选函数）
(catalog "关键词")            → 搜索（跨全部 curated 库）
```

未知包自动 fallback 到 `importlib` + `dir()` 动态列出。

### 搜索范围

`_search()` 遍历全部 curated 数据库的函数名、说明和来源包名。未匹配时返回友好提示。最大显示 30 条。

## 添加新包

1. 在 `TOP_CATALOG` 中添加条目
2. 在 domains 中添加领域分组
3. （可选）在 curated 数据库中添加函数列表
4. 在 `_show_module()` 中添加对应 `if modpath == 'xxx':` 分支
5. 在 `_search()` 中添加 `for fn_name, desc in XXX_HIGHLIGHTS:` 循环

## 注意事项

- `_module_version()` 通过 `importlib.import_module` 获取版本
- `_get_pkg_short()` 维护显示名→导入名的映射（如 `Pillow→PIL`, `opencv→cv2`）
- transformers 无 PyTorch 时也可显示目录，仅加载分词器配置
