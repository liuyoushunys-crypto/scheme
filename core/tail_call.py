from typing import List, Optional, Tuple
from core.schemevalue import *
from core.schemevalue import PythonObject
from core.env import Env

def apply(proc: SchemeValue, args: List[SchemeValue], env: Env) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    result = apply_tail(proc, args, env)
    is_tc, exp, new_env = unwrap_tail(result)
    if is_tc:
        return eval_scheme(exp, new_env)
    return result

def apply_tail(proc: SchemeValue, args: List[SchemeValue], env: Env) -> SchemeValue:
    match proc:
        case Prim(_, func):
            return func(args)
        case PythonObject(obj=py_obj) if callable(py_obj):
            from eval.eval_python_import import wrap_python_value, unwrap_python_value
            # 分离位置参数与关键词参数 (:key value 模式)
            py_args = []
            py_kwargs = {}
            i = 0
            while i < len(args):
                arg = args[i]
                if isinstance(arg, Sym) and arg.name.startswith(":"):
                    kw_name = arg.name[1:]
                    if i + 1 >= len(args):
                        raise Exception(f"Missing value for keyword :{kw_name}")
                    py_kwargs[kw_name] = unwrap_python_value(args[i + 1])
                    i += 2
                else:
                    py_args.append(unwrap_python_value(arg))
                    i += 1
            try:
                result = py_obj(*py_args, **py_kwargs)
            except Exception as e:
                raise Exception(f"Python call error: {e}")
            return wrap_python_value(result)
        case PythonObject(obj=py_obj):
            # 不可调用 + 0 参数 → 当作属性访问（值本身）
            if len(args) == 0:
                return proc
            raise Exception(f"Python object is not callable: {py_obj}")
        case Continuation(func):
            val = args[0] if args else Nil()
            r = func(val)
            if r is not None:
                return r
            raise ContinuationException(val)
        case Closure() as c:
            return invoke_closure(c, args)
        case CaseLambda(clauses, env):
            for formals, body in clauses:
                raw_formals = unwrap_to_sym(formals)
                min_args = 0
                exact = False
                match raw_formals:
                    case Sym():
                        min_args = 0
                    case Nil():
                        exact = True
                        min_args = 0
                    case Cons() as f:
                        count = 0
                        curr = f
                        while isinstance(curr, Cons):
                            count += 1
                            cdr = unwrap_to_sym(curr.cdr)
                            if isinstance(cdr, Sym):
                                count = -1
                                break
                            elif isinstance(cdr, Nil):
                                exact = True
                                break
                            curr = curr.cdr
                        if count == -1:
                            min_args = 0
                            while isinstance(f, Cons):
                                min_args += 1
                                cdr = unwrap_to_sym(f.cdr)
                                if isinstance(cdr, Sym):
                                    break
                                f = f.cdr
                        else:
                            min_args = count
                if exact and len(args) != min_args:
                    continue
                if not exact and len(args) < min_args:
                    continue
                try:
                    local_env = Env(env)
                    bind_formals(formals, args, local_env)
                    curr = body
                    if isinstance(curr, Nil):
                        return Nil()
                    while isinstance(curr, Cons) and not isinstance(curr.cdr, Nil):
                        from eval.eval_scheme import eval_scheme
                        eval_scheme(curr.car, local_env)
                        curr = curr.cdr
                    if isinstance(curr, Cons):
                        return TailCallSentinel(curr.car, local_env)
                    raise Exception("Invalid case-lambda body structure")
                except Exception:
                    continue
            raise Exception("No matching clause in case-lambda")
        case Parameter(proc, value, filter_proc):
            if len(args) == 0:
                return value
            new_val = args[0]
            if filter_proc is not None:
                from eval.eval_scheme import eval_scheme
                new_val = eval_scheme(Cons(filter_proc, Cons(new_val, Nil())), env)
            proc.value = new_val
            return new_val
        case Cons() as cons:
            unpacked = unpack_list(cons)
            if unpacked and isinstance(unpacked[0], Sym) and unpacked[0].name == "primitive":
                return apply_tail(unpacked[1], args, env)
    raise Exception(f"Not a procedure: {proc}")

def unwrap_tail(result: SchemeValue) -> Tuple[bool, Optional[SchemeValue], Optional[Env]]:
    if isinstance(result, TailCallSentinel):
        return True, result.expr, result.env
    return False, None, None

def invoke_closure(closure: Closure, args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    local_env = Env(closure.env)
    bind_formals(closure.formals, args, local_env)

    curr = closure.body
    if isinstance(curr, Nil):
        return Nil()
    while isinstance(curr, Cons) and not isinstance(curr.cdr, Nil):
        eval_scheme(curr.car, local_env)
        curr = curr.cdr
    if isinstance(curr, Cons):
        return TailCallSentinel(curr.car, local_env)
    raise Exception("Invalid closure body structure")

def invoke_macro_closure(mac: MacroClosure, quoted_args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    lambda_expr = Cons(Sym("lambda"), Cons(mac.formals, mac.body))
    app_args = [lambda_expr] + quoted_args
    app_expr = to_lisp_list(app_args)
    return eval_scheme(app_expr, mac.env)

def bind_formals(formals: SchemeValue, args: List[SchemeValue], env: Env) -> None:
    formals = unwrap_to_sym(formals)
    match formals:
        case Sym() as sym:
            env.define(sym, to_lisp_list(args))
        case Nil():
            if len(args) != 0:
                raise Exception("Arity mismatch")
        case Cons() as pair:
            current = pair
            idx = 0
            while isinstance(current, Cons):
                if idx >= len(args):
                    raise Exception("Arity mismatch")
                car_sym = unwrap_to_sym(current.car)
                if isinstance(car_sym, Sym):
                    env.define(car_sym, args[idx])
                idx += 1
                cdr_val = unwrap_to_sym(current.cdr)
                if not isinstance(cdr_val, Cons) and not isinstance(cdr_val, Nil):
                    if isinstance(cdr_val, Sym):
                        env.define(cdr_val, to_lisp_list(args[idx:]))
                        return
                    raise Exception("Invalid dotted formal parameters")
                if isinstance(cdr_val, Nil):
                    break
                current = current.cdr

def lookup_macro(head: Sym, env: Env) -> Optional[SyntaxRulesMacro]:
    try:
        val = env.lookup(head)
        if isinstance(val, SyntaxRulesMacro):
            return val
    except Exception:
        pass
    return None
