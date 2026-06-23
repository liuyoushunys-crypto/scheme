"""
Serialization - Based on Python pickle and json modules.

Pickle:
  (pickle-dump obj path)            -> serialize object to file
  (pickle-load path)                -> deserialize object from file
  (pickle-bytes obj)                -> serialize to bytes
  (pickle-from-bytes bytes)         -> deserialize from bytes

JSON Serialization:
  (json-serialize obj)              -> serialize to JSON string
  (json-deserialize str)            -> deserialize from JSON string

Pretty Printing:
  (pprint obj)                      -> pretty print Scheme value
  (pprint obj port)                 -> pretty print to port

Utility:
  (object-size obj)                 -> approximate size of object
"""
import pickle
import io
import sys
from typing import List

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _unwrap_str(val) -> str:
    if isinstance(val, (Str,)):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_bytes(val) -> bytes:
    if isinstance(val, Bytevector):
        return bytes(val.data)
    return _unwrap_str(val).encode("utf-8")


# ==================== Pickle ====================


def pickle_dump(args: List[SchemeValue]) -> SchemeValue:
    """(pickle-dump obj path) -> serialize to file"""
    if len(args) < 2:
        raise Exception("pickle-dump: need 2 arguments (obj path)")
    obj = args[0]
    path = _unwrap_str(args[1])
    py_obj = unwrap_python_value(obj)
    with open(path, 'wb') as f:
        pickle.dump(py_obj, f)
    return Bool(True)


def pickle_load(args: List[SchemeValue]) -> SchemeValue:
    """(pickle-load path) -> deserialize from file"""
    if len(args) < 1:
        raise Exception("pickle-load: need 1 argument (path)")
    path = _unwrap_str(args[0])
    with open(path, 'rb') as f:
        py_obj = pickle.load(f)
    return wrap_python_value(py_obj)


def pickle_bytes(args: List[SchemeValue]) -> SchemeValue:
    """(pickle-bytes obj) -> serialize to bytes"""
    if len(args) < 1:
        raise Exception("pickle-bytes: need 1 argument (obj)")
    obj = args[0]
    py_obj = unwrap_python_value(obj)
    data = pickle.dumps(py_obj)
    return Bytevector(bytearray(data))


def pickle_from_bytes(args: List[SchemeValue]) -> SchemeValue:
    """(pickle-from-bytes bytes) -> deserialize from bytes"""
    if len(args) < 1:
        raise Exception("pickle-from-bytes: need 1 argument")
    data = _unwrap_bytes(args[0])
    py_obj = pickle.loads(data)
    return wrap_python_value(py_obj)


# ==================== JSON Serialization ====================


def json_serialize(args: List[SchemeValue]) -> SchemeValue:
    """(json-serialize obj) -> serialize to JSON string"""
    if len(args) < 1:
        raise Exception("json-serialize: need 1 argument")
    from eval.data.json import scheme_to_json
    obj = args[0]
    import json as _json_module
    py_obj = scheme_to_json(obj)
    try:
        s = _json_module.dumps(py_obj, ensure_ascii=False)
        return Str(s)
    except Exception as e:
        raise Exception(f"Failed to serialize: {e}")


def json_deserialize(args: List[SchemeValue]) -> SchemeValue:
    """(json-deserialize str) -> deserialize from JSON string"""
    if len(args) < 1:
        raise Exception("json-deserialize: need 1 argument")
    from eval.data.json import json_to_scheme
    s = _unwrap_str(args[0])
    import json as _json_module
    try:
        py_obj = _json_module.loads(s)
        return json_to_scheme(py_obj)
    except Exception as e:
        raise Exception(f"Failed to deserialize: {e}")


# ==================== Pretty Print ====================


def _collect_list(val) -> list:
    items = []
    c = val
    while isinstance(c, Cons):
        items.append(c.car)
        c = c.cdr
    if isinstance(c, Nil):
        return items
    return None


def _pprint_val(val, depth=0) -> str:
    indent = "  " * depth
    if isinstance(val, Cons):
        items = _collect_list(val)
        if items is not None:
            if not items:
                return "()"
            if len(items) <= 4 and all(not isinstance(x, Cons) for x in items):
                contents = " ".join(_pprint_val(x, depth+1) for x in items)
                return f"({contents})"
            parts = [f"({_pprint_val(items[0], depth+1)}"]
            for item in items[1:]:
                parts.append(f"{indent}  {_pprint_val(item, depth+1)}")
            parts.append(f"{indent})")
            return "\n".join(parts)
        car = _pprint_val(val.car, depth+1)
        cdr = _pprint_val(val.cdr, depth+1)
        return f"({car} . {cdr})"
    elif isinstance(val, Vector):
        items = [str(x) for x in val.items]
        if len(items) <= 8:
            return "#(" + " ".join(items) + ")"
        parts = ["#(" + items[0]]
        for item in items[1:-1]:
            parts.append(f"{indent}  {item}")
        parts.append(f"{indent}  {items[-1]})")
        parts.append(f"{indent})")
        return "\n".join(parts)
    else:
        from core.schemevalue import scheme_format
        return scheme_format(val)


def pprint_scheme(args: List[SchemeValue]) -> SchemeValue:
    """(pprint obj) or (pprint obj port) -> pretty print"""
    if len(args) < 1:
        raise Exception("pprint: need at least 1 argument")
    obj = args[0]
    if len(args) > 1:
        from core.schemevalue import Port
        if isinstance(args[1], Port):
            port = args[1]
            text = _pprint_val(obj, 0)
            port.write(Str(text))
            return Bool(True)
    text = _pprint_val(obj, 0)
    print(text)
    return Bool(True)


# ==================== Object Size ====================


def object_size(args: List[SchemeValue]) -> SchemeValue:
    """(object-size obj) -> approximate size in bytes"""
    if len(args) < 1:
        raise Exception("object-size: need 1 argument")
    obj = args[0]
    try:
        data = pickle.dumps(obj)
        return Num(len(data))
    except Exception:
        return Num(0)


# ==================== Registration ====================


def register_serialize_primitives(env):
    env.define("pickle-dump", Prim("pickle-dump", pickle_dump))
    env.define("pickle-load", Prim("pickle-load", pickle_load))
    env.define("pickle-bytes", Prim("pickle-bytes", pickle_bytes))
    env.define("pickle-from-bytes", Prim("pickle-from-bytes", pickle_from_bytes))

    env.define("json-serialize", Prim("json-serialize", json_serialize))
    env.define("json-deserialize", Prim("json-deserialize", json_deserialize))

    env.define("pprint", Prim("pprint", pprint_scheme))

    env.define("object-size", Prim("object-size", object_size))