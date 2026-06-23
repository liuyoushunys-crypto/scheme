# 可视化增强系统 — 参考

## 模块文件

`eval/eval_py_viz.py` — 17 种图表类型 + 图管理 + 标注，基于 matplotlib。

注册: `register_viz_primitives(env)` 在 `primitives/primitives.py` 中调用。

## 17 种图表类型

| 命令 | 参数 | 说明 |
|------|------|------|
| `plot` | `(plot xs ys :kw)` 或 `(plot expr var lo hi :kw)` | 折线图 — numpy 数据或 CAS 表达式 |
| `scatter` | `(scatter x y :color 'red :s 20 :alpha 0.7)` | 散点图 |
| `bar` | `(bar x height :width 0.8 :color 'steelblue)` | 柱状图 |
| `barh` | `(barh y width :height 0.8)` | 水平柱状图 |
| `hist` | `(hist data :bins 30 :density #f :cumulative #f)` | 直方图 |
| `boxplot` | `(boxplot data :notch #f :vert #t)` | 箱线图 |
| `violin` | `(violin data :showmeans #t)` | 小提琴图 |
| `errorbar` | `(errorbar x y yerr :fmt 'o :capsize 5)` | 误差棒图 |
| `contour` | `(contour X Y Z :levels 20 :fill #f)` | 等高线图 |
| `imshow` | `(imshow data :cmap 'viridis :aspect 'auto)` | 热力图/图像 |
| `stem` | `(stem x y :linefmt 'C0-)` | 茎叶图 |
| `pie` | `(pie sizes :labels (list 'a 'b) :autopct '%1.1f%%')` | 饼图 |
| `fill-between` | `(fill-between x y1 y2 :color 'blue :alpha 0.3)` | 填充区域 |
| `plot-param` | `(plot-param fx fy var lo hi :title ...)` | 2D 参数曲线 |
| `plot3d` | `(plot3d expr var1 lo1 hi1 var2 lo2 hi2 :title ...)` | 3D 曲面 |

## 通用关键词参数

所有图表类型共享:

| 关键词 | 类型 | 说明 |
|--------|------|------|
| `:title` | string | 图标题 |
| `:xlabel` | string | 横轴标签 |
| `:ylabel` | string | 纵轴标签 |
| `:grid` | bool | 显示网格 |
| `:xlim` | list [lo, hi] | 横轴范围 |
| `:ylim` | list [lo, hi] | 纵轴范围 |
| `:size` | list [w, h] | 图形尺寸 (inches) |
| `:legend` | bool/string | 显示图例 |
| `:save` | string | 保存路径 (自动 150dpi) |
| `:show` | bool | 显示窗口 (默认 #t, :show #f 静默生成) |

图类型特有参数:

| 图类型 | 特有参数 |
|--------|---------|
| scatter | `:c`/`:color` `:s`(size) `:marker` `:alpha` `:cmap` |
| bar | `:width` `:color` `:edgecolor` `:alpha` `:align` |
| hist | `:bins` `:density` `:cumulative` `:histtype` `:weights` |
| boxplot | `:notch` `:vert` `:patch_artist` `:labels` `:showmeans` |
| errorbar | `:yerr` `:xerr` `:fmt` `:capsize` `:color` `:marker` |
| contour | `:levels` `:fill` `:cmap` `:colorbar` |
| imshow | `:cmap` `:aspect` `:interpolation` `:vmin` `:vmax` `:colorbar` |
| pie | `:labels` `:autopct` `:colors` `:explode` `:shadow` `:startangle` |

## CAS 表达式模式

`(plot #{x^2} x -3 3 :title "Parabola")` — 用 `#{...}` 中缀：

```python
# 解析流程
pos = [unwrap_python_value(a) for a in args if not :kw]
expr, var, lo, hi = pos[0], pos[1], pos[2], pos[3]

import sympy as _sp
sym_var = _sp.Symbol(str(var))
f = _sp.lambdify(sym_var, _sp.sympify(expr), 'numpy')
xs = np.linspace(float(lo), float(hi), 400)
ys = f(xs)
```

**重要**: lambdify 必须用 `import sympy` 而非引擎模块 `_sympy()`（调用 `get_engine()` 可能返回 symengine 导致 `lambdify()` 接口不兼容）。

## 图管理

| 命令 | 说明 |
|------|------|
| `(figure :size (list 10 6) :dpi 100 :title 'Fig)` | 创建/切换图 |
| `(subplot rows cols index)` | 创建子图 |
| `(savefig "path.png" :dpi 150)` | 保存当前图 |
| `(clf)` | 清空当前图 |
| `(close)` | 关闭当前图 |

## 标注

| 命令 | 说明 |
|------|------|
| `(text x y "str" :fontsize 12 :color 'red)` | 文字标注 |
| `(axvline x :color 'red :linestyle '-- :label 'cutoff)` | 竖线 |
| `(axhline y :color 'gray :linestyle ': :label 'base)` | 横线 |
| `(title "text")` | 设置标题（快捷） |
| `(xlabel "text")` | 设置横轴标签 |
| `(ylabel "text")` | 设置纵轴标签 |
| `(legend)` | 显示图例 |
| `(grid)` | 显示网格 |

## 多子图示例

```scheme
(figure :size (list 12 8) :show #f)
(subplot 2 3 1) (plot xs ys :show #f) (title "sin")
(subplot 2 3 2) (hist (np.random.randn 500) :bins 20 :show #f) (title "hist")
(subplot 2 3 3) (imshow (np.random.rand 10 10) :show #f :cmap "plasma") (title "heat")
(subplot 2 3 4) (scatter xs ys :show #f :color "red") (title "scatter")
(savefig "/tmp/comprehensive.png")
```

## 实现模式

所有图表函数遵循统一模式:

```python
def cas_xxx(args):
    plt = _mpl()
    pos, kwargs = _pos_kw(args)    # 分离位置/关键词参数
    if len(pos) < N: raise ...      # 参数检查
    fig, ax = plt.subplots()        # 创建图
    ax.xxx(pos[0], pos[1], **kwargs)# matplotlib 调用
    return _finalize(plt, kwargs, fig)  # 样式+保存+显示
```

`_pos_kw` 将 Scheme 关键词 `:key val` 转为 Python 字典 `{'key': val}`（自动 `-` → `_`）。

`_finalize` 应用通用样式参数 + 保存/显示/关闭。
