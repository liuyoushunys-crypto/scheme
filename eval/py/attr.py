"""
Attr
"""
from typing import List, Optional
from core.schemevalue import *
import importlib
from eval.py.convert import wrap_python_value, unwrap_python_value


def _sym_name(val: SchemeValue) -> str:
    if isinstance(val, Sym):
        return val.name
    if isinstance(val, Str):
        return val.get_str()
    raise Exception(f"Expected symbol or string, got {type(val).__name__}")


# ——————— 属性链解析 ———————

def resolve_python_attr_chain(name: str, env: 'Env') -> Optional['PythonObject']:
    """
    解析带点号的 Python 属性链。
    "math.pi" → 查找 env 中 math → getattr(math, pi)
    "os.path.join" → 查找 env 中 os → getattr(os, path) → getattr(path, join)
    返回 None 表示无法解析。
    """
    parts = name.split('.')
    try:
        current = env.lookup(Sym(parts[0]))
    except Exception:
        return None
    
    for part in parts[1:]:
        if not isinstance(current, PythonObject):
            return None
        try:
            attr = getattr(current.obj, part)
        except AttributeError:
            # 尝试子模块导入
            try:
                submodule_path = parts[0]
                for p in parts[1:]:
                    if p == part:
                        break
                    submodule_path += '.' + p
                attr = importlib.import_module(submodule_path + '.' + part)
            except (ImportError, ValueError):
                return None
        current = wrap_python_value(attr)
    return current


def resolve_python_attr_chain_parent(name: str, env: 'Env') -> Optional['PythonObject']:
    """
    解析属性链到最后一个父对象（用于 set!）。
    "mpmath.mp.dps" → 返回 PythonObject(mpmath.mp)，用于 setattr(parent, "dps", val)
    """
    parts = name.split('.')
    if len(parts) < 2:
        return None
    try:
        current = env.lookup(Sym(parts[0]))
    except Exception:
        return None
    for part in parts[1:-1]:
        if not isinstance(current, PythonObject):
            return None
        try:
            current = wrap_python_value(getattr(current.obj, part))
        except AttributeError:
            return None
    if not isinstance(current, PythonObject):
        return None
    return current


def set_python_attr(parent: 'PythonObject', attr_name: str, val: SchemeValue) -> None:
    """设置 Python 对象的属性"""
    py_val = unwrap_python_value(val)
    setattr(parent.obj, attr_name, py_val)




# ——————— py-set! 工具 ———————

def _set_py_item(args: List[SchemeValue]) -> bool:
    if len(args) != 3:
        return False
    obj = args[0]
    key = args[1]
    val = args[2]
    if isinstance(obj, PythonObject) and isinstance(key, (Sym, Str)):
        setattr(obj.obj, _sym_name(key), unwrap_python_value(val))
        return True
    if isinstance(obj, PythonObject):
        try:
            obj.obj[unwrap_python_value(key)] = unwrap_python_value(val)
            return True
        except (TypeError, IndexError, KeyError):
            pass
    return False




