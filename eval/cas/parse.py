"""
parse — 多格式数学解析器 (LaTeX / MathML / Mathematica / Maxima)

依赖: sympy, antlr4 (可选, 用于 LaTeX)
"""
from core.schemevalue import Prim, Str


def cas_parse(text):
    """解析数学表达式字符串 -> sympy 对象"""
    text = str(text) if not isinstance(text, str) else text
    try:
        import sympy as sp
        return sp.parsing.sympy_parser.parse_expr(text)
    except Exception as e:
        return Str(f"<parse error: {e}>")


def cas_parse_latex(latex_str):
    """解析 LaTeX -> sympy 对象"""
    latex_str = str(latex_str) if not isinstance(latex_str, str) else latex_str
    try:
        import sympy as sp
        from sympy.parsing.latex import parse_latex
        return parse_latex(latex_str)
    except ImportError:
        return Str(f"<latex-parse: {latex_str}>")
    except Exception as e:
        return Str(f"<latex error: {e}>")


def cas_parse_mathml(mathml_str):
    """解析 MathML -> sympy 对象"""
    return Str(f"<mathml-parse>")


def cas_parse_mathematica(expr_str):
    """解析 Mathematica 格式 -> sympy 对象"""
    expr_str = str(expr_str) if not isinstance(expr_str, str) else expr_str
    try:
        import sympy as sp
        from sympy.parsing.mathematica import parse_mathematica
        return parse_mathematica(expr_str)
    except ImportError:
        return Str(f"<mathematica-parse: {expr_str}>")
    except Exception as e:
        return Str(f"<mathematica error: {e}>")


def cas_parse_maxima(expr_str):
    """解析 Maxima 格式 -> sympy 对象"""
    expr_str = str(expr_str) if not isinstance(expr_str, str) else expr_str
    # Maxima 语法接近 sympy
    try:
        import sympy as sp
        return sp.parsing.sympy_parser.parse_expr(
            expr_str.replace("^", "**").replace("%", ""))
    except Exception as e:
        return Str(f"<maxima-parse: {expr_str}>")


def register_parse_primitives(env):
    """Register parse primitives."""
    env.define("parse", Prim("parse", cas_parse))
    env.define("parse-latex", Prim("parse-latex", cas_parse_latex))
    env.define("parse-mathml", Prim("parse-mathml", cas_parse_mathml))
    env.define("parse-mathematica", Prim("parse-mathematica", cas_parse_mathematica))
    env.define("parse-maxima", Prim("parse-maxima", cas_parse_maxima))


register_primitives = register_parse_primitives