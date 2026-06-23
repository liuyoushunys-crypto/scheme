import os
from typing import List
from core.schemevalue import *
from core.port import BinaryInputFilePort, BinaryOutputFilePort
from core.tail_call import apply
from parser.parse_program import parse_program
from reader.reader import read_datum
import primitives.primitives_shared as _shared

current_input_port: Port = ConsoleInputPort()
current_output_port: Port = ConsoleOutputPort()
current_error_port: Port = ConsoleErrorPort()


def prim_display(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) > 0:
        val = args[0]
        s = val.get_str() if isinstance(val, Str) else scheme_format(val)
        current_output_port.write(s)
    return Sym("undefined")


def prim_newline(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    current_output_port.write("\n")
    return Sym("undefined")


def prim_load(args: List[SchemeValue]) -> SchemeValue:
    from eval.eval_scheme import eval_scheme
    match args:
        case [Str() as s]:
            path = s.get_str()
            if not os.path.exists(path):
                raise FileNotFoundError(f"load: file not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                expressions = parse_program(f.read())
            last = Sym("undefined")
            for expr in expressions:
                last = eval_scheme(expr, _shared.registering_env)
            return last
    raise Exception("load: expected string path")


def prim_read(args: List[SchemeValue]) -> SchemeValue:
    port = args[0] if (len(args) > 0 and isinstance(args[0], Port)) else current_input_port
    return read_datum(port)


def prim_write(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) > 0:
        current_output_port.write(scheme_format(args[0]))
    return Sym("undefined")


def prim_close_port(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Port):
        args[0].close()
        return Sym("undefined")
    raise Exception("close-port: expected port")


def prim_set_input_port(args: List[SchemeValue]) -> SchemeValue:
    global current_input_port
    if len(args) == 1 and isinstance(args[0], Port):
        current_input_port = args[0]
        return Sym("undefined")
    raise Exception("set-input-port error")


def prim_set_output_port(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) == 1 and isinstance(args[0], Port):
        current_output_port = args[0]
        return Sym("undefined")
    raise Exception("set-output-port error")


def prim_with_input_from_file(args: List[SchemeValue]) -> SchemeValue:
    global current_input_port
    if len(args) == 2 and isinstance(args[0], Str):
        path = args[0].get_str()
        thunk = args[1]
        old_port = current_input_port
        current_input_port = InputFilePort(open(path, "r", encoding="utf-8"))
        try:
            return apply(thunk, [], _shared.registering_env)
        finally:
            current_input_port.close()
            current_input_port = old_port
    raise Exception("with-input-from-file error")


def prim_with_output_to_file(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) == 2 and isinstance(args[0], Str):
        path = args[0].get_str()
        thunk = args[1]
        old_port = current_output_port
        current_output_port = OutputFilePort(open(path, "w", encoding="utf-8"))
        try:
            return apply(thunk, [], _shared.registering_env)
        finally:
            current_output_port.close()
            current_output_port = old_port
    raise Exception("with-output-to-file error")


def prim_call_with_input_file(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Str):
        path = args[0].get_str()
        proc = args[1]
        port = InputFilePort(open(path, "r", encoding="utf-8"))
        try:
            return apply(proc, [port], _shared.registering_env)
        finally:
            port.close()
    raise Exception("call-with-input-file error")


def prim_call_with_output_file(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 2 and isinstance(args[0], Str):
        path = args[0].get_str()
        proc = args[1]
        port = OutputFilePort(open(path, "w", encoding="utf-8"))
        try:
            return apply(proc, [port], _shared.registering_env)
        finally:
            port.close()
    raise Exception("call-with-output-file error")


def prim_peek_char(args: List[SchemeValue]) -> SchemeValue:
    global current_input_port
    port = args[0] if (len(args) > 0 and isinstance(args[0], Port)) else current_input_port
    ch = port.peek_char()
    return Sym("eof") if ch < 0 else Char(ch)


def prim_read_char(args: List[SchemeValue]) -> SchemeValue:
    global current_input_port
    port = args[0] if (len(args) > 0 and isinstance(args[0], Port)) else current_input_port
    ch = port.read_char()
    return Sym("eof") if ch < 0 else Char(ch)


def prim_write_shared(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) > 0:
        current_output_port.write(scheme_format(args[0]))
    return Sym("undefined")


def prim_write_simple(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    if len(args) > 0:
        current_output_port.write(scheme_format(args[0]))
    return Sym("undefined")


def prim_open_binary_input_file(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return BinaryInputFilePort(args[0].get_str())
    raise Exception("open-binary-input-file error")


def prim_open_binary_output_file(args: List[SchemeValue]) -> SchemeValue:
    if len(args) == 1 and isinstance(args[0], Str):
        return BinaryOutputFilePort(args[0].get_str())
    raise Exception("open-binary-output-file error")


def prim_write_char(args: List[SchemeValue]) -> SchemeValue:
    global current_output_port
    port = args[1] if (len(args) > 1 and isinstance(args[1], Port)) else current_output_port
    if len(args) > 0 and isinstance(args[0], Char):
        port.write(chr(args[0].value))
    return Sym("undefined")


def register_io(env: 'Env') -> None:
    env.define("current-input-port", Prim("current-input-port", lambda _: current_input_port))
    env.define("current-output-port", Prim("current-output-port", lambda _: current_output_port))
    env.define("current-error-port", Prim("current-error-port", lambda _: current_error_port))
    env.define("set-input-port", Prim("set-input-port", prim_set_input_port))
    env.define("set-output-port", Prim("set-output-port", prim_set_output_port))
    env.define("open-input-file", Prim("open-input-file", lambda args: InputFilePort(open(args[0].get_str(), "r", encoding="utf-8")) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("open-input-file error"))))
    env.define("open-output-file", Prim("open-output-file", lambda args: OutputFilePort(open(args[0].get_str(), "w", encoding="utf-8")) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("open-output-file error"))))
    env.define("open-input-string", Prim("open-input-string", lambda args: InputStringPort(args[0].get_str()) if (len(args) == 1 and isinstance(args[0], Str)) else (_ for _ in ()).throw(Exception("open-input-string error"))))
    env.define("open-output-string", Prim("open-output-string", lambda _: OutputStringPort()))
    env.define("get-output-string", Prim("get-output-string", lambda args: Str(list(args[0].get_string())) if (len(args) == 1 and isinstance(args[0], OutputStringPort)) else (_ for _ in ()).throw(Exception("get-output-string error"))))
    env.define("close-input-port", Prim("close-input-port", lambda args: args[0].close() or Sym("undefined") if (len(args) == 1 and isinstance(args[0], Port)) else (_ for _ in ()).throw(Exception("close-input-port error"))))
    env.define("close-output-port", Prim("close-output-port", lambda args: args[0].close() or Sym("undefined") if (len(args) == 1 and isinstance(args[0], Port)) else (_ for _ in ()).throw(Exception("close-output-port error"))))
    env.define("close-port", Prim("close-port", prim_close_port))
    env.define("read", Prim("read", prim_read))
    env.define("display", Prim("display", prim_display))
    env.define("write", Prim("write", prim_write))
    env.define("newline", Prim("newline", prim_newline))
    env.define("peek-char", Prim("peek-char", prim_peek_char))
    env.define("read-char", Prim("read-char", prim_read_char))
    env.define("write-char", Prim("write-char", prim_write_char))
    env.define("char-ready?", Prim("char-ready?", lambda args: Bool(True)))
    env.define("with-input-from-file", Prim("with-input-from-file", prim_with_input_from_file))
    env.define("with-output-to-file", Prim("with-output-to-file", prim_with_output_to_file))
    env.define("call-with-input-file", Prim("call-with-input-file", prim_call_with_input_file))
    env.define("call-with-output-file", Prim("call-with-output-file", prim_call_with_output_file))
    env.define("write-shared", Prim("write-shared", prim_write_shared))
    env.define("write-simple", Prim("write-simple", prim_write_simple))
    env.define("open-binary-input-file", Prim("open-binary-input-file", prim_open_binary_input_file))
    env.define("open-binary-output-file", Prim("open-binary-output-file", prim_open_binary_output_file))
