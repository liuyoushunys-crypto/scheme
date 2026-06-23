"""
info -- aggregator
"""

from .help import register_primitives as register_help
from .nav import register_primitives as register_nav

def register_info_primitives(env):
    register_help(env)
    register_nav(env)

