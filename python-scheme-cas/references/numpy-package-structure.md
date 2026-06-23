# NumPy 包结构 (301 注册原语 + 7 增强工具)

## 顶层结构

```
eval/cas/numpy/
├── __init__.py         包初始化 — 聚合 8 子模块 register
├── core.py             (use-numpy) 入口 + 7 增强工具
├── create/             数组创建 (35)
├── manipulate/         数组操作 (42)
├── math/               数学/统计/逻辑/位运算 (132)
├── linalg/             线性代数 (18)
├── transform/          FFT/窗/排序/集合/多项式 (46)
├── random/             随机抽样 (22)
└── io/                 文件 IO (6)
```

## 7 增强工具 (core.py)

| 函数 | 用途 |
|------|------|
| `np-size` | 元素总数 |
| `np-shape` | 形状列表 |
| `np-ndim` | 维度数 |
| `np-dtype` | 元素类型名 |
| `np-astype` | 类型转换 |
| `np-slice` | 切片 |
| `np-index` | 多维索引 |

## 35 数组创建 (create/)

`array`, `zeros`, `ones`, `empty`, `full`,
`zeros-like`, `ones-like`, `empty-like`, `full-like`,
`eye`, `identity`,
`diag`, `diagflat`, `diag-indices`,
`arange`, `linspace`, `logspace`, `geomspace`,
`meshgrid`, `indices`,
`asarray`, `asanyarray`, `ascontiguousarray`,
`bmat`, `matrix`,
`tri`, `tril`, `triu`,
`vander`, `fromstring`, `fromfunction`, `frombuffer`, `fromiter`,
`require`, `copy`

## 42 数组操作 (manipulate/)

`reshape`, `transpose`, `flatten`, `ravel`,
`moveaxis`, `swapaxes`,
`atleast-1d`, `atleast-2d`, `atleast-3d`,
`squeeze`, `expand-dims`, `broadcast-to`,
`fliplr`, `flipud`, `flip`, `rot90`,
`concatenate`, `stack`, `hstack`, `vstack`, `dstack`, `column-stack`,
`append`, `insert`, `delete`,
`split`, `hsplit`, `vsplit`, `array-split`,
`take`, `choose`, `compress`,
`tile`, `repeat`,
`pad`,
`copyto`, `put`,
`apply-along-axis`, `vectorize`,
`unwraps`, `trim-zeros`,
`ndenumerate`

## 132 数学 (math/)

**聚合**: sum, mean, std, var, min, max, ptp, prod,
cumsum, cumprod,
nansum, nanmean, nanstd, nanvar, nanmin, nanmax, nanprod, nancumsum, nancumprod,
trace, all, any, average

**逐元素**: abs, sqrt, square, sign, floor, ceil, trunc, rint, round, fix, clip,
where, negative, positive, reciprocal

**三角**: sin, cos, tan, arcsin, arccos, arctan,
sinh, cosh, tanh, arcsinh, arccosh, arctanh,
arctan2, hypot,
degrees, radians, deg2rad, rad2deg

**指数/对数**: exp, exp2, expm1, log, log10, log2,
log1p, logaddexp, logaddexp2, power, cbrt

**向量**: dot, cross, outer, inner, kron, tensordot,
vdot, matmul, einsum, convolve

**梯度**: gradient, trapz, diff

**统计**: median, percentile, quantile,
corrcoef, cov, histogram, bincount, digitize, correlate

**逻辑/比较**: allclose, isclose, isfinite, isinf, isnan,
iscomplex, isreal,
logical-and, logical-or, logical-not, logical-xor,
greater, less, equal, greater-equal, less-equal, not-equal, array-equal,
heaviside, sinc, i0

**浮点**: ldexp, frexp, modf, spacing, nextafter,
copysign, signbit, fabs, fmax, fmin

**复数**: angle, real, imag, conj

**位运算**: bitwise-and, bitwise-or, bitwise-xor, bitwise-not,
invert, left-shift, right-shift

**特殊**: interp

## 18 线性代数 (linalg/)

inv, det, slogdet,
matrix-power, matrix-rank,
norm, cond, solve, lstsq,
eig, eigvals, eigh,
svd, qr, cholesky,
pinv, multi-dot, tensorinv

## 46 变换 (transform/)

**FFT**: fft, ifft, fft2, ifft2, fftn, ifftn,
fftshift, ifftshift, rfft, irfft

**窗**: bartlett, blackman, hamming, hanning, kaiser

**排序**: sort, argsort, searchsorted, partition,
lexsort, msort, sort-complex,
nonzero, argwhere, count-nonzero, extract, nan-to-num

**集合**: unique, intersect1d, union1d, setdiff1d, setxor1d, in1d, isin

**多项式**: polyfit, polyval, polyder, polyint,
polyroots, roots,
polyadd, polysub, polymul, polydiv

**特殊**: sinc, i0

## 22 随机 (random/)

seed, rand, randn, randint,
uniform, normal,
beta, gamma, exponential, chisquare, f, t,
poisson, binomial,
lognormal, weibull, laplace, logistic, pareto,
shuffle, permutation, choice

## 6 IO (io/)

save, load, savetxt, loadtxt, savez, genfromtxt

## 系统信息 (distutils/)

`np.system-info` — NumPy 构建配置检测器。支持：

- `(np.system-info 'version)` → NumPy 版本
- `(np.system-info 'include)` → include 路径
- `(np.system-info 'blas)` → BLAS 库信息 (scipy-openblas/OpenBLAS/MKL/ATLAS)
- `(np.system-info 'lapack)` → LAPACK 库信息
- `(np.system-info)` → 全部系统信息 (BLAS/LAPACK/编译器/SIMD 扩展/CPU 架构)

## 注册模式

各子模块独立导出 `register_numpy_xxx_primitives(env)`，
`__init__.py` 中的 `register_numpy_primitives(env)` 依次调用所有子模块注册函数。
`primitives.py` 只需要 `from eval.cas.numpy import register_numpy_primitives`。

## 自动扫描注册修复

当发现函数定义 (`def pnp_xxx`) 但没有在注册列表中出现时，用脚本自动修复：
```python
# 找到 register 函数的结尾 `]`，在之前插入缺失的 `("np.xxx", pnp_xxx),`
# 用 pnp_to_np_name(fn_name) 映射函数名到注册名
```
