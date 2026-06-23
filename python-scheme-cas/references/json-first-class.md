# JSON 作为 Scheme 一等公民 - 完整支持

基于 Python json 模块的完整 JSON 支持。

## 核心设计

- JSON 字面量可直接作为 Scheme 值
- 自动双向转换: Scheme list ↔ JSON array, HashTable ↔ JSON object
- Python 风格的 dict/list 操作 API

## API 参考

### 构造函数
```scheme
(json-object)                      → {} 
(json-object 'key1 "val1" 'key2 42) → {"key1": "val1", "key2": 42}
(json-array 1 2 3)                 → [1, 2, 3]
```

### 解析与序列化
```scheme
(json-parse "{\"a\": 1}")           → HashTable
(json-dumps obj)                   → "{\"a\": 1}"
(json-dumps-pretty obj)            → 带缩进的 JSON
```

### 访问与修改
```scheme
(json-get obj 'key)                → 值或 Nil
(json-get obj 'a 'b 'c)           → 多级访问 obj['a']['b']['c']
(json-set! obj 'key val)          → 设置属性
(json-del! obj 'key)              → 删除属性
```

### 查询
```scheme
(json-keys obj)                    → ("key1" "key2" ...)
(json-values obj)                  → (val1 val2 ...)
(json-has? obj 'key)               → #t/#f
```

### 合并与追加
```scheme
(json-merge obj1 obj2 ...)         → 合并对象(后者覆盖前者)
(json-append arr val ...)          → 数组追加元素
```

### 文件操作
```scheme
(json-read "/path/file.json")      → 解析后的值
(json-write "/path/file.json" obj #t) → 写入(第三参数是否格式化)
(json-update "/path/file.json" fn) → 读取→函数处理→写回
```

## 数据映射

| Scheme | JSON |
|--------|------|
| Nil() | null |
| Bool | true/false |
| Integer/Num | number |
| Str | string |
| Cons (list) | array |
| Vector | array |
| HashTable | object |
| Bytevector | base64 string |
| Sym | string |

## 实现文件

- `eval/eval_py_json.py` - 所有 JSON 原语 (18 个函数)
- 注册: `register_json_primitives(env)` 在 `primitives/primitives.py`

## 使用示例

```scheme
; 构建配置对象
(define config (json-object 'host "localhost" 'port 8080 'debug #f))

; 从文件读取
(define data (json-read "data/users.json"))

; 多级访问
(define first-username (json-get data 'users 0 'name))

; 更新并写回
(json-update "config.json" 
  (lambda (cfg) 
    (json-set! cfg 'version "2.0")))

; 与 CAS 集成
(define cas-result (json-object 
  'expression "x^2 + 1"
  'integral (integrate #{x^2 + 1} x)
  'latex (latex (integrate #{x^2 + 1} x))))
(json-dumps-pretty cas-result)
```
