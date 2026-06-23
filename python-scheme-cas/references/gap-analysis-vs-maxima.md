# CAS 差距分析 vs Maxima

本会话对标 Maxima 完成的功能强化。

## 新增功能汇总

| 领域 | 新增命令 | 实现文件 |
|------|---------|---------|
| 假设系统 | `assume/unassume/refine/assuming/ask` | `eval/eval_py_assume.py` |
| 方程工具 | `lhs/rhs/num/denom/isolate` | `eval/eval_py_cas.py` |
| 表达式部件 | `part/pickapart` | `eval/eval_py_cas.py` |
| 数值方法 | `find-root/numerical-integrate/numerical-derivative` | `eval/eval_py_numerical.py` |
| 矩阵分解 | `lu-decomp/qr-decomp/svd/norm/rank/nullspace/col/row` | `eval/eval_py_cas.py` |
| 输出格式 | `ratsimp/ccode/fcode/mathml` | `eval/eval_py_cas.py` |
| 数论扩展 | `chinese/jacobi-symbol/power-mod` | `eval/eval_py_cas.py` |
| REPL | `%` 上一步结果 | `main.py` |
| 图论桥接 | `use-graph` → Graph/DiGraph/shortest-path/pagerank | `eval/eval_py_bridge.py` |
| 物理单位 | `use-units` → meter/second/c/G/kilo/convert-to | `eval/eval_py_bridge.py` |
| 张量桥接 | `use-tensor` → Array/tensor-product/tensor-contraction | `eval/eval_py_bridge.py` |

## 关键修复

| 问题 | 修复 | 文件 |
|------|------|------|
| `math.sin(symengine.Symbol)` 抛 RuntimeError | 所有 `except (TypeError, ValueError)` 加 `RuntimeError` | `eval/eval_py_arithmetic.py` |
| sympy-only 函数走 engine 管理器 | 直接 `import sympy` 而非 `_sympy()` | `cas_refine`, `cas_isolate` 等 |
| 单位注册因个别名称不存在而整体失败 | `_safe_bind` 跳过不存在的对象 | `eval/eval_py_bridge.py` |
