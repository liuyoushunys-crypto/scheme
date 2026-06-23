"""
CAS 假设系统 — 对标 Maxima assume/declare/assuming/refine/ask。

使用方式：
  (assume '(positive x))       → 声明 x > 0
  (assume '(integer n))        → 声明 n 是整数
  (assume '(> x 0))            → 等价声明
  (assume '(real x) '(> n 0))  → 多条假设

  (unassume)                   → 清除全部假设
  (unassume 'x)               → 清除关于 x 的假设

  (assuming facts expr ...)    → 临时假设下求值
  (assuming '((positive x)) (refine (sqrt (^ x 2))))

  (refine expr)                → 在当前假设下化简
  (refine expr '(positive x))  → 给定假设下化简

  (ask '(positive x))          → 查询性质 (#t/#f/unknown)
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


# ==================== 内部工具 ====================

def _sympy():
    from eval.cas.engine import get_engine
    return get_engine()


def _unwrap1(args):
    return unwrap_python_value(args[0])


def _get_predicate(name: str):
    """从 sympy.assumptions.Q 获取谓词"""
    sp = _sympy()
    try:
        from sympy.assumptions import Q
        return getattr(Q, name, None)
    except ImportError:
        return None


# ==================== 事实解析 ====================

_FACT_MAP = {
    'positive':    'positive',
    'negative':    'negative',
    'nonnegative': 'nonnegative',
    'nonpositive': 'nonpositive',
    'zero':        'zero',
    'nonzero':     'nonzero',
    'integer':     'integer',
    'real':        'real',
    'rational':    'rational',
    'complex':     'complex',
    'imaginary':   'imaginary',
    'even':        'even',
    'odd':         'odd',
    'finite':      'finite',
    'infinite':    'infinite',
    'commutative': 'commutative',
    'algebraic':   'algebraic',
    'prime':       'prime',
    'composite':   'composite',
}

_OP_MAP = {
    '>':  'gt',
    '<':  'lt',
    '>=': 'ge',
    '<=': 'le',
    '=':  'eq',
    '!=': 'ne',
}


def _parse_fact(fact):
    """解析 Scheme 事实描述 → sympy 谓词应用
    
    (positive x)  →  Q.positive(x)
    (> x 0)       →  Q.gt(x, 0)
    (integer n)   →  Q.integer(n)
    """
    from sympy.assumptions import Q
    py_fact = unwrap_python_value(fact)
    
    if not isinstance(py_fact, list) or len(py_fact) < 2:
        raise Exception(f"assume: 无效的事实格式 {py_fact}")
    
    prop_or_op = str(py_fact[0])
    args = py_fact[1:]
    
    # 检查是否为比较运算符
    if prop_or_op in _OP_MAP:
        q_name = _OP_MAP[prop_or_op]
        q_func = getattr(Q, q_name, None)
        if q_func is None:
            raise Exception(f"assume: 不支持的运算符 {prop_or_op}")
        # args 需要是 sympy 表达式
        py_args = [_sympy().sympify(a) for a in args]
        return q_func(*py_args)
    
    # 检查是否为性质谓词
    q_name = _FACT_MAP.get(prop_or_op)
    if q_name is None:
        # 直接尝试 Q 属性
        q_name = prop_or_op
    q_func = getattr(Q, q_name, None)
    if q_func is None:
        raise Exception(f"assume: 不支持的谓词 {prop_or_op}")
    
    # args 中的符号需要是 sympy Symbol
    py_args = []
    for a in args:
        if isinstance(a, str):
            py_args.append(_sympy().Symbol(a))
        else:
            py_args.append(_sympy().sympify(a))
    return q_func(*py_args)


# ==================== CAS Prim 函数 ====================

def cas_assume(args: List[SchemeValue]) -> SchemeValue:
    """
    (assume fact ...) — 添加全局假设
    
    示例：
      (assume '(positive x))
      (assume '(> x 0))
      (assume '(integer n) '(positive x))
    """
    if len(args) == 0:
        raise Exception("assume: 需要至少 1 参数")
    
    from sympy.assumptions.assume import global_assumptions
    for fact_val in args:
        predicate = _parse_fact(fact_val)
        global_assumptions.add(predicate)
    
    return Str(list(f"assumed {len(args)} fact(s)"))


def cas_unassume(args: List[SchemeValue]) -> SchemeValue:
    """
    (unassume)      → 清除全部假设
    (unassume sym)  → 清除关于该符号的假设
    """
    from sympy.assumptions.assume import global_assumptions
    
    if len(args) == 0:
        global_assumptions.clear()
        return Str(list("all assumptions cleared"))
    
    sym_name = unwrap_python_value(args[0])
    if isinstance(sym_name, str):
        # 找出涉及该符号的假设并移除
        removed = []
        for fact in list(global_assumptions):
            fact_str = str(fact)
            if sym_name in fact_str:
                global_assumptions.remove(fact)
                removed.append(str(fact))
        return Str(list(f"removed {len(removed)} fact(s) about {sym_name}"))
    
    return Str(list("unassume: 参数应为符号名或空"))


def cas_refine(args: List[SchemeValue]) -> SchemeValue:
    """
    (refine expr)                     → 在当前全局假设下化简
    (refine expr '(positive x))       → 给定假设下化简
    """
    if len(args) < 1:
        raise Exception("refine: 需要至少 1 参数 (refine expr)")
    
    expr = _unwrap1(args[:1])
    import sympy
    py_expr = sympy.sympify(expr)
    
    if len(args) >= 2:
        # 给定假设
        from sympy.assumptions.assume import global_assumptions
        saved = list(global_assumptions)
        try:
            for fact_val in args[1:]:
                predicate = _parse_fact(fact_val)
                global_assumptions.add(predicate)
            result = sympy.refine(py_expr)
            return wrap_python_value(result)
        finally:
            global_assumptions.clear()
            for f in saved:
                global_assumptions.add(f)
    else:
        # 当前全局假设
        result = sympy.refine(py_expr)
        return wrap_python_value(result)


def cas_assuming(args: List[SchemeValue]) -> SchemeValue:
    """
    (assuming facts expr ...) — 在临时假设下求值表达式
    
    示例：
      (assuming '((positive x)) (refine (sqrt (^ x 2))))
      (assuming '((integer n)) (refine (sin (* n pi))))
    """
    if len(args) < 2:
        raise Exception("assuming: 需要 (assuming facts expr ...)")
    
    facts_val = args[0]
    body_exprs = args[1:]
    
    # 解析事实列表
    py_facts = unwrap_python_value(facts_val)
    if not isinstance(py_facts, list):
        raise Exception("assuming: 第一个参数应为事实列表")
    
    from sympy.assumptions.assume import global_assumptions
    from sympy.assumptions import assuming as sympy_assuming
    
    saved = list(global_assumptions)
    try:
        predicates = []
        for f in py_facts:
            # f is already a Python list like ['positive', 'x']
            if isinstance(f, list) and len(f) >= 2:
                prop = str(f[0])
                args_list = f[1:]
                py_args = [_sympy().sympify(a) if not isinstance(a, str) else _sympy().Symbol(a) for a in args_list]
                
                if prop in _OP_MAP:
                    from sympy.assumptions import Q
                    q_func = getattr(Q, _OP_MAP[prop])
                    predicates.append(q_func(*py_args))
                else:
                    q_name = _FACT_MAP.get(prop, prop)
                    from sympy.assumptions import Q
                    q_func = getattr(Q, q_name)
                    predicates.append(q_func(*py_args))
        
        # 使用 sympy 的 assuming 上下文
        from eval.eval_scheme import eval_scheme
        from core.tail_call import apply_tail, unwrap_tail
        
        # 在临时假设下求值每个 body 表达式
        with sympy_assuming(*predicates):
            env = None  # will be set below
            results = []
            for expr in body_exprs:
                result = eval_scheme(expr, env)
                results.append(result)
        
        return results[-1] if results else Nil()
    finally:
        global_assumptions.clear()
        for f in saved:
            global_assumptions.add(f)


def cas_ask(args: List[SchemeValue]) -> SchemeValue:
    """
    (ask '(positive x))   → #t / #f / unknown
    (ask '(integer n))
    """
    if len(args) != 1:
        raise Exception("ask: 需要 1 参数 (ask '(predicate symbol))")
    
    try:
        predicate = _parse_fact(args[0])
        from sympy.assumptions import ask
        result = ask(predicate)
        if result is True:
            return Bool(True)
        elif result is False:
            return Bool(False)
        else:
            return Sym("unknown")
    except Exception as e:
        raise Exception(f"ask error: {e}")


# ==================== 注册 ====================

def register_assume_primitives(env: 'Env') -> None:
    """注册假设系统 Prim"""
    env.define("assume", Prim("assume", cas_assume))
    env.define("unassume", Prim("unassume", cas_unassume))
    env.define("refine", Prim("refine", cas_refine))
    env.define("assuming", Prim("assuming", cas_assuming))
    env.define("ask", Prim("ask", cas_ask))
