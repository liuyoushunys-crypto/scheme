"""
viz — CAS 可视化

对标 Maxima 的绘图功能：
  (plot expr var low high)       → 2D 函数曲线
  (plot-param fx fy var low high) → 参数曲线
  (plot3d expr var1 low1 high1 var2 low2 high2) → 3D 曲面
"""
from core.schemevalue import Prim, Str


def _plot(expr, var, low, high):
    """2D 函数绘图"""
    return Str(f"<plot: {expr} from {low} to {high}>")


def _plot_param(fx, fy, var, low, high):
    """参数曲线绘图"""
    return Str(f"<plot-param: {fx} {fy} from {low} to {high}>")


def _plot3d(expr, var1, low1, high1, var2, low2, high2):
    """3D 曲面绘图"""
    return Str(f"<plot3d: {expr}>")


def register_viz_primitives(env):
    """注册绘图原语（匹配文档 API 名）"""
    env.define("plot", Prim("plot", _plot))
    env.define("plot-param", Prim("plot-param", _plot_param))
    env.define("plot3d", Prim("plot3d", _plot3d))


register_primitives = register_viz_primitives
