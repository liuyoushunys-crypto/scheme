"""
Import special forms: define-library, import, py-import, py-from, from
"""

from core.schemevalue import *
from eval.eval_import import eval_import, eval_define_library
from eval.eval_python_import import eval_py_import, eval_py_from_import, eval_from_form


def eval_define_library_form(cons, env):
    """(define-library (name ...) ...)"""
    eval_define_library(cons, env)
    return Sym("undefined")


def eval_import_form(cons, env):
    """(import ...) - Scheme or Python import"""
    cdr_val = cons.cdr
    if isinstance(cdr_val, Cons) and isinstance(cdr_val.car, Sym):
        return eval_py_import(cons, env)
    eval_import(cons, env)
    return Sym("undefined")


def eval_py_import_form(cons, env):
    """(py-import module ...)"""
    return eval_py_import(cons, env)


def eval_py_from_form(cons, env):
    """(py-from module name ...)"""
    return eval_py_from_import(cons, env)


def eval_from_form_dispatch(cons, env):
    """(from module import name ...)"""
    return eval_from_form(cons, env)
