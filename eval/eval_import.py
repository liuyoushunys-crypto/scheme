from typing import Any, List, Optional, Tuple, Dict, Set
from core.schemevalue import *
from parser.parse_program import parse_program
from core.env import Env

# 全局 R7RS 库字典注册表
global_libraries: Dict[Tuple[Any, ...], Library] = {}

# 局部特性环境，用于 cond-expand
SUPPORTED_FEATURES: Set[str] = {"r7rs", "scheme-by-python", "exact-closed", "complex", "utf-8", "sympy"}

def library_name_to_tuple(name: SchemeValue) -> Tuple[Any, ...]:
    lst = unpack_list(name)
    if lst is None:
        raise Exception("Invalid library name")
    res = []
    for x in lst:
        if isinstance(x, Sym):
            res.append(x.name)
        elif isinstance(x, Integer):
            res.append(x.value)
        else:
            raise Exception("Library name must consist of symbols or integers")
    return tuple(res)

def resolve_import_set(import_set: SchemeValue) -> Dict[str, SchemeValue]:
    """递归解析 import 语法树集并返回解析后外部绑定的符号映射"""
    lst = unpack_list(import_set)
    if lst is None:
        raise Exception("Invalid import set")

    first = lst[0]
    if isinstance(first, Sym) and first.name in ("only", "except", "prefix", "rename"):
        inner_set = lst[1]
        inner_bindings = resolve_import_set(inner_set)

        match first.name:
            case "only":
                only_names = {x.name for x in lst[2:] if isinstance(x, Sym)}
                return {k: v for k, v in inner_bindings.items() if k in only_names}
            case "except":
                except_names = {x.name for x in lst[2:] if isinstance(x, Sym)}
                return {k: v for k, v in inner_bindings.items() if k not in except_names}
            case "prefix":
                prefix = lst[2].name if isinstance(lst[2], Sym) else ""
                return {f"{prefix}{k}": v for k, v in inner_bindings.items()}
            case "rename":
                rename_map = {}
                i = 2
                while i < len(lst):
                    # 支持两种格式：
                    # 1. (rename (lib) (old new) ...) — 平级对
                    # 2. (rename (lib) ((old new)) ...) — 嵌套对
                    pair = lst[i]
                    if isinstance(pair, Sym):
                        # 平级格式: (rename (lib) old new ...)
                        if i + 1 < len(lst) and isinstance(lst[i+1], Sym):
                            rename_map[pair.name] = lst[i+1].name
                            i += 2
                        else:
                            i += 1
                    else:
                        # 嵌套格式: (rename (lib) (old new) ...)
                        pair_lst = unpack_list(pair)
                        if pair_lst and len(pair_lst) == 2 and isinstance(pair_lst[0], Sym) and isinstance(pair_lst[1], Sym):
                            rename_map[pair_lst[0].name] = pair_lst[1].name
                        i += 1
                return {rename_map.get(k, k): v for k, v in inner_bindings.items()}
    else:
        lib_key = library_name_to_tuple(import_set)
        if lib_key not in global_libraries:
            raise Exception(f"Library not found: {scheme_format(import_set)}")
        lib = global_libraries[lib_key]

        bindings = {}
        for exp in lib.exports:
            exp_lst = unpack_list(exp)
            if exp_lst and len(exp_lst) == 3 and isinstance(exp_lst[0], Sym) and exp_lst[0].name == "rename":
                internal_name = exp_lst[1].name if isinstance(exp_lst[1], Sym) else ""
                external_name = exp_lst[2].name if isinstance(exp_lst[2], Sym) else ""
                if internal_name and external_name:
                    try:
                        bindings[external_name] = lib.env.lookup(internal_name)
                    except Exception:
                        pass
            elif isinstance(exp, Sym):
                try:
                    bindings[exp.name] = lib.env.lookup(exp.name)
                except Exception:
                    pass
        return bindings

def evaluate_feature_requirement(req: SchemeValue) -> bool:
    if isinstance(req, Sym):
        return req.name in SUPPORTED_FEATURES
    req_lst = unpack_list(req)
    if req_lst:
        first = req_lst[0]
        if isinstance(first, Sym):
            match first.name:
                case "and":
                    return all(evaluate_feature_requirement(x) for x in req_lst[1:])
                case "or":
                    return any(evaluate_feature_requirement(x) for x in req_lst[1:])
                case "not":
                    return not evaluate_feature_requirement(req_lst[1])
                case "library":
                    lib_key = library_name_to_tuple(req_lst[1])
                    return lib_key in global_libraries
    return False

def eval_cond_expand(clauses: List[SchemeValue], env: Env) -> None:
    from eval.eval_scheme import eval_scheme
    for clause in clauses:
        clause_lst = unpack_list(clause)
        if clause_lst:
            feature_req = clause_lst[0]
            if isinstance(feature_req, Sym) and feature_req.name == "else":
                for expr in clause_lst[1:]:
                    eval_scheme(expr, env)
                return
            if evaluate_feature_requirement(feature_req):
                for expr in clause_lst[1:]:
                    eval_scheme(expr, env)
                return


def eval_import(cons: Cons, env: Env) -> None:
    import_sets = from_lisp_list(cons.cdr)
    for st in import_sets:
        bindings = resolve_import_set(st)
        for name, val in bindings.items():
            env.define(name, val)


def eval_define_library(cons: Cons, env: Env) -> None:
    from eval.eval_scheme import eval_scheme
    unpacked = unpack_list(cons)
    if unpacked is None or len(unpacked) < 3:
        raise Exception("Invalid define-library syntax")
    lib_name_val = unpacked[1]
    lib_key = library_name_to_tuple(lib_name_val)

    lib_env = Env(outer=env)
    exports = []

    declarations = unpacked[2:]
    for decl in declarations:
        decl_lst = unpack_list(decl)
        if not decl_lst:
            continue
        first = decl_lst[0]
        if isinstance(first, Sym):
            match first.name:
                case "import":
                    for st in decl_lst[1:]:
                        bindings = resolve_import_set(st)
                        for name, val in bindings.items():
                            lib_env.define(name, val)
                case "export":
                    for exp in decl_lst[1:]:
                        exports.append(exp)
                case "begin":
                    for expr in decl_lst[1:]:
                        eval_scheme(expr, lib_env)
                case "include":
                    for path_val in decl_lst[1:]:
                        if isinstance(path_val, Str):
                            path = path_val.get_str()
                            with open(path, "r", encoding="utf-8") as f:
                                exprs = parse_program(f.read())
                            for expr in exprs:
                                eval_scheme(expr, lib_env)
                case "cond-expand":
                    eval_cond_expand(decl_lst[1:], lib_env)

    global_libraries[lib_key] = Library(lib_key, exports, lib_env)
