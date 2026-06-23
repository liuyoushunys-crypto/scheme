# numpy 单原语拆分模式（2026-06-22 扩展）

## 背景

继 `learn/` 拆分到 118 个单模型目录后，`numpy/` 也按同样模式拆分到 356 个单原语目录。

## 结构

```
numpy/
├── __init__.py              ← 聚合 12 子包
├── core.py                  ← (use-numpy) 入口
├── create/
│   ├── core.py              ← 聚合器 (导入 35 个单原语目录)
│   ├── array/core.py        ← 注册 np.array 一个原语
│   ├── array/__init__.py
│   ├── array/demo.md        ← 该原语的完整使用文档
│   ├── zeros/core.py        ← 注册 np.zeros
│   └── ...
├── math/                    ← 145 个单原语目录
│   ├── sin/core.py
│   ├── cos/core.py
│   ├── sum/core.py
│   └── ...
├── manipulate/              ← 46
├── linalg/                  ← 20
├── fft/                     ← 18
├── random/                  ← 22
├── transform/               ← 24
├── strings/                 ← 26
├── polynomial/              ← 10
├── io/                      ← 6
├── testing/                 ← 4
└── distutils/               ← 1
```

## 单原语 core.py 模板（含注释标准）

每个 `numpy/*/xxx/core.py` 遵循固定模板，包含 3 层注释：

```python
"""
numpy/math/sin — np.sin
正弦函数。输入为弧度。               ← 第一行：功能描述
参数: a(输入数组), out?(输出数组), where?(条件掩码)  ← 第二行：参数说明
"""
import numpy as _np
from eval.eval_python_import import wrap_python_value, unwrap_python_value
from core.schemevalue import Sym, Prim, PythonObject

# 注册 np.sin 原语                     ← 注释：注册说明
def register_sin(env):
    """注册 np.sin 到 Scheme 环境。"""  ← 函数 docstring
    # 从 NumPy 获取 sin 函数            ← 注释：代码说明
    fn = getattr(_np, "sin", None)
    if fn is None:
        return
    # 注册到 Scheme 环境，包装为 Prim 原语 ← 注释：注册说明
    env.define(Sym("np.sin"), Prim("np.sin",
        lambda args: wrap_python_value(fn(*[unwrap_python_value(a) for a in args]))))
```

## 聚合器 core.py 模板

```python
"""
numpy/math — 144 primitives (individual directories)  ← 统计数量
"""
from eval.cas.numpy.math.sin.core import register_sin
from eval.cas.numpy.math.cos.core import register_cos
...

def register_math(env):
    # 注册每个原语到 Scheme 环境
    register_sin(env)
    register_cos(env)
    ...
```

## FFT demo.md 应用场景模板

FFT 原语的 demo.md 采用实际应用场景驱动：

| 函数 | 应用场景 | 关键代码 |
|------|---------|---------|
| `fft` | 频谱分析: 50Hz+120Hz 信号分解 | `(np.fft signal)` + `(np.fftfreq n T)` |
| `fft` | 噪声滤波: FFT→置零小幅度→IFFT | `Y-filtered` + `(np.ifft Y-filtered)` |
| `fft2` | 图像低通滤波: 掩膜+频域相乘 | `(np.fftshift (np.fft2 img))` |
| `fftshift` | 频谱可视化: 零频移中心 | `(np.log (+ 1 (np.abs (np.fftshift F))))` |
| `rfft` | 音频分析: 440Hz A4 音 | `(np.rfft audio)` + `(np.rfftfreq ...)` |
| `fftfreq` | 频率分辨率计算 | `fs/N`, `k * fs / N` |

## 代码添加陷阱

**`sed` 行内替换破坏语法**：在单原语 core.py 中添加 `getattr` 注释时，以下模式：

```python
fn = getattr(_np, "sin", None)
```

被替换为：

```python
fn = # 从 NumPy 获取 sin 函数
getattr(_np, "sin", None)
```

修复：先用 sed 恢复 `# 从 NumPy 获取` 到正确位置，匹配整行而非部分字符串。

**最佳实践**：对 300+ 文件的批量修改，先对 5 个文件测试，再全量应用。每个替换后运行 `compile()` 语法检查。

## 相关

- `references/extreme-granularity.md` — learn/ 目录模式的原始记录
- `references/demo-md-standard.md` — demo.md 编写标准
