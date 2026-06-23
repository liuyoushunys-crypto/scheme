from typing import List
from core.schemevalue import *
from core.tail_call import apply
import primitives.primitives_shared as _shared


def prim_map(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2: raise Exception("map: arity mismatch")
    proc = args[0]
    lists = args[1:]
    lists_unpacked = [from_lisp_list(lst) for lst in lists]
    min_len = min(len(lst) for lst in lists_unpacked)
    res_items = []
    for i in range(min_len):
        call_args = [lst[i] for lst in lists_unpacked]
        res_items.append(apply(proc, call_args, _shared.registering_env))
    return to_lisp_list(res_items)


def prim_for_each(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2: raise Exception("for-each: arity mismatch")
    proc = args[0]
    lists = args[1:]
    lists_unpacked = [from_lisp_list(lst) for lst in lists]
    min_len = min(len(lst) for lst in lists_unpacked)
    for i in range(min_len):
        call_args = [lst[i] for lst in lists_unpacked]
        apply(proc, call_args, _shared.registering_env)
    return Sym("undefined")


def prim_filter(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2: raise Exception("filter: arity mismatch")
    proc, curr = args[0], args[1]
    res_items = []
    while isinstance(curr, Cons):
        val = curr.car
        pred_res = apply(proc, [val], _shared.registering_env)
        if not (isinstance(pred_res, Bool) and not pred_res.value):
            res_items.append(val)
        curr = curr.cdr
    return to_lisp_list(res_items)


def prim_vector_map(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        proc = args[0]
        vectors = args[1:]
        if all(isinstance(v, Vector) for v in vectors):
            min_len = min(len(v.items) for v in vectors)
            res_items = []
            for i in range(min_len):
                call_args = [v.items[i] for v in vectors]
                res_items.append(apply(proc, call_args, _shared.registering_env))
            return Vector(res_items)
    raise Exception("vector-map error")


def prim_vector_for_each(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        proc = args[0]
        vectors = args[1:]
        if all(isinstance(v, Vector) for v in vectors):
            min_len = min(len(v.items) for v in vectors)
            for i in range(min_len):
                call_args = [v.items[i] for v in vectors]
                apply(proc, call_args, _shared.registering_env)
            return Sym("undefined")
    raise Exception("vector-for-each error")


def register_iter(env: 'Env') -> None:
    env.define("map", Prim("map", prim_map))
    env.define("for-each", Prim("for-each", prim_for_each))
    env.define("filter", Prim("filter", prim_filter))
    env.define("vector-map", Prim("vector-map", prim_vector_map))
    env.define("vector-for-each", Prim("vector-for-each", prim_vector_for_each))
