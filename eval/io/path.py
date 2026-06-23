"""
File Path Operations - Based on Python pathlib module.

First-class citizen features:
  - Path objects can be used as values
  - Support path manipulation, query, and file I/O
  - Scheme strings and path objects integrate seamlessly

Path creation:
  (path "str")                      -> Path object
  (path "a" "b" "c")               -> Path from multiple segments

Properties:
  (path-parent p)                  -> parent directory
  (path-name p)                    -> file/dir name
  (path-stem p)                    -> filename without suffix
  (path-suffix p)                  -> file extension
  (path-parts p)                   -> list of path components

Query:
  (path-exists? p)                 -> check existence
  (path-file? p)                   -> check if file
  (path-dir? p)                    -> check if directory
  (path-absolute? p)               -> check if absolute
  (path-same? a b)                 -> check if same path

Manipulation:
  (path-join p "child" ...)        -> join path segments
  (path-with-name p "new")         -> replace filename
  (path-with-suffix p ".md")       -> replace extension
  (path-relative-to p "base")      -> relative path
  (path-resolve p)                 -> resolve to absolute

Directory listing:
  (path-iterdir p)                 -> list directory contents
  (path-glob p "*.py")             -> glob pattern matching
  (path-rglob p "**/*.py")         -> recursive glob
  (path-listdir p)                 -> list filenames (strings)

File I/O:
  (path-read-text p)               -> read file text
  (path-read-text p "utf-8")       -> read with encoding
  (path-write-text p "content")    -> write text
  (path-write-text p "content" "utf-8") -> write with encoding
  (path-read-bytes p)              -> read as bytes
  (path-write-bytes p bytes)       -> write bytes

Directory operations:
  (path-mkdir p)                   -> create directory
  (path-mkdir p #t)                -> create parents too
  (path-rmdir p)                   -> remove empty directory
  (path-unlink p)                  -> delete file
  (path-rename p new-name)         -> rename file/dir

Special paths:
  (path-home)                      -> home directory
  (path-cwd)                       -> current directory
  (path-tempdir)                   -> temp directory
  (path-cwd-set! "dir")            -> change working dir

Utility:
  (path-which "name")              -> find executable in PATH
  (path-expanduser "~")            -> expand ~ to home directory
"""

import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import List, Optional, Union
from dataclasses import dataclass

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


# ==================== Path Object ====================

@dataclass(frozen=True, slots=True)
class PathValue(SchemeValue):
    path: Path

    def __str__(self):
        return f"#<path \"{self.path}\">"


def _to_path(val: SchemeValue) -> Path:
    """Convert Scheme value to Path"""
    if isinstance(val, PathValue):
        return val.path
    if isinstance(val, Str):
        return Path(val.get_str())
    if isinstance(val, Sym):
        return Path(val.name)
    raise Exception(f"Expected path or string, got {type(val).__name__}")


def _unwrap_str(val: SchemeValue) -> str:
    """Extract string from Scheme value"""
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_int(val: SchemeValue) -> int:
    """Extract integer from Scheme value"""
    return int(unwrap_python_value(val))


def _cons_list(items) -> SchemeValue:
    """Build a Scheme list from Python iterable"""
    result = Nil()
    for item in reversed(list(items)):
        result = Cons(item, result)
    return result


# ==================== Path Creation ====================

def path_create(args: List[SchemeValue]) -> SchemeValue:
    """
    (path "str")          -> Path object
    (path "a" "b" "c")    -> joined path
    (path)                -> Path(".") current dir
    """
    if len(args) == 0:
        return PathValue(Path("."))

    segments = []
    for arg in args:
        segments.append(_unwrap_str(arg))

    return PathValue(Path(*segments))


# ==================== Properties ====================

def path_parent(args: List[SchemeValue]) -> SchemeValue:
    """(path-parent p) -> parent directory"""
    if len(args) < 1:
        raise Exception("path-parent: need 1 argument")
    p = _to_path(args[0])
    return PathValue(p.parent)


def path_name(args: List[SchemeValue]) -> SchemeValue:
    """(path-name p) -> file/dir name"""
    if len(args) < 1:
        raise Exception("path-name: need 1 argument")
    p = _to_path(args[0])
    return Str(p.name)


def path_stem(args: List[SchemeValue]) -> SchemeValue:
    """(path-stem p) -> filename without suffix"""
    if len(args) < 1:
        raise Exception("path-stem: need 1 argument")
    p = _to_path(args[0])
    return Str(p.stem)


def path_suffix(args: List[SchemeValue]) -> SchemeValue:
    """(path-suffix p) -> file extension"""
    if len(args) < 1:
        raise Exception("path-suffix: need 1 argument")
    p = _to_path(args[0])
    return Str(p.suffix)


def path_parts(args: List[SchemeValue]) -> SchemeValue:
    """(path-parts p) -> list of path components"""
    if len(args) < 1:
        raise Exception("path-parts: need 1 argument")
    p = _to_path(args[0])
    parts = [Str(part) for part in p.parts]
    return _cons_list(parts)


# ==================== Query ====================

def path_exists(args: List[SchemeValue]) -> SchemeValue:
    """(path-exists? p) -> check existence"""
    if len(args) < 1:
        raise Exception("path-exists?: need 1 argument")
    p = _to_path(args[0])
    return Bool(p.exists())


def path_is_file(args: List[SchemeValue]) -> SchemeValue:
    """(path-file? p) -> check if file"""
    if len(args) < 1:
        raise Exception("path-file?: need 1 argument")
    p = _to_path(args[0])
    return Bool(p.is_file())


def path_is_dir(args: List[SchemeValue]) -> SchemeValue:
    """(path-dir? p) -> check if directory"""
    if len(args) < 1:
        raise Exception("path-dir?: need 1 argument")
    p = _to_path(args[0])
    return Bool(p.is_dir())


def path_is_absolute(args: List[SchemeValue]) -> SchemeValue:
    """(path-absolute? p) -> check if absolute"""
    if len(args) < 1:
        raise Exception("path-absolute?: need 1 argument")
    p = _to_path(args[0])
    return Bool(p.is_absolute())


def path_same(args: List[SchemeValue]) -> SchemeValue:
    """(path-same? a b) -> check if same path"""
    if len(args) < 2:
        raise Exception("path-same?: need 2 arguments")
    a = _to_path(args[0])
    b = _to_path(args[1])
    return Bool(a.samefile(b) if a.exists() and b.exists() else False)


# ==================== Manipulation ====================

def path_join(args: List[SchemeValue]) -> SchemeValue:
    """(path-join p "child" ...) -> join path segments"""
    if len(args) < 1:
        raise Exception("path-join: need at least 1 argument")
    p = _to_path(args[0])
    for arg in args[1:]:
        p = p / _unwrap_str(arg)
    return PathValue(p)


def path_with_name(args: List[SchemeValue]) -> SchemeValue:
    """(path-with-name p "new") -> replace filename"""
    if len(args) < 2:
        raise Exception("path-with-name: need 2 arguments")
    p = _to_path(args[0])
    new_name = _unwrap_str(args[1])
    return PathValue(p.with_name(new_name))


def path_with_suffix(args: List[SchemeValue]) -> SchemeValue:
    """(path-with-suffix p ".md") -> replace extension"""
    if len(args) < 2:
        raise Exception("path-with-suffix: need 2 arguments")
    p = _to_path(args[0])
    new_suffix = _unwrap_str(args[1])
    return PathValue(p.with_suffix(new_suffix))


def path_relative_to(args: List[SchemeValue]) -> SchemeValue:
    """(path-relative-to p "base") -> relative path"""
    if len(args) < 2:
        raise Exception("path-relative-to: need 2 arguments")
    p = _to_path(args[0])
    base = _unwrap_str(args[1])
    return PathValue(p.relative_to(base))


def path_resolve(args: List[SchemeValue]) -> SchemeValue:
    """(path-resolve p) -> resolve to absolute"""
    if len(args) < 1:
        raise Exception("path-resolve: need 1 argument")
    p = _to_path(args[0])
    return PathValue(p.resolve())


# ==================== Directory Listing ====================

def path_iterdir(args: List[SchemeValue]) -> SchemeValue:
    """(path-iterdir p) -> list directory contents as Path objects"""
    if len(args) < 1:
        raise Exception("path-iterdir: need 1 argument")
    p = _to_path(args[0])
    if not p.is_dir():
        raise Exception(f"Not a directory: {p}")
    items = sorted(p.iterdir())
    return _cons_list([PathValue(item) for item in items])


def path_glob(args: List[SchemeValue]) -> SchemeValue:
    """(path-glob p "*.py") -> glob pattern matching"""
    if len(args) < 2:
        raise Exception("path-glob: need 2 arguments (path pattern)")
    p = _to_path(args[0])
    pattern = _unwrap_str(args[1])
    items = sorted(p.glob(pattern))
    return _cons_list([PathValue(item) for item in items])


def path_rglob(args: List[SchemeValue]) -> SchemeValue:
    """(path-rglob p "**/*.py") -> recursive glob"""
    if len(args) < 2:
        raise Exception("path-rglob: need 2 arguments")
    p = _to_path(args[0])
    pattern = _unwrap_str(args[1])
    items = sorted(p.rglob(pattern))
    return _cons_list([PathValue(item) for item in items])


def path_listdir(args: List[SchemeValue]) -> SchemeValue:
    """(path-listdir p) -> list filenames as strings"""
    if len(args) < 1:
        raise Exception("path-listdir: need 1 argument")
    p = _to_path(args[0])
    if not p.is_dir():
        raise Exception(f"Not a directory: {p}")
    names = sorted([entry.name for entry in p.iterdir()])
    return _cons_list([Str(name) for name in names])


# ==================== File I/O ====================

def path_read_text(args: List[SchemeValue]) -> SchemeValue:
    """(path-read-text p) -> read file text
    (path-read-text p encoding) -> read with encoding"""
    if len(args) < 1:
        raise Exception("path-read-text: need at least 1 argument")
    p = _to_path(args[0])
    encoding = "utf-8"
    if len(args) > 1:
        encoding = _unwrap_str(args[1])
    try:
        text = p.read_text(encoding=encoding)
        return Str(text)
    except Exception as e:
        raise Exception(f"Failed to read {p}: {e}")


def path_write_text(args: List[SchemeValue]) -> SchemeValue:
    """(path-write-text p "content") -> write text
    (path-write-text p "content" encoding) -> write with encoding"""
    if len(args) < 2:
        raise Exception("path-write-text: need at least 2 arguments (path content)")
    p = _to_path(args[0])
    content = _unwrap_str(args[1])
    encoding = "utf-8"
    if len(args) > 2:
        encoding = _unwrap_str(args[2])
    try:
        p.write_text(content, encoding=encoding)
        return PathValue(p)
    except Exception as e:
        raise Exception(f"Failed to write {p}: {e}")


def path_read_bytes(args: List[SchemeValue]) -> SchemeValue:
    """(path-read-bytes p) -> read as bytes"""
    if len(args) < 1:
        raise Exception("path-read-bytes: need 1 argument")
    p = _to_path(args[0])
    try:
        data = p.read_bytes()
        # Convert bytes to Scheme bytevector
        return Bytevector(bytearray(data))
    except Exception as e:
        raise Exception(f"Failed to read {p}: {e}")


def path_write_bytes(args: List[SchemeValue]) -> SchemeValue:
    """(path-write-bytes p bytes) -> write bytes"""
    if len(args) < 2:
        raise Exception("path-write-bytes: need 2 arguments (path bytes)")
    p = _to_path(args[0])
    data_arg = args[1]
    if isinstance(data_arg, Bytevector):
        data = bytes(data_arg.value)
    elif isinstance(data_arg, Str):
        data = data_arg.get_str().encode('utf-8')
    else:
        raise Exception(f"Expected bytes, got {type(data_arg).__name__}")
    try:
        p.write_bytes(data)
        return PathValue(p)
    except Exception as e:
        raise Exception(f"Failed to write {p}: {e}")


# ==================== Directory Operations ====================

def path_mkdir(args: List[SchemeValue]) -> SchemeValue:
    """(path-mkdir p) -> create directory
    (path-mkdir p #t)  -> create parents too"""
    if len(args) < 1:
        raise Exception("path-mkdir: need at least 1 argument")
    p = _to_path(args[0])
    parents = False
    if len(args) > 1 and not isinstance(args[1], Bool):
        raise Exception("path-mkdir: second argument must be boolean")
    if len(args) > 1:
        parents = args[1].value
    try:
        p.mkdir(parents=parents, exist_ok=parents)
        return PathValue(p)
    except Exception as e:
        raise Exception(f"Failed to create directory {p}: {e}")


def path_rmdir(args: List[SchemeValue]) -> SchemeValue:
    """(path-rmdir p) -> remove empty directory"""
    if len(args) < 1:
        raise Exception("path-rmdir: need 1 argument")
    p = _to_path(args[0])
    try:
        p.rmdir()
        return Bool(True)
    except Exception as e:
        raise Exception(f"Failed to remove directory {p}: {e}")


def path_unlink(args: List[SchemeValue]) -> SchemeValue:
    """(path-unlink p) -> delete file"""
    if len(args) < 1:
        raise Exception("path-unlink: need 1 argument")
    p = _to_path(args[0])
    try:
        p.unlink()
        return Bool(True)
    except Exception as e:
        raise Exception(f"Failed to delete {p}: {e}")


def path_rename(args: List[SchemeValue]) -> SchemeValue:
    """(path-rename p new) -> rename file/dir"""
    if len(args) < 2:
        raise Exception("path-rename: need 2 arguments (path new)")
    p = _to_path(args[0])
    new = _unwrap_str(args[1])
    try:
        result = p.rename(new)
        return PathValue(result)
    except Exception as e:
        raise Exception(f"Failed to rename {p} to {new}: {e}")


# ==================== Special Paths ====================

def path_home(args: List[SchemeValue]) -> SchemeValue:
    """(path-home) -> home directory"""
    return PathValue(Path.home())


def path_cwd(args: List[SchemeValue]) -> SchemeValue:
    """(path-cwd) -> current working directory"""
    return PathValue(Path.cwd())


def path_set_cwd(args: List[SchemeValue]) -> SchemeValue:
    """(path-cwd-set! "dir") -> change working directory"""
    if len(args) < 1:
        raise Exception("path-cwd-set!: need 1 argument")
    p = _to_path(args[0])
    os.chdir(str(p))
    return PathValue(p)


def path_tempdir(args: List[SchemeValue]) -> SchemeValue:
    """(path-tempdir) -> system temp directory"""
    return PathValue(Path(tempfile.gettempdir()))


# ==================== Utility ====================

def path_which(args: List[SchemeValue]) -> SchemeValue:
    """(path-which "name") -> find executable in PATH"""
    if len(args) < 1:
        raise Exception("path-which: need 1 argument")
    name = _unwrap_str(args[0])
    path = shutil.which(name)
    if path:
        return PathValue(Path(path))
    return Bool(False)


def path_expanduser(args: List[SchemeValue]) -> SchemeValue:
    """(path-expanduser "~") -> expand ~ to home directory"""
    if len(args) < 1:
        raise Exception("path-expanduser: need 1 argument")
    p = _to_path(args[0])
    return PathValue(p.expanduser())


def path_stat(args: List[SchemeValue]) -> SchemeValue:
    """(path-stat p) -> file stat info as alist"""
    if len(args) < 1:
        raise Exception("path-stat: need 1 argument")
    p = _to_path(args[0])
    if not p.exists():
        raise Exception(f"File does not exist: {p}")
    stat = p.stat()
    # Return stat info as property list (alist)
    pairs = [
        Cons(Sym("size"), Num(stat.st_size)),
        Cons(Sym("mode"), Num(stat.st_mode)),
        Cons(Sym("uid"), Num(stat.st_uid)),
        Cons(Sym("gid"), Num(stat.st_gid)),
        Cons(Sym("mtime"), Num(stat.st_mtime)),
        Cons(Sym("atime"), Num(stat.st_atime)),
        Cons(Sym("ctime"), Num(stat.st_ctime)),
    ]
    return _cons_list(pairs)


# ==================== Registration ====================

def register_path_primitives(env):
    """Register all path-related primitives"""
    # Creation
    env.define("path", Prim("path", path_create))

    # Properties
    env.define("path-parent", Prim("path-parent", path_parent))
    env.define("path-name", Prim("path-name", path_name))
    env.define("path-stem", Prim("path-stem", path_stem))
    env.define("path-suffix", Prim("path-suffix", path_suffix))
    env.define("path-parts", Prim("path-parts", path_parts))

    # Query
    env.define("path-exists?", Prim("path-exists?", path_exists))
    env.define("path-file?", Prim("path-file?", path_is_file))
    env.define("path-dir?", Prim("path-dir?", path_is_dir))
    env.define("path-absolute?", Prim("path-absolute?", path_is_absolute))
    env.define("path-same?", Prim("path-same?", path_same))

    # Manipulation
    env.define("path-join", Prim("path-join", path_join))
    env.define("path-with-name", Prim("path-with-name", path_with_name))
    env.define("path-with-suffix", Prim("path-with-suffix", path_with_suffix))
    env.define("path-relative-to", Prim("path-relative-to", path_relative_to))
    env.define("path-resolve", Prim("path-resolve", path_resolve))

    # Directory listing
    env.define("path-iterdir", Prim("path-iterdir", path_iterdir))
    env.define("path-glob", Prim("path-glob", path_glob))
    env.define("path-rglob", Prim("path-rglob", path_rglob))
    env.define("path-listdir", Prim("path-listdir", path_listdir))

    # File I/O
    env.define("path-read-text", Prim("path-read-text", path_read_text))
    env.define("path-write-text", Prim("path-write-text", path_write_text))
    env.define("path-read-bytes", Prim("path-read-bytes", path_read_bytes))
    env.define("path-write-bytes", Prim("path-write-bytes", path_write_bytes))

    # Directory operations
    env.define("path-mkdir", Prim("path-mkdir", path_mkdir))
    env.define("path-rmdir", Prim("path-rmdir", path_rmdir))
    env.define("path-unlink", Prim("path-unlink", path_unlink))
    env.define("path-rename", Prim("path-rename", path_rename))

    # Special paths
    env.define("path-home", Prim("path-home", path_home))
    env.define("path-cwd", Prim("path-cwd", path_cwd))
    env.define("path-cwd-set!", Prim("path-cwd-set!", path_set_cwd))
    env.define("path-tempdir", Prim("path-tempdir", path_tempdir))

    # Utility
    env.define("path-which", Prim("path-which", path_which))
    env.define("path-expanduser", Prim("path-expanduser", path_expanduser))
    env.define("path-stat", Prim("path-stat", path_stat))