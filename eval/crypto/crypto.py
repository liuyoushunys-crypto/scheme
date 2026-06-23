"""
Crypto/Hash Module - Based on Python hashlib, secrets, base64, and hmac libraries.

Hash (hashlib):
  (md5 str)                         -> MD5 hex digest
  (sha1 str)                        -> SHA1 hex digest
  (sha256 str)                      -> SHA256 hex digest
  (sha512 str)                      -> SHA512 hex digest
  (sha3-256 str)                    -> SHA3-256 hex digest
  (sha3-512 str)                    -> SHA3-512 hex digest
  (blake2b str)                     -> BLAKE2b hex digest
  (blake2s str)                     -> BLAKE2s hex digest
  (hash-file path algo)             -> hash a file (algo: 'md5 'sha256 etc.)

HMAC:
  (hmac key msg)                    -> HMAC-SHA256 hex digest
  (hmac key msg algo)               -> HMAC with custom algo

Encoding:
  (base64-encode str)               -> base64 encode
  (base64-decode str)               -> base64 decode
  (hex-encode bytes)                -> hex encode bytes
  (hex-decode str)                  -> hex decode to bytes

Random:
  (random-bytes n)                  -> n random bytes as bytevector
  (random-int n)                    -> random integer in [0, n-1]
  (random-string n)                 -> random alphanumeric string
  (uuid)                            -> generate UUID v4 string

Password:
  (password-hash password)          -> bcrypt-style hash (SHA256 + salt)
  (password-verify password hash)   -> verify against hash

Constants:
  (hash-algorithms)                 -> list of available hash algos
"""
import hashlib
import hmac as _hmac
import base64
import secrets
import uuid as _uuid
import struct
from typing import List, Optional, Union

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _unwrap_str(val) -> str:
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_bytes(val) -> bytes:
    if isinstance(val, Bytevector):
        return bytes(val.value)
    if isinstance(val, Str):
        return val.get_str().encode("utf-8")
    if isinstance(val, Sym):
        return val.name.encode("utf-8")
    raise Exception(f"Expected bytes/string, got {type(val).__name__}")


_ALGO_MAP = {
    'md5': 'md5',
    'sha1': 'sha1',
    'sha256': 'sha256',
    'sha512': 'sha512',
    'sha224': 'sha224',
    'sha384': 'sha384',
    'sha3-256': 'sha3_256',
    'sha3-512': 'sha3_512',
    'blake2b': 'blake2b',
    'blake2s': 'blake2s',
    'sm3': 'sm3',
}


def _get_digest(name: str, data: bytes) -> str:
    algo = _ALGO_MAP.get(name, name)
    try:
        h = hashlib.new(algo, data)
        return h.hexdigest()
    except ValueError:
        raise Exception(f"Unknown hash algorithm: {name}")


# ==================== Hash ====================


def fn_md5(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("md5: need 1 argument")
    return Str(hashlib.md5(_unwrap_bytes(args[0])).hexdigest())


def fn_sha1(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("sha1: need 1 argument")
    return Str(hashlib.sha1(_unwrap_bytes(args[0])).hexdigest())


def fn_sha256(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("sha256: need 1 argument")
    return Str(hashlib.sha256(_unwrap_bytes(args[0])).hexdigest())


def fn_sha512(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("sha512: need 1 argument")
    return Str(hashlib.sha512(_unwrap_bytes(args[0])).hexdigest())


def sha3_256_fn(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("sha3-256: need 1 argument")
    return Str(hashlib.sha3_256(_unwrap_bytes(args[0])).hexdigest())


def sha3_512_fn(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("sha3-512: need 1 argument")
    return Str(hashlib.sha3_512(_unwrap_bytes(args[0])).hexdigest())


def blake2b_fn(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("blake2b: need 1 argument")
    return Str(hashlib.blake2b(_unwrap_bytes(args[0])).hexdigest())


def blake2s_fn(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("blake2s: need 1 argument")
    return Str(hashlib.blake2s(_unwrap_bytes(args[0])).hexdigest())


def hash_file(args: List) -> SchemeValue:
    """(hash-file path algo) -> hex digest of file"""
    if len(args) < 2:
        raise Exception("hash-file: need 2 arguments (path algo)")
    path = _unwrap_str(args[0])
    algo = _unwrap_str(args[1])
    algo_name = _ALGO_MAP.get(algo, algo)
    h = hashlib.new(algo_name)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return Str(h.hexdigest())


# ==================== HMAC ====================


def fn_hmac(args: List) -> SchemeValue:
    """(hmac key msg) or (hmac key msg algo)"""
    if len(args) < 2:
        raise Exception("hmac: need at least 2 arguments (key msg)")
    key = _unwrap_bytes(args[0])
    msg = _unwrap_bytes(args[1])
    algo = 'sha256'
    if len(args) > 2:
        algo = _ALGO_MAP.get(_unwrap_str(args[2]), _unwrap_str(args[2]))
    h = _hmac.new(key, msg, algo)
    return Str(h.hexdigest())


# ==================== Encoding ====================


def base64_encode(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("base64-encode: need 1 argument")
    data = _unwrap_bytes(args[0])
    return Str(base64.b64encode(data).decode('ascii'))


def base64_decode(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("base64-decode: need 1 argument")
    s = _unwrap_str(args[0])
    return Str(base64.b64decode(s).decode('utf-8', errors='replace'))


def hex_encode(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("hex-encode: need 1 argument")
    data = _unwrap_bytes(args[0])
    return Str(data.hex())


def hex_decode(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("hex-decode: need 1 argument")
    s = _unwrap_str(args[0])
    return Bytevector(bytearray(bytes.fromhex(s)))


# ==================== Random ====================


def random_bytes(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("random-bytes: need 1 argument (n)")
    n = int(unwrap_python_value(args[0]))
    return Bytevector(bytearray(secrets.token_bytes(n)))


def random_int(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("random-int: need 1 argument (n)")
    n = int(unwrap_python_value(args[0]))
    return Num(secrets.randbelow(n))


def random_string(args: List) -> SchemeValue:
    if len(args) < 1: raise Exception("random-string: need 1 argument (n)")
    n = int(unwrap_python_value(args[0]))
    import string as _str_mod
    chars = _str_mod.ascii_letters + _str_mod.digits
    result = ''.join(secrets.choice(chars) for _ in range(n))
    return Str(result)


def fn_uuid(args: List) -> SchemeValue:
    return Str(str(_uuid.uuid4()))


# ==================== Password ====================


def password_hash(args: List) -> SchemeValue:
    """Simple password hashing: SHA256(password + salt) with random salt"""
    if len(args) < 1: raise Exception("password-hash: need 1 argument")
    password = _unwrap_str(args[0])
    salt = secrets.token_hex(16)
    h = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return Str(f"{salt}${h}")


def password_verify(args: List) -> SchemeValue:
    """Verify password against hash from password-hash"""
    if len(args) < 2: raise Exception("password-verify: need 2 arguments (password hash)")
    password = _unwrap_str(args[0])
    stored = _unwrap_str(args[1])
    salt, h = stored.split('$', 1)
    verify = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return Bool(verify == h)


# ==================== Constants ====================


def hash_algorithms(args: List) -> SchemeValue:
    result = Nil()
    for name in reversed(sorted(_ALGO_MAP.keys())):
        result = Cons(Sym(name), result)
    return result


# ==================== Registration ====================


def register_crypto_primitives(env):
    env.define("md5", Prim("md5", fn_md5))
    env.define("sha1", Prim("sha1", fn_sha1))
    env.define("sha256", Prim("sha256", fn_sha256))
    env.define("sha512", Prim("sha512", fn_sha512))
    env.define("sha3-256", Prim("sha3-256", sha3_256_fn))
    env.define("sha3-512", Prim("sha3-512", sha3_512_fn))
    env.define("blake2b", Prim("blake2b", blake2b_fn))
    env.define("blake2s", Prim("blake2s", blake2s_fn))
    env.define("hash-file", Prim("hash-file", hash_file))

    env.define("hmac", Prim("hmac", fn_hmac))

    env.define("base64-encode", Prim("base64-encode", base64_encode))
    env.define("base64-decode", Prim("base64-decode", base64_decode))
    env.define("hex-encode", Prim("hex-encode", hex_encode))
    env.define("hex-decode", Prim("hex-decode", hex_decode))

    env.define("random-bytes", Prim("random-bytes", random_bytes))
    env.define("random-int", Prim("random-int", random_int))
    env.define("random-string", Prim("random-string", random_string))
    env.define("uuid", Prim("uuid", fn_uuid))

    env.define("password-hash", Prim("password-hash", password_hash))
    env.define("password-verify", Prim("password-verify", password_verify))

    env.define("hash-algorithms", Prim("hash-algorithms", hash_algorithms))