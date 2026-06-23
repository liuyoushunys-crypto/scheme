# bridge — 图/数组/单位封装

提供 Graph/DiGraph/MultiGraph、tensor-product、make-array 等。

## 图

```scheme
(use-graph 'networkx)   →  切换到 networkx 后端

(Graph)                            →  空图
(Graph '(1 2) '(2 3))             →  含两条边的图
(DiGraph '(1 2) '(2 3))           →  有向图
```

## 数组

```scheme
(make-array '(1 2 3))              →  numpy array [1 2 3]
(Array 1 2 3)                      →  numpy array [1 2 3]
```

## 转换

```scheme
(convert-to (list 1 2 3) 'numpy)   →  numpy array
(convert-to m 'list)               →  Python list
```
