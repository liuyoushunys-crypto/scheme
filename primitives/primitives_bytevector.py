from typing import List
from core.schemevalue import *


def prim_bytevector_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], Bytevector))


def prim_make_bytevector(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1:
        length = as_int(args[0])
        fill = as_int(args[1]) if len(args) >= 2 else 0
        return Bytevector(bytearray([fill] * length))
    raise Exception("make-bytevector error")


def prim_bytevector(args: List[SchemeValue]) -> SchemeValue:
    return Bytevector(bytearray(as_int(a) for a in args))


def prim_bytevector_length(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Bytevector):
        return Integer(len(args[0].data))
    raise Exception("bytevector-length error")


def prim_bytevector_u8_ref(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Bytevector):
        return Integer(args[0].data[as_int(args[1])])
    raise Exception("bytevector-u8-ref error")


def prim_bytevector_u8_set_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 3 and isinstance(args[0], Bytevector):
        args[0].data[as_int(args[1])] = as_int(args[2])
        return Sym("undefined")
    raise Exception("bytevector-u8-set! error")


def prim_bytevector_copy(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1 and isinstance(args[0], Bytevector):
        bv = args[0]
        start = as_int(args[1]) if len(args) >= 2 else 0
        end = as_int(args[2]) if len(args) >= 3 else len(bv.data)
        return Bytevector(bytearray(bv.data[start:end]))
    raise Exception("bytevector-copy error")


def prim_bytevector_copy_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 3 and isinstance(args[0], Bytevector) and isinstance(args[2], Bytevector):
        to_bv, at, from_bv = args[0], as_int(args[1]), args[2]
        start = as_int(args[3]) if len(args) >= 4 else 0
        end = as_int(args[4]) if len(args) >= 5 else len(from_bv.data)
        slice_data = from_bv.data[start:end]
        to_bv.data[at:at+len(slice_data)] = slice_data
        return Sym("undefined")
    raise Exception("bytevector-copy! error")


def prim_bytevector_append(args: List[SchemeValue]) -> SchemeValue:
    res = bytearray()
    for arg in args:
        if isinstance(arg, Bytevector):
            res.extend(arg.data)
        else:
            raise Exception("bytevector-append: expected bytevector")
    return Bytevector(res)


def prim_utf8_to_string(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1 and isinstance(args[0], Bytevector):
        bv = args[0]
        start = as_int(args[1]) if len(args) >= 2 else 0
        end = as_int(args[2]) if len(args) >= 3 else len(bv.data)
        decoded = bv.data[start:end].decode('utf-8', errors='ignore')
        return Str(list(decoded))
    raise Exception("utf8->string error")


def prim_string_to_utf8(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 1 and isinstance(args[0], Str):
        s = args[0]
        start = as_int(args[1]) if len(args) >= 2 else 0
        end = as_int(args[2]) if len(args) >= 3 else len(s.value)
        substring_val = "".join(s.value[start:end])
        return Bytevector(bytearray(substring_val.encode('utf-8')))
    raise Exception("string->utf8 error")



def register_bytevector(env: 'Env') -> None:
    env.define("make-bytevector", Prim("make-bytevector", prim_make_bytevector))
    env.define("bytevector", Prim("bytevector", prim_bytevector))
    env.define("bytevector-length", Prim("bytevector-length", prim_bytevector_length))
    env.define("bytevector-u8-ref", Prim("bytevector-u8-ref", prim_bytevector_u8_ref))
    env.define("bytevector-u8-set!", Prim("bytevector-u8-set!", prim_bytevector_u8_set_bang))
    env.define("bytevector-copy", Prim("bytevector-copy", prim_bytevector_copy))
    env.define("bytevector-copy!", Prim("bytevector-copy!", prim_bytevector_copy_bang))
    env.define("bytevector-append", Prim("bytevector-append", prim_bytevector_append))
    env.define("utf8->string", Prim("utf8->string", prim_utf8_to_string))
    env.define("string->utf8", Prim("string->utf8", prim_string_to_utf8))
