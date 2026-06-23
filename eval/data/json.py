"""
JSON 作为 Scheme 一等公民 - 完整支持。

一等公民特性:
  - JSON 字面量可直接作为值
  - JSON 和 Scheme 值自动双向转换
  - 支持 Python 风格的 dict/list 操作
  - 完全基于 Python json 模块

基本功能:
  (json-object)             → 新空对象 {}
  (json-object 'a 1 'b 2)   → {"a": 1, "b": 2}
  (json-array 1 2 3)        → [1, 2, 3]
  (json-parse str)          → 解析 JSON 字符串
  (json-dumps obj)          → JSON 字符串
  (json-dumps-pretty obj)   → 格式化 JSON
  
访问与操作:
  (json-get obj 'key)       → 访问属性 / 数组索引
  (json-get obj "key")      → 字符串键
  (json-get obj 'a 'b 'c)   → 多级访问 obj['a']['b']['c']
  (json-set! obj 'key val)  → 设置属性
  (json-del! obj 'key)      → 删除属性
  (json-keys obj)           → 所有键列表
  (json-values obj)         → 所有值列表
  (json-has? obj 'key)      → 检查键存在
  (json-append obj val ...) → 数组追加元素
  (json-merge a b ...)      → 合并对象/数组

文件操作:
  (json-read path)          → 从文件读取 JSON
  (json-write path obj)     → 写入 JSON 到文件
  (json-update path fn)     → 读取→函数处理→写回

Scheme 值映射:
  Scheme list   → JSON array
  Scheme vector → JSON array  
  Scheme HashTable → JSON object
  Scheme symbol → JSON string
  Scheme bool   → JSON true/false
  Scheme nil    → JSON null
  Python bytes  → JSON base64字符串
"""

import json
import base64
from typing import Any, List, Union

from core.schemevalue import *
from eval.eval_python_import import wrap_python_value, unwrap_python_value


# ==================== Scheme ↔ Python 转换 ====================

def scheme_to_json(val) -> Any:
    """将 Scheme 值转换为 JSON 序列化友好的 Python 值"""
    if val is None:
        return None
    if isinstance(val, Nil):
        return None
    if isinstance(val, Bool):
        return val.value
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        v = val.value
        # 处理 Python 数值
        if isinstance(v, bool):  # bool 是 int 的子类，先检查
            return v
        if isinstance(v, (int, float)):
            return v
        # 处理 Scheme 数值 (Integer, Float, Rational 等)
        from fractions import Fraction
        if isinstance(v, Fraction):
            return float(v)
        # sympy 数值
        if hasattr(v, 'is_number') and v.is_number:
            try:
                f = float(v)
                # 检查是否是整数
                if f == int(f):
                    return int(f)
                return f
            except:
                pass
        # 尝试其他转换方法
        if hasattr(v, '__int__'):
            try:
                return int(v)
            except:
                pass
        if hasattr(v, '__float__'):
            try:
                return float(v)
            except:
                pass
        return str(v)
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    if isinstance(val, Cons):
        # Scheme list -> JSON array
        result = []
        current = val
        while isinstance(current, Cons):
            result.append(scheme_to_json(current.car))
            current = current.cdr
        return result
    if isinstance(val, Vector):
        # Scheme vector -> JSON array
        return [scheme_to_json(v) for v in val.items]
    if isinstance(val, Bytevector):
        # bytes -> base64
        return base64.b64encode(val.data).decode('ascii')
    if isinstance(val, HashTable):
        # HashTable -> JSON object
        result = {}
        for k, v in val.table.items():
            # k 是普通 Python 字符串
            result[k] = scheme_to_json(v)
        return result
    if isinstance(val, PythonObject):
        py_val = val.value
        # 如果是可 JSON 序列化的原生 Python 类型
        if isinstance(py_val, (dict, list, tuple, str, int, float, bool)):
            return py_val
        # 尝试转换其他类型
        try:
            return json.loads(json.dumps(py_val, default=lambda o: str(o)))
        except:
            return str(py_val)
    return str(val)


def json_to_scheme(val) -> SchemeValue:
    """将 Python 值（通常是 json.loads 的结果）转换为 Scheme 值"""
    if val is None:
        return Nil()
    if isinstance(val, bool):
        return Bool(val)
    if isinstance(val, int):
        return Num(val)
    if isinstance(val, float):
        return Num(val)
    if isinstance(val, str):
        return Str(val)
    if isinstance(val, list):
        # JSON array -> Scheme list
        items = [json_to_scheme(item) for item in val]
        result = Nil()
        for item in reversed(items):
            result = Cons(item, result)
        return result
    if isinstance(val, dict):
        # JSON object -> Scheme HashTable
        ht = HashTable(table={})
        for k, v in val.items():
            # 使用普通 Python 字符串作为键，而不是 Str 对象
            ht.table[k] = json_to_scheme(v)
        return ht
    return Str(str(val))


# ==================== JSON 对象/数组构造 ====================

def json_object(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-object)           → 空 HashTable
    (json-object 'a 1 'b 2) → HashTable{"a": 1, "b": 2}
    """
    ht = HashTable(table={})
    i = 0
    while i < len(args) - 1:
        key = args[i]
        val = args[i + 1]
        # 键可以是 symbol 或 string
        if isinstance(key, Sym):
            key_str = key.name
        elif isinstance(key, Str):
            key_str = key.get_str()
        else:
            key_str = str(scheme_to_json(key))
        ht.table[key_str] = val
        i += 2
    return ht


def json_array(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-array 1 2 3) → #(1 2 3)
    """
    items = list(args)
    return Vector(items)


# ==================== 解析/序列化 ====================

def json_parse(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-parse str) → Scheme 值
    支持 JSON 字符串解析为 Scheme 数据结构。
    """
    if len(args) < 1:
        raise Exception("json-parse: need at least 1 argument")
    s = unwrap_python_value(args[0])
    if not isinstance(s, str):
        raise Exception("json-parse: argument must be string")
    try:
        py_val = json.loads(s)
        return json_to_scheme(py_val)
    except json.JSONDecodeError as e:
        raise Exception(f"json-parse error: {e}")


def json_dumps(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-dumps obj) → JSON 字符串
    (json-dumps obj indent) → 带缩进的 JSON
    """
    if len(args) < 1:
        raise Exception("json-dumps: need at least 1 argument")
    obj = args[0]
    indent = None
    if len(args) > 1:
        indent = unwrap_python_value(args[1])
    
    py_val = scheme_to_json(obj)
    try:
        json_str = json.dumps(py_val, indent=indent, ensure_ascii=False)
        return Str(json_str)
    except (TypeError, ValueError) as e:
        raise Exception(f"json-dumps error: {e}")


def json_dumps_pretty(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-dumps-pretty obj) → 缩进为 2 的格式化 JSON
    """
    if len(args) < 1:
        raise Exception("json-dumps-pretty: need at least 1 argument")
    return json_dumps([args[0], Num(2)])


# ==================== 访问与操作 ====================

def json_get(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-get obj 'key)        → 访问属性
    (json-get obj 0)           → 数组索引
    (json-get obj 'a 'b 'c)   → 多级访问
    """
    if len(args) < 2:
        raise Exception("json-get: need at least 2 arguments")
    
    obj = args[0]
    keys = args[1:]
    
    current = obj
    for key in keys:
        if isinstance(current, Vector):
            idx = unwrap_python_value(key)
            if not isinstance(idx, int):
                raise Exception(f"json-get: vector index must be integer")
            items = current.items
            if idx < 0 or idx >= len(items):
                raise Exception(f"json-get: index {idx} out of range")
            current = items[idx]
            
        elif isinstance(current, Cons):
            idx = unwrap_python_value(key)
            if not isinstance(idx, int):
                raise Exception(f"json-get: list index must be integer")
            items = []
            c = current
            while isinstance(c, Cons):
                items.append(c.car)
                c = c.cdr
            if idx < 0 or idx >= len(items):
                raise Exception(f"json-get: index {idx} out of range")
            current = items[idx]
            
        elif hasattr(current, 'table'):
            # HashTable 类型 - 键是普通 Python 字符串
            if isinstance(key, Sym):
                key_val = key.name
            elif isinstance(key, Str):
                key_val = key.get_str()
            else:
                key_val = str(scheme_to_json(key))
            if key_val in current.table:
                current = current.table[key_val]
            else:
                return Nil()
                
        elif isinstance(current, PythonObject):
            py_val = current.value
            k = unwrap_python_value(key)
            if isinstance(py_val, dict):
                if k not in py_val:
                    return Nil()
                current = wrap_python_value(py_val[k])
            elif isinstance(py_val, list):
                if not isinstance(k, int):
                    raise Exception(f"json-get: list index must be integer")
                if k < 0 or k >= len(py_val):
                    return Nil()
                current = wrap_python_value(py_val[k])
            else:
                try:
                    current = wrap_python_value(getattr(py_val, str(k)))
                except AttributeError:
                    return Nil()
        else:
            raise Exception(f"json-get: cannot access {type(current)}")
    
    return current


def json_set(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-set! obj 'key val) → 设置属性（返回 obj本身）
    """
    if len(args) < 3:
        raise Exception("json-set!: need at least 3 arguments")
    
    obj = args[0]
    key = args[1]
    val = args[2]
    
    if hasattr(obj, 'table'):
        # HashTable 类型 - 键是普通 Python 字符串
        if isinstance(key, Sym):
            key_val = key.name
        elif isinstance(key, Str):
            key_val = key.get_str()
        else:
            key_val = str(scheme_to_json(key))
        obj.table[key_val] = val
        return obj
        
    elif isinstance(obj, PythonObject):
        py_val = obj.value
        k = unwrap_python_value(key)
        if isinstance(py_val, dict):
            py_val[k] = unwrap_python_value(val)
            return obj
        elif isinstance(py_val, list):
            if not isinstance(k, int):
                raise Exception("json-set!: list index must be integer")
            py_val[k] = unwrap_python_value(val)
            return obj
    
    raise Exception(f"json-set!: cannot set on {type(obj)}")


def json_del(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-del! obj 'key) → 删除属性（返回 obj本身）
    """
    if len(args) < 2:
        raise Exception("json-del!: need at least 2 arguments")
    
    obj = args[0]
    key = args[1]
    
    if hasattr(obj, 'table'):
        # HashTable 类型 - 使用 del
        if isinstance(key, Sym):
            key_str = key.name
        elif isinstance(key, Str):
            key_str = key.get_str()
        else:
            key_str = str(scheme_to_json(key))
        if key_str in obj.table:
            del obj.table[key_str]
        return obj
        
    elif isinstance(obj, PythonObject):
        py_val = obj.value
        k = unwrap_python_value(key)
        if isinstance(py_val, dict) and k in py_val:
            del py_val[k]
        elif isinstance(py_val, list):
            if isinstance(k, int) and 0 <= k < len(py_val):
                del py_val[k]
    
    return obj


def json_keys(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-keys obj) -> 所有键的列表
    """
    if len(args) < 1:
        raise Exception("json-keys: need at least 1 argument")
    
    obj = args[0]
    keys_list = []
    
    if hasattr(obj, 'table'):
        # HashTable 类型 - 键是普通字符串
        for k in obj.table.keys():
            keys_list.append(Str(k))
    elif isinstance(obj, PythonObject):
        py_val = obj.value
        if isinstance(py_val, dict):
            for k in py_val.keys():
                keys_list.append(Str(str(k)))
    
    # 构造 list
    result = Nil()
    for k in reversed(keys_list):
        result = Cons(k, result)
    return result


def json_values(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-values obj) -> 所有值的列表
    """
    if len(args) < 1:
        raise Exception("json-values: need at least 1 argument")
    
    obj = args[0]
    vals_list = []
    
    if hasattr(obj, 'table'):
        # HashTable 类型
        for v in obj.table.values():
            vals_list.append(v)
    elif isinstance(obj, PythonObject):
        py_val = obj.value
        if isinstance(py_val, dict):
            for v in py_val.values():
                vals_list.append(wrap_python_value(v))
        elif isinstance(py_val, list):
            for v in py_val:
                vals_list.append(wrap_python_value(v))
    
    result = Nil()
    for v in reversed(vals_list):
        result = Cons(v, result)
    return result


def json_has(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-has? obj 'key) -> #t/#f 检查键存在
    """
    if len(args) < 2:
        raise Exception("json-has?: need at least 2 arguments")
    
    obj = args[0]
    key = args[1]
    
    if hasattr(obj, 'table'):
        # HashTable 类型 - 键是普通 Python 字符串
        if isinstance(key, Sym):
            k = key.name
        elif isinstance(key, Str):
            k = key.get_str()
        else:
            k = str(scheme_to_json(key))
        return Bool(k in obj.table)
    
    if isinstance(obj, PythonObject):
        py_val = obj.value
        k = unwrap_python_value(key)
        if isinstance(py_val, dict):
            return Bool(k in py_val)
        elif isinstance(py_val, list) and isinstance(k, int):
            return Bool(0 <= k < len(py_val))
    
    return Bool(False)


def json_append(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-append arr val ...) → 数组/vector 追加元素
    """
    if len(args) < 2:
        raise Exception("json-append: need at least 2 arguments")
    
    obj = args[0]
    vals = args[1:]
    
    if isinstance(obj, Vector):
        new_items = list(obj.items) + list(vals)
        return Vector(new_items)
    
    if isinstance(obj, PythonObject):
        py_val = obj.value
        if isinstance(py_val, list):
            for v in vals:
                py_val.append(unwrap_python_value(v))
            return obj
    
    raise Exception(f"json-append: cannot append to {type(obj)}")


def json_merge(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-merge a b ...) -> 合并多个 JSON 对象或数组
    对象: 后者覆盖前者的相同键
    数组: 顺序连接
    """
    if len(args) < 2:
        raise Exception("json-merge: need at least 2 arguments")
    
    # 检查类型
    first = args[0]
    is_dict = hasattr(first, 'table') or (isinstance(first, PythonObject) and isinstance(first.value, dict))
    
    if is_dict:
        # 合并对象 - HashTable
        result = HashTable(table={})
        # 复制第一个
        if hasattr(first, 'table'):
            for k, v in first.table.items():
                # k 是普通 Python 字符串
                result.table[k] = v
        elif isinstance(first, PythonObject):
            for k, v in first.value.items():
                result.table[k] = wrap_python_value(v)
        # 合并后续
        for obj in args[1:]:
            if hasattr(obj, 'table'):
                for k, v in obj.table.items():
                    result.table[k] = v
            elif isinstance(obj, PythonObject) and isinstance(obj.value, dict):
                for k, v in obj.value.items():
                    result.table[k] = wrap_python_value(v)
        return result
    else:
        # 合并数组/vector
        items = []
        for obj in args:
            if isinstance(obj, Vector):
                items.extend(obj.items)
            elif isinstance(obj, Cons):
                # List
                c = obj
                while isinstance(c, Cons):
                    items.append(c.car)
                    c = c.cdr
            elif isinstance(obj, PythonObject) and isinstance(obj.value, list):
                for v in obj.value:
                    items.append(wrap_python_value(v))
        return Vector(items)


# ==================== 文件操作 ====================

def json_read(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-read path) → 从文件读取并解析 JSON
    """
    if len(args) < 1:
        raise Exception("json-read: need at least 1 argument")
    
    path = unwrap_python_value(args[0])
    if not isinstance(path, str):
        raise Exception("json-read: path must be string")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        py_val = json.loads(content)
        return json_to_scheme(py_val)
    except FileNotFoundError:
        raise Exception(f"json-read: file not found: {path}")
    except json.JSONDecodeError as e:
        raise Exception(f"json-read: parse error: {e}")
    except Exception as e:
        raise Exception(f"json-read: {e}")


def json_write(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-write path obj) → 写入 JSON 到文件
    (json-write path obj pretty) → 格式化写入
    """
    if len(args) < 2:
        raise Exception("json-write: need at least 2 arguments")
    
    path = unwrap_python_value(args[0])
    obj = args[1]
    pretty = len(args) > 2 and (args[2] is True or (isinstance(args[2], Bool) and args[2].value))
    
    if not isinstance(path, str):
        raise Exception("json-write: path must be string")
    
    py_val = scheme_to_json(obj)
    try:
        indent = 2 if pretty else None
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(py_val, f, indent=indent, ensure_ascii=False)
        return Str(path)
    except Exception as e:
        raise Exception(f"json-write: {e}")


def json_update(args: List[SchemeValue]) -> SchemeValue:
    """
    (json-update path fn) → 读取→函数处理→写回
    """
    if len(args) < 2:
        raise Exception("json-update: need at least 2 arguments")
    
    path = unwrap_python_value(args[0])
    fn = args[1]
    
    # 读取
    obj = json_read([Str(path)])
    # 函数处理
    from eval.eval_scheme import apply
    new_obj = apply(fn, [obj])
    # 写回
    return json_write([Str(path), new_obj, Bool(True)])


# ==================== 注册 ====================

def register_json_primitives(env):
    """注册所有 JSON 相关原语"""
    env.define("json-object", Prim("json-object", json_object))
    env.define("json-array", Prim("json-array", json_array))
    env.define("json-parse", Prim("json-parse", json_parse))
    env.define("json-dumps", Prim("json-dumps", json_dumps))
    env.define("json-dumps-pretty", Prim("json-dumps-pretty", json_dumps_pretty))
    
    env.define("json-get", Prim("json-get", json_get))
    env.define("json-set!", Prim("json-set!", json_set))
    env.define("json-del!", Prim("json-del!", json_del))
    env.define("json-keys", Prim("json-keys", json_keys))
    env.define("json-values", Prim("json-values", json_values))
    env.define("json-has?", Prim("json-has?", json_has))
    env.define("json-append", Prim("json-append", json_append))
    env.define("json-merge", Prim("json-merge", json_merge))
    
    env.define("json-read", Prim("json-read", json_read))
    env.define("json-write", Prim("json-write", json_write))
    env.define("json-update", Prim("json-update", json_update))
