# NumPy Enhancement — `(use-numpy)`

One-step numpy import with short alias `np` and convenience wrappers.

## Usage

```scheme
(use-numpy)   ; → binds np + 40+ shortcut functions
```

## What gets bound

| Pattern | Example | Notes |
|---------|---------|-------|
| `np` module alias | `(np.array ...)` | `(import numpy as np)` equivalent |
| Creation | `np.array`, `np.zeros`, `np.ones`, `np.eye` | Shape as list: `(np.zeros (list 3 3))` |
| Sequences | `(range start end step)`, `np.linspace`, `np.arange` | `(range 0 10 2)` → `[0 2 4 6 8]` |
| Math | `np.sin`, `np.cos`, `np.sqrt`, `np.exp`, `np.log` | Broadcasting works automatically |
| Aggregation | `np.sum`, `np.mean`, `np.std`, `np.var` | |
| Shape | `(np-shape a)`, `(np-size a)`, `(np-ndim a)` | Returns Scheme list |
| Index/Slice | `(np-index a i j)`, `(np-slice a start end step)` | |
| Type | `(np-dtype a)`, `(np-astype a 'float64)` | |
| Linalg | `np.dot`, `np.linalg.inv`, `np.linalg.det`, `np.linalg.eig` | |
| Random | `np.random.rand`, `np.random.randint`, `np.random.normal` | |

## Key pattern: bypassing `wrap_python_value` for dict-likes

When loading sklearn datasets, `wrap_python_value` converts dict-like `Bunch` objects to Scheme alists, destroying attribute access. Use `PythonObject(ds)` directly:

```python
def _bind_dataset(env, name, loader):
    def do_load(args):
        ds = loader()
        return PythonObject(ds)  # Force PythonObject, bypass wrap
    env.define(Sym(name), Prim(name, do_load))
```

## Arithmetic proxy with numpy

Already works automatically via `try_py_binary_op`:
```scheme
(+ a 10)       → numpy broadcast
(* a 2)        → numpy broadcast
(expt a 2)     → power
(np.sin a)     → numpy ufunc
```

## Files

- `eval/eval_py_numpy.py` — implementation
