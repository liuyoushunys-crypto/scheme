# 极端粒度拆分模式

（2026-06-22 新增 — 来自 numpy/learn/metrics 拆分到单例的经验）

## 触发条件

用户说："拆分到单例级别"、"一个模型一个子目录"、"每个函数一个目录"

## 模式

每个 Python API 函数/类/原语 → 一个独立目录：

```
模块/
├── core.py              ← 聚合器（导入所有单例）
├── __init__.py          ← from core import register
├── demo.md              ← 模块总览
├── func_1/
│   ├── core.py          ← register_func_1(env)
│   ├── __init__.py      ← from core import register
│   └── demo.md          ← 使用文档
├── func_2/ ...
```

## 聚合器

```python
from eval.cas.mymod.func_1.core import register_func_1
from eval.cas.mymod.func_2.core import register_func_2

def register_mymod(env):
    register_func_1(env)
    register_func_2(env)
```

## 单例 core.py

```python
\"\"\"mymod/func_1 — 说明\"\"\"
from core.schemevalue import Sym, Prim, PythonObject  # 必须！自导入
from eval.eval_python_import import wrap_python_value, unwrap_python_value

def register_func_1(env):
    # 注册单一原语
```

**关键**：每个 core.py 必须**自导入所有符号**。Sym/Prim/PythonObject/wrap/unwrap 等都不能依赖父级作用域传递。

## 命名转换

```python
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()  # LinearRegression→linear_regression, SVC→svc
```

Hyphens in Scheme names → underscores in dir names: `accuracy-score`→`accuracy_score`。

## 示例规模

| 模块 | 单例数 | 生成方式 |
|------|:------:|---------|
| `models/` | 118 | 批量脚本 + 聚合器 |
| `metrics/` | 58 | 批量脚本 + 聚合器 |
| `preprocessing/` | 29 | 批量脚本 + 聚合器 |
| `model_selection/` | 19 | 批量脚本 + 聚合器 |
| `numpy/` 全部 | 356 | 批量脚本 + 聚合器 |

## 验证命令

```bash
python3 -c "from eval.cas.XXX.YYY.core import register_ZZZ; print('OK')"
```

如果失败 → 缺少顶层符号导入（Sym, Prim 等）。
