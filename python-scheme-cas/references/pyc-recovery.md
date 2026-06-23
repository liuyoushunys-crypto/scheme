# `.pyc` 缓存恢复: 从字节码重建被截断的 `.py` 源文件

## 场景

本会话中 `eval/eval_python_import.py` 被截断为 5 行（缩进错误），
导致 `SyntaxError: unexpected indent`，整个系统无法 import。
但 `__pycache__/eval_python_import.cpython-311.pyc` 仍保留完整的字节码。

## 恢复方法

### 1. 读取 `.pyc` 头 + marshal 加载

```python
import dis, marshal, struct

with open('eval/__pycache__/eval_python_import.cpython-311.pyc', 'rb') as f:
    magic = f.read(4)         # 魔数
    flags = struct.unpack('<I', f.read(4))[0]
    if flags & 0x1:           # Future flags 存在时跳过
        f.read(4)
    timestamp = f.read(4)     # 修改时间戳
    size = f.read(4)          # 原始 .py 大小
    code = marshal.load(f)    # 顶层 code 对象
```

### 2. 提取结构信息

```python
print("NAMES:", code.co_names)        # 全局名字
print("CONSTS:", [type(c).__name__ for c in code.co_consts])  # 查看常量类型
print("FUNCTIONS:")
for c in code.co_consts:
    if hasattr(c, 'co_code'):          # 函数 code 对象
        print(f"  def {c.co_name}({', '.join(c.co_varnames[:c.co_argcount])}):")
        for cc in c.co_consts:
            if isinstance(cc, str) and cc.strip():
                print(f"    # doc: {cc[:120]}")
```

### 3. 完整反编译

```bash
pip install uncompyle6
uncompyle6 eval/__pycache__/eval_python_import.cpython-311.pyc > eval/eval_python_import.py
```

或用 `pycdc`:
```bash
# 从 https://github.com/zrax/pycdc 编译
pycdc eval/__pycache__/eval_python_import.cpython-311.pyc
```

### 4. 注意事项

- `.pyc` 头格式因 Python 版本而异（3.3+ 含 flags，3.11 后含 bitcode 字段）
- 反编译结果通常需要手动修复（缩进、变量名、控制流）
- 确认 `.pyc` 时间戳与期望版本匹配，避免反编译过期缓存
- 本会话最终采用手动 re-impl（基于字节码中提取的函数签名和文档字符串），
  而非全自动反编译，因为需要确保代码质量

## 核心函数签名（从字节码提取）

| 函数 | 参数 | 用途 |
|------|------|------|
| `_sym_name(val)` | 1 | Sym/Str → Python str |
| `wrap_python_value(val)` | 1 | Python → SchemeValue |
| `unwrap_python_value(val)` | 1 | SchemeValue → Python |
| `SchemeClosureWrapper.__init__` | self, closure | 包装 Closure→Python callable |
| `resolve_python_attr_chain(name, env)` | 2 | "a.b.c" → 逐级 getattr |
| `eval_py_import(cons, env)` | 2 | (import ...) 处理 |
| `register_python_import_primitives(env)` | 1 | 注册所有原语 |
