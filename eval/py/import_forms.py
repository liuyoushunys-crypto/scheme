"""
Import Forms
"""
from typing import List, Optional
from core.schemevalue import *
from eval.py.attr import _sym_name
import importlib

# ——————— 导入处理 ———————

def eval_py_import(cons: Cons, env: 'Env') -> SchemeValue:
    """
    处理 (import module ...) 和 (import module as alias ...)
    导入 Python 模块并以短名绑定到当前环境。
    """
    from eval.py.convert import wrap_python_value
    cdr = cons.cdr
    if not isinstance(cdr, Cons):
        raise Exception("import requires at least one module name")
    curr = cdr
    while isinstance(curr, Cons):
        module_name_val = curr.car
        module_name = _sym_name(module_name_val)
        alias = None
        rest = curr.cdr
        if isinstance(rest, Cons) and isinstance(rest.car, Sym) and rest.car.name == 'as':
            if isinstance(rest.cdr, Cons):
                alias = _sym_name(rest.cdr.car)
                curr = rest.cdr.cdr
            else:
                raise Exception("import as: missing alias name")
        else:
            curr = rest
        try:
            mod = importlib.import_module(module_name)
        except ImportError as e:
            raise Exception(f"Python import error: {e}")
        if alias:
            env.define(Sym(alias), wrap_python_value(mod))
        else:
            short = module_name.split('.')[-1]
            env.define(Sym(short), wrap_python_value(mod))
    return Sym("undefined")


def eval_py_from_import(cons: Cons, env: 'Env') -> SchemeValue:
    """
    处理 (py-from module.name1 name2 ...)
    从 Python 模块导入特定成员到当前 Scheme 环境。
    "*" 表示导入所有公开成员。
    """
    from eval.py.convert import wrap_python_value
    cdr = cons.cdr
    if not isinstance(cdr, Cons):
        raise Exception("py-from requires module name and at least one import name")
    module_name = _sym_name(cdr.car)
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        raise Exception(f"Python import error: {e}")
    names = cdr.cdr
    if not isinstance(names, Cons):
        raise Exception("py-from requires module name and at least one import name")
    curr = names
    while isinstance(curr, Cons):
        name_val = curr.car
        name = _sym_name(name_val)
        if name == '*':
            for attr_name in dir(mod):
                if not attr_name.startswith('_'):
                    env.define(Sym(attr_name), wrap_python_value(getattr(mod, attr_name)))
        else:
            env.define(Sym(name), wrap_python_value(getattr(mod, name)))
        curr = curr.cdr
    return Sym("undefined")


def eval_from_form(cons: Cons, env: 'Env') -> SchemeValue:
    """
    处理 (from module import name1 name2 ...)
    Python 风格的 from-import 语法。
    """
    from eval.py.convert import wrap_python_value
    from core.schemevalue import from_lisp_list
    cdr = cons.cdr
    args = from_lisp_list(cdr)
    if len(args) < 2:
        raise Exception("from requires: (from <module> import <names>)")
    
    module_name = _sym_name(args[0])
    if len(args) < 2 or not (isinstance(args[1], Sym) and args[1].name == 'import'):
        raise Exception("Expected 'import' keyword after module name")
    names = args[2:]
    if not names:
        raise Exception("from requires at least one name to import")
    
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        raise Exception(f"Python import error: {e}")
    
    if len(names) == 1 and isinstance(names[0], Sym) and names[0].name == '*':
        for attr_name in dir(mod):
            if not attr_name.startswith('_'):
                env.define(Sym(attr_name), wrap_python_value(getattr(mod, attr_name)))
    else:
        for name_val in names:
            name = _sym_name(name_val)
            env.define(Sym(name), wrap_python_value(getattr(mod, name)))
    return Sym("undefined")




