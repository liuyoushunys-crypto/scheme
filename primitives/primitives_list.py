from typing import List
from core.schemevalue import *


def prim_list_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("list?: arity mismatch")
    curr = args[0]
    slow = curr
    fast = curr
    while isinstance(fast, Cons) and isinstance(fast.cdr, Cons):
        slow = slow.cdr
        fast = fast.cdr.cdr
        if slow is fast:
            return Bool(False)

    curr = args[0]
    while isinstance(curr, Cons):
        curr = curr.cdr
    return Bool(isinstance(curr, Nil))


def prim_length(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1: raise Exception("length: arity mismatch")
    curr = args[0]
    n = 0
    while isinstance(curr, Cons):
        n += 1
        curr = curr.cdr
    if isinstance(curr, Nil):
        return Integer(n)
    raise Exception("length: expected proper list")


def prim_reverse(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1: raise Exception("reverse: arity mismatch")
    curr = args[0]
    acc = Nil()
    while isinstance(curr, Cons):
        acc = Cons(curr.car, acc)
        curr = curr.cdr
    if isinstance(curr, Nil):
        return acc
    raise Exception("reverse: expected proper list")


def prim_list_tail(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("list-tail: arity mismatch")
    curr = args[0]
    k = as_int(args[1])
    for _ in range(k):
        if isinstance(curr, Cons):
            curr = curr.cdr
        else:
            raise Exception("list-tail: index out of range")
    return curr


def prim_last_pair(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1: raise Exception("last-pair: arity mismatch")
    curr = args[0]
    if not isinstance(curr, Cons):
        raise Exception("last-pair: expected pair")
    while isinstance(curr.cdr, Cons):
        curr = curr.cdr
    return curr


def prim_list_ref(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("list-ref: arity mismatch")
    curr = args[0]
    k = as_int(args[1])
    for _ in range(k):
        if isinstance(curr, Cons):
            curr = curr.cdr
        else:
            raise Exception("list-ref: index out of range")
    if isinstance(curr, Cons):
        return curr.car
    raise Exception("list-ref: index out of range")


def prim_append(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 0:
        return Nil()
    result = args[-1]
    for i in range(len(args) - 2, -1, -1):
        result = append_lists(args[i], result)
    return result


def prim_set_car(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Cons):
        args[0].car = args[1]
        return Sym("undefined")
    raise Exception("set-car! error")


def prim_set_cdr(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Cons):
        args[0].cdr = args[1]
        return Sym("undefined")
    raise Exception("set-cdr! error")


def prim_eq(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        a, b = args[0], args[1]
        if isinstance(a, Sym) and isinstance(b, Sym):
            return Bool(a.name == b.name)
        return Bool(a is b or a == b)
    return Bool(False)



def _car(x: SchemeValue) -> SchemeValue:
    if isinstance(x, Cons):
        return x.car
    raise Exception("car: expected pair")


def _cdr(x: SchemeValue) -> SchemeValue:
    if isinstance(x, Cons):
        return x.cdr
    raise Exception("cdr: expected pair")


def register_pairs(env: 'Env') -> None:
    from primitives.primitives_eq import prim_memq, prim_memv, prim_member, prim_assq, prim_assv, prim_assoc
    env.define("cons", Prim("cons", lambda args: Cons(args[0], args[1]) if len(args) == 2 else (_ for _ in ()).throw(Exception("cons: arity mismatch"))))
    env.define("car", Prim("car", lambda args: args[0].car if (len(args) == 1 and isinstance(args[0], Cons)) else (_ for _ in ()).throw(Exception("car: expected pair"))))
    env.define("cdr", Prim("cdr", lambda args: args[0].cdr if (len(args) == 1 and isinstance(args[0], Cons)) else (_ for _ in ()).throw(Exception("cdr: expected pair"))))
    env.define("set-car!", Prim("set-car!", prim_set_car))
    env.define("set-cdr!", Prim("set-cdr!", prim_set_cdr))
    env.define("list", Prim("list", to_lisp_list))
    env.define("append", Prim("append", prim_append))
    env.define("not", Prim("not", lambda args: Bool(isinstance(args[0], Bool) and not args[0].value)))
    env.define("length", Prim("length", prim_length))
    env.define("reverse", Prim("reverse", prim_reverse))
    env.define("list-tail", Prim("list-tail", prim_list_tail))
    env.define("last-pair", Prim("last-pair", prim_last_pair))
    env.define("list-ref", Prim("list-ref", prim_list_ref))
    env.define("memq", Prim("memq", prim_memq))
    env.define("memv", Prim("memv", prim_memv))
    env.define("member", Prim("member", prim_member))
    env.define("assq", Prim("assq", prim_assq))
    env.define("assv", Prim("assv", prim_assv))
    env.define("assoc", Prim("assoc", prim_assoc))

    # Level 2
    env.define("caar", Prim("caar", lambda args: _car(_car(args[0]))))
    env.define("cadr", Prim("cadr", lambda args: _car(_cdr(args[0]))))
    env.define("cdar", Prim("cdar", lambda args: _cdr(_car(args[0]))))
    env.define("cddr", Prim("cddr", lambda args: _cdr(_cdr(args[0]))))
    # Level 3
    env.define("caaar", Prim("caaar", lambda args: _car(_car(_car(args[0])))))
    env.define("caadr", Prim("caadr", lambda args: _car(_car(_cdr(args[0])))))
    env.define("cadar", Prim("cadar", lambda args: _car(_cdr(_car(args[0])))))
    env.define("caddr", Prim("caddr", lambda args: _car(_cdr(_cdr(args[0])))))
    env.define("cdaar", Prim("cdaar", lambda args: _cdr(_car(_car(args[0])))))
    env.define("cdadr", Prim("cdadr", lambda args: _cdr(_car(_cdr(args[0])))))
    env.define("cddar", Prim("cddar", lambda args: _cdr(_cdr(_car(args[0])))))
    env.define("cdddr", Prim("cdddr", lambda args: _cdr(_cdr(_cdr(args[0])))))
    # Level 4
    env.define("caaaar", Prim("caaaar", lambda args: _car(_car(_car(_car(args[0]))))))
    env.define("caaadr", Prim("caaadr", lambda args: _car(_car(_car(_cdr(args[0]))))))
    env.define("caadar", Prim("caadar", lambda args: _car(_car(_cdr(_car(args[0]))))))
    env.define("caaddr", Prim("caaddr", lambda args: _car(_car(_cdr(_cdr(args[0]))))))
    env.define("cadaar", Prim("cadaar", lambda args: _car(_cdr(_car(_car(args[0]))))))
    env.define("cadadr", Prim("cadadr", lambda args: _car(_cdr(_car(_cdr(args[0]))))))
    env.define("caddar", Prim("caddar", lambda args: _car(_cdr(_cdr(_car(args[0]))))))
    env.define("cadddr", Prim("cadddr", lambda args: _car(_cdr(_cdr(_cdr(args[0]))))))
    env.define("cdaaar", Prim("cdaaar", lambda args: _cdr(_car(_car(_car(args[0]))))))
    env.define("cdaadr", Prim("cdaadr", lambda args: _cdr(_car(_car(_cdr(args[0]))))))
    env.define("cdadar", Prim("cdadar", lambda args: _cdr(_car(_cdr(_car(args[0]))))))
    env.define("cdaddr", Prim("cdaddr", lambda args: _cdr(_car(_cdr(_cdr(args[0]))))))
    env.define("cddaar", Prim("cddaar", lambda args: _cdr(_cdr(_car(_car(args[0]))))))
    env.define("cddadr", Prim("cddadr", lambda args: _cdr(_cdr(_car(_cdr(args[0]))))))
    env.define("cdddar", Prim("cdddar", lambda args: _cdr(_cdr(_cdr(_car(args[0]))))))
    env.define("cddddr", Prim("cddddr", lambda args: _cdr(_cdr(_cdr(_cdr(args[0]))))))
