# 测试框架

21 个测试文件，全量回归命令：
```bash
cd /workspace/99 && for f in tests/*.scm; do python3 main.py "$f"; done
```

## 测试文件结构

| 文件 | 覆盖范围 |
|------|---------|
| as_alias.scm | import xxx as yyy |
| cas_demo.scm | CAS 基础功能 |
| cas_enriched.scm | CAS 增强功能 (60+ 函数) |
| cas_sugar.scm | defsym, with-symbols, describe |
| comprehensive.scm | sympy/scipy/numpy 综合 |
| deep_numpy.scm | numpy 全功能深度测试 |
| deep_scipy.scm | scipy 7 子模块深度测试 |
| deep_medium.scm | mpmath+uncertainties+pint+galois+symengine |
| deep_ds_opt.scm | pandas+sklearn+cvxpy+pulp |
| deep_report.scm | 基础设施缺失报告 |
| numpy_demo.scm | numpy 示例 |
| numpy_kwargs.scm | 关键词参数 |
| opencv_test.scm | OpenCV 12 项测试 |
| package_registry.scm | 17 包注册表 |
| pypi_ecosystem.scm | 生态集成验证 |
| python_cascade.scm | 级联调用 |
| python_interop.scm | 基础互操作 |
| r1_types.scm / r1b_fixes.scm | 类型转换边缘 (#1) |
| r2_numpy_scipy.scm | numpy/scipy 深层边缘 (#2) |
| r3_r4_r5.scm | sympy/pandas/networkx 边缘 (#3-5) |
| scipy_stats.scm | scipy 统计测试 |
| sympy_full.scm | sympy 11 模块全覆盖 |
| sympy_pretty.scm | 漂亮打印 |
| sympy_seamless.scm | 无缝集成 |
| vector_interop.scm | Vector 数据互操作 |

## 发现的 Bug 与修复

### 已修复

1. **py-eval 变量隔离**: `(py-eval "arr[2:8:2]")` → `(py-eval "expr" :var val)` ✅
2. **py-slice 缺失**: 添加 `(py-slice start stop step)` → Python slice ✅
3. **py-dict 缺失**: 添加 `(py-dict :k1 v1 :k2 v2)` → Python dict ✅
4. **多维索引**: `(py-get obj (list slice1 slice2))` ✅
5. **`.method` 点对语法**: `(obj).method` 被误读 → 添加 `(. obj method args...)` ✅
6. **多参数 lambda 内省**: scipy.curve_fit 失败 → `__code__` + `__signature__` ✅
7. **py-len**: `(len obj)` 未定义 → `(py-len obj)` ✅
8. **整数索引 py-get**: `(py-get tuple 0)` ✅
9. **PythonObject 索引 py-get**: `(py-get dict py_key)` ✅
10. **Vector → tuple 索引**: 多维 numpy 索引 ✅
11. **Cons → tuple 索引**: `(list slice1 slice2)` ✅
12. **Sym → str 自动解包**: 符号自动转为字符串 ✅

### 已知限制 (待修复)

1. 切片语法: `arr[2:8:2]` 只能用 py-eval 绕行
2. 异常桥接: Python 异常 → Scheme guard 未完全打通
3. `+=` 运算符: Python 的 `+=` 需用 `__iadd__`