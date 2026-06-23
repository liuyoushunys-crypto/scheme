"""
PyPI 数学生态友好展示 — 一站浏览所有可用包及用法。

使用：
  (ecosystem)              → 按分类展示全部 19+ 个数学包
  (ecosystem 'category)    → 只看某个分类
  (ecosystem 'package)     → 只看某个包详情
  (ecosystem \"keyword\")   → 搜索关键词
"""

from typing import List
from core.schemevalue import *

# ==================== 生态数据库 ====================

ECOSYSTEM = [
    # (分类, 包名, 导入名, 版本, 简介, 示例)
    
    ("数值计算", "numpy", "numpy", "2.4.3",
     "核心数值计算库：数组、矩阵运算、线性代数、随机数",
     "(import numpy)\n"
     "(define a (numpy.array (list 1 2 3)))\n"
     "(numpy.linspace 0 1 5)         → (0.0 0.25 0.5 0.75 1.0)\n"
     "(numpy.random.rand 3 3)         → 3×3 随机矩阵"),
    
    ("数值计算", "scipy", "scipy", "1.17.1",
     "科学计算：优化、插值、信号、统计、稀疏矩阵",
     "(import scipy)\n"
     "(scipy.optimize.minimize ...)   → 数值优化\n"
     "(scipy.integrate.quad f 0 1)    → 数值积分 (已在 find-root/numerical-integrate 中包装)\n"
     "(scipy.interpolate.interp1d ...) → 插值"),
    
    ("数值计算", "mpmath", "mpmath", "1.3.0",
     "任意精度浮点运算（sympy 底层依赖）",
     "(import mpmath)\n"
     "(mpmath.mp.dps 50)              → 设 50 位精度\n"
     "(mpmath.pi)                     → π 到 50 位"),
    
    ("数值计算", "numba", "numba", "0.65.1",
     "JIT 编译器：数值循环加速 100×",
     "(import numba)\n"
     ";; 配合 numpy 使用，自动加速"),
    
    ("符号计算", "sympy", "sympy", "1.14.0",
     "符号数学：微积分、代数、方程、ODE、数论（CAS 核心）",
     "(import sympy)\n"
     "(define x (sympy.Symbol 'x))\n"
     "(sympy.diff (expt x 3) x)       → 3*x² (已包装为 diff)\n"
     "(sympy.integrate (expt x 2) x)  → x³/3 (已包装为 integrate)\n"
     "(sympy.series (sin x) x 0 5)    → 泰勒展开 (已包装为 series)"),
    
    ("符号计算", "symengine", "symengine", "0.14.1",
     "sympy 兼容的 C++ 引擎，速度 10-100×",
     "(import symengine)\n"
     "(define x (symengine.Symbol 'x))\n"
     "(use-engine 'symengine)          → 切换引擎\n"
     "(engine-info)                    → 查看引擎状态"),
    
    ("符号计算", "galois", "galois", "0.4.11",
     "有限域 (GF(2^8), GF(p))：编码、密码",
     "(import galois)\n"
     "(define GF (galois.GF 2 8))      → GF(2⁸)\n"
     "GF.primitive_element"),
    
    ("数据科学", "pandas", "pandas", "3.0.3",
     "表格数据处理：DataFrame、CSV 读写、统计",
     "(import pandas)\n"
     "(define df (pandas.DataFrame (list ...) :columns (list 'a 'b)))\n"
     "(pandas.read_csv \"data.csv\")"),
    
    ("数据科学", "statsmodels", "statsmodels", "0.14.6",
     "统计建模：回归、时间序列、假设检验",
     "(import statsmodels)\n"
     "(statsmodels.api.OLS y X)        → 线性回归"),
    
    ("数据科学", "scikit-learn", "sklearn", "1.9.0",
     "机器学习：分类、聚类、降维、回归",
     "(import sklearn)\n"
     "(sklearn.linear_model.LinearRegression)"),
    
    ("优化", "cvxpy", "cvxpy", "1.9.1",
     "凸优化建模：LP、QP、SOCP、SDP",
     "(import cvxpy)\n"
     "(define x (cvxpy.Variable 2))\n"
     "(define prob (cvxpy.Problem (cvxpy.Minimize ...) ...))"),
    
    ("优化", "pulp", "pulp", "3.3.2",
     "线性规划：LP、MILP",
     "(import pulp)\n"
     "(pulp.LpProblem \"test\" pulp.LpMinimize)"),
    
    ("优化", "ortools", "ortools", "9.15.6755",
     "Google 运筹优化：约束规划、VRP、调度",
     "(import ortools)\n"
     "(import ortools.sat.python.cp_model)"),
    
    ("图论", "networkx", "networkx", "3.6.1",
     "图与网络：最短路、中心性、社区检测、图绘制",
     "(use-graph)                       → 一键导入 + 绑定\n"
     "(define g (Graph))\n"
     "(add-edge g 1 2 :weight 5)\n"
     "(shortest-path g 1 3)            → 最短路"),
    
    ("绘图", "matplotlib", "matplotlib", "3.10.9",
     "出版级 2D/3D 绘图（CAS 可视化后端）",
     "(plot #{x^2} x -5 5 :title \"抛物线\" :grid #t)\n"
     "(plot-param #{cos(t)} #{sin(t)} t 0 6.28)\n"
     "(plot3d #{x^2 + y^2} x -2 2 y -2 2)"),
    
    ("绘图", "Pillow", "PIL", "12.2.0",
     "图像处理：打开、变换、滤镜",
     "(import PIL.Image)\n"
     "(PIL.Image.open \"photo.jpg\")"),
    
    ("绘图", "opencv-python", "cv2", "4.13.0",
     "计算机视觉：摄像头、特征检测、深度学习",
     "(import cv2)\n"
     "(cv2.imread \"image.jpg\")"),
    
    ("物理/单位", "pint", "pint", "0.25.3",
     "物理单位：量纲分析、单位转换",
     "(import pint)\n"
     "(define ureg (pint.UnitRegistry))\n"
     "((. ureg 'meter) * 10)"),
    
    ("物理/单位", "uncertainties", "uncertainties", "3.2.3",
     "误差传播：自动计算测量不确定度",
     "(import uncertainties)\n"
     "(define u (uncertainties.ufloat 3.14 0.01))\n"
     "(+ u 1)                          → 自动误差传播\n"
     "(sin u)                           → 自动误差传播"),
]

_CATEGORY_ORDER = [
    "数值计算", "符号计算", "数据科学", "优化",
    "图论", "绘图", "物理/单位",
]


def _fmt(text: str, width: int) -> str:
    """填充到指定宽度"""
    t = str(text)
    if len(t) >= width:
        return t[:width - 1] + '…'
    return t + ' ' * (width - len(t))


def _show_all() -> str:
    """显示全部生态"""
    lines = []
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append("║      PyPI 数学生态系统 — 19 个包已就绪                    ║")
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    lines.append("")
    
    for cat in _CATEGORY_ORDER:
        entries = [e for e in ECOSYSTEM if e[0] == cat]
        if not entries:
            continue
        
        lines.append(f"  ┌─ {cat} ──────────────────────────────────────────┐")
        for _, pkg, import_name, ver, desc, _ in entries:
            lines.append(f"  │ ✅ {pkg:15s} v{ver:8s}  {desc}")
        lines.append(f"  └──────────────────────────────────────────────────┘")
        lines.append("")
    
    lines.append("  输入 (ecosystem '包名)  查看详情和示例")
    lines.append("  输入 (ecosystem \"关键词\") 搜索")
    return '\n'.join(lines)


def _show_package(name: str) -> str:
    """显示单个包的详情"""
    name_lower = name.lower()
    for cat, pkg, import_name, ver, desc, example in ECOSYSTEM:
        if pkg.lower() == name_lower or import_name.lower() == name_lower:
            lines = []
            lines.append(f"── {pkg} (v{ver}) ──")
            lines.append(f"  分类: {cat}")
            lines.append(f"  简介: {desc}")
            lines.append(f"  导入: (import {import_name})")
            lines.append(f"")
            lines.append(f"  示例:")
            for ex_line in example.split('\n'):
                lines.append(f"    {ex_line}")
            return '\n'.join(lines)
    
    return f"未找到包 '{name}'。输入 (ecosystem) 浏览全部可用包。"


def _search(keyword: str) -> str:
    """搜索包"""
    kw = keyword.lower()
    matches = []
    for cat, pkg, import_name, ver, desc, example in ECOSYSTEM:
        if (kw in pkg.lower() or kw in import_name.lower() 
            or kw in cat.lower() or kw in desc.lower()):
            matches.append((cat, pkg, import_name, ver, desc))
    
    if not matches:
        return f"未找到包含 '{keyword}' 的包。"
    
    lines = [f"搜索 \"{keyword}\" 找到 {len(matches)} 个包：", ""]
    for cat, pkg, import_name, ver, desc in matches:
        lines.append(f"  ✅ {pkg:15s} [{cat:6s}]  {desc}")
    return '\n'.join(lines)


# ==================== Scheme Prim ====================

def cas_ecosystem(args: List[SchemeValue]) -> SchemeValue:
    """
    (ecosystem)              → 分类浏览全部
    (ecosystem 'numpy)       → 查看 numpy 详情
    (ecosystem \"积分\")      → 搜索
    """
    if len(args) == 0:
        return Str(list(_show_all()))
    
    first = args[0]
    if isinstance(first, Sym):
        return Str(list(_show_package(first.name)))
    
    if isinstance(first, Str):
        return Str(list(_search(first.get_str())))
    
    return Str(list("ecosystem: 参数应为包名(符号)、关键词(字符串)或空"))


# ==================== 注册 ====================

def register_ecosystem_primitives(env: 'Env') -> None:
    """注册生态展示 Prim"""
    env.define("ecosystem", Prim("ecosystem", cas_ecosystem))
