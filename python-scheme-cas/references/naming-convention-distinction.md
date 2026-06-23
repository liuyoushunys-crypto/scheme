# 命名约定：PyPI 包 vs 内部 CAS 模块

## 核心原则（2026-06-23 确立）

命名规则 `eval/cas/xxx/yyy/zzz.py` + `env.define("xxx.yyy.zzz")` **只适用于 PyPI 生态系统包**（numpy, scipy, sympy, pandas, networkx, mpmath 等）。

**内部 CAS 模块不遵循此规则** — 它们保持原有的扁平 Scheme 名（`diff`, `expand`, `integrate`, `factor`, `help`, `assume` 等）。

## 适用 vs 不适用

| 类别 | 示例包 | env.define 命名 | 目录结构 |
|------|--------|----------------|----------|
| ✅ PyPI 桥接 | numpy, scipy, sympy | `"numpy.linalg.solve"` | `eval/cas/numpy/linalg/core.py` |
| ❌ 内部 CAS | core, info, sugar, assume | `"diff"`, `"expand"` (扁平) | `eval/cas/core/calculus.py` (扁平或包) |
| ❌ 内部 CAS | engine, bridge, parse | `"use-engine"`, `"Graph"` (扁平) | `eval/cas/engine.py` (扁平) |

## 映射规则（仅 PyPI）

```
site-packages/xxx/yyy/zzz.py  →  eval/cas/xxx/yyy/zzz.py + zzz.md
Python 模块 xxx.yyy.zzz       →  env.define("xxx.yyy.zzz", ...)
```

但生成粒度是 **模块聚合级**：每个包/子模块生成一个 `core.py`，聚合注册其下所有函数，而非每个函数一个独立的 `.py` 文件。

```
eval/cas/numpy/
  __init__.py          → """numpy"""
  core.py              → 注册顶层函数
  demo.md              → 文档
  linalg/
    __init__.py        → """numpy.linalg"""
    core.py            → 注册 numpy.linalg 函数
    demo.md            → 文档
```

## 历史原因

之前生成脚本错误地将所有模块（含内部 CAS）按 PyPI 规则重命名，导致 `env.define("core.algebra.expand")`。这是错误的——内部 CAS 的 Scheme API 保持简洁的扁平名。

## 常见陷阱

1. `primitives.py` 中 import 的 `register_numpy_primitives` 等 PyPI 桥接函数在未生成时须用 `try/except ModuleNotFoundError` 包裹。
2. 生成脚本（`_rebuild_final.py`, `_agg_final.py` 等）遗留的破坏性代码必须修复：literal `\n`、缩进错误、空 `__init__.py`、`register_unknown` 占位名。
