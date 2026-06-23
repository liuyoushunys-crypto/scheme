# core/linear — 线性代数

```scheme
(use-cas)
(define m (matrix '((1 2) (3 4))))
```

## 基础矩阵运算

```scheme
(matrix '((1 2) (3 4)))                →  Matrix([1, 2], [3, 4])

(det m)                                →  -2

(inv m)
  → Matrix([[-2, 1], [3/2, -1/2]])

(transpose m)
  → Matrix([1, 3], [2, 4])
```

## 特征值/特征向量

```scheme
(define m2 (matrix '((3 1) (1 3))))

(eigenvals m2)                         →  {2: 1, 4: 1}
(eigenvects m2)
  → [(2, 1, [[-1], [1]]), (4, 1, [[1], [1]])]
```

## 特殊矩阵构造

```scheme
(eye 3)
  → Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

(zeros 2 3)                            →  Matrix([[0, 0, 0], [0, 0, 0]])

(ones 2 3)                             →  Matrix([[1, 1, 1], [1, 1, 1]])
```

## 矩阵分解

```scheme
(lu-decomp m)                          →  (L, U, perm)
(qr-decomp (matrix '((1 2) (3 4))))    →  (Q, R)
```