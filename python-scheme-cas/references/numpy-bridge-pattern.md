# NumPy Bridge — 目录结构与全覆盖方法论

## 目录对齐（匹配 NumPy 源码）

每个 `core.py` 文件头部有带 Scheme 调用示例的文档注释：

```scheme
"""
对应: numpy.fft (傅里叶变换)
原语: 18

  [标准 FFT]
    (np.fft (np.array '(0 1 0 -1)))     →  离散傅里叶变换
    (np.ifft (np.fft sig))               →  逆变换
  [频率]
    (np.fftfreq n)                       →  FFT 频率
"""
```

## 全覆盖方法论

### "定义但未注册"扫描

扩展模块时最常见的 bug：定义了函数但忘记加入 `register_*` 函数。

```python
# 扫描 8 个 core.py
for root, dirs, files in os.walk(numpy_dir):
    for f in files:
        if f == 'core.py':
            # 收集所有 def pnp_xxx
            defined = {fn for line in content if line.strip().startswith('def pnp_')}
            # 收集所有 ("np.xxx", pnp_xxx) 注册项
            registered = {fn_part for line in register_block if '("np.' in line}
            # 差值 = 缺失
            missing = defined - registered
```

本会话中一次性修复 124 个缺失（numpy 原语从 170→322）。

### 命名转换（kebab → underscore）

注册的 Scheme 原语名用 kebab-case（`np.array-equal`），Python 函数名用 underscore（`pnp_array_equal`）。

```python
def pnp_to_np_name(fn_name):
    name = fn_name[4:]  # strip 'pnp_'
    special = {
        'zeros_like': 'zeros-like',
        'array_equal': 'array-equal',
        ...
    }
    return special.get(name, name)
```

### 用 `__all__` 白名单确保私有符号被导出

```python
__all__ = [
    '_sym_name',  # 下划线开头也被显式包含
    'register_numpy_primitives',
]
```
