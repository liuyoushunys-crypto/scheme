"""
info/help — 帮助系统

提供 (help), (help 'func), (help "keyword") 以及函数数据库。
"""
from core.schemevalue import Str, Sym, Prim

# ========== CAS 函数数据库 ==========
_CAS_FUNCTIONS = {
    # ---- 微积分 ----
    "diff": {
        "语法": "(diff expr var)",
        "说明": "对 expr 关于 var 求导",
        "示例": "(diff #{x^3} x) → 3*x^2",
        "类别": "微积分",
    },
    "integrate": {
        "语法": "(integrate expr var [lower upper])",
        "说明": "求不定/定积分",
        "示例": "(integrate #{x^2} x) → x^3/3",
        "类别": "微积分",
    },
    "limit": {
        "语法": "(limit expr var point)",
        "说明": "求极限",
        "示例": "(limit #{sin(x)/x} x 0) → 1",
        "类别": "微积分",
    },
    "series": {
        "语法": "(series expr var point order)",
        "说明": "泰勒展开",
        "示例": "(series #{exp(x)} x 0 5) → 1 + x + x^2/2 + ...",
        "类别": "微积分",
    },
    "taylor": {
        "语法": "(taylor expr var point order)",
        "说明": "泰勒展开（series 别名）",
        "类别": "微积分",
    },
    "summation": {
        "语法": "(summation expr (var low high))",
        "说明": "求和",
        "示例": "(summation #{1/x^2} (list x 1 (inf)))  →  pi^2/6",
        "类别": "微积分",
    },
    "product": {
        "语法": "(product expr (var low high))",
        "说明": "求积",
        "类别": "微积分",
    },
    "grad": {
        "语法": "(grad expr var ...)",
        "说明": "梯度",
        "类别": "微积分",
    },
    "div": {
        "语法": "(div funcs var ...)",
        "说明": "散度",
        "类别": "微积分",
    },
    "curl": {
        "语法": "(curl funcs var ...)",
        "说明": "旋度",
        "类别": "微积分",
    },
    "hessian": {
        "语法": "(hessian expr var ...)",
        "说明": "Hessian 矩阵",
        "类别": "微积分",
    },
    "jacobian": {
        "语法": "(jacobian funcs var ...)",
        "说明": "Jacobian 矩阵",
        "类别": "微积分",
    },

    # ---- 代数 ----
    "expand": {
        "语法": "(expand expr)",
        "说明": "展开表达式",
        "示例": "(expand #{ (x+1)^5 }) → x^5 + 5x^4 + ... + 1",
        "类别": "代数",
    },
    "factor": {
        "语法": "(factor expr)",
        "说明": "因式分解",
        "示例": "(factor #{x^4 - 1}) → (x-1)(x+1)(x^2+1)",
        "类别": "代数",
    },
    "simplify": {
        "语法": "(simplify expr)",
        "说明": "自动简化表达式",
        "类别": "代数",
    },
    "ratsimp": {
        "语法": "(ratsimp expr)",
        "说明": "有理式简化",
        "类别": "代数",
    },
    "apart": {
        "语法": "(apart expr var)",
        "说明": "部分分式分解",
        "类别": "代数",
    },
    "together": {
        "语法": "(together expr)",
        "说明": "合并分式",
        "类别": "代数",
    },
    "collect": {
        "语法": "(collect expr var)",
        "说明": "按变量合并同类项",
        "类别": "代数",
    },
    "coeff": {
        "语法": "(coeff expr var n)",
        "说明": "提取系数",
        "类别": "代数",
    },
    "normal": {
        "语法": "(normal expr)",
        "说明": "有理式正规化",
        "类别": "代数",
    },
    "resultant": {
        "语法": "(resultant expr1 expr2 var)",
        "说明": "结式",
        "类别": "代数",
    },
    "discriminant": {
        "语法": "(discriminant expr var)",
        "说明": "判别式",
        "类别": "代数",
    },
    "compose": {
        "语法": "(compose f g)",
        "说明": "函数复合",
        "类别": "代数",
    },
    "num": {
        "语法": "(num expr)",
        "说明": "取分子",
        "类别": "代数",
    },
    "denom": {
        "语法": "(denom expr)",
        "说明": "取分母",
        "类别": "代数",
    },
    "part": {
        "语法": "(part expr n)",
        "说明": "取表达式第 n 部分",
        "类别": "代数",
    },
    "pickapart": {
        "语法": "(pickapart expr depth)",
        "说明": "按深度拆分表达式",
        "类别": "代数",
    },

    # ---- 三角/对数 ----
    "trigexpand": {
        "语法": "(trigexpand expr)",
        "说明": "三角展开",
        "类别": "三角/对数",
    },
    "trigsimp": {
        "语法": "(trigsimp expr)",
        "说明": "三角化简",
        "类别": "三角/对数",
    },
    "logcombine": {
        "语法": "(logcombine expr)",
        "说明": "合并对数",
        "类别": "三角/对数",
    },
    "powsimp": {
        "语法": "(powsimp expr)",
        "说明": "合并幂",
        "类别": "三角/对数",
    },
    "radsimp": {
        "语法": "(radsimp expr)",
        "说明": "根式化简",
        "类别": "三角/对数",
    },

    # ---- 方程 ----
    "solve": {
        "语法": "(solve eqn var)",
        "说明": "求解方程",
        "示例": "(solve #{x^2 - 4 = 0} x) → [-2, 2]",
        "类别": "方程",
    },
    "subs": {
        "语法": "(subs expr old new)",
        "说明": "代入替换",
        "类别": "方程",
    },
    "lhs": {
        "语法": "(lhs eqn)",
        "说明": "取方程左侧",
        "类别": "方程",
    },
    "rhs": {
        "语法": "(rhs eqn)",
        "说明": "取方程右侧",
        "类别": "方程",
    },
    "isolate": {
        "语法": "(isolate eqn var)",
        "说明": "分离变量",
        "类别": "方程",
    },

    # ---- 线性代数 ----
    "matrix": {
        "语法": "(matrix '((1 2) (3 4)))",
        "说明": "创建矩阵",
        "类别": "线性代数",
    },
    "det": {
        "语法": "(det M)",
        "说明": "行列式",
        "类别": "线性代数",
    },
    "inv": {
        "语法": "(inv M)",
        "说明": "逆矩阵",
        "类别": "线性代数",
    },
    "transpose": {
        "语法": "(transpose M)",
        "说明": "转置",
        "类别": "线性代数",
    },
    "eigenvals": {
        "语法": "(eigenvals M)",
        "说明": "特征值",
        "类别": "线性代数",
    },
    "eigenvects": {
        "语法": "(eigenvects M)",
        "说明": "特征向量",
        "类别": "线性代数",
    },
    "eye": {
        "语法": "(eye n)",
        "说明": "单位矩阵",
        "类别": "线性代数",
    },
    "zeros": {
        "语法": "(zeros n) / (zeros m n)",
        "说明": "零矩阵",
        "类别": "线性代数",
    },
    "ones": {
        "语法": "(ones n) / (ones m n)",
        "说明": "全一矩阵",
        "类别": "线性代数",
    },
    "lu-decomp": {
        "语法": "(lu-decomp M)",
        "说明": "LU 分解",
        "类别": "线性代数",
    },
    "qr-decomp": {
        "语法": "(qr-decomp M)",
        "说明": "QR 分解",
        "类别": "线性代数",
    },
    "svd": {
        "语法": "(svd M)",
        "说明": "SVD 分解",
        "类别": "线性代数",
    },
    "norm": {
        "语法": "(norm M)",
        "说明": "范数",
        "类别": "线性代数",
    },
    "rank": {
        "语法": "(rank M)",
        "说明": "矩阵秩",
        "类别": "线性代数",
    },
    "nullspace": {
        "语法": "(nullspace M)",
        "说明": "零空间",
        "类别": "线性代数",
    },

    # ---- 数论 ----
    "prime?": {
        "语法": "(prime? n)",
        "说明": "素数判断",
        "类别": "数论",
    },
    "nextprime": {
        "语法": "(nextprime n)",
        "说明": "下一个素数",
        "类别": "数论",
    },
    "prevprime": {
        "语法": "(prevprime n)",
        "说明": "上一个素数",
        "类别": "数论",
    },
    "factorint": {
        "语法": "(factorint n)",
        "说明": "整数分解",
        "类别": "数论",
    },
    "divisors": {
        "语法": "(divisors n)",
        "说明": "所有因子",
        "类别": "数论",
    },
    "totient": {
        "语法": "(totient n)",
        "说明": "欧拉函数 φ(n)",
        "类别": "数论",
    },
    "mobius": {
        "语法": "(mobius n)",
        "说明": "Möbius 函数 μ(n)",
        "类别": "数论",
    },
    "primerange": {
        "语法": "(primerange low high)",
        "说明": "范围内素数",
        "类别": "数论",
    },

    # ---- 特殊函数 ----
    "roots": {
        "语法": "(roots poly)",
        "说明": "多项式求根",
        "类别": "特殊函数",
    },
    "nroots": {
        "语法": "(nroots poly)",
        "说明": "数值求根",
        "类别": "特殊函数",
    },
    "dsolve": {
        "语法": "(dsolve eqn func)",
        "说明": "求解微分方程",
        "类别": "特殊函数",
    },
    "laplace": {
        "语法": "(laplace expr t s)",
        "说明": "拉普拉斯变换",
        "类别": "特殊函数",
    },
    "inverse-laplace": {
        "语法": "(inverse-laplace expr s t)",
        "说明": "逆拉普拉斯变换",
        "类别": "特殊函数",
    },
    "fourier": {
        "语法": "(fourier expr var k)",
        "说明": "傅里叶变换",
        "类别": "特殊函数",
    },
    "inverse-fourier": {
        "语法": "(inverse-fourier expr k x)",
        "说明": "逆傅里叶变换",
        "类别": "特殊函数",
    },
    "lambertw": {
        "语法": "(lambertw x)",
        "说明": "Lambert W 函数",
        "类别": "特殊函数",
    },
    "stirling": {
        "语法": "(stirling n k)",
        "说明": "第一类 Stirling 数",
        "类别": "特殊函数",
    },
    "bernoulli": {
        "语法": "(bernoulli n)",
        "说明": "Bernoulli 数",
        "类别": "特殊函数",
    },
    "fibonacci": {
        "语法": "(fibonacci n)",
        "说明": "Fibonacci 数",
        "类别": "特殊函数",
    },
    "polylog": {
        "语法": "(polylog s z)",
        "说明": "多重对数函数",
        "类别": "特殊函数",
    },
    "factorial": {
        "语法": "(factorial n)",
        "说明": "阶乘",
        "类别": "特殊函数",
    },
    "binomial": {
        "语法": "(binomial n k)",
        "说明": "二项式系数",
        "类别": "特殊函数",
    },

    # ---- 假设 ----
    "assume": {
        "语法": "(assume prop)",
        "说明": "添加假设",
        "类别": "假设",
    },
    "unassume": {
        "语法": "(unassume)",
        "说明": "清除假设",
        "类别": "假设",
    },
    "refine": {
        "语法": "(refine expr)",
        "说明": "基于假设化简",
        "类别": "假设",
    },
    "assuming": {
        "语法": "(assuming facts expr)",
        "说明": "临时假设求值",
        "类别": "假设",
    },
    "ask": {
        "语法": "(ask prop)",
        "说明": "查询假设",
        "类别": "假设",
    },

    # ---- 输出 ----
    "pretty": {
        "语法": "(pretty expr)",
        "说明": "美观输出",
        "类别": "输出",
    },
    "latex": {
        "语法": "(latex expr)",
        "说明": "输出 LaTeX",
        "类别": "输出",
    },
    "ccode": {
        "语法": "(ccode expr)",
        "说明": "输出 C 代码",
        "类别": "输出",
    },
    "fcode": {
        "语法": "(fcode expr)",
        "说明": "输出 Fortran 代码",
        "类别": "输出",
    },
    "mathml": {
        "语法": "(mathml expr)",
        "说明": "输出 MathML",
        "类别": "输出",
    },
    "describe": {
        "语法": "(describe obj)",
        "说明": "查看 Python 对象描述",
        "类别": "输出",
    },
    "py-len": {
        "语法": "(py-len obj)",
        "说明": "Python 对象长度",
        "类别": "输出",
    },

    # ---- 集合 ----
    "set": {
        "语法": "(set elem ...)",
        "说明": "创建集合",
        "类别": "集合",
    },
    "union": {
        "语法": "(union set1 set2)",
        "说明": "并集",
        "类别": "集合",
    },
    "intersection": {
        "语法": "(intersection set1 set2)",
        "说明": "交集",
        "类别": "集合",
    },
    "set-difference": {
        "语法": "(set-difference s1 s2)",
        "说明": "差集",
        "类别": "集合",
    },
    "symmetric-difference": {
        "语法": "(symmetric-difference s1 s2)",
        "说明": "对称差",
        "类别": "集合",
    },
    "subset?": {
        "语法": "(subset? set1 set2)",
        "说明": "子集判断",
        "类别": "集合",
    },
    "element?": {
        "语法": "(element? elem set)",
        "说明": "元素判断",
        "类别": "集合",
    },

    # ---- 统计 ----
    "mean": {
        "语法": "(mean data)",
        "说明": "均值",
        "类别": "统计",
    },
    "median": {
        "语法": "(median data)",
        "说明": "中位数",
        "类别": "统计",
    },
    "variance": {
        "语法": "(variance data)",
        "说明": "方差",
        "类别": "统计",
    },
    "std": {
        "语法": "(std data)",
        "说明": "标准差",
        "类别": "统计",
    },
    "correlation": {
        "语法": "(correlation data1 data2)",
        "说明": "相关系数",
        "类别": "统计",
    },
    "regression": {
        "语法": "(regression xs ys)",
        "说明": "线性回归",
        "类别": "统计",
    },

    # ---- 数值 ----
    "find-root": {
        "语法": "(find-root f a b)",
        "说明": "数值求根",
        "类别": "数值",
    },
    "numerical-integrate": {
        "语法": "(numerical-integrate f a b)",
        "说明": "数值积分",
        "类别": "数值",
    },
    "numerical-derivative": {
        "语法": "(numerical-derivative f x)",
        "说明": "数值微分",
        "类别": "数值",
    },

    # ---- 语法糖 ----
    "use-cas": {
        "语法": "(use-cas)",
        "说明": "一键加载全部 CAS 原语",
        "类别": "系统",
    },
    "use-engine": {
        "语法": "(use-engine 'mode)",
        "说明": "切换 CAS 引擎 (auto/sympy/symengine)",
        "类别": "系统",
    },
    "engine-info": {
        "语法": "(engine-info)",
        "说明": "显示引擎状态",
        "类别": "系统",
    },
    "defsym": {
        "语法": "(defsym sym ...)",
        "说明": "便捷创建 sympy 符号",
        "类别": "系统",
    },
    "with-symbols": {
        "语法": "(with-symbols (sym ...) body ...)",
        "说明": "临时符号作用域",
        "类别": "系统",
    },
}

# 按类别排序
_CATEGORY_ORDER = [
    "微积分", "代数", "三角/对数", "方程", "线性代数",
    "数论", "特殊函数", "假设", "输出", "集合",
    "统计", "数值", "系统",
]


def cas_help(args):
    """帮助系统"""
    if not args:
        # 全部帮助
        lines = ["╔══════════════════════════════════════════╗"]
        lines.append("║         CAS 帮助系统 (90+ 函数)        ║")
        lines.append("╚══════════════════════════════════════════╝")
        lines.append("")
        lines.append("用法: (help)            → 全部函数列表")
        lines.append("      (help '函数名)    → 查看函数详情")
        lines.append("      (help \"关键词\")  → 搜索关键词")
        lines.append("")

        by_cat = {}
        for name, info in _CAS_FUNCTIONS.items():
            cat = info.get("类别", "其他")
            by_cat.setdefault(cat, []).append(name)

        for cat in _CATEGORY_ORDER:
            if cat in by_cat:
                lines.append(f"── {cat} ──")
                for name in sorted(by_cat[cat]):
                    syn = _CAS_FUNCTIONS[name]["语法"]
                    lines.append(f"  {syn}")
                lines.append("")
        for cat in sorted(by_cat):
            if cat not in _CATEGORY_ORDER:
                lines.append(f"── {cat} ──")
                for name in sorted(by_cat[cat]):
                    syn = _CAS_FUNCTIONS[name]["语法"]
                    lines.append(f"  {syn}")
                lines.append("")

        lines.append(f"共 {len(_CAS_FUNCTIONS)} 个函数")
        return Str("\n".join(lines))

    arg = args[0]
    if isinstance(arg, Sym):
        name = arg.name
        if name in _CAS_FUNCTIONS:
            info = _CAS_FUNCTIONS[name]
            lines = [f"── {name} ──"]
            for k, v in info.items():
                lines.append(f"  {k}: {v}")
            return Str("\n".join(lines))
        return Str(f"未知函数: {name}")

    # 字符串查询
    if hasattr(arg, 'get_str'):
        query = arg.get_str().lower()
    else:
        query = str(arg).lower()
    results = []
    for name, info in _CAS_FUNCTIONS.items():
        info_str = name.lower() + ' ' + info.get("说明", "").lower() + ' ' + info.get("类别", "").lower()
        if query in info_str:
            results.append(name)
    if results:
        lines = [f"搜索 '{query}' 找到 {len(results)} 个结果:"]
        for name in sorted(results):
            syn = _CAS_FUNCTIONS[name]["语法"]
            desc = _CAS_FUNCTIONS[name]["说明"]
            lines.append(f"  {syn}  — {desc}")
        return Str("\n".join(lines))
    return Str(f"未找到与 '{query}' 相关的结果")


def register_help_primitives(env):
    """Register help primitives."""
    env.define("help", Prim("help", cas_help))
    env.define("?",
               Prim("?", lambda args: cas_help(args) if args else cas_help([args])))
    env.define("??",
               Prim("??", lambda args: cas_help(args) if args else Str("??: need keyword")))
    env.define("apropos",
               Prim("apropos", lambda args: cas_help(args) if args else Str("apropos: need keyword")))


register_primitives = register_help_primitives