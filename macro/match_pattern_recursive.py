from typing import Dict, List, Optional, Tuple
from core.schemevalue import *
from macro.pattern_utils import add_binding, parse_pattern_segments, reconstruct_list, find_pattern_vars


def match_pattern_recursive(
    pattern: SchemeValue,
    input_val: SchemeValue,
    literals: List[Sym],
    ellipsis_id: str,
    bindings: Dict[str, Tuple[int, SchemeValue]],
    expected_depths: Dict[str, int]
) -> Optional[Dict[str, Tuple[int, SchemeValue]]]:
    if isinstance(pattern, Sym) and pattern.name == "_":
        return bindings

    if isinstance(pattern, Sym) and any(l.name == pattern.name for l in literals):
        return bindings if (isinstance(input_val, Sym) and input_val.name == pattern.name) else None

    if isinstance(pattern, Sym):
        if pattern.name == ellipsis_id:
            return None
        depth = expected_depths.get(pattern.name, 0)
        return add_binding(bindings, pattern.name, depth, input_val)

    if isinstance(pattern, Nil):
        return bindings if isinstance(input_val, Nil) else None

    if isinstance(pattern, (Num, Integer, Str, Bool, Char, Complex)):
        return bindings if lisp_equal(pattern, input_val) else None

    if isinstance(pattern, Vector):
        if not isinstance(input_val, Vector):
            return None
        return match_pattern_recursive(
            to_lisp_list(pattern.items),
            to_lisp_list(input_val.items),
            literals, ellipsis_id, bindings, expected_depths
        )

    if isinstance(pattern, Cons):
        segments, tail = parse_pattern_segments(pattern, ellipsis_id)

        input_list = []
        curr = input_val
        while isinstance(curr, Cons):
            input_list.append(curr.car)
            curr = curr.cdr
        input_tail = curr

        return match_segments_recursive(
            segments, tail, input_list, input_tail, 0, 0,
            literals, ellipsis_id, bindings, expected_depths
        )

    return None


def match_segments_recursive(
    segments: List[Tuple[bool, SchemeValue]],
    tail: Optional[SchemeValue],
    input_list: List[SchemeValue],
    input_tail: SchemeValue,
    seg_idx: int,
    inp_idx: int,
    literals: List[Sym],
    ellipsis_id: str,
    bindings: Dict[str, Tuple[int, SchemeValue]],
    expected_depths: Dict[str, int]
) -> Optional[Dict[str, Tuple[int, SchemeValue]]]:
    if seg_idx == len(segments):
        if tail is not None:
            remaining_input = reconstruct_list(input_list[inp_idx:], input_tail)
            return match_pattern_recursive(tail, remaining_input, literals, ellipsis_id, bindings, expected_depths)
        else:
            if inp_idx == len(input_list) and isinstance(input_tail, Nil):
                return bindings
            return None

    is_ellipsis, sub_pat = segments[seg_idx]
    if is_ellipsis:
        max_len = len(input_list) - inp_idx
        for match_len in range(max_len + 1):
            sub_bindings_list = []
            ok = True
            for i in range(match_len):
                sub_bind = match_pattern_recursive(sub_pat, input_list[inp_idx + i], literals, ellipsis_id, {}, expected_depths)
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

            res = match_segments_recursive(
                segments, tail, input_list, input_tail, seg_idx + 1, inp_idx + match_len,
                literals, ellipsis_id, merged_bindings, expected_depths
            )
            if res is not None:
                return res
        return None
    else:
        if inp_idx >= len(input_list):
            return None
        sub_bind = match_pattern_recursive(sub_pat, input_list[inp_idx], literals, ellipsis_id, bindings, expected_depths)
        if sub_bind is not None:
            return match_segments_recursive(
                segments, tail, input_list, input_tail, seg_idx + 1, inp_idx + 1,
                literals, ellipsis_id, sub_bind, expected_depths
            )
        return None
