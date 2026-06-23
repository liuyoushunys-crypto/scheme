# Scikit-learn Enhancement — `(use-learn)`

One-step import of sklearn models, datasets, metrics, preprocessing, and train-test-split.

## Usage

```scheme
(use-learn)            ; → 20+ models, 10+ metrics, datasets, preprocessing
(use-learn 'full)      ; → import ALL sklearn submodule classes
```

## Models auto-bound

Linear: `LinearRegression`, `Ridge`, `Lasso`, `LogisticRegression`, `SGDRegressor`
SVM: `SVC`, `SVR`, `NuSVC`, `LinearSVC`
Ensemble: `RandomForestClassifier/Regressor`, `GradientBoostingClassifier/Regressor`
Clustering: `KMeans`, `DBSCAN`, `AgglomerativeClustering`
Decomposition: `PCA`
Neighbors: `KNeighborsClassifier/Regressor`
Trees: `DecisionTreeClassifier/Regressor`
Neural: `MLPClassifier/Regressor`

All models support keyword arguments: `(LogisticRegression :max_iter 2000)`

## Datasets

```scheme
(load-digits) (load-iris) (load-diabetes) (load-wine) (load-breast-cancer)
```

## Workflow

```scheme
;; 1. Load
(define digits (load-digits))
(define X (. digits 'data))     ; attribute access via '.'
(define y (. digits 'target))

;; 2. Split — returns PythonObject tuple
(define split (train-test-split X y :test_size 0.2))
(define X_train (py-get split 0))
(define X_test (py-get split 1))
(define y_train (py-get split 2))
(define y_test (py-get split 3))

;; 3. Train
(define model (LogisticRegression :max_iter 2000))
(. model 'fit X_train y_train)   ; 'fit or fit — both work

;; 4. Predict
(define y_pred (. model 'predict X_test))

;; 5. Evaluate
(accuracy-score y_test y_pred)       → 0.975
(confusion-matrix y_test y_pred)     → numpy array
(classification-report y_test y_pred) → string report
(r2-score y_test y_pred)             → 0.945
(mean-squared-error y_test y_pred)
```

## `train-test-split` returns PythonObject

Critical pattern — the split function must return `PythonObject(result)` not `wrap_python_value(list(result))`. The latter converts to a Scheme Cons list which `py-get` can't index:

```python
# Correct — keeps tuple as PythonObject
result = _split(*pos, **kwargs)
return PythonObject(result)
```

## `.` method syntax

Both `(. model 'fit X y)` and `(. model fit X y)` work. The fix handles quoted symbols by unwrapping `Cons(Sym("quote"), Cons(Sym("method"), Nil()))`.

## Bug fix: `from ... import ...`

`eval_from_form` in `eval/eval_python_import.py` used `list(cdr)` on a Cons, but `Cons` doesn't implement `__iter__`. Fix: use `from_lisp_list(cdr)` instead.

```python
# Broken
if not isinstance(cdr, Cons) or len(list(cdr)) < 2:

# Fixed  
from core.schemevalue import from_lisp_list
args = from_lisp_list(cdr)
if len(args) < 2:
```

## Files

- `eval/eval_py_learn.py` — implementation
