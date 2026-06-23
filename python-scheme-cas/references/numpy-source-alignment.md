# NumPy 源码目录对齐 (2026-06-22 会话)

## 原则

`eval/cas/numpy/` 的目录结构应与 `numpy` Python 包的源码目录高度匹配。
每个 numpy 子包对应一个目录：

| numpy 子包 | `eval/cas/numpy/` 目录 | 说明 |
|------------|----------------------|------|
| `numpy._core` | `create/` | 数组创建 (array/zeros/eye/arange/linspace...) |
| `numpy._core` | `manipulate/` | 数组操作 (reshape/transpose/concat/split...) |
| `numpy._core` | `math/` | 数值计算 (sum/mean/dot/sin/exp/logical...) |
| `numpy.fft` | `fft/` | 傅里叶变换 (18 原语) |
| `numpy.linalg` | `linalg/` | 线性代数 (20 原语) |
| `numpy.polynomial` | `polynomial/` | 多项式 (10 原语) |
| `numpy.random` | `random/` | 随机抽样 (22 原语) |
| `numpy.lib` | `io/` | 文件 IO (6 原语) |
| `numpy.strings` | `strings/` | 字符串操作 (26 原语) |
| `numpy.testing` | `testing/` | 测试断言 (4 原语) |
| `numpy.distutils` | `distutils/` | 构建系统信息 |
| `numpy._core` | `transform/` | 排序/搜索/集合/窗 (14 原语) |

## 全覆盖验证方法

```python
import numpy as np

# 收集所有已注册的 np.xxx 名
# 归一化 kebab → underscore
# 与 dir(np) 求差集 → 报告顶层缺失
# 对 linalg/random/fft 子模块同样操作

# 关键阈值:
# 顶层 numpy API: 50%+
# linalg: 70%+
# fft: 90%+
# random: 35%+ (基础分布已全，Generator 新 API 未覆盖)
```

## 新增子包步骤

1. 创建 `numpy/<subpkg>/` 目录
2. 编写 `core.py` + `__init__.py` (导出 register 函数)
3. 在 `numpy/__init__.py` 中添加 import + `register_*()` 调用
4. 运行全覆盖扫描确认无 omission
5. 更新此文件

## 当前统计 (2026-06-22)

总注册原语: 322 + 7 增强工具 = 329
子包数: 11 (含 core)
