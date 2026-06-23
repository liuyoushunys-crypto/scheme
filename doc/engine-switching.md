# CAS 引擎管理器 — `eval/cas/engine.py`

## 架构

```
用户层:  (use-engine 'auto|'symengine|'sympy)
                   │
                   ▼
         eval/cas/engine.py
         ┌─────────────────────────┐
         │  _engine_name           │  ← 'auto', 'symengine', 'sympy'
         │  _engine_cache = {}     │  ← 惰性缓存
         │                         │
         │  get_engine() → Proxy   │  ← 返回 _EngineProxy（统一接口）
         │  call(name, *args)      │  ← 智能调度
         └─────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    symengine 0.14.1    sympy 1.14.0
    (fast C++ core)     (full CAS)
```
