# 批量包装器生成模式

## 背景

2026-06-23 会话中发现原本的覆盖率审计方法（数 env.define 调用数）是倒果为因。正确方法是：**以 site-packages 为基准**，比较 `dir(package)` 中的真实可调用函数与 `env.define` 注册的包装函数。

## 初始覆盖率（对比 site-packages）

| 包 | 真实 API | 已包装 | 缺口 |
|:---|:--------:|:------:|:----:|
| numpy | 496 | ~224 | 272 |
| scipy | 21子包(~1000) | 0 | ~1000 |
| pandas | 119 | ~5 | 114 |
| networkx | 944 | ~7 | 937 |
| sympy | 928 | ~38 | 890 |
| symengine | 160 | ~14 | 146 |
| mpmath | 361 | ~7 | 354 |
| matplotlib | 48 | 0 | 48 |
| cvxpy | 63 | ~4 | 59 |
| 其他 | ~200 | ~10 | ~190 |
| **总计** | **~4300** | **~309** | **~4000** |

## 多轮批量生成

每轮流程：

```python
# 1. 定义要包装的函数列表
new_funcs = [
    ('subcat', 'name', 'package.func', '文档', [('参数','默认','说明')], ["(scheme-example ...)"], ["注意"]),
]

# 2. 批量创建包装器
for subcat, name, api, doc, params, ex, notes in new_funcs:
    create_wrapper(mod_dir, subcat, name, api, doc, params, ex, notes)
    update_agg(mod_dir, subcat)  # 更新聚合器

# 3. 验证
python3 -c "from eval.cas.{mod}.core import register_{mod}_primitives; print('OK')"
```

## create_wrapper 函数

```python
def create_wrapper(module_dir, subcat, name, api_name, doc, params, examples, notes):
    """创建单个原语包装器: core.py + __init__.py + demo.md"""
    prim_dir = os.path.join(module_dir, subcat, name)
    os.makedirs(prim_dir, exist_ok=True)
    
    # __init__.py (空)
    with open(os.path.join(prim_dir, '__init__.py'), 'w'): pass
    
    # core.py — 使用 getattr 链解析 API 路径
    parts = api_name.split('.')
    top_pkg = parts[0]
    attr_path = '.'.join(parts[1:])
    with open(os.path.join(prim_dir, 'core.py'), 'w') as f:
        f.write(f'''
"""\n{api_name}\n{doc}\n"""
from eval.eval_python_import import wrap_python_value, unwrap_python_value
from core.schemevalue import Sym, Prim
def register(env):
    import {top_pkg}
    obj = {top_pkg}
    for p in "{attr_path}".split("."):
        obj = getattr(obj, p, None)
        if obj is None: return
    env.define(Sym("{api_name}"), Prim("{api_name}",
        lambda args: wrap_python_value(obj(*[unwrap_python_value(a) for a in args]))))
''')
    
    # demo.md — 参数表 + 实参示例 + 注意事项
    lines = [f"# {subcat}/{name} -- {api_name}", "", doc, ""]
    if params:
        lines.append("## 参数\n\n| 参数 | 默认 | 说明 |\n|------|------|------|")
        for p, d, desc in params:
            lines.append(f"| `{p}` | `{d}` | {desc} |")
        lines.append("")
    lines.append("```scheme")
    for ln in examples: lines.append(ln)
    lines.append("```")
    if notes:
        lines.append("\n## 注意")
        for n in notes: notes.append(f"- {n}")
    lines.append("")
    with open(os.path.join(prim_dir, 'demo.md'), 'w') as f:
        f.write('\n'.join(lines))
```

## update_agg 函数

```python
def update_agg(module_dir, subcat):
    """重新生成子分类的聚合器 core.py"""
    cat_dir = os.path.join(module_dir, subcat)
    if not os.path.isdir(cat_dir): return
    prims = sorted([d for d in os.listdir(cat_dir) 
                    if os.path.isdir(os.path.join(cat_dir, d)) and d not in ('__pycache__',)])
    agg = ['"""', f'{subcat} -- aggregator', '"""', '']
    for p in prims:
        agg.append(f'from .{p}.core import register as register_{p}')
    agg.append(f'\ndef register_{subcat}(env):')
    for p in prims:
        agg.append(f'    register_{p}(env)')
    agg.append('')
    with open(os.path.join(cat_dir, 'core.py'), 'w') as f:
        f.write('\n'.join(agg))
```

## 最终覆盖率（2026-06-23 多轮后）

| 包 | 最终 env.define | 估计 API 覆盖率 |
|:---|:---------------:|:--------------:|
| numpy | 516 | ~75% |
| scipy | 158 | ~15% |
| sympy | 154 | ~25% |
| networkx | 129 | ~12% |
| mpmath | 107 | ~30% |
| matplotlib | 63 | ~60% |
| pandas | 62 | ~40% |
| symengine | 46 | ~30% |
| galois | 45 | ~60% |
| cvxpy | 42 | ~20% |
| statsmodels | 40 | ~15% |
| numba | 26 | ~20% |
| pulp | 18 | ~10% |
| pint | 15 | ~40% |
| uncertainties | 15 | ~60% |
| **总计** | **1436 (含非前缀1909)** | |

## 关键教训

1. **site-packages 是本源** — 不要数包装层的 env.define，要对比真实 Python API
2. **批量生成 > 手写** — 一次性定义列表+创建函数，远快于逐个手写目录
3. **聚合器必须实时更新** — 每批次后调 update_agg
4. **每个包装器必须含 demo.md** — 参数表 + 实参 Scheme 示例 + 注意事项
