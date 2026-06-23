# 正则表达式完整支持 - 基于 Python re 模块

一等公民特性: 正则表达式对象可作为值传递，匹配对象支持分组提取。

## 基本匹配

```scheme
; 从头匹配 (re.match)
(re-match "hello" "hello world")    → #<match "hello">
(re-match "world" "hello world")    → #f

; 任意位置搜索 (re.search)
(re-search "world" "hello world")   → #<match "world">

; 完全匹配 (re.fullmatch)
(re-fullmatch "\\d+" "12345")       → #<match "12345">
(re-fullmatch "\\d+" "12345abc")   → #f
```

## 捕获组提取

```scheme
(define m (re-search "([a-z]+)@([a-z]+)" "user@example.com"))
(re-group m)        → "user@example"      ; 整个匹配
(re-group m 1)      → "user"              ; 第1组
(re-group m 2)      → "example"           ; 第2组
(re-groups m)       → ("user" "example")  ; 所有捕获组
```

## 查找所有匹配

```scheme
; 返回匹配字符串列表
(re-findall "\\d+" "Room 101 and 202")  → ("101" "202")

; 返回匹配对象列表
(define matches (re-finditer "\\d+" "101, 202, 303"))
(re-group (car matches))  → "101"
```

## 分割与替换

```scheme
; 分割 (re.split)
(re-split "," "a,b,c")               → ("a" "b" "c")
(re-split "\\s+" "hello   world")    → ("hello" "world")

; 替换 (re.sub)
(re-sub "\\d+" "[NUM]" "Room 101")   → "Room [NUM]"

; 替换并计数 (re.subn) → (result . count)
(re-subn "\\d+" "[NUM]" "Room 101 and 202")
→ ("Room [NUM] and [NUM]" . 2)
```

## 编译与复用

```scheme
; 编译正则 (带标志)
(define re-email (re-compile "^[a-z]+@[a-z]+\\.[a-z]+$" 'i))  ; 'i = 忽略大小写

; 标志组合: 'i|'m|'s|'x|'a|'u|'l
; 'i/ignorecase, 'm/multiline, 's/dotall, 'x/verbose

; 使用编译对象
(re-match-obj re-email "test@example.com")   → #<match ...>
(re-search-obj re-email "Contact: test@example.com")  → #<match ...>
```

## 位置信息

```scheme
(define m (re-search "world" "hello world"))
(re-start m)        → 6        ; 开始位置
(re-end m)          → 11       ; 结束位置
(re-span m)         → (6 . 11) ; (开始 . 结束)
```

## 转义特殊字符

```scheme
(re-escape ".+*?{}[]()")   → "\\.\\+\\*\\?\\{\\}\\[\\]\\(\\)"
```

## 与 CAS 集成

```scheme
; 提取数学表达式中的数值
(define expr "3*x^2 + 2*x + 5")
(define coeffs (re-findall "\\d+" expr))   → ("3" "2" "5")

; 解析函数调用
(define code "f(x) + g(y, z)")
(define funcs (re-findall "([a-z]+)\\(" code))  → ("f" "g")
```

## 实现文件

- `eval/eval_py_re.py` - 所有正则表达式原语 (18 个函数)
- 注册: `register_re_primitives(env)` 在 `primitives/primitives.py`
- 特殊类型: `RegexObject` (编译对象), `MatchObject` (匹配对象)

## 注意事项

- Scheme 字符串中 `\` 需要双写: `\\d`, `\\s`, `\\w`
- 编译对象可重复使用，提高多次匹配效率
- 所有匹配函数支持字符串模式和编译对象
