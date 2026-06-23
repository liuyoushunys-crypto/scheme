"""
Core special forms: quote, if, define, lambda, begin, set!
Extracted from eval_scheme.py to keep the evaluator lean.
"""

from core.schemevalue import *
from core.schemevalue import unwrap_syntax, unwrap_to_sym


def eval_quote(cdr):
    """(quote val)"""
    match cdr:
        case Cons(val, Nil()):
            return unwrap_syntax(val)
    raise Exception("Invalid quote syntax")


def eval_if(cdr, env):
    """(if test then [else])"""
    from eval.eval_scheme import eval_scheme
    match cdr:
        case Cons(test_exp, Cons(then_exp, Cons(else_exp, Nil()))):
            test_res = eval_scheme(test_exp, env)
            return (else_exp if (isinstance(test_res, Bool) and not test_res.value)
                    else then_exp), True  # (expr, continue_flag)
        case Cons(test_exp, Cons(then_exp, Nil())):
            test_res = eval_scheme(test_exp, env)
            if isinstance(test_res, Bool) and not test_res.value:
                return Nil(), False
            return then_exp, True
    raise Exception("Invalid if syntax")


def eval_define(cdr, env):
    """(define name val) or (define (name formals ...) body ...)"""
    from eval.eval_scheme import eval_scheme
    match cdr:
        case Cons(Cons(name_val, formals), body):
            name_sym = unwrap_to_sym(name_val)
            if isinstance(name_sym, Sym):
                env.define(name_sym, Closure(formals, body, env))
                return Sym("undefined"), False
        case Cons(name_val, Cons(val_exp, Nil())):
            name_sym = unwrap_to_sym(name_val)
            if isinstance(name_sym, Sym):
                env.define(name_sym, eval_scheme(val_exp, env))
                return Sym("undefined"), False
    raise Exception("Invalid define syntax")


def eval_lambda(cdr, env):
    """(lambda (args ...) body ...)"""
    match cdr:
        case Cons(formals, body):
            return Closure(formals, body, env), False
    raise Exception("Invalid lambda syntax")


def eval_begin(cdr, env):
    """(begin expr ...)"""
    from eval.eval_scheme import eval_scheme
    exps = cdr
    if isinstance(exps, Nil):
        return Nil(), False
    curr = exps
    while isinstance(curr, Cons) and not isinstance(curr.cdr, Nil):
        eval_scheme(curr.car, env)
        curr = curr.cdr
    if isinstance(curr, Cons):
        return curr.car, True
    return Nil(), False


def eval_set(cdr, env):
    """(set! name val)"""
    from eval.eval_scheme import eval_scheme
    match cdr:
        case Cons(name_val, Cons(val_exp, Nil())):
            name_sym = unwrap_to_sym(name_val)
            if isinstance(name_sym, Sym):
                if "." in name_sym.name:
                    from eval.eval_python_import import resolve_python_attr_chain_parent, set_python_attr
                    val = eval_scheme(val_exp, env)
                    parent = resolve_python_attr_chain_parent(name_sym.name, env)
                    if parent is not None:
                        attr_name = name_sym.name.split(".")[-1]
                        set_python_attr(parent, attr_name, val)
                        return Sym("undefined"), False
                env.set(name_sym, eval_scheme(val_exp, env))
                return Sym("undefined"), False
    raise Exception("Invalid set! syntax")
