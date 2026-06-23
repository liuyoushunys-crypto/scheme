from typing import Any, Dict, List, Optional, Tuple, Set
from core.schemevalue import *
from core.env import Env

def add_binding(bindings: Dict[str, Tuple[int, SchemeValue]], name: str, depth: int, val: SchemeValue) -> Dict[str, Tuple[int, SchemeValue]]:
    new_bindings = dict(bindings)
    new_bindings[name] = (depth, val)
    return new_bindings

def lookup_pattern_var(sym: Sym, env: Env) -> Optional[PatternVar]:
    try:
        val = env.lookup(sym)
        if isinstance(val, PatternVar):
            return val
    except Exception:
        pass
    return None

def _collect_formals(f: SchemeValue, bound_vars: Set[str]) -> None:
    f = unwrap_to_sym(f)
    if isinstance(f, Sym):
        bound_vars.add(f.name)
    elif isinstance(f, Cons):
        _collect_formals(f.car, bound_vars)
        _collect_formals(f.cdr, bound_vars)

def _collect_binding_names(bindings_list: SchemeValue, bound_vars: Set[str]) -> None:
    bindings = unpack_list(unwrap_to_sym(bindings_list))
    if bindings is not None:
        for b in bindings:
            b_unpacked = unpack_list(unwrap_to_sym(b))
            if b_unpacked is not None and len(b_unpacked) >= 1:
                sym = unwrap_to_sym(b_unpacked[0])
                if isinstance(sym, Sym):
                    bound_vars.add(sym.name)

def find_locally_bound_identifiers(template: SchemeValue) -> Set[str]:
    bound_vars: Set[str] = set()
    def walk(t):
        if isinstance(t, Cons):
            unpacked = unpack_list(t)
            if unpacked is not None and len(unpacked) >= 2:
                first = unpacked[0]
                if isinstance(first, Sym):
                    match first.name:
                        case "let" | "let*" | "letrec":
                            if len(unpacked) >= 3:
                                if isinstance(unwrap_to_sym(unpacked[1]), Sym):
                                    if len(unpacked) >= 4:
                                        name_sym = unwrap_to_sym(unpacked[1])
                                        if isinstance(name_sym, Sym):
                                            bound_vars.add(name_sym.name)
                                        _collect_binding_names(unpacked[2], bound_vars)
                                else:
                                    _collect_binding_names(unpacked[1], bound_vars)
                        case "let-values":
                            if len(unpacked) >= 3:
                                bindings = unpack_list(unwrap_to_sym(unpacked[1]))
                                if bindings is not None:
                                    for b in bindings:
                                        b_unpacked = unpack_list(unwrap_to_sym(b))
                                        if b_unpacked is not None and len(b_unpacked) >= 1:
                                            _collect_formals(b_unpacked[0], bound_vars)
                        case "lambda":
                            _collect_formals(unpacked[1], bound_vars)
                        case "define":
                            if isinstance(unpacked[1], Cons):
                                name_sym = unwrap_to_sym(unpacked[1].car)
                                if isinstance(name_sym, Sym):
                                    bound_vars.add(name_sym.name)
                                _collect_formals(unpacked[1].cdr, bound_vars)
                            else:
                                name_sym = unwrap_to_sym(unpacked[1])
                                if isinstance(name_sym, Sym):
                                    bound_vars.add(name_sym.name)
                        case "define-syntax" | "define-macro":
                            target = unwrap_to_sym(unpacked[1].car) if isinstance(unpacked[1], Cons) else unwrap_to_sym(unpacked[1])
                            if isinstance(target, Sym):
                                bound_vars.add(target.name)
                        case "do":
                            if len(unpacked) >= 2:
                                _collect_binding_names(unpacked[1], bound_vars)
                        case "case-lambda":
                            for clause in unpacked[1:]:
                                clause_unpacked = unpack_list(unwrap_to_sym(clause))
                                if clause_unpacked is not None and len(clause_unpacked) >= 1:
                                    _collect_formals(clause_unpacked[0], bound_vars)
                        case "let-syntax" | "letrec-syntax":
                            if len(unpacked) >= 3:
                                _collect_binding_names(unpacked[1], bound_vars)
            walk(t.car)
            walk(t.cdr)
        elif isinstance(t, Vector):
            for item in t.items:
                walk(item)
    walk(template)
    return bound_vars

def find_pattern_vars(pattern: SchemeValue, literals: List[Sym], ellipsis_id: str) -> List[str]:
    vars_ = []
    def walk(p):
        if isinstance(p, Sym):
            name = p.name
            if name != ellipsis_id and name != "_" and not any(l.name == name for l in literals):
                if name not in vars_:
                    vars_.append(name)
        elif isinstance(p, Cons):
            walk(p.car)
            walk(p.cdr)
        elif isinstance(p, Vector):
            for item in p.items:
                walk(item)
    walk(pattern)
    return vars_

def find_template_vars(template: SchemeValue, bindings: Dict[str, Tuple[int, SchemeValue]]) -> List[str]:
    vars_ = []
    def walk(t):
        if isinstance(t, Sym):
            if t.name in bindings:
                if t.name not in vars_:
                    vars_.append(t.name)
        elif isinstance(t, Cons):
            walk(t.car)
            walk(t.cdr)
        elif isinstance(t, Vector):
            for item in t.items:
                walk(item)
    walk(template)
    return vars_

def find_syntax_template_vars(template: SchemeValue, env: Env) -> List[str]:
    vars_ = []
    def walk(t):
        if isinstance(t, Sym):
            pvar = lookup_pattern_var(t, env)
            if pvar is not None and t.name not in vars_:
                vars_.append(t.name)
        elif isinstance(t, Cons):
            walk(t.car)
            walk(t.cdr)
        elif isinstance(t, Vector):
            for item in t.items:
                walk(item)
    walk(template)
    return vars_

def reconstruct_list(elements: List[SchemeValue], tail: SchemeValue) -> SchemeValue:
    res = tail
    for el in reversed(elements):
        res = Cons(el, res)
    return res

def parse_pattern_segments(pattern: SchemeValue, ellipsis_id: str) -> Tuple[List[Tuple[bool, SchemeValue]], Optional[SchemeValue]]:
    segments = []
    curr = pattern
    while isinstance(curr, Cons):
        if isinstance(curr.cdr, Cons) and isinstance(curr.cdr.car, Sym) and curr.cdr.car.name == ellipsis_id:
            segments.append((True, curr.car))
            curr = curr.cdr.cdr
        else:
            segments.append((False, curr.car))
            curr = curr.cdr
    return segments, (curr if not isinstance(curr, Nil) else None)

def get_pattern_vars_depth(pattern: SchemeValue, ellipsis_id: str, current_depth: int = 0) -> Dict[str, int]:
    depths = {}
    def walk(p, d):
        if isinstance(p, Sym):
            if p.name != ellipsis_id and p.name != "_":
                depths[p.name] = d
        elif isinstance(p, Cons):
            if isinstance(p.cdr, Cons) and isinstance(p.cdr.car, Sym) and p.cdr.car.name == ellipsis_id:
                walk(p.car, d + 1)
                walk(p.cdr.cdr, d)
            else:
                walk(p.car, d)
                walk(p.cdr, d)
        elif isinstance(p, Vector):
            walk(to_lisp_list(p.items), d)
    walk(pattern, current_depth)
    return depths

def get_ellipsis_loop_length(sub_tmpl: SchemeValue, bindings: Dict[str, Tuple[int, SchemeValue]], index_stack: List[int]) -> int:
    vars_ = find_template_vars(sub_tmpl, bindings)
    for v in vars_:
        depth, val = bindings[v]
        if depth > len(index_stack):
            curr = val
            for idx in index_stack:
                curr = from_lisp_list(curr)[idx]
            return len(from_lisp_list(curr))
    return 0

def get_syntax_val_and_env(val: SchemeValue, default_env: Env) -> Tuple[SchemeValue, Env]:
    if isinstance(val, Syntax):
        return val.expression, val.env
    return val, default_env


global _hygiene_counter
_hygiene_counter = 0


def collect_hygiene_renames(
    template: SchemeValue,
    literals: List[Sym],
    ellipsis_id: str,
    bindings: Dict[str, Any]
) -> Dict[str, str]:
    global _hygiene_counter
    renames = {}

    def walk(t):
        global _hygiene_counter
        if isinstance(t, Sym):
            name = t.name
            if (name not in bindings and
                name not in CORE_KEYWORDS and
                name != ellipsis_id and
                not any(l.name == name for l in literals)):
                if name not in renames:
                    _hygiene_counter += 1
                    renames[name] = f"{name}_hygiene_{_hygiene_counter}"
        elif isinstance(t, Cons):
            if isinstance(t.car, Sym) and t.car.name in ("quote", "quasiquote"):
                walk(t.car)
                return
            walk(t.car)
            walk(t.cdr)
        elif isinstance(t, Vector):
            for item in t.items:
                walk(item)

    walk(template)
    return renames


global _syntax_hygiene_counter
_syntax_hygiene_counter = 0


def make_syntax_hygiene_renames(template: SchemeValue, env: Env) -> Dict[str, str]:
    global _syntax_hygiene_counter
    renames = {}

    local_bounds = find_locally_bound_identifiers(template)
    for name in local_bounds:
        if lookup_pattern_var(Sym(name), env) is None:
            _syntax_hygiene_counter += 1
            renames[name] = f"{name}_hy_stx_{_syntax_hygiene_counter}"

    return renames


