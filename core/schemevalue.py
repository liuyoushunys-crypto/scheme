import io
import sys
import math
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Iterable, Tuple, Union, Dict, Set
from core.exceptions import *
from core.port import *

class SchemeValue:
    """所有 Scheme 值的基类"""
    __slots__ = ()
    
    def __repr__(self) -> str:
        return scheme_format(self)


class Nil(SchemeValue):
    """空列表单例 (Null)"""
    __slots__ = ()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Nil, cls).__new__(cls)
        return cls._instance


class Eof(SchemeValue):
    """EOF 对象单例"""
    __slots__ = ()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Eof, cls).__new__(cls)
        return cls._instance


@dataclass(frozen=True, slots=True)
class Sym(SchemeValue):
    """符号类型 (Symbol)"""
    name: str


@dataclass(frozen=True, slots=True)
class Num(SchemeValue):
    """不精确实数 (Float)"""
    value: float


@dataclass(frozen=True, slots=True)
class Integer(SchemeValue):
    """精确整数 (Int)"""
    value: int


@dataclass(frozen=True, slots=True)
class Complex(SchemeValue):
    """复数类型"""
    real: float
    imag: float


@dataclass(frozen=True, slots=True)
class Bool(SchemeValue):
    """布尔类型"""
    value: bool


@dataclass(frozen=True, slots=True)
class Char(SchemeValue):
    """字符类型"""
    value: int


@dataclass(frozen=True, slots=True)
class EnvValue(SchemeValue):
    """环境包装值"""
    env: Any


@dataclass(frozen=True, slots=True)
class SchemeValues(SchemeValue):
    """多值返回容器 (Values)"""
    values: List[SchemeValue]


@dataclass(frozen=True, slots=True)
class Prim(SchemeValue):
    """内建原语函数"""
    name: str
    func: Callable[[List[SchemeValue]], SchemeValue]


@dataclass(frozen=True, slots=True)
class Continuation(SchemeValue):
    """一等控制流续体 (Continuation)"""
    func: Callable[[SchemeValue], Optional[SchemeValue]]


@dataclass(frozen=True, slots=True)
class TailCallSentinel(SchemeValue):
    """尾调用哨兵：在蹦床中承载未完成的求值上下文"""
    expr: SchemeValue
    env: Any


@dataclass(slots=True)
class Cons(SchemeValue):
    """点对结构 (Pair / Cons Cells) - 可变，支持 set-car! 和 set-cdr!"""
    car: SchemeValue
    cdr: SchemeValue


@dataclass(slots=True)
class Str(SchemeValue):
    """字符串类型（采用 list[str] 支持就地修改，符合 R7RS 标准）"""
    value: list[str]

    def get_str(self) -> str:
        return "".join(self.value)


@dataclass(slots=True)
class Vector(SchemeValue):
    """向量类型 (Vector) - 可变，支持 vector-set!"""
    items: list[SchemeValue]


@dataclass(slots=True)
class HashTable(SchemeValue):
    """R7RS 哈希表实现（内部使用 Python dict）"""
    table: dict  # key: SchemeValue → value: SchemeValue


@dataclass(slots=True)
class Bytevector(SchemeValue):
    """R7RS 字节向量类型 (Bytevector) - 可变，支持 bytevector-u8-set!"""
    data: bytearray



@dataclass(slots=True)
class Closure(SchemeValue):
    """用户自定义闭包"""
    formals: SchemeValue
    body: SchemeValue
    env: Any


@dataclass(slots=True)
class MacroClosure(SchemeValue):
    """非卫生常规宏闭包"""
    formals: SchemeValue
    body: SchemeValue
    env: Any


@dataclass(slots=True)
class SyntaxRulesMacro(SchemeValue):
    """R7RS 卫生宏宏定义"""
    literals: List[Sym]
    rules: List[tuple[SchemeValue, SchemeValue]]
    env: Any
    ellipsis_id: str = "..."


@dataclass(slots=True)
class Syntax(SchemeValue):
    """语法对象：包装表达式及其求值时的词法环境"""
    expression: SchemeValue
    env: Any


@dataclass(slots=True)
class PatternVar(SchemeValue):
    """syntax-case 中绑定的模式变量描述符"""
    depth: int
    value: SchemeValue


@dataclass(slots=True)
class MacroTransformer(SchemeValue):
    """一等过程宏变换器"""
    proc: SchemeValue


@dataclass(slots=True)
class Library(SchemeValue):
    """R7RS 模块/库类型 (Library)"""
    name: tuple
    exports: list
    env: Any


@dataclass(slots=True)
class SchemePromise(SchemeValue):
    """延迟求值承诺 (Promise) - 在求值后需要修改内部 ready 与 cached 状态"""
    proc: SchemeValue
    lazy: bool
    cached: Optional[SchemeValue] = None
    ready: bool = False


@dataclass(slots=True)
class Parameter(SchemeValue):
    proc: SchemeValue
    value: SchemeValue
    filter_proc: Any = None


@dataclass(slots=True)
class CaseLambda(SchemeValue):
    clauses: List[tuple]
    env: Any


@dataclass(slots=True)
class PythonObject(SchemeValue):
    """包装 Python 对象的 Scheme 值 — 用于 Python 互操作"""
    obj: Any

    def __repr__(self) -> str:
        s = str(self.obj)
        if len(s) > 80:
            s = s[:77] + "..."
        return f"#<python:{type(self.obj).__module__}.{type(self.obj).__qualname__} {s}>"


@dataclass(slots=True)
class ConditionType(SchemeValue):
    id: Sym
    supertypes: List['ConditionType']
    field_names: List[str]

    def get_all_fields(self) -> Set[str]:
        fields = set(self.field_names)
        for st in self.supertypes:
            fields |= st.get_all_fields()
        return fields

    def is_subtype(self, other: 'ConditionType') -> bool:
        if self is other:
            return True
        for st in self.supertypes:
            if st is other or st.is_subtype(other):
                return True
        return False


@dataclass(slots=True)
class Condition(SchemeValue):
    type: ConditionType
    fields: Dict[str, SchemeValue]


@dataclass(slots=True)
class CompoundCondition(SchemeValue):
    conditions: List[Condition]


    



def unpack_list(val: SchemeValue) -> Optional[List[SchemeValue]]:
    """尝试将点对链扁平化解包为标准的 Python 列表"""
    if isinstance(val, Nil):
        return []
    lst = []
    current = val
    while isinstance(current, Cons):
        lst.append(current.car)
        current = current.cdr
    return lst if isinstance(current, Nil) else None

def lisp_equal(a: SchemeValue, b: SchemeValue) -> bool:
    """深度结构比对 (符合 equal? 与 values_equal 的判定规范)"""
    match (a, b):
        case (Sym(s1), Sym(s2)): return s1 == s2
        case (Integer(i1), Integer(i2)): return i1 == i2
        case (Integer(i1), Num(n2)): return float(i1) == n2
        case (Num(n1), Integer(i2)): return n1 == float(i2)
        case (Num(n1), Num(n2)): return n1 == n2
        case (Bool(b1), Bool(b2)): return b1 == b2
        case (Char(c1), Char(c2)): return c1 == c2
        case (Nil(), Nil()): return True
        case (Cons() as c1, Cons() as c2):
            return lisp_equal(c1.car, c2.car) and lisp_equal(c1.cdr, c2.cdr)
        case (Vector(v1), Vector(v2)):
            return len(v1) == len(v2) and all(lisp_equal(x, y) for x, y in zip(v1, v2))
        case (Bytevector(v1), Bytevector(v2)):
            return v1 == v2
        case (Complex(r1, im1), Complex(r2, im2)):
            return r1 == r2 and im1 == im2
        case _ if hasattr(a, 'get_str') and hasattr(b, 'get_str'):
            return a.get_str() == b.get_str()
        case _:
            return a is b

def append_lists(l1: SchemeValue, l2: SchemeValue) -> SchemeValue:
    if isinstance(l1, Cons):
        return Cons(l1.car, append_lists(l1.cdr, l2))
    return l2

def as_double(v: SchemeValue) -> float:
    match v:
        case Num(val): return val
        case Integer(val): return float(val)
        case Complex(real, _): return real
        case _: raise Exception("expected number")

def as_int(v: SchemeValue) -> int:
    match v:
        case Integer(val): return val
        case Num(val): return int(val)
        case Complex(real, _): return int(real)
        case _: raise Exception("expected number")

def to_number(val: float) -> SchemeValue:
    if val == math.trunc(val) and -9223372036854775808 <= val <= 9223372036854775807:
        return Integer(int(val))
    return Num(val)

def to_complex_number(real: float, imag: float) -> SchemeValue:
    if imag == 0:
        return to_number(real)
    return Complex(real, imag)

def numbers_equal(a: SchemeValue, b: SchemeValue) -> bool:
    match (a, b):
        case (Integer(i1), Integer(i2)): return i1 == i2
        case (Integer(i1), Num(n2)): return float(i1) == n2
        case (Num(n1), Integer(i2)): return n1 == float(i2)
        case (Num(n1), Num(n2)): return n1 == n2
        case (Complex(r1, im1), Complex(r2, im2)): return r1 == r2 and im1 == im2
        case (Complex(r, im), Num(n)): return r == n and im == 0
        case (Num(n), Complex(r, im)): return n == r and im == 0
        case (Complex(r, im), Integer(i)): return r == float(i) and im == 0
        case (Integer(i), Complex(r, im)): return float(i) == r and im == 0
        case _: return as_double(a) == as_double(b)

def to_lisp_list(elements: Iterable[SchemeValue]) -> SchemeValue:
    res = Nil()
    for el in reversed(list(elements)):
        res = Cons(el, res)
    return res

def from_lisp_list(val: SchemeValue) -> List[SchemeValue]:
    res = []
    current = val
    while isinstance(current, Cons):
        res.append(current.car)
        current = current.cdr
    return res

def datum_to_syntax(template_id: SchemeValue, datum: SchemeValue) -> SchemeValue:
    """参考 template_id 的词法上下文，将 datum 包装为语法对象"""
    env = template_id.env if isinstance(template_id, Syntax) else None
    def wrap(d):
        if isinstance(d, Syntax):
            return d
        if isinstance(d, Cons):
            return Cons(wrap(d.car), wrap(d.cdr))
        if isinstance(d, Vector):
            return Vector([wrap(x) for x in d.items])
        return Syntax(d, env)
    return wrap(datum)

def unwrap_to_sym(val: SchemeValue) -> SchemeValue:
    """递归解包语法对象以获取底层真实的值（例如 Symbol）"""
    while isinstance(val, Syntax):
        val = val.expression
    return val

def unwrap_syntax(val: SchemeValue) -> SchemeValue:
    """递归将整个语法对象转换为纯 datum 结构（移除所有 Lexical Context）"""
    if isinstance(val, Syntax):
        return unwrap_syntax(val.expression)
    if isinstance(val, Cons):
        return Cons(unwrap_syntax(val.car), unwrap_syntax(val.cdr))
    if isinstance(val, Vector):
        return Vector([unwrap_syntax(x) for x in val.items])
    return val


def scheme_format(val) -> str:
    match val:
        case Syntax(expression, _):
            return f"#<syntax {scheme_format(expression)}>"
        case PatternVar(depth, value):
            return f"#<pattern-var:{depth}:{scheme_format(value)}>"
        case MacroTransformer():
            return "#<macro-transformer>"
        case Library(name, _, _):
            name_str = " ".join(str(x) for x in name)
            return f"#<library ({name_str})>"
        case Sym(name):
            return name
        case Integer(value):
            return str(value)
        case Num(value):
            return str(value)
        case Str() as s:
            escaped = s.get_str().replace('"', '\\"')
            return f'"{escaped}"'
        case Bool(value):
            return "#t" if value else "#f"
        case Nil():
            return "()"
        case Eof():
            return "#<eof>"
        case Cons() as cons:
            unpacked = unpack_list(cons)
            if unpacked is not None:
                match unpacked:
                    case [Sym("quote"), q]:
                        return f"'{scheme_format(q)}"
                    case [Sym("quasiquote"), qq]:
                        return f"`{scheme_format(qq)}"
                    case [Sym("unquote"), u]:
                        return f",{scheme_format(u)}"
                    case [Sym("unquote-splicing"), us]:
                        return f",@{scheme_format(us)}"
                    case [Sym("syntax"), s]:
                        return f"#'{scheme_format(s)}"
                    case [Sym("quasisyntax"), qs]:
                        return f"#`{scheme_format(qs)}"
                    case [Sym("unsyntax"), us]:
                        return f"#,{scheme_format(us)}"
                    case [Sym("unsyntax-splicing"), uss]:
                        return f"#,@{scheme_format(uss)}"
                    case _:
                        return "(" + " ".join(scheme_format(x) for x in unpacked) + ")"
            else:
                return f"({scheme_format(cons.car)} . {scheme_format(cons.cdr)})"
        case Prim(name):
            return f"#<primitive:{name}>"
        case Closure():
            return "#<procedure>"
        case MacroClosure():
            return "#<macro>"
        case EnvValue():
            return "#<environment>"
        case SchemeValues(values):
            return " ".join(scheme_format(x) for x in values)
        case HashTable():
            return "#<hash-table>"
        case Char(value):
            if value == 0x20:
                return "#\\space"
            elif value == 0x0A:
                return "#\\newline"
            elif value == 0x09:
                return "#\\tab"
            elif value == 0x0D:
                return "#\\return"
            elif value == 0x08:
                return "#\\backspace"
            elif value < 0x10000:
                c = chr(value)
                return f"#\\x{value:x}" if not c.isprintable() else f"#\\{c}"
            else:
                return f"#\\x{value:x}"
        case Vector(items):
            return "#(" + " ".join(scheme_format(x) for x in items) + ")"
        case Bytevector(data):
            return "#u8(" + " ".join(str(b) for b in data) + ")"
        case Complex(real, imag):
            real_str = scheme_format(Num(real))
            imag_str = scheme_format(Num(imag))
            sign = "+" if imag >= 0 else ""
            return f"{real_str}{sign}{imag_str}i"
        case Port() as p:
            match p:
                case ConsoleInputPort(): return "#<input-port:stdin>"
                case ConsoleOutputPort(): return "#<output-port:stdout>"
                case ConsoleErrorPort(): return "#<output-port:stderr>"
                case InputFilePort(): return "#<input-port:file>"
                case OutputFilePort(): return "#<output-port:file>"
                case InputStringPort(): return "#<input-port:string>"
                case OutputStringPort(): return "#<output-port:string>"
                case InputBytevectorPort(): return "#<input-port:bytevector>"
                case OutputBytevectorPort(): return "#<output-port:bytevector>"
                case BinaryInputFilePort(): return "#<input-port:binary-file>"
                case BinaryOutputFilePort(): return "#<output-port:binary-file>"
                case _: return "#<port>"
        case ConditionType(id, _, _):
            return f"#<condition-type {id.name}>"
        case Condition(type_, fields):
            parts = [f"#<condition {type_.id.name}"] + [f" {k}: {scheme_format(v)}" for k, v in fields.items()] + [">"]
            return "".join(parts)
        case CompoundCondition(conds):
            return f"#<compound-condition {len(conds)} components>"
        case SchemePromise():
            return "#<promise>"
        case CaseLambda():
            return "#<case-lambda>"
        case PythonObject(obj=obj):
            s = str(obj)
            if len(s) > 80:
                s = s[:77] + "..."
            return f"#<python:{type(obj).__module__}.{type(obj).__qualname__} {s}>"
        case _:
            # 尝试用 __str__ 显示自定义类型
            s = str(val)
            if s != "unknown":
                return s
            return "unknown"
