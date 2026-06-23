from typing import List, Dict, Optional
from core.schemevalue import *
import primitives.primitives_shared as _shared


def prim_condition_type_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], ConditionType))


def prim_condition_p(args: List[SchemeValue]) -> SchemeValue:
    return Bool(len(args) == 1 and isinstance(args[0], (Condition, CompoundCondition)))


def prim_make_condition_type(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("make-condition-type: arity mismatch")
    tid = args[0]
    if not isinstance(tid, Sym):
        raise Exception("make-condition-type: id must be a symbol")
    parent = args[1]
    supertypes = []
    if isinstance(parent, ConditionType):
        supertypes.append(parent)
    elif not isinstance(parent, Nil):
        raise Exception("make-condition-type: parent must be a condition-type or ()")
    field_names = []
    if len(args) >= 3:
        fields_list = args[2]
        fields = unpack_list(unwrap_to_sym(fields_list))
        if fields is not None:
            for f in fields:
                if isinstance(f, Sym):
                    field_names.append(f.name)
                else:
                    raise Exception("make-condition-type: field names must be symbols")
    return ConditionType(tid, supertypes, field_names)


def prim_make_condition(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("make-condition: arity mismatch")
    ct = args[0]
    if not isinstance(ct, ConditionType):
        raise Exception("make-condition: first argument must be a condition-type")
    fields = {}
    i = 1
    while i + 1 < len(args):
        if not isinstance(args[i], Sym):
            raise Exception("make-condition: field keys must be symbols")
        fields[args[i].name] = args[i + 1]
        i += 2
    all_field_names = ct.get_all_fields()
    for key in fields:
        if key not in all_field_names:
            raise Exception(f"make-condition: unknown field '{key}' for {ct.id.name}")
    return Condition(ct, fields)


def prim_condition_has_type_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("condition-has-type?: arity mismatch")
    cond = args[0]
    ct = args[1]
    if not isinstance(ct, ConditionType):
        raise Exception("condition-has-type?: second argument must be a condition-type")
    if isinstance(cond, Condition):
        return Bool(cond.type.is_subtype(ct))
    elif isinstance(cond, CompoundCondition):
        for c in cond.conditions:
            if c.type.is_subtype(ct):
                return Bool(True)
        return Bool(False)
    return Bool(False)


def prim_condition_ref(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("condition-ref: arity mismatch")
    cond = args[0]
    field_name = args[1]
    if not isinstance(field_name, Sym):
        raise Exception("condition-ref: field name must be a symbol")
    if isinstance(cond, Condition):
        return cond.fields[field_name.name]
    elif isinstance(cond, CompoundCondition):
        for c in cond.conditions:
            if field_name.name in c.fields:
                return c.fields[field_name.name]
        raise Exception(f"condition-ref: field '{field_name.name}' not found")
    raise Exception("condition-ref: first argument must be a condition")


def prim_make_compound_condition(args: List[SchemeValue]) -> SchemeValue:
    conditions = []
    for a in args:
        if isinstance(a, Condition):
            conditions.append(a)
        elif isinstance(a, CompoundCondition):
            conditions.extend(a.conditions)
        else:
            raise Exception("make-compound-condition: arguments must be conditions")
    if len(conditions) == 1:
        return conditions[0]
    return CompoundCondition(conditions)


def prim_extract_condition(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("extract-condition: arity mismatch")
    cond = args[0]
    ct = args[1]
    if not isinstance(ct, ConditionType):
        raise Exception("extract-condition: second argument must be a condition-type")
    if isinstance(cond, Condition):
        if cond.type.is_subtype(ct):
            return cond
        raise Exception(f"extract-condition: condition is not of type {ct.id.name}")
    elif isinstance(cond, CompoundCondition):
        for c in cond.conditions:
            if c.type.is_subtype(ct):
                return c
        raise Exception(f"extract-condition: no component of type {ct.id.name}")
    raise Exception("extract-condition: first argument must be a condition")


def register_condition_types(env) -> None:
    _shared.registering_env = env

    env.define("&condition",
               ConditionType(Sym("&condition"), [], []))

    env.define("&message",
               ConditionType(Sym("&message"), [env.lookup(Sym("&condition"))], ["message"]))

    env.define("&warning",
               ConditionType(Sym("&warning"), [env.lookup(Sym("&condition"))], []))

    env.define("&serious",
               ConditionType(Sym("&serious"), [env.lookup(Sym("&condition"))], []))

    env.define("&error",
               ConditionType(Sym("&error"), [env.lookup(Sym("&serious"))], []))

    env.define("&violation",
               ConditionType(Sym("&violation"), [env.lookup(Sym("&serious"))], []))

    env.define("&assertion",
               ConditionType(Sym("&assertion"), [env.lookup(Sym("&violation"))], []))

    env.define("&irritants",
               ConditionType(Sym("&irritants"), [env.lookup(Sym("&condition"))], ["irritants"]))

    env.define("&i/o",
               ConditionType(Sym("&i/o"), [env.lookup(Sym("&serious"))], []))

    env.define("&i/o-read",
               ConditionType(Sym("&i/o-read"), [env.lookup(Sym("&i/o"))], []))

    env.define("&i/o-write",
               ConditionType(Sym("&i/o-write"), [env.lookup(Sym("&i/o"))], []))

    env.define("&i/o-invalid-position",
               ConditionType(Sym("&i/o-invalid-position"), [env.lookup(Sym("&i/o"))], []))

    env.define("&i/o-filename",
               ConditionType(Sym("&i/o-filename"), [env.lookup(Sym("&i/o"))], ["filename"]))

    env.define("&i/o-port",
               ConditionType(Sym("&i/o-port"), [env.lookup(Sym("&i/o"))], ["port"]))

    env.define("&lexical",
               ConditionType(Sym("&lexical"), [env.lookup(Sym("&violation"))], []))

    env.define("&syntax",
               ConditionType(Sym("&syntax"), [env.lookup(Sym("&violation"))], ["expression"]))

    env.define("&undefined",
               ConditionType(Sym("&undefined"), [env.lookup(Sym("&violation"))], []))

    env.define("&implementation-restriction",
               ConditionType(Sym("&implementation-restriction"), [env.lookup(Sym("&violation"))], []))

    env.define("&no-inspector",
               ConditionType(Sym("&no-inspector"), [env.lookup(Sym("&violation"))], []))

    env.define("&interrupt",
               ConditionType(Sym("&interrupt"), [env.lookup(Sym("&condition"))], []))


def register_condition(env) -> None:
    _shared.registering_env = env
    register_condition_types(env)

    env.define("condition?", Prim("condition?", prim_condition_p))
    env.define("condition-type?", Prim("condition-type?", prim_condition_type_p))
    env.define("make-condition-type", Prim("make-condition-type", prim_make_condition_type))
    env.define("make-condition", Prim("make-condition", prim_make_condition))
    env.define("condition-has-type?", Prim("condition-has-type?", prim_condition_has_type_p))
    env.define("condition-ref", Prim("condition-ref", prim_condition_ref))
    env.define("extract-condition", Prim("extract-condition", prim_extract_condition))
    env.define("make-compound-condition", Prim("make-compound-condition", prim_make_compound_condition))

    env.define("message-condition?", Prim("message-condition?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&message"))))))
    env.define("serious-condition?", Prim("serious-condition?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&serious"))))))
    env.define("error?", Prim("error?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&error"))))))
    env.define("violation?", Prim("violation?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&violation"))))))
    env.define("assertion-violation?", Prim("assertion-violation?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&assertion"))))))
    env.define("irritants-condition?", Prim("irritants-condition?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&irritants"))))))
    env.define("lexical-violation?", Prim("lexical-violation?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&lexical"))))))
    env.define("syntax-violation?", Prim("syntax-violation?", lambda args: Bool(isinstance(args[0], (Condition, CompoundCondition)) and condition_has_type(args[0], env.lookup(Sym("&syntax"))))))

    env.define("condition-message", Prim("condition-message", lambda args: condition_ref_field(args[0], "message")))
    env.define("condition-irritants", Prim("condition-irritants", lambda args: condition_ref_field(args[0], "irritants")))


def condition_has_type(cond, ct):
    if isinstance(cond, Condition):
        return cond.type.is_subtype(ct)
    elif isinstance(cond, CompoundCondition):
        for c in cond.conditions:
            if c.type.is_subtype(ct):
                return True
    return False


def condition_ref_field(cond, field):
    if isinstance(cond, Condition):
        return cond.fields[field]
    elif isinstance(cond, CompoundCondition):
        for c in cond.conditions:
            if field in c.fields:
                return c.fields[field]
    raise Exception(f"condition field '{field}' not found")