from typing import Dict, List, Optional, Tuple
from core.schemevalue import *
from macro.pattern_utils import add_binding, parse_pattern_segments, reconstruct_list, find_pattern_vars, get_syntax_val_and_env
from core.env import Env


def match_syntax_pattern(
    pattern: SchemeValue,
    input_val: SchemeValue,
    literals: List[Sym],
    ellipsis_id: str,
    bindings: Dict[str, Tuple[int, SchemeValue]],
    expected_depths: Dict[str, int],
    default_env: Env
) -> Optional[Dict[str, Tuple[int, SchemeValue]]]:
    if isinstance(pattern, Sym) and pattern.name == "_":
        return bindings

    if isinstance(pattern, Sym) and any(l.name == pattern.name for l in literals):
        val_expr, _ = get_syntax_val_and_env(input_val, default_env)
        return bindings if (isinstance(val_expr, Sym) and val_expr.name == pattern.name) else None

    if isinstance(pattern, Sym):
        if pattern.name == ellipsis_id:
            return None
        depth = expected_depths.get(pattern.name, 0)
        return add_binding(bindings, pattern.name, depth, input_val)

    if isinstance(pattern, Nil):
        val_expr, _ = get_syntax_val_and_env(input_val, default_env)
        return bindings if isinstance(val_expr, Nil) else None

    if isinstance(pattern, (Num, Integer, Str, Bool, Char, Complex)):
        val_expr, _ = get_syntax_val_and_env(input_val, default_env)
        return bindings if lisp_equal(pattern, val_expr) else None

    if isinstance(pattern, Vector):
        val_expr, val_env = get_syntax_val_and_env(input_val, default_env)
        if not isinstance(val_expr, Vector):
            return None
        return match_syntax_pattern(
            to_lisp_list(pattern.items),
            to_lisp_list([Syntax(x, val_env) for x in val_expr.items]),
            literals, ellipsis_id, bindings, expected_depths, default_env
        )

    if isinstance(pattern, Cons):
        segments, tail = parse_pattern_segments(pattern, ellipsis_id)
        input_list = []
        curr, val_env = get_syntax_val_and_env(input_val, default_env)
        while isinstance(curr, Cons):
            el = curr.car
            if not isinstance(el, Syntax):
                el = Syntax(el, val_env)
            input_list.append(el)
            curr, val_env = get_syntax_val_and_env(curr.cdr, val_env)

        input_tail = Syntax(curr, val_env) if not isinstance(curr, Nil) else Nil()
        return match_syntax_segments(
            segments, tail, input_list, input_tail, 0, 0,
            literals, ellipsis_id, bindings, expected_depths, default_env
        )

    return None


def match_syntax_segments(
    segments: List[Tuple[bool, SchemeValue]],
    tail: Optional[SchemeValue],
    input_list: List[SchemeValue],
    input_tail: SchemeValue,
    seg_idx: int,
    inp_idx: int,
    literals: List[Sym],
    ellipsis_id: str,
    bindings: Dict[str, Tuple[int, SchemeValue]],
    expected_depths: Dict[str, int],
    default_env: Env
) -> Optional[Dict[str, Tuple[int, SchemeValue]]]:
    if seg_idx == len(segments):
        if tail is not None:
            remaining_input = reconstruct_list(input_list[inp_idx:], input_tail)
            return match_syntax_pattern(tail, remaining_input, literals, ellipsis_id, bindings, expected_depths, default_env)
        else:
            val_expr, _ = get_syntax_val_and_env(input_tail, default_env)
            if inp_idx == len(input_list) and isinstance(val_expr, Nil):
                return bindings
            return None

    is_ellipsis, sub_pat = segments[seg_idx]
    if is_ellipsis:
        max_len = len(input_list) - inp_idx
        for match_len in range(max_len + 1):
            sub_bindings_list = []
            ok = True
            for i in range(match_len):
                sub_bind = match_syntax_pattern(sub_pat, input_list[inp_idx + i], literals, ellipsis_id, {}, expected_depths, default_env)
                if sub_bind is None:
                    ok = False
                    break
                sub_bindings_list.append(sub_bind)
            if not ok:
                continue

            merged_bindings = dict(bindings)
            all_vars = find_pattern_vars(sub_pat, literals, ellipsis_id)
            for var in all_vars:
                vals = []
                for s_bind in sub_bindings_list:
                    vals.append(s_bind[var][1] if var in s_bind else Nil())
                depth = expected_depths.get(var, 1)
                merged_bindings[var] = (depth, to_lisp_list(vals))

            res = match_syntax_segments(
                segments, tail, input_list, input_tail, seg_idx + 1, inp_idx + match_len,
                literals, ellipsis_id, merged_bindings, expected_depths, default_env
            )
            if res is not None:
                return res
        return None
    else:
        if inp_idx >= len(input_list):
            return None
        sub_bind = match_syntax_pattern(sub_pat, input_list[inp_idx], literals, ellipsis_id, bindings, expected_depths, default_env)
        if sub_bind is not None:
            return match_syntax_segments(
                segments, tail, input_list, input_tail, seg_idx + 1, inp_idx + 1,
                literals, ellipsis_id, sub_bind, expected_depths, default_env
            )
        return None
