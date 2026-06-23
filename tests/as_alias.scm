; 测试 import as 语法

; 1. import as 别名
(import numpy as np)
(display "np.array: ")
(display (np.array '(1 2 3)))
(newline)

; 2. 普通 import 仍然可用
(import math)
(display "math.pi: ")
(display math.pi)
(newline)

; 3. 混合使用
(import json as j)
(display "j.dumps: ")
(display (j.dumps (py-eval "{'hello': 'world'}")))
(newline)

; 4. 多层 as 不影响后续模块
(import os as operating_system)
(display "operating_system.getcwd: ")
(display (operating_system.getcwd))
(newline)

(display "All as-alias tests passed!")