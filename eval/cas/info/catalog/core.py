"""
Python 科学计算包目录系统 — 层级浏览全部功能。

使用：
  (catalog)                          → 顶级分类浏览
  (catalog 'scipy)                   → scipy 子模块
  (catalog 'scipy.optimize)          → scipy.optimize 函数列表
  (catalog 'scipy.optimize.minimize) → 函数详情
  (catalog \"最小二乘\")              → 搜索
"""

from typing import List, Optional, Dict, Any
from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value, _sym_name
import importlib, inspect


# ==================== 顶级目录 ====================

TOP_CATALOG = [
    ("scipy",        "scipy",        "科学计算: 优化/积分/信号/统计/稀疏矩阵/插值/FFT/图像"),
    ("statsmodels",  "statsmodels",  "统计建模: 回归/时间序列/假设检验/多元分析"),
    ("pandas",       "pandas",       "表格数据处理: DataFrame/CSV/聚合/透视表"),
    ("cvxpy",        "cvxpy",        "凸优化: LP/QP/SOCP/SDP 建模"),
    ("transformers", "transformers", "预训练模型: BERT/GPT/Llama/Mistral (HuggingFace)"),
    ("networkx",     "networkx",     "图与网络: 最短路/中心性/社区检测/图绘制"),
    ("numpy",        "numpy",        "核心数值计算: 数组/矩阵/随机数/线性代数"),
    ("sympy",        "sympy",        "符号数学: 微积分/代数/方程/ODE"),
    ("matplotlib",   "matplotlib",   "出版级绘图: 2D/3D/统计图"),
    ("scikit-learn", "sklearn",      "机器学习: 分类/回归/聚类/降维"),
    ("Pillow",       "PIL",          "图像处理: 打开/变换/滤镜"),
    ("opencv",       "cv2",          "计算机视觉: 摄像头/特征检测"),
    ("pint",         "pint",         "物理单位: 量纲分析/单位转换"),
    ("uncertainties","uncertainties","误差传播: 自动不确定度计算"),
    ("onnxruntime",  "onnxruntime",  "模型推理加速: ONNX Runtime"),
    ("sounddevice",  "sounddevice",  "音频录制/播放"),
    ("faster-whisper","faster_whisper","语音识别: OpenAI Whisper 加速版"),
    ("patsy",        "patsy",        "统计公式: R 风格 y ~ x1 + x2"),
    ("joblib",       "joblib",       "并行/缓存: 函数并行 + 结果缓存"),
    ("pydantic",     "pydantic",     "数据验证: 类型注解 + 校验"),
    ("SQLAlchemy",   "sqlalchemy",   "数据库 ORM"),
    ("beautifulsoup4","bs4",         "HTML/XML 解析"),
    ("lxml",         "lxml",         "高性能 XML/HTML 解析"),
    ("galois",       "galois",       "有限域: GF(2^n), GF(p)"),
    ("mpmath",       "mpmath",       "高精度浮点运算"),
    ("osqp",         "osqp",         "OSQP 二次规划求解器"),
    ("scs",          "scs",          "SCS 锥优化求解器"),
    ("highspy",      "highspy",      "HiGHS LP/MIP 求解器"),
]

# scipy 子模块重点函数
SCIPY_HIGHLIGHTS = {
    "optimize": [
        ("minimize",        "多变量函数优化 (Nelder-Mead, BFGS, SLSQP 等)"),
        ("minimize_scalar", "单变量函数优化"),
        ("least_squares",   "非线性最小二乘"),
        ("root",            "多变量方程求根"),
        ("root_scalar",     "单变量方程求根"),
        ("linear_sum_assignment", "线性分配/匈牙利算法"),
        ("curve_fit",       "曲线拟合"),
        ("differential_evolution", "差分进化全局优化"),
        ("basinhopping",    "盆地跳跃全局优化"),
        ("shgo",            "SHG 全局优化"),
        ("dual_annealing",  "双重模拟退火"),
        ("linprog",         "线性规划"),
        ("milp",            "混合整数线性规划"),
    ],
    "integrate": [
        ("quad",            "自适应数值积分 (1D)"),
        ("dblquad",         "二重积分"),
        ("tplquad",         "三重积分"),
        ("nquad",           "多重积分 (通用)"),
        ("odeint",          "常微分方程组求解"),
        ("solve_ivp",       "初值问题求解 (RK45, BDF 等)"),
        ("simpson",         "Simpson 法则数值积分"),
        ("cumulative_trapezoid", "累积梯形积分"),
        ("romb",            "Romberg 积分"),
    ],
    "stats": [
        ("norm",            "正态分布"),
        ("ttest_ind",       "独立样本 t 检验"),
        ("ttest_rel",       "配对样本 t 检验"),
        ("ttest_1samp",     "单样本 t 检验"),
        ("mannwhitneyu",    "Mann-Whitney U 检验"),
        ("wilcoxon",        "Wilcoxon 符号秩检验"),
        ("kruskal",         "Kruskal-Wallis H 检验"),
        ("pearsonr",        "Pearson 相关系数"),
        ("spearmanr",       "Spearman 秩相关"),
        ("chisquare",       "卡方检验"),
        ("f_oneway",        "单因素方差分析"),
        ("linregress",      "线性回归 (含统计量)"),
        ("describe",        "描述性统计"),
        ("gmean",           "几何平均"),
        ("hmean",           "调和平均"),
        ("mode",            "众数"),
        ("skew",            "偏度"),
        ("kurtosis",        "峰度"),
        ("zscore",          "Z 分数"),
        ("binom",           "二项分布"),
        ("poisson",         "泊松分布"),
        ("expon",           "指数分布"),
        ("uniform",         "均匀分布"),
        ("beta",            "Beta 分布"),
        ("gamma_dist",      "Gamma 分布"),
        ("chi2",            "卡方分布"),
        ("t",               "t 分布"),
        ("f",               "F 分布"),
    ],
    "linalg": [
        ("inv",             "矩阵求逆"),
        ("det",             "行列式"),
        ("solve",           "线性方程组求解 Ax=b"),
        ("lu",              "LU 分解"),
        ("qr",              "QR 分解"),
        ("svd",             "SVD 分解"),
        ("eig",             "特征值/特征向量 (一般矩阵)"),
        ("eigh",            "特征值/特征向量 (对称/Hermite)"),
        ("eigvals",         "仅特征值"),
        ("eigvalsh",        "仅特征值 (对称)"),
        ("cholesky",        "Cholesky 分解"),
        ("schur",           "Schur 分解"),
        ("norm",            "矩阵/向量范数"),
        ("cond",            "条件数"),
        ("expm",            "矩阵指数"),
        ("logm",            "矩阵对数"),
        ("sqrtm",           "矩阵平方根"),
        ("pinv",            "伪逆 (Moore-Penrose)"),
        ("lstsq",           "最小二乘解"),
    ],
    "signal": [
        ("convolve",        "卷积"),
        ("correlate",       "互相关"),
        ("fftconvolve",     "FFT 卷积"),
        ("firwin",          "FIR 滤波器设计 (窗口法)"),
        ("butter",          "Butterworth 滤波器"),
        ("cheby1",          "Chebyshev I 型滤波器"),
        ("ellip",           "椭圆滤波器"),
        ("filtfilt",        "零相位滤波"),
        ("lfilter",         "IIR/FIR 滤波"),
        ("spectrogram",     "频谱图"),
        ("welch",           "Welch 功率谱密度"),
        ("peak_widths",     "峰宽检测"),
        ("find_peaks",      "峰检测"),
        ("resample",        "重采样"),
        ("decimate",        "降采样"),
    ],
    "sparse": [
        ("csr_matrix",      "压缩稀疏行矩阵"),
        ("csc_matrix",      "压缩稀疏列矩阵"),
        ("coo_matrix",      "坐标格式稀疏矩阵"),
        ("eye",             "稀疏单位阵"),
        ("diags",           "稀疏对角矩阵"),
        ("hstack",          "水平堆叠"),
        ("vstack",          "垂直堆叠"),
        ("linalg.spsolve",  "稀疏线性方程组求解"),
        ("linalg.eigs",     "稀疏特征值 (部分)"),
        ("linalg.svds",     "稀疏 SVD (部分)"),
    ],
    "interpolate": [
        ("interp1d",        "1D 插值"),
        ("interp2d",        "2D 插值"),
        ("griddata",        "散点数据网格插值"),
        ("splrep",          "B 样条拟合"),
        ("splev",           "B 样条求值"),
        ("UnivariateSpline","一元样条"),
        ("RegularGridInterpolator", "规则网格插值"),
        ("RBFInterpolator", "径向基函数插值"),
    ],
    "fft": [
        ("fft",             "快速傅里叶变换"),
        ("ifft",            "逆 FFT"),
        ("fft2",            "2D FFT"),
        ("fftn",            "N 维 FFT"),
        ("rfft",            "实信号 FFT"),
        ("irfft",           "实信号逆 FFT"),
        ("fftfreq",         "FFT 频率"),
        ("fftshift",        "平移 FFT"),
    ],
    "ndimage": [
        ("gaussian_filter", "高斯滤波"),
        ("median_filter",   "中值滤波"),
        ("sobel",           "Sobel 边缘检测"),
        ("laplace",         "Laplace 边缘检测"),
        ("binary_opening",  "二值开运算"),
        ("binary_closing",  "二值闭运算"),
        ("label",           "连通区域标记"),
        ("center_of_mass",  "质心"),
        ("rotate",          "图像旋转"),
        ("zoom",            "图像缩放"),
        ("measurements",    "区域测量"),
    ],
}

# statsmodels 重点功能
STATSMODELS_HIGHLIGHTS = [
    ("OLS",              "普通最小二乘回归"),
    ("WLS",              "加权最小二乘回归"),
    ("GLM",              "广义线性模型"),
    ("Logit",            "Logit 回归 (二分类)"),
    ("Probit",           "Probit 回归"),
    ("Poisson",          "泊松回归"),
    ("NegativeBinomial", "负二项回归"),
    ("MixedLM",          "混合线性模型"),
    ("GEE",              "广义估计方程"),
    ("QuantReg",         "分位数回归"),
    ("tsa.ARIMA",        "ARIMA 时间序列"),
    ("tsa.SARIMAX",      "SARIMAX 时间序列"),
    ("tsa.stattools",    "时间序列统计工具 (ADF, KPSS, ACF, PACF)"),
    ("tsa.statespace",   "状态空间模型"),
    ("graphics",         "统计图形"),
    ("stats",            "统计检验 (JB, Durbin-Watson, Breusch-Pagan)"),
    ("robust",           "稳健统计"),
    ("duration",         "生存分析"),
    ("imputation",       "缺失值插补"),
    ("multivariate",     "多元分析 (因子分析, MANOVA)"),
    ("nonparametric",    "非参数统计 (KDE, kernel regression)"),
    ("discrete",         "离散选择模型"),
    ("regression",       "回归工具"),
]

# cvxpy 重点
CVXPY_HIGHLIGHTS = [
    ("Variable",    "优化变量"),
    ("Parameter",   "参数"),
    ("Problem",     "优化问题 (minimize/maximize + constraints)"),
    ("Minimize",    "最小化目标"),
    ("Maximize",    "最大化目标"),
    ("sum_squares", "平方和 (最小二乘)"),
    ("norm",        "范数 (L1, L2, Inf)"),
    ("quad_form",   "二次型"),
    ("abs",         "绝对值"),
    ("Maximum",     "逐元素最大值"),
    ("Minimum",     "逐元素最小值"),
    ("ExpCone",     "指数锥"),
    ("SOC",         "二阶锥"),
    ("PSD",         "半正定锥"),
]

# pandas 重点
PANDAS_HIGHLIGHTS = [
    ("read_csv",     "读取 CSV"),
    ("read_excel",   "读取 Excel"),
    ("read_sql",     "读取 SQL"),
    ("read_json",    "读取 JSON"),
    ("DataFrame",    "表格数据结构"),
    ("Series",       "一维序列"),
    ("df.head",     "前 N 行"),
    ("df.describe", "统计摘要"),
    ("df.groupby",  "分组聚合"),
    ("df.pivot_table", "透视表"),
    ("df.merge",    "合并 (类似 SQL JOIN)"),
    ("df.plot",     "绘图"),
    ("df.to_csv",   "写入 CSV"),
    ("df.to_excel", "写入 Excel"),
]

# transformers 重点
TRANSFORMERS_HIGHLIGHTS = [
    ("pipeline",     "一行加载 NLP/CV/音频模型"),
    ("AutoTokenizer","自动匹配分词器"),
    ("AutoModelForSequenceClassification", "文本分类"),
    ("AutoModelForTokenClassification",    "命名实体识别"),
    ("AutoModelForQuestionAnswering",      "问答"),
    ("AutoModelForCausalLM",    "自回归语言模型 (GPT/Llama)"),
    ("AutoModelForSeq2SeqLM",   "序列到序列 (T5/BART)"),
    ("AutoModelForMaskedLM",    "掩码语言模型 (BERT)"),
    ("Trainer",       "训练 API"),
    ("TrainingArguments", "训练参数配置"),
]

# patsy/joblib/sqlalchemy 重点
PATSY_HIGHLIGHTS = [
    ("dmatrices",    "从公式创建设计矩阵 (y ~ x1 + x2)"),
    ("dmatrix",      "创建设计矩阵"),
]
JOBLIB_HIGHLIGHTS = [
    ("Parallel",     "并行循环"),
    ("delayed",      "延迟执行"),
    ("dump",         "序列化到磁盘"),
    ("load",         "从磁盘加载"),
    ("Memory",       "函数结果缓存"),
]
SQLA_HIGHLIGHTS = [
    ("create_engine","创建数据库连接"),
    ("text",         "原生 SQL 查询"),
    ("Table",        "表定义"),
    ("session",      "会话管理"),
]


# ==================== 目录显示引擎 ====================

def _module_version(mod_name: str) -> str:
    try:
        mod = importlib.import_module(mod_name)
        return getattr(mod, '__version__', '?')
    except:
        return '?'


def _get_pkg_short(mod_name: str) -> Optional[str]:
    """获取可导入的模块名"""
    mapping = {
        'scipy': 'scipy', 'statsmodels': 'statsmodels',
        'pandas': 'pandas', 'cvxpy': 'cvxpy',
        'networkx': 'networkx', 'matplotlib': 'matplotlib',
        'Pillow': 'PIL', 'opencv': 'cv2', 'pint': 'pint',
        'uncertainties': 'uncertainties',
        'numpy': 'numpy', 'sympy': 'sympy', 'scikit-learn': 'sklearn',
    }
    return mapping.get(mod_name, mod_name)


def _try_import(name: str):
    """尝试导入模块"""
    try:
        return importlib.import_module(name)
    except:
        return None


# ==================== Top 级 ====================

def _show_top() -> str:
    lines = []
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append("║       Python 科学计算包目录                               ║")
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    lines.append("")
    
    # 按领域分组
    domains = [
        ("科学计算",     ["scipy", "numpy", "mpmath", "galois"]),
        ("统计/建模",    ["statsmodels", "patsy", "scikit-learn", "pandas"]),
        ("优化",         ["cvxpy", "osqp", "scs", "highspy", "ortools"]),
        ("符号数学",     ["sympy"]),
        ("NLP/ML",       ["transformers", "onnxruntime", "faster-whisper"]),
        ("绘图/视觉",    ["matplotlib", "Pillow", "opencv"]),
        ("图论",         ["networkx"]),
        ("物理/单位",    ["pint", "uncertainties"]),
        ("数据/工具",    ["SQLAlchemy", "beautifulsoup4", "lxml", "joblib", "pydantic", "sounddevice"]),
    ]
    
    for domain, pkgs in domains:
        lines.append(f"  ┌─ {domain} {'─' * (40 - len(domain))}┐")
        for pkg_name, mod_name, desc in TOP_CATALOG:
            import_name = _get_pkg_short(pkg_name) or mod_name
            mod = _try_import(import_name)
            if mod and any(pkg_name == p or pkg_name.startswith(p) for p in pkgs):
                ver = getattr(mod, '__version__', '?')
                lines.append(f"  │ 📦 {pkg_name:15s} v{str(ver):8s} {desc}")
        lines.append(f"  └{'─' * 48}┘")
        lines.append("")
    
    lines.append("  (catalog '包名)         → 查看子模块和核心函数")
    lines.append("  (catalog 'scipy.stats)  → 查看子模块函数")
    lines.append("  (catalog 'scipy.optimize.minimize) → 函数详情")
    lines.append("  (catalog \"关键词\")     → 搜索")
    return '\n'.join(lines)


# ==================== 包级 / 子模块级 ====================

def _show_module(modpath: str) -> Optional[str]:
    """显示模块内容"""
    # 先查 curated 目录
    parts = modpath.split('.')
    
    # scipy 子模块
    if len(parts) == 2 and parts[0] == 'scipy' and parts[1] in SCIPY_HIGHLIGHTS:
        lines = [f"  scipy.{parts[1]} 核心函数:"]
        lines.append(f"  {'─' * 55}")
        for fn_name, desc in SCIPY_HIGHLIGHTS[parts[1]]:
            lines.append(f"  • {fn_name:30s}  {desc}")
        lines.append(f"")
        lines.append(f"  (catalog 'scipy.{parts[1]}')  → 显示全部函数")
        return '\n'.join(lines)
    
    # scipy 顶级
    if modpath == 'scipy':
        lines = [f"  scipy v{_module_version('scipy')} 子模块:", ""]
        for sub, funcs in SCIPY_HIGHLIGHTS.items():
            lines.append(f"  📁 {sub:15s}  {funcs[0][1] if funcs else '...'}")
            for fn_name, desc in funcs[:4]:
                lines.append(f"       ├ {fn_name:28s} {desc}")
            lines.append(f"       └ (catalog 'scipy.{sub}') 查看全部")
            lines.append("")
        return '\n'.join(lines)
    
    # statsmodels
    if modpath == 'statsmodels':
        lines = [f"  statsmodels v{_module_version('statsmodels')}:", ""]
        for fn_name, desc in STATSMODELS_HIGHLIGHTS:
            lines.append(f"  • {fn_name:30s}  {desc}")
        return '\n'.join(lines)
    
    # cvxpy
    if modpath == 'cvxpy':
        lines = [f"  cvxpy v{_module_version('cvxpy')}:", ""]
        for fn_name, desc in CVXPY_HIGHLIGHTS:
            lines.append(f"  • {fn_name:30s}  {desc}")
        return '\n'.join(lines)
    
    # transformers
    if modpath == 'transformers':
        lines = [f"  transformers v{_module_version('transformers')}:", ""]
        lines.append("  ️ 注意: 需要 PyTorch 才能加载模型，否则仅可用分词器")
        lines.append("")
        for fn_name, desc in TRANSFORMERS_HIGHLIGHTS:
            lines.append(f"  • {fn_name:40s} {desc}")
        lines.append("")
        lines.append("  示例: (import transformers)")
        lines.append("        (define nlp (transformers.pipeline 'sentiment-analysis))")
        lines.append("        (nlp \"I love this!\" )")
        return '\n'.join(lines)
    
    # pandas
    if modpath == 'pandas':
        lines = [f"  pandas v{_module_version('pandas')}:", ""]
        for fn_name, desc in PANDAS_HIGHLIGHTS:
            lines.append(f"  • {fn_name:30s}  {desc}")
        return '\n'.join(lines)
    
    # 动态：尝试导入并列出公开内容
    mod = _try_import(modpath)
    if mod is not None:
        lines = [f"  {modpath} 公开接口:"]
        lines.append(f"  {'─' * 55}")
        classes = []; funcs = []; others = []
        for name in dir(mod):
            if name.startswith('_'):
                continue
            obj = getattr(mod, name)
            if isinstance(obj, type):
                classes.append(name)
            elif callable(obj):
                funcs.append(name)
            else:
                others.append(name)
        
        if classes:
            lines.append(f"  📦 类 ({len(classes)}):")
            for c in classes[:20]:
                lines.append(f"    • {c}")
            if len(classes) > 20:
                lines.append(f"    ... 及 {len(classes)-20} 个更多")
        if funcs:
            lines.append(f"  📋 函数 ({len(funcs)}):")
            for f in funcs[:30]:
                lines.append(f"    • {f}")
            if len(funcs) > 30:
                lines.append(f"    ... 及 {len(funcs)-30} 个更多")
        
        lines.append("")
        lines.append(f"  (describe {modpath}.xxx) 查看函数详情")
        return '\n'.join(lines)
    
    # 尝试找函数详情
    if '.' in modpath:
        parent = '.'.join(modpath.split('.')[:-1])
        func_name = modpath.split('.')[-1]
        mod = _try_import(parent)
        if mod and hasattr(mod, func_name):
            obj = getattr(mod, func_name)
            doc = inspect.getdoc(obj)
            lines = [f"── {modpath} ──", ""]
            if doc:
                for line in doc.split('\n'):
                    lines.append(f"  {line}")
            else:
                lines.append("  (无文档)")
            lines.append("")
            lines.append(f"  导入: (import {parent})")
            lines.append(f"  ({parent}.{func_name} ...)")
            return '\n'.join(lines)
    
    return None


# ==================== 搜索 ====================

def _search(keyword: str) -> str:
    kw = keyword.lower()
    results = []
    
    # 搜索 curated 目录
    all_curated = []
    for sub, funcs in SCIPY_HIGHLIGHTS.items():
        for fn_name, desc in funcs:
            all_curated.append((f"scipy.{sub}", fn_name, desc))
    for fn_name, desc in STATSMODELS_HIGHLIGHTS:
        all_curated.append(("statsmodels", fn_name, desc))
    for fn_name, desc in CVXPY_HIGHLIGHTS:
        all_curated.append(("cvxpy", fn_name, desc))
    for fn_name, desc in PANDAS_HIGHLIGHTS:
        all_curated.append(("pandas", fn_name, desc))
    for fn_name, desc in TRANSFORMERS_HIGHLIGHTS:
        all_curated.append(("transformers", fn_name, desc))
    for fn_name, desc in PATSY_HIGHLIGHTS:
        all_curated.append(("patsy", fn_name, desc))
    for fn_name, desc in JOBLIB_HIGHLIGHTS:
        all_curated.append(("joblib", fn_name, desc))
    for fn_name, desc in SQLA_HIGHLIGHTS:
        all_curated.append(("SQLAlchemy", fn_name, desc))
    
    for src, fn, desc in all_curated:
        if kw in fn.lower() or kw in desc.lower() or kw in src.lower():
            results.append((src, fn, desc))
    
    if not results:
        return f"未找到包含 '{keyword}' 的函数。"
    
    lines = [f"搜索 \"{keyword}\" 找到 {len(results)} 个结果：", ""]
    for src, fn, desc in results[:30]:
        lines.append(f"  • {fn:30s} [{src}]  {desc}")
    if len(results) > 30:
        lines.append(f"  ... 及 {len(results)-30} 个更多")
    return '\n'.join(lines)


# ==================== Scheme Prim ====================

def cas_catalog(args: List[SchemeValue]) -> SchemeValue:
    """
    (catalog)                    → 顶级分类目录
    (catalog 'scipy)             → scipy 子模块及核心函数
    (catalog 'scipy.optimize)    → scipy.optimize 函数列表
    (catalog 'scipy.optimize.minimize) → 函数详情
    (catalog "回归")             → 搜索
    """
    if len(args) == 0:
        return Str(list(_show_top()))
    
    first = args[0]
    if isinstance(first, Sym):
        path = first.name
        result = _show_module(path)
        if result is not None:
            return Str(list(result))
        return Str(list(f"模块 '{path}' 未找到。输入 (catalog) 浏览全部。"))
    
    if isinstance(first, Str):
        return Str(list(_search(first.get_str())))
    
    return Str(list("catalog: 参数应为包名(符号)、关键词(字符串)或空"))


# ==================== 注册 ====================

def register_catalog_primitives(env: 'Env') -> None:
    """注册目录系统 Prim"""
    env.define("catalog", Prim("catalog", cas_catalog))
