# Module Registry — Python-Library-to-Scheme Integration Pattern

## Directory Structure (as of 2026-06-22)

```
eval/
├── eval_scheme.py           ← Core evaluator (496 lines)
├── eval_python_import.py    ← Python import bridge + 5 bridge prims
├── eval_bracket.py          ← [obj key ...] slice/index (~130 lines)
├── eval_try.py              ← (try body handler) (~15 lines)
├── eval_let.py / cond / case / guard / quasiquote / ... ← extracted special forms
│
├── cas/                     ← CAS subsystem (17 files)
│   ├── engine.py            ← symengine/sympy switching
│   ├── entry.py             ← (use-cas) entry
│   ├── core.py              ← 60+ CAS prims (diff/integrate/factor/solve/...)
│   ├── parse.py             ← 5 format parsers
│   ├── tensor.py            ← tensor algebra
│   ├── pattern.py           ← pattern matching (match/defrule/rewrite)
│   ├── assume.py            ← assumption system
│   ├── numerical.py         ← numerical methods
│   ├── numpy.py             ← numpy shortcut
│   ├── learn.py             ← sklearn wrapper
│   ├── bridge.py            ← graph/units/tensor bridge
│   ├── viz.py               ← 17 chart types
│   ├── help.py              ← help system
│   ├── nav.py               ← navigation
│   ├── catalog.py           ← package catalog
│   ├── sugar.py             ← syntax sugar macros
│   └── ecosystem.py         ← package ecosystem display
│
├── data/                    ← Data processing (3 files)
│   ├── json.py              ← JSON first-class (18 prims)
│   ├── csv.py               ← CSV (7 prims)
│   └── serialize.py         ← Pickle/JSON/pprint (8 prims)
│
├── text/                    ← Text processing (1 file)
│   └── re.py                ← Regex (20 prims)
│
├── io/                      ← I/O (5 files)
│   ├── path.py              ← pathlib path ops (30+ prims)
│   ├── http.py              ← HTTP client (26 prims)
│   ├── image.py             ← Pillow image (40 prims)
│   ├── compress.py          ← gzip/bz2/lzma/zip/tar (16 prims)
│   └── db.py                ← SQLite3 (22 prims)
│
├── crypto/                  ← Cryptography (1 file)
│   └── crypto.py            ← Hash/hmac/base64/uuid (22 prims)
│
└── system/                  ← System (2 files)
    ├── system.py            ← OS/process/env/memory (30+ prims)
    └── datetime.py          ← Date/time (28 prims)
```

## Adding a New Python-Library Module

### Step 1: Create the module

`eval/<category>/<name>.py`

```python
"""
Short description - Based on Python <library> module.

Functions:
  (func-name arg...)           -> description
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value

def _unwrap_str(val) -> str:
    if isinstance(val, Str): return val.get_str()
    if isinstance(val, Sym): return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")

def my_func(args: List[SchemeValue]) -> SchemeValue:
    """(my-func arg) -> description"""
    if len(args) < 1:
        raise Exception("my-func: need 1 argument")
    # unwrap Scheme -> Python
    py_val = unwrap_python_value(args[0])
    # do work with Python library
    result = some_python_lib.some_func(py_val)
    # wrap Python -> Scheme
    return wrap_python_value(result)

def register_xxx_primitives(env):
    env.define("my-func", Prim("my-func", my_func))
```

### Step 2: Register in `primitives/primitives.py`

```python
# Add import
from eval.<category>.<name> import register_xxx_primitives

# Add call in register_all()
register_xxx_primitives(env)
```

### Step 3: Handle Bytevector correctly

`Bytevector` uses `.data` (bytearray), NOT `.value`:

```python
def _unwrap_bytes(val) -> bytes:
    if isinstance(val, Bytevector):
        return bytes(val.data)
```

## Pitfalls

1. **HashTable keys** are plain Python `str`, not `Str` objects. Use `ht.table["key"] = val`, never `Str` as dict key.
2. **Json keys** in hash tables are plain strings. When converting JSON to scheme, `json_to_scheme` stores `ht.table[k] = wrap_python_value(v)`.
3. **Integer vs Num** — Scheme values come as `Integer` for exact ints, `Num` for floats. Always check `isinstance(val, (Integer, Num))` or just `unwrap_python_value()`.
4. **Bytevector** — Field is `.data` (bytearray), not `.value`.
5. **Custom types** need `__str__` for display. Also add a `case <Type>():` branch in `scheme_format` in `core/schemevalue.py` (or rely on fallback: `str(val)` at the `case _:` branch).
6. **Bracket extraction** — The `bracket` handler was moved to `eval/eval_bracket.py` in 2026-06-22 refactoring. Do NOT add bracket logic back into `eval_scheme.py`.
7. **Lazy import pattern** — Use try/except ImportError inside function, not at module level, for optional dependencies:
   ```python
   def my_func(args):
       try:
           import some_lib
       except ImportError:
           raise Exception("Install: pip install some-lib")
   ```
