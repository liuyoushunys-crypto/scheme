# eval/cas 命名与存储约定（2026-06-23 更新）

## 核心原则

PyPI 生态系统包的存储路径、文件组织和 `env.define` 名称必须镜像其 Python 模块导入路径。
**此规则只适用于 PyPI 生态系统包**（CAS_ECOSYSTEM.md 中列出的包），**不适用于内部 CAS 模块**。

```
site-packages/xxx/yyy/zzz.py  (模块 xxx.yyy.zzz, 来自 PyPI)
  ↓
eval/cas/xxx/yyy/zzz.py       (镜像文件)
eval/cas/xxx/yyy/zzz.md       (文档)
env.define("xxx.yyy.zzz", ...)  (注册名)
```

## 适用范围

| 类型 | 适用规则 | 示例 |
|------|---------|------|
| **PyPI 生态包** (CAS_ECOSYSTEM.md) | ✅ 必须镜像模块路径 | `numpy.linalg.solve` → `eval/cas/numpy/linalg/solve.py`, `env.define("numpy.linalg.solve")` |
| **内部 CAS 模块** (core, info, sugar, assume, numerical, entry, bridge, engine, parse, pattern, tensor, viz) | ❌ 不适用，保留短名 | `env.define("expand", ...)`, `env.define("help", ...)`, `env.define("diff", ...)` |

## 映射细则（PyPI 生态包适用）

| Python 模块 | 存储位置 | env.define 名称 |
|---|---|---|
| `numpy.linalg.solve` | `eval/cas/numpy/linalg/solve.py` + `solve.md` | `"numpy.linalg.solve"` |
| `scipy.optimize.minimize` | `eval/cas/scipy/optimize/minimize.py` + `minimize.md` | `"scipy.optimize.minimize"` |

## 内部 CAS 模块命名（不适用镜像规则）

内部 CAS 模块保留短名（无模块路径前缀），保持 Scheme API 简洁：

```scheme
; 用户直接调用
(expand expr)
(diff f x)
(help)

; 内部注册
env.define("expand", Prim("expand", cas_expand))
env.define("diff", Prim("diff", cas_diff))
env.define("help", Prim("help", cas_help))
```

## 执行规则

当用户给出明确的存储/命名原则时：
1. 先确认适用范围（PyPI 包 vs 内部模块）
2. 直接应用并展示结果 — 不需要用 3+ 个问题确认理解
3. 先做一个具体示例看效果，再批量执行

## 原错误（已修正）

之前错误地将镜像规则（`xxx.yyy.zzz` → 完全限定名）应用到了内部 CAS 模块。2026-06-23 会话中用户明确澄清：**只限于 PyPI 生态包，内部 CAS 模块保留短名**。
