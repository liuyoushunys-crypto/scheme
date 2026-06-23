"""
Closure
"""
from typing import List, Optional
from core.schemevalue import *
import types
import inspect

# ——————— SchemeClosureWrapper ———————

class SchemeClosureWrapper:
    """包装 Scheme closure 为 Python 可调用对象"""
    
    def __init__(self, closure: 'Closure'):
        self._closure = closure
        self._code = self._make_code(closure)
        self._signature = self._make_signature(closure)
    
    def _make_code(self, closure):
        formals = closure.formals
        arg_count = 0
        while isinstance(formals, Cons):
            arg_count += 1
            formals = formals.cdr
        return types.CodeType(
            arg_count, 0, 0, arg_count, 0, b'',
            (), (), (), '<lambda>', 'eval_python_import', 0, b''
        )
    
    def _make_signature(self, closure):
        import inspect
        params = []
        formals = closure.formals
        while isinstance(formals, Cons):
            name = formals.car.name if isinstance(formals.car, Sym) else str(formals.car)
            params.append(inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD))
            formals = formals.cdr
        return inspect.Signature(params)
    
    def __call__(self, *args):
        from core.tail_call import apply
        from eval.eval_scheme import eval_scheme
        from eval.py.convert import wrap_python_value
        scheme_args = [wrap_python_value(a) for a in args]
        result = apply(self._closure, scheme_args, self._closure.env)
        # 结果可能包含 tail call sentinel
        if isinstance(result, TailCallSentinel):
            result = eval_scheme(result.expr, result.env)
        return unwrap_python_value(result) if isinstance(result, PythonObject) else result
    
    def __repr__(self):
        return f"#<SchemeClosure {scheme_format(self._closure)}>"




