"""
algebra — CAS algebra primitives: expand, factor, simplify, solve, etc.

Wraps sympy functions for Scheme access.
"""
from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _sympy():
    """Get engine proxy (auto-fallback symengine→sympy)."""
    from eval.cas.engine import get_engine
    return get_engine()


def _unwrap1(args):
    """Unwrap the first argument."""
    return unwrap_python_value(args[0])


def _unwrap(args):
    """Unwrap all arguments."""
    return [unwrap_python_value(a) for a in args]


def cas_expand(args):
    """(expand expr) — expand expression"""
    sp = _sympy()
    return wrap_python_value(sp.expand(_unwrap1(args)))


def cas_factor(args):
    """(factor expr) — factor expression"""
    sp = _sympy()
    return wrap_python_value(sp.factor(_unwrap1(args)))


def cas_simplify(args):
    """(simplify expr) — simplify expression"""
    sp = _sympy()
    return wrap_python_value(sp.simplify(_unwrap1(args)))


def cas_apart(args):
    """(apart expr var) — partial fraction decomposition"""
    sp = _sympy()
    vals = _unwrap(args)
    return wrap_python_value(sp.apart(vals[0], vals[1] if len(vals) > 1 else sp.Symbol('x')))


def cas_together(args):
    """(together expr) — combine fractions"""
    sp = _sympy()
    return wrap_python_value(sp.together(_unwrap1(args)))


def cas_collect(args):
    """(collect expr var) — collect coefficients"""
    sp = _sympy()
    vals = _unwrap(args)
    return wrap_python_value(sp.collect(vals[0], vals[1]))


def cas_coeff(args):
    """(coeff expr var n) — extract coefficient"""
    sp = _sympy()
    vals = _unwrap(args)
    if len(vals) == 2:
        return wrap_python_value(sp.Poly(vals[0], vals[1]).coeff_monomial(vals[1]))
    return wrap_python_value(sp.Poly(vals[0], vals[1]).coeff_monomial(vals[1]**vals[2]))


def cas_normal(args):
    """(normal expr) — normalize rational expression"""
    sp = _sympy()
    return wrap_python_value(sp.together(_unwrap1(args)).cancel())


def cas_resultant(args):
    """(resultant expr1 expr2 var) — resultant of two polynomials"""
    sp = _sympy()
    vals = _unwrap(args)
    if len(vals) >= 2:
        var = vals[2] if len(vals) > 2 else sp.Symbol('x')
        return wrap_python_value(sp.resultant(vals[0], vals[1], var))
    raise Exception("resultant: need (resultant expr1 expr2 var)")


def cas_discriminant(args):
    """(discriminant expr var) — discriminant of polynomial"""
    sp = _sympy()
    vals = _unwrap(args)
    var = vals[1] if len(vals) > 1 else sp.Symbol('x')
    return wrap_python_value(sp.discriminant(vals[0], var))


def cas_compose(args):
    """(compose f g) — function composition"""
    sp = _sympy()
    vals = _unwrap(args)
    return wrap_python_value(sp.compose(vals[0], vals[1]))


def cas_trigexpand(args):
    """(trigexpand expr) — expand trig functions"""
    sp = _sympy()
    return wrap_python_value(sp.expand_trig(_unwrap1(args)))


def cas_trigsimp(args):
    """(trigsimp expr) — simplify trig expressions"""
    sp = _sympy()
    return wrap_python_value(sp.simplify(_unwrap1(args)))


def cas_powsimp(args):
    """(powsimp expr) — simplify powers"""
    sp = _sympy()
    return wrap_python_value(sp.powsimp(_unwrap1(args)))


def cas_logcombine(args):
    """(logcombine expr) — combine logarithms"""
    sp = _sympy()
    return wrap_python_value(sp.logcombine(_unwrap1(args)))


def cas_radsimp(args):
    """(radsimp expr) — simplify radicals"""
    sp = _sympy()
    return wrap_python_value(sp.radsimp(_unwrap1(args)))


def cas_solve(args):
    """(solve eqn var) — solve equation"""
    sp = _sympy()
    vals = _unwrap(args)
    var = vals[1] if len(vals) > 1 else None
    if var:
        return wrap_python_value(sp.solve(vals[0], var))
    return wrap_python_value(sp.solve(vals[0]))


def cas_subs(args):
    """(subs expr old new) — substitute"""
    sp = _sympy()
    vals = _unwrap(args)
    if len(vals) == 3:
        return wrap_python_value(vals[0].subs(vals[1], vals[2]))
    raise Exception("subs: need (subs expr old new)")


def cas_lhs(args):
    """(lhs eqn) — left-hand side of equation"""
    sp = _sympy()
    eq = _unwrap1(args)
    return wrap_python_value(eq.lhs)


def cas_rhs(args):
    """(rhs eqn) — right-hand side of equation"""
    sp = _sympy()
    eq = _unwrap1(args)
    return wrap_python_value(eq.rhs)


def cas_numer(args):
    """(num expr) — numerator"""
    sp = _sympy()
    return wrap_python_value(sp.fraction(_unwrap1(args))[0])


def cas_denom(args):
    """(denom expr) — denominator"""
    sp = _sympy()
    return wrap_python_value(sp.fraction(_unwrap1(args))[1])


def cas_isolate(args):
    """(isolate eqn var) — isolate variable"""
    sp = _sympy()
    vals = _unwrap(args)
    result = sp.solve(vals[0], vals[1])
    return wrap_python_value(result)


def cas_part(args):
    """(part expr n) — extract nth sub-expression"""
    sp = _sympy()
    vals = _unwrap(args)
    expr, n = vals[0], int(vals[1])
    return wrap_python_value(expr.args[n])


def cas_pickapart(args):
    """(pickapart expr n) — decompose at level n"""
    sp = _sympy()
    vals = _unwrap(args)
    return wrap_python_value(sp.pickapart(vals[0], int(vals[1])))


def cas_ratsimp(args):
    """(ratsimp expr) — rational simplification"""
    sp = _sympy()
    return wrap_python_value(sp.ratsimp(_unwrap1(args)))


def cas_eqn(args):
    """(eqn lhs rhs) — 创建方程 Eq(lhs, rhs)"""
    if len(args) != 2:
        raise Exception("eqn: 需要 (eqn lhs rhs)")
    sp = _sympy()
    lhs = sp.sympify(_unwrap1(args[:1]))
    rhs = sp.sympify(_unwrap1(args[1:2])) if len(args) > 1 else None
    return wrap_python_value(sp.Eq(lhs, rhs))


def register_primitives(env):
    """Register all CAS algebra primitives."""
    prims = [
        ("expand", cas_expand),
        ("factor", cas_factor),
        ("simplify", cas_simplify),
        ("apart", cas_apart),
        ("together", cas_together),
        ("collect", cas_collect),
        ("coeff", cas_coeff),
        ("normal", cas_normal),
        ("resultant", cas_resultant),
        ("discriminant", cas_discriminant),
        ("compose", cas_compose),
        ("trigexpand", cas_trigexpand),
        ("trigsimp", cas_trigsimp),
        ("powsimp", cas_powsimp),
        ("logcombine", cas_logcombine),
        ("radsimp", cas_radsimp),
        ("solve", cas_solve),
        ("subs", cas_subs),
        ("lhs", cas_lhs),
        ("rhs", cas_rhs),
        ("num", cas_numer),
        ("denom", cas_denom),
        ("isolate", cas_isolate),
        ("part", cas_part),
        ("pickapart", cas_pickapart),
        ("ratsimp", cas_ratsimp),
        ("eqn", cas_eqn),
    ]
    for name, func in prims:
        env.define(name, Prim(name, func))