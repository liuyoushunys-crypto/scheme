# reader.py
from core.schemevalue import *
from parser.parse_form import parse_form
from parser.parse_char import parse_char
from core.port import InputStringPort

# 流式 R7RS 表达式读取器 (Datum Reader)

def skip_whitespace_and_comments(port: Port) -> None:
    while True:
        c_val = port.peek_char()
        if c_val < 0:
            break
        c = chr(c_val)
        if c.isspace():
            port.read_char()
            continue
        if c == ';':
            while True:
                nc_val = port.read_char()
                if nc_val < 0 or chr(nc_val) in ('\n', '\r'):
                    break
            continue
        break

def read_token_from_port(port: Port, initial_chars: str = "") -> str:
    token_chars = list(initial_chars)
    delimiters = {'(', ')', '[', ']', ';', '"', "'", '`', ','}
    while True:
        c_val = port.peek_char()
        if c_val < 0:
            break
        c = chr(c_val)
        if c.isspace() or c in delimiters:
            break
        port.read_char()
        token_chars.append(c)
    return "".join(token_chars)

def read_string_from_port(port: Port) -> Str:
    port.read_char()  # 移出 '"'
    chars = []
    while True:
        c_val = port.read_char()
        if c_val < 0:
            raise Exception("Unexpected EOF in string literal")
        c = chr(c_val)
        if c == '"':
            break
        if c == '\\':
            next_val = port.read_char()
            if next_val < 0:
                raise Exception("Unexpected EOF in string escape")
            nc = chr(next_val)
            match nc:
                case 'n': chars.append('\n')
                case 't': chars.append('\t')
                case 'r': chars.append('\r')
                case '"': chars.append('"')
                case '\\': chars.append('\\')
                case _: chars.append(nc)
        else:
            chars.append(c)
    return Str(chars)

def read_list_from_port(port: Port) -> SchemeValue:
    skip_whitespace_and_comments(port)
    c_val = port.peek_char()
    if c_val < 0:
        raise Exception("Unexpected EOF in list")
    c = chr(c_val)
    if c in (')', ']'):
        port.read_char()
        return Nil()
    
    car = read_datum(port)
    skip_whitespace_and_comments(port)
    next_c_val = port.peek_char()
    if next_c_val >= 0 and chr(next_c_val) == '.':
        port.read_char()  # 移出 '.'
        follow_val = port.peek_char()
        if follow_val >= 0 and (chr(follow_val).isspace() or chr(follow_val) in ('(', ')', '[', ']', '"', ';', "'", '`', ',')):
            cdr = read_datum(port)
            skip_whitespace_and_comments(port)
            closing_val = port.read_char()
            if closing_val < 0 or chr(closing_val) not in (')', ']'):
                raise Exception("Expected ')' or ']' after dotted tail")
            return Cons(car, cdr)
        else:
            token = read_token_from_port(port, initial_chars=".")
            cdr_car = parse_form([token], [0])
            cdr = read_list_from_port(port)
            return Cons(car, Cons(cdr_car, cdr))
            
    cdr = read_list_from_port(port)
    return Cons(car, cdr)

def read_datum(port: Port) -> SchemeValue:
    """从输入端口中读取单个 Scheme 数据单元"""
    skip_whitespace_and_comments(port)
    c_val = port.peek_char()
    if c_val < 0:
        return Sym("eof")
    c = chr(c_val)
    
    if c in ('(', '['):
        port.read_char()
        return read_list_from_port(port)
    elif c == '"':
        return read_string_from_port(port)
    elif c == "'":
        port.read_char()
        return Cons(Sym("quote"), Cons(read_datum(port), Nil()))
    elif c == "`":
        port.read_char()
        return Cons(Sym("quasiquote"), Cons(read_datum(port), Nil()))
    elif c == ",":
        port.read_char()
        next_c = port.peek_char()
        if next_c >= 0 and chr(next_c) == '@':
            port.read_char()
            return Cons(Sym("unquote-splicing"), Cons(read_datum(port), Nil()))
        return Cons(Sym("unquote"), Cons(read_datum(port), Nil()))
    elif c == '#':
        port.read_char()
        next_c_val = port.peek_char()
        if next_c_val < 0:
            raise Exception("Unexpected EOF after '#'")
        next_c = chr(next_c_val)

        # #{...} infix reader macro
        if next_c == '{':
            port.read_char()  # consume '{'
            chars = []
            depth = 1
            while depth > 0:
                cv = port.read_char()
                if cv < 0:
                    raise Exception("Unexpected EOF in #{...} infix expression")
                ch = chr(cv)
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                if depth > 0:
                    chars.append(ch)
            infix_content = ''.join(chars).strip()
            if not infix_content:
                raise Exception("Empty infix expression in #{}")
            from parser.infix import parse_infix
            expr_str = parse_infix(infix_content)
            return read_datum(InputStringPort(expr_str))
        if next_c == "'":
            port.read_char()
            return Cons(Sym("syntax"), Cons(read_datum(port), Nil()))
        elif next_c == '`':
            port.read_char()
            return Cons(Sym("quasisyntax"), Cons(read_datum(port), Nil()))
        elif next_c == ',':
            port.read_char()
            nc2 = port.peek_char()
            if nc2 >= 0 and chr(nc2) == '@':
                port.read_char()
                return Cons(Sym("unsyntax-splicing"), Cons(read_datum(port), Nil()))
            return Cons(Sym("unsyntax"), Cons(read_datum(port), Nil()))
            
        if next_c in ('(', '['):
            port.read_char()
            elements = []
            while True:
                skip_whitespace_and_comments(port)
                nc = port.peek_char()
                if nc >= 0 and chr(nc) in (')', ']'):
                    port.read_char()
                    break
                if nc < 0:
                    raise Exception("Unexpected EOF in vector")
                elements.append(read_datum(port))
            return Vector(elements)
        elif next_c == '\\':
            port.read_char()
            token = read_token_from_port(port, initial_chars="#\\")
            return parse_char(token)
        elif next_c in ('t', 'f', 'T', 'F'):
            tc = chr(port.read_char()).lower()
            return Bool(tc == 't')
        elif next_c in ('u', 'U'):
            port.read_char()  # 'u'
            eight = chr(port.read_char())
            paren = chr(port.read_char())
            if eight == '8' and paren in ('(', '['):
                elements = []
                while True:
                    skip_whitespace_and_comments(port)
                    nc = port.peek_char()
                    if nc >= 0 and chr(nc) in (')', ']'):
                        port.read_char()
                        break
                    if nc < 0:
                        raise Exception("Unexpected EOF in bytevector")
                    val = read_datum(port)
                    if not isinstance(val, Integer) or not (0 <= val.value <= 255):
                        raise Exception("Invalid bytevector element")
                    elements.append(val.value)
                return Bytevector(bytearray(elements))
            raise Exception("Invalid #u8 syntax")
        else:
            token = read_token_from_port(port, initial_chars="#")
            return parse_form([token], [0])
    elif c in (')', ']'):
        raise Exception("Unexpected ')'")
    else:
        token = read_token_from_port(port)
        return parse_form([token], [0])