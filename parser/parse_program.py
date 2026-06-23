from typing import List
from core.schemevalue import *
from parser.tokenize import tokenize
from parser.parse_form import parse_form


def parse_program(input_str: str) -> List[SchemeValue]:
    tokens = tokenize(input_str)
    index = [0]
    forms = []
    while index[0] < len(tokens):
        forms.append(parse_form(tokens, index))
    return forms


def parse(input_str: str) -> SchemeValue:
    parsed = parse_program(input_str)
    return parsed[0] if parsed else Nil()
