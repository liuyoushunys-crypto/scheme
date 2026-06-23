from typing import List, Tuple
from core.schemevalue import *
from core.tail_call import apply


def eval_define_condition_type(rest: SchemeValue) -> SchemeValue:
    parsed = unpack_list(rest)
    if parsed is None or len(parsed) < 4:
        raise Exception("define-condition-type: invalid syntax")
    name, parent, ctor, pred = parsed[0], parsed[1], parsed[2], parsed[3]
    field_pairs_raw = parsed[4:] if len(parsed) > 4 else []
    field_pairs = []
    for p in field_pairs_raw:
        fp = unpack_list(p)
        if fp is not None and len(fp) == 2:
            field_pairs.append((fp[0], fp[1]))
        else:
            raise Exception("define-condition-type: field spec must be (field accessor)")
    field_names = [fp[0] for fp in field_pairs]
    accessors = [fp[1] for fp in field_pairs]

    kv_pairs = []
    for fn in field_names:
        kv_pairs.append(Cons(Sym("quote"), Cons(fn, Nil())))
        kv_pairs.append(fn)

    exprs = []

    exprs.append(
        Cons(Sym("define"),
            Cons(name,
                Cons(
                    Cons(Sym("make-condition-type"),
                        to_lisp_list([
                            Cons(Sym("quote"), Cons(name, Nil())),
                            parent,
                            Cons(Sym("quote"), Cons(to_lisp_list(field_names), Nil()))
                        ])),
                    Nil()))))

    exprs.append(
        Cons(Sym("define"),
            Cons(ctor,
                Cons(
                    Cons(Sym("lambda"),
                        to_lisp_list([
                            to_lisp_list(field_names),
                            Cons(Sym("make-condition"),
                                Cons(name,
                                    to_lisp_list(kv_pairs)))
                        ])),
                    Nil()))))

    exprs.append(
        Cons(Sym("define"),
            Cons(pred,
                Cons(
                    Cons(Sym("lambda"),
                        to_lisp_list([
                            Cons(Sym("obj"), Nil()),
                            Cons(Sym("condition-has-type?"),
                                to_lisp_list([Sym("obj"), name]))
                        ])),
                    Nil()))))

    for fn, an in zip(field_names, accessors):
        exprs.append(
            Cons(Sym("define"),
                Cons(an,
                    Cons(
                        Cons(Sym("lambda"),
                            to_lisp_list([
                                Cons(Sym("c"), Nil()),
                                Cons(Sym("condition-ref"),
                                    to_lisp_list([
                                        Sym("c"),
                                        Cons(Sym("quote"), Cons(fn, Nil()))
                                    ]))
                            ])),
                        Nil()))))

    return Cons(Sym("begin"), to_lisp_list(exprs))