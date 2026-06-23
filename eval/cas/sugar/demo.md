# sugar — 语法糖

Scheme 中更自然表达式的语法糖。

```scheme
(use-cas)
```

## Lambda 简化

```scheme
((lambda (x) (* x 2)) 3)          →  6
((lambda (x y) (+ x y)) 10 20)    →  30
```

## 箭头操作符

```scheme
; -> 和 ->> 宏
; (-> x f1 f2 ...)  =  (f2 (f1 x))
; (->> x f1 f2 ...) =  (f2 (... (f1 x)))
```

## for 循环宏

```scheme
(for (i 0 10 2) (display i) (newline))   ; 类似 for loop
```

## 字符串字面量

```scheme
(str "hello" " " "world")               →  "hello world"
```

## 无穷大

```scheme
(inf)  →  oo
```

## 方括号索引

```scheme
; [a i]  →  a[i]  (通过 bracket 宏)
```