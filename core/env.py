from typing import Dict, Iterable, Optional, Set, Union
from core.schemevalue import SchemeValue, Sym


CORE_KEYWORDS: Set[str] = {
    "quote", "if", "define", "lambda", "begin", "set!", "let", "let*", "letrec", 
    "let-values", "cond", "case", "and", "or", "define-syntax", "define-macro", 
    "guard", "quasiquote", "unquote", "unquote-splicing", "...", "syntax-rules", 
    "syntax-case", "syntax", "quasisyntax", "with-syntax", "unsyntax", "unsyntax-splicing",
    "else", "=>", "_"
}


class Env:
    """词法作用域链承载体"""
    def __init__(self, outer: Optional['Env'] = None):
        self.outer: Optional['Env'] = outer
        self._bindings: Dict[str, SchemeValue] = {}

    @classmethod
    def from_bindings(cls, vars_: Iterable[Union[str, Sym]], vals: Iterable[SchemeValue], outer: Optional['Env'] = None) -> 'Env':
        new_env = cls(outer)
        for var, val in zip(vars_, vals):
            new_env.define(var, val)
        return new_env

    def _get_name(self, name: Union[str, Sym]) -> str:
        if isinstance(name, Sym):
            return name.name
        return name

    def is_bound(self, name: Union[str, Sym]) -> bool:
        """检查符号在当前环境或父环境中是否存在绑定"""
        actual_name = self._get_name(name)
        if actual_name in CORE_KEYWORDS:
            return True
        if actual_name in self._bindings:
            return True
        if self.outer is not None:
            return self.outer.is_bound(actual_name)
        return False

    def lookup(self, name: Union[str, Sym]) -> SchemeValue:
        actual_name = self._get_name(name)
        if actual_name in self._bindings:
            return self._bindings[actual_name]
        if self.outer is not None:
            return self.outer.lookup(actual_name)
        raise Exception(f"Unbound variable: {name}")

    def define(self, name: Union[str, Sym], val: SchemeValue) -> None:
        self._bindings[self._get_name(name)] = val

    def set(self, name: Union[str, Sym], val: SchemeValue) -> None:
        actual_name = self._get_name(name)
        if actual_name in self._bindings:
            self._bindings[actual_name] = val
            return
        if self.outer is not None:
            self.outer.set(actual_name, val)
            return
        raise Exception(f"Cannot set unbound variable: {name}")
