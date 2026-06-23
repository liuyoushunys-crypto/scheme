"""
Runtime
"""
from typing import List, Optional
from core.schemevalue import *
from eval.py.convert import wrap_python_value, unwrap_python_value
from eval.py.attr import _sym_name

# ——————— Python 运行时工具 ———————

def py_get_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-get obj "attr" | attr | idx | key) — 属性/索引/键访问"""
    if len(args) != 2:
        raise Exception("py-get requires 2 arguments: obj and attr_name")
    obj, key = args
    if isinstance(obj, PythonObject):
        if isinstance(key, (Sym, Str)):
            name = _sym_name(key)
            try:
                return wrap_python_value(getattr(obj.obj, name))
            except AttributeError:
                raise Exception(f"Python object has no attribute '{name}'")
        try:
            idx = unwrap_python_value(key)
            return wrap_python_value(obj.obj[idx])
        except (TypeError, IndexError, KeyError) as e:
            raise Exception(f"Python multi-index error: {e}")
    raise Exception(f"py-get requires PythonObject, got {type(obj).__name__}")


def py_call_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-call callable arg ...) — 调用 Python 可调用对象"""
    if len(args) < 1:
        raise Exception("py-call requires at least 1 argument: callable")
    callable_val = args[0]
    py_args = [unwrap_python_value(a) for a in args[1:]]
    
    if isinstance(callable_val, PythonObject):
        fn = callable_val.obj
        if not callable(fn):
            raise Exception(f"Python object is not callable: {fn}")
        try:
            result = fn(*py_args)
        except Exception as e:
            raise Exception(f"Python call error: {e}")
        return wrap_python_value(result)
    
    # Scheme closure via wrapper
    if hasattr(callable_val, '__call__'):
        try:
            result = callable_val(*py_args)
            return wrap_python_value(result)
        except Exception as e:
            raise Exception(f"Scheme call error: {e}")
    
    raise Exception(f"Not callable: {scheme_format(callable_val)}")


def py_eval_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-eval "expr" :var1 val1 :var2 val2 ...) — 求值 Python 表达式"""
    if len(args) < 1:
        raise Exception("py-eval requires at least 1 argument: expression string")
    expr_val = args[0]
    if not isinstance(expr_val, Str):
        raise Exception(f"Expression must be a string, got {scheme_format(expr_val)}")
    expr = expr_val.get_str()
    # 关键字参数
    locals_dict = {}
    i = 1
    while i < len(args):
        key_val = args[i]
        if not isinstance(key_val, Sym) or not key_val.name.startswith(':'):
            raise Exception(f"Expected keyword argument :name, got {scheme_format(key_val)}")
        var_name = key_val.name[1:]  # strip ':'
        if i + 1 >= len(args):
            raise Exception(f"Missing value for variable :{var_name}")
        i += 1
        val = args[i]
        locals_dict[var_name] = unwrap_python_value(val)
        i += 1
    try:
        result = eval(expr, {'__builtins__': __builtins__}, locals_dict)
    except Exception as e:
        raise Exception(f"Python eval error: {e}")
    return wrap_python_value(result)




