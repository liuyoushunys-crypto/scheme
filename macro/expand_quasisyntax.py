from typing import List
from core.schemevalue import *
from macro.pattern_utils import get_syntax_val_and_env
from macro.expand_syntax_template import expand_syntax_template
from core.env import Env


def expand_quasisyntax(
    val: SchemeValue,
    depth: int,
    env: Env,
    index_stack: List[int],
    ellipsis_id: str
) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    if not isinstance(val, Cons):
        return expand_syntax_template(val, env, index_stack, ellipsis_id)

    unpacked = unpacked_val = unpack_list(val)
    if unpacked_val is not None:
        match unpacked_val:
            case [Sym(name="unsyntax"), sub_exp]:
                if depth == 0:
                    return eval_scheme(sub_exp, env)
                return Cons(Sym("unsyntax"), Cons(expand_quasisyntax(sub_exp, depth - 1, env, index_stack, ellipsis_id), Nil()))
            case [Sym(name="quasisyntax"), sub_exp]:
                return Cons(Sym("quasisyntax"), Cons(expand_quasisyntax(sub_exp, depth + 1, env, index_stack, ellipsis_id), Nil()))

    if isinstance(val.car, Cons):
        car_unpacked = unpack_list(val.car)
        if car_unpacked is not None:
            match car_unpacked:
                case [Sym(name="unsyntax-splicing"), splice_exp]:
                    if depth == 0:
                        spliced_val = eval_scheme(splice_exp, env)
                        spliced_expr, _ = get_syntax_val_and_env(spliced_val, env)
                        return append_lists(spliced_expr, expand_quasisyntax(val.cdr, depth, env, index_stack, ellipsis_id))

    return Cons(
        expand_quasisyntax(val.car, depth, env, index_stack, ellipsis_id),
        expand_quasisyntax(val.cdr, depth, env, index_stack, ellipsis_id)
    )
