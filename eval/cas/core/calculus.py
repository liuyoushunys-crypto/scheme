"""
calculus — 微积分: diff/integrate/limit/series/taylor/summation/product/grad/div/curl/hessian/jacobian

对标 Maxima 的微积分功能。

使用方式：
  (integrate expr var)                → 不定积分
  (integrate expr var a b)            → 定积分
  (diff expr var)                     → 一阶导数
  (diff expr var n)                   → n 阶导数
  (limit expr var pt)                 → 极限
  (limit expr var pt dir)             → 方向极限
  (series expr var pt n)              → 级数展开（含余项）
  (taylor expr var pt n)              → 泰勒展开（去除余项）
  (summation expr (var a b))          → 求和
  (product expr (var a b))            → 求积
  (grad expr var ...)                 → 梯度
  (div field var ...)                 → 散度
  (curl field var ...)                → 旋度
  (hessian expr var ...)              → Hessian 矩阵
  (jacobian funcs var ...)            → Jacobian 矩阵
"""
from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


# ==================== 内部工具 ====================

def _sympy():
    """Get engine proxy (auto-fallback symengine→sympy)."""
    from eval.cas.engine import get_engine
    return get_engine()


def _unwrap1(args):
    """解包第一个参数。"""
    return unwrap_python_value(args[0])


def _unwrap(args):
    """解包所有参数。"""
    return [unwrap_python_value(a) for a in args]


# ==================== 微分 ====================

def cas_diff(args):
    """
    (diff expr var [n]) — 求导。

    示例：
      (diff #{x^3} x)       →  3*x^2
      (diff #{x^3} x 2)     →  6*x
    """
    if len(args) < 2:
        raise Exception("diff: 需要 (diff expr var) 或 (diff expr var n)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var = sp.Symbol(py_args[1]) if isinstance(py_args[1], str) else sp.sympify(py_args[1])
    if len(py_args) >= 3:
        n = int(py_args[2])
        result = sp.diff(expr, var, n)
    else:
        result = sp.diff(expr, var)
    return wrap_python_value(result)


# ==================== 积分 ====================

def cas_integrate(args):
    """
    (integrate expr var [a b]) — 不定/定积分。

    示例：
      (integrate #{x^2} x)               →  x^3/3
      (integrate #{x^2} x 0 1)           →  1/3
    """
    if len(args) < 2:
        raise Exception("integrate: 需要 (integrate expr var) 或 (integrate expr var a b)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var = sp.Symbol(py_args[1]) if isinstance(py_args[1], str) else sp.sympify(py_args[1])
    match len(py_args):
        case 2:
            # 不定积分
            result = sp.integrate(expr, var)
        case 4:
            # 定积分
            a = py_args[2]
            b = py_args[3]
            result = sp.integrate(expr, (var, a, b))
        case _:
            raise Exception("integrate: 需要 2 或 4 个参数")
    return wrap_python_value(result)


# ==================== 极限 ====================

def cas_limit(args):
    """
    (limit expr var pt [dir]) — 求极限。

    示例：
      (limit #{1/x} x 0)          →  ±oo (根据方向)
      (limit #{1/x} x 0 '+')      →  +oo
      (limit #{1/x} x 0 '-')      →  -oo
    """
    if len(args) < 3:
        raise Exception("limit: 需要 (limit expr var pt) 或 (limit expr var pt dir)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var = sp.Symbol(py_args[1]) if isinstance(py_args[1], str) else sp.sympify(py_args[1])
    pt = py_args[2]
    if len(py_args) >= 4:
        dir_ = py_args[3]
        result = sp.limit(expr, var, pt, dir_)
    else:
        result = sp.limit(expr, var, pt)
    return wrap_python_value(result)


# ==================== 级数展开 ====================

def cas_series(args):
    """
    (series expr var pt n) — 级数展开（含余项 O 项）。

    示例：
      (series #{exp(x)} x 0 5)  →  1 + x + x^2/2 + x^3/6 + x^4/24 + O(x^5)
    """
    if len(args) < 4:
        raise Exception("series: 需要 (series expr var pt n)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var = sp.Symbol(py_args[1]) if isinstance(py_args[1], str) else sp.sympify(py_args[1])
    pt = py_args[2]
    n = int(py_args[3])
    result = sp.series(expr, var, pt, n)
    return wrap_python_value(result)


def cas_taylor(args):
    """
    (taylor expr var pt n) — 泰勒展开（去除余项）。

    示例：
      (taylor #{exp(x)} x 0 5)  →  1 + x + x^2/2 + x^3/6 + x^4/24
    """
    if len(args) < 4:
        raise Exception("taylor: 需要 (taylor expr var pt n)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var = sp.Symbol(py_args[1]) if isinstance(py_args[1], str) else sp.sympify(py_args[1])
    pt = py_args[2]
    n = int(py_args[3])
    series = sp.series(expr, var, pt, n)
    result = sp.expand(series.removeO())
    return wrap_python_value(result)


# ==================== 求和与求积 ====================

def cas_sum(args):
    """
    (summation expr (var a b)) — 求和。

    示例：
      (summation #{k} (k 1 10))  →  55
      (summation #{k^2} (k 1 n))  →  n*(n+1)*(2*n+1)/6
    """
    if len(args) < 2:
        raise Exception("summation: 需要 (summation expr (var a b))")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    # py_args[1] 是一个列表/元组 (var, a, b)
    var_spec = py_args[1]
    if not isinstance(var_spec, (list, tuple)) or len(var_spec) != 3:
        raise Exception("summation: 需要 (var a b) 作为第二个参数")
    var = sp.Symbol(var_spec[0]) if isinstance(var_spec[0], str) else sp.sympify(var_spec[0])
    a = var_spec[1]
    b = var_spec[2]
    result = sp.summation(expr, (var, a, b))
    return wrap_python_value(result)


def cas_product(args):
    """
    (product expr (var a b)) — 求积。

    示例：
      (product #{k} (k 1 5))  →  120
    """
    if len(args) < 2:
        raise Exception("product: 需要 (product expr (var a b))")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    var_spec = py_args[1]
    if not isinstance(var_spec, (list, tuple)) or len(var_spec) != 3:
        raise Exception("product: 需要 (var a b) 作为第二个参数")
    var = sp.Symbol(var_spec[0]) if isinstance(var_spec[0], str) else sp.sympify(var_spec[0])
    a = var_spec[1]
    b = var_spec[2]
    result = sp.product(expr, (var, a, b))
    return wrap_python_value(result)


# ==================== 向量微积分 ====================

def cas_gradient(args):
    """
    (grad expr var ...) — 梯度。

    示例：
      (grad #{x^2 + y^2} x y)  →  [2*x, 2*y]
    """
    if len(args) < 2:
        raise Exception("grad: 需要 (grad expr var ...)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    vars_list = [sp.Symbol(v) if isinstance(v, str) else sp.sympify(v) for v in py_args[1:]]
    result = sp.derive_by_array(expr, vars_list)
    return wrap_python_value(result)


def cas_divergence(args):
    """
    (div field var ...) — 散度。

    示例：
      (div #[x, y, z] x y z)  →  3
    """
    if len(args) < 2:
        raise Exception("div: 需要 (div field var ...)")
    from sympy.vector import divergence as sp_divergence
    sp = _sympy()
    py_args = _unwrap(args)
    field = py_args[0]
    vars_list = [sp.Symbol(v) if isinstance(v, str) else sp.sympify(v) for v in py_args[1:]]
    result = sp_divergence(field, vars_list)
    return wrap_python_value(result)


def cas_curl(args):
    """
    (curl field var ...) — 旋度。

    示例：
      (curl #[y, -x, 0] x y z)  →  [0, 0, -2]
    """
    if len(args) < 2:
        raise Exception("curl: 需要 (curl field var ...)")
    from sympy.vector import curl as sp_curl
    sp = _sympy()
    py_args = _unwrap(args)
    field = py_args[0]
    vars_list = [sp.Symbol(v) if isinstance(v, str) else sp.sympify(v) for v in py_args[1:]]
    result = sp_curl(field, vars_list)
    return wrap_python_value(result)


def cas_hessian(args):
    """
    (hessian expr var ...) — Hessian 矩阵。

    示例：
      (hessian #{x^2 + y^2} x y)  →  [[2, 0], [0, 2]]
    """
    if len(args) < 2:
        raise Exception("hessian: 需要 (hessian expr var ...)")
    sp = _sympy()
    py_args = _unwrap(args)
    expr = sp.sympify(py_args[0])
    vars_list = [sp.Symbol(v) if isinstance(v, str) else sp.sympify(v) for v in py_args[1:]]
    result = sp.hessian(expr, vars_list)
    return wrap_python_value(result)


def cas_jacobian(args):
    """
    (jacobian funcs var ...) — Jacobian 矩阵。

    示例：
      (jacobian #[x*y, x^2] x y)  →  [[y, x], [2*x, 0]]
    """
    if len(args) < 2:
        raise Exception("jacobian: 需要 (jacobian funcs var ...)")
    sp = _sympy()
    py_args = _unwrap(args)
    funcs = py_args[0]
    if isinstance(funcs, (list, tuple)):
        funcs = sp.Matrix(funcs)
    else:
        funcs = sp.sympify(funcs)
    vars_list = [sp.Symbol(v) if isinstance(v, str) else sp.sympify(v) for v in py_args[1:]]
    # Matrix.jacobian is the canonical method in sympy
    result = funcs.jacobian(vars_list)
    return wrap_python_value(result)


# ==================== 注册 ====================

def register_calculus_primitives(env):
    """注册微积分原语。"""
    prims = [
        ("integrate", cas_integrate),
        ("diff", cas_diff),
        ("limit", cas_limit),
        ("series", cas_series),
        ("taylor", cas_taylor),
        ("summation", cas_sum),
        ("product", cas_product),
        ("grad", cas_gradient),
        ("div", cas_divergence),
        ("curl", cas_curl),
        ("hessian", cas_hessian),
        ("jacobian", cas_jacobian),
    ]
    for name, func in prims:
        env.define(name, Prim(name, func))

register_primitives = register_calculus_primitives