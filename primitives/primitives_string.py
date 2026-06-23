from typing import List
from core.schemevalue import *
from core.tail_call import apply
import primitives.primitives_shared as _shared
def prim_string_fill_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Str) and isinstance(args[1], Char):
        fill_char = chr(args[1].value)
        for i in range(len(args[0].value)):
            args[0].value[i] = fill_char
        return Sym("undefined")
    raise Exception("string-fill! error")


def prim_string_set_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 3 and isinstance(args[0], Str) and isinstance(args[2], Char):
        idx = as_int(args[1])
        args[0].value[idx] = chr(args[2].value)
        return Sym("undefined")
    raise Exception("string-set! error")


def prim_string_ci_eq(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and len(set(s.get_str().lower() for s in args if isinstance(s, Str))) == 1)


def prim_string_ci_lt(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(args[i].get_str().lower() < args[i+1].get_str().lower() for i in range(len(args)-1)))


def prim_string_ci_gt(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(args[i].get_str().lower() > args[i+1].get_str().lower() for i in range(len(args)-1)))


def prim_string_ci_le(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(args[i].get_str().lower() <= args[i+1].get_str().lower() for i in range(len(args)-1)))


def prim_string_ci_ge(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) >= 2 and all(args[i].get_str().lower() >= args[i+1].get_str().lower() for i in range(len(args)-1)))


def prim_string_copy_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 3 and isinstance(args[0], Str) and isinstance(args[2], Str):
        to_str, at, from_str = args[0], as_int(args[1]), args[2]
        start = as_int(args[3]) if len(args) >= 4 else 0
        end = as_int(args[4]) if len(args) >= 5 else len(from_str.value)
        slice_chars = from_str.value[start:end]
        to_str.value[at:at+len(slice_chars)] = slice_chars
        return Sym("undefined")
    raise Exception("string-copy! error")


def make_string_fn(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("make-string error")
    length = as_int(args[0])
    fill_cp = args[1].value if len(args) >= 2 and isinstance(args[1], Char) else 0x20
    return Str([chr(fill_cp)] * length)


def prim_string_to_number(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        s = args[0].get_str()
        try:
            return Integer(int(s))
        except ValueError:
            pass
        try:
            return Num(float(s))
        except ValueError:
            pass
    return Bool(False)


def prim_string_map(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        proc = args[0]
        strings = args[1:]
        if all(isinstance(s, Str) for s in strings):
            min_len = min(len(s.value) for s in strings)
            res_chars = []
            for i in range(min_len):
                call_args = [Char(ord(s.value[i])) for s in strings]
                char_res = apply(proc, call_args, _shared.registering_env)
                if isinstance(char_res, Char):
                    res_chars.append(chr(char_res.value))
                else:
                    raise Exception("string-map: procedure must return character")
            return Str(res_chars)
    raise Exception("string-map error")


def prim_string_for_each(args: List[SchemeValue]) -> SchemeValue:
    if len(args) >= 2:
        proc = args[0]
        strings = args[1:]
        if all(isinstance(s, Str) for s in strings):
            min_len = min(len(s.value) for s in strings)
            for i in range(min_len):
                call_args = [Char(ord(s.value[i])) for s in strings]
                apply(proc, call_args, _shared.registering_env)
            return Sym("undefined")
    raise Exception("string-for-each error")


def prim_string_upcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return Str(list(args[0].get_str().upper()))
    raise Exception("string-upcase: arity mismatch")


def prim_string_downcase(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return Str(list(args[0].get_str().lower()))
    raise Exception("string-downcase: arity mismatch")


def register_string(env: 'Env') -> None:
    env.define("string", Prim("string", lambda args: Str([chr(c.value) for c in args if isinstance(c, Char)])))
    env.define("make-string", Prim("make-string", make_string_fn))
    env.define("string-length", Prim("string-length", lambda args: Integer(len(args[0].value)) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("string-length error"))))
    env.define("string-ref", Prim("string-ref", lambda args: Char(ord(args[0].value[as_int(args[1])])) if (len(args) == 2 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("string-ref error"))))
    env.define("string-copy", Prim("string-copy", lambda args: Str(list(args[0].value)) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("string-copy error"))))
    env.define("string-copy!", Prim("string-copy!", prim_string_copy_bang))
    env.define("substring", Prim("substring", lambda args: Str(args[0].value[as_int(args[1]):as_int(args[2])]) if (len(args) == 3 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("substring error"))))
    env.define("string-append", Prim("string-append", lambda args: Str(list("".join(s.get_str() for s in args if isinstance(s, Str))))))
    env.define("string->list", Prim("string->list", lambda args: to_lisp_list(Char(ord(c)) for c in args[0].value) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("string->list error"))))
    env.define("list->string", Prim("list->string", lambda args: Str([chr(c.value) for c in from_lisp_list(args[0]) if isinstance(c, Char)]) if len(args) == 1 else (_ for _ in ()).throw(Exception("list->string error"))))
    env.define("string->number", Prim("string->number", prim_string_to_number))
    env.define("number->string", Prim("number->string", lambda args: Str(list(str(args[0].value))) if (len(args) == 1 and isinstance(args[0], (Integer, Num))) else (_ for _ in ()).throw(Exception("number->string error"))))
    env.define("string->symbol", Prim("string->symbol", lambda args: Sym(args[0].get_str()) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("string->symbol error"))))
    env.define("symbol->string", Prim("symbol->string", lambda args: Str(list(args[0].name)) if (len(args) == 1 and isinstance(args[0], Sym)) else (_ for _ in ()).throw(Exception("symbol->string error"))))
    env.define("string=?", Prim("string=?", lambda args: Bool(len(args) >= 2 and len(set(s.get_str() for s in args if isinstance(s, Str))) == 1)))
    env.define("string<?", Prim("string<?", lambda args: Bool(len(args) >= 2 and all(args[i].get_str() < args[i+1].get_str() for i in range(len(args)-1)))))
    env.define("string>?", Prim("string>?", lambda args: Bool(len(args) >= 2 and all(args[i].get_str() > args[i+1].get_str() for i in range(len(args)-1)))))
    env.define("string<=?", Prim("string<=?", lambda args: Bool(len(args) >= 2 and all(args[i].get_str() <= args[i+1].get_str() for i in range(len(args)-1)))))
    env.define("string>=?", Prim("string>=?", lambda args: Bool(len(args) >= 2 and all(args[i].get_str() >= args[i+1].get_str() for i in range(len(args)-1)))))
    env.define("string-ci=?", Prim("string-ci=?", prim_string_ci_eq))
    env.define("string-ci<?", Prim("string-ci<?", prim_string_ci_lt))
    env.define("string-ci>?", Prim("string-ci>?", prim_string_ci_gt))
    env.define("string-ci<=?", Prim("string-ci<=?", prim_string_ci_le))
    env.define("string-ci>=?", Prim("string-ci>=?", prim_string_ci_ge))
    env.define("string-fill!", Prim("string-fill!", prim_string_fill_bang))
    env.define("string-set!", Prim("string-set!", prim_string_set_bang))
    env.define("string-map", Prim("string-map", prim_string_map))
    env.define("string-for-each", Prim("string-for-each", prim_string_for_each))
    env.define("string-upcase", Prim("string-upcase", prim_string_upcase))
    env.define("string-downcase", Prim("string-downcase", prim_string_downcase))
