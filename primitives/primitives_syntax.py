from typing import List
from core.schemevalue import *
import primitives.primitives_shared as _shared


def prim_syntax_to_datum(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("syntax->datum: arity mismatch")
    return unwrap_syntax(args[0])


def prim_datum_to_syntax(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("datum->syntax: arity mismatch")
    template_id, datum = args[0], args[1]
    return datum_to_syntax(template_id, datum)


def prim_syntax_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], Syntax))


def prim_generate_temporaries(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("generate-temporaries: arity mismatch")
    from macro.pattern_utils import get_syntax_val_and_env
    expr, env = get_syntax_val_and_env(args[0], None)
    lst = from_lisp_list(expr)
    temps = []
    for _ in lst:
        _shared.gensym_counter += 1
        sym = Sym(f"t_{_shared.gensym_counter}")
        temps.append(Syntax(sym, env))
    return to_lisp_list(temps)


def prim_bound_identifier_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("bound-identifier=?: arity mismatch")
    id1, id2 = args[0], args[1]
    if not isinstance(id1, Syntax) or not isinstance(id1.expression, Sym):
        return Bool(False)
    if not isinstance(id2, Syntax) or not isinstance(id2.expression, Sym):
        return Bool(False)
    return Bool(id1.expression.name == id2.expression.name and id1.env is id2.env)


def prim_free_identifier_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("free-identifier=?: arity mismatch")
    id1, id2 = args[0], args[1]
    if not isinstance(id1, Syntax) or not isinstance(id1.expression, Sym):
        return Bool(False)
    if not isinstance(id2, Syntax) or not isinstance(id2.expression, Sym):
        return Bool(False)
    sym1 = id1.expression
    sym2 = id2.expression
    if sym1.name != sym2.name:
        return Bool(False)
    binding1 = None
    binding2 = None
    try:
        if id1.env is not None:
            binding1 = id1.env.lookup(sym1)
    except Exception:
        pass
    try:
        if id2.env is not None:
            binding2 = id2.env.lookup(sym2)
    except Exception:
        pass
    return Bool(binding1 is binding2)


def register_syntax_primitives(env: 'Env') -> None:
    env.define("syntax->datum", Prim("syntax->datum", prim_syntax_to_datum))
    env.define("datum->syntax", Prim("datum->syntax", prim_datum_to_syntax))
    env.define("syntax?", Prim("syntax?", prim_syntax_p))
    env.define("generate-temporaries", Prim("generate-temporaries", prim_generate_temporaries))
    env.define("free-identifier=?", Prim("free-identifier=?", prim_free_identifier_p))
    env.define("bound-identifier=?", Prim("bound-identifier=?", prim_bound_identifier_p))
