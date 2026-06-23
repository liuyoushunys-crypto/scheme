# numpy/scikit-learn 增强

## `(use-numpy)` — 一键 numpy

`eval/eval_py_numpy.py`，注册在 `register_numpy_primitives`。

- 绑定 `np` 别名 + 40+ 函数
- `(range 0 10 2)` → np.arange 简写
- 算术代理自动生效
- 增强函数: np-shape, np-size, np-ndim, np-slice, np-astype

## `(use-learn)` — 一键 scikit-learn

`eval/eval_py_learn.py`，注册在 `register_learn_primitives`。

### Bunch 处理
`load-digits` 等返回 `PythonObject(ds)` 而非 `wrap_python_value(ds)`。

### 关键修复
- `.` 方法: `'method`/`method` 两种写法
- `train-test-split` 返回 `PythonObject(result)`，py-get 解包

### 非参模型补充
GaussianNB, MultinomialNB, KernelDensity, GaussianProcess*, IsolationForest, BaggingClassifier, VotingClassifier, StackingClassifier

### CV/调参
```
(cross-val-score model X y :cv 5)
(grid-search (SVC) (list (list 'kernel '(linear rbf))) X y :cv 3)
(feature-importances model)
(make-pipeline (StandardScaler) (SVC))
```
