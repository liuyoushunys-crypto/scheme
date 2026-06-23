import sys
from typing import List, Optional

registering_env = None
exception_handlers: List['SchemeValue'] = []
gensym_counter = 0
