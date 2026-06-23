"""
rule — 表达式重写规则系统

用法：
  (rule trig-double (sin (* 2 %x)) → (* 2 (sin %x) (cos %x)))
  (rewrite (sin (* 2 a)) trig-double)
  → 2*sin(a)*cos(a)
"""

_rule_registry = {}


def define_rule(name, pattern_expr, replacement_expr):
    """注册重写规则"""
    _rule_registry[name] = (pattern_expr, replacement_expr)


def apply_rules(expr, rule_names):
    """按顺序应用规则到表达式"""
    result = expr
    for name in rule_names:
        if name in _rule_registry:
            pat, repl = _rule_registry[name]
            # sympy 的 replace 方法处理 Wild 匹配
            try:
                result = result.replace(pat, repl)
            except Exception:
                pass
    return result


def list_rules():
    """列出全部已注册规则"""
    return list(_rule_registry.keys())
