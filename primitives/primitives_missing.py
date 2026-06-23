import sys
import math
import io
import os as os_module
from typing import List, Optional
from core.schemevalue import *
from core.tail_call import apply
import primitives.primitives_shared as _shared


def prim_eof_object(args: List[SchemeValue]) -> SchemeValue:
    return Eof()


def prim_eof_object_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], Eof))


def prim_read_line(args: List[SchemeValue]) -> SchemeValue:
    from primitives.primitives_io import current_input_port
    port = args[0] if (len(args) > 0 and isinstance(args[0], Port)) else current_input_port
    ch = port.read_char()
    if ch < 0:
        return Eof()
    chars = []
    while ch >= 0 and ch != 0x0A:
        chars.append(chr(ch))
        ch = port.read_char()
    return Str(chars)


def prim_flush_output(args: List[SchemeValue]) -> SchemeValue:
    from primitives.primitives_io import current_output_port
    port = args[0] if (len(args) > 0 and isinstance(args[0], Port)) else current_output_port
    port.flush()
    return Sym("undefined")


def prim_call_with_port(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        port, proc = args[0], args[1]
        if not isinstance(port, Port):
            raise Exception("call-with-port: first argument must be a port")
        try:
            return apply(proc, [port], _shared.registering_env)
        finally:
            port.close()
    raise Exception("call-with-port: arity mismatch")


def prim_finite_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        try:
            d = as_double(args[0])
            return Bool(math.isfinite(d))
        except Exception:
            return Bool(False)
    raise Exception("finite?: arity mismatch")


def prim_infinite_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        try:
            d = as_double(args[0])
            return Bool(math.isinf(d))
        except Exception:
            return Bool(False)
    raise Exception("infinite?: arity mismatch")


def prim_nan_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        try:
            d = as_double(args[0])
            return Bool(math.isnan(d))
        except Exception:
            return Bool(False)
    raise Exception("nan?: arity mismatch")


def prim_rationalize(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        x = as_double(args[0])
        eps = as_double(args[1])
        if eps == 0:
            return to_number(round(x))
        return Num(x)
    raise Exception("rationalize: arity mismatch")


def prim_floor_quotient(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        n = as_int(args[0])
        d = as_int(args[1])
        return Integer(math.floor(n / d))
    raise Exception("floor-quotient: arity mismatch")


def prim_floor_remainder(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        n = as_int(args[0])
        d = as_int(args[1])
        return Integer(n - d * int(math.floor(n / d)))
    raise Exception("floor-remainder: arity mismatch")


def prim_floor_div(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2:
        n = as_int(args[0])
        d = as_int(args[1])
        q = int(math.floor(n / d))
        r = n - d * q
        return SchemeValues([Integer(q), Integer(r)])
    raise Exception("floor/: arity mismatch")


def prim_make_parameter(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1:
        init = args[0]
        filt = args[1] if len(args) >= 2 else None
        if filt is not None:
            from eval.eval_scheme import eval_scheme
            init = eval_scheme(Cons(filt, Cons(init, Nil())), _shared.registering_env)
        return Parameter(None, init, filt)
    raise Exception("make-parameter: arity mismatch")


def prim_symbol_eq(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        for a, b in zip(args, args[1:]):
            if not isinstance(a, Sym) or not isinstance(b, Sym):
                return Bool(False)
            if a.name != b.name:
                return Bool(False)
        return Bool(True)
    raise Exception("symbol=?: arity mismatch")


def prim_boolean_eq(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        for a, b in zip(args, args[1:]):
            if not isinstance(a, Bool) or not isinstance(b, Bool):
                return Bool(False)
            if a.value != b.value:
                return Bool(False)
        return Bool(True)
    raise Exception("boolean=?: arity mismatch")


def prim_delay(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        return SchemePromise(args[0], True)
    raise Exception("delay: arity mismatch")


def prim_delay_force(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        return SchemePromise(args[0], True)
    raise Exception("delay-force: arity mismatch")


def prim_make_promise(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1:
        return SchemePromise(args[0], False, args[0], True)
    raise Exception("make-promise: arity mismatch")


def prim_force(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], SchemePromise):
        from eval.eval_scheme import eval_scheme
        p = args[0]
        if p.ready:
            val = p.cached
            if isinstance(val, SchemePromise):
                return prim_force([val])
            return val
        if p.lazy:
            if isinstance(p.proc, (Cons, Sym)):
                val = eval_scheme(p.proc, _shared.registering_env)
            else:
                val = p.proc
            p.cached = val
            p.ready = True
            if isinstance(val, SchemePromise):
                return prim_force([val])
            return val
        val = apply(p.proc, [], _shared.registering_env)
        p.cached = val
        p.ready = True
        if isinstance(val, SchemePromise):
            return prim_force([val])
        return val
    if len(args) == 1:
        return args[0]
    raise Exception("force: arity mismatch")


def prim_promise_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], SchemePromise))


def prim_features(args: List[SchemeValue]) -> SchemeValue:
    return to_lisp_list([
        Sym("r7rs"), Sym("r6rs"), Sym("r5rs"),
        Sym("exact-closed"), Sym("ieee-float"),
        Sym("full-unicode"), Sym("ratios"), Sym("posix"),
    ])


def prim_emergency_exit(args: List[SchemeValue]) -> SchemeValue:
    code = as_int(args[0]) if len(args) > 0 else 0
    os_module._exit(code)


def prim_environment(args: List[SchemeValue]) -> SchemeValue:
    env = Env()
    for a in args:
        if isinstance(a, Library):
            for exp in a.exports:
                try:
                    val = a.env.lookup(exp)
                    env.define(exp, val)
                except Exception:
                    pass
        elif isinstance(a, EnvValue):
            for k in a.env._bindings:
                try:
                    val = a.env.lookup(Sym(k))
                    env.define(Sym(k), val)
                except Exception:
                    pass
    return EnvValue(env)


def prim_string_foldcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        s = args[0].get_str()
        return Str(list(s.lower()))
    raise Exception("string-foldcase: arity mismatch")


def prim_char_foldcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        return Char(ord(chr(args[0].value).lower()))
    raise Exception("char-foldcase: arity mismatch")


def prim_open_input_bytevector(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Bytevector):
        return InputBytevectorPort(args[0].data)
    raise Exception("open-input-bytevector: arity mismatch")


def prim_open_output_bytevector(args: List[SchemeValue]) -> SchemeValue:
    return OutputBytevectorPort()


def prim_get_output_bytevector(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], OutputBytevectorPort):
        return Bytevector(args[0].get_bytevector())
    raise Exception("get-output-bytevector: expected output port")


def prim_utf8_to_string(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Bytevector):
        return Str(list(bytes(args[0].data).decode("utf-8")))
    raise Exception("utf8->string: arity mismatch")


def prim_string_to_utf8(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return Bytevector(bytearray(args[0].get_str().encode("utf-8")))
    raise Exception("string->utf8: arity mismatch")


def register_missing(env) -> None:
    _shared.registering_env = env

    env.define("eof-object", Prim("eof-object", prim_eof_object))
    env.define("eof-object?", Prim("eof-object?", prim_eof_object_p))
    env.define("read-line", Prim("read-line", prim_read_line))
    env.define("flush-output-port", Prim("flush-output-port", prim_flush_output))
    env.define("call-with-port", Prim("call-with-port", prim_call_with_port))

    env.define("finite?", Prim("finite?", prim_finite_p))
    env.define("infinite?", Prim("infinite?", prim_infinite_p))
    env.define("nan?", Prim("nan?", prim_nan_p))
    env.define("rationalize", Prim("rationalize", prim_rationalize))
    env.define("floor-quotient", Prim("floor-quotient", prim_floor_quotient))
    env.define("floor-remainder", Prim("floor-remainder", prim_floor_remainder))
    env.define("floor/", Prim("floor/", prim_floor_div))

    env.define("make-parameter", Prim("make-parameter", prim_make_parameter))
    env.define("symbol=?", Prim("symbol=?", prim_symbol_eq))
    env.define("boolean=?", Prim("boolean=?", prim_boolean_eq))

    env.define("delay", Prim("delay", prim_delay))
    env.define("delay-force", Prim("delay-force", prim_delay_force))
    env.define("force", Prim("force", prim_force))
    env.define("promise?", Prim("promise?", prim_promise_p))
    env.define("make-promise", Prim("make-promise", prim_make_promise))

    env.define("features", Prim("features", prim_features))
    env.define("emergency-exit", Prim("emergency-exit", prim_emergency_exit))
    env.define("environment", Prim("environment", prim_environment))

    env.define("string-foldcase", Prim("string-foldcase", prim_string_foldcase))
    env.define("char-foldcase", Prim("char-foldcase", prim_char_foldcase))

    env.define("open-input-bytevector", Prim("open-input-bytevector", prim_open_input_bytevector))
    env.define("open-output-bytevector", Prim("open-output-bytevector", prim_open_output_bytevector))
    env.define("get-output-bytevector", Prim("get-output-bytevector", prim_get_output_bytevector))
    env.define("utf8->string", Prim("utf8->string", prim_utf8_to_string))
    env.define("string->utf8", Prim("string->utf8", prim_string_to_utf8))
