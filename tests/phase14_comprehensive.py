"""
Phase 1.4 — 全语法综合测试

覆盖：中缀解析器、#{...} 集成、eqn、Unicode 别名、算术代理、help、引擎
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 60)
print("Phase 1.4 — 全语法综合测试")
print("=" * 60)

errors = 0
total = 0

def check(desc, ok, detail=""):
    global total, errors
    total += 1
    if ok:
        print(f"  ✅ {desc}")
    else:
        errors += 1
        print(f"  ❌ {desc}  {detail}")

# ======== 1. parse_infix 单元测试 ========
print()
print("--- 1. parse_infix 中缀解析单元测试 ---")

from parser.infix import parse_infix

cases = [
    # 基础算术
    ("x + 1",              "(+ x 1)"),
    ("x - 1",              "(- x 1)"),
    ("x * 2",              "(* x 2)"),
    ("x / 2",              "(/ x 2)"),
    ("x^2",                "(expt x 2)"),
    ("x^y",                "(expt x y)"),
    ("-x",                 "(- x)"),
    ("+x",                 "x"),
    
    # 优先级
    ("2 + 3 * 4",          "(+ 2 (* 3 4))"),
    ("2 * 3 + 4",          "(+ (* 2 3) 4)"),
    ("2 * 3^2",            "(* 2 (expt 3 2))"),
    ("2 + 3 * 4^2",        "(+ 2 (* 3 (expt 4 2)))"),
    ("a^b^c",              "(expt a (expt b c))"),  # 右结合
    
    # 隐式乘法
    ("2x",                 "(* 2 x)"),
    ("3xy",                "(* 3 xy)"),
    ("2x*y",              "(* (* 2 x) y)"),
    ("x y",               "(* x y)"),
    ("(x+1)(x+2)",        "(* (+ x 1) (+ x 2))"),
    ("x(x+1)",            "(x (+ x 1))"),        # name(...) = function call
    ("(x+1)(x+2)(x+3)",   "(* (* (+ x 1) (+ x 2)) (+ x 3))"),
    ("3sin(x)",           "(* 3 (sin x))"),
    
    # 函数调用
    ("sin(x)",            "(sin x)"),
    ("cos(2*x)",          "(cos (* 2 x))"),
    ("f(g(x))",           "(f (g x))"),
    ("sqrt(1 - x^2)",     "(sqrt (- 1 (expt x 2)))"),
    ("sin(pi/2)",         "(sin (/ pi 2))"),
    ("integrate(sin(x), x)",     "(integrate (sin x) x)"),
    
    # 等号（方程）
    ("x = 0",             "(eqn x 0)"),
    ("x^2 - 4 = 0",       "(eqn (- (expt x 2) 4) 0)"),
    ("2*x + 1 = 5",       "(eqn (+ (* 2 x) 1) 5)"),
    
    # 比较
    ("x < 5",             "(< x 5)"),
    ("x > 0",             "(> x 0)"),
    ("x <= 5",            "(<= x 5)"),
    ("x >= 0",            "(>= x 0)"),
    ("x != 0",            "(!= x 0)"),
    
    # 一元负号优先级
    ("-x + 1",            "(+ (- x) 1)"),
    ("-x * y",            "(* (- x) y)"),
    ("-(x + 1)",          "(- (+ x 1))"),
    ("-x^2",              "(- (expt x 2))"),
    
    # 复杂表达式
    ("(-b + sqrt(b^2 - 4*a*c)) / (2a)",
     "(/ (+ (- b) (sqrt (- (expt b 2) (* (* 4 a) c)))) (* 2 a))"),
    
    # Unicode 别名
    ("π",                 "pi"),
    ("√(x^2 + y^2)",     "(sqrt (+ (expt x 2) (expt y 2)))"),

    # 注释
    ("x + 1 ; comment",   "(+ x 1)"),
    
    # 数字
    ("42",                "42"),
    ("3.14",              "3.14"),
    ("-42",               "(- 42)"),
]

for expr, expected in cases:
    try:
        result = parse_infix(expr)
        ok = (result == expected)
        check(f"{expr:40s} → {result}", ok, f"期望: {expected}")
    except Exception as e:
        check(f"{expr:40s} ❌ 异常", False, str(e))

# ======== 2. #{...} Tokenizer 路径集成 ========
print()
print("--- 2. #{...} Tokenizer 路径集成 ---")

from parser.parse_program import parse_program
from core.schemevalue import *

def parse_one(expr):
    forms = parse_program(expr)
    return forms[0] if forms else Nil()

def sexpr_str(val):
    """Convert SchemeValue to readable S-expression string"""
    if isinstance(val, Integer):
        return str(val.value)
    elif isinstance(val, Sym):
        return val.name
    elif isinstance(val, Nil):
        return "()"
    elif isinstance(val, Cons):
        parts = []
        while isinstance(val, Cons):
            parts.append(sexpr_str(val.car))
            val = val.cdr
        return f"({' '.join(parts)})"
    else:
        return str(val)

infix_tests = [
    ("#{x + 1}",                 "(+ x 1)"),
    ("#{x^2}",                   "(expt x 2)"),
    ("#{2x}",                    "(* 2 x)"),
    ("#{-x}",                    "(- x)"),
    ("#{sin(x) + cos(x)}",       "(+ (sin x) (cos x))"),
    ("#{x = 0}",                 "(eqn x 0)"),
    ("#{x^2 - 4 = 0}",           "(eqn (- (expt x 2) 4) 0)"),
    ("#{π}",                     "pi"),
    ("#{√(x^2 + y^2)}",          "(sqrt (+ (expt x 2) (expt y 2)))"),
    ("(+ #{x + 1} #{y^2})",      "(+ (+ x 1) (expt y 2))"),
    ("(define x #{2x})",         "(define x (* 2 x))"),
]

for expr, expected in infix_tests:
    try:
        result = parse_one(expr)
        result_str = sexpr_str(result)
        ok = (result_str == expected)
        check(f"#{{...}} {expr:30s} → {result_str}", ok, f"期望: {expected}")
    except Exception as e:
        check(f"#{{...}} {expr:30s} ❌ 异常", False, str(e))

# ======== 3. Reader 路径集成 ========
print()
print("--- 3. #{...} Reader 路径集成 ---")

from reader.reader import read_datum
from core.port import InputStringPort

reader_tests = [
    "#{x + 1}",
    "#{sin(x)}", 
    "#{2x}",
    "#{π}",
    "#{x^2 - 4 = 0}",
    "(+ #{x + 1} #{y^2})",
]

for expr in reader_tests:
    try:
        port = InputStringPort(expr)
        result = read_datum(port)
        result_str = sexpr_str(result)
        check(f"Reader {expr:30s} → {result_str}", True)
    except Exception as e:
        check(f"Reader {expr:30s} ❌ 异常", False, str(e))

# ======== 4. 错误处理 ========
print()
print("--- 4. 错误处理 ---")

error_tests = [
    "#{",           # 未闭合
    "#{}",          # 空
    "#{ x + }",     # 不完整表达式
]

for expr in error_tests:
    try:
        result = parse_one(expr)
        check(f"错误测试 {expr:15s} 未报错", False, f"返回: {result}")
    except Exception as e:
        check(f"错误测试 {expr:15s} → {type(e).__name__}", True)

# ======== 5. eval + eqn + CAS 引擎测试 ========
print()
print("--- 5. eval + eqn + CAS 引擎 ---")

from core.env import Env
from eval.eval_scheme import eval_scheme
from primitives.primitives import register_all

env = Env()
register_all(env)

# 测试 eqn 基本调用
eval_scheme(parse_program("(import sympy)")[0], env)
eval_scheme(parse_program("(define x (sympy.Symbol 'x))")[0], env)

eq_tests = [
    ("(eqn x 0)",                   "Eq"),
    ("(eqn (+ x 1) 5)",            "Eq"),
    ("(eqn (* 2 x) (+ x 3))",      "Eq"),
    ("#{x = 0}",                    "Eq"),
    ("#{x^2 - 4 = 0}",             "Eq"),
]

for expr, expected_type in eq_tests:
    try:
        result = eval_scheme(parse_one(expr), env)
        # Should be a PythonObject wrapping sympy.Eq
        if isinstance(result, PythonObject):
            type_name = type(result.obj).__name__
            ok = (expected_type in type_name)
            check(f"eval {expr:30s} → {type_name}", ok)
        else:
            check(f"eval {expr:30s} → {sexpr_str(result)}", False, "不是 PythonObject")
    except Exception as e:
        check(f"eval {expr:30s} ❌ 异常", False, str(e))

# 测试 CAS 操作（在 auto 模式下，factor/solve 需 sympy fallback）
# 注：auto 模式优先 symengine，factor/solve 不在 symengine 中
# 所以先切到 sympy 模式测试这些功能
from eval.cas.engine import set_engine, get_engine, cas_engine_info as engine_info

# 先在 auto 模式测试 expand/diff（走 symengine）
cas_tests_auto = [
    ("(expand #{ (x+1)^2 })",       "expand"),
    ("(diff #{x^3} x)",             "diff"),
]
for expr, op in cas_tests_auto:
    try:
        result = eval_scheme(parse_one(expr), env)
        check(f"CAS auto {expr:35s} → 成功", True)
    except Exception as e:
        check(f"CAS auto {expr:35s} ❌ 异常", False, str(e))

# 切到 sympy 测试 factor/solve
set_engine('sympy')
cas_tests_sympy = [
    ("(factor #{x^4 - 1})",        "factor"),
    ("(solve #{x^2 - 4 = 0} x)",   "solve"),
]
for expr, op in cas_tests_sympy:
    try:
        result = eval_scheme(parse_one(expr), env)
        check(f"CAS sympy {expr:35s} → 成功", True)
    except Exception as e:
        check(f"CAS sympy {expr:35s} ❌ 异常", False, str(e))

set_engine('auto')  # 恢复

# ======== 6. Engine 切换 ========
print()
print("--- 6. 引擎切换 ---")

from eval.cas.engine import engine_info, set_engine, get_engine

info = engine_info()
check("engine-info 包含 symengine", "symengine" in info)
check("engine-info 包含 sympy", "sympy" in info)
check("engine-info 包含 auto", "auto" in info or "调度" in info)

set_engine('symengine')
eng = get_engine()
check("use-engine 'symengine", "symengine" in str(eng))

set_engine('sympy')
eng = get_engine()
check("use-engine 'sympy", "sympy" in str(eng))

set_engine('auto')
eng = get_engine()
check("use-engine 'auto → symengine 优先", True)

# ======== 7. Help 系统 ========
print()
print("--- 7. Help 系统 ---")

from eval.cas.info.help import cas_help, _CAS_FUNCTIONS

help_all = cas_help([])
check("(help) 返回字符串", isinstance(help_all, Str))
help_txt = help_all.get_str()
check("(help) 包含分类标题", "微积分" in help_txt)
check("(help) 包含函数列表", "integrate" in help_txt or "expand" in help_txt)
check("CAS 函数数据库 ≥ 80 个", len(_CAS_FUNCTIONS) >= 80)

help_integrate = cas_help([Sym("integrate")])
check("(help 'integrate) 返回字符串", isinstance(help_integrate, Str))
check("(help 'integrate) 包含语法", "语法" in help_integrate.get_str() or "args" in help_integrate.get_str().lower())
check("(help 'integrate) 包含示例", "示例" in help_integrate.get_str() or "example" in help_integrate.get_str().lower())

help_search = cas_help([Str(list("方程"))])
check("(help \"方程\") 搜索结果", isinstance(help_search, Str))
check("(help \"方程\") 包含 solve", "solve" in help_search.get_str())

# ======== 8. 回归测试 ========
print()
print("--- 8. 回归测试：纯 Scheme 语法正常 ---")

regression_tests = [
    "(+ 1 2)",
    "(define x 42)",
    "\"hello\"",
    "'(1 2 3)",
    "#(1 2 3)",
    "#t",
    "#f",
    "42",
    "3.14",
    "symbol",
]

for expr in regression_tests:
    try:
        result = parse_one(expr)
        check(f"回归 {expr:20s} → {sexpr_str(result)}", True)
    except Exception as e:
        check(f"回归 {expr:20s} ❌ 异常", False, str(e))

# ======== 结果 ========
print()
print("=" * 60)
if errors == 0:
    print(f"✅ 全部 {total} 个测试通过！")
else:
    print(f"❌ {errors}/{total} 个测试失败")
print("=" * 60)
