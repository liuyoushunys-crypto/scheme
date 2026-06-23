from typing import Dict, Any, List
from core.schemevalue import *
from macro.pattern_utils import get_pattern_vars_depth
from macro.match_pattern_recursive import match_pattern_recursive
from macro.pattern_utils import collect_hygiene_renames
from macro.expand_template_recursive import expand_template_recursive
from core.env import Env


def expand_macro(macro: SyntaxRulesMacro, macro_call: Cons, env: Env) -> SchemeValue:
    ellipsis_id = getattr(macro, "ellipsis_id", "...")
    for pattern, template in macro.rules:
        expected_depths = get_pattern_vars_depth(pattern, ellipsis_id)
        bindings = match_pattern_recursive(pattern, macro_call, macro.literals, ellipsis_id, {}, expected_depths)
        if bindings is not None:
            hygiene_renames = collect_hygiene_renames(template, macro.literals, ellipsis_id, bindings)
            for orig, hygienic in hygiene_renames.items():
                try:
                    val = macro.env.lookup(orig)
                    env.define(hygienic, val)
                except Exception:
                    pass
            return expand_template_recursive(template, bindings, ellipsis_id, [], hygiene_renames)

    raise Exception(f"No matching syntax-rules pattern for: {macro_call}")
