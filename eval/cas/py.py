"""
py — Python 互操作糖（Prim 实现，稳妥可靠）

用法：
  (py "np.sin(x) + np.cos(x)")         → 自动注入 env 变量执行 Python
  (py-f "x = {x}, y = {y}")           → f-string 风格
  (.. obj (method1 args...) (method2 args...)) → 方法链
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import wrap_python_value, unwrap_python_value
from eval.eval_scheme import eval_scheme
from parser.parse_program import parse


def register_py_sugar_primitives(env: 'Env') -> None:
    """注册 Python 互操作糖"""
    import re
    
    # ------------ py: 自动注入 env 变量的 Python eval ------------
    def _py_prim(args, env):
        """(py \"expr\") — 执行 Python 表达式，自动注入 env 变量"""
        if len(args) < 1:
            raise Exception("py: need (py \"expr\")")
        expr_str = args[0].get_str() if isinstance(args[0], Str) else str(args[0])
        # 提取表达式中的标识符
        var_names = set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_.]*', expr_str))
        # 过滤掉 Python 关键字和内置函数
        python_keywords = {'None', 'True', 'False', 'and', 'or', 'not',
                           'if', 'else', 'for', 'while', 'in', 'is',
                           'lambda', 'def', 'class', 'return', 'import',
                           'from', 'as', 'try', 'except', 'finally',
                           'raise', 'with', 'yield', 'pass', 'break',
                           'continue', 'abs', 'all', 'any', 'bool', 'bytes',
                           'chr', 'complex', 'dict', 'dir', 'divmod',
                           'enumerate', 'eval', 'exec', 'filter', 'float',
                           'format', 'frozenset', 'globals', 'hasattr',
                           'hash', 'help', 'hex', 'id', 'input', 'int',
                           'isinstance', 'issubclass', 'iter', 'len', 'list',
                           'locals', 'map', 'max', 'min', 'next', 'object',
                           'oct', 'open', 'ord', 'pow', 'print', 'property',
                           'range', 'repr', 'reversed', 'round', 'set',
                           'slice', 'sorted', 'staticmethod', 'str', 'sum',
                           'super', 'tuple', 'type', 'vars', 'zip',
                           # numpy/sympy common
                           'array', 'matrix', 'zeros', 'ones', 'eye',
                           'linspace', 'arange', 'reshape', 'shape', 'size',
                           'ndim', 'dtype', 'float64', 'int32', 'int64',
                           'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan',
                           'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10',
                           'sqrt', 'abs', 'sign', 'floor', 'ceil', 'round',
                           'pi', 'e', 'inf', 'nan', 'Infinity', 'NaN',
                           'Symbol', 'Function', 'symbols', 'var',
                           'integrate', 'diff', 'limit', 'series',
                           'expand', 'factor', 'simplify', 'solve',
                           'Eq', 'Ne', 'Lt', 'Le', 'Gt', 'Ge',
                           'Matrix', 'eye', 'zeros', 'ones', 'det', 'inv',
                           'transpose', 'eigenvals', 'eigenvects',
                           'lambdify', 'oo', 'I', 'E', 'pi'}
        locals_dict = {}
        from core.env import Env
        from eval.eval_scheme import eval_scheme
        for vname in sorted(var_names, key=len, reverse=True):
            # 跳过纯数字、Python 关键字
            if vname.isdigit() or vname in python_keywords:
                continue
            # 处理属性链如 np.linalg.solve → 只用顶级名 np
            top_name = vname.split('.')[0]
            if top_name in locals_dict:
                continue
            try:
                sym = Sym(top_name)
                sv = env.lookup(sym)
                pv = unwrap_python_value(sv)
                locals_dict[top_name] = pv
            except Exception:
                pass
        
        # 构建变量名映射：np→np, sp→sp 等
        # 执行
        try:
            builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
            # 注入常见模块
            import numpy as _np
            import sympy as _sp
            import math as _math
            locals_dict.setdefault('np', _np)
            locals_dict.setdefault('numpy', _np)
            locals_dict.setdefault('sp', _sp)
            locals_dict.setdefault('sympy', _sp)
            locals_dict.setdefault('math', _math)
            locals_dict.setdefault('__builtins__', builtins)
            result = eval(expr_str, {'__builtins__': builtins}, locals_dict)
            return wrap_python_value(result)
        except Exception as e:
            return Str(list(f"py error: {e}"))
    
    env.define("py", Prim("py", lambda args: _py_prim(args, env)))
    
    # ------------ py-f: Python f-string 格式化 ------------
    def _pyf_prim(args, env):
        """(py-f \"format string with {vars}\") — Python 风格格式化"""
        if len(args) < 1:
            raise Exception("py-f: need (py-f \"fmt\")")
        fmt_str = args[0].get_str() if isinstance(args[0], Str) else str(args[0])
        # 用 Python f-string
        import re
        var_names = set(re.findall(r'\{([^}]+)\}', fmt_str))
        locals_dict = {}
        for vname in var_names:
            try:
                sym = Sym(vname.strip())
                sv = env.lookup(sym)
                pv = unwrap_python_value(sv)
                locals_dict[vname.strip()] = pv
            except Exception:
                locals_dict[vname.strip()] = f"<{vname}>"
        
        try:
            builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
            result = eval(f'f"""{fmt_str}"""', {'__builtins__': builtins}, locals_dict)
            return Str(list(str(result)))
        except Exception as e:
            return Str(list(f"py-f error: {e}"))
    
    env.define("py-f", Prim("py-f", lambda args: _pyf_prim(args, env)))
    
    # ------------ .. 方法链（宏版本，避免参数提前求值）------------
    _DOTDOT_MACRO = """
(define-macro (.. obj . steps)
  (if (null? steps)
      obj
      (let loop ((expr obj)
                 (remaining steps))
        (if (null? remaining)
            expr
            (let ((step (car remaining)))
              (loop
                (cons 'py-call
                  (cons (list 'py-get expr
                        (list 'quote (car step)))
                        (cdr step)))
                (cdr remaining)))))))
"""
    eval_scheme(parse(_DOTDOT_MACRO), env)
