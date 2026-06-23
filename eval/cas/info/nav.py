"""
info/nav — 导航系统

提供 (nav) 浏览模块层级结构。
"""
from core.schemevalue import Prim, Str


def cas_nav(*args):
    """导航 CAS 模块层级"""
    modules = [
        ("core",        "核心数学: algebra, calculus, linear, special, output"),
        ("assume",      "假设系统: assume, unassume, refine, ask"),
        ("bridge",      "图/数组/单位封装: Graph, DiGraph, Array"),
        ("engine",      "引擎管理: use-engine, engine-info"),
        ("entry",       "入口: use-cas 一键加载"),
        ("info",        "帮助/导航: help, apropos, nav, catalog"),
        ("numerical",   "数值计算: numerical integration, approximation"),
        ("parse",       "多格式解析: parse, parse-latex, parse-mathematica"),
        ("pattern",     "模式匹配: match, defrule, rewrite"),
        ("sugar",       "语法糖: λ, ->, ->>, for, str"),
        ("tensor",      "张量代数: index, tensor, contract"),
        ("viz",         "可视化: visualize, plot-2d, plot-3d"),
        ("numpy",       "numpy 集成"),
        ("learn",       "机器学习集成"),
    ]
    lines = ["╔══════════════════════════════════════════╗"]
    lines.append("║         CAS 模块导航                    ║")
    lines.append("╚══════════════════════════════════════════╝")
    for name, desc in modules:
        lines.append(f"  {name:12s} {desc}")
    return Str("\n".join(lines))


def register_nav_primitives(env):
    """Register nav primitives."""
    env.define("nav", Prim("nav", cas_nav))


register_primitives = register_nav_primitives