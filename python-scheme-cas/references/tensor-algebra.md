# 张量代数系统

指标符号 / 爱因斯坦求和 / 缩并 / 升降指标。

## 命令

```scheme
;; 声明指标
(index i j k l)                  → 注册指标符号

;; 创建张量
(define R (tensor "R" (i j k l) ()))    ;; R_ijkl (Riemann)
(define g (tensor "g" (i j) ()))        ;; g_ij (协变度规)
(define T (tensor "T" (i j) (list k)))  ;; T^k_ij (混合)

;; 显示
(tensor-show R)                  → R_{ijkl}

;; 缩并
(contract R i k)                 → R_ijkl → R_jl (Ricci)
(contract Ric j l)               → R_jl → R (标量曲率)

;; 升/降指标
(raise-index g i)                → g_ij → g^i_j
(lower-index T k)                → T^k_ij → T_kij
```

## 内部表示

```python
class Index:
    name: str        # 指标名 (如 "i")

class TensorComponent:
    name: str        # 张量名 (如 "R")
    cov: list        # 协变指标列表 [Index, ...]
    contra: list     # 逆变指标列表 [Index, ...]
    value: Any       # 数值或 sympy 表达式（可选）
```

## 实现

所有张量操作在 `eval_scheme.py` 中注册为**特殊形式**（非 Prim），原因：指标符号 `i`, `j`, `k` 在环境中未绑定。

| 特殊形式 | 处理函数 | 说明 |
|----------|---------|------|
| `Sym("index")` | `_declare_indices(names)` | 注册指标到 `_index_registry` |
| `Sym("tensor")` | `_make_tensor(name, cov_form, contra_form)` | 创建 TensorComponent |
| `Sym("contract")` | `_do_contract(tc_val, idx1, idx2)` | 缩并两个指标 |
| `Sym("raise-index")` | `_do_raise(tc_val, idx)` | 协变→逆变 |
| `Sym("lower-index")` | `_do_lower(tc_val, idx)` | 逆变→协变 |

`tensor-show` 仍是 Prim（参数不需要特殊形式保护）。

## 文件

- `eval/eval_py_tensor.py` — `TensorComponent`, `Index`, 全部操作, `register_tensor_primitives`
- `eval/eval_scheme.py` — `case Sym("index"/"tensor"/"contract"/"raise-index"/"lower-index"):`

## 陷阱

1. **指标不要用 Prim**: 始终使用 `(contract R i j)` 形式（特殊形式保护 `i`, `j` 不被求值），不要先 `(define i (index 'i))` 再传参。

2. **Cons 不可迭代**: `_make_tensor` 中 cov/contra 参数是未求值 Cons 树，须用 `from_lisp_list()` 展平，不能用 `list()`。

3. **显示不变**: 缩并后张量名不变，需用户自行区分 `R` vs `Ric`。
