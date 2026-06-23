from core.schemevalue import *
from core.tail_call import apply_tail
from core.env import Env


def eval_case(key_exp: SchemeValue, clauses: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    key_value = eval_scheme(key_exp, env)
    curr = clauses
    while isinstance(curr, Cons):
        clause = curr.car
        unpacked = unpack_list(clause)
        if not unpacked:
            raise Exception("Invalid case clause")
        if len(unpacked) == 0:
            curr = curr.cdr
            continue
        if isinstance(unpacked[0], Sym) and unpacked[0].name == "else":
            return TailCallSentinel(Cons(Sym("begin"), to_lisp_list(unpacked[1:])), env)
        if not isinstance(unpacked[0], Cons):
            curr = curr.cdr
            continue
        keys = from_lisp_list(unpacked[0])
        for key in keys:
            if lisp_equal(key_value, key):
                if len(unpacked) >= 2 and isinstance(unpacked[1], Sym) and unpacked[1].name == "=>":
                    if len(unpacked) < 3:
                        raise Exception("case => clause requires transformer")
                    transformer = unpacked[2]
                    clause_body = unpacked[3:]
                    proc = eval_scheme(transformer, env)
                    result = apply_tail(proc, [key_value], env)
                    if isinstance(result, TailCallSentinel):
                        result = eval_scheme(result.expr, result.env)
                    if len(clause_body) == 0:
                        return result
                    body_list = Cons(result, to_lisp_list(clause_body))
                    return TailCallSentinel(Cons(Sym("begin"), body_list), env)
                if len(unpacked) >= 2:
                    return TailCallSentinel(Cons(Sym("begin"), to_lisp_list(unpacked[1:])), env)
                return key_value
        curr = curr.cdr
    return Nil()
