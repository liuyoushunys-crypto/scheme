# PyPI 数学生态 — 快速参考

`(ecosystem)` — 交互式分类浏览（19 包，带版本和示例）
`(ecosystem 'pkg)` — 查看详情
`(ecosystem "关键词")` — 搜索

## 分类一览

### 数值计算
| 包 | 导入 | 用途 |
|----|------|------|
| numpy 2.4.3 | `(import numpy)` | 数组/矩阵/线性代数/随机数 |
| scipy 1.17.1 | `(import scipy)` | 优化/插值/信号/统计/稀疏矩阵 |
| mpmath 1.3.0 | `(import mpmath)` | 任意精度浮点 |
| numba 0.65.1 | `(import numba)` | JIT 加速数值循环 |

### 符号计算
| 包 | 导入 | 用途 |
|----|------|------|
| sympy 1.14.0 | `(import sympy)` | 符号数学（CAS 核心，60+ 原生函数） |
| symengine 0.14.1 | `(import symengine)` | sympy 兼容 C++ 引擎，10-100× 快 |
| galois 0.4.11 | `(import galois)` | 有限域 GF(p)/GF(2ⁿ) |

### 数据科学
| 包 | 导入 | 用途 |
|----|------|------|
| pandas 3.0.3 | `(import pandas)` | DataFrame/CSV/统计 |
| statsmodels 0.14.6 | `(import statsmodels)` | 回归/时间序列/检验 |
| scikit-learn 1.9.0 | `(import sklearn)` | 分类/聚类/降维 |

### 优化
| 包 | 导入 | 用途 |
|----|------|------|
| cvxpy 1.9.1 | `(import cvxpy)` | 凸优化 LP/QP/SOCP/SDP |
| pulp 3.3.2 | `(import pulp)` | 线性规划 MILP |
| ortools 9.15.6755 | `(import ortools)` | 约束规划/VRP/调度 |

### 图论
| 包 | 导入 | 用途 |
|----|------|------|
| networkx 3.6.1 | `(use-graph)` | 图/网络/最短路/中心性/社区 |

### 绘图
| 包 | 导入 | 用途 |
|----|------|------|
| matplotlib 3.10.9 | `(plot ...)` | 出版级 2D/3D 绘图（原生包装） |
| Pillow 12.2.0 | `(import PIL.Image)` | 图像处理 |
| opencv-python 4.13.0 | `(import cv2)` | 计算机视觉 |

### 物理/单位
| 包 | 导入 | 用途 |
|----|------|------|
| pint 0.25.3 | `(import pint)` | 物理单位/量纲 |
| uncertainties 3.2.3 | `(import uncertainties)` | 误差传播 |

## 文件位置

- 桥接模块: `eval/eval_py_bridge.py` (use-graph/use-units/use-tensor)
- 生态展示: `eval/eval_py_ecosystem.py` (ecosystem)
- 注册入口: `primitives/primitives.py` → `register_all()`
