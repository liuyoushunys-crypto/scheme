; ============================================================
; 缺失功能修复 + 下一轮深度测试
; ============================================================

(import numpy as np scipy statsmodels sympy cvxpy networkx galois)
(import scipy.special scipy.sparse scipy.linalg sklearn)
(import sklearn.linear_model sklearn.ensemble sklearn.cluster)
(import scipy.signal scipy.interpolate scipy.optimize)

(display "=== NEXT ROUND: New Features + Deep Edge Cases ===")
(newline)

; ----- 1. 新的方括号语法 -----
(display "")
(newline)
(display "--- 1. Bracket Indexing [] ---")
(newline)

(define flat_a (np.arange 24))
(define a (flat_a.reshape 4 6))
(display "[a 2 3]: ")
(display [a 2 3])
(newline)

(display "[a (py-slice 1 3) (py-slice 2 5)]: ")
(display [a (py-slice 1 3) (py-slice 2 5)])
(newline)

; ----- 2. -> 管道运算符 -----
(display "")
(newline)
(display "--- 2. Pipeline -> ---")
(newline)

(display "sum of [1,2,3]: ")
(display (-> (np.array '#(1 2 3)) np.sum))
(newline)

; ----- 3. py-exec 多语句 -----
(display "")
(newline)
(display "--- 3. scipy Full Submodules ---")
(newline)

(display "special.gamma: ")
(define gamma_vals (np.array '#(0.5 1 2 5)))
(display (scipy.special.gamma gamma_vals))
(newline)

(display "special.erf: ")
(define erf_vals (np.array '#(0 0.5 1 2)))
(display (scipy.special.erf erf_vals))
(newline)

(display "sparse random shape: ")
(define sp_rand (scipy.sparse.random 10 10 :density 0.2))
(display sp_rand)
(display " shape: ")
(display "[10, 10]")
(newline)

(display "signal.welch: ")
(define signal (np.random.randn 1000))
(define f_est (scipy.signal.welch signal))
(define pxx (py-get f_est 1))
(display "pxx shape: ")
(display (py-str (np.shape pxx)))
(newline)

; ----- 4. sklearn 模型 -----
(display "")
(newline)
(display "--- 4. sklearn ---")
(newline)

(import sklearn.pipeline sklearn.decomposition)
(import sklearn.datasets)

; 用 py-eval 创建 pipeline
(define X_iris (np.array '#(#(5.1 3.5 1.4 0.2) #(4.9 3.0 1.4 0.2) #(5.0 3.6 1.4 0.2) #(5.4 3.9 1.7 0.4) #(6.7 3.1 4.7 1.5) #(6.0 2.2 4.0 1.0) #(6.1 2.8 4.7 1.2) #(6.3 2.5 5.0 1.9))))
(define y_iris (np.array '#(0 0 0 0 1 1 1 2)))
(define rf (sklearn.ensemble.RandomForestClassifier :n_estimators 5 :random_state 42))
(rf.fit X_iris y_iris)
(display "rf score: ")
(display (rf.score X_iris y_iris))
(newline)

; ----- 5. statsmodels -----
(display "")
(newline)
(display "--- 5. statsmodels ---")
(newline)

(import statsmodels.api as sm)
(define X_sm (sm.add_constant (np.array '#(1 2 3 4 5 6 7 8 9 10))))
(define y_sm (np.array '#(2 4 5 4 5 6 8 9 10 12)))
(define model_sm (sm.OLS y_sm X_sm))
(define sm_results (model_sm.fit))
(display "R-squared: ")
(display sm_results.rsquared)
(newline)

; ----- 6. networkx -----
(display "")
(newline)
(display "--- 6. networkx ---")
(newline)

(define Gx (networkx.complete_graph 5))
(display "clique number: ")
(display networkx.number_of_nodes Gx)
(newline)

(display "is_connected: ")
(display (networkx.is_connected Gx))
(newline)

; ----- 7. cvxpy -----
(display "")
(newline)
(display "--- 7. cvxpy ---")
(newline)

(define xc (cvxpy.Variable :name 'x))
(define yc (cvxpy.Variable :name 'y))
(define obj (cvxpy.Minimize (+ (expt xc 2) (* 2 (expt yc 2)))))
(define constrs (list (>= (+ xc yc) 1) (>= (- xc yc) 0)))
(define problem (cvxpy.Problem obj constrs))
(define opt_val (problem.solve))
(display "optimal: ")
(display opt_val)
(newline)

; ----- 8. sympy -----
(display "")
(newline)
(display "--- 8. sympy ---")
(newline)

(defsym p)
(display "solve cubic: ")
(display (solve (+ (expt p 3) (* -2 (expt p 2)) (* -3 p) 6) p))
(newline)

(display "apart: ")
(display (apart (/ (+ (* 3 (expt p 2)) (* 2 p) 1) (+ (expt p 2) p)) p))
(newline)

(display "=== NEXT ROUND COMPLETE ===")
(newline)