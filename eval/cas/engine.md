# engine — CAS 引擎管理

CAS 符号计算引擎核心。统一管理 symengine（高速）和 sympy（完整功能）。

## 快速开始

```scheme
(use-cas)                  ; 自动加载引擎 + 所有 CAS 原语
```

## 引擎信息

```scheme
(engine-info)              ; 查看当前引擎状态
  -> 当前引擎: auto
     symengine: symengine 0.14.1 ✅
     sympy:     sympy 1.14.0 ✅
     调度策略: symengine 优先，不支持的操作 → sympy
```

## 引擎切换

```scheme
(use-engine 'auto)         ; 自动调度（默认）: symengine 优先，自动降级
(use-engine 'sympy)        ; 强制使用 sympy（所有功能可用，但慢 10-100x）
(use-engine 'symengine)    ; 强制使用 symengine（更快，但功能有限）
```

## 引擎能力矩阵

| 操作 | symengine | sympy | auto 模式调度 |
|------|-----------|-------|:------------:|
| Symbol/算术/Symbol 定义 | ✅ | ✅ | symengine |
| diff/expand/series | ✅ | ✅ | symengine |
| sin/cos/tan/sqrt/log | ✅ | ✅ | symengine |
| Matrix 创建 (eye/zeros/ones) | ✅ | ✅ | symengine |
| Eq/关系运算 | ✅ | ✅ | symengine |
| lambdify (转函数) | ✅ | ✅ | symengine |
| **integrate** | ❌ | ✅ | → sympy |
| **factor** | ❌ | ✅ | → sympy |
| **simplify** | ❌ | ✅ | → sympy |
| **solve** | ❌ | ✅ | → sympy |
| **subs** | ❌ | ✅ | → sympy |
| **limit** | ❌ | ✅ | → sympy |
| **dsolve** | ❌ | ✅ | → sympy |
| **laplace/fourier** | ❌ | ✅ | → sympy |
| **special functions** | ❌ | ✅ | → sympy |

## 参数

| 操作 | 参数 | 说明 |
|------|------|------|
| `(use-engine mode)` | `mode` | 'auto / 'symengine / 'sympy |
| `(engine-info)` | 无 | 返回引擎状态字符串 |

## 注意

- symengine 比 sympy 快 10-100 倍，但只支持约 40% 的功能
- auto 模式自动处理降级，通常不需要手动切换
- 如果安装失败：(pip install symengine) 或 (pip install sympy)
- 执行 (use-engine 'sympy) 后再用 integrate/factor/solve 等高级操作
