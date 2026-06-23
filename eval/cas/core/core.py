"""
core -- aggregator
"""

from .algebra import register_primitives as register_algebra
from .calculus import register_primitives as register_calculus
from .linear import register_primitives as register_linear
from .output import register_primitives as register_output
from .special import register_primitives as register_special

def register_core_primitives(env):
    register_algebra(env)
    register_calculus(env)
    register_linear(env)
    register_output(env)
    register_special(env)

