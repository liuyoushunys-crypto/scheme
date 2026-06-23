; ============================================================
; 深度测试 4/5: pandas + networkx + sklearn + optimizers
; ============================================================

(display "=== Data Science & Optimization Depth Test ===\n")

; ----- 4.1 pandas 数据框 -----
(display "\n--- 4.1 pandas ---")
(newline)

(import pandas)
(import numpy as np)

; Series
(display "Series: ")
(define s (pandas.Series '#(10 20 30 40) :name 'values))
(display s)
(newline)

; DataFrame from dict
(display "DataFrame: ")
(define df (pandas.DataFrame (py-dict :name '#(Alice Bob Carol) :age '#(25 30 35) :score '#(88 92 85))))
(display df)
(newline)

; 属性和方法
(display "columns: ")
(display df.columns)
(newline)

(display "describe: ")
(display (df.describe))
(newline)

(display "mean (numeric only): ")
(define num_mean_df (pandas.DataFrame (py-dict :age '#(25 30 35) :score '#(88 92 85))))
(display (num_mean_df.mean))
(newline)

; 索引 — py-get 支持整数索引
(display "iloc[0]: ")
(display (py-get df.iloc 0))
(newline)

; 切片 — py-eval 创建 slice 对象
(display "iloc[0:2]: ")
(display (py-get df.iloc (py-eval "slice(0,2)")))
(newline)

; 统计
(display "corr: ")
(define num_df (pandas.DataFrame (py-dict :age '#(25 30 35) :score '#(88 92 85))))
(display (num_df.corr))
(newline)

; CSV IO
(display "to_csv: ")
(df.to_csv "/tmp/test_pandas.csv")
(display "written")
(newline)

(display "read_csv: ")
(define df2 (pandas.read_csv "/tmp/test_pandas.csv"))
(display df2.shape)
(newline)

; ----- 4.2 networkx 图论 -----
(display "\n--- 4.2 networkx ---")
(newline)

(import networkx)

; 创建图
(define G (networkx.Graph))
(G.add_edge 'A 'B :weight 1.0)
(G.add_edge 'B 'C :weight 2.0)
(G.add_edge 'C 'D :weight 3.0)
(G.add_edge 'D 'A :weight 1.5)
(G.add_edge 'A 'C :weight 0.5)

(display "nodes: ")
(display (list (G.nodes)))
(newline)

(display "edges: ")
(display (list (G.edges)))
(newline)

; 路径
(display "shortest_path: ")
(display (networkx.shortest_path G 'A 'D :weight 'weight))
(newline)

(display "shortest_path_length: ")
(display (networkx.shortest_path_length G 'A 'D :weight 'weight))
(newline)

; 中心性
(display "pagerank: ")
(display (networkx.pagerank G))
(newline)

(display "betweenness: ")
(display (networkx.betweenness_centrality G))
(newline)

; 生成器
(display "erdos_renyi: ")
(define G2 (networkx.erdos_renyi_graph 10 0.3 :seed 42))
(display "nodes: ")
(display (G2.number_of_nodes))
(newline)

; ----- 4.3 sklearn 机器学习 -----
(display "\n--- 4.3 sklearn ---")
(newline)

(import sklearn)
(import sklearn.linear_model sklearn.ensemble sklearn.cluster sklearn.model_selection)

; 线性回归
(define X (np.array '#(#(1) #(2) #(3) #(4) #(5))))
(define y (np.array '#(2 4 6 8 10)))
(define reg (sklearn.linear_model.LinearRegression))
(reg.fit X y)
(display "coef_: ")
(display (reg.coef_))
(newline)

(display "intercept_: ")
(display reg.intercept_)
(newline)

(display "score: ")
(display (reg.score X y))
(newline)

; 随机森林分类
(import sklearn.datasets)
(define iris (sklearn.datasets.load_iris))
(define rf (sklearn.ensemble.RandomForestClassifier :n_estimators 10 :random_state 42))
(rf.fit iris.data iris.target)
(display "rf accuracy: ")
(display (rf.score iris.data iris.target))
(newline)

; K-means 聚类
(define kmeans (sklearn.cluster.KMeans :n_clusters 3 :random_state 42 :n_init 10))
(kmeans.fit iris.data)
(display "kmeans inertia: ")
(display kmeans.inertia_)
(newline)

; 数据集分割
(define X_train_test (sklearn.model_selection.train_test_split iris.data iris.target :test_size 0.3 :random_state 42))
(display "train_test_split: ")
; py-get 支持整数索引
(display (np.shape (py-get X_train_test 0)))
(newline)

; ----- 4.4 cvxpy 凸优化 -----
(display "\n--- 4.4 cvxpy ---")
(newline)

(import cvxpy)

; 二次规划
(display "quadratic program: ")
(define xv (cvxpy.Variable :name 'x))
(define yv (cvxpy.Variable :name 'y))
(define objective (cvxpy.Minimize (+ (expt xv 2) (expt yv 2))))
(define constraints (list (>= (+ xv yv) 1) (>= (- xv yv) 0)))
(define prob (cvxpy.Problem objective constraints))
(define result (prob.solve))
(display result)
(newline)

(display "x.value: ")
(display xv.value)
(newline)

(display "y.value: ")
(display yv.value)
(newline)

; ----- 4.5 pulp 线性规划 -----
(display "\n--- 4.5 pulp ---")
(newline)

(import pulp)

(define prob_lp (pulp.LpProblem "test" pulp.LpMinimize))
(define xl (pulp.LpVariable "x" 0))
(define yl (pulp.LpVariable "y" 0))

; 设置目标 (用 __iadd__)
(prob_lp.__iadd__ (+ xl yl))

; 添加约束
(prob_lp.__iadd__ (>= (+ (* 2 xl) yl) 4))
(prob_lp.__iadd__ (>= (+ xl (* 3 yl)) 6))

(display "solve: ")
(define status (prob_lp.solve))
(display status)
(newline)

(display "x.value: ")
(display (pulp.value xl))
(newline)

(display "y.value: ")
(display (pulp.value yl))
(newline)

(display "=== Data Science & Optimization Depth Complete ===\n")
(newline)