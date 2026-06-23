from core.schemevalue import *
from core.tail_call import apply_tail
from core.env import Env


def eval_cond(clauses: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    curr = clauses
    while isinstance(curr, Cons):
        clause = curr.car
        unpacked = unpack_list(clause)
        if not unpacked:
            raise Exception("Invalid cond clause")
        match unpacked:
            case [Sym(name="else"), *body]:
                return TailCallSentinel(Cons(Sym("begin"), to_lisp_list(body)), env)
            case [test_exp, *rest_body]:
                test_val = eval_scheme(test_exp, env)
                if not (isinstance(test_val, Bool) and not test_val.value):
                    if len(rest_body) >= 2 and isinstance(rest_body[0], Sym) and rest_body[0].name == "=>":
                        transformer = rest_body[1]
                        clause_body = rest_body[2:]
                        proc = eval_scheme(transformer, env)
                        result = apply_tail(proc, [test_val], env)
                        if isinstance(result, TailCallSentinel):
                            result = eval_scheme(result.expr, result.env)
                        if len(clause_body) == 0:
                            return result
                        body_list = Cons(result, to_lisp_list(clause_body))
                        return TailCallSentinel(Cons(Sym("begin"), body_list), env)
                    return test_val if len(rest_body) == 0 else TailCallSentinel(Cons(Sym("begin"), to_lisp_list(rest_body)), env)
        curr = curr.cdr
    return Bool(False)
