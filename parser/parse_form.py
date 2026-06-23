from typing import List
from core.schemevalue import *
from parser.parse_char import parse_char
from parser.parse_base import parse_base
from parser.parse_complex import parse_complex


def parse_form(tokens: List[str], index_ref: List[int]) -> SchemeValue:
    if index_ref[0] >= len(tokens):
        raise Exception("Unexpected EOF")
    token = tokens[index_ref[0]]
    index_ref[0] += 1

    match token:
        case "(":
            return parse_list(tokens, index_ref)
        case ")":
            raise Exception("Unexpected ')'")
        case "[":
            # 方括号: [a b c] → (bracket a b c)
            return Cons(Sym("bracket"), parse_list_elems(tokens, index_ref))
        case "]":
            raise Exception("Unexpected ']'")
        case "'":
            return Cons(Sym("quote"), Cons(parse_form(tokens, index_ref), Nil()))
        case "`":
            return Cons(Sym("quasiquote"), Cons(parse_form(tokens, index_ref), Nil()))
        case ",":
            return Cons(Sym("unquote"), Cons(parse_form(tokens, index_ref), Nil()))
        case ",@":
            return Cons(Sym("unquote-splicing"), Cons(parse_form(tokens, index_ref), Nil()))
        case "#t":
            return Bool(True)
        case "#f":
            return Bool(False)
        case "#'":
            return Cons(Sym("syntax"), Cons(parse_form(tokens, index_ref), Nil()))
        case "#`":
            return Cons(Sym("quasisyntax"), Cons(parse_form(tokens, index_ref), Nil()))
        case "#,":
            return Cons(Sym("unsyntax"), Cons(parse_form(tokens, index_ref), Nil()))
        case "#,@":
            return Cons(Sym("unsyntax-splicing"), Cons(parse_form(tokens, index_ref), Nil()))

        case "#(":
            return parse_vector(tokens, index_ref)
        case _ if token.startswith('#{') and token.endswith('}'):
            # #{...} infix reader macro
            content = token[2:-1].strip()  # strip '#{' and '}'
            if not content:
                raise Exception("Empty infix expression in #{}")
            from parser.infix import parse_infix
            expr_str = parse_infix(content)
            # 重新解析产生的 Scheme S-表达式字符串
            from parser.tokenize import tokenize
            inner_tokens = tokenize(expr_str)
            if not inner_tokens:
                return Nil()
            inner_idx = [0]
            result = parse_form(inner_tokens, inner_idx)
            if inner_idx[0] < len(inner_tokens):
                raise Exception(f"Extra tokens after infix expression: {inner_tokens[inner_idx[0]:]}")
            return result
        case _ if token.startswith('"""') and token.endswith('"""') and len(token) >= 6:
            # Python 风格多行字符串
            content = token[3:-3]
            return Str(list(content))
        case _ if token.startswith('"'):
            return Str(list(token[1:-1].replace('\\"', '"')))
        case _ if token.startswith("#\\"):
            return parse_char(token)
        case _ if token.startswith("#b") or token.startswith("#B"):
            return parse_base(token, 2)
        case _ if token.startswith("#o") or token.startswith("#O"):
            return parse_base(token, 8)
        case _ if token.startswith("#x") or token.startswith("#X"):
            return parse_base(token, 16)
        case _ if (complex_val := parse_complex(token)) is not None:
            return complex_val
        case _:
            try:
                if token.startswith(('+', '-')):
                    val = int(token[1:])
                    return Integer(-val if token[0] == '-' else val)
                else:
                    return Integer(int(token))
            except ValueError:
                pass

            try:
                return Num(float(token))
            except ValueError:
                pass

            return Sym(token)


def parse_vector(tokens: List[str], index_ref: List[int]) -> SchemeValue:
    items = []
    while index_ref[0] < len(tokens) and tokens[index_ref[0]] not in (")", "]"):
        items.append(parse_form(tokens, index_ref))
    if index_ref[0] >= len(tokens):
        raise Exception("Unexpected EOF in vector")
    index_ref[0] += 1
    return Vector(items)


def parse_list_elems(tokens: List[str], index_ref: List[int]) -> SchemeValue:
    """解析列表元素（共用）"""
    if index_ref[0] >= len(tokens):
        raise Exception("Unexpected EOF in list")
    if tokens[index_ref[0]] in (")", "]"):
        index_ref[0] += 1
        return Nil()

    car = parse_form(tokens, index_ref)
    if index_ref[0] < len(tokens) and tokens[index_ref[0]] == ".":
        index_ref[0] += 1
        cdr = parse_form(tokens, index_ref)
        if index_ref[0] >= len(tokens) or tokens[index_ref[0]] not in (")", "]"):
            raise Exception("Expected ')' after dot notation")
        index_ref[0] += 1
        return Cons(car, cdr)

    cdr_list = parse_list_elems(tokens, index_ref)
    return Cons(car, cdr_list)


def parse_list(tokens: List[str], index_ref: List[int]) -> SchemeValue:
    """标准圆括号列表解析"""
    return parse_list_elems(tokens, index_ref)