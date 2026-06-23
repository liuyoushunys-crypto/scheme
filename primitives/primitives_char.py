from typing import List
from core.schemevalue import *


def prim_char_alphabetic(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            return Bool(chr(val).isalpha())
    return Bool(False)


def prim_char_lower_case(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            return Bool(chr(val).islower())
    return Bool(False)


def prim_char_numeric(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            return Bool(chr(val).isdigit())
    return Bool(False)


def prim_char_upper_case(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            return Bool(chr(val).isupper())
    return Bool(False)


def prim_char_whitespace(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            return Bool(chr(val).isspace())
        return Bool(val in (0x1680, 0x2000))
    return Bool(False)


def prim_char_downcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        return Char(ord(chr(args[0].value).lower()))
    raise Exception("char-downcase: expected character")


def prim_char_upcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        return Char(ord(chr(args[0].value).upper()))
    raise Exception("char-upcase: expected character")


def prim_digit_value(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Char):
        val = args[0].value
        if val < 0x10000:
            c = chr(val)
            if c.isdigit():
                return Integer(ord(c) - ord('0'))
            if c.isalpha():
                lower = c.lower()
                if 'a' <= lower <= 'f':
                    return Integer(ord(lower) - ord('a') + 10)
            if c in ('i', 'I'):
                return Integer(-1)
            return Bool(False)
        return Bool(False)
    raise Exception("digit-value: expected character")


def prim_char_ci_gt(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2 and all(isinstance(x, Char) for x in args):
        for i in range(len(args) - 1):
            c1 = chr(args[i].value).lower()
            c2 = chr(args[i+1].value).lower()
            if c1 <= c2:
                return Bool(False)
        return Bool(True)
    raise Exception("char-ci>?: expected characters")


def prim_char_ci_lt(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(chr(args[i].value).lower() < chr(args[i+1].value).lower() for i in range(len(args)-1)))


def prim_char_ci_le(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(chr(args[i].value).lower() <= chr(args[i+1].value).lower() for i in range(len(args)-1)))


def prim_char_ci_ge(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(chr(args[i].value).lower() >= chr(args[i+1].value).lower() for i in range(len(args)-1)))


def register_char_predicates(env: 'Env') -> None:
    env.define("char->integer", Prim("char->integer", lambda args: Integer(args[0].value) if (len(args) == 1 and isinstance(args[0], Char)) else (_ for _ in ()).throw(Exception("char->integer error"))))
    env.define("integer->char", Prim("integer->char", lambda args: Char(as_int(args[0])) if len(args) == 1 else (_ for _ in ()).throw(Exception("integer->char error"))))
    env.define("char=?", Prim("char=?", lambda args: Bool(len(args) >= 2 and len(set(c.value for c in args if isinstance(c, Char))) == 1)))
    env.define("char<?", Prim("char<?", lambda args: Bool(len(args) >= 2 and all(args[i].value < args[i+1].value for i in range(len(args)-1)))))
    env.define("char>?", Prim("char>?", lambda args: Bool(len(args) >= 2 and all(args[i].value > args[i+1].value for i in range(len(args)-1)))))
    env.define("char<=?", Prim("char<=?", lambda args: Bool(len(args) >= 2 and all(args[i].value <= args[i+1].value for i in range(len(args)-1)))))
    env.define("char>=?", Prim("char>=?", lambda args: Bool(len(args) >= 2 and all(args[i].value >= args[i+1].value for i in range(len(args)-1)))))
    env.define("char-ci=?", Prim("char-ci=?", lambda args: Bool(len(args) >= 2 and len(set(ord(chr(c.value).lower()) for c in args if isinstance(c, Char))) == 1)))
    env.define("char-ci<?", Prim("char-ci<?", prim_char_ci_lt))
    env.define("char-ci>?", Prim("char-ci>?", prim_char_ci_gt))
    env.define("char-ci<=?", Prim("char-ci<=?", prim_char_ci_le))
    env.define("char-ci>=?", Prim("char-ci>=?", prim_char_ci_ge))
    env.define("char-alphabetic?", Prim("char-alphabetic?", prim_char_alphabetic))
    env.define("char-lower-case?", Prim("char-lower-case?", prim_char_lower_case))
    env.define("char-upper-case?", Prim("char-upper-case?", prim_char_upper_case))
    env.define("char-numeric?", Prim("char-numeric?", prim_char_numeric))
    env.define("char-whitespace?", Prim("char-whitespace?", prim_char_whitespace))
    env.define("char-downcase", Prim("char-downcase", prim_char_downcase))
    env.define("char-upcase", Prim("char-upcase", prim_char_upcase))
    env.define("digit-value", Prim("digit-value", prim_digit_value))
