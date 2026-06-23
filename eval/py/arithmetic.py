"""
Python 算术代理模块 — 让 Scheme 算术原语透明地代理到 Python。

当任意操作数为 PythonObject 时，将所有操作数转为 Python 值，
然后使用 Python 运算符/函数执行操作，最后转回 Scheme 值。

这使得 sympy 等库可以与 Scheme 原生算术无缝协作：
  (+ x 1)  →  sympy.Add(x, 1)  （如果 x 是 sympy Symbol）
  (* x 2)  →  sympy.Mul(x, 2)
  (sin x)  →  sympy.sin(x)
"""
import math as py_math
import operator as py_op
from functools import reduce
from typing import Any, Callable, List, Optional

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value

# 二元运算符映射
_BINARY_OPS = {
    "+": py_op.add,
    "-": py_op.sub,
    "*": py_op.mul,
    "/": py_op.truediv,
    "expt": py_op.pow,
    "modulo": py_op.mod,
    "quotient": py_op.floordiv,
}

# 比较运算符映射
_COMPARE_OPS = {
    "=": py_op.eq,
    "<": py_op.lt,
    ">": py_op.gt,
    "<=": py_op.le,
    ">=": py_op.ge,
}

# 一元数学函数映射（优先 native math，失败时尝试 sympy）
_UNARY_MATH = {
    "sin": py_math.sin,
    "cos": py_math.cos,
    "tan": py_math.tan,
    "asin": py_math.asin,
    "acos": py_math.acos,
    "atan": py_math.atan,
    "sinh": py_math.sinh,
    "cosh": py_math.cosh,
    "tanh": py_math.tanh,
    "asinh": py_math.asinh,
    "acosh": py_math.acosh,
    "atanh": py_math.atanh,
    "sqrt": py_math.sqrt,
    "log": None,  # 特殊处理（支持双参数）
    "exp": py_math.exp,
    "abs": py_math.fabs if False else abs,  # abs 可处理任意类型
}


def _has_py_object(args: List[SchemeValue]) -> bool:
    """检查参数列表中是否含有 PythonObject"""
    return any(isinstance(a, PythonObject) for a in args)


def try_py_binary_op(op_name: str, args: List[SchemeValue]) -> Optional[SchemeValue]:
    """
    尝试用 Python 二元运算符执行操作。
    仅当存在 PythonObject 操作数时触发。
    """
    if not _has_py_object(args):
        return None
    if len(args) < 2:
        return None

    op_func = _BINARY_OPS.get(op_name)
    if op_func is None:
        return None

    py_args = [unwrap_python_value(a) for a in args]
    try:
        result = reduce(op_func, py_args)
    except Exception as e:
        raise Exception(f"Python {op_name} error: {e}")
    return wrap_python_value(result)


def try_py_compare(op_name: str, args: List[SchemeValue]) -> Optional[SchemeValue]:
    """尝试用 Python 比较运算符。仅当存在 PythonObject 时触发。"""
    if not _has_py_object(args):
        return None
    if len(args) < 2:
        return None
    op_func = _COMPARE_OPS.get(op_name)
    if op_func is None:
        return None
    py_args = [unwrap_python_value(a) for a in args]
    try:
        # 单对比较: 返回原始结果（可能是 sympy 关系表达式）
        if len(py_args) == 2:
            result = op_func(py_args[0], py_args[1])
            if isinstance(result, bool):
                return Bool(result)
            # sympy 关系表达式 → PythonObject
            return wrap_python_value(result)
        # 多对链式比较: 全部必须为 bool
        results = [op_func(py_args[i], py_args[i+1]) for i in range(len(py_args)-1)]
        if all(isinstance(r, bool) for r in results):
            return Bool(all(results))
        # 混合类型 → 向量
        return Vector([wrap_python_value(r) for r in results])
    except Exception as e:
        raise Exception(f"Python {op_name} error: {e}")


def try_py_unary_math(func_name: str, args: List[SchemeValue]) -> Optional[SchemeValue]:
    """
    尝试用 Python 数学函数执行操作。
    先试原生 math.xxx，失败时尝试 sympy.xxx。
    """
    if not _has_py_object(args):
        return None
    if len(args) < 1:
        return None

    py_arg = unwrap_python_value(args[0])

    # 特殊处理 log（支持双参数）
    if func_name == "log":
        try:
            if len(args) >= 2:
                base = unwrap_python_value(args[1])
                result = py_math.log(py_arg, base)
            else:
                result = py_math.log(py_arg)
        except (TypeError, ValueError, RuntimeError):
            try:
                import sympy
                if len(args) >= 2:
                    base = unwrap_python_value(args[1])
                    result = sympy.log(py_arg, base)
                else:
                    result = sympy.log(py_arg)
            except ImportError:
                raise Exception(f"Python log error: unsupported type {type(py_arg)}")
        return wrap_python_value(result)

    py_func = _UNARY_MATH.get(func_name)
    if py_func is None:
        return None

    try:
        result = py_func(py_arg)
    except (TypeError, ValueError, RuntimeError):
        # 原生 math 失败 → 尝试 sympy
        try:
            import sympy
            sympy_func = getattr(sympy, func_name, None)
            if sympy_func is None:
                raise Exception(f"sympy has no function '{func_name}'")
            result = sympy_func(py_arg)
        except ImportError:
            raise Exception(f"Python {func_name} error: unsupported type {type(py_arg)}")
    return wrap_python_value(result)


def try_py_unary_op(op_name: str, args: List[SchemeValue]) -> Optional[SchemeValue]:
    """尝试用 Python 一元运算符（取负等）"""
    if not _has_py_object(args):
        return None
    if len(args) != 1:
        return None

    py_arg = unwrap_python_value(args[0])

    if op_name == "negate":
        try:
            result = -py_arg
        except Exception as e:
            raise Exception(f"Python negation error: {e}")
        return wrap_python_value(result)

    return None


def try_py_atan(args: List[SchemeValue]) -> Optional[SchemeValue]:
    """atan 特殊处理：1参数 atan, 2参数 atan2"""
    if not _has_py_object(args):
        return None
    if len(args) < 1:
        return None

    py_args = [unwrap_python_value(a) for a in args]
    try:
        if len(args) == 1:
            result = py_math.atan(py_args[0])
        else:
            result = py_math.atan2(py_args[0], py_args[1])
    except (TypeError, ValueError, RuntimeError):
        try:
            import sympy
            if len(args) == 1:
                result = sympy.atan(py_args[0])
            else:
                result = sympy.atan2(py_args[0], py_args[1])
        except ImportError:
            raise Exception(f"Python atan error: unsupported type {type(py_args[0])}")
    return wrap_python_value(result)