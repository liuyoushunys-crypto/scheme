"""
Compression & Archiving - Based on Python gzip, zipfile, bz2, lzma, tarfile modules.

GZip:
  (gzip-compress data)              -> compress string to gzip bytes
  (gzip-decompress bytes)           -> decompress gzip bytes
  (gzip-file path)                  -> read gzip file
  (gzip-write path data)            -> write gzip file

Zip:
  (zip-create path files)           -> create zip from list of files
  (zip-extract path dest)           -> extract zip to directory
  (zip-list path)                   -> list files in zip
  (zip-read path filename)          -> read specific file from zip

BZip2:
  (bz2-compress data)               -> compress with bzip2
  (bz2-decompress bytes)            -> decompress bzip2

LZMA / XZ:
  (lzma-compress data)              -> compress with lzma/xz
  (lzma-decompress bytes)           -> decompress lzma/xz

Tar:
  (tar-create path files)           -> create tar.gz archive
  (tar-extract path dest)           -> extract tar.gz archive
  (tar-list path)                   -> list files in tar

Utility:
  (compression-formats)             -> list available formats
"""
import gzip
import bz2
import lzma
import zipfile
import tarfile
import os
import io
from typing import List

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _unwrap_str(val) -> str:
    if isinstance(val, (Str,)):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_bytes(val) -> bytes:
    if isinstance(val, Bytevector):
        return bytes(val.data)
    if isinstance(val, Str):
        return val.get_str().encode("utf-8")
    return _unwrap_str(val).encode("utf-8")


def _scheme_list_to_pylist(val) -> list:
    items = []
    c = val
    while isinstance(c, Cons):
        items.append(c.car)
        c = c.cdr
    return items


# ==================== GZip ====================


def gzip_compress(args: List[SchemeValue]) -> SchemeValue:
    """(gzip-compress data) -> gzip compressed bytes"""
    if len(args) < 1:
        raise Exception("gzip-compress: need 1 argument")
    data = _unwrap_bytes(args[0])
    level = int(unwrap_python_value(args[1])) if len(args) > 1 else 9
    compressed = gzip.compress(data, compresslevel=level)
    return Bytevector(bytearray(compressed))


def gzip_decompress(args: List[SchemeValue]) -> SchemeValue:
    """(gzip-decompress bytes) -> decompressed data"""
    if len(args) < 1:
        raise Exception("gzip-decompress: need 1 argument")
    data = _unwrap_bytes(args[0])
    result = gzip.decompress(data)
    return Bytevector(bytearray(result))


def gzip_file(args: List[SchemeValue]) -> SchemeValue:
    """(gzip-file path) -> read gzip file content"""
    if len(args) < 1:
        raise Exception("gzip-file: need 1 argument (path)")
    path = _unwrap_str(args[0])
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        content = f.read()
    return Str(content)


def gzip_write(args: List[SchemeValue]) -> SchemeValue:
    """(gzip-write path data) -> write gzip file"""
    if len(args) < 2:
        raise Exception("gzip-write: need 2 arguments (path data)")
    path = _unwrap_str(args[0])
    data = _unwrap_str(args[1])
    level = int(unwrap_python_value(args[2])) if len(args) > 2 else 9
    with gzip.open(path, 'wt', encoding='utf-8', compresslevel=level) as f:
        f.write(data)
    return Bool(True)


# ==================== Zip ====================


def zip_create(args: List[SchemeValue]) -> SchemeValue:
    """(zip-create path files) -> create zip archive"""
    if len(args) < 2:
        raise Exception("zip-create: need 2 arguments (path files)")
    zip_path = _unwrap_str(args[0])
    files_val = args[1]
    files = _scheme_list_to_pylist(files_val)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            fpath = _unwrap_str(f)
            arcname = os.path.basename(fpath)
            zf.write(fpath, arcname)
    return Bool(True)


def zip_extract(args: List[SchemeValue]) -> SchemeValue:
    """(zip-extract path dest) -> extract zip to directory"""
    if len(args) < 2:
        raise Exception("zip-extract: need 2 arguments (path dest)")
    zip_path = _unwrap_str(args[0])
    dest = _unwrap_str(args[1])
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)
    return Bool(True)


def zip_list(args: List[SchemeValue]) -> SchemeValue:
    """(zip-list path) -> list files in zip"""
    if len(args) < 1:
        raise Exception("zip-list: need 1 argument (path)")
    zip_path = _unwrap_str(args[0])
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
    result = Nil()
    for name in reversed(names):
        result = Cons(Str(name), result)
    return result


def zip_read(args: List[SchemeValue]) -> SchemeValue:
    """(zip-read path filename) -> read specific file from zip"""
    if len(args) < 2:
        raise Exception("zip-read: need 2 arguments (path filename)")
    zip_path = _unwrap_str(args[0])
    filename = _unwrap_str(args[1])
    with zipfile.ZipFile(zip_path, 'r') as zf:
        content = zf.read(filename)
    return Bytevector(bytearray(content))


# ==================== BZip2 ====================


def bz2_compress(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("bz2-compress: need 1 argument")
    data = _unwrap_bytes(args[0])
    level = int(unwrap_python_value(args[1])) if len(args) > 1 else 9
    compressed = bz2.compress(data, compresslevel=level)
    return Bytevector(bytearray(compressed))


def bz2_decompress(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("bz2-decompress: need 1 argument")
    data = _unwrap_bytes(args[0])
    result = bz2.decompress(data)
    return Bytevector(bytearray(result))


# ==================== LZMA ====================


def lzma_compress(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("lzma-compress: need 1 argument")
    data = _unwrap_bytes(args[0])
    compressed = lzma.compress(data)
    return Bytevector(bytearray(compressed))


def lzma_decompress(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("lzma-decompress: need 1 argument")
    data = _unwrap_bytes(args[0])
    result = lzma.decompress(data)
    return Bytevector(bytearray(result))


# ==================== Tar ====================


def tar_create(args: List[SchemeValue]) -> SchemeValue:
    """(tar-create path files) -> create tar.gz archive"""
    if len(args) < 2:
        raise Exception("tar-create: need 2 arguments (path files)")
    tar_path = _unwrap_str(args[0])
    files_val = args[1]
    files = _scheme_list_to_pylist(files_val)
    mode = 'w:gz'  # default gzip compressed
    if len(args) > 2:
        compression = _unwrap_str(args[2]).lower()
        mode_map = {'gz': 'w:gz', 'bzip2': 'w:bz2', 'xz': 'w:xz', 'none': 'w'}
        mode = mode_map.get(compression, 'w:gz')
    with tarfile.open(tar_path, mode) as tf:
        for f in files:
            fpath = _unwrap_str(f)
            tf.add(fpath, arcname=os.path.basename(fpath))
    return Bool(True)


def tar_extract(args: List[SchemeValue]) -> SchemeValue:
    """(tar-extract path dest) -> extract tar archive"""
    if len(args) < 2:
        raise Exception("tar-extract: need 2 arguments (path dest)")
    tar_path = _unwrap_str(args[0])
    dest = _unwrap_str(args[1])
    with tarfile.open(tar_path, 'r:*') as tf:
        tf.extractall(dest)
    return Bool(True)


def tar_list(args: List[SchemeValue]) -> SchemeValue:
    """(tar-list path) -> list files in tar"""
    if len(args) < 1:
        raise Exception("tar-list: need 1 argument (path)")
    tar_path = _unwrap_str(args[0])
    with tarfile.open(tar_path, 'r:*') as tf:
        names = tf.getnames()
    result = Nil()
    for name in reversed(names):
        result = Cons(Str(name), result)
    return result


# ==================== Utility ====================


def compression_formats(args: List[SchemeValue]) -> SchemeValue:
    result = Nil()
    for name in reversed(['gzip', 'bz2', 'lzma', 'zip', 'tar']):
        result = Cons(Sym(name), result)
    return result


# ==================== Registration ====================


def register_compress_primitives(env):
    env.define("gzip-compress", Prim("gzip-compress", gzip_compress))
    env.define("gzip-decompress", Prim("gzip-decompress", gzip_decompress))
    env.define("gzip-file", Prim("gzip-file", gzip_file))
    env.define("gzip-write", Prim("gzip-write", gzip_write))

    env.define("zip-create", Prim("zip-create", zip_create))
    env.define("zip-extract", Prim("zip-extract", zip_extract))
    env.define("zip-list", Prim("zip-list", zip_list))
    env.define("zip-read", Prim("zip-read", zip_read))

    env.define("bz2-compress", Prim("bz2-compress", bz2_compress))
    env.define("bz2-decompress", Prim("bz2-decompress", bz2_decompress))

    env.define("lzma-compress", Prim("lzma-compress", lzma_compress))
    env.define("lzma-decompress", Prim("lzma-decompress", lzma_decompress))

    env.define("tar-create", Prim("tar-create", tar_create))
    env.define("tar-extract", Prim("tar-extract", tar_extract))
    env.define("tar-list", Prim("tar-list", tar_list))

    env.define("compression-formats", Prim("compression-formats", compression_formats))