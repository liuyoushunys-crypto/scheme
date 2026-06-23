import os
import sys
import time
from typing import List
from core.schemevalue import *


def prim_current_second(args: List[SchemeValue]) -> SchemeValue:
    return Num(time.time())


def prim_current_jiffy(args: List[SchemeValue]) -> SchemeValue:
    return Integer(int(time.perf_counter() * 1_000_000))


def prim_jiffies_per_second(args: List[SchemeValue]) -> SchemeValue:
    return Integer(1_000_000)


def prim_exit(args: List[SchemeValue]) -> SchemeValue:
    sys.exit(as_int(args[0]) if args else 0)


def prim_file_exists(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return Bool(os.path.exists(args[0].get_str()))
    raise Exception("file-exists? error")


def prim_delete_file(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        os.remove(args[0].get_str())
        return Sym("undefined")
    raise Exception("delete-file error")


def prim_command_line(args: List[SchemeValue]) -> SchemeValue:
    return to_lisp_list(Str(list(arg)) for arg in sys.argv)


def prim_get_environment_variable(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        val = os.getenv(args[0].get_str())
        return Str(list(val)) if val is not None else Bool(False)
    raise Exception("get-environment-variable error")


def prim_get_environment_variables(args: List[SchemeValue]) -> SchemeValue:
    bindings = []
    for k, v in os.environ.items():
        bindings.append(Cons(Str(list(k)), Str(list(v))))
    return to_lisp_list(bindings)



def register_system(env: 'Env') -> None:
    import gc as python_gc
    from eval.eval_scheme import eval_scheme
    from eval.eval_quasiquote import eval_quasiquote
    from primitives.primitives_control import prim_defined, prim_gensym, prim_make_closure
    from primitives.primitives_io import prim_load
    from primitives.primitives_misc import prim_get_closure_code
    env.define("defined?", Prim("defined?", prim_defined))
    env.define("load", Prim("load", prim_load))
    env.define("eval", Prim("eval", lambda args: eval_scheme(args[0], args[1].env) if (len(args) == 2 and isinstance(args[1], EnvValue)) else (_ for _ in ()).throw(Exception("eval error"))))
    env.define("quasiquote", Prim("quasiquote", lambda args: eval_quasiquote(args[0], 0, env) if len(args) > 0 else (_ for _ in ()).throw(Exception("quasiquote arity mismatch"))))
    env.define("interaction-environment", Prim("interaction-environment", lambda _: EnvValue(env)))
    env.define("current-environment", Prim("current-environment", lambda _: EnvValue(env)))
    env.define("gensym", Prim("gensym", prim_gensym))
    env.define("get-closure-code", Prim("get-closure-code", prim_get_closure_code))
    env.define("make-closure", Prim("make-closure", prim_make_closure))
    env.define("macro-expand", Prim("macro-expand", lambda args: (_ for _ in ()).throw(Exception("macro-expand not implemented"))))
    env.define("gc", Prim("gc", lambda _: python_gc.collect() or Sym("undefined")))
    env.define("gc-verbose", Prim("gc-verbose", lambda _: Sym("undefined")))
    env.define("exit", Prim("exit", prim_exit))
    env.define("quit", Prim("quit", prim_exit))
    env.define("current-second", Prim("current-second", prim_current_second))
    env.define("current-jiffy", Prim("current-jiffy", prim_current_jiffy))
    env.define("jiffies-per-second", Prim("jiffies-per-second", prim_jiffies_per_second))
    env.define("file-exists?", Prim("file-exists?", prim_file_exists))
    env.define("delete-file", Prim("delete-file", prim_delete_file))
    env.define("command-line", Prim("command-line", prim_command_line))
    env.define("get-environment-variable", Prim("get-environment-variable", prim_get_environment_variable))
    env.define("get-environment-variables", Prim("get-environment-variables", prim_get_environment_variables))
