"""
语法糖增强 — 让 Scheme 更自然、更简洁。

提供：
  ->   线程宏 (thread-first)    (-> x f1 f2 f3)  → (f3 (f2 (f1 x)))
  ->>  线程宏 (thread-last)     (->> x f1 f2 f3) → (f3 (f2 (f1 x)))
  \u03bb    lambda 别名              (\u03bb (x) (* x 2))  → (lambda (x) (* x 2))
  for  列表推导                  (for (x xs) (expt x 2)) → 结果列表
  str  字符串插值                (str "x = " x)  → "x = 42"

P0:
  with   上下文管理器              (with (open f) body...)
  pmatch 模式匹配                 (pmatch expr [(+ a b) body] ...)

P1:
  define-data 记录类型            (define-data Point (x y))
  yield/define-gen 生成器         (define-gen (fib) ... (yield n) ...)
"""

from typing import List
from core.schemevalue import *
from eval.eval_scheme import eval_scheme
from core.tail_call import apply_tail, unwrap_tail
from eval.eval_python_import import unwrap_python_value, wrap_python_value


# ==================== 线程宏 -> 和 ->> ====================

def cas_thread_first(args: List[SchemeValue], env: 'Env') -> SchemeValue:
    """
    (-> x f1 f2 ...) → 线程优先宏
    每个函数的返回值作为下一个函数的第一个参数。
    
    示例:
      (-> #{x^2 + 1} (diff x) expand)
      (-> 5 (* 2) (+ 1))  → 11
    """
    from core.schemevalue import from_lisp_list
    raise Exception("内部错误: -> 应在 eval_scheme 中处理")


# ==================== 注册宏 (定义在 Scheme 层面) ====================

# \u03bb 宏: (\u03bb args body) → (lambda args body)
_LAMBDA_MACRO_CODE = """
(define-macro (\u03bb . rest)
  (cons 'lambda rest))
"""

# for 宏: (for (x xs) expr ...) → (map (lambda (x) expr ...) xs)
_FOR_MACRO_CODE = """
(define-macro (for bindings . body)
  (let ((var (car bindings))
        (iter (cadr bindings)))
    (list 'map (cons 'lambda (cons (list var) body)) iter)))
"""

# -> 宏: (-> x f1 f2 ...) → 嵌套调用
_THREAD_FIRST_MACRO = """
(define-macro (-> x . forms)
  (if (null? forms)
      x
      (let ((form (car forms))
            (rest (cdr forms)))
        (if (pair? form)
            (let ((result (append (list (car form) x) (cdr form))))
              (if (null? rest) result
                  (cons '-> (cons result (cdr forms)))))
            (if (null? rest) (list form x)
                (cons '-> (cons (list form x) (cdr forms))))))))
"""

# ->> 宏: (->> x f1 f2 ...) → 嵌套调用 (参数在最后)
_THREAD_LAST_MACRO = """
(define-macro (->> x . forms)
  (if (null? forms)
      x
      (let ((form (car forms))
            (rest (cdr forms)))
        (if (pair? form)
            (let ((result (append form (list x))))
              (if (null? rest) result
                  (cons '->> (cons result (cdr forms)))))
            (if (null? rest) (list form x)
                (cons '->> (cons (list form x) (cdr forms))))))))
"""

# str 宏: (str "hello " name) → 拼接字符串
_STR_MACRO_CODE = """
(define-macro (str . args)
  (cons 'string-append (map (lambda (a) (if (string? a) a (list 'number->string a))) args)))
"""

# try/catch — 用 define-macro + quasiquote 实现
_TRY_CATCH_CODE = """
(define-macro (try body handler)
  (list 'call-with-current-continuation
    (list 'lambda (list 'k)
      (list 'with-exception-handler
        (list 'lambda (list 'e)
          (list 'k (list (cadr handler) 'e)))
        (list 'lambda () body)))))
"""

# ==================== P0: with 上下文管理器 ====================

_WITH_MACRO_CODE = """
(define-macro (with init var . body)
  (list 'call-with-current-continuation
    (list 'lambda (list 'k)
      (list 'with-exception-handler
        (list 'lambda (list '%e)
          (list 'close-port var)
          (list 'k '%e))
        (list 'lambda ()
          (list 'let (list (list var init))
            (list 'begin
              (cons 'begin body)
              (list 'close-port var))))))))
"""

# ==================== P0: pmatch 模式匹配 ====================

_MATCH_HELPER = """
(define (%range n)
  (let loop ((i 1) (acc '()))
    (if (> i n) (reverse acc)
      (loop (+ i 1) (cons i acc)))))
"""

_PMATCH_MACRO_CODE = """
(define-macro (pmatch expr . clauses)
  (let ((v '%v))
    (list 'let (list (list v expr))
      (cons 'cond
        (map (lambda (clause)
               (if (eq? (car clause) 'else)
                   (cons #t (cdr clause))
                 (let ((pat (car clause))
                       (body (cdr clause)))
                   (list
                     (list 'and
                       (list 'pair? v)
                       (list 'equal? (list 'car v) (list 'quote (car pat)))
                       (list '= (list 'length v)
                             (+ 1 (length (cdr pat)))))
                     (list 'let
                       (map (lambda (p i)
                              (list p (list 'list-ref v i)))
                            (cdr pat)
                            (%range (length (cdr pat))))
                       (cons 'begin body))))))
             clauses)))))
"""

# ==================== P1: define-data 记录类型 ====================

_DEFINE_DATA_MACRO = """
(define-macro (define-data name . fields)
  (list 'define (cons name fields)
    (cons 'list (cons (list 'quote name) fields))))
"""

# ==================== P2: 增强赋值 ====================

_P2_AUGMENT = """
(begin
  (define-macro (+= var val) (list 'set! var (list '+ var val)))
  (define-macro (-= var val) (list 'set! var (list '- var val)))
  (define-macro (*= var val) (list 'set! var (list '* var val)))
  (define-macro (/= var val) (list 'set! var (list '/ var val))))
"""

# ==================== P2: 多重赋值/交换 ====================

_P2_MULTI = """
(define-macro (swap a b)
  (let ((_t a))
    (list 'let (list (list '_t a))
      (list 'begin
        (list 'set! a b)
        (list 'set! b '_t)))))
"""

# ==================== P2: 列表解构赋值 ====================

_P2_DESTRUCT = """
(define-macro (set!-values vars expr)
  (let ((_v '%_v))
    (list 'let (list (list '_v expr))
      (cons 'begin
        (map (lambda (v i)
               (list 'set! v (list 'list-ref '_v i)))
             vars
             (%range (length vars)))))))
"""

# ==================== SymPy: sym 宏（自动 import + 符号创建）====================

_SYM_SYM = """
(define-macro (sym . symbols)
  (cons 'begin
    (cons '(import sympy)
      (map (lambda (s) (list 'define s (list 'sympy.Symbol (list 'quote s))))
           symbols))))
"""

# ==================== SymPy: lambdify 宏 ====================

_SYM_LAMBDIFY = """
(define-macro (lambdify vars expr)
  (list 'sympy.lambdify
    (list 'quote vars)
    expr
    (list 'quote 'numpy)))
"""

# ==================== P0a: with-eng 引擎上下文 ====================

_WITH_ENG = """
(define-macro (with-eng engine . body)
  (list 'let (list (list '%saved '(engine-name)))
    (list 'begin
      (list 'use-engine engine)
      (list 'let (list (list '%result (cons 'begin body)))
        (list 'begin
          (list 'use-engine '%saved)
          '%result)))))
"""

# ==================== P0b: solve-for 方程求解糖 ====================

# solve-for 由 Prim 实现（宏对参数配对处理过于复杂）
# 用法： (solve-for x (eqn (expt x 2) 4))
#        (solve-for (x y) (eqn (+ x y) 5) (eqn (- x y) 1))
# Prim 实现在 register_sugar_primitives 中

# ==================== P0c: rule/rewrite 表达式重写 ====================

_RULE_MACRO = """
(define-macro (rule name pattern replacement)
  (list 'define-rule (list 'quote name)
    (list 'quote pattern) (list 'quote replacement)))
"""

_REWRITE_MACRO = """
(define-macro (rewrite expr . rule-names)
  (cons 'apply-rules (cons expr
    (map (lambda (n) (list 'quote n)) rule-names))))
"""


# ==================== 注册 ====================

def register_sugar_primitives(env: 'Env') -> None:
    """注册语法糖"""
    from parser.parse_program import parse
    from eval.eval_scheme import eval_scheme
    
    eval_scheme(parse(_LAMBDA_MACRO_CODE), env)
    eval_scheme(parse(_FOR_MACRO_CODE), env)
    eval_scheme(parse(_THREAD_FIRST_MACRO), env)
    eval_scheme(parse(_THREAD_LAST_MACRO), env)
    eval_scheme(parse(_STR_MACRO_CODE), env)
    # try/catch — 已经在 eval_scheme.py 中作为特殊形式实现
    
    # P0: with 上下文管理器
    eval_scheme(parse(_WITH_MACRO_CODE), env)
    # P0: pmatch 模式匹配
    eval_scheme(parse(_MATCH_HELPER), env)
    eval_scheme(parse(_PMATCH_MACRO_CODE), env)
    
    # P1: define-data 记录类型
    eval_scheme(parse(_DEFINE_DATA_MACRO), env)
    
    # P2: 增强赋值 += -= *= /=
    eval_scheme(parse(_P2_AUGMENT), env)
    # P2: swap
    eval_scheme(parse(_P2_MULTI), env)
    # P2: set!-values 多重赋值
    eval_scheme(parse(_P2_DESTRUCT), env)
    
    # SymPy: sym 自动符号创建（自动 import sympy）
    eval_scheme(parse(_SYM_SYM), env)
    # SymPy: lambdify 简化
    eval_scheme(parse(_SYM_LAMBDIFY), env)
    
    # P0c: rule/rewrite 表达式重写
    eval_scheme(parse(_RULE_MACRO), env)
    eval_scheme(parse(_REWRITE_MACRO), env)
    
    # 绑定数学增强函数
    import sympy as _sp
    from eval.eval_python_import import wrap_python_value, unwrap_python_value
    
    # factorial
    def _fact(args):
        n = unwrap_python_value(args[0])
        return wrap_python_value(_sp.factorial(n))
    env.define("factorial", Prim("factorial", _fact))
    
    # ref (下标访问)
    def _ref(args):
        if len(args) != 2:
            raise Exception("ref: 需要 (ref obj idx)")
        obj = unwrap_python_value(args[0])
        idx = unwrap_python_value(args[1])
        if hasattr(obj, '__getitem__'):
            return wrap_python_value(obj[idx])
        return wrap_python_value(getattr(obj, str(idx)))
    env.define("ref", Prim("ref", _ref))
    
    # 绑定 ∞
    env.define(Sym("\u221e"), wrap_python_value(_sp.oo))
    
    # 绑定 CAS-aware 的 abs: 对 sympy 对象用 sympy.Abs
    try:
        _orig_abs = env.lookup(Sym('abs'))
    except (Exception):
        _orig_abs = lambda args: abs(args[0]) if args else 0
    def _cas_abs(args):
        if len(args) != 1:
            return _orig_abs(args) if callable(_orig_abs) else abs(args[0])
        val = args[0]
        if isinstance(val, PythonObject):
            import sympy as _sp2
            try:
                return wrap_python_value(_sp2.Abs(unwrap_python_value(val)))
            except:
                pass
        return _orig_abs(args) if callable(_orig_abs) else abs(unwrap_python_value(val))
    env.define("abs", Prim("abs", _cas_abs))
    
    # P0c: rule/rewrite 规则系统原语
    _rule_registry = {}
    def _define_rule_prim(args):
        if len(args) < 3:
            raise Exception("define-rule: need (define-rule name pattern replacement)")
        name = args[0].name if hasattr(args[0], 'name') else str(args[0])
        # 存储原始 S-表达式（quoted），apply 时再解释为 sympy
        _rule_registry[name] = (args[1], args[2])
        return Str(list(f"rule '{name}' defined" + (f" ({len(_rule_registry)} total)")))
    env.define("define-rule", Prim("define-rule", _define_rule_prim))
    
    def _apply_rules_prim(args):
        if len(args) < 2:
            raise Exception("apply-rules: need (apply-rules expr rule-name ...)")
        # 第一个参数是要重写的表达式（已求值）
        expr = args[0]
        from eval.eval_python_import import unwrap_python_value
        # 解包 PythonObject 为 sympy 表达式
        py_expr = unwrap_python_value(expr) if hasattr(expr, 'obj') else expr
        result = py_expr
        # 解释器：将 Scheme S-表达式转为 sympy 表达式
        from parser.infix import parse_infix
        from parser.parse_program import parse as sexpr_parse
        from eval.eval_scheme import eval_scheme
        for i in range(1, len(args)):
            name = args[i].name if hasattr(args[i], 'name') else str(args[i])
            if name in _rule_registry:
                pat_sexpr, repl_sexpr = _rule_registry[name]
                # 转 S-表达式为字符串，再经 infix→sympy
                from core.schemevalue import scheme_format
                try:
                    pat_str = scheme_format(pat_sexpr)
                    repl_str = scheme_format(repl_sexpr)
                    pat_infix = parse_infix(pat_str)
                    repl_infix = parse_infix(repl_str)
                    pat_sympy = eval_scheme(sexpr_parse(pat_infix), env)
                    repl_sympy = eval_scheme(sexpr_parse(repl_infix), env)
                    p = unwrap_python_value(pat_sympy) if hasattr(pat_sympy, 'obj') else pat_sympy
                    r = unwrap_python_value(repl_sympy) if hasattr(repl_sympy, 'obj') else repl_sympy
                    result = result.replace(p, r)
                except Exception:
                    pass
        from eval.eval_python_import import wrap_python_value
        return wrap_python_value(result)
    env.define("apply-rules", Prim("apply-rules", _apply_rules_prim))
