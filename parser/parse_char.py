from core.schemevalue import *


def parse_char(token: str) -> SchemeValue:
    inner = token[2:]
    if len(inner) == 0:
        return Char(0x20)
    if len(inner) == 1:
        return Char(ord(inner[0]))
    match inner:
        case "space": return Char(0x20)
        case "newline": return Char(0x0A)
        case "tab": return Char(0x09)
        case "return": return Char(0x0D)
        case "backspace": return Char(0x08)
        case _ if inner.startswith("x") and len(inner) > 1:
            try:
                return Char(int(inner[1:], 16))
            except ValueError:
                pass
    return Char(ord(inner[0]))
