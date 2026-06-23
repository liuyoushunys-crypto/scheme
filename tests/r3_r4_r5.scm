; ============================================================
; R3+R4+R5: sympy + pandas + networkx 深层边缘
; ============================================================

(import sympy numpy as np pandas sklearn networkx galois cvxpy)
(import scipy.stats)

(display "=== R3+R4+R5: Deep Edge Cases ===\n")

; ----- R3: sympy 深层边缘 -----
(display "\n--- R3: sympy Deep Edges ---")
(newline)

(defsym x y)
(display "Piecewise: ")
(display (py-eval "sympy.Piecewise((x, x < 0), (x**2, x >= 0))" :sympy sympy :x x))
(newline)

(display "expand complex: ")
(display (expand (* (+ x sympy.I) (- x sympy.I))))
(newline)

(display "integrate x*y: ")
(display (sympy.integrate (* x y) (list x 0 1) (list y 0 1)))
(newline)

(display "compose: ")
(display (compose (sin x) (+ x 1) x))
(newline)

; ----- R4: pandas/sklearn 深层边缘 -----
(display "\n--- R4: pandas/sklearn Edges ---")
(newline)

(define df (pandas.DataFrame (py-dict :group '#(A A B B) :val '#(1 2 3 4))))
(display "groupby sum: ")
(define grp (df.groupby 'group))
(display grp.sum)
(newline)

(define with_nan (pandas.DataFrame (py-dict :x '#(1 np.nan 3) :y '#(np.nan 5 6))))
(display "fillna: ")
(display (with_nan.fillna 0))
(newline)

(import sklearn.preprocessing)
(define data (np.array '#(#(1 2) #(2 4) #(3 6))))
(display "StandardScaler: ")
(define scaler (sklearn.preprocessing.StandardScaler))
(define scaled (scaler.fit_transform data))
(display (np.mean scaled :axis 0))
(newline)

; ----- R5: networkx/galois/cvxpy 深层边缘 -----
(display "\n--- R5: networkx/galois/cvxpy Edges ---")
(newline)

(define DG (networkx.DiGraph))
(DG.add_edge 'A 'B :weight 1)
(DG.add_edge 'B 'C :weight 2)
(display "has_path A->C: ")
(display (networkx.has_path DG 'A 'C))
(newline)

(define GF (galois.GF 7))
(define mat (. (np.array '#(#(1 2) #(3 4))) view GF))
(display "GF(7) matrix: ")
(display mat)
(newline)

(define xv (cvxpy.Variable :name 'x))
(define cons (list (>= xv 0) (<= xv 10)))
(display "cvxpy constraints: ")
(display cons)
(newline)

(display "=== R3+R4+R5 Complete ===\n")
(newline)