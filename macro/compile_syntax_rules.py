from typing import List, Optional
from core.schemevalue import *
from core.env import Env


def compile_syntax_rules(rules_exp: SchemeValue, env: Env) -> SyntaxRulesMacro:
    unpacked = unpack_list(rules_exp)
    if unpacked is not None and len(unpacked) >= 3 and isinstance(unpacked[0], Sym) and unpacked[0].name == "syntax-rules":
        second = unpacked[1]
        if isinstance(second, Sym):
            ellipsis_id = second.name
            literals_val = unpacked[2]
            rules_list = unpacked[3:]
        else:
            ellipsis_id = "..."
            literals_val = second
            rules_list = unpacked[2:]

        lits = []
        if isinstance(literals_val, Cons):
            lits_unpacked = unpack_list(literals_val)
            if lits_unpacked is not None:
                lits = [x for x in lits_unpacked if isinstance(x, Sym)]
        elif isinstance(literals_val, Nil):
            lits = []
        else:
            raise Exception("Invalid syntax-rules literals")

        rules = []
        for rule in rules_list:
            rule_unpacked = unpack_list(rule)
            if rule_unpacked is not None and len(rule_unpacked) == 2:
                rules.append((rule_unpacked[0], rule_unpacked[1]))
            else:
                raise Exception("Invalid syntax rule")

        macro = SyntaxRulesMacro(lits, rules, env)
        macro.ellipsis_id = ellipsis_id
        return macro
    raise Exception("Invalid syntax-rules macro structure")
