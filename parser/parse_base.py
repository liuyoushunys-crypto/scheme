from core.schemevalue import *


def parse_base(token: str, radix: int) -> SchemeValue:
    digits = token[2:]
    negative = False
    if digits.startswith("-"):
        negative = True
        digits = digits[1:]
    elif digits.startswith("+"):
        digits = digits[1:]
    if not digits:
        raise Exception("Empty radix number: " + token)

    try:
        val = int(digits, radix)
        if negative:
            val = -val
        return Integer(val)
    except ValueError:
        raise Exception("Invalid radix number representation: " + token)
