from typing import List
from core.schemevalue import *


def prim_vector_fill_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Vector):
        v, fill = args[0], args[1]
        for i in range(len(v.items)):
            v.items[i] = fill
        return Sym("undefined")
    raise Exception("vector-fill! error")


def prim_vector_set(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 3 and isinstance(args[0], Vector):
        args[0].items[as_int(args[1])] = args[2]
        return Sym("undefined")
    raise Exception("vector-set! error")


def prim_vector_copy(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1 and isinstance(args[0], Vector):
        v = args[0]
        start = as_int(args[1]) if len(args) >= 2 else 0
        end = as_int(args[2]) if len(args) >= 3 else len(v.items)
        return Vector(v.items[start:end])
    raise Exception("vector-copy error")


def prim_vector_copy_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 3 and isinstance(args[0], Vector) and isinstance(args[2], Vector):
        to_v, at, from_v = args[0], as_int(args[1]), args[2]
        start = as_int(args[3]) if len(args) >= 4 else 0
        end = as_int(args[4]) if len(args) >= 5 else len(from_v.items)
        slice_items = from_v.items[start:end]
        to_v.items[at:at+len(slice_items)] = slice_items
        return Sym("undefined")
    raise Exception("vector-copy! error")


def prim_vector_append(args: List[SchemeValue]) -> SchemeValue:
    res = []
    for arg in args:
        if isinstance(arg, Vector):
            res.extend(arg.items)
        else:
            raise Exception("vector-append: expected vector")
    return Vector(res)



def register_vector(env: 'Env') -> None:
    env.define("vector", Prim("vector", lambda args: Vector(list(args))))
    env.define("make-vector", Prim("make-vector", lambda args: Vector([args[1] if len(args) >= 2 else Bool(False)] * as_int(args[0]))))
    env.define("vector-length", Prim("vector-length", lambda args: Integer(len(args[0].items)) if (len(args) == 1 and isinstance(args[0], Vector)) else (_ for _ in ()).throw(Exception("vector-length error"))))
    env.define("vector-ref", Prim("vector-ref", lambda args: args[0].items[as_int(args[1])] if (len(args) == 2 and isinstance(args[0], Vector)) else (_ for _ in ()).throw(Exception("vector-ref error"))))
    env.define("vector-set!", Prim("vector-set!", prim_vector_set))
    env.define("list->vector", Prim("list->vector", lambda args: Vector(from_lisp_list(args[0])) if len(args) == 1 else (_ for _ in ()).throw(Exception("list->vector error"))))
    env.define("vector->list", Prim("vector->list", lambda args: to_lisp_list(args[0].items) if (len(args) == 1 and isinstance(args[0], Vector)) else (_ for _ in ()).throw(Exception("vector->list error"))))
    env.define("vector-fill!", Prim("vector-fill!", prim_vector_fill_bang))
    env.define("vector-copy", Prim("vector-copy", prim_vector_copy))
    env.define("vector-copy!", Prim("vector-copy!", prim_vector_copy_bang))
    env.define("vector-append", Prim("vector-append", prim_vector_append))
