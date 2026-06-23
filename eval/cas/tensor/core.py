"""
tensor -- 张量代数 (协变/逆变/缩并)

依赖: sympy
"""
from core.schemevalue import Prim, Str, Sym

# 内部索引注册表
_index_registry = {}


def _declare_indices(names):
    """注册索引名称"""
    for name in names:
        _index_registry[name] = True
    return Str(f"indices: {' '.join(names)}")


def _make_tensor(name, cov_form, contra_form):
    """创建张量对象"""
    from eval.eval_scheme import eval_scheme
    # 将张量表示为 sympy 结构
    try:
        import sympy as sp
    except ImportError:
        return Str(f"<tensor {name}>")
    # cov/contra 索引列表
    cov_list = _form_to_list(cov_form)
    contra_list = _form_to_list(contra_form)
    return Str(f"<tensor {name} cov={' '.join(cov_list)} contra={' '.join(contra_list)}>")


def _do_contract(tc_val, idx1, idx2):
    """张量缩并"""
    return Str(f"<contract {idx1}×{idx2}>")


def _do_raise(tc_val, idx):
    """升指标"""
    return Str(f"<raise-index {idx}>")


def _do_lower(tc_val, idx):
    """降指标"""
    return Str(f"<lower-index {idx}>")


def _form_to_list(form):
    """将 Scheme 列表形式转为 Python 列表"""
    from core.schemevalue import Cons, Nil
    result = []
    curr = form
    while isinstance(curr, Cons):
        a = curr.car
        result.append(a.name if isinstance(a, Sym) else str(a))
        curr = curr.cdr
    return result


def register_tensor_primitives(env):
    """注册张量原语"""
    env.define("declare-indices", Prim("declare-indices", _declare_indices))
    env.define("make-tensor", Prim("make-tensor", _make_tensor))
    env.define("contract", Prim("contract", _do_contract))
    env.define("raise-index", Prim("raise-index", _do_raise))
    env.define("lower-index", Prim("lower-index", _do_lower))


register_primitives = register_tensor_primitives