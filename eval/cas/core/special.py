"""
special — CAS special functions, number theory, set operations, statistics
======================================================================

Wraps sympy functions for:
  - Polynomial root finding (roots/nroots)
  - ODE solving (dsolve)
  - Integral transforms (laplace, inverse-laplace, fourier, inverse-fourier)
  - Number theory (prime?, nextprime, prevprime, primerange, factorint,
    divisors, totient, mobius, continued-fraction, diophantine,
    chinese, jacobi-symbol, power-mod)
  - Set operations (set, union, intersection, set-difference,
    symmetric-difference, subset?, element?)
  - Statistics (mean, median, variance, std, correlation, regression)
  - Special functions (lambertw, polylog, stirling, bernoulli,
    euler_fn, fibonacci)
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value
import statistics
import math


# ---------------------------------------------------------------------------
# Helper: get the active CAS engine (sympy/symengine)
# ---------------------------------------------------------------------------

def _sympy():
    """Return engine proxy (auto-fallback symengine→sympy)."""
    from eval.cas.engine import get_engine
    return get_engine()


def _unwrap1(args):
    """Unwrap the first argument."""
    return unwrap_python_value(args[0])


def _unwrap(args):
    """Unwrap all arguments."""
    return [unwrap_python_value(a) for a in args]


# ===========================================================================
# Polynomial roots
# ===========================================================================

def cas_roots(args: List[SchemeValue]) -> SchemeValue:
    """
    (roots poly) — numerical roots via sympy.nroots

    Example:
      (roots #{x^2 + 2*x + 1})  ->  [-1.0, -1.0]
    """
    if len(args) < 1:
        raise Exception("roots: need (roots poly)")
    sp = _sympy()
    poly = sp.sympify(_unwrap1(args))
    result = sp.nroots(poly)
    return wrap_python_value(result)


def cas_nroots(args: List[SchemeValue]) -> SchemeValue:
    """
    (nroots poly) — numerical roots via sympy.nroots (alias for roots)

    Example:
      (nroots #{x^2 + 2*x + 1})  ->  [-1.0, -1.0]
    """
    return cas_roots(args)


# ===========================================================================
# ODE solving
# ===========================================================================

def cas_dsolve(args: List[SchemeValue]) -> SchemeValue:
    """
    (dsolve eqn func [ics]) — solve ODE symbolically

    Example:
      (dsolve #{diff(y(x), x, 2) + y(x)} y(x))
    """
    if len(args) < 2:
        raise Exception("dsolve: need (dsolve eqn func [ics])")
    sp = _sympy()
    eqn = sp.sympify(_unwrap1(args))
    func = _unwrap1(args[1:])
    ics = None
    if len(args) >= 3:
        ics = _unwrap1(args[2:])
    try:
        result = sp.dsolve(eqn, func, ics=ics)
    except Exception:
        result = sp.dsolve(eqn, func)
    return wrap_python_value(result)


# ===========================================================================
# Laplace transform
# ===========================================================================

def cas_laplace(args: List[SchemeValue]) -> SchemeValue:
    """
    (laplace expr t s) — Laplace transform

    Example:
      (laplace #{t^2} t s)
    """
    if len(args) < 3:
        raise Exception("laplace: need (laplace expr t s)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args[0:1]))
    t = sp.sympify(_unwrap1(args[1:2]))
    s = sp.sympify(_unwrap1(args[2:3]))
    result = sp.laplace_transform(expr, t, s)
    # laplace_transform returns (result, condition) tuple
    if isinstance(result, tuple):
        return wrap_python_value(result[0])
    return wrap_python_value(result)


def cas_inverse_laplace(args: List[SchemeValue]) -> SchemeValue:
    """
    (inverse-laplace expr s t) — inverse Laplace transform

    Example:
      (inverse-laplace #{1/(s^2)} s t)
    """
    if len(args) < 3:
        raise Exception("inverse-laplace: need (inverse-laplace expr s t)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args[0:1]))
    s = sp.sympify(_unwrap1(args[1:2]))
    t = sp.sympify(_unwrap1(args[2:3]))
    result = sp.inverse_laplace_transform(expr, s, t)
    return wrap_python_value(result)


# ===========================================================================
# Fourier transform
# ===========================================================================

def cas_fourier(args: List[SchemeValue]) -> SchemeValue:
    """
    (fourier expr x k) — Fourier transform

    Example:
      (fourier #{exp(-x^2)} x k)
    """
    if len(args) < 3:
        raise Exception("fourier: need (fourier expr x k)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args[0:1]))
    x = sp.sympify(_unwrap1(args[1:2]))
    k = sp.sympify(_unwrap1(args[2:3]))
    result = sp.fourier_transform(expr, x, k)
    return wrap_python_value(result)


def cas_inverse_fourier(args: List[SchemeValue]) -> SchemeValue:
    """
    (inverse-fourier expr k x) — inverse Fourier transform

    Example:
      (inverse-fourier #{exp(-k^2/4)/(2*sqrt(pi))} k x)
    """
    if len(args) < 3:
        raise Exception("inverse-fourier: need (inverse-fourier expr k x)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args[0:1]))
    k = sp.sympify(_unwrap1(args[1:2]))
    x = sp.sympify(_unwrap1(args[2:3]))
    result = sp.inverse_fourier_transform(expr, k, x)
    return wrap_python_value(result)


# ===========================================================================
# Number theory -- primality
# ===========================================================================

def cas_primep(args: List[SchemeValue]) -> SchemeValue:
    """
    (prime? n) — test if n is prime using sympy.isprime

    Example:
      (prime? 7)  ->  #t
    """
    if len(args) != 1:
        raise Exception("prime?: need (prime? n)")
    from sympy.ntheory import isprime
    n = _unwrap1(args)
    return Bool(isprime(n))


def cas_nextprime(args: List[SchemeValue]) -> SchemeValue:
    """
    (nextprime n) — smallest prime greater than n

    Example:
      (nextprime 10)  ->  11
    """
    if len(args) != 1:
        raise Exception("nextprime: need (nextprime n)")
    from sympy.ntheory import nextprime
    n = _unwrap1(args)
    return wrap_python_value(nextprime(n))


def cas_prevprime(args: List[SchemeValue]) -> SchemeValue:
    """
    (prevprime n) — largest prime less than n

    Example:
      (prevprime 10)  ->  7
    """
    if len(args) != 1:
        raise Exception("prevprime: need (prevprime n)")
    from sympy.ntheory import prevprime
    n = _unwrap1(args)
    return wrap_python_value(prevprime(n))


def cas_primerange(args: List[SchemeValue]) -> SchemeValue:
    """
    (primerange a b) — list of primes in [a, b)

    Example:
      (primerange 10 20)  ->  [11, 13, 17, 19]
    """
    if len(args) < 2:
        raise Exception("primerange: need (primerange a b)")
    from sympy.ntheory import primerange
    vals = _unwrap(args)
    a, b = int(vals[0]), int(vals[1])
    return wrap_python_value(list(primerange(a, b)))


# ===========================================================================
# Number theory -- factorization
# ===========================================================================

def cas_factorint(args: List[SchemeValue]) -> SchemeValue:
    """
    (factorint n) — prime factorization of n (dict of factor -> exponent)

    Example:
      (factorint 12)  ->  {2: 2, 3: 1}
    """
    if len(args) != 1:
        raise Exception("factorint: need (factorint n)")
    from sympy.ntheory import factorint
    n = _unwrap1(args)
    return wrap_python_value(factorint(int(n)))


# ===========================================================================
# Number theory -- divisors, totient, mobius
# ===========================================================================

def cas_divisors(args: List[SchemeValue]) -> SchemeValue:
    """
    (divisors n) — list of all positive divisors of n

    Example:
      (divisors 12)  ->  [1, 2, 3, 4, 6, 12]
    """
    if len(args) != 1:
        raise Exception("divisors: need (divisors n)")
    from sympy.ntheory import divisors
    n = _unwrap1(args)
    return wrap_python_value(sorted(divisors(int(n))))


def cas_totient(args: List[SchemeValue]) -> SchemeValue:
    """
    (totient n) — Euler's totient function phi(n)

    Example:
      (totient 10)  ->  4
    """
    if len(args) != 1:
        raise Exception("totient: need (totient n)")
    from sympy.ntheory import totient
    n = _unwrap1(args)
    return wrap_python_value(totient(int(n)))


def cas_mobius(args: List[SchemeValue]) -> SchemeValue:
    """
    (mobius n) — Moebius function mu(n)

    Example:
      (mobius 6)  ->  -1
    """
    if len(args) != 1:
        raise Exception("mobius: need (mobius n)")
    from sympy.ntheory import mobius
    n = _unwrap1(args)
    return wrap_python_value(mobius(int(n)))


# ===========================================================================
# Number theory -- continued fraction, diophantine
# ===========================================================================

def cas_continued_fraction(args: List[SchemeValue]) -> SchemeValue:
    """
    (continued-fraction expr) — continued fraction convergents

    Example:
      (continued-fraction #{sqrt(2)})  ->  [1, 3/2, 7/5, 17/12, ...]
    """
    if len(args) < 1:
        raise Exception("continued-fraction: need (continued-fraction expr)")
    sp = _sympy()
    expr = sp.sympify(_unwrap1(args))
    from sympy.ntheory.continued_fraction import continued_fraction_convergents
    from sympy.ntheory.continued_fraction import continued_fraction as _cf
    cf = _cf(expr)
    result = list(continued_fraction_convergents(cf))
    return wrap_python_value(result)


def cas_diophantine(args: List[SchemeValue]) -> SchemeValue:
    """
    (diophantine eqn) — solve Diophantine equation

    Example:
      (diophantine #{x^2 + y^2 - z^2})  ->  {(t0, t1, t2), ...}
    """
    if len(args) < 1:
        raise Exception("diophantine: need (diophantine eqn)")
    sp = _sympy()
    eqn = sp.sympify(_unwrap1(args))
    result = sp.diophantine(eqn)
    return wrap_python_value(result)


# ===========================================================================
# Number theory -- chinese remainder, jacobi symbol, modular exponent
# ===========================================================================

def cas_chinese(args: List[SchemeValue]) -> SchemeValue:
    """
    (chinese moduli remainders) — Chinese remainder theorem

    Example:
      (chinese '(2 3) '(3 5 7))  ->  23  (x = 2 mod 3, x = 3 mod 5, x = 2 mod 7...)
    """
    if len(args) != 2:
        raise Exception("chinese: need (chinese moduli remainders)")
    from sympy.ntheory.modular import crt
    moduli = _unwrap1(args[0:1])
    remainders = _unwrap1(args[1:2])
    moduli = [int(m) for m in moduli]
    remainders = [int(r) for r in remainders]
    result, _ = crt(moduli, remainders)
    return wrap_python_value(result)


def cas_jacobi_symbol(args: List[SchemeValue]) -> SchemeValue:
    """
    (jacobi-symbol a n) — Jacobi symbol (a/n)

    Example:
      (jacobi-symbol 2 5)  ->  -1
    """
    if len(args) != 2:
        raise Exception("jacobi-symbol: need (jacobi-symbol a n)")
    from sympy.ntheory import jacobi_symbol
    a, n = _unwrap(args)
    return wrap_python_value(jacobi_symbol(int(a), int(n)))


def cas_power_mod(args: List[SchemeValue]) -> SchemeValue:
    """
    (power-mod a n m) — a^n mod m

    Example:
      (power-mod 2 10 1000)  ->  24
    """
    if len(args) != 3:
        raise Exception("power-mod: need (power-mod a n m)")
    a, n, m = _unwrap(args)
    return wrap_python_value(pow(int(a), int(n), int(m)))


# ===========================================================================
# Set operations
# ===========================================================================

def cas_set(args: List[SchemeValue]) -> SchemeValue:
    """
    (set ...) — create a finite set

    Example:
      (set 1 2 3)  ->  {1, 2, 3}
    """
    vals = _unwrap(args)
    from sympy import FiniteSet
    return wrap_python_value(FiniteSet(*vals))


def cas_union(args: List[SchemeValue]) -> SchemeValue:
    """
    (union s1 s2 ...) — union of sets

    Example:
      (union (set 1 2) (set 2 3))  ->  {1, 2, 3}
    """
    if len(args) < 1:
        raise Exception("union: need at least 1 set")
    from sympy import Union
    sets = _unwrap(args)
    result = sets[0]
    for s in sets[1:]:
        result = Union(result, s)
    return wrap_python_value(result)


def cas_intersection(args: List[SchemeValue]) -> SchemeValue:
    """
    (intersection s1 s2 ...) — intersection of sets

    Example:
      (intersection (set 1 2) (set 2 3))  ->  {2}
    """
    if len(args) < 1:
        raise Exception("intersection: need at least 1 set")
    from sympy import Intersection
    sets = _unwrap(args)
    result = sets[0]
    for s in sets[1:]:
        result = Intersection(result, s)
    return wrap_python_value(result)


def cas_set_difference(args: List[SchemeValue]) -> SchemeValue:
    """
    (set-difference s1 s2) — set difference

    Example:
      (set-difference (set 1 2 3) (set 2 3))  ->  {1}
    """
    if len(args) != 2:
        raise Exception("set-difference: need (set-difference s1 s2)")
    from sympy import Complement
    s1, s2 = _unwrap(args)
    return wrap_python_value(Complement(s1, s2))


def cas_symdiff(args: List[SchemeValue]) -> SchemeValue:
    """
    (symmetric-difference s1 s2) — symmetric difference

    Example:
      (symmetric-difference (set 1 2) (set 2 3))  ->  {1, 3}
    """
    if len(args) != 2:
        raise Exception("symmetric-difference: need (symmetric-difference s1 s2)")
    from sympy import SymmetricDifference
    s1, s2 = _unwrap(args)
    return wrap_python_value(SymmetricDifference(s1, s2))


def cas_is_subset(args: List[SchemeValue]) -> SchemeValue:
    """
    (subset? s1 s2) — test if s1 is a subset of s2

    Example:
      (subset? (set 1) (set 1 2))  ->  #t
    """
    if len(args) != 2:
        raise Exception("subset?: need (subset? s1 s2)")
    s1, s2 = _unwrap(args)
    if hasattr(s1, 'is_subset'):
        return Bool(s1.is_subset(s2))
    from sympy import FiniteSet
    return Bool(FiniteSet(*s1).is_subset(FiniteSet(*s2)))


def cas_is_element(args: List[SchemeValue]) -> SchemeValue:
    """
    (element? x s) — test if x is an element of set s

    Example:
      (element? 1 (set 1 2))  ->  #t
    """
    if len(args) != 2:
        raise Exception("element?: need (element? x s)")
    x, s = _unwrap(args)
    if hasattr(s, '__contains__'):
        return Bool(x in s)
    return Bool(False)


# ===========================================================================
# Statistics
# ===========================================================================

def cas_mean(args: List[SchemeValue]) -> SchemeValue:
    """
    (mean ...) — arithmetic mean of numbers

    Example:
      (mean 1 2 3)  ->  2.0
    """
    if len(args) < 1:
        raise Exception("mean: need at least 1 number")
    vals = _unwrap(args)
    return wrap_python_value(statistics.mean(vals))


def cas_median(args: List[SchemeValue]) -> SchemeValue:
    """
    (median ...) — median of numbers

    Example:
      (median 1 2 3)  ->  2
    """
    if len(args) < 1:
        raise Exception("median: need at least 1 number")
    vals = _unwrap(args)
    return wrap_python_value(statistics.median(vals))


def cas_variance(args: List[SchemeValue]) -> SchemeValue:
    """
    (variance ...) — sample variance

    Example:
      (variance 1 2 3)  ->  1.0
    """
    if len(args) < 2:
        raise Exception("variance: need at least 2 numbers")
    vals = _unwrap(args)
    return wrap_python_value(statistics.variance(vals))


def cas_std(args: List[SchemeValue]) -> SchemeValue:
    """
    (std ...) — sample standard deviation

    Example:
      (std 1 2 3)  ->  1.0
    """
    if len(args) < 2:
        raise Exception("std: need at least 2 numbers")
    vals = _unwrap(args)
    return wrap_python_value(statistics.stdev(vals))


def cas_correlation(args: List[SchemeValue]) -> SchemeValue:
    """
    (correlation xs ys) — Pearson correlation coefficient

    Example:
      (correlation '(1 2 3) '(1 2 3))  ->  1.0
    """
    if len(args) != 2:
        raise Exception("correlation: need (correlation xs ys)")
    xs = _unwrap1(args[0:1])
    ys = _unwrap1(args[1:2])
    if len(xs) != len(ys) or len(xs) < 2:
        raise Exception("correlation: xs and ys must be same length >= 2")
    return wrap_python_value(statistics.correlation(xs, ys))


def cas_regression(args: List[SchemeValue]) -> SchemeValue:
    """
    (regression xs ys) — linear regression y = ax + b

    Returns (slope, intercept) as a list.

    Example:
      (regression '(1 2 3) '(2 4 6))  ->  (2.0, 0.0)
    """
    if len(args) != 2:
        raise Exception("regression: need (regression xs ys)")
    xs = _unwrap1(args[0:1])
    ys = _unwrap1(args[1:2])
    if len(xs) != len(ys) or len(xs) < 2:
        raise Exception("regression: xs and ys must be same length >= 2")
    slope, intercept = statistics.linear_regression(xs, ys)
    return wrap_python_value([slope, intercept])


# ===========================================================================
# Special functions
# ===========================================================================

def cas_lambertw(args: List[SchemeValue]) -> SchemeValue:
    """
    (lambertw x) — Lambert W function

    Example:
      (lambertw 1)  ->  0.567... (Omega constant)
    """
    if len(args) < 1:
        raise Exception("lambertw: need (lambertw x)")
    sp = _sympy()
    x = sp.sympify(_unwrap1(args))
    if len(args) >= 2:
        k = int(unwrap_python_value(args[1]))
        return wrap_python_value(sp.lambertw(x, k))
    return wrap_python_value(sp.lambertw(x))


def cas_polylog(args: List[SchemeValue]) -> SchemeValue:
    """
    (polylog s z) — polylogarithm function Li_s(z)

    Example:
      (polylog 2 0.5)  ->  0.582...
    """
    if len(args) < 2:
        raise Exception("polylog: need (polylog s z)")
    sp = _sympy()
    s, z = _unwrap(args)
    return wrap_python_value(sp.polylog(sp.sympify(s), sp.sympify(z)))


def cas_stirling(args: List[SchemeValue]) -> SchemeValue:
    """
    (stirling n k) — Stirling numbers of the first kind

    Example:
      (stirling 4 2)  ->  11
    """
    if len(args) != 2:
        raise Exception("stirling: need (stirling n k)")
    from sympy.functions.combinatorial.numbers import stirling
    n, k = _unwrap(args)
    return wrap_python_value(stirling(int(n), int(k)))


def cas_bernoulli(args: List[SchemeValue]) -> SchemeValue:
    """
    (bernoulli n) — Bernoulli numbers B_n

    Example:
      (bernoulli 4)  ->  -1/30
    """
    if len(args) < 1:
        raise Exception("bernoulli: need (bernoulli n)")
    from sympy.functions.combinatorial.numbers import bernoulli
    n = _unwrap1(args)
    return wrap_python_value(bernoulli(int(n)))


def cas_euler(args: List[SchemeValue]) -> SchemeValue:
    """
    (euler_fn n) — Euler numbers E_n

    Example:
      (euler_fn 4)  ->  5
    """
    if len(args) < 1:
        raise Exception("euler_fn: need (euler_fn n)")
    from sympy.functions.combinatorial.numbers import euler
    n = _unwrap1(args)
    return wrap_python_value(euler(int(n)))


def cas_fibonacci(args: List[SchemeValue]) -> SchemeValue:
    """
    (fibonacci n) — Fibonacci numbers F_n

    Example:
      (fibonacci 10)  ->  55
    """
    if len(args) < 1:
        raise Exception("fibonacci: need (fibonacci n)")
    from sympy.functions.combinatorial.numbers import fibonacci
    n = _unwrap1(args)
    return wrap_python_value(fibonacci(int(n)))


# ===========================================================================
# Registration
# ===========================================================================

def register_special_primitives(env):
    """Register special CAS primitives."""
    prims = [
        # Polynomial roots
        ("roots", cas_roots),
        ("nroots", cas_nroots),

        # ODE
        ("dsolve", cas_dsolve),

        # Integral transforms
        ("laplace", cas_laplace),
        ("inverse-laplace", cas_inverse_laplace),
        ("fourier", cas_fourier),
        ("inverse-fourier", cas_inverse_fourier),

        # Number theory — primality
        ("prime?", cas_primep),
        ("nextprime", cas_nextprime),
        ("prevprime", cas_prevprime),
        ("primerange", cas_primerange),

        # Number theory — factorization
        ("factorint", cas_factorint),

        # Number theory — divisors/totient/mobius
        ("divisors", cas_divisors),
        ("totient", cas_totient),
        ("mobius", cas_mobius),

        # Number theory — continued fraction / diophantine
        ("continued-fraction", cas_continued_fraction),
        ("diophantine", cas_diophantine),

        # Number theory — CRT, Jacobi, pow_mod
        ("chinese", cas_chinese),
        ("jacobi-symbol", cas_jacobi_symbol),
        ("power-mod", cas_power_mod),

        # Set operations
        ("set", cas_set),
        ("union", cas_union),
        ("intersection", cas_intersection),
        ("set-difference", cas_set_difference),
        ("symmetric-difference", cas_symdiff),
        ("subset?", cas_is_subset),
        ("element?", cas_is_element),

        # Statistics
        ("mean", cas_mean),
        ("median", cas_median),
        ("variance", cas_variance),
        ("std", cas_std),
        ("correlation", cas_correlation),
        ("regression", cas_regression),

        # Special functions
        ("lambertw", cas_lambertw),
        ("polylog", cas_polylog),
        ("stirling", cas_stirling),
        ("bernoulli", cas_bernoulli),
        ("euler", cas_euler),
        ("fibonacci", cas_fibonacci),
    ]
    for name, func in prims:
        env.define(name, Prim(name, func))


register_primitives = register_special_primitives