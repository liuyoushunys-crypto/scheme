# numerical — 数值方法

## 求根

```scheme
(use-cas)

(find-root (lambda (x) (- (* x x) 2)) 0 2)
  →  1.4142135623730951    ; √2

(find-root (lambda (x) (- (cos x) x)) 0 1)
  →  0.7390851332151607    ; cos(x) = x 的解
```

## 数值积分

```scheme
(numerical-integrate (lambda (x) (* x x)) 0 1)
  →  0.3333333333333333    ; ∫x²dx = 1/3

(numerical-integrate (lambda (x) (exp (- (* x x)))) -1 1)
  →  1.493648265624854     ; ∫e^(-x²)dx 高斯积分
```

## 数值微分

```scheme
(numerical-derivative (lambda (x) (* x x)) 2)
  →  4.000000000          ; f'(2) = 4
(numerical-derivative (lambda (x) (exp x)) 0)
  →  0.999999999          ; e^0 = 1
```
