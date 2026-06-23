"""
Short-circuit logical operators: and, or
"""

from core.schemevalue import *


class _Continue:
    """Sentinel: continue evaluating this expression"""
    __slots__ = ('expr',)
    def __init__(self, expr):
        self.expr = expr


def CONT(expr):
    return _Continue(expr)


def is_cont(val):
    return isinstance(val, _Continue)


def eval_and(cdr, env):
    """(and expr ...) -> short-circuit AND"""
    from eval.eval_scheme import eval_scheme
    sub_exps = cdr
    if isinstance(sub_exps, Nil):
        return Bool(True)
    curr = sub_exps
    while isinstance(curr, Cons) and not isinstance(curr.cdr, Nil):
        res = eval_scheme(curr.car, env)
        if isinstance(res, Bool) and not res.value:
            return Bool(False)
        curr = curr.cdr
    if isinstance(curr, Cons):
        return _Continue(curr.car)
    return Bool(True)


def eval_or(cdr, env):
    """(or expr ...) -> short-circuit OR"""
    from eval.eval_scheme import eval_scheme
    sub_exps = cdr
    if isinstance(sub_exps, Nil):
        return Bool(False)
    curr = sub_exps
    while isinstance(curr, Cons) and not isinstance(curr.cdr, Nil):
        res = eval_scheme(curr.car, env)
        if not (isinstance(res, Bool) and not res.value):
            return res
        curr = curr.cdr
    if isinstance(curr, Cons):
        return _Continue(curr.car)
    return Bool(False)
