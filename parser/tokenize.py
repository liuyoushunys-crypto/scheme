from typing import List


def tokenize(input_str: str) -> List[str]:
    tokens = []
    i = 0
    span_len = len(input_str)
    while i < span_len:
        if input_str[i].isspace():
            i += 1
            continue
        if input_str[i] == ';':
            while i < span_len and input_str[i] not in ('\n', '\r'):
                i += 1
            continue

        if input_str[i] == '#' and i + 1 < span_len:
            if input_str[i+1] == '{':
                # #{...} infix expression — collect everything until matching '}'
                start = i
                i += 2  # skip '#{'
                depth = 1
                while i < span_len and depth > 0:
                    if input_str[i] == '{':
                        depth += 1
                    elif input_str[i] == '}':
                        depth -= 1
                    i += 1
                if depth > 0:
                    raise Exception("Unclosed #{...} infix expression")
                tokens.append(input_str[start:i])
                continue
            if input_str[i+1] == "'":
                tokens.append("#'")
                i += 2
                continue
            if input_str[i+1] == '`':
                tokens.append("#`")
                i += 2
                continue
            if input_str[i+1] == ',':
                if i + 2 < span_len and input_str[i+2] == '@':
                    tokens.append("#,@")
                    i += 3
                    continue
                tokens.append("#,")
                i += 2
                continue

        if input_str[i] == '#' and i + 1 < span_len and input_str[i+1] in ('(', '\\', '['):
            if input_str[i+1] in ('(', '['):
                tokens.append("#(")
                i += 2
                continue
            i += 2
            start = i
            while i < span_len and not input_str[i].isspace() and input_str[i] not in ('(', ')', '[', ']', ';', '"', "'", '`', ','):
                i += 1
            tokens.append("#\\" + input_str[start:i])
            continue

        if input_str[i] == '#' and i + 1 < span_len and input_str[i+1] in ('b', 'B', 'o', 'O', 'x', 'X'):
            start = i
            i += 2
            while i < span_len and not input_str[i].isspace() and input_str[i] not in ('(', ')', '[', ']', ';', '"', "'", '`', ','):
                i += 1
            tokens.append(input_str[start:i])
            continue
        if input_str[i] == '#' and i + 1 < span_len and input_str[i+1].isdigit():
            start = i
            i += 1
            while i < span_len and not input_str[i].isspace() and input_str[i] not in ('(', ')', '[', ']', ';', '"', "'", '`', ','):
                i += 1
            tokens.append(input_str[start:i])
            continue
        if input_str[i] in ('(', ')', '[', ']'):
            tokens.append(input_str[i])
            i += 1
            continue
        if input_str[i] == '"' and i + 2 < span_len and input_str[i:i+3] == '"""':
            # Python 风格多行字符串 """..."""
            start = i
            i += 3  # skip opening """
            # 跳过紧跟的换行（符合 Python 习惯）
            if i < span_len and input_str[i] == '\n':
                i += 1
            elif i < span_len and input_str[i:i+2] == '\r\n':
                i += 2
            while i + 2 < span_len:
                if input_str[i:i+3] == '"""':
                    i += 3
                    break
                if input_str[i] == '\\' and i + 1 < span_len:
                    i += 2
                else:
                    i += 1
            else:
                raise Exception("Unclosed triple-quoted string")
            tokens.append(input_str[start:i])
            continue

        if input_str[i] == '"':
            start = i
            i += 1
            while i < span_len and input_str[i] != '"':
                if input_str[i] == '\\' and i + 1 < span_len:
                    i += 2
                else:
                    i += 1
            if i < span_len:
                i += 1
            tokens.append(input_str[start:i])
            continue
        if input_str[i] == ',' and i + 1 < span_len and input_str[i+1] == '@':
            tokens.append(",@")
            i += 2
            continue
        if input_str[i] in ("'", '`', ','):
            tokens.append(input_str[i])
            i += 1
            continue

        sym_start = i
        while i < span_len and not input_str[i].isspace() and input_str[i] not in ('(', ')', '[', ']', ';', '"', "'", '`', ','):
            i += 1
        tokens.append(input_str[sym_start:i])
    return tokens
