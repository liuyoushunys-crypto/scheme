"""
CAS 入口系统 — (use-cas) 一键加载。

文档参考：doc/cas-entry-system.md

注：语法糖宏 (λ/->/->>/for/str) 已在 sugar/core.py 启动时注册，此处不重复。

用法：
  (use-cas)          → 核心: sympy + 假设 + 数值 + 语法糖
  (use-cas 'all)     → 含图论 + 张量 + 物理单位
  (use-cas 'min)     → 仅符号计算
  (list-all)         → 列出环境全部 500+ 函数
"""

from eval.eval_scheme import eval_scheme
from parser.parse_program import parse


def cas_use_cas(args, env):
    """(use-cas [mode]) — 一键加载 CAS 能力"""
    mode = 'normal'
    if args:
        mode = args[0].name if hasattr(args[0], 'name') else str(args[0])
    
    # 核心：所有模式下确保引擎可用
    core_commands = [
        "(import sympy)",
        "(use-engine 'auto)",
    ]
    
    # all 模式额外加载
    all_commands = [
        "(use-graph 'networkx)",
        "(use-tensor 'sympy)",
        "(use-units 'pint)",
    ]
    
    # 执行
    all_cmds = core_commands[:]
    if mode == 'all':
        all_cmds += all_commands
    elif mode == 'min':
        all_cmds = core_commands[:1]  # 仅 import sympy
    
    for cmd_str in all_cmds:
        try:
            expr = parse(cmd_str)
            eval_scheme(expr, env)
        except Exception:
            pass  # 可选包可能未安装
    
    from core.schemevalue import Str
    return Str(list(f"CAS loaded (mode: {mode})"))


def cas_list_all(args, env):
    """(list-all) — 列出环境全部注册函数"""
    from core.schemevalue import Str, Sym
    bindings = env._bindings
    funcs = []
    for k in sorted(bindings.keys(), key=str):
        v = bindings[k]
        name = k.name if isinstance(k, Sym) else str(k)
        vtype = type(v).__name__
        funcs.append(f"  {name:30s}  [{vtype}]")
    
    lines = [f"环境绑定: {len(funcs)} 个"]
    lines.append("─" * 60)
    lines.extend(funcs)
    return Str('\n'.join(lines))


def register_entry_primitives(env):
    """注册入口原语"""
    from core.schemevalue import Prim
    env.define("use-cas", Prim("use-cas", lambda args: cas_use_cas(args, env)))
    env.define("list-all", Prim("list-all", lambda args: cas_list_all(args, env)))


register_primitives = register_entry_primitives
