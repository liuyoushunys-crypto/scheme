# Library Wrapper Auto-Generation Pattern

When wrapping a large Python library (OpenCV, SciPy, Statsmodels) as CAS primitives, **write a generator script** rather than hand-authoring each primitive directory.

Modules built with this pattern: vision (58 primitives), scipy (77 primitives), statsmodels (24 primitives).

## When to auto-generate

- Library has 30+ functions to wrap
- Each function follows a consistent registration pattern
- You want uniform demo.md structure with minimal per-function effort

## Pattern Steps

### 1. Define primitives as data tuples

```python
prims = []

def P(name, func, doc, params, examples, notes):
    prims.append((name, func, doc, params, examples, notes))

P('imread', 'imread',
  '读取图像文件。',
  [('filename', '必选', '文件路径'), (':flags', '1', '读取模式')],
  ["(define img (cv.imread \"/path/to/photo.jpg\"))"],
  ["flags: IMREAD_COLOR(1)/GRAYSCALE(0)/UNCHANGED(-1)"])
```

### 2. Three access patterns for core.py

**Pattern A — Direct module attribute** (numpy/vision/sm-stats):
```python
fn = getattr(_scipy, "linalg", None)
fn = getattr(fn, "inv", None)
```

**Pattern B — Class constructor** (statsmodels OLS/Logit):
```python
fn = getattr(_sm, "OLS", None)
env.define(Sym("sm.OLS"), Prim("sm.OLS", lambda args: ...))
```

**Pattern C — Submodule function** (statsmodels tsa/sm.stats):
```python
# For sm.tsa.adfuller:
fn = getattr(_sm.tsa, "adfuller", None)
# For sm.stats.anova_lm:
fn = getattr(_sm.stats, "anova_lm", None)
```

Choose the right pattern based on Python module structure.

### 3. Generate directory structure

For each primitive, create:
- `{cat}/{name}/core.py` — registration function
- `{cat}/{name}/__init__.py` — empty
- `{cat}/{name}/demo.md` — documentation

### 4. Handle model classes (statsmodels pattern)

Statsmodels models differ from sklearn:
- Constructor order: `sm.OLS(y, X)` not `Model(X, y)` — y first!
- `.fit()` takes no arguments (vs sklearn `model.fit(X, y)`)
- Results accessed via `py-get` / `py-call`

**Demo example for model workflow:**
```scheme
(define X (sm.add-constant (np.array '((1 2) (2 3) (3 4)))))
(define y (np.array '(2 3 4)))
(define model (sm.OLS y X))
(define results (model.fit model))           ; .fit() no args
(py-call results 'summary)                   ; OLS regression table
(py-get results 'params)                     ; coefficients
(py-get results 'rsquared)                   ; R-squared
(py-call results 'predict :exog X-new)       ; prediction
```

### 5. Post-generation enrichment

After auto-gen, replace generic parameter tables with per-function specific ones:

```python
param_tables = {
    'OLS': '| `endog` | 必选 | 因变量 y |\n| `exog` | 必选 | 自变量 X |',
    'adfuller': '| `x` | 必选 | 时序 |\n| `:maxlag` | `None` | 滞后阶 |\n| `:autolag` | `\"AIC\"` | 准则 |',
}
```

### 6. Verification

```bash
cd /workspace/99
# Top-level
python3 -c "from eval.cas.scipy.core import register_scipy_primitives; print('OK')"
# Subpackage
python3 -c "from eval.cas.scipy.linalg.core import register_linalg; print('OK')"
# Single primitive
python3 -c "from eval.cas.scipy.linalg.inv.core import register; print('OK')"
```
