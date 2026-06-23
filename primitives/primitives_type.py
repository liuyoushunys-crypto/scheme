import math
from typing import List
from core.schemevalue import *
from primitives.primitives_bytevector import prim_bytevector_p
from primitives.primitives_list import prim_list_p


def register_type_predicates(env: 'Env') -> None:
    env.define("null?", Prim("null?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Nil))))
    env.define("pair?", Prim("pair?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Cons))))
    env.define("symbol?", Prim("symbol?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Sym))))
    env.define("boolean?", Prim("boolean?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Bool))))
    env.define("string?", Prim("string?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Str))))
    env.define("char?", Prim("char?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Char))))
    env.define("vector?", Prim("vector?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Vector))))
    env.define("bytevector?", Prim("bytevector?", prim_bytevector_p))
    env.define("list?", Prim("list?", prim_list_p))
    env.define("zero?", Prim("zero?", lambda args: Bool(as_double(args[0]) == 0)))
    env.define("positive?", Prim("positive?", lambda args: Bool(as_double(args[0]) > 0)))
    env.define("negative?", Prim("negative?", lambda args: Bool(as_double(args[0]) < 0)))
    env.define("even?", Prim("even?", lambda args: Bool(as_int(args[0]) % 2 == 0)))
    env.define("odd?", Prim("odd?", lambda args: Bool(as_int(args[0]) % 2 != 0)))
    env.define("atom?", Prim("atom?", lambda args: Bool(not isinstance(args[0], Cons))))
    env.define("number?", Prim("number?", lambda args: Bool(len(args) == 1 and isinstance(args[0], (Num, Integer, Complex)))))
    env.define("complex?", Prim("complex?", lambda args: Bool(len(args) > 0 and isinstance(args[0], Complex))))
    env.define("real?", Prim("real?", lambda args: Bool(len(args) > 0 and (isinstance(args[0], (Num, Integer)) or (isinstance(args[0], Complex) and args[0].imag == 0)))))
    env.define("imag?", Prim("imag?", lambda args: Bool(len(args) > 0 and isinstance(args[0], Complex) and args[0].imag != 0)))
    env.define("integer?", Prim("integer?", lambda args: Bool(len(args) == 1 and (isinstance(args[0], Integer) or (isinstance(args[0], Num) and math.floor(args[0].value) == args[0].value)))))
    env.define("exact?", Prim("exact?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Integer))))
    env.define("inexact?", Prim("inexact?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Num))))
    env.define("port?", Prim("port?", lambda args: Bool(len(args) > 0 and isinstance(args[0], Port))))
    env.define("input-port?", Prim("input-port?", lambda args: Bool(len(args) == 1 and isinstance(args[0], (InputFilePort, InputStringPort, ConsoleInputPort)))))
    env.define("output-port?", Prim("output-port?", lambda args: Bool(len(args) == 1 and isinstance(args[0], (OutputFilePort, OutputStringPort, ConsoleOutputPort)))))
    env.define("procedure?", Prim("procedure?", lambda args: Bool(len(args) == 1 and isinstance(args[0], (Closure, Prim)))))
    env.define("closure?", Prim("closure?", lambda args: Bool(len(args) == 1 and isinstance(args[0], Closure))))
    env.define("macro?", Prim("macro?", lambda args: Bool(len(args) == 1 and isinstance(args[0], SyntaxRulesMacro))))
    env.define("environment?", Prim("environment?", lambda args: Bool(len(args) == 1 and isinstance(args[0], EnvValue))))
