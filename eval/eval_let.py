from core.schemevalue import *
from core.tail_call import bind_formals
from core.env import Env


def eval_let(bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid let bindings")

    evaluated_bindings = []
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            sym = unwrap_to_sym(unpacked_b[0])
            if isinstance(sym, Sym):
                val = eval_scheme(unpacked_b[1], env)
                evaluated_bindings.append((sym, val))
                continue
        raise Exception("Invalid binding form in let")

    new_env = Env(env)
    for sym, val in evaluated_bindings:
        new_env.define(sym, val)

    return TailCallSentinel(Cons(Sym("begin"), body), new_env)


def eval_let_star(bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid let* bindings")

    current_env = env
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            sym = unwrap_to_sym(unpacked_b[0])
            if isinstance(sym, Sym):
                val = eval_scheme(unpacked_b[1], current_env)
                next_env = Env(current_env)
                next_env.define(sym, val)
                current_env = next_env
                continue
        raise Exception("Invalid binding form in let*")

    return TailCallSentinel(Cons(Sym("begin"), body), current_env)


def eval_named_let(name: Sym, bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid let bindings")
    vars_ = []
    init_vals = []
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            sym = unwrap_to_sym(unpacked_b[0])
            if isinstance(sym, Sym):
                vars_.append(sym)
                init_vals.append(eval_scheme(unpacked_b[1], env))
                continue
        raise Exception("Invalid binding form in let")
    local_env = Env(env)
    closure = Closure(to_lisp_list(vars_), body, local_env)
    name_sym = unwrap_to_sym(name)
    if not isinstance(name_sym, Sym):
        raise Exception("Invalid name in named let")
    local_env.define(name_sym, closure)
    return TailCallSentinel(Cons(name_sym, to_lisp_list([Cons(Sym("quote"), Cons(v, Nil())) for v in init_vals])), local_env)


def eval_let_rec(bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid letrec bindings")
    local_env = Env(env)
    vars_ = []
    val_exps = []
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            sym = unwrap_to_sym(unpacked_b[0])
            if isinstance(sym, Sym):
                vars_.append(sym)
                val_exps.append(unpacked_b[1])
                local_env.define(sym, Nil())
                continue
        raise Exception("Invalid binding form in letrec")
    for i in range(len(vars_)):
        local_env.set(vars_[i], eval_scheme(val_exps[i], local_env))
    return TailCallSentinel(Cons(Sym("begin"), body), local_env)


def eval_let_values(bindings: Cons, body: SchemeValue, env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    bind_list = unpack_list(bindings)
    if bind_list is None:
        raise Exception("Invalid let-values bindings")
    current_env = env
    for b in bind_list:
        unpacked_b = unpack_list(unwrap_to_sym(b))
        if unpacked_b is not None and len(unpacked_b) == 2:
            formals, producer_exp = unpacked_b[0], unpacked_b[1]
            produced = eval_scheme(producer_exp, current_env)
            produced_args = produced.values if isinstance(produced, SchemeValues) else [produced]
            next_env = Env(current_env)
            bind_formals(formals, produced_args, next_env)
            current_env = next_env
            continue
        raise Exception("Invalid binding form in let-values")
    return TailCallSentinel(Cons(Sym("begin"), body), current_env)
