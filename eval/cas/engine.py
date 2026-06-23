"""
CAS 引擎管理器 — symengine/sympy 切换与自动降级。

文档参考：doc/engine-switching.md

用法：
  (use-engine 'sympy)       → 切换到 sympy
  (use-engine 'symengine)   → 切换到 symengine (auto: symengine 优先)
  (engine-info)             → 引擎状态
"""

from typing import List, Optional
from core.schemevalue import *

_engine_name = 'auto'
_engine_cache = {}


def _get_symengine():
    """惰性导入 symengine"""
    if 'symengine' not in _engine_cache:
        try:
            import symengine
            _engine_cache['symengine'] = symengine
        except ImportError:
            _engine_cache['symengine'] = None
    return _engine_cache['symengine']


def _get_sympy():
    """惰性导入 sympy"""
    if 'sympy' not in _engine_cache:
        import sympy
        _engine_cache['sympy'] = sympy
    return _engine_cache['sympy']


class _EngineProxy:
    """引擎代理：auto/symengine 模式自动降级到 sympy。
    
    所有 37 处 _sympy().xxx(...) 调用点零改动，全享受自动降级。
    """
    def __getattr__(self, name):
        if _engine_name == 'sympy':
            sp = _get_sympy()
            if hasattr(sp, name):
                return getattr(sp, name)
        elif _engine_name == 'symengine':
            se = _get_symengine()
            if se and hasattr(se, name):
                return getattr(se, name)
            raise AttributeError(f"symengine 不支持 '{name}'")
        else:  # auto: symengine 优先
            se = _get_symengine()
            if se and hasattr(se, name):
                return getattr(se, name)
            sp = _get_sympy()
            if hasattr(sp, name):
                return getattr(sp, name)
        raise AttributeError(f"引擎不支持 '{name}'")


_engine = _EngineProxy()


def get_engine():
    """返回引擎代理对象（统一接口，自动降级）"""
    return _engine


def get_engine_name():
    """获取当前引擎模式名"""
    return _engine_name


def call(name, *args, **kwargs):
    """智能调度：按引擎模式调用函数。
    
    预留 API，供 CAS 原语统一调用。
    """
    if _engine_name in ('auto', 'symengine'):
        se = _get_symengine()
        if se and hasattr(se, name):
            try:
                return getattr(se, name)(*args, **kwargs)
            except Exception:
                if _engine_name == 'symengine':
                    raise
    sp = _get_sympy()
    if hasattr(sp, name):
        return getattr(sp, name)(*args, **kwargs)
    raise AttributeError(f"引擎不支持 '{name}'")


def _set_engine(name):
    """设置引擎模式"""
    global _engine_name
    raw = str(name).lower().strip("'\"")
    if raw not in ('auto', 'sympy', 'symengine'):
        raise Exception(f"未知引擎 '{raw}' (try: auto, sympy, symengine)")
    _engine_name = raw


def set_engine(name):
    """Python 端设置引擎"""
    _set_engine(name)


def engine_info():
    """返回引擎信息字符串"""
    sp = get_engine()
    name = getattr(sp, '__name__', str(type(sp).__name__))
    ver = '?'
    try:
        se = _get_symengine()
        if se:
            ver = getattr(se, '__version__', '?')
    except:
        pass
    lines = [f"当前引擎: {name} (mode: {_engine_name})"]
    for eng in ['symengine', 'sympy']:
        try:
            mod = _get_symengine() if eng == 'symengine' else _get_sympy()
            v = getattr(mod, '__version__', '?') if mod else '?'
            ok = '✅' if mod else '❌'
            lines.append(f"  {eng} v{v} {ok}")
        except:
            lines.append(f"  {eng}: ❌")
    lines.append("  调度: symengine 优先 → sympy fallback")
    return "\n".join(lines)


def cas_use_engine(args):
    """(use-engine 'mode) — 切换引擎"""
    if len(args) == 0:
        return Str(list(f"Current mode: {_engine_name}"))
    if len(args) != 1:
        raise Exception("use-engine: need (use-engine 'name)")
    name = args[0].name if hasattr(args[0], 'name') else str(args[0])
    _set_engine(name)
    return Str(list(f"Switched to: {_engine_name}"))


def cas_engine_info(args):
    """(engine-info) — 显示引擎状态"""
    return Str(list(engine_info()))


def register_engine_primitives(env):
    """注册引擎原语"""
    env.define("use-engine", Prim("use-engine", cas_use_engine))
    env.define("engine-info", Prim("engine-info", cas_engine_info))
    env.define("engine-name", Prim("engine-name",
        lambda args: Sym(_engine_name)))
    # with-eng: 临时切换引擎
    # 用法: (with-eng 'sympy '(expand (expt x 3)))  — body 需 quote
    # 理由: Prim 对参数先求值，用 quote 阻止求值后在内部 eval
    def cas_with_eng(args, env):
        if len(args) < 2:
            raise Exception("with-eng: need (with-eng 'engine body)")
        engine_name = args[0].name if hasattr(args[0], 'name') else str(args[0])
        body_expr = args[1]
        from eval.eval_scheme import eval_scheme
        saved = _engine_name
        _set_engine(engine_name)
        try:
            # body_expr 是 quoted 后的表达式（如 '(expand (expt x 3))')
            # 但 Prim 已对它求值了一次（quote 阻止了求值，body_expr 是 Cons 树）
            # 需要再次 eval_scheme 让它在新引擎下执行
            return eval_scheme(body_expr, env)
        finally:
            _set_engine(saved)
    env.define("with-eng", Prim("with-eng",
        lambda args: cas_with_eng(args, env)))


register_primitives = register_engine_primitives
