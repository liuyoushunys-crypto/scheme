from typing import List, Optional, Tuple
from core.schemevalue import *
from macro.expand_macro import expand_macro
from macro.compile_syntax_rules import compile_syntax_rules
from macro.pattern_utils import make_syntax_hygiene_renames
from macro.expand_syntax_template import expand_syntax_template
from macro.expand_quasisyntax import expand_quasisyntax
from eval.eval_import import eval_import, eval_define_library
from eval.eval_python_import import eval_py_import, eval_py_from_import, eval_from_form, py_get_prim, _sym_name
from eval.eval_let import eval_let, eval_let_star, eval_named_let, eval_let_rec, eval_let_values
from eval.eval_cond import eval_cond
from eval.eval_case import eval_case
from eval.eval_guard import eval_guard
from eval.eval_quasiquote import eval_quasiquote
from core.tail_call import apply, apply_tail, unwrap_tail, invoke_macro_closure, lookup_macro
from eval.eval_syntax_case import eval_syntax_case
from eval.eval_with_syntax import eval_with_syntax
from core.env import Env

def eval_scheme(exp: SchemeValue, env: Env) -> SchemeValue:
    """核心 Scheme 求值解释器（完全平坦化蹦床架构）"""
    while True:
        if isinstance(exp, TailCallSentinel):
            env = exp.env
            exp = exp.expr
            continue

        match exp:
            case Syntax(expression, syntax_env):
                target_env = env
                if syntax_env is not None:
                    if isinstance(expression, Sym):
                        if syntax_env.is_bound(expression):
                            target_env = syntax_env
                    else:
                        target_env = syntax_env
                env = target_env
                exp = expression
                continue

            case Num() | Integer() | Str() | Bool() | Char() | Vector() | Bytevector() | Port() | Prim() | Closure() | MacroClosure() | Complex() | PatternVar() | MacroTransformer() | Library() :
                return exp
            case Sym() as sym:
                if sym.name.startswith(":") or (sym.name.startswith("?") and len(sym.name) > 1 and not sym.name.startswith("??")):
                    return sym
                try:
                    return env.lookup(sym)
                except Exception:
                    if "." in sym.name:
                        from eval.eval_python_import import resolve_python_attr_chain
                        result = resolve_python_attr_chain(sym.name, env)
                        if result is not None:
                            return result
                    raise
            case Cons() as cons:
                op = cons.car
                op_env = env
                while isinstance(op, Syntax):
                    op_env = op.env if op.env is not None else op_env
                    op = op.expression
                
                match op:
                    case Sym("quote"):
                        from eval.eval_special_forms import eval_quote
                        return eval_quote(cons.cdr)
                        
                    case Sym("if"):
                        from eval.eval_special_forms import eval_if
                        result = eval_if(cons.cdr, env)
                        if isinstance(result, tuple):
                            exp, dc = result
                            if dc:
                                continue
                            return exp
                        return result
                        
                    case Sym("define"):
                        from eval.eval_special_forms import eval_define
                        return eval_define(cons.cdr, env)[0]
                        
                    case Sym("lambda"):
                        from eval.eval_special_forms import eval_lambda
                        return eval_lambda(cons.cdr, env)[0]
                        
                    case Sym("begin"):
                        from eval.eval_special_forms import eval_begin
                        result = eval_begin(cons.cdr, env)
                        if isinstance(result, tuple):
                            exp, dc = result
                            if dc:
                                continue
                            return exp
                        return result
                        
                    case Sym("set!"):
                        from eval.eval_special_forms import eval_set
                        return eval_set(cons.cdr, env)[0]
                        
                    case Sym("let"):
                        match cons.cdr:
                            case Cons(Sym() as name, Cons(bindings, body)) if isinstance(bindings, Cons):
                                exp = eval_named_let(name, bindings, body, env)
                                continue
                            case Cons(bindings, body) if isinstance(bindings, Cons):
                                exp = eval_let(bindings, body, env)
                                continue
                        raise Exception("Invalid let syntax")
                        
                    case Sym("let*"):
                        match cons.cdr:
                            case Cons(bindings, body) if isinstance(bindings, Cons):
                                exp = eval_let_star(bindings, body, env)
                                continue
                        raise Exception("Invalid let* syntax")
                        
                    case Sym("letrec"):
                        match cons.cdr:
                            case Cons(bindings, body) if isinstance(bindings, Cons):
                                exp = eval_let_rec(bindings, body, env)
                                continue
                        raise Exception("Invalid letrec syntax")
                        
                    case Sym("let-values"):
                        match cons.cdr:
                            case Cons(bindings, body) if isinstance(bindings, Cons):
                                exp = eval_let_values(bindings, body, env)
                                continue
                        raise Exception("Invalid let-values syntax")
                        
                    case Sym("cond"):
                        res = eval_cond(cons.cdr, env)
                        if isinstance(res, TailCallSentinel):
                            exp = res
                            continue
                        return res
                        
                    case Sym("case"):
                        match cons.cdr:
                            case Cons(key_exp, clauses):
                                res = eval_case(key_exp, clauses, env)
                                if isinstance(res, TailCallSentinel):
                                    exp = res
                                    continue
                                return res
                        raise Exception("Invalid case syntax")
                        
                    case Sym("and"):
                        from eval.eval_short_circuit import eval_and, is_cont
                        result = eval_and(cons.cdr, env)
                        if is_cont(result):
                            exp = result.expr
                            continue
                        return result
                        
                    case Sym("or"):
                        from eval.eval_short_circuit import eval_or, is_cont
                        result = eval_or(cons.cdr, env)
                        if is_cont(result):
                            exp = result.expr
                            continue
                        return result
                        
                    case Sym("define-syntax"):
                        from eval.eval_macro_forms import eval_define_syntax
                        return eval_define_syntax(cons.cdr, env)

                    case Sym("try"):
                        from eval.eval_try import eval_try
                        return eval_try(cons.cdr, env)

                    case Sym("match"):
                        from eval.eval_cas_dispatch import eval_match
                        return eval_match(cons.cdr, env)

                    case Sym("defrule"):
                        from eval.eval_cas_dispatch import eval_defrule
                        return eval_defrule(cons.cdr, env)

                    case Sym("rewrite"):
                        from eval.eval_cas_dispatch import eval_rewrite
                        return eval_rewrite(cons.cdr, env)

                    case Sym("index"):
                        from eval.eval_cas_dispatch import eval_index
                        return eval_index(cons.cdr)

                    case Sym("tensor"):
                        from eval.eval_cas_dispatch import eval_tensor_form
                        return eval_tensor_form(cons.cdr)

                    case Sym("contract"):
                        from eval.eval_cas_dispatch import eval_contract
                        return eval_contract(cons.cdr, env)

                    case Sym("raise-index"):
                        from eval.eval_cas_dispatch import eval_raise_index
                        return eval_raise_index(cons.cdr, env)

                    case Sym("lower-index"):
                        from eval.eval_cas_dispatch import eval_lower_index
                        return eval_lower_index(cons.cdr, env)

                    case Sym("define-macro"):
                        from eval.eval_macro_forms import eval_define_macro
                        return eval_define_macro(cons.cdr, env)

                    case Sym("case-lambda"):
                        from eval.eval_macro_forms import eval_case_lambda
                        return eval_case_lambda(cons.cdr, env)

                    case Sym("define-condition-type"):
                        from eval.eval_macro_forms import eval_define_condition_type_form
                        exp = eval_define_condition_type_form(cons.cdr)
                        continue

                    case Sym("guard"):
                        match cons.cdr:
                            case Cons(Cons() as guard_expr, body):
                                exp = eval_guard(guard_expr, body, env)
                                continue
                        raise Exception("Invalid guard syntax")

                    case Sym("quasiquote"):
                        match cons.cdr:
                            case Cons(qq_exp, Nil()):
                                return eval_quasiquote(qq_exp, 0, env)
                        raise Exception("Invalid quasiquote syntax")

                    case Sym("syntax-case"):
                        from eval.eval_macro_forms import eval_syntax_case_form
                        exp = eval_syntax_case_form(cons.cdr, env)
                        continue

                    case Sym("syntax"):
                        from eval.eval_macro_forms import eval_syntax_form
                        return eval_syntax_form(cons.cdr, env)

                    case Sym("quasisyntax"):
                        from eval.eval_macro_forms import eval_quasisyntax_form
                        return eval_quasisyntax_form(cons.cdr, env)

                    case Sym("with-syntax"):
                        from eval.eval_macro_forms import eval_with_syntax_form
                        exp = eval_with_syntax_form(cons.cdr, env)
                        continue

                    case Sym("define-library"):
                        from eval.eval_import_forms import eval_define_library_form
                        return eval_define_library_form(cons, env)

                    case Sym("import"):
                        from eval.eval_import_forms import eval_import_form
                        return eval_import_form(cons, env)

                    case Sym("py-import"):
                        from eval.eval_import_forms import eval_py_import_form
                        return eval_py_import_form(cons, env)

                    case Sym("py-from"):
                        from eval.eval_import_forms import eval_py_from_form
                        return eval_py_from_form(cons, env)

                    case Sym("from"):
                        from eval.eval_import_forms import eval_from_form_dispatch
                        return eval_from_form_dispatch(cons, env)

                    # case Sym("->"):
                        # 已迁移为宏 -- 见 eval_py_sugar.py
                        # 宏展开在 compile time 处理，更正确

                    case Sym("bracket"):
                        from eval.eval_bracket import eval_bracket_args
                        return eval_bracket_args(cons.cdr, env)

                    case Sym("."):
                        # (. obj method arg ...) -> obj.method(arg ...)
                        args_uneval = from_lisp_list(cons.cdr)
                        if len(args_uneval) < 2:
                            raise Exception(".: 需要至少 2 参数 (. obj method ...)")
                        obj = eval_scheme(args_uneval[0], env)
                        # 支持 'method 和 method 两种写法
                        method_val = args_uneval[1]
                        if isinstance(method_val, Cons) and method_val.car == Sym("quote"):
                            method_val = method_val.cdr.car
                        method_name = _sym_name(method_val)
                        method_args = [eval_scheme(a, env) for a in args_uneval[2:]]
                        
                        proc = py_get_prim([obj, Sym(method_name)])
                        if isinstance(proc, PythonObject):
                            result = apply_tail(proc, method_args, env)
                            is_tc, te, ten = unwrap_tail(result)
                            if is_tc:
                                exp = te
                                env = ten
                                continue
                            return result
                        return proc

                    case Sym() as head_sym:
                        macro = lookup_macro(head_sym, op_env)
                        if macro is not None:
                            exp = expand_macro(macro, cons, op_env)
                            continue

                        try:
                            mac_val = op_env.lookup(head_sym)
                            if isinstance(mac_val, MacroTransformer):
                                syntax_input = Syntax(cons, op_env)
                                exp = apply(mac_val.proc, [syntax_input], op_env)
                                continue
                            elif isinstance(mac_val, MacroClosure):
                                args_list = from_lisp_list(cons.cdr)
                                quoted = [Cons(Sym("quote"), Cons(a, Nil())) for a in args_list]
                                exp = invoke_macro_closure(mac_val, quoted)
                                continue
                        except Exception as e:
                            if "mac_val" in locals() and isinstance(mac_val, MacroTransformer):
                                print("--- Macro Expansion Error Traceback ---", file=sys.stderr)
                                traceback.print_exc(file=sys.stderr)
                                print("---------------------------------------", file=sys.stderr)
                                raise e
                            pass
                            
                        proc = eval_scheme(cons.car, env)
                        args = [eval_scheme(r, env) for r in from_lisp_list(cons.cdr)]
                        result = apply_tail(proc, args, env)
                        is_tc, te, ten = unwrap_tail(result)
                        if is_tc:
                            exp = te
                            env = ten
                            continue
                        return result
                        
                    case _:
                        proc2 = eval_scheme(cons.car, env)
                        args2 = [eval_scheme(r, env) for r in from_lisp_list(cons.cdr)]
                        result2 = apply_tail(proc2, args2, env)
                        is_tc, te2, ten2 = unwrap_tail(result2)
                        if is_tc:
                            exp = te2
                            env = ten2
                            continue
                        return result2
            case Nil():
                return Nil()
            case _:
                raise Exception(f"Unknown AST node: {exp}")