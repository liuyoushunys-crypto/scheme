from typing import Dict, List, Tuple
from core.schemevalue import *
from macro.pattern_utils import get_ellipsis_loop_length


def expand_template_recursive(
    template: SchemeValue,
    bindings: Dict[str, Tuple[int, SchemeValue]],
    ellipsis_id: str,
    index_stack: List[int],
    hygiene_renames: Dict[str, str]
) -> SchemeValue:
    match template:
        case Sym(name):
            if name in bindings:
                depth, val = bindings[name]
                curr = val
                use_indices = index_stack[:depth]
                for idx in use_indices:
                    curr = from_lisp_list(curr)[idx]
                return curr
            if name in hygiene_renames:
                return Sym(hygiene_renames[name])
            return template

        case Nil():
            return Nil()

        case Vector(items):
            expanded_list = expand_template_recursive(
                to_lisp_list(items), bindings, ellipsis_id, index_stack, hygiene_renames
            )
            return Vector(from_lisp_list(expanded_list))

        case Cons() as cons:
            if isinstance(cons.cdr, Cons) and isinstance(cons.cdr.car, Sym) and cons.cdr.car.name == ellipsis_id:
                sub_tmpl = cons.car
                rest_tmpl = cons.cdr.cdr

                loop_len = get_ellipsis_loop_length(sub_tmpl, bindings, index_stack)
                expanded_elements = []
                for i in range(loop_len):
                    new_stack = index_stack + [i]
                    expanded_elements.append(
                        expand_template_recursive(sub_tmpl, bindings, ellipsis_id, new_stack, hygiene_renames)
                    )
                rest_expanded = expand_template_recursive(rest_tmpl, bindings, ellipsis_id, index_stack, hygiene_renames)
                return append_lists(to_lisp_list(expanded_elements), rest_expanded)

            return Cons(
                expand_template_recursive(cons.car, bindings, ellipsis_id, index_stack, hygiene_renames),
                expand_template_recursive(cons.cdr, bindings, ellipsis_id, index_stack, hygiene_renames)
            )

    return template
