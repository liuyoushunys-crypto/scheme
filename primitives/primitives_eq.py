from typing import List
from core.schemevalue import *


def prim_eqv(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("eqv?: arity mismatch")
    a, b = args[0], args[1]
    if a is b: return Bool(True)
    match (a, b):
        case (Sym(s1), Sym(s2)): return Bool(s1 == s2)
        case (Integer(i1), Integer(i2)): return Bool(i1 == i2)
        case (Num(n1), Num(n2)): return Bool(n1 == n2)
        case (Integer(i1), Num(n2)): return Bool(float(i1) == n2)
        case (Num(n1), Integer(i2)): return Bool(n1 == float(i2))
        case (Char(c1), Char(c2)): return Bool(c1 == c2)
        case (Complex(r1, im1), Complex(r2, im2)): return Bool(r1 == r2 and im1 == im2)
        case _: return Bool(False)


def prim_memq(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("memq: arity mismatch")
    item, curr = args[0], args[1]
    while isinstance(curr, Cons):
        if curr.car is item or (isinstance(curr.car, Sym) and isinstance(item, Sym) and curr.car.name == item.name):
            return curr
        curr = curr.cdr
    return Bool(False)


def prim_memv(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("memv: arity mismatch")
    item, curr = args[0], args[1]
    while isinstance(curr, Cons):
        if prim_eqv([item, curr.car]).value:
            return curr
        curr = curr.cdr
    return Bool(False)


def prim_member(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("member: arity mismatch")
    item, curr = args[0], args[1]
    while isinstance(curr, Cons):
        if lisp_equal(item, curr.car):
            return curr
        curr = curr.cdr
    return Bool(False)


def prim_assq(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("assq: arity mismatch")
    key, curr = args[0], args[1]
    while isinstance(curr, Cons):
        pair = curr.car
        if isinstance(pair, Cons):
            if pair.car is key or (isinstance(pair.car, Sym) and isinstance(key, Sym) and pair.car.name == key.name):
                return pair
        curr = curr.cdr
    return Bool(False)


def prim_assv(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("assv: arity mismatch")
    key, curr = args[0], args[1]
    while isinstance(curr, Cons):
        pair = curr.car
        if isinstance(pair, Cons):
            if prim_eqv([key, pair.car]).value:
                return pair
        curr = curr.cdr
    return Bool(False)


def prim_assoc(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("assoc: arity mismatch")
    key, curr = args[0], args[1]
    while isinstance(curr, Cons):
        pair = curr.car
        if isinstance(pair, Cons):
            if lisp_equal(key, pair.car):
                return pair
        curr = curr.cdr
    return Bool(False)



def register_comparison(env: 'Env') -> None:
    from primitives.primitives_list import prim_eq
    env.define("eq?", Prim("eq?", prim_eq))
    env.define("eqv?", Prim("eqv?", prim_eqv))
    env.define("equal?", Prim("equal?", lambda args: Bool(len(args) == 2 and lisp_equal(args[0], args[1]))))
    env.define("=", Prim("=", lambda args: (
        Bool(True) if len(args) < 2 else
        (lambda r: r if r is not None else Bool(all(numbers_equal(x, args[0]) for x in args[1:])))(
            __import__('eval.eval_py_arithmetic', fromlist=['try_py_compare']).try_py_compare("=", args)
        )
    )))
    env.define("<", Prim("<", lambda args: (
        Bool(True) if len(args) < 2 else
        (lambda r: r if r is not None else Bool(all(as_double(args[i]) < as_double(args[i+1]) for i in range(len(args)-1))))(
            __import__('eval.eval_py_arithmetic', fromlist=['try_py_compare']).try_py_compare("<", args)
        )
    )))
    env.define(">", Prim(">", lambda args: (
        Bool(True) if len(args) < 2 else
        (lambda r: r if r is not None else Bool(all(as_double(args[i]) > as_double(args[i+1]) for i in range(len(args)-1))))(
            __import__('eval.eval_py_arithmetic', fromlist=['try_py_compare']).try_py_compare(">", args)
        )
    )))
    env.define("<=", Prim("<=", lambda args: (
        Bool(True) if len(args) < 2 else
        (lambda r: r if r is not None else Bool(all(as_double(args[i]) <= as_double(args[i+1]) for i in range(len(args)-1))))(
            __import__('eval.eval_py_arithmetic', fromlist=['try_py_compare']).try_py_compare("<=", args)
        )
    )))
    env.define(">=", Prim(">=", lambda args: (
        Bool(True) if len(args) < 2 else
        (lambda r: r if r is not None else Bool(all(as_double(args[i]) >= as_double(args[i+1]) for i in range(len(args)-1))))(
            __import__('eval.eval_py_arithmetic', fromlist=['try_py_compare']).try_py_compare(">=", args)
        )
    )))
    # eqn: 符号方程构造器 — 从 #{...} 中 = 映射而来，创建 sympy.Eq
    def prim_eqn(args: List[SchemeValue]) -> SchemeValue:
        """(eqn a b) → 创建符号方程 sympy.Eq(a, b)"""
        if len(args) != 2:
            raise Exception("eqn: 需要 2 个参数")
        a, b = args
        from eval.eval_python_import import unwrap_python_value, wrap_python_value
        py_a = unwrap_python_value(a)
        py_b = unwrap_python_value(b)
        try:
            import sympy
            result = sympy.Eq(py_a, py_b)
        except (ImportError, Exception):
            result = (py_a == py_b)
        return wrap_python_value(result)
    env.define("eqn", Prim("eqn", prim_eqn))
