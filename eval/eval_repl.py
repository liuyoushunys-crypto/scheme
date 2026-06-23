"""
REPL 增强 — readline TAB 补全 + 多行编辑。

在 main.py 中 import：
  from eval.eval_repl import install_repl
  install_repl(global_env)
"""

import atexit
import os


def _make_completer(env_ref):
    """创建 readline 补全器"""
    import readline
    
    def complete(text, state):
        try:
            env = env_ref()
            if env is None:
                return None
            
            # 收集所有可补全的符号
            candidates = []
            for name in env._bindings:
                if name.startswith(text):
                    candidates.append(name)
            
            candidates.sort()
            if state < len(candidates):
                return candidates[state]
            return None
        except:
            return None
    
    return complete


def install_repl(env_fn):
    """
    安装 REPL 增强（TAB 补全、历史记录）
    在 main.py 中：install_repl(lambda: global_env)
    """
    try:
        import readline
    except ImportError:
        return  # 不支持 readline 的环境
    
    histfile = os.path.expanduser("~/.cas_history")
    
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    
    atexit.register(readline.write_history_file, histfile)
    
    completer = _make_completer(env_fn)
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_history_length(1000)
