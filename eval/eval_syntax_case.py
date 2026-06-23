from typing import List
import traceback
import sys
from core.schemevalue import *
from macro.pattern_utils import get_pattern_vars_depth
from macro.match_syntax_pattern import match_syntax_pattern
from core.env import Env


def eval_syntax_case(expr_val: SchemeValue, literals_val: SchemeValue, clauses_val: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    try:
        input_syntax = eval_scheme(expr_val, env)
        if not isinstance(input_syntax, Syntax):
            input_syntax = Syntax(input_syntax, env)

        literals = []
        lits_unpacked = unpack_list(literals_val)
        if lits_unpacked is not None:
            literals = [x for x in lits_unpacked if isinstance(x, Sym)]

        curr = clauses_val
        ellipsis_id = "..."
        while isinstance(curr, Cons):
            clause = curr.car
            unpacked = unpack_list(clause)
            if unpacked is None or len(unpacked) not in (2, 3):
                raise Exception("Invalid syntax-case clause")

            pattern = unpacked[0]
            if len(unpacked) == 2:
                fender = None
                output_expr = unpacked[1]
            else:
                fender = unpacked[1]
                output_expr = unpacked[2]

            expected_depths = get_pattern_vars_depth(pattern, ellipsis_id)
            bindings = match_syntax_pattern(pattern, input_syntax, literals, ellipsis_id, {}, expected_depths, env)
            if bindings is not None:
                local_env = Env(env)
                for name, (depth, val) in bindings.items():
                    local_env.define(Sym(name), PatternVar(depth, val))

                if fender is not None:
                    fender_res = eval_scheme(fender, local_env)
                    if isinstance(fender_res, Bool) and not fender_res.value:
                        curr = curr.cdr
                        continue

                return TailCallSentinel(output_expr, local_env)

            curr = curr.cdr

        raise Exception(f"syntax-case: no matching clause for {scheme_format(input_syntax)}")
    except Exception as e:
        print("--- eval_syntax_case Error Traceback ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("----------------------------------------", file=sys.stderr)
        raise e
