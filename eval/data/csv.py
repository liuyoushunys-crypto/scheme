"""
CSV Processing - Based on Python csv module.

Reading:
  (csv-read path)                  -> list of rows (first row = headers)
  (csv-read path 'no-header)       -> list of rows (no header assumption)
  (csv-read path 'no-header sep)   -> custom delimiter
  (csv-rows path)                  -> list of HashTable rows (keyed by header)
  (csv-rows path sep)              -> with custom delimiter

Writing:
  (csv-write path rows)            -> write rows to CSV
  (csv-write path rows sep)        -> write with custom delimiter
  (csv-dump rows)                  -> return CSV string

Utility:
  (csv-headers path)               -> get header row only
  (csv-count path)                 -> count data rows
  (csv-col path col)               -> extract a column as list

Options:
  'comma   = comma separated (default)
  'tab     = tab separated
  'semicolon = semicolon separated
  'pipe    = pipe separated
"""
import csv
import io
from typing import List
from pathlib import Path

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


def _unwrap_str(val) -> str:
    if isinstance(val, (Str,)):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_int(val) -> int:
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        return int(val.value)
    return int(unwrap_python_value(val))


_SEP_MAP = {
    'comma': ',',
    'tab': '\t',
    'tabs': '\t',
    'semicolon': ';',
    'pipe': '|',
    'space': ' ',
}


def _get_delimiter(args, start_idx=1):
    """Extract delimiter from args, return (delimiter, next_idx, no_header)"""
    delim = ','
    no_header = False
    idx = start_idx
    while idx < len(args):
        arg = args[idx]
        if isinstance(arg, Bool) and not arg.value:
            no_header = True
        elif isinstance(arg, Sym):
            name = arg.name.lower()
            if name == 'no-header':
                no_header = True
            elif name in _SEP_MAP:
                delim = _SEP_MAP[name]
            else:
                raise Exception(f"Unknown CSV option: {name}")
        elif isinstance(arg, Str):
            s = arg.get_str().lower()
            if s in _SEP_MAP:
                delim = _SEP_MAP[s]
            else:
                delim = s
        else:
            # Assume it's a delimiter char
            delim = str(arg)
        idx += 1
    return delim, idx, no_header


def _read_all(path: str, delim: str, no_header: bool) -> list:
    """Read CSV file and return list of rows"""
    rows = []
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=delim)
        for row in reader:
            rows.append(row)
    return rows


def _rows_to_scheme(rows, no_header: bool) -> SchemeValue:
    """Convert list of rows to Scheme list of lists"""
    result = Nil()
    for row in reversed(rows):
        scheme_row = Nil()
        for cell in reversed(row):
            scheme_row = Cons(Str(cell), scheme_row)
        result = Cons(scheme_row, result)
    return result


def _rows_to_hashtables(rows, no_header: bool) -> SchemeValue:
    """Convert rows to list of HashTables keyed by header"""
    if not rows:
        return Nil()
    if no_header:
        headers = [f"col{i}" for i in range(len(rows[0]))]
        data_rows = rows
    else:
        headers = rows[0]
        data_rows = rows[1:]

    result = Nil()
    for row in reversed(data_rows):
        ht = HashTable(table={})
        for i, cell in enumerate(row):
            h = headers[i] if i < len(headers) else f"col{i}"
            ht.table[h] = Str(cell)
        result = Cons(ht, result)
    return result


# ==================== Reading ====================


def csv_read(args: List[SchemeValue]) -> SchemeValue:
    """(csv-read path) or (csv-read path 'no-header) or (csv-read path 'no-header 'tab)"""
    if len(args) < 1:
        raise Exception("csv-read: need at least 1 argument (path)")
    path = _unwrap_str(args[0])
    delim, _, no_header = _get_delimiter(args, 1)
    rows = _read_all(path, delim, no_header)
    return _rows_to_scheme(rows, no_header)


def csv_rows(args: List[SchemeValue]) -> SchemeValue:
    """(csv-rows path) -> list of HashTable rows keyed by header"""
    if len(args) < 1:
        raise Exception("csv-rows: need at least 1 argument (path)")
    path = _unwrap_str(args[0])
    delim, _, no_header = _get_delimiter(args, 1)
    rows = _read_all(path, delim, no_header)
    return _rows_to_hashtables(rows, no_header)


# ==================== Writing ====================


def csv_write(args: List[SchemeValue]) -> SchemeValue:
    """(csv-write path rows) or (csv-write path rows 'tab)"""
    if len(args) < 2:
        raise Exception("csv-write: need at least 2 arguments (path rows)")
    path = _unwrap_str(args[0])
    rows_val = args[1]
    delim, _, _ = _get_delimiter(args, 2)

    # Convert Scheme list of lists to Python rows
    py_rows = []
    current = rows_val
    while isinstance(current, Cons):
        row = current.car
        py_row = []
        r = row
        while isinstance(r, Cons):
            py_row.append(_unwrap_str(r.car))
            r = r.cdr
        py_rows.append(py_row)
        current = current.cdr

    with open(path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=delim)
        for py_row in py_rows:
            writer.writerow(py_row)

    return Bool(True)


def csv_dump(args: List[SchemeValue]) -> SchemeValue:
    """(csv-dump rows) -> return CSV string"""
    if len(args) < 1:
        raise Exception("csv-dump: need at least 1 argument (rows)")
    rows_val = args[0]
    delim = ','
    if len(args) > 1:
        delim, _, _ = _get_delimiter(args, 1)

    # Convert rows
    py_rows = []
    current = rows_val
    while isinstance(current, Cons):
        row = current.car
        py_row = []
        r = row
        while isinstance(r, Cons):
            py_row.append(_unwrap_str(r.car))
            r = r.cdr
        py_rows.append(py_row)
        current = current.cdr

    output = io.StringIO()
    writer = csv.writer(output, delimiter=delim)
    for py_row in py_rows:
        writer.writerow(py_row)

    return Str(output.getvalue().rstrip('\n'))


# ==================== Utility ====================


def csv_headers(args: List[SchemeValue]) -> SchemeValue:
    """(csv-headers path) -> header row"""
    if len(args) < 1:
        raise Exception("csv-headers: need 1 argument (path)")
    path = _unwrap_str(args[0])
    delim, _, _ = _get_delimiter(args, 1)
    rows = _read_all(path, delim, False)
    if not rows:
        return Nil()
    headers = rows[0]
    result = Nil()
    for h in reversed(headers):
        result = Cons(Str(h), result)
    return result


def csv_count(args: List[SchemeValue]) -> SchemeValue:
    """(csv-count path) -> count data rows (excluding header)"""
    if len(args) < 1:
        raise Exception("csv-count: need 1 argument (path)")
    path = _unwrap_str(args[0])
    delim, _, _ = _get_delimiter(args, 1)
    rows = _read_all(path, delim, False)
    count = max(0, len(rows) - 1)
    return Num(count)


def csv_col(args: List[SchemeValue]) -> SchemeValue:
    """(csv-col path col) -> extract a column as list"""
    if len(args) < 2:
        raise Exception("csv-col: need 2 arguments (path col)")
    path = _unwrap_str(args[0])
    col_val = args[1]
    delim, _, _ = _get_delimiter(args, 2)

    rows = _read_all(path, delim, True)
    if not rows:
        return Nil()

    # Determine column index
    if isinstance(col_val, Num):
        col_idx = int(col_val.value)
    elif isinstance(col_val, Integer):
        col_idx = col_val.value
    elif isinstance(col_val, (Str, Sym)):
        col_name = _unwrap_str(col_val)
        if not rows:
            return Nil()
        headers = rows[0]
        try:
            col_idx = headers.index(col_name)
        except ValueError:
            raise Exception(f"Column not found: {col_name}")
        rows = rows[1:]  # Skip header row
    else:
        col_idx = int(unwrap_python_value(col_val))

    result = Nil()
    for row in reversed(rows):
        if col_idx < len(row):
            result = Cons(Str(row[col_idx]), result)
        else:
            result = Cons(Str(""), result)

    return result


# ==================== Registration ====================


def register_csv_primitives(env):
    env.define("csv-read", Prim("csv-read", csv_read))
    env.define("csv-rows", Prim("csv-rows", csv_rows))
    env.define("csv-write", Prim("csv-write", csv_write))
    env.define("csv-dump", Prim("csv-dump", csv_dump))
    env.define("csv-headers", Prim("csv-headers", csv_headers))
    env.define("csv-count", Prim("csv-count", csv_count))
    env.define("csv-col", Prim("csv-col", csv_col))