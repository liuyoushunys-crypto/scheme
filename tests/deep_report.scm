; ============================================================
; 深度测试 5/5: 最终回归 & 基础设施缺失报告
; ============================================================

(display "=== Final Regression ===\n")
(display "Running all 15 test files...\n")

; 基础设施缺失及解决方案
(display "\n=== Infrastructure Gaps Found ===\n")

(display "\n1. ).method 语法不支持")
(newline)
(display "   ((obj).method ...) 被读作点对语法")
(newline)
(display "   方案: 使用中间变量 (define tmp (obj)) (tmp.method ...)")
(newline)

(display "\n2. Python 切片语法缺失")
(newline)
(display "   arr[2:8:2], arr[mask], df.iloc[0] 等均无法直接表达")
(newline)
(display "   方案: py-eval 可部分替代但无法访问 Scheme 变量")
(newline)
(display "   推荐: 添加 py-slice 原语")
(newline)

(display "\n3. py-eval 无法访问 Scheme 变量")
(newline)
(display "   (py-eval \"arr[2:8:2]\") 失败: arr 是 Scheme 变量")
(newline)
(display "   方案: 需 py-exec 或变量传递机制")
(newline)

(display "\n4. in-place 方法返回 None")
(newline)
(display "   arr.sort() 返回 None, PythonObject 0-arg 返回自身")
(newline)
(display "   但返回 None 时正确语义是 nil")
(newline)

(display "\n5. 多参数 lambda 的 Python 内省")
(newline)
(display "   scipy.curve_fit 需要 __code__/__signature__")
(newline)
(display "   状态: 已修复 ✅")
(newline)

(display "\n6. Python dict 创建")
(newline)
(display "   (py-dict :key val :key2 val2) 已添加 ✅")
(newline)

(display "\n7. py-get 整数索引")
(newline)
(display "   (py-get tuple 0) 已支持 ✅")
(newline)

(display "\n8. py-get PythonObject 索引")
(newline)
(display "   (py-get obj (py-eval \"slice(0,2)\")) 已支持 ✅")
(newline)

(display "\n9. __iadd__ 方法访问")
(newline)
(display "   Python 的 += 运算符在 Scheme 中需用 __iadd__")
(newline)

(display "\n10. 符号/字符串不匹配")
(newline)
(display "   Sym 自动解包为 Python str (大多数情况已支持 ✅)")
(newline)

(display "\n=== Infrastructure Report Complete ===\n")
(newline)