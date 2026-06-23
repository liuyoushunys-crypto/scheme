from core.schemevalue import *
from core.env import Env


def eval_guard(guard_expr: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    gv = guard_expr.car
    guard_clauses = from_lisp_list(guard_expr.cdr) if isinstance(guard_expr.cdr, Cons) else []

    escape_sym = Sym("escape")
    temp_exn_sym = Sym("temp-exn")

    cond_clauses = []
    has_else = False
    for clause in guard_clauses:
        unpacked = unpack_list(clause)
        if not unpacked:
            raise Exception("Invalid guard clause")
        match unpacked:
            case [Sym(name="else"), *clause_body]:
                has_else = True
                thunk = Cons(Sym("lambda"), Cons(Nil(), to_lisp_list(clause_body)))
                cond_clauses.append(Cons(Sym("else"), Cons(Cons(escape_sym, Cons(thunk, Nil())), Nil())))
            case [cond_exp, Sym(name="=>"), transformer]:
                thunk = Cons(Sym("lambda"), Cons(Nil(), Cons(Cons(transformer, Cons(gv, Nil())), Nil())))
                cond_clauses.append(Cons(cond_exp, Cons(Cons(escape_sym, Cons(thunk, Nil())), Nil())))
            case [cond_exp, *clause_body]:
                thunk = Cons(Sym("lambda"), Cons(Nil(), to_lisp_list(clause_body)))
                cond_clauses.append(Cons(cond_exp, Cons(Cons(escape_sym, Cons(thunk, Nil())), Nil())))

    if not has_else:
        re_raise_thunk = Cons(Sym("lambda"), Cons(Nil(), Cons(Cons(Sym("raise"), Cons(temp_exn_sym, Nil())), Nil())))
        cond_clauses.append(Cons(Sym("else"), Cons(Cons(escape_sym, Cons(re_raise_thunk, Nil())), Nil())))

    cond_expr = Cons(Sym("cond"), to_lisp_list(cond_clauses))

    handler_body = Cons(Sym("let"), Cons(Cons(Cons(gv, Cons(temp_exn_sym, Nil())), Nil()), Cons(cond_expr, Nil())))
    handler_lambda = Cons(Sym("lambda"), Cons(Cons(temp_exn_sym, Nil()), Cons(handler_body, Nil())))

    res_sym = Sym("res")
    body_val = Cons(Sym("begin"), body)
    escape_res_thunk = Cons(Sym("lambda"), Cons(Nil(), Cons(res_sym, Nil())))
    escape_res_call = Cons(escape_sym, Cons(escape_res_thunk, Nil()))
    body_let = Cons(Sym("let"), Cons(Cons(Cons(res_sym, Cons(body_val, Nil())), Nil()), Cons(escape_res_call, Nil())))
    body_lambda = Cons(Sym("lambda"), Cons(Nil(), Cons(body_let, Nil())))

    weh_call = Cons(Sym("with-exception-handler"), Cons(handler_lambda, Cons(body_lambda, Nil())))

    callcc_lambda = Cons(Sym("lambda"), Cons(Cons(escape_sym, Nil()), Cons(weh_call, Nil())))
    callcc_call = Cons(Sym("call-with-current-continuation"), Cons(callcc_lambda, Nil()))
    final_expr = Cons(callcc_call, Nil())

    return TailCallSentinel(final_expr, env)
