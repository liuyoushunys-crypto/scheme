# NumPy 桥接系统扫描与自动补齐 (2026-06-22)

## 原则

用编程方式扫描 `def pnp_xxx` 函数定义与 `("np.xxx", pnp_xxx)` 注册项之间的差距，自动补齐缺失的注册。

## 方法

### 第1步: 全量扫描

```python
# 扫描所有 core.py 文件
for root, dirs, files in os.walk(numpy_dir):
    for f in files:
        if f == 'core.py':
            # 提取所有 def pnp_xxx
            defined = {fn for line in content if fn.startswith('def pnp_')}
            # 提取所有 ("np.xxx", pnp_xxx) 注册
            registered = {fn for line in register_func if line contains '("np.'}
            missing = defined - registered
```

### 第2步: 命名映射

`pnp_xxx` → `np.xxx` 的命名转换表 (kebab-case):

```python
def pnp_to_np_name(fn_name):
    special = {
        'zeros_like': 'zeros-like',
        'ones_like': 'ones-like',
        'atleast_1d': 'atleast-1d',
        'logical_and': 'logical-and',
        'bitwise_and': 'bitwise-and',
        'column_stack': 'column-stack',
        'greater_equal': 'greater-equal',
        'array_equal': 'array-equal',
        'sort_complex': 'sort-complex',
        'count_nonzero': 'count-nonzero',
        'nan_to_num': 'nan-to-num',
        # ... ~100+ entries
    }
    return special.get(name, name)  # default: same name
```

### 第3步: 自动生成注册条目

```python
new_lines = []
for fn in missing:
    np_name = pnp_to_np_name(fn)
    if not skip:
        new_lines.append(f'        ("np.{np_name}", {fn}),')

# 插入到 register 函数的 ] 之前
reg_end = content.rfind('\n    ]')
content = content[:reg_end] + '\n' + '\n'.join(new_lines) + content[reg_end:]
```

### 第4步: 验证

```python
# 重新验证: 0 missing = 通过
missing = defined - registered
assert len(missing) == 0, f"Still missing: {missing}"
```

## 全覆盖审计工作流

完整方法：`dir()` 扫描 → 归一化命名(kebab↔underscore) → 分类重要性 → 批量补齐。

```python
# 1. 获取完整 API
all_np = {n for n in dir(np) if not n.startswith('_') and (callable(n) or ...)}

# 2. 归一化对比（kebab ↔ underscore）
ours_norm = {name.replace('-', '_') for name in our_registered_names}

# 3. 分类重要程度
high = {'argmax', 'argmin', 'eigvalsh', 'fftfreq', 'nanmedian', ...}
missing_important = [n for n in missing if n in high]

# 4. 批量补齐（每次 ~20 函数）
```

归一化后 top-level 覆盖 244/462 (53%), linalg 23/33 (70%), fft 10/19 (53%)。

## 结果

| 指标 | 之前 | 之后 |
|------|:----:|:----:|
| 注册原语 | 170 | 322 (含 distutils) |
| 新增（本会话） | - | 146 (注册修复 124 + 补齐 22) |
| 修复文件数 | - | create/manipulate/math/transform/random/io/linalg/gistutils |
| distutils | - | `np.system-info` — 构建配置/BLAS/LAPACK/编译器/SIMD 检测 |

## Cons 遍历陷阱

`_lst` 辅助函数最初用 `for i in range(len(a))` 遍历 Scheme Cons 列表，但 `Cons` 不支持 `len()`:

```python
# ❌ TypeError: object of type 'Cons' has no len()
def _lst(a):
    items = []
    for i in range(len(a)):  # ← fails
        items.append(_a(i, a))
    return items

# ✅ 正确模式
def _lst(cons):
    items = []
    while isinstance(cons, Cons):
        items.append(unwrap_python_value(cons.car))
        cons = cons.cdr
    return items
```
