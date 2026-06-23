"""
Bracket notation [obj key ...] - Python-style indexing and slicing.

Syntax:
  [obj idx]             -> obj[idx]
  [obj (list lo hi)]    -> obj[lo:hi]
  [obj start stop step] -> obj[start:stop:step]
  [obj i j ...]         -> obj[i, j, ...]  multi-dim
  [obj 0 : 2 1 : 3]     -> obj[0:2, 1:3]  natural slice
  [obj : 5]             -> obj[:5]
  [obj 3 :]             -> obj[3:]
  [obj :]               -> obj[:]
  [obj 1 : 7 : 2]       -> obj[1:7:2]
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value, py_get_prim


def eval_bracket_args(cons_cdr, env):
    """Evaluate [obj key ...] syntax - collect args + dispatch"""
    from eval.eval_scheme import eval_scheme
    args_list = []
    curr = cons_cdr
    while isinstance(curr, Cons):
        args_list.append(eval_scheme(curr.car, env))
        curr = curr.cdr
    return eval_bracket(args_list, env)


def eval_bracket(args_list, env):
    """Evaluate bracket expression [obj key ...]"""
    if len(args_list) < 2:
        raise Exception("bracket: need at least 2 arguments [obj key ...]")

    obj = args_list[0]
    indices = args_list[1:]

    # Does it contain : slice marker?
    has_colon = any(isinstance(a, Sym) and a.name == ':' for a in indices)

    if has_colon:
        return _eval_slice_bracket(obj, indices)
    
    # No colon -> original logic
    match len(args_list):
        case 2:
            obj, key = args_list
            if isinstance(key, Cons):
                py_key = unwrap_python_value(key)
                if isinstance(py_key, list) and 2 <= len(py_key) <= 3:
                    slice_obj = wrap_python_value(slice(*py_key))
                    return py_get_prim([obj, slice_obj])
            return py_get_prim(args_list)
        case 4:
            obj, start, stop, step = args_list
            slice_obj = wrap_python_value(slice(
                unwrap_python_value(start),
                unwrap_python_value(stop),
                unwrap_python_value(step)))
            return py_get_prim([obj, slice_obj])
        case _:
            py_indices = []
            for a in args_list[1:]:
                if isinstance(a, Cons):
                    py_val = unwrap_python_value(a)
                    if isinstance(py_val, list) and 2 <= len(py_val) <= 3:
                        py_indices.append(slice(*py_val))
                    else:
                        py_indices.append(py_val)
                else:
                    py_indices.append(unwrap_python_value(a))
            if isinstance(obj, PythonObject):
                try:
                    return wrap_python_value(obj.obj[tuple(py_indices)])
                except Exception as e:
                    raise Exception(f"index error: {e}")
            raise Exception("bracket: only supports PythonObject")


def _eval_slice_bracket(obj, indices):
    """Handle : slice syntax: [obj start : stop : step ...]"""
    cols = [unwrap_python_value(a) for a in indices
            if not (isinstance(a, Sym) and a.name == ':')]
    colon_pos = [i for i, a in enumerate(indices)
                 if isinstance(a, Sym) and a.name == ':']

    py_entries = {}
    consumed = set()

    for cp in colon_pos:
        if cp - 1 not in consumed and cp + 1 not in consumed:
            left_val = None
            right_val = None
            step_val = None
            has_left = cp > 0 and cp - 1 not in consumed
            has_right = cp + 1 < len(indices) and cp + 1 not in consumed

            dim_pos = (cp - 1) if has_left else cp

            if has_left:
                left_val = unwrap_python_value(indices[cp - 1])
                consumed.add(cp - 1)

            # Check for :: pattern (second colon = step)
            if (has_right
                and isinstance(indices[cp + 1], Sym)
                and indices[cp + 1].name == ':'):
                consumed.add(cp + 1)
                if cp + 2 < len(indices) and cp + 2 not in consumed:
                    step_val = unwrap_python_value(indices[cp + 2])
                    consumed.add(cp + 2)
            elif has_right:
                right_val = unwrap_python_value(indices[cp + 1])
                consumed.add(cp + 1)
                # Check for step (val : val : step)
                if (cp + 2 < len(indices)
                    and isinstance(indices[cp + 2], Sym)
                    and indices[cp + 2].name == ':'
                    and cp + 3 < len(indices)
                    and cp + 3 not in consumed):
                    step_val = unwrap_python_value(indices[cp + 3])
                    consumed.add(cp + 2)
                    consumed.add(cp + 3)

            consumed.add(cp)
            py_entries[dim_pos] = slice(left_val, right_val, step_val)

    # Non-paired values as scalar dimensions
    for i, a in enumerate(indices):
        if i not in consumed:
            py_entries[i] = unwrap_python_value(a)

    # Sort by position
    py_indices = [v for _, v in sorted(py_entries.items())]

    if isinstance(obj, PythonObject):
        try:
            return wrap_python_value(obj.obj[tuple(py_indices)])
        except Exception as e:
            raise Exception(f"index error: {e}")
    raise Exception("bracket: only supports PythonObject")
