import math
from typing import List
from core.schemevalue import *


def prim_add(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_binary_op
    result = try_py_binary_op("+", args)
    if result is not None:
        return result
    if len(args) == 0:
        return Integer(0)
    has_complex = any(isinstance(a, Complex) for a in args)
    if has_complex:
        r, im = 0.0, 0.0
        for a in args:
            if isinstance(a, Complex):
                r += a.real
                im += a.imag
            else:
                r += as_double(a)
        return to_complex_number(r, im)
    if all(isinstance(a, Integer) for a in args):
        return Integer(sum(a.value for a in args))
    return Num(sum(as_double(a) for a in args))


def prim_sub(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_binary_op, try_py_unary_op
    result = try_py_binary_op("-", args)
    if result is not None:
        return result
    if len(args) == 0:
        return Integer(0)
    if len(args) == 1:
        r = try_py_unary_op("negate", args)
        if r is not None:
            return r
        v = args[0]
        match v:
            case Complex(real, imag): return Complex(-real, -imag)
            case Integer(val): return Integer(-val)
            case _: return Num(-as_double(v))
    has_complex = any(isinstance(a, Complex) for a in args)
    if has_complex:
        c0 = args[0]
        r = c0.real if isinstance(c0, Complex) else as_double(c0)
        im = c0.imag if isinstance(c0, Complex) else 0.0
        for a in args[1:]:
            if isinstance(a, Complex):
                r -= a.real
                im -= a.imag
            else:
                r -= as_double(a)
        return to_complex_number(r, im)
    if all(isinstance(a, Integer) for a in args):
        res = args[0].value
        for a in args[1:]:
            res -= a.value
        return Integer(res)
    res_f = as_double(args[0])
    for a in args[1:]:
        res_f -= as_double(a)
    return Num(res_f)


def prim_mul(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_binary_op
    result = try_py_binary_op("*", args)
    if result is not None:
        return result
    has_complex = any(isinstance(a, Complex) for a in args)
    if has_complex:
        r, im = 1.0, 0.0
        for a in args:
            if isinstance(a, Complex):
                nr = r * a.real - im * a.imag
                nim = r * a.imag + im * a.real
                r, im = nr, nim
            else:
                d = as_double(a)
                r *= d
                im *= d
        return to_complex_number(r, im)
    if all(isinstance(a, Integer) for a in args):
        res = 1
        for a in args:
            res *= a.value
        return Integer(res)
    res_f = 1.0
    for a in args:
        res_f *= as_double(a)
    return Num(res_f)


def prim_div(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_binary_op
    result = try_py_binary_op("/", args)
    if result is not None:
        return result
    if len(args) == 0:
        raise Exception("/: arity mismatch")
    if len(args) == 1:
        v = args[0]
        if isinstance(v, Complex):
            denom = v.real * v.real + v.imag * v.imag
            if denom == 0:
                raise Exception("division by zero")
            return Complex(v.real / denom, -v.imag / denom)
        d = as_double(v)
        if d == 0:
            raise Exception("division by zero")
        return to_number(1.0 / d)
    has_complex = any(isinstance(a, Complex) for a in args)
    if has_complex:
        c0 = args[0]
        r = c0.real if isinstance(c0, Complex) else as_double(c0)
        im = c0.imag if isinstance(c0, Complex) else 0.0
        for a in args[1:]:
            if isinstance(a, Complex):
                denom = a.real * a.real + a.imag * a.imag
                if denom == 0:
                    raise Exception("division by zero")
                nr = (r * a.real + im * a.imag) / denom
                nim = (im * a.real - r * a.imag) / denom
                r, im = nr, nim
            else:
                d = as_double(a)
                if d == 0:
                    raise Exception("division by zero")
                r /= d
                im /= d
        return to_complex_number(r, im)
    val = as_double(args[0])
    for a in args[1:]:
        d = as_double(a)
        if d == 0:
            raise Exception("division by zero")
        val /= d
    return Num(val)


def prim_abs(args: List[SchemeValue]) -> SchemeValue:
    v = args[0]
    if isinstance(v, Complex):
        return Num(math.sqrt(v.real * v.real + v.imag * v.imag))
    if isinstance(v, Integer):
        return Integer(abs(v.value))
    return Num(abs(as_double(v)))


def prim_asinh(args: List[SchemeValue]) -> SchemeValue:
    v = as_double(args[0])
    return Num(math.log(v + math.sqrt(v * v + 1.0)))


def prim_expt(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_binary_op
    result = try_py_binary_op("expt", args)
    if result is not None:
        return result
    base_val, pow_val = args[0], args[1]
    if isinstance(base_val, Integer) and isinstance(pow_val, Integer) and pow_val.value >= 0:
        return Integer(base_val.value ** pow_val.value)
    if isinstance(base_val, Complex):
        r = math.sqrt(base_val.real * base_val.real + base_val.imag * base_val.imag)
        theta = math.atan2(base_val.imag, base_val.real)
        p_real = as_double(pow_val)
        log_r = math.log(r)
        mag = math.exp(p_real * log_r)
        new_theta = p_real * theta
        return Complex(mag * math.cos(new_theta), mag * math.sin(new_theta))
    return Num(as_double(base_val) ** as_double(pow_val))


def prim_log(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_unary_math
    result = try_py_unary_math("log", args)
    if result is not None:
        return result
    if isinstance(args[0], Complex):
        c = args[0]
        r = math.sqrt(c.real * c.real + c.imag * c.imag)
        theta = math.atan2(c.imag, c.real)
        return Complex(math.log(r), theta)
    return Num(math.log(as_double(args[0])) if len(args) == 1 else (math.log(as_double(args[0])) / math.log(as_double(args[1]))))


def prim_modulo(args: List[SchemeValue]) -> SchemeValue:
    n = as_int(args[0])
    d = as_int(args[1])
    r = n % d
    return Integer(r + abs(d) if r < 0 else r)


def prim_sin(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_unary_math
    result = try_py_unary_math("sin", args)
    if result is not None:
        return result
    if isinstance(args[0], Complex):
        c = args[0]
        return Complex(math.sin(c.real) * math.cosh(c.imag), math.cos(c.real) * math.sinh(c.imag))
    return Num(math.sin(as_double(args[0])))


def prim_cos(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_unary_math
    result = try_py_unary_math("cos", args)
    if result is not None:
        return result
    if isinstance(args[0], Complex):
        c = args[0]
        return Complex(math.cos(c.real) * math.cosh(c.imag), -math.sin(c.real) * math.sinh(c.imag))
    return Num(math.cos(as_double(args[0])))


def prim_sqrt(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_py_arithmetic import try_py_unary_math
    result = try_py_unary_math("sqrt", args)
    if result is not None:
        return result
    if isinstance(args[0], Complex):
        c = args[0]
        r = math.sqrt(c.real * c.real + c.imag * c.imag)
        real = math.sqrt((r + c.real) / 2.0)
        imag = (1 if c.imag >= 0 else -1) * math.sqrt((r - c.real) / 2.0)
        return Complex(real, imag)
    val = as_double(args[0])
    if val < 0:
        return Complex(0.0, math.sqrt(-val))
    return Num(math.sqrt(val))


def prim_gcd(args: List[SchemeValue]) -> SchemeValue:
    g = 0
    for a in args:
        g = math.gcd(g, abs(as_int(a)))
    return Integer(g)


def prim_lcm(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 0:
        return Integer(1)
    l = abs(as_int(args[0]))
    for a in args[1:]:
        v = abs(as_int(a))
        l = (l * v) // math.gcd(l, v) if l != 0 and v != 0 else 0
    return Integer(l)



def _py_math_prim(name, fallback):
    """创建 Python-aware 数学原语：先尝试 Python 代理，失败后走 Scheme 原生"""
    def wrapper(args):
        from eval.eval_py_arithmetic import try_py_unary_math
        r = try_py_unary_math(name, args)
        if r is not None:
            return r
        return fallback(args)
    return Prim(name, wrapper)


def _py_bin_prim(name, fallback):
    """创建 Python-aware 二元原语"""
    def wrapper(args):
        from eval.eval_py_arithmetic import try_py_binary_op
        r = try_py_binary_op(name, args)
        if r is not None:
            return r
        return fallback(args)
    return Prim(name, wrapper)


def register_arithmetic(env: 'Env') -> None:
    env.define("+", Prim("+", prim_add))
    env.define("-", Prim("-", prim_sub))
    env.define("*", Prim("*", prim_mul))
    env.define("/", Prim("/", prim_div))
    env.define("abs", Prim("abs", prim_abs))
    env.define("ceiling", Prim("ceiling", lambda args: to_number(math.ceil(as_double(args[0])))))
    env.define("floor", Prim("floor", lambda args: to_number(math.floor(as_double(args[0])))))
    env.define("truncate", Prim("truncate", lambda args: to_number(math.trunc(as_double(args[0])))))
    env.define("round", Prim("round", lambda args: to_number(round(as_double(args[0])))))
    env.define("modulo", _py_bin_prim("modulo", lambda args: Integer(prim_modulo(args).value)))
    env.define("quotient", _py_bin_prim("quotient", lambda args: Integer(as_int(args[0]) // as_int(args[1]))))
    env.define("remainder", Prim("remainder", lambda args: Integer(as_int(args[0]) % as_int(args[1]))))
    env.define("gcd", Prim("gcd", prim_gcd))
    env.define("lcm", Prim("lcm", prim_lcm))
    env.define("max", Prim("max", lambda args: Nil() if len(args) == 0 else (args[0] if len(args) == 1 else (max(args, key=as_double)))))
    env.define("min", Prim("min", lambda args: Nil() if len(args) == 0 else (args[0] if len(args) == 1 else (min(args, key=as_double)))))
    env.define("sqrt", _py_math_prim("sqrt", lambda args: prim_sqrt(args)))
    env.define("expt", _py_math_prim("expt", lambda args: prim_expt(args)))
    env.define("log", _py_math_prim("log", lambda args: prim_log(args)))
    env.define("exp", _py_math_prim("exp", lambda args: Complex(math.exp(args[0].real) * math.cos(args[0].imag), math.exp(args[0].real) * math.sin(args[0].imag)) if isinstance(args[0], Complex) else Num(math.exp(as_double(args[0])))))

    # 经典三角函数
    env.define("sin", Prim("sin", prim_sin))
    env.define("cos", Prim("cos", prim_cos))
    env.define("tan", _py_math_prim("tan", lambda args: Num(math.tan(as_double(args[0])))))
    env.define("asin", _py_math_prim("asin", lambda args: Num(math.asin(as_double(args[0])))))
    env.define("acos", _py_math_prim("acos", lambda args: Num(math.acos(as_double(args[0])))))
    env.define("atan", _py_math_prim("atan", lambda args: (
        Num(math.atan(as_double(args[0])))
        if len(args) == 1
        else Num(math.atan2(as_double(args[0]), as_double(args[1])))
    )))
    env.define("sinh", _py_math_prim("sinh", lambda args: Num(math.sinh(as_double(args[0])))))
    env.define("cosh", _py_math_prim("cosh", lambda args: Num(math.cosh(as_double(args[0])))))
    env.define("tanh", _py_math_prim("tanh", lambda args: Num(math.tanh(as_double(args[0])))))
    env.define("asinh", _py_math_prim("asinh", lambda args: prim_asinh(args)))
    env.define("acosh", _py_math_prim("acosh", lambda args: Num(math.acosh(as_double(args[0])))))
    env.define("atanh", _py_math_prim("atanh", lambda args: Num(0.5 * math.log((1.0 + as_double(args[0])) / (1.0 - as_double(args[0]))))))
    env.define("sec", Prim("sec", lambda args: Num(1.0 / math.cos(as_double(args[0])))))
    env.define("csc", Prim("csc", lambda args: Num(1.0 / math.sin(as_double(args[0])))))
    env.define("cot", Prim("cot", lambda args: Num(1.0 / math.tan(as_double(args[0])))))

    # 复数运算原语
    env.define("real-part", Prim("real-part", lambda args: Num(args[0].real) if isinstance(args[0], Complex) else Num(as_double(args[0]))))
    env.define("imag-part", Prim("imag-part", lambda args: Num(args[0].imag) if isinstance(args[0], Complex) else Num(0.0)))
    env.define("magnitude", Prim("magnitude", lambda args: Num(math.sqrt(args[0].real * args[0].real + args[0].imag * args[0].imag)) if isinstance(args[0], Complex) else Num(abs(as_double(args[0])))))
    env.define("angle", Prim("angle", lambda args: Num(math.atan2(args[0].imag, args[0].real)) if isinstance(args[0], Complex) else Num(math.atan2(0.0, as_double(args[0])))))
    env.define("make-rectangular", Prim("make-rectangular", lambda args: Complex(as_double(args[0]), as_double(args[1]))))
    env.define("make-polar", Prim("make-polar", lambda args: Complex(as_double(args[0]) * math.cos(as_double(args[1])), as_double(args[0]) * math.sin(as_double(args[1])))))
    env.define("conjugate", Prim("conjugate", lambda args: Complex(args[0].real, -args[0].imag) if isinstance(args[0], Complex) else args[0]))

    # 精确度转换原语
    env.define("exact->inexact", Prim("exact->inexact", lambda args: Num(as_double(args[0]))))
    env.define("inexact->exact", Prim("inexact->exact", lambda args: Integer(int(math.trunc(as_double(args[0]))))))
