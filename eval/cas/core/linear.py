"""
core/linear — 矩阵运算

对标 Maxima 的矩阵/线性代数功能。

使用方式：
  (matrix '((1 2) (3 4)))              → sympy.Matrix
  (det M)                               → 行列式
  (inv M)                               → 逆矩阵
  (transpose M)                         → 转置
  (eigenvals M)                         → 特征值
  (eigenvects M)                        → 特征向量
  (eye n)                               → 单位矩阵
  (zeros n) / (zeros m n)              → 零矩阵
  (ones n) / (ones m n)                → 全一矩阵
  (lu-decomp M)                         → LU 分解 (L, U, perm)
  (qr-decomp M)                         → QR 分解 (Q, R)
  (svd M)                               → 奇异值
  (norm M) / (norm M p)                → 范数
  (rank M)                              → 秩
  (nullspace M)                         → 零空间基
  (col M i)                             → 第 i 列
  (row M i)                             → 第 i 行
"""

from typing import List
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


# ==================== 内部工具 ====================

def _sympy():
    """Get engine proxy (auto-fallback symengine→sympy)."""
    from eval.cas.engine import get_engine
    return get_engine()

def _unwrap(args):
    """解包所有参数。"""
    return [unwrap_python_value(a) for a in args]


def _as_matrix(val):
    """确保值为 sympy Matrix。"""
    sp = _sympy()
    return val if isinstance(val, sp.Matrix) else sp.Matrix(val)


# ==================== 矩阵运算 ====================

def cas_matrix(args: List[SchemeValue]) -> SchemeValue:
    """
    (matrix rows) — 创建矩阵。

    示例：
      (matrix '((1 2) (3 4)))  →  Matrix([[1, 2], [3, 4]])
    """
    if len(args) < 1:
        raise Exception("matrix: 需要 (matrix rows)")
    py_args = _unwrap(args)
    result = _sympy().Matrix(py_args[0])
    return wrap_python_value(result)


def cas_det(args: List[SchemeValue]) -> SchemeValue:
    """
    (det M) — 行列式。

    示例：
      (det #{ matrix([1, 2], [3, 4]) })  →  -2
    """
    if len(args) < 1:
        raise Exception("det: 需要 (det M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.det()
    return wrap_python_value(result)


def cas_inv(args: List[SchemeValue]) -> SchemeValue:
    """
    (inv M) — 逆矩阵。

    示例：
      (inv #{ matrix([1, 0], [0, 1]) })  →  Matrix([[1, 0], [0, 1]])
    """
    if len(args) < 1:
        raise Exception("inv: 需要 (inv M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.inv()
    return wrap_python_value(result)


def cas_transpose(args: List[SchemeValue]) -> SchemeValue:
    """
    (transpose M) — 转置。

    示例：
      (transpose #{ matrix([1, 2], [3, 4]) })  →  Matrix([[1, 3], [2, 4]])
    """
    if len(args) < 1:
        raise Exception("transpose: 需要 (transpose M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.T
    return wrap_python_value(result)


def cas_eigenvals(args: List[SchemeValue]) -> SchemeValue:
    """
    (eigenvals M) — 特征值。

    示例：
      (eigenvals #{ matrix([1, 0], [0, 2]) })  →  {1: 1, 2: 1}
    """
    if len(args) < 1:
        raise Exception("eigenvals: 需要 (eigenvals M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.eigenvals()
    return wrap_python_value(result)


def cas_eigenvects(args: List[SchemeValue]) -> SchemeValue:
    """
    (eigenvects M) — 特征向量。

    示例：
      (eigenvects #{ matrix([1, 0], [0, 2]) })  →  [(1, 1, [Matrix([1, 0])]), (2, 1, [Matrix([0, 1])])]
    """
    if len(args) < 1:
        raise Exception("eigenvects: 需要 (eigenvects M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.eigenvects()
    return wrap_python_value(result)

def cas_eye(args: List[SchemeValue]) -> SchemeValue:
    """
    (eye n) / (eye m n) — 创建单位矩阵。

    示例：
      (eye 3)         → Matrix([[1,0,0],[0,1,0],[0,0,1]])
      (eye 2 3)       → Matrix([[1,0,0],[0,1,0]])
    """
    if len(args) < 1:
        raise Exception("eye: 需要 (eye n) 或 (eye m n)")
    py_args = _unwrap(args)
    n = int(py_args[0])
    if len(py_args) >= 2:
        m = int(py_args[1])
        result = _sympy().eye(n, m)
    else:
        result = _sympy().eye(n)
    return wrap_python_value(result)


def cas_zeros(args: List[SchemeValue]) -> SchemeValue:
    """
    (zeros n) / (zeros m n) — 创建零矩阵。

    示例：
      (zeros 3)       → Matrix([[0,0,0],[0,0,0],[0,0,0]])
      (zeros 2 3)     → Matrix([[0,0,0],[0,0,0]])
    """
    if len(args) < 1:
        raise Exception("zeros: 需要 (zeros n) 或 (zeros m n)")
    py_args = _unwrap(args)
    r = int(py_args[0])
    c = r if len(py_args) < 2 else int(py_args[1])
    result = _sympy().zeros(r, c)
    return wrap_python_value(result)


def cas_ones(args: List[SchemeValue]) -> SchemeValue:
    """
    (ones n) / (ones m n) — 创建全一矩阵。

    示例：
      (ones 3)       → Matrix([[1,1,1],[1,1,1],[1,1,1]])
      (ones 2 3)     → Matrix([[1,1,1],[1,1,1]])
    """
    if len(args) < 1:
        raise Exception("ones: 需要 (ones n) 或 (ones m n)")
    py_args = _unwrap(args)
    r = int(py_args[0])
    c = r if len(py_args) < 2 else int(py_args[1])
    result = _sympy().ones(r, c)
    return wrap_python_value(result)


def cas_lu_decomp(args: List[SchemeValue]) -> SchemeValue:
    """
    (lu-decomp M) — LU 分解。返回 (L U perm)。

    示例：
      (lu-decomp #{ matrix([4, 3], [6, 3]) })
    """
    if len(args) < 1:
        raise Exception("lu-decomp: 需要 (lu-decomp M)")
    M = _as_matrix(_unwrap(args)[0])
    L, U, perm = M.LUdecomposition()
    return wrap_python_value([L, U, perm])


def cas_qr_decomp(args: List[SchemeValue]) -> SchemeValue:
    """
    (qr-decomp M) — QR 分解。返回 (Q R)。

    示例：
      (qr-decomp #{ matrix([1, 2], [3, 4]) })
    """
    if len(args) < 1:
        raise Exception("qr-decomp: 需要 (qr-decomp M)")
    M = _as_matrix(_unwrap(args)[0])
    Q, R = M.QRdecomposition()
    return wrap_python_value([Q, R])


def cas_svd(args: List[SchemeValue]) -> SchemeValue:
    """
    (svd M) — 奇异值（列表形式）。

    示例：
      (svd #{ matrix([1, 0], [0, 2]) })  →  [2, 1]
    """
    if len(args) < 1:
        raise Exception("svd: 需要 (svd M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.singular_values()
    return wrap_python_value(result)


def cas_norm(args: List[SchemeValue]) -> SchemeValue:
    """
    (norm M) / (norm M p) — 矩阵/向量范数。p 为可选范数阶数。

    示例：
      (norm #{ matrix([3, 4]) })  →  5
      (norm #{ matrix([3, 4]) } 2)  →  5
    """
    if len(args) < 1:
        raise Exception("norm: 需要 (norm M) 或 (norm M p)")
    py_args = _unwrap(args)
    M = _as_matrix(py_args[0])
    if len(py_args) >= 2:
        p = py_args[1]
        result = M.norm(p)
    else:
        result = M.norm()
    return wrap_python_value(result)


def cas_rank(args: List[SchemeValue]) -> SchemeValue:
    """
    (rank M) — 矩阵的秩。

    示例：
      (rank #{ matrix([1, 2], [3, 4]) })  →  2
    """
    if len(args) < 1:
        raise Exception("rank: 需要 (rank M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.rank()
    return wrap_python_value(result)


def cas_nullspace(args: List[SchemeValue]) -> SchemeValue:
    """
    (nullspace M) — 零空间的一组基向量。

    示例：
      (nullspace #{ matrix([1, 0], [0, 1]) })  →  []
    """
    if len(args) < 1:
        raise Exception("nullspace: 需要 (nullspace M)")
    M = _as_matrix(_unwrap(args)[0])
    result = M.nullspace()
    return wrap_python_value(result)


def cas_col(args: List[SchemeValue]) -> SchemeValue:
    """
    (col M i) — 取第 i 列（0-indexed）。

    示例：
      (col #{ matrix([1, 2], [3, 4]) } 0)  →  Matrix([1], [3])
    """
    if len(args) < 2:
        raise Exception("col: 需要 (col M i)")
    py_args = _unwrap(args)
    M = _as_matrix(py_args[0])
    i = int(py_args[1])
    result = M.col(i)
    return wrap_python_value(result)


def cas_row(args: List[SchemeValue]) -> SchemeValue:
    """
    (row M i) — 取第 i 行（0-indexed）。

    示例：
      (row #{ matrix([1, 2], [3, 4]) } 0)  →  Matrix([[1, 2]])
    """
    if len(args) < 2:
        raise Exception("row: 需要 (row M i)")
    py_args = _unwrap(args)
    M = _as_matrix(py_args[0])
    i = int(py_args[1])
    result = M.row(i)
    return wrap_python_value(result)


# ==================== 注册 ====================

def register_linear_primitives(env):
    """Register all CAS linear algebra primitives."""
    prims = [
        ("matrix", cas_matrix),
        ("det", cas_det),
        ("inv", cas_inv),
        ("transpose", cas_transpose),
        ("eigenvals", cas_eigenvals),
        ("eigenvects", cas_eigenvects),
        ("eye", cas_eye),
        ("zeros", cas_zeros),
        ("ones", cas_ones),
        ("lu-decomp", cas_lu_decomp),
        ("qr-decomp", cas_qr_decomp),
        ("svd", cas_svd),
        ("norm", cas_norm),
        ("rank", cas_rank),
        ("nullspace", cas_nullspace),
        ("col", cas_col),
        ("row", cas_row),
    ]
    for name, func in prims:
        env.define(name, Prim(name, func))

register_primitives = register_linear_primitives


register_primitives = register_linear_primitives