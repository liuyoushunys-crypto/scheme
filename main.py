# main.py
import sys
from typing import Optional
from core.schemevalue import *
from parser.parse_program import parse_program
from eval.eval_scheme import eval_scheme
from primitives.primitives import register_all

# 惰性加载：非核心模块延后到首次使用时才加载
_LazyPrimitiveModules = {}  # 缓存已加载的模块注册函数

def _lazy_register(module_path, reg_name):
    """延迟注册：首次调用时导入模块"""
    if module_path not in _LazyPrimitiveModules:
        import importlib
        try:
            mod = importlib.import_module(module_path)
            _LazyPrimitiveModules[module_path] = getattr(mod, reg_name)
        except ImportError:
            _LazyPrimitiveModules[module_path] = None
    return _LazyPrimitiveModules[module_path]

def start_native_repl(global_env: Env) -> None:
    """启动带有多行括号匹配支持的 Scheme 交互式终端 (REPL)"""
    while True:
        try:
            expr_str = read_expression()
            if expr_str is None or expr_str in ("(exit)", "(quit)"):
                print("Goodbye.")
                break
            if not expr_str.strip():
                continue
                
            expressions = parse_program(expr_str)
            last_result = Nil()
            for expr in expressions:
                result = eval_scheme(expr, global_env)
                if not (isinstance(result, Sym) and result.name == "undefined"):
                    print(f"=> {scheme_format(result)}")
                last_result = result
            if not (isinstance(last_result, Sym) and last_result.name == "undefined"):
                global_env.define(Sym("%"), last_result)
        except SchemeRaiseException as rex:
            print(f"Error: {scheme_format(rex.value)}")
        except Exception as ex:
            print(f"Evaluation Error: {ex}")

def read_expression() -> Optional[str]:
    """支持括号、字符串配对判定，进行多行输入读取"""
    buffer = []
    open_parens = 0
    in_string = False
    first_line = True
    
    while True:
        prompt = "scheme> " if first_line else "        "
        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                return None
        except KeyboardInterrupt:
            print()
            return ""
            
        buffer.append(line)
        first_line = False
        
        i = 0
        line_len = len(line)
        while i < line_len:
            c = line[i]
            if c == ';':
                break
            if c == '"' and (i == 0 or line[i - 1] != '\\'):
                in_string = not in_string
            if not in_string:
                if c in ('(', '['):
                    open_parens += 1
                elif c in (')', ']'):
                    open_parens -= 1
            i += 1
            
        if open_parens <= 0 and not in_string:
            break
            
    return "".join(buffer).strip()

def main() -> None:
    """初始化并配置环境上下文，启动执行逻辑"""
    global_env = Env()
    register_all(global_env)
    
    # 安装 REPL 增强 (TAB 补全)
    try:
        from eval.eval_repl import install_repl
        install_repl(lambda: global_env)
    except:
        pass
        
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            exprs = parse_program(content)
            for expr in exprs:
                eval_scheme(expr, global_env)
        except Exception as ex:
            print(f"Error: {ex}")
        return
        
    start_native_repl(global_env)

if __name__ == "__main__":
    main()