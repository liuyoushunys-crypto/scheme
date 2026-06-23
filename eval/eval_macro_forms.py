"""
Macro & syntax special forms extracted from eval_scheme.

Handles:
  define-syntax, define-macro, case-lambda,
  syntax (#'), quasisyntax (#`), with-syntax
"""

from typing import List
from core.schemevalue import *
from macro.compile_syntax_rules import compile_syntax_rules
from macro.pattern_utils import make_syntax_hygiene_renames
from macro.expand_syntax_template import expand_syntax_template
from macro.expand_quasisyntax import expand_quasisyntax
from eval.eval_syntax_case import eval_syntax_case
from eval.eval_with_syntax import eval_with_syntax


def eval_define_syntax(cdr, env):
    """(define-syntax name transformer-expr)"""
    from core.schemevalue import Cons, Nil, Sym
    match cdr:
        case Cons(Sym() as name, Cons(transformer_exp, Nil())):
            is_syntax_rules = False
            if isinstance(transformer_exp, Cons):
                first = transformer_exp.car
                if isinstance(first, Sym) and first.name == "syntax-rules":
                    is_syntax_rules = True
            if is_syntax_rules:
                env.define(name, compile_syntax_rules(transformer_exp, env))
            else:
                from eval.eval_scheme import eval_scheme
                transformer = eval_scheme(transformer_exp, env)
                env.define(name, MacroTransformer(transformer))
            return Sym("undefined")
    raise Exception("Invalid define-syntax syntax")


def eval_define_macro(cdr, env):
    """(define-macro (name formals ...) body ...)"""
    from core.schemevalue import Cons, Nil, Sym
    match cdr:
        case Cons(Cons(Sym() as macro_name, macro_formals), macro_body):
            env.define(macro_name, MacroClosure(macro_formals, macro_body, env))
            return Sym("undefined")
    raise Exception("Invalid define-macro syntax")


def eval_case_lambda(cdr, env):
    """(case-lambda (formals body ...) ...)"""
    from core.schemevalue import Cons, Nil
    from core.schemevalue import from_lisp_list, CaseLambda
    match cdr:
        case clauses_val:
            clauses_list = from_lisp_list(clauses_val)
            parsed_clauses = []
            for clause in clauses_list:
                if isinstance(clause, Cons):
                    formals = clause.car
                    body = clause.cdr
                    parsed_clauses.append((formals, body))
                else:
                    raise Exception("Invalid case-lambda clause")
            return CaseLambda(parsed_clauses, env)
    raise Exception("Invalid case-lambda syntax")


def eval_syntax_form(cdr, env):
    """(syntax template) -> #'template"""
    from core.schemevalue import Cons, Nil, Sym
    match cdr:
        case Cons(template, Nil()):
            renames = make_syntax_hygiene_renames(template, env)
            for orig, hygienic in renames.items():
                try:
                    val = env.lookup(Sym(orig))
                    env.define(Sym(hygienic), val)
                except Exception:
                    pass
            return expand_syntax_template(template, env, [], "...", renames)
    raise Exception("Invalid syntax syntax")


def eval_quasisyntax_form(cdr, env):
    """(quasisyntax template) -> #`template"""
    from core.schemevalue import Cons, Nil
    match cdr:
        case Cons(template, Nil()):
            return expand_quasisyntax(template, 0, env, [], "...")
    raise Exception("Invalid quasisyntax syntax")


def eval_with_syntax_form(cdr, env):
    """(with-syntax (pat expr) ...) body ...)"""
    from core.schemevalue import Cons
    match cdr:
        case Cons(bindings, body) if isinstance(bindings, Cons):
            return eval_with_syntax(bindings, body, env)
    raise Exception("Invalid with-syntax syntax")


def eval_define_condition_type_form(cdr, env):
    """(define-condition-type name parent pred fields...)"""
    from eval.eval_condition import eval_define_condition_type
    return eval_define_condition_type(cdr)


def eval_syntax_case_form(cdr, env):
    """(syntax-case expr (literal ...) clause ...)"""
    from core.schemevalue import Cons
    match cdr:
        case Cons(expr_val, Cons(literals_val, clauses_val)):
            from eval.eval_scheme import eval_scheme
            return eval_syntax_case(expr_val, literals_val, clauses_val, env)
    raise Exception("Invalid syntax-case syntax")
