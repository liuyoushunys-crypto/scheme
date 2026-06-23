# Vision Module Auto-Generation Pattern

When wrapping a large Python library like OpenCV (cv2) as CAS primitives, **write a generator script** rather than hand-authoring each primitive directory. This session created 58 primitives (9 categories) in under 1 minute.

## When to auto-generate

- Library has 50+ functions to wrap
- Each function follows the same registration pattern (`getattr(lib, name)` → `wrap_python_value(fn(...))`)
- You want consistent demo.md with minimal per-function effort

## Pattern Steps

### 1. Define primitives as data

```python
P = []  # list of (category, dir_name, cv_func, cn_desc, [demo_lines])

def a(cat, name, func, desc, demo):
    P.append((cat, name, func, desc, demo))

a('basic', 'imread', 'imread',
  '读取图像文件。返回 numpy 数组 (H,W,C)。',
  ["(define img (cv.imread \"/path/to/photo.jpg\"))",
   "  ->  numpy.ndarray (480, 640, 3)",
   "",
   "(define img-gray (cv.imread \"photo.jpg\" :flags cv.IMREAD_GRAYSCALE))"])
```

### 2. Generate directory structure

For each primitive:
- Create `{cat}/{dir_name}/core.py` from template
- Create `{cat}/{dir_name}/demo.md` from template (embed demo lines)
- Create `{cat}/{dir_name}/__init__.py` (empty or minimal)

**core.py template:**
```python
"""
vision/{cat}/{name} — cv.{func}
{desc}
"""
import cv2 as _cv
from eval.eval_python_import import wrap_python_value, unwrap_python_value
from core.schemevalue import Sym, Prim

def register_{name}(env):
    \"\"\"注册 cv.{func} 到 Scheme 环境。\"\"\"
    fn = getattr(_cv, "{func}", None)
    if fn is None:
        return
    env.define(Sym("cv.{func}"), Prim("cv.{func}",
        lambda args: wrap_python_value(fn(*[unwrap_python_value(a) for a in args]))))
```

### 3. Generate aggregator core.py

For each category, scan subdirectories and generate:

```python
from .prim1.core import register_prim1
from .prim2.core import register_prim2

def register_cat(env):
    register_prim1(env)
    register_prim2(env)
```

### 4. Handle category naming conflict

If `core` is both a category name and the top-level aggregator filename, rename the category to avoid the `core.py` vs `core/` package conflict:

- Top-level: `vision/core.py` (aggregator: `register_vision_primitives`)
- Category: `vision/basic/` (was `core/`, renamed to avoid conflict)

Python will prefer `core/` (dir with `__init__.py`) over `core.py` when both exist.

### 5. Parameter table enrichment (post-gen)

After auto-generation, replace generic placeholder param tables with per-function specific ones using a dict lookup:

```python
param_tables = {
    'imread': '| `filename` | 必选 | 图像文件路径 |\n| `:flags` | `1` | IMREAD_COLOR(1)/GRAYSCALE(0)/UNCHANGED(-1) |',
    'Canny': '| `image` | 必选 | 输入灰度图 |\n| `threshold1` | 必选 | 低阈值 |\n| `threshold2` | 必选 | 高阈值 (高/低≈3:1) |',
    ...
}
```

### Verification

```bash
cd /workspace/99
python3 -c "from eval.cas.vision.core import register_vision_primitives; print('OK')"
python3 -c "from eval.cas.vision.basic.imread.core import register_imread; print('OK')"
```

## Scope

Session baseline: 58 primitives across 9 categories in ~150 lines of generator code.
Scales linearly — adding 50 more functions = 50 more data tuples + 5 param table entries.
