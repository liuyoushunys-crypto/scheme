"""
Try/catch - exception handling.
  (try body handler)  ->  (lambda (e) ...) catches Exception
"""

from typing import List
from core.schemevalue import *
from core.env import Env
from core.tail_call import apply_tail
from eval.eval_scheme import eval_scheme


def eval_try(cdr, env):
    """Evaluate (try body handler)"""
    from core.schemevalue import Cons, Nil, Str
    match cdr:
        case Cons(body_form, Cons(handler_form, Nil())):
            try:
                return eval_scheme(body_form, env)
            except Exception as exc:
                handler_proc = eval_scheme(handler_form, env)
                return apply_tail(handler_proc, [Str(str(exc))], env)
    raise Exception("try: need (try body handler)")
