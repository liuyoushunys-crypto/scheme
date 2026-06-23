from typing import List, Optional
from core.schemevalue import *
from core.tail_call import apply
import primitives.primitives_shared as _shared


def prim_gensym(args: List[SchemeValue]) -> SchemeValue:
    prefix = args[0].name if (len(args) > 0 and isinstance(args[0], Sym)) else "g"
    _shared.gensym_counter += 1
    return Sym(f"{prefix}{_shared.gensym_counter}")


def prim_raise(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("raise: missing argument")
    val = args[0]

    if _shared.exception_handlers:
        handler = _shared.exception_handlers[-1]
        old_handlers = _shared.exception_handlers
        _shared.exception_handlers = _shared.exception_handlers[:-1]
        try:
            apply(handler, [val], _shared.registering_env)
        finally:
            _shared.exception_handlers = old_handlers

        _shared.exception_handlers = _shared.exception_handlers[:-1]
        try:
            return prim_raise([Str(list("raise: exception handler returned"))])
        finally:
            _shared.exception_handlers = old_handlers
    else:
        raise SchemeRaiseException(val)


def prim_raise_continuable(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("raise-continuable: missing argument")
    val = args[0]

    if _shared.exception_handlers:
        handler = _shared.exception_handlers[-1]
        old_handlers = _shared.exception_handlers
        _shared.exception_handlers = _shared.exception_handlers[:-1]
        try:
            res = apply(handler, [val], _shared.registering_env)
            return res
        finally:
            _shared.exception_handlers = old_handlers
    else:
        raise Exception(f"Unhandled continuable exception: {scheme_format(val)}")


def prim_make_closure(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        formals = args[1]
        body = from_lisp_list(args[2]) if len(args) >= 3 else []
        return Closure(formals, to_lisp_list(body), _shared.registering_env)
    raise Exception("make-closure error")


def call_cc(args: List[SchemeValue]) -> SchemeValue:
    from core.schemevalue import ContinuationException
    if len(args) < 1:
        raise Exception("call/cc: missing argument")
    proc = args[0]
    result = [None]

    def cont_func(val: SchemeValue) -> Optional[SchemeValue]:
        result[0] = val
        raise ContinuationException(val)

    cont = Continuation(cont_func)
    try:
        return apply(proc, [cont], _shared.registering_env)
    except ContinuationException as ex:
        return result[0]


def prim_apply(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("apply: arity mismatch")
    proc = args[0]
    last_arg = args[-1]
    if not isinstance(last_arg, Cons) and not isinstance(last_arg, Nil):
        raise Exception("apply: expected list")
    combined = list(args[1:-1]) + from_lisp_list(last_arg)
    return apply(proc, combined, _shared.registering_env)


def prim_defined(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Sym):
        try:
            _shared.registering_env.lookup(args[0].name)
            return Bool(True)
        except Exception:
            return Bool(False)
    return Bool(False)


def prim_with_exception_handler(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("with-exception-handler: arity mismatch")
    handler, thunk = args[0], args[1]
    _shared.exception_handlers.append(handler)
    try:
        return apply(thunk, [], _shared.registering_env)
    finally:
        _shared.exception_handlers.pop()


def prim_dynamic_wind(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 3:
        before, thunk, after = args[0], args[1], args[2]
        apply(before, [], _shared.registering_env)
        try:
            return apply(thunk, [], _shared.registering_env)
        finally:
            apply(after, [], _shared.registering_env)
    raise Exception("dynamic-wind error")


def prim_call_with_values(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        producer, consumer = args[0], args[1]
        produced = apply(producer, [], _shared.registering_env)
        produced_args = produced.values if isinstance(produced, SchemeValues) else [produced]
        return apply(consumer, produced_args, _shared.registering_env)
    raise Exception("call-with-values error")


def register_control(env: 'Env') -> None:
    _shared.registering_env = env
    from primitives.primitives_misc import prim_eager
    env.define("apply", Prim("apply", prim_apply))
    env.define("call-with-current-continuation", Prim("call-with-current-continuation", call_cc))
    env.define("call/cc", Prim("call/cc", call_cc))
    env.define("values", Prim("values", lambda args: args[0] if len(args) == 1 else SchemeValues(args)))
    env.define("call-with-values", Prim("call-with-values", prim_call_with_values))
    env.define("dynamic-wind", Prim("dynamic-wind", prim_dynamic_wind))
    env.define("raise", Prim("raise", prim_raise))
    env.define("raise-continuable", Prim("raise-continuable", prim_raise_continuable))
    env.define("error", Prim("error", lambda args: (_ for _ in ()).throw(SchemeRaiseException(Str(list(scheme_format(args[0]) if len(args) > 0 else "error"))))))
    env.define("with-exception-handler", Prim("with-exception-handler", prim_with_exception_handler))
    env.define("eager", Prim("eager", prim_eager))
