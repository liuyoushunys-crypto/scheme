from core.schemevalue import *
from macro.pattern_utils import get_pattern_vars_depth
from macro.match_syntax_pattern import match_syntax_pattern
from core.env import Env


def eval_with_syntax(bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid with-syntax bindings")

    current_env = env
    ellipsis_id = "..."
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            pattern, expr = unpacked_b[0], unpacked_b[1]
            val = eval_scheme(expr, current_env)
            if not isinstance(val, Syntax):
                val = Syntax(val, current_env)

            expected_depths = get_pattern_vars_depth(pattern, ellipsis_id)
            bindings_map = match_syntax_pattern(pattern, val, [], ellipsis_id, {}, expected_depths, current_env)
            if bindings_map is None:
                raise Exception("with-syntax: pattern failed to match")

            next_env = Env(current_env)
            for name, (depth, v) in bindings_map.items():
                next_env.define(Sym(name), PatternVar(depth, v))
            current_env = next_env
            continue
        raise Exception("Invalid binding form in with-syntax")

    return TailCallSentinel(Cons(Sym("begin"), body), current_env)
