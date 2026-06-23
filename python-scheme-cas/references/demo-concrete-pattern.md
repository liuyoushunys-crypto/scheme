# demo.md Concrete Example Pattern (2026-06-26)

## Rule: 用实参演示，不用形参

Every demo.md must use concrete values, not abstract parameter names.

### ❌ BAD (old style — parameter tables + abstract code)

```markdown
| 参数 | 类型 | 说明 |
|------|------|------|
| `a` | 数组 | 输入数组 |
| `:axis` | int/None | 操作轴 |
```

```scheme
(np.sum a)
(np.sum a :axis 0)
```

### ✅ GOOD (new style — concrete values)

```scheme
(np.sum (np.array '(1 2 3 4 5)))                           ; → 15
(np.sum (np.array '((1 2) (3 4))) :axis 0)                 ; → [4 6]
(np.sum (np.array '((1 2) (3 4))) :axis 1)                 ; → [3 7]
```

The reader sees real inputs and real outputs directly — no mental substitution needed.

## Output Format

Code on its own line, result indented on the next line with `→`:

```scheme
(np.reshape (np.arange 0 6) '(2 3))
  →  [[0 1 2]
      [3 4 5]]
```

NOT inline: `(np.xxx a)  →  [1 2 3]`

## Scheme Code Comments

Every line of Scheme code needs a `;` comment:

```scheme
(np.random.seed 42)                          ; 固定随机种子，确保可复现
(define t (np.arange 0 1 T))                 ; 创建时间序列
(np.fft signal)                              ; 做 FFT 变换到频域
```

## Python Code Comments (core.py)

Every core.py needs:
1. Module docstring with description
2. `# 注册 xxx 原语` before register function
3. Function docstring
4. `# 从 NumPy 获取 xxx 函数` before getattr
5. `# 注册到 Scheme 环境，包装为 Prim 原语` before env.define

```python
# 注册 np.fft 原语
def register_fft(env):
    """注册 np.fft 到 Scheme 环境。"""
    fn = getattr(_np, "fft", None)           # 从 NumPy 获取 fft 函数
    if fn is None:
        return
    env.define(Sym("np.fft"), Prim("np.fft", # 注册为 Prim 原语
        lambda args: wrap_python_value(fn(*[unwrap_python_value(a) for a in args]))))
```

## Per-Primitive Import Independence (Critical Pitfall)

Each subdirectory's `core.py` MUST import its own symbols. NEVER rely on the aggregator's imports leaking into scope.

### ❌ BAD
```python
# subdir/core.py
def register_sin(env):
    fn = getattr(_np, "sin", None)
    env.define(Sym("np.sin"), Prim("np.sin", lambda args: ...))  # Sym, Prim not imported!
```

### ✅ GOOD
```python
"""subdir/core.py — description"""
from core.schemevalue import Sym, Prim, PythonObject  # MUST import own symbols
from eval.eval_python_import import wrap_python_value, unwrap_python_value

def register_sin(env):
    fn = getattr(_np, "sin", None)
    env.define(Sym("np.sin"), Prim("np.sin", lambda args: ...))
```

## Demo Content Checklist

Every demo.md must include:
- [ ] Concrete code examples with `→` output annotations
- [ ] `;` comments on every Scheme code line
- [ ] `## 参数` section with parameter table (| 参数 | 默认 | 说明 |)
- [ ] 2-3 code examples covering different parameter scenarios
- [ ] `## 注意` section (edge cases, traps, type constraints)
- [ ] Minimum 20 lines for primitives, 15 for category demos

Optional but recommended:
- [ ] `## 何时用` section (when to use this function/model)
- [ ] `## 对比` section (comparison with similar methods)
- [ ] Real-world application flow (for core functions)

## Per-Type Template Reference

### 数学函数 (numpy math, fft, linalg)
```
# numpy/{sub}/{dir} — np.{name}

1-2 sentence Chinese description.

## 参数
| 参数 | 默认 | 说明 |
|------|------|------|

```scheme
; 注释
(np.{name} (np.array '(1 2 3)))
  →  预期结果

; 不同参数
(np.{name} (np.array '(1 2 3)) :axis 0)
  →  预期结果
```

## 注意
- trap 1
- trap 2
```\```

### 模型类 (learn/models/{subcat}/{dir})
```
# models/{subcat} — {ModelName}

1-2 sentence Chinese description.

## 参数
| 参数 | 默认 | 说明 |
|------|------|------|
| `:param1` | default | description |

```scheme
; 创建模型（具体参数值！）
(define model ({ModelName} :param1 concrete-val1 :param2 concrete-val2))
(model-fit model X y)
(model-predict model X-new)
(py-get model 'attribute-)
```

## 注意
- caution 1
- caution 2
```\```

### CV 分割器 (model_selection/)
```
# model_selection/{name} — {ClassName}

1-2 sentence.

## 何时用
- scenario 1
- scenario 2

## 参数
| 参数 | 默认 | 说明 |
|------|------|------|

```scheme
(define cv ({ClassName} :n-splits 5 :shuffle #t :random-state 42))
(cross-val-score model X y :cv cv)
```

## 注意
- trap 1
```\```

### 子类聚合 demo (models/{subcat}/demo.md)
```
# models/{subcat} — {Subcategory Name}

Overview table + selection guide.

| 模型 | 任务 | 特点 |
|-----|------|------|
| ... | ... | ... |

## 注意
- general notes
```\```

### Statsmodels 模型类 (statsmodels/{name}/)

注意与 sklearn 的区别：
- 构造器参数顺序不同: `sm.OLS(y, X)`（y 在前）
- `.fit()` 无参数（sklearn 的 `model.fit(X, y)` 不接受）
- 结果通过 `py-get` / `py-call` 访问

```scheme
;; 构造（具体参数值）
(define X (sm.add-constant (np.array '((1 2) (2 3) (3 4)))))
(define y (np.array '(2 3 4)))
(define model (sm.OLS y X))
(define results (model.fit model))
(py-get results 'params)        ; 系数
(py-get results 'rsquared)      ; R²
(py-get results 'pvalues)       ; p 值
(py-call results 'summary)      ; 完整回归表
(py-call results 'predict :exog X-new)  ; 预测
```\```
