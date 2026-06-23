"""
bridge — 图/数组/单位封装

依赖: networkx (可选), numpy (可选), pint (可选)
"""
from core.schemevalue import Prim, Str


def graph_create(*args):
    """创建空 Graph"""
    return Str(f"<Graph {' '.join(str(a) for a in args)}>")


def digraph_create(*args):
    """创建有向图"""
    return Str(f"<DiGraph {' '.join(str(a) for a in args)}>")


def multigraph_create(*args):
    """创建多重图"""
    return Str(f"<MultiGraph>")


def make_array(*args):
    """创建数组"""
    import numpy as np
    return np.array([a.value if hasattr(a, 'value') else a for a in args])


def convert_to(val, target):
    """格式转换"""
    return Str(f"<convert {val} to {target}>")


def array_wrapper(*args):
    """Array 封装"""
    import numpy as np
    return np.array([a.value if hasattr(a, 'value') else a for a in args])


def tensor_product(*args):
    """张量积"""
    return Str(f"<tensor-product>")


def tensor_contraction(*args):
    """张量缩并"""
    return Str(f"<tensor-contraction>")


def use_graph(backend):
    """切换到指定图后端"""
    return Str(f"<use-graph {backend}>")


def use_tensor(backend):
    """切换到指定张量后端"""
    return Str(f"<use-tensor {backend}>")


def use_units(backend):
    """切换到指定单位后端"""
    return Str(f"<use-units {backend}>")


def register_bridge_primitives(env):
    """Register bridge primitives."""
    env.define("Graph", Prim("Graph", graph_create))
    env.define("DiGraph", Prim("DiGraph", digraph_create))
    env.define("MultiGraph", Prim("MultiGraph", multigraph_create))
    env.define("make-array", Prim("make-array", make_array))
    env.define("convert-to", Prim("convert-to", convert_to))
    env.define("Array", Prim("Array", array_wrapper))
    env.define("tensor-product", Prim("tensor-product", tensor_product))
    env.define("tensor-contraction", Prim("tensor-contraction", tensor_contraction))
    env.define("use-graph", Prim("use-graph", use_graph))
    env.define("use-tensor", Prim("use-tensor", use_tensor))
    env.define("use-units", Prim("use-units", use_units))


register_primitives = register_bridge_primitives