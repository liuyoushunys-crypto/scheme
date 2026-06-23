# Ecosystem Display — `(ecosystem)`

Command to browse all available PyPI math packages from the Scheme REPL.

## Usage

```scheme
(ecosystem)               → categorized table of all 19 packages
(ecosystem 'numpy)        → details + usage examples for numpy
(ecosystem "绘图")        → search by keyword
```

## Package list

Categories: 数值计算 (numpy/scipy/mpmath/numba) | 符号计算 (sympy/symengine/galois) | 数据科学 (pandas/statsmodels/sklearn) | 优化 (cvxpy/pulp/ortools) | 图论 (networkx) | 绘图 (matplotlib/Pillow/opencv) | 物理/单位 (pint/uncertainties)

## Files

- `eval/eval_py_ecosystem.py` — implementation (19-package database)
