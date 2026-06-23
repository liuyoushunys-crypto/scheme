from typing import List
from core.schemevalue import *


def prim_eager(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("eager: missing argument")
    sp = SchemePromise(args[0], False)
    sp.ready = True
    sp.cached = args[0]
    return sp


def prim_get_closure_code(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Closure):
        return args[0].body
    raise Exception("get-closure-code: expected closure")
