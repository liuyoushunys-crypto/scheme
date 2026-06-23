"""
CAS 数值方法 — 对标 Maxima find_root/quad_qags/romberg。

使用：
  (find-root f a b)                    → 在 [a,b] 求根（Brent 法）
  (find-root f a b :method 'bisect)    → 指定方法
  (numerical-integrate f a b)          → 数值积分
  (numerical-derivative f x)           → 数值微分
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _unwrap1(args):
    return unwrap_python_value(args[0])


def _unwrap(args):
    return [unwrap_python_value(a) for a in args]


def _parse_kwargs(args: List, offset: int = 0) -> dict:
    kwargs = {}
    i = offset
    while i < len(args):
        arg = args[i]
        if isinstance(arg, Sym) and arg.name.startswith(':'):
            key = arg.name[1:]
            if i + 1 >= len(args):
                raise Exception(f"数值: 缺少关键词 :{key} 的值")
            i += 1
            kwargs[key] = unwrap_python_value(args[i])
        i += 1
    return kwargs


def _to_callable(f, var_name='x'):
    """将 Scheme 值转为 Python 可调用对象"""
    from core.tail_call import apply_tail
    from eval.eval_scheme import eval_scheme
    import numpy as np
    import sympy
    
    # 从 PythonObject 中提取原生对象
    py_obj = f.obj if isinstance(f, PythonObject) else f
    
    # Python 原生可调用对象
    if callable(py_obj):
        return py_obj
    
    # sympy 表达式 → lambdify
    try:
        if hasattr(py_obj, 'free_symbols'):
            symbols = list(py_obj.free_symbols)
            if symbols:
                f_lambda = sympy.lambdify(symbols, py_obj, 'numpy')
                if len(symbols) == 1:
                    return lambda x: float(f_lambda(np.array([x]))[0]) if hasattr(x, '__len__') else float(f_lambda(x))
                return lambda x: float(f_lambda(x))
    except (AttributeError, TypeError):
        pass
    
    # Scheme closure → wrapper
    if isinstance(f, Closure):
        def wrapped(x):
            result = apply_tail(f, [wrap_python_value(float(x))], f.env)
            if isinstance(result, TailCallSentinel):
                result = eval_scheme(result.expr, result.env)
            if isinstance(result, PythonObject):
                return float(result.obj)
            return float(unwrap_python_value(result))
        return wrapped
    
    # 数值（转为常数函数）
    if isinstance(f, (int, float)):
        return lambda x: float(f)
    
    raise Exception(f"数值: 不可调用的参数 {type(f).__name__}")


def _try_sympy_callable(expr, var_name='x'):
    """将 sympy 表达式转为可调用函数"""
    import sympy, numpy as np
    if isinstance(expr, str):
        expr = sympy.sympify(expr)
    f_lambda = sympy.lambdify(sympy.Symbol(var_name), expr, 'numpy')
    return lambda x: float(f_lambda(np.array([x]))[0]) if hasattr(x, '__len__') else float(f_lambda(x))


# ==================== 数值求根 ====================

def cas_find_root(args: List) -> SchemeValue:
    """
    (find-root f a b)              → 在 [a,b] 求根
    (find-root f a b :method 'bisect)
    
    方法可选: 'bisect 'brentq 'newton 'ridder (默认 'brentq)
    """
    if len(args) < 3:
        raise Exception("find-root: 需要 (find-root f a b [:method ...])")
    
    pos_args = []
    kw_offset = len(args)
    for i, arg in enumerate(args):
        if isinstance(arg, Sym) and arg.name.startswith(':'):
            kw_offset = i
            break
        pos_args.append(unwrap_python_value(arg))
    
    kwargs = _parse_kwargs(args, kw_offset)
    method = kwargs.get('method', 'brentq')
    
    f_raw = pos_args[0]
    a, b = pos_args[1], pos_args[2]
    
    # Convert f to callable
    f = _to_callable(f_raw)
    
    from scipy import optimize
    try:
        if method == 'bisect':
            result = optimize.bisect(f, a, b)
        elif method == 'newton':
            result = optimize.newton(f, (a + b) / 2)
        elif method == 'ridder':
            result = optimize.ridder(f, a, b)
        else:  # brentq (default)
            result = optimize.brentq(f, a, b)
    except Exception as e:
        raise Exception(f"find-root error: {e}")
    
    return wrap_python_value(result)


# ==================== 数值积分 ====================

def cas_numerical_integrate(args: List) -> SchemeValue:
    """
    (numerical-integrate f a b)    → 自适应数值积分 (quad)
    """
    if len(args) < 3:
        raise Exception("numerical-integrate: 需要 (numerical-integrate f a b)")
    
    pos_args = []
    kw_offset = len(args)
    for i, arg in enumerate(args):
        if isinstance(arg, Sym) and arg.name.startswith(':'):
            kw_offset = i
            break
        pos_args.append(unwrap_python_value(arg))
    
    f_raw = pos_args[0]
    a, b = pos_args[1], pos_args[2]
    
    f = _to_callable(f_raw)
    
    from scipy import integrate
    try:
        result, error = integrate.quad(f, a, b)
    except Exception as e:
        raise Exception(f"numerical-integrate error: {e}")
    
    return wrap_python_value(result)


# ==================== 数值微分 ====================

def cas_numerical_derivative(args: List) -> SchemeValue:
    """
    (numerical-derivative f x)     → 在 x 处的数值导数
    """
    if len(args) < 2:
        raise Exception("numerical-derivative: 需要 (numerical-derivative f x)")
    
    pos_args = [unwrap_python_value(a) for a in args 
                if not (isinstance(a, Sym) and a.name.startswith(':'))]
    
    f_raw = pos_args[0]
    x_val = pos_args[1]
    
    f = _to_callable(f_raw)
    
    from scipy.misc import derivative
    try:
        result = derivative(f, x_val, dx=1e-6)
    except Exception as e:
        raise Exception(f"numerical-derivative error: {e}")
    
    return wrap_python_value(result)


# ==================== 注册 ====================

def register_numerical_primitives(env: 'Env') -> None:
    """注册数值方法 Prim"""
    env.define("find-root", Prim("find-root", cas_find_root))
    env.define("numerical-integrate", Prim("numerical-integrate", cas_numerical_integrate))
    env.define("numerical-derivative", Prim("numerical-derivative", cas_numerical_derivative))
