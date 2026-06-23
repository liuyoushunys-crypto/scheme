"""
core/output — 输出格式

提供各种表达式输出格式。

使用方式：
  (pretty expr)    → 美观输出（ASCII 数学排版）
  (latex expr)     → LaTeX 格式输出
  (ccode expr)     → C 代码生成
  (fcode expr)     → Fortran 代码生成
  (mathml expr)    → MathML 输出
  (describe expr)  → 表达式描述
  (py-len obj)     → Python 对象长度
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


# ==================== 数学显示 ====================

def cas_pretty(args: List[SchemeValue]) -> SchemeValue:
    """
    (pretty expr) — 美观输出表达式（ASCII 数学排版）。

    示例：
      (pretty (integrate #{x^2} x))  →  ASCII 排版显示
    """
    if len(args) < 1:
        raise Exception("pretty: 需要 (pretty expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    # Use pretty() which returns a string (pretty_print prints to stdout and returns None)
    result = sp.pretty(expr)
    return Str(result)


def cas_latex(args: List[SchemeValue]) -> SchemeValue:
    """
    (latex expr) — 输出 LaTeX 格式。

    示例：
      (latex (integrate #{x^2} x))  →  \\frac{x^{3}}{3}
    """
    if len(args) < 1:
        raise Exception("latex: 需要 (latex expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    result = sp.latex(expr)
    return Str(result)


def cas_describe(args: List[SchemeValue]) -> SchemeValue:
    """
    (describe expr) — 返回表达式/对象的字符串描述。

    示例：
      (describe (integrate #{x^2} x))  →  返回描述字符串
    """
    if len(args) < 1:
        raise Exception("describe: 需要 (describe expr)")
    val = args[0]
    py_val = _unwrap1(args) if not isinstance(val, (Str, Sym, Integer, Num, Bool, Nil)) else val
    if isinstance(val, PythonObject):
        obj = val.obj
        lines = [f"类型: {type(obj).__name__}", f"值: {obj}"]
        if hasattr(obj, 'free_symbols'):
            symbols = obj.free_symbols
            if symbols:
                lines.append(f"自由符号: {', '.join(str(s) for s in symbols)}")
        if hasattr(obj, 'func'):
            lines.append(f"函数类型: {obj.func}")
        if hasattr(obj, 'args'):
            lines.append(f"子表达式数: {len(obj.args)}")
        return Str("\n".join(lines))
    return Str(f"值: {py_val}, 类型: {type(py_val).__name__}")


# ==================== 代码生成 ====================

def cas_ccode(args: List[SchemeValue]) -> SchemeValue:
    """
    (ccode expr) — 将表达式转为 C 代码。

    示例：
      (ccode (integrate #{x^2} x))  →  pow(x, 3)/3
    """
    if len(args) < 1:
        raise Exception("ccode: 需要 (ccode expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    result = sp.ccode(expr)
    return Str(result)


def cas_fcode(args: List[SchemeValue]) -> SchemeValue:
    """
    (fcode expr) — 将表达式转为 Fortran 代码。

    示例：
      (fcode (integrate #{x^2} x))  →  x**3/3
    """
    if len(args) < 1:
        raise Exception("fcode: 需要 (fcode expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    result = sp.fcode(expr)
    return Str(result)


def cas_mathml(args: List[SchemeValue]) -> SchemeValue:
    """
    (mathml expr) — 输出 MathML 格式。

    示例：
      (mathml (integrate #{x^2} x))  →  <math>...</math>
    """
    if len(args) < 1:
        raise Exception("mathml: 需要 (mathml expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    result = sp.mathml(expr)
    return Str(result)


# ==================== 元操作 ====================

def cas_pylen(args: List[SchemeValue]) -> SchemeValue:
    """
    (py-len obj) — 返回 Python 对象的长度。

    示例：
      (py-len (list 1 2 3))  →  3
    """
    if len(args) < 1:
        raise Exception("py-len: 需要 (py-len obj)")
    val = args[0]
    if isinstance(val, PythonObject):
        obj = val.obj
    else:
        obj = _unwrap1(args)
    return Integer(len(obj))


# ==================== 注册 ====================

def register_output_primitives(env):
    """注册输出格式 Primitive。"""
    prims = [
        ("pretty", cas_pretty),
        ("latex", cas_latex),
        ("describe", cas_describe),
        ("ccode", cas_ccode),
        ("fcode", cas_fcode),
        ("mathml", cas_mathml),
        ("py-len", cas_pylen),
    ]
    for name, func in prims:
        env.define(name, Prim(name, func))


register_primitives = register_output_primitives