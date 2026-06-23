"""
CAS pattern/tensor dispatchers - thin wrappers to eval.cas.pattern and eval.cas.tensor.

Handles:
  match, defrule, rewrite      → cas.pattern
  index, tensor, contract, raise-index, lower-index  → cas.tensor
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import _sym_name


def eval_match(cdr, env):
    """(match pattern expr)"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(pat_form, Cons(expr_form, Nil())):
            from eval.eval_scheme import eval_scheme
            expr_val = eval_scheme(expr_form, env)
            from eval.cas.pattern import _eval_match
            return _eval_match(pat_form, expr_val, env)
    raise Exception("match: need (match pattern expr)")


def eval_defrule(cdr, env):
    """(defrule name pattern replacement)"""
    from core.schemevalue import Cons, Nil, Sym
    match cdr:
        case Cons(name_form, Cons(pat_form, Cons(repl_form, Nil()))):
            name = _sym_name(name_form) if isinstance(name_form, Sym) else str(name_form)
            from eval.cas.pattern import _define_rule
            _define_rule(name, pat_form, repl_form)
            return Str(f"rule '{name}' defined")
    raise Exception("defrule: need (defrule name pattern replacement)")


def eval_rewrite(cdr, env):
    """(rewrite expr rule-name ...)"""
    from core.schemevalue import Cons, Nil, Sym
    match cdr:
        case Cons(expr_form, rest):
            from eval.eval_scheme import eval_scheme
            expr_val = eval_scheme(expr_form, env)
            rule_names = []
            curr = rest
            while isinstance(curr, Cons):
                r = curr.car
                if isinstance(r, Sym):
                    rule_names.append(r.name)
                curr = curr.cdr
            from eval.cas.pattern import _apply_rules
            result = _apply_rules(expr_val, rule_names)
            if isinstance(result, Cons):
                try:
                    result2 = eval_scheme(result, env)
                    if isinstance(result2, PythonObject):
                        return result2
                except Exception:
                    pass
            return result
    raise Exception("rewrite: need (rewrite expr [rule-name ...])")


def eval_index(cdr):
    """(index i j k ...)"""
    from core.schemevalue import Cons
    names = []
    curr = cdr
    while isinstance(curr, Cons):
        a = curr.car
        name = a.name if isinstance(a, Sym) else str(a)
        names.append(name)
        curr = curr.cdr
    from eval.cas.tensor import _declare_indices
    return _declare_indices(names)


def eval_tensor_form(cdr):
    """(tensor name (cov ...) (contra ...))"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(name_form, Cons(cov_form, Cons(contra_form, Nil()))):
            name = _sym_name(name_form) if isinstance(name_form, Sym) else str(name_form)
            from eval.cas.tensor import _make_tensor
            return _make_tensor(name, cov_form, contra_form)
    raise Exception("tensor: need (tensor name (cov ...) (contra ...))")


def eval_contract(cdr, env):
    """(contract tensor idx1 idx2)"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(tc_form, Cons(idx1_form, Cons(idx2_form, Nil()))):
            from eval.eval_scheme import eval_scheme
            tc_val = eval_scheme(tc_form, env)
            idx1 = idx1_form.name if isinstance(idx1_form, Sym) else str(idx1_form)
            idx2 = idx2_form.name if isinstance(idx2_form, Sym) else str(idx2_form)
            from eval.cas.tensor import _do_contract
            return _do_contract(tc_val, idx1, idx2)
    raise Exception("contract: need (contract tensor idx1 idx2)")


def eval_raise_index(cdr, env):
    """(raise-index tensor idx)"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(tc_form, Cons(idx_form, Nil())):
            from eval.eval_scheme import eval_scheme
            tc_val = eval_scheme(tc_form, env)
            idx = idx_form.name if isinstance(idx_form, Sym) else str(idx_form)
            from eval.cas.tensor import _do_raise
            return _do_raise(tc_val, idx)
    raise Exception("raise-index: need (raise-index tensor idx)")


def eval_lower_index(cdr, env):
    """(lower-index tensor idx)"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(tc_form, Cons(idx_form, Nil())):
            from eval.eval_scheme import eval_scheme
            tc_val = eval_scheme(tc_form, env)
            idx = idx_form.name if isinstance(idx_form, Sym) else str(idx_form)
            from eval.cas.tensor import _do_lower
            return _do_lower(tc_val, idx)
    raise Exception("lower-index: need (lower-index tensor idx)")
