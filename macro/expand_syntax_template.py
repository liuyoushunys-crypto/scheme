from typing import Dict, List, Optional
from core.schemevalue import *
from macro.pattern_utils import lookup_pattern_var, get_syntax_val_and_env, find_syntax_template_vars
from core.env import Env


def expand_syntax_template(
    template: SchemeValue,
    env: Env,
    index_stack: List[int] = None,
    ellipsis_id: str = "...",
    renames: Optional[Dict[str, str]] = None
) -> SchemeValue:
    if index_stack is None:
        index_stack = []
    if renames is None:
        renames = {}

    match template:
        case Sym(name):
            pvar = lookup_pattern_var(template, env)
            if pvar is not None:
                depth, val = pvar.depth, pvar.value
                curr = val
                use_indices = index_stack[:depth]
                for idx in use_indices:
                    curr_expr, _ = get_syntax_val_and_env(curr, env)
                    curr = from_lisp_list(curr_expr)[idx]
                return curr
            if name in renames:
                return Sym(renames[name])
            return Syntax(template, env)

        case Nil():
            return Nil()

        case Vector(items):
            expanded_list = expand_syntax_template(
                to_lisp_list(items), env, index_stack, ellipsis_id, renames
            )
            return Vector(from_lisp_list(expanded_list))

        case Cons() as cons:
            if isinstance(cons.cdr, Cons) and isinstance(cons.cdr.car, Sym) and cons.cdr.car.name == ellipsis_id:
                sub_tmpl = cons.car
                rest_tmpl = cons.cdr.cdr

                vars_ = find_syntax_template_vars(sub_tmpl, env)
                loop_len = 0
                for v in vars_:
                    pvar = lookup_pattern_var(Sym(v), env)
                    if pvar is not None and pvar.depth > len(index_stack):
                        curr = pvar.value
                        for idx in index_stack:
                            curr_expr, _ = get_syntax_val_and_env(curr, env)
                            curr = from_lisp_list(curr_expr)[idx]
                        curr_expr, _ = get_syntax_val_and_env(curr, env)
                        loop_len = len(from_lisp_list(curr_expr))
                        break

                expanded_elements = []
                for i in range(loop_len):
                    new_stack = index_stack + [i]
                    expanded_elements.append(
                        expand_syntax_template(sub_tmpl, env, new_stack, ellipsis_id, renames)
                    )
                rest_expanded = expand_syntax_template(rest_tmpl, env, index_stack, ellipsis_id, renames)
                return append_lists(to_lisp_list(expanded_elements), rest_expanded)

            return Cons(
                expand_syntax_template(cons.car, env, index_stack, ellipsis_id, renames),
                expand_syntax_template(cons.cdr, env, index_stack, ellipsis_id, renames)
            )

    return template
