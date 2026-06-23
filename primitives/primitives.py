import gc as python_gc
from typing import List, Optional
from core.schemevalue import *
from core.tail_call import apply
from eval.eval_scheme import eval_scheme
from eval.eval_import import global_libraries
from macro.compile_syntax_rules import compile_syntax_rules
from parser.parse_program import parse, parse_program
from reader.reader import read_datum
from primitives.primitives_arith import *
from primitives.primitives_list import *
from primitives.primitives_eq import *
from primitives.primitives_string import *
from primitives.primitives_vector import *
from primitives.primitives_bytevector import *
from primitives.primitives_hashtable import *
from primitives.primitives_system import *
from primitives.primitives_condition import register_condition
from primitives.primitives_missing import register_missing
from primitives.primitives_type import register_type_predicates
from primitives.primitives_eq import register_comparison
from primitives.primitives_list import register_pairs
from primitives.primitives_arith import register_arithmetic
from primitives.primitives_char import register_char_predicates
from primitives.primitives_string import register_string
from primitives.primitives_vector import register_vector
from primitives.primitives_bytevector import register_bytevector
from primitives.primitives_control import register_control
from primitives.primitives_iter import register_iter
from primitives.primitives_io import register_io
from primitives.primitives_system import register_system
from primitives.primitives_hashtable import register_hashtable
from primitives.primitives_syntax import register_syntax_primitives
from eval.eval_python_import import register_python_import_primitives
from eval.cas.core import register_core_primitives
from eval.cas.viz import register_viz_primitives
from eval.cas.info.help import register_help_primitives
from eval.cas.engine import register_engine_primitives
from eval.cas.assume import register_assume_primitives
from eval.cas.numerical import register_numerical_primitives
from eval.cas.bridge import register_bridge_primitives
from eval.cas.info.ecosystem import register_ecosystem_primitives
try:
    from eval.cas.numpy import register_numpy_primitives
except ModuleNotFoundError:
    register_numpy_primitives = None
try:
    from eval.cas.learn import register_learn_primitives
except ModuleNotFoundError:
    register_learn_primitives = None
from eval.cas.info.catalog import register_catalog_primitives
from eval.cas.sugar import register_sugar_primitives
from eval.cas.info.nav import register_nav_primitives
from eval.cas.pattern import register_pattern_primitives
from eval.cas.tensor import register_tensor_primitives
from eval.cas.parse import register_parse_primitives
from eval.data.json import register_json_primitives
from eval.text.re import register_re_primitives
from eval.io.path import register_path_primitives
from eval.io.http import register_http_primitives
from eval.system.datetime import register_datetime_primitives
from eval.system.system import register_system_primitives
from eval.crypto.crypto import register_crypto_primitives
from eval.data.csv import register_csv_primitives
from eval.io.compress import register_compress_primitives
from eval.data.serialize import register_serialize_primitives
from eval.io.db import register_db_primitives
from eval.io.image import register_image_primitives
from eval.cas.entry import register_entry_primitives
from eval.cas.py import register_py_sugar_primitives
import primitives.primitives_shared as _shared
from core.env import Env

registering_env = None


def register_all(env: Env) -> None:
    global registering_env
    _shared.registering_env = env
    registering_env = env

    register_type_predicates(env)
    register_comparison(env)
    register_pairs(env)
    register_arithmetic(env)
    register_char_predicates(env)
    register_string(env)
    register_vector(env)
    register_bytevector(env)
    register_control(env)
    register_iter(env)
    register_io(env)
    register_system(env)
    register_hashtable(env)
    register_syntax_primitives(env)
    register_condition(env)
    register_missing(env)
    register_python_import_primitives(env)
    register_core_primitives(env)
    register_viz_primitives(env)
    register_help_primitives(env)
    register_engine_primitives(env)
    register_assume_primitives(env)
    register_numerical_primitives(env)
    register_bridge_primitives(env)
    register_ecosystem_primitives(env)
    if register_numpy_primitives:
        register_numpy_primitives(env)
    if register_learn_primitives:
        register_learn_primitives(env)
    register_catalog_primitives(env)
    register_sugar_primitives(env)
    register_entry_primitives(env)
    register_py_sugar_primitives(env)
    register_nav_primitives(env)
    register_pattern_primitives(env)
    register_tensor_primitives(env)
    register_parse_primitives(env)
    register_json_primitives(env)
    register_re_primitives(env)
    register_path_primitives(env)
    register_http_primitives(env)
    register_datetime_primitives(env)
    register_system_primitives(env)
    register_crypto_primitives(env)
    register_csv_primitives(env)
    register_compress_primitives(env)
    register_serialize_primitives(env)
    register_db_primitives(env)
    register_image_primitives(env)

    # when/unless macros
    from parser.parse_program import parse
    when_syntax = compile_syntax_rules(parse("(syntax-rules () ((when test body ...) (if test (begin body ...))))"), env)
    unless_syntax = compile_syntax_rules(parse("(syntax-rules () ((unless test body ...) (if (not test) (begin body ...))))"), env)
    env.define("when", when_syntax)
    env.define("unless", unless_syntax)

    # defsym: 便捷创建 sympy 符号（非卫生宏，需引用 sympy.Symbol）
    # (defsym x y z) → (begin (define x (sympy.Symbol 'x)) (define y (sympy.Symbol 'y)) (define z (sympy.Symbol 'z)))
    defsym_code = "(define-macro (defsym . symbols) (cons 'begin (map (lambda (s) (list 'define s (list 'sympy.Symbol (list 'quote s)))) symbols)))"
    eval_scheme(parse(defsym_code), env)

    # with-symbols: 临时创建符号
    # (with-symbols (x y) body ...) → 
    #   (let ((x (sympy.Symbol 'x)) (y (sympy.Symbol 'y))) body ...)
    with_syms_code = "(define-macro (with-symbols symbols . body) (cons 'let (cons (map (lambda (s) (list s (list 'sympy.Symbol (list 'quote s)))) symbols) body)))"
    eval_scheme(parse(with_syms_code), env)

    # describe: 查看 Python 对象文档
    # (describe sympy.diff) 用 Prim 实现，已注册

    # py->: 简化 py-eval, (py-> (+ x 1)) → (py-eval "+ x 1") 等
    # 实际由 Prim 处理，macro 更复杂，暂不实现

    register_standard_libraries(env)


def register_standard_libraries(env: Env) -> None:
    # 1. (scheme base)
    scheme_base_env = Env()
    for k, v in env._bindings.items():
        scheme_base_env.define(k, v)

    core_syntax_names = [
        "quote", "if", "define", "lambda", "begin", "set!", "let", "let*", "letrec",
        "let-values", "cond", "case", "and", "or", "define-syntax", "define-macro",
        "guard", "quasiquote", "unquote", "unquote-splicing", "syntax-case", "syntax",
        "quasisyntax", "with-syntax", "define-condition-type", "case-lambda"
    ]
    exports = [Sym(k) for k in scheme_base_env._bindings.keys()]
    for name in core_syntax_names:
        exports.append(Sym(name))

    global_libraries[("scheme", "base")] = Library(("scheme", "base"), exports, scheme_base_env)

    def reg_lib(lib_name, export_names):
        lib_env = Env()
        for k in export_names:
            if k in env._bindings:
                lib_env.define(k, env._bindings[k])
        global_libraries[lib_name] = Library(lib_name, [Sym(k) for k in export_names], lib_env)

    # 2. (scheme write)
    reg_lib(("scheme", "write"), ["display", "write", "write-shared", "write-simple", "newline"])

    # 3. (scheme file)
    reg_lib(("scheme", "file"), [
        "open-input-file", "open-output-file", "open-binary-input-file", "open-binary-output-file",
        "close-input-port", "close-output-port", "close-port",
        "call-with-input-file", "call-with-output-file",
        "with-input-from-file", "with-output-to-file",
        "file-exists?", "delete-file"
    ])

    # 4. (scheme process-context)
    reg_lib(("scheme", "process-context"), [
        "exit", "quit", "command-line",
        "get-environment-variable", "get-environment-variables", "emergency-exit"
    ])

    # 5. (scheme time)
    reg_lib(("scheme", "time"), ["current-second", "current-jiffy", "jiffies-per-second"])

    # 6. (scheme lazy)
    reg_lib(("scheme", "lazy"), ["delay", "delay-force", "force", "make-promise", "promise?"])

    # 7. (scheme case-lambda)
    reg_lib(("scheme", "case-lambda"), ["case-lambda"])

    # 8. (scheme char)
    reg_lib(("scheme", "char"), [
        "char-alphabetic?", "char-ci<=?", "char-ci<?", "char-ci=?", "char-ci>=?", "char-ci>?",
        "char-downcase", "char-foldcase", "char-lower-case?", "char-numeric?",
        "char-upcase", "char-upper-case?", "char-whitespace?", "digit-value",
        "string-ci<=?", "string-ci<?", "string-ci=?", "string-ci>=?", "string-ci>?",
        "string-downcase", "string-foldcase", "string-upcase"
    ])

    # 9. (scheme complex)
    reg_lib(("scheme", "complex"), [
        "angle", "imag-part", "magnitude", "make-polar", "make-rectangular", "real-part"
    ])

    # 10. (scheme cxr)
    reg_lib(("scheme", "cxr"), [
        "caaar", "caaadr", "caaar", "caadar", "caaddr", "caadr",
        "cadaar", "cadadr", "cadar", "caddar", "cadddr", "caddr",
        "cdaaar", "cdaadr", "cdaar", "cdadar", "cdaddr", "cdadr",
        "cddaar", "cddadr", "cddar", "cdddar", "cddddr", "cdddr"
    ])

    # 11. (scheme eval)
    reg_lib(("scheme", "eval"), ["eval", "environment"])

    # 12. (scheme inexact)
    reg_lib(("scheme", "inexact"), [
        "acos", "asin", "atan", "cos", "exp", "finite?", "infinite?",
        "log", "nan?", "sin", "sqrt", "tan"
    ])

    # 13. (scheme load)
    reg_lib(("scheme", "load"), ["load"])

    # 14. (scheme read)
    reg_lib(("scheme", "read"), ["read"])

    # 15. (scheme repl)
    reg_lib(("scheme", "repl"), ["interaction-environment"])


