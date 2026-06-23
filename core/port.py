import io
import sys
from typing import Any


class Port:
    def read_line(self) -> str:
        return ""
    def read_char(self) -> int:
        return -1
    def peek_char(self) -> int:
        return -1
    def write(self, s: str) -> None:
        pass
    def flush(self) -> None:
        pass
    def close(self) -> None:
        pass
    @property
    def is_open(self) -> bool:
        return True


class StreamInputPort(Port):
    def __init__(self, stream: Any, close_on_exit: bool = False):
        self._stream = stream
        self._close_on_exit = close_on_exit
        self._peek = -2

    def read_line(self) -> str:
        try:
            return self._stream.readline() or ""
        except EOFError:
            return ""

    def read_char(self) -> int:
        if self._peek != -2:
            p = self._peek
            self._peek = -2
            return p
        char = self._stream.read(1)
        return ord(char) if char else -1

    def peek_char(self) -> int:
        if self._peek != -2:
            return self._peek
        char = self._stream.read(1)
        self._peek = ord(char) if char else -1
        return self._peek

    def close(self) -> None:
        if self._close_on_exit:
            self._stream.close()
        self._peek = -2

    @property
    def is_open(self) -> bool:
        return not self._stream.closed if hasattr(self._stream, 'closed') else True


class StreamOutputPort(Port):
    def __init__(self, stream: Any, close_on_exit: bool = False):
        self._stream = stream
        self._close_on_exit = close_on_exit

    def write(self, s: str) -> None:
        self._stream.write(s)
        self._stream.flush()

    def flush(self) -> None:
        self._stream.flush()

    def close(self) -> None:
        if self._close_on_exit:
            self._stream.close()

    @property
    def is_open(self) -> bool:
        return not self._stream.closed if hasattr(self._stream, 'closed') else True


class InputFilePort(StreamInputPort):
    def __init__(self, reader: io.TextIOWrapper):
        super().__init__(reader, close_on_exit=True)


class OutputFilePort(StreamOutputPort):
    def __init__(self, writer: io.TextIOWrapper):
        super().__init__(writer, close_on_exit=True)


class InputStringPort(StreamInputPort):
    def __init__(self, content: str):
        super().__init__(io.StringIO(content), close_on_exit=True)


class OutputStringPort(StreamOutputPort):
    def __init__(self):
        super().__init__(io.StringIO(), close_on_exit=True)

    def get_string(self) -> str:
        return self._stream.getvalue()


class ConsoleInputPort(StreamInputPort):
    def __init__(self):
        super().__init__(sys.stdin, close_on_exit=False)


class ConsoleOutputPort(StreamOutputPort):
    def __init__(self):
        super().__init__(sys.stdout, close_on_exit=False)


class ConsoleErrorPort(StreamOutputPort):
    def __init__(self):
        super().__init__(sys.stderr, close_on_exit=False)


class BinaryInputFilePort(Port):
    def __init__(self, path: str):
        self._fp = open(path, "rb")
        self._closed = False

    def read_char(self) -> int:
        if self._closed:
            return -1
        b = self._fp.read(1)
        return b[0] if b else -1

    def peek_char(self) -> int:
        if self._closed:
            return -1
        pos = self._fp.tell()
        b = self._fp.read(1)
        self._fp.seek(pos)
        return b[0] if b else -1

    def close(self) -> None:
        if not self._closed:
            self._fp.close()
            self._closed = True

    @property
    def is_open(self) -> bool:
        return not self._closed


class BinaryOutputFilePort(Port):
    def __init__(self, path: str):
        self._fp = open(path, "wb")
        self._closed = False

    def write(self, s: str) -> None:
        if not self._closed:
            self._fp.write(s.encode("utf-8"))
            self._fp.flush()

    def flush(self) -> None:
        if not self._closed:
            self._fp.flush()

    def close(self) -> None:
        if not self._closed:
            self._fp.close()
            self._closed = True

    @property
    def is_open(self) -> bool:
        return not self._closed


class InputBytevectorPort(Port):
    def __init__(self, data):
        self._data = bytes(data)
        self._pos = 0

    def read_char(self) -> int:
        if self._pos >= len(self._data):
            return -1
        b = self._data[self._pos]
        self._pos += 1
        return b

    def peek_char(self) -> int:
        if self._pos >= len(self._data):
            return -1
        return self._data[self._pos]

    def close(self) -> None:
        pass


class OutputBytevectorPort(Port):
    def __init__(self):
        self._buf = bytearray()

    def write(self, s: str) -> None:
        self._buf.extend(s.encode("utf-8"))

    def flush(self) -> None:
        pass

    def get_bytevector(self) -> bytearray:
        return self._buf

    def close(self) -> None:
        pass