"""
Register
"""
from typing import List, Optional
from core.schemevalue import *
from eval.py.convert import wrap_python_value, unwrap_python_value
from eval.py.attr import _set_py_item, _sym_name
from eval.py.runtime import py_get_prim, py_call_prim, py_eval_prim

# ——————— 注册所有 Python 交互原语 ———————

def py_unwrap_prim(args: List[SchemeValue]) -> SchemeValue:
    """(unwrap-python val) -> Python native value"""
    if len(args) < 1:
        raise Exception("unwrap-python: need 1 argument")
    return wrap_python_value(unwrap_python_value(args[0]))

def py_wrap_prim(args: List[SchemeValue]) -> SchemeValue:
    """(wrap-python val) -> wrap as PythonObject"""
    if len(args) < 1:
        raise Exception("wrap-python: need 1 argument")
    if isinstance(args[0], PythonObject):
        return wrap_python_value(args[0].obj)
    return wrap_python_value(args[0])

def py_str_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-str val) -> Python str representation"""
    if len(args) < 1:
        raise Exception("py-str: need 1 argument")
    return Str(str(unwrap_python_value(args[0])))

def py_eq_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-eq a b) -> Python =="""
    if len(args) < 2:
        raise Exception("py-eq: need 2 arguments")
    return Bool(unwrap_python_value(args[0]) == unwrap_python_value(args[1]))

def py_type_prim(args: List[SchemeValue]) -> SchemeValue:
    """(py-type val) -> Python type name"""
    if len(args) < 1:
        raise Exception("py-type: need 1 argument")
    return Str(type(unwrap_python_value(args[0])).__name__)

def register_python_import_primitives(env: 'Env') -> None:
    """Register Python interaction primitives"""
    from core.schemevalue import Prim

    # py-get
    env.define("py-get", Prim("py-get", py_get_prim))
    # py-call
    env.define("py-call", Prim("py-call", py_call_prim))
    # py-eval
    env.define("py-eval", Prim("py-eval", py_eval_prim))

    # py-set!
    env.define("py-set!", Prim("py-set!", lambda args: (
        Nil() if len(args) == 3 and isinstance(args[1], Sym) and _set_py_item(args)
        else Nil() if len(args) == 3 and _set_py_item(args)
        else (_ for _ in ()).throw(Exception("py-set!: need 3 args"))
    )))

    # Bridge primitives (4-direction roundtrip)
    env.define("unwrap-python", Prim("unwrap-python", py_unwrap_prim))
    env.define("wrap-python", Prim("wrap-python", py_wrap_prim))
    env.define("py-str", Prim("py-str", py_str_prim))
    env.define("py-eq", Prim("py-eq", py_eq_prim))
    env.define("py-type", Prim("py-type", py_type_prim))


