"""
Regular Expression Support - Based on Python re module.

First-class citizen features:
  - Regex pattern objects can be passed as values
  - Match objects support group extraction
  - Scheme strings integrate seamlessly with regex

Basic functions:
  (re-match pattern string)      -> match object or #f
  (re-search pattern string)     -> match object or #f  
  (re-findall pattern string)    -> list of matched strings
  (re-split pattern string)      -> list of split strings
  (re-sub pattern repl string)   -> replaced string
  (re-subn pattern repl string)  -> (replaced-string . count)

Compile and reuse:
  (re-compile pattern)           -> compiled regex object
  (re-match-obj regex string)    -> match using compiled regex
  (re-search-obj regex string)   -> search using compiled regex

Match object operations:
  (re-group match)               -> entire match
  (re-group match 1)             -> first capture group
  (re-groups match)              -> list of all capture groups
  (re-start match)               -> match start position
  (re-end match)                 -> match end position
  (re-span match)                -> (start . end)

Advanced features:
  (re-escape string)             -> escape special chars
  (re-pattern match)             -> get original pattern
"""

import re
from typing import List, Optional, Union
from dataclasses import dataclass

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


@dataclass(frozen=True, slots=True)
class RegexObject(SchemeValue):
    """Compiled regular expression object"""
    pattern: str
    compiled: 're.Pattern'
    
    def __str__(self):
        return f"#<regex \"{self.pattern}\">"


@dataclass(frozen=True, slots=True)
class MatchObject(SchemeValue):
    """Regular expression match result object"""
    match: 're.Match'
    string: str
    
    def __str__(self):
        return f"#<match \"{self.match.group()}\">"


def _unwrap_string(val: SchemeValue) -> str:
    """Extract Python string from Scheme value, converting Scheme \\ to Python \\"""
    if isinstance(val, Str):
        s = val.get_str()
        # Convert Scheme \\ to Python \
        return s.replace("\\\\", "\\")
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _get_pattern(val: SchemeValue) -> Union[str, 're.Pattern']:
    """Get pattern (string or compiled object), handle Scheme escapes"""
    if isinstance(val, RegexObject):
        return val.compiled
    if isinstance(val, Str):
        s = val.get_str()
        # Convert Scheme \\ to Python \
        return s.replace("\\\\", "\\")
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string or regex, got {type(val).__name__}")


def re_match(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-match pattern string) -> match object or #f
    Match pattern from beginning of string.
    """
    if len(args) < 2:
        raise Exception("re-match: need 2 arguments (pattern string)")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    
    result = re.match(pattern, string)
    if result:
        return MatchObject(match=result, string=string)
    return Bool(False)


def re_search(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-search pattern string) -> match object or #f
    Search for pattern anywhere in string.
    """
    if len(args) < 2:
        raise Exception("re-search: need 2 arguments (pattern string)")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    
    result = re.search(pattern, string)
    if result:
        return MatchObject(match=result, string=string)
    return Bool(False)


def re_findall(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-findall pattern string) -> list of matched strings
    Return all non-overlapping matches.
    """
    if len(args) < 2:
        raise Exception("re-findall: need 2 arguments (pattern string)")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    
    results = re.findall(pattern, string)
    
    # Convert to Scheme list
    scheme_results = Nil()
    for r in reversed(results):
        if isinstance(r, tuple):
            # Multiple groups, convert to Scheme list
            group_items = Nil()
            for item in reversed(r):
                group_items = Cons(Str(str(item)), group_items)
            scheme_results = Cons(group_items, scheme_results)
        else:
            scheme_results = Cons(Str(str(r)), scheme_results)
    
    return scheme_results


def re_split(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-split pattern string) -> list of split strings
    (re-split pattern string maxsplit) -> limit split count
    """
    if len(args) < 2:
        raise Exception("re-split: need at least 2 arguments")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    maxsplit = 0
    if len(args) > 2:
        maxsplit = int(unwrap_python_value(args[2]))
    
    results = re.split(pattern, string, maxsplit=maxsplit)
    
    # Convert to Scheme list
    scheme_results = Nil()
    for r in reversed(results):
        scheme_results = Cons(Str(r), scheme_results)
    
    return scheme_results


def re_sub(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-sub pattern repl string) -> replaced string
    (re-sub pattern repl string count) -> limit replacement count
    """
    if len(args) < 3:
        raise Exception("re-sub: need at least 3 arguments (pattern repl string)")
    
    pattern = _get_pattern(args[0])
    repl = _unwrap_string(args[1])
    string = _unwrap_string(args[2])
    count = 0
    if len(args) > 3:
        count = int(unwrap_python_value(args[3]))
    
    result = re.sub(pattern, repl, string, count=count)
    return Str(result)


def re_subn(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-subn pattern repl string) -> (replaced-string . count)
    Return replacement result and count.
    """
    if len(args) < 3:
        raise Exception("re-subn: need at least 3 arguments")
    
    pattern = _get_pattern(args[0])
    repl = _unwrap_string(args[1])
    string = _unwrap_string(args[2])
    count = 0
    if len(args) > 3:
        count = int(unwrap_python_value(args[3]))
    
    result, num = re.subn(pattern, repl, string, count=count)
    # Return cons: (result . num)
    return Cons(Str(result), Num(num))


def re_compile(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-compile pattern) -> compiled regex object
    (re-compile pattern flags) -> compile with flags
    
    flags: 'i (ignorecase), 'm (multiline), 's (dotall), 'x (verbose)
    """
    if len(args) < 1:
        raise Exception("re-compile: need at least 1 argument (pattern)")
    
    pattern = _unwrap_string(args[0])
    
    flags = 0
    if len(args) > 1:
        # Parse flags
        flag_arg = args[1]
        if isinstance(flag_arg, Sym):
            flag_names = flag_arg.name.split('|')
            for name in flag_names:
                if name == 'i' or name == 'ignorecase':
                    flags |= re.IGNORECASE
                elif name == 'm' or name == 'multiline':
                    flags |= re.MULTILINE
                elif name == 's' or name == 'dotall':
                    flags |= re.DOTALL
                elif name == 'x' or name == 'verbose':
                    flags |= re.VERBOSE
                elif name == 'a' or name == 'ascii':
                    flags |= re.ASCII
                elif name == 'u' or name == 'unicode':
                    flags |= re.UNICODE
                elif name == 'l' or name == 'locale':
                    flags |= re.LOCALE
        elif isinstance(flag_arg, Num):
            flags = int(flag_arg.value)
    
    compiled = re.compile(pattern, flags)
    return RegexObject(pattern=pattern, compiled=compiled)


def re_match_obj(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-match-obj compiled-regex string) -> match object or #f
    Match using compiled regex.
    """
    if len(args) < 2:
        raise Exception("re-match-obj: need 2 arguments (regex string)")
    
    if not isinstance(args[0], RegexObject):
        raise Exception("re-match-obj: first argument must be compiled regex")
    
    string = _unwrap_string(args[1])
    result = args[0].compiled.match(string)
    
    if result:
        return MatchObject(match=result, string=string)
    return Bool(False)


def re_search_obj(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-search-obj compiled-regex string) -> match object or #f
    Search using compiled regex.
    """
    if len(args) < 2:
        raise Exception("re-search-obj: need 2 arguments (regex string)")
    
    if not isinstance(args[0], RegexObject):
        raise Exception("re-search-obj: first argument must be compiled regex")
    
    string = _unwrap_string(args[1])
    result = args[0].compiled.search(string)
    
    if result:
        return MatchObject(match=result, string=string)
    return Bool(False)


def re_findall_obj(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-findall-obj compiled-regex string) -> list of matches
    """
    if len(args) < 2:
        raise Exception("re-findall-obj: need 2 arguments")
    
    if not isinstance(args[0], RegexObject):
        raise Exception("re-findall-obj: first argument must be compiled regex")
    
    string = _unwrap_string(args[1])
    results = args[0].compiled.findall(string)
    
    scheme_results = Nil()
    for r in reversed(results):
        if isinstance(r, tuple):
            group_items = Nil()
            for item in reversed(r):
                group_items = Cons(Str(str(item)), group_items)
            scheme_results = Cons(group_items, scheme_results)
        else:
            scheme_results = Cons(Str(str(r)), scheme_results)
    
    return scheme_results


def re_group(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-group match) -> entire match string
    (re-group match n) -> nth capture group (0=entire match)
    """
    if len(args) < 1:
        raise Exception("re-group: need at least 1 argument (match object)")
    
    if not isinstance(args[0], MatchObject):
        raise Exception("re-group: argument must be match object")
    
    match = args[0].match
    
    if len(args) == 1:
        # Return entire match
        return Str(match.group())
    else:
        # Return specified group
        group_num = int(unwrap_python_value(args[1]))
        try:
            result = match.group(group_num)
            return Str(result) if result is not None else Nil()
        except IndexError:
            return Nil()


def re_groups(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-groups match) -> list of all capture groups (excluding group 0)
    """
    if len(args) < 1:
        raise Exception("re-groups: need 1 argument (match object)")
    
    if not isinstance(args[0], MatchObject):
        raise Exception("re-groups: argument must be match object")
    
    groups = args[0].match.groups()
    
    scheme_groups = Nil()
    for g in reversed(groups):
        scheme_groups = Cons(Str(g) if g is not None else Nil(), scheme_groups)
    
    return scheme_groups


def re_start(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-start match) -> entire match start position
    (re-start match n) -> nth group start position
    """
    if len(args) < 1:
        raise Exception("re-start: need at least 1 argument")
    
    if not isinstance(args[0], MatchObject):
        raise Exception("re-start: argument must be match object")
    
    match = args[0].match
    group_num = 0
    if len(args) > 1:
        group_num = int(unwrap_python_value(args[1]))
    
    return Num(match.start(group_num))


def re_end(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-end match) -> entire match end position
    (re-end match n) -> nth group end position
    """
    if len(args) < 1:
        raise Exception("re-end: need at least 1 argument")
    
    if not isinstance(args[0], MatchObject):
        raise Exception("re-end: argument must be match object")
    
    match = args[0].match
    group_num = 0
    if len(args) > 1:
        group_num = int(unwrap_python_value(args[1]))
    
    return Num(match.end(group_num))


def re_span(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-span match) -> (start . end) pair
    (re-span match n) -> nth group's pair
    """
    if len(args) < 1:
        raise Exception("re-span: need at least 1 argument")
    
    if not isinstance(args[0], MatchObject):
        raise Exception("re-span: argument must be match object")
    
    match = args[0].match
    group_num = 0
    if len(args) > 1:
        group_num = int(unwrap_python_value(args[1]))
    
    start, end = match.span(group_num)
    return Cons(Num(start), Num(end))


def re_pattern(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-pattern match) -> original regex pattern string
    (re-pattern compiled-regex) -> original pattern
    """
    if len(args) < 1:
        raise Exception("re-pattern: need 1 argument")
    
    arg = args[0]
    if isinstance(arg, MatchObject):
        return Str(arg.match.re.pattern)
    elif isinstance(arg, RegexObject):
        return Str(arg.pattern)
    else:
        raise Exception("re-pattern: argument must be match or compiled regex")


def re_escape(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-escape string) -> escaped string
    Escape special regex characters.
    """
    if len(args) < 1:
        raise Exception("re-escape: need 1 argument")
    
    string = _unwrap_string(args[0])
    return Str(re.escape(string))


def re_fullmatch(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-fullmatch pattern string) -> match object or #f
    Entire string must match pattern.
    """
    if len(args) < 2:
        raise Exception("re-fullmatch: need 2 arguments")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    
    result = re.fullmatch(pattern, string)
    if result:
        return MatchObject(match=result, string=string)
    return Bool(False)


def re_finditer(args: List[SchemeValue]) -> SchemeValue:
    """
    (re-finditer pattern string) -> list of match objects
    Return all matches as MatchObject list.
    """
    if len(args) < 2:
        raise Exception("re-finditer: need 2 arguments")
    
    pattern = _get_pattern(args[0])
    string = _unwrap_string(args[1])
    
    results = list(re.finditer(pattern, string))
    
    scheme_results = Nil()
    for r in reversed(results):
        scheme_results = Cons(MatchObject(match=r, string=string), scheme_results)
    
    return scheme_results


def register_re_primitives(env):
    """Register all regex-related primitives"""
    env.define("re-match", Prim("re-match", re_match))
    env.define("re-search", Prim("re-search", re_search))
    env.define("re-findall", Prim("re-findall", re_findall))
    env.define("re-split", Prim("re-split", re_split))
    env.define("re-sub", Prim("re-sub", re_sub))
    env.define("re-subn", Prim("re-subn", re_subn))
    env.define("re-fullmatch", Prim("re-fullmatch", re_fullmatch))
    env.define("re-finditer", Prim("re-finditer", re_finditer))
    
    env.define("re-compile", Prim("re-compile", re_compile))
    env.define("re-match-obj", Prim("re-match-obj", re_match_obj))
    env.define("re-search-obj", Prim("re-search-obj", re_search_obj))
    env.define("re-findall-obj", Prim("re-findall-obj", re_findall_obj))
    
    env.define("re-group", Prim("re-group", re_group))
    env.define("re-groups", Prim("re-groups", re_groups))
    env.define("re-start", Prim("re-start", re_start))
    env.define("re-end", Prim("re-end", re_end))
    env.define("re-span", Prim("re-span", re_span))
    env.define("re-pattern", Prim("re-pattern", re_pattern))
    
    env.define("re-escape", Prim("re-escape", re_escape))
