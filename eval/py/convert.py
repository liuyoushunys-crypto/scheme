"""
Python ↔ Scheme 值转换
"""
from typing import Any, List, Optional
from core.schemevalue import *

def wrap_python_value(val) -> SchemeValue:
    """Convert Python value recursively to Scheme value"""
    if val is None:
        return Nil()
    if isinstance(val, bool):
        return Bool(val)
    if isinstance(val, int):
        return Integer(val)
    if isinstance(val, float):
        return Num(val)
    if isinstance(val, complex):
        return Complex(val.real, val.imag)
    if isinstance(val, str):
        return Str(list(val))
    if isinstance(val, bytes):
        return Bytevector(bytearray(val))
    if isinstance(val, (list, tuple)):
        result = Nil()
        for item in reversed(val):
            result = Cons(wrap_python_value(item), result)
        return result
    if isinstance(val, dict):
        result = Nil()
        for k, v in val.items():
            result = Cons(
                Cons(wrap_python_value(k), Cons(wrap_python_value(v), Nil())),
                result
            )
        return result
    if isinstance(val, SchemeValue):
        return val
    return PythonObject(val)


def unwrap_python_value(val: SchemeValue):
    """Unpack Scheme value to Python native value"""
    if isinstance(val, PythonObject):
        return val.obj
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        return val.value
    if isinstance(val, Complex):
        return complex(val.real, val.imag)
    if isinstance(val, Bool):
        return val.value
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Nil):
        return None
    if isinstance(val, Sym):
        return val.name
    if isinstance(val, Cons):
        result = []
        while isinstance(val, Cons):
            result.append(unwrap_python_value(val.car))
            val = val.cdr
        return result
    if isinstance(val, Vector):
        return [unwrap_python_value(item) for item in val.items]
    if isinstance(val, Bytevector):
        return bytes(val.data)
    if isinstance(val, Char):
        return chr(val.value)
    raise Exception(f"Cannot unwrap Scheme value to Python: {type(val).__name__}")
