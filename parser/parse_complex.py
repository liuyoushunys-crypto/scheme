import re
from typing import Optional
from core.schemevalue import *

_FLOAT_RE = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'

_COMPLEX_REAL_IMAG_RE = re.compile(
    rf'^#({_FLOAT_RE})([+-](?:\d+(?:\.\d*)?|\.\d+)?)[iI]$'
)
_COMPLEX_PURE_IMAG_RE = re.compile(
    rf'^#([+-]?(?:\d+(?:\.\d*)?|\.\d+)?)[iI]$'
)


def parse_complex(token: str) -> Optional[Complex]:
    if not token.startswith('#') or len(token) < 3:
        return None

    match_ab = _COMPLEX_REAL_IMAG_RE.match(token)
    if match_ab:
        real_str, imag_str = match_ab.groups()
        real_val = float(real_str)
        if imag_str == '+':
            imag_val = 1.0
        elif imag_str == '-':
            imag_val = -1.0
        else:
            imag_val = float(imag_str)
        return Complex(real_val, imag_val)

    match_b = _COMPLEX_PURE_IMAG_RE.match(token)
    if match_b:
        imag_str = match_b.group(1)
        if not imag_str or imag_str == '+':
            imag_val = 1.0
        elif imag_str == '-':
            imag_val = -1.0
        else:
            imag_val = float(imag_str)
        return Complex(0.0, imag_val)

    return None
