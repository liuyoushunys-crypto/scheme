from core.schemevalue import *
from core.env import Env


def eval_quasiquote(val: SchemeValue, depth: int, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    if not isinstance(val, Cons):
        return val
    unpacked = unpack_list(val)
    if unpacked is not None:
        match unpacked:
            case [Sym(name="unquote"), sub_exp]:
                if depth == 0:
                    return eval_scheme(sub_exp, env)
                return Cons(Sym("unquote"), Cons(eval_quasiquote(sub_exp, depth - 1, env), Nil()))
            case [Sym(name="quasiquote"), sub_exp]:
                return Cons(Sym("quasiquote"), Cons(eval_quasiquote(sub_exp, depth + 1, env), Nil()))

    if isinstance(val.car, Cons):
        car_unpacked = unpack_list(val.car)
        if car_unpacked is not None:
            match car_unpacked:
                case [Sym(name="unquote-splicing"), splice_exp]:
                    if depth == 0:
                        return append_lists(eval_scheme(splice_exp, env), eval_quasiquote(val.cdr, depth, env))

    return Cons(eval_quasiquote(val.car, depth, env), eval_quasiquote(val.cdr, depth, env))
