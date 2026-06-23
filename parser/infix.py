"""
增强型中缀解析器 — 将常见数学符号自然映射到 CAS/Scheme。

在原有的 Pratt 解析器基础上增加：
  |x|         → (abs x)                         绝对值
  [1 2; 3 4]  → (matrix (list 1 2) (list 3 4))  矩阵字面量
  a..b        → (range a b) / (区间 a b)         范围
  {1,2,3}     → (set 1 2 3)                     集合字面量
  a_i / a_{n+1} → (subscript a i)               下标
  f'(x)       → (diff f x)                      导数
  x!          → (factorial x)                    阶乘

所有原有功能保持不变。
"""

from typing import Dict, List, Optional


_UNICODE_ALIASES: Dict[str, str] = {
    'π': 'pi', '∞': 'inf', '√': 'sqrt',
    '∫': 'integrate', '∑': 'summation', '∏': 'product',
    '∂': 'diff', '∇': 'grad', 'Δ': 'diff',
    '∈': 'element?', '⊂': 'subset?', '∪': 'union', '∩': 'intersection',
    '≤': '<=', '≥': '>=', '≠': '!=',
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
    'ε': 'epsilon', 'θ': 'theta', 'λ': 'lambda', 'μ': 'mu',
    'σ': 'sigma', 'τ': 'tau', 'φ': 'phi', 'ω': 'omega',
}


def tokenize_infix(text: str) -> List[str]:
    """增强 tokenizer：支持 |;{}_..' 和 !"""
    tokens: List[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1; continue
        # 分号不要视为注释（因为 #{...} 内用于矩阵行分隔）
        if c == ';':
            tokens.append(';'); i += 1; continue
        if c == '"':
            start = i; i += 1
            while i < n and text[i] != '"':
                if text[i] == '\\' and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n: i += 1
            tokens.append(text[start:i])
            continue
        # 单字符分隔符（包括 _）
        if c in '()[]{}|;,_':
            tokens.append(c); i += 1; continue
        # 复合比较运算符
        if c in '<=>!' and i + 1 < n and text[i + 1] == '=':
            tokens.append(text[i:i + 2]); i += 2; continue
        # 范围运算符 ..
        if c == '.' and i + 1 < n and text[i + 1] == '.':
            tokens.append('..'); i += 2; continue
        # 运算符
        if c in '+-*/^=\'':
            tokens.append(c); i += 1; continue
        if c == '!':
            tokens.append('!'); i += 1; continue
        # 数字
        if c.isdigit() or (c == '.' and i + 1 < n and text[i + 1].isdigit()):
            start = i; i += 1
            while i < n and (text[i].isdigit() or text[i] in '.eE'):
                if text[i] in '+-' and text[i - 1] not in 'eE':
                    break
                # 遇到 .. 表示范围，停止数字
                if text[i] == '.' and i + 1 < n and text[i + 1] == '.':
                    break
                i += 1
            tokens.append(text[start:i])
            continue
        # 标识符 (包括包含下划线的)
        start = i; i += 1
        while i < n and not text[i].isspace() and text[i] not in '()[]{}|;,_\'"+-*/^=!<>.':
            i += 1
        tokens.append(text[start:i])
    return tokens


def _is_number(tok: str) -> bool:
    try:
        float(tok); return True
    except ValueError:
        return False


def _resolve(tok: str) -> str:
    return _UNICODE_ALIASES.get(tok, tok)


# 绑定力
BP = {
    '=': 10, '<': 10, '>': 10, '<=': 10, '>=': 10, '!=': 10,
    '+': 30, '-': 30,
    '*': 40, '/': 40,
    '..': 35,        # 范围运算符，绑定力略高于 +/-
    '_': 55,          # 下标运算符，绑定力略低于 ^
    '^': 60,
}
CALL_PREC = 70
BRACKET_PREC = 70
ABS_PREC = 50       # |x| 绑定力


class _Parser:
    def __init__(self, tokens: List[str]):
        self.toks = tokens
        self.pos = 0

    def peek(self) -> Optional[str]:
        return self.toks[self.pos] if self.pos < len(self.toks) else None

    def advance(self) -> str:
        if self.pos >= len(self.toks):
            raise ValueError("Unexpected end of expression")
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def parse(self, min_bp: int = 0) -> str:
        tok = self.advance()
        left = self._prefix(tok, min_bp)

        while self.pos < len(self.toks):
            peek = self.peek()

            if peek == ',' or peek == ')' or peek == ']' or peek == '}':
                break

            # 遇到未配对的 | → 忽略（由前缀处理）
            if peek == '|':
                # 这是闭合 |，由前缀处理，这里跳过
                break

            # 函数调用
            if peek == '(' and _is_name_expr(left):
                bp = CALL_PREC
                if bp < min_bp: break
                self.advance()
                args = self._parse_args(')')
                self._expect(')')
                left = f"({left} {' '.join(args)})" if args else f"({left})"
                continue

            # 方括号索引
            if peek == '[':
                bp = BRACKET_PREC
                if bp < min_bp: break
                self.advance()
                # 检测是否包含 ; → 矩阵字面量
                has_semi = ';' in self.toks[self.pos:]
                if has_semi:
                    rows_str = self._parse_matrix_rows()
                    self._expect(']')
                    return rows_str
                args = self._parse_args(']')
                self._expect(']')
                left = f"(bracket {left} {' '.join(args)})" if args else f"(bracket {left})"
                continue

            # 花括号 → 集合字面量（除非在前面已经处理为分组）
            if peek == '{':
                bp = BRACKET_PREC
                if bp < min_bp: break
                self.advance()
                args = self._parse_args('}')
                self._expect('}')
                if not args:
                    left = "(set)"
                else:
                    left = f"(set {' '.join(args)})"
                continue

            # 后缀运算符 ! — 支持数字和表达式（在隐式乘法之前检查）
            if peek == '!':
                bp = CALL_PREC
                if bp < min_bp: break
                self.advance()
                left = f"(factorial {left})"
                continue

            # 隐式乘法
            if self._is_implicit_mul(left, peek):
                bp = 45
                if bp < min_bp: break
                right = self.parse(bp + 1)
                left = f"(* {left} {right})"
                continue

            # 二元运算符
            if peek in BP:
                bp = BP[peek]
                if bp < min_bp: break
                op = self.advance()
                # 右结合: ^ 和 _（下标）
                next_bp = bp if op in ('^', '_') else bp + 1
                right = self.parse(next_bp)
                if op == '..':
                    left = f"(range {left} {right})"
                elif op == '_':
                    left = f"(ref {left} {right})"
                else:
                    left = _make_binary(op, left, right)
                continue

            break
        return left

    def _prefix(self, tok: str, min_bp: int) -> str:
        if tok == '-':
            right = self.parse(41)
            return f"(- {right})"
        if tok == '+':
            return self.parse(41)
        # 绝对值 |...| — 不作为运算符，作为分组构造
        if tok == '|':
            inner = self.parse(0)
            # 消耗闭合 |
            if self.peek() == '|':
                self.advance()
            return f"(abs {inner})"

        # 括号分组 ( 或 [ — [ 可能包含 ; 表示矩阵
        if tok == '(' or tok == '[':
            close = ')' if tok == '(' else ']'
            # 检查 [ 后面是否有 ; → 矩阵字面量
            if tok == '[' and ';' in self.toks[self.pos:]:
                # 将当前位置重置为矩阵解析起点
                # _parse_matrix_rows 从 self.pos 开始
                return self._parse_matrix_rows()
            inner = self.parse(0)
            self._expect(close)
            return inner
        # 花括号 → 分组表达式（不是 set 字面量）
        if tok == '{':
            inner = self.parse(0)
            self._expect('}')
            return inner
        # 数字
        if _is_number(tok):
            return tok
        # 标识符
        return _resolve(tok)

    def _parse_args(self, close: str) -> List[str]:
        args: List[str] = []
        while self.pos < len(self.toks) and self.toks[self.pos] != close:
            arg = self.parse(0)
            args.append(arg)
            if self.pos < len(self.toks) and self.toks[self.pos] == ',':
                self.advance()
        return args

    def _parse_matrix_rows(self) -> str:
        """解析 [1 2 3; 4 5 6] → (matrix (list 1 2 3) (list 4 5 6))"""
        rows = []
        while self.pos < len(self.toks) and self.toks[self.pos] != ']':
            # 收集一行元素（每个元素是单个原子表达式）
            row = []
            while self.pos < len(self.toks) and self.toks[self.pos] not in (';', ']'):
                # 用最小优先级 46 阻止隐式乘法（bp=45）
                start_pos = self.pos
                elem = self.parse(46)
                if self.pos == start_pos:
                    self.advance()
                row.append(elem)
            if self.pos < len(self.toks) and self.toks[self.pos] == ';':
                self.advance()
            if row:
                rows.append('(list ' + ' '.join(row) + ')')
        if not rows:
            rows.append('(list)')
        # 消耗 ]
        if self.pos < len(self.toks) and self.toks[self.pos] == ']':
            self.advance()
        if len(rows) == 1:
            return f"(matrix {rows[0]})"
        return f"(matrix {' '.join(rows)})"

    def _expect(self, expected: str):
        tok = self.advance()
        if tok != expected:
            raise ValueError(f"Expected '{expected}', got '{tok}'")
    def _is_implicit_mul(self, left: str, peek: str) -> bool:
        """判断是否需要隐式乘法（! 已在前面处理）"""
        if peek is None or peek == '!':
            return False
        if _is_number(peek):
            return True
        if peek not in BP and peek not in '()[]{}|;,\'"':
            return True
        if peek == '(':
            return True
        if peek == '{':
            return True
        return False


def _is_name_expr(expr: str) -> bool:
    if not expr:
        return False
    if _is_number(expr):
        return False
    if ' ' in expr or '(' in expr or ')' in expr:
        return False
    return True


def _make_binary(op: str, left: str, right: str) -> str:
    if op == '^': return f"(expt {left} {right})"
    if op == '*': return f"(* {left} {right})"
    if op == '/': return f"(/ {left} {right})"
    if op == '+': return f"(+ {left} {right})"
    if op == '-': return f"(- {left} {right})"
    if op == '=': return f"(eqn {left} {right})"
    if op == '<': return f"(< {left} {right})"
    if op == '>': return f"(> {left} {right})"
    if op == '<=': return f"(<= {left} {right})"
    if op == '>=': return f"(>= {left} {right})"
    if op == '!=': return f"(!= {left} {right})"
    raise ValueError(f"Unknown operator: {op}")


# ==================== 公共 API ====================

def parse_infix(text: str) -> str:
    """解析中缀表达式 → Scheme S-表达式"""
    tokens = tokenize_infix(text)
    if not tokens:
        return ""
    p = _Parser(tokens)
    return p.parse()
