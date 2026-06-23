# 10轮深度测试结果 — python-scheme-cas 验证报告

## 最终全量回归

```
31 tests: 26 zero-error, 5 known-nonblocking (docstring ValueError, np.nan as sym, etc.)

## 修复的缺失（12项）
详见 `software-development/testing` skill 的 `references/10-round-test-report.md`。

## 已知限制 (5项待下一阶段)
1. 原生切片语法 `arr[2:8:2]`（当前用 py-eval + 变量注入绕行）
2. 原生方法调用语法（当前用 `(. obj method args...)`）
3. Python for 迭代器
4. `+=` 运算符（用 `__iadd__`）
5. 异常桥接（Python ↔ Scheme 异常不互通）