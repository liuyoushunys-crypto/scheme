; 测试级联调用 — Python 风格

; 1. 直接 math.pi (无括号)
(py-import math)
(display "math.pi = ")
(display math.pi)
(newline)

; 2. 直接 (math.sqrt 16) (级联调用)
(display "(math.sqrt 16) = ")
(display (math.sqrt 16))
(newline)

; 3. 级联属性 + 调用
(display "(math.sin math.pi) = ")
(display (math.sin math.pi))
(newline)

; 4. 级联子模块 + 调用
(py-import os)
(display "(os.path.join \"/a\" \"b\" \"c\") = ")
(display (os.path.join "/a" "b" "c"))
(newline)

; 5. 复杂链式
(display "(math.factorial 5) = ")
(display (math.factorial 5))
(newline)

; 6. from-import 风格仍然工作
(from math import sqrt)
(display "(sqrt 25) = ")
(display (sqrt 25))
(newline)

; 7. 新旧混合
(display "(math.sqrt (math.sin 1)) = ")
(display (math.sqrt (math.sin 1)))
(newline)

; 8. PythonObject 直接调用 (py-call 不再必需！)
(py-import json)
(display "(json.dumps (py-eval \"{'a': 1, 'b': 2}\")) = ")
(display (json.dumps (py-eval "{'a': 1, 'b': 2}")))
(newline)

(display "All cascade tests passed!")