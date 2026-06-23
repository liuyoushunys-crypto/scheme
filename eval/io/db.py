"""
Database - Based on Python sqlite3 module.

Connection:
  (db-open path)                    -> open database connection
  (db-close conn)                   -> close connection
  (db-path conn)                    -> database file path

Execute:
  (db-exec conn sql)                -> execute SQL, return rows
  (db-exec conn sql params)         -> execute with parameters
  (db-execute conn sql)             -> execute (no return)
  (db-execute conn sql params)      -> execute with params

Query Convenience:
  (db-one conn sql)                 -> first column of first row
  (db-row conn sql)                 -> first row as alist
  (db-all conn sql)                 -> all rows as list of alists
  (db-col conn sql)                 -> first column as list
  (db-val conn sql)                 -> alias for db-one

DDL:
  (db-table? conn name)             -> check if table exists
  (db-tables conn)                  -> list table names
  (db-schema conn name)             -> table schema as alist
  (db-tables-info conn)             -> all table schemas

Transaction:
  (db-commit conn)                  -> commit transaction
  (db-rollback conn)                -> rollback transaction
  (db-autocommit conn bool)         -> set autocommit mode

Utility:
  (db-last-insert-id conn)          -> last inserted row id
  (db-changes conn)                 -> number of rows changed
  (db-driver-version)               -> sqlite3 version string

Row format:
  Rows returned as alists: ((column-name . value) ...)
  Parameters: ? or :name placeholders
"""
import sqlite3
import os
from typing import List, Optional
from dataclasses import dataclass

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


@dataclass
class DbConnection(SchemeValue):
    """SQLite database connection object"""
    conn: sqlite3.Connection
    path: str

    def __str__(self):
        return f"#<db \"{self.path}\">"


def _unwrap_str(val) -> str:
    if isinstance(val, Str):
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


def _scheme_to_sql(val: SchemeValue):
    """Convert Scheme value to SQL-friendly Python value"""
    if isinstance(val, Nil):
        return None
    if isinstance(val, Bool):
        return val.value
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        v = val.value
        return int(v) if isinstance(v, int) else v
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    if isinstance(val, Bytevector):
        return bytes(val.data)
    return str(val)


def _fetch_as_alist(cursor) -> list:
    """Fetch all rows as list of alists"""
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = []
    for row in cursor.fetchall():
        alist = Nil()
        for col, val in reversed(list(zip(columns, row))):
            sv = wrap_python_value(val)
            alist = Cons(Cons(Str(col), sv), alist)
        rows.append(alist)
    return rows


def _execute(db: sqlite3.Connection, sql: str, params: Optional[list] = None):
    """Execute SQL and return cursor"""
    if params:
        return db.execute(sql, params)
    return db.execute(sql)


# ==================== Connection ====================


def db_open(args: List[SchemeValue]) -> SchemeValue:
    """(db-open path) -> open database connection"""
    if len(args) < 1:
        raise Exception("db-open: need 1 argument (path)")
    path = _unwrap_str(args[0])
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return DbConnection(conn=conn, path=os.path.abspath(path))
    except Exception as e:
        raise Exception(f"Failed to open database: {e}")


def db_close(args: List[SchemeValue]) -> SchemeValue:
    """(db-close conn) -> close connection"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-close: need a database connection")
    try:
        args[0].conn.close()
        return Bool(True)
    except Exception as e:
        raise Exception(f"Failed to close database: {e}")


def db_path(args: List[SchemeValue]) -> SchemeValue:
    """(db-path conn) -> database file path"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-path: need a database connection")
    return Str(args[0].path)


# ==================== Execute ====================


def db_exec(args: List[SchemeValue]) -> SchemeValue:
    """(db-exec conn sql) or (db-exec conn sql param1 param2 ...)"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-exec: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            cursor = db.execute(sql, params)
        else:
            cursor = db.execute(sql)

        if cursor.description:
            rows = _fetch_as_alist(cursor)
            scheme_rows = Nil()
            for row in reversed(rows):
                scheme_rows = Cons(row, scheme_rows)
            return scheme_rows
        return Nil()
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


def db_execute(args: List[SchemeValue]) -> SchemeValue:
    """(db-execute conn sql) or (db-execute conn sql params...) -> no return"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-execute: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            db.execute(sql, params)
        else:
            db.execute(sql)
        return Bool(True)
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


# ==================== Query Convenience ====================


def db_one(args: List[SchemeValue]) -> SchemeValue:
    """(db-one conn sql) -> first column of first row"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-one: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            cursor = db.execute(sql, params)
        else:
            cursor = db.execute(sql)

        row = cursor.fetchone()
        if row:
            return wrap_python_value(row[0])
        return Bool(False)
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


def db_row(args: List[SchemeValue]) -> SchemeValue:
    """(db-row conn sql) -> first row as alist"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-row: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            cursor = db.execute(sql, params)
        else:
            cursor = db.execute(sql)

        rows = _fetch_as_alist(cursor)
        if rows:
            return rows[0]
        return Bool(False)
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


def db_all(args: List[SchemeValue]) -> SchemeValue:
    """(db-all conn sql) -> all rows as list of alists"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-all: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            cursor = db.execute(sql, params)
        else:
            cursor = db.execute(sql)

        rows = _fetch_as_alist(cursor)
        scheme_rows = Nil()
        for row in reversed(rows):
            scheme_rows = Cons(row, scheme_rows)
        return scheme_rows
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


def db_col(args: List[SchemeValue]) -> SchemeValue:
    """(db-col conn sql) -> first column as list"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-col: need connection and sql")
    db = args[0].conn
    sql = _unwrap_str(args[1])

    params = [_scheme_to_sql(a) for a in args[2:]] if len(args) > 2 else []

    try:
        if params:
            cursor = db.execute(sql, params)
        else:
            cursor = db.execute(sql)

        result = Nil()
        for row in reversed(cursor.fetchall()):
            result = Cons(wrap_python_value(row[0]), result)
        return result
    except Exception as e:
        raise Exception(f"SQL error: {e}\nSQL: {sql}")


def db_val(args: List[SchemeValue]) -> SchemeValue:
    """(db-val conn sql) -> alias for db-one"""
    return db_one(args)


# ==================== DDL ====================


def db_table_exists(args: List[SchemeValue]) -> SchemeValue:
    """(db-table? conn name) -> check if table exists"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-table?: need connection and table name")
    db = args[0].conn
    name = _unwrap_str(args[1])

    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,)
    )
    return Bool(cursor.fetchone() is not None)


def db_tables(args: List[SchemeValue]) -> SchemeValue:
    """(db-tables conn) -> list table names"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-tables: need a database connection")
    db = args[0].conn

    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    result = Nil()
    for row in reversed(cursor.fetchall()):
        result = Cons(Str(row[0]), result)
    return result


def db_schema(args: List[SchemeValue]) -> SchemeValue:
    """(db-schema conn name) -> table schema as alist"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-schema: need connection and table name")
    db = args[0].conn
    name = _unwrap_str(args[1])

    cursor = db.execute(f"PRAGMA table_info({name})")
    rows = cursor.fetchall()

    result = Nil()
    for row in reversed(rows):
        info = _cons_alist([
            (Sym("cid"), Num(row[0])),
            (Sym("name"), Str(row[1])),
            (Sym("type"), Str(row[2])),
            (Sym("notnull"), Bool(bool(row[3]))),
            (Sym("default"), wrap_python_value(row[4])),
            (Sym("pk"), Bool(bool(row[5]))),
        ])
        result = Cons(info, result)
    return result


def db_tables_info(args: List[SchemeValue]) -> SchemeValue:
    """(db-tables-info conn) -> all table schemas"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-tables-info: need a database connection")
    db = args[0].conn

    tables_val = db_tables(args)
    result = Nil()
    c = tables_val
    while isinstance(c, Cons):
        name = _unwrap_str(c.car)
        schema = db_schema([args[0], Str(name)])
        result = Cons(Cons(Str(name), schema), result)
        c = c.cdr
    return result


# ==================== Transaction ====================


def db_commit(args: List[SchemeValue]) -> SchemeValue:
    """(db-commit conn) -> commit transaction"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-commit: need a database connection")
    args[0].conn.commit()
    return Bool(True)


def db_rollback(args: List[SchemeValue]) -> SchemeValue:
    """(db-rollback conn) -> rollback transaction"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-rollback: need a database connection")
    args[0].conn.rollback()
    return Bool(True)


def db_autocommit(args: List[SchemeValue]) -> SchemeValue:
    """(db-autocommit conn bool) -> set autocommit mode"""
    if len(args) < 2 or not isinstance(args[0], DbConnection):
        raise Exception("db-autocommit: need connection and boolean")
    db = args[0].conn
    if isinstance(args[1], Bool):
        db.isolation_level = None if args[1].value else ""
    else:
        raise Exception("db-autocommit: second argument must be boolean")
    return Bool(True)


# ==================== Utility ====================


def db_last_insert_id(args: List[SchemeValue]) -> SchemeValue:
    """(db-last-insert-id conn) -> last inserted row id"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-last-insert-id: need a database connection")
    cursor = args[0].conn.execute("SELECT last_insert_rowid()")
    return Num(cursor.fetchone()[0])


def db_changes(args: List[SchemeValue]) -> SchemeValue:
    """(db-changes conn) -> number of rows changed"""
    if len(args) < 1 or not isinstance(args[0], DbConnection):
        raise Exception("db-changes: need a database connection")
    cursor = args[0].conn.execute("SELECT changes()")
    return Num(cursor.fetchone()[0])


def db_driver_version(args: List[SchemeValue]) -> SchemeValue:
    """(db-driver-version) -> sqlite3 version string"""
    return Str(sqlite3.sqlite_version)


# ==================== Helpers ====================


def _cons_alist(pairs: list) -> SchemeValue:
    result = Nil()
    for k, v in reversed(pairs):
        result = Cons(Cons(k, v), result)
    return result


# ==================== Registration ====================


def register_db_primitives(env):
    env.define("db-open", Prim("db-open", db_open))
    env.define("db-close", Prim("db-close", db_close))
    env.define("db-path", Prim("db-path", db_path))

    env.define("db-exec", Prim("db-exec", db_exec))
    env.define("db-execute", Prim("db-execute", db_execute))

    env.define("db-one", Prim("db-one", db_one))
    env.define("db-row", Prim("db-row", db_row))
    env.define("db-all", Prim("db-all", db_all))
    env.define("db-col", Prim("db-col", db_col))
    env.define("db-val", Prim("db-val", db_val))

    env.define("db-table?", Prim("db-table?", db_table_exists))
    env.define("db-tables", Prim("db-tables", db_tables))
    env.define("db-schema", Prim("db-schema", db_schema))
    env.define("db-tables-info", Prim("db-tables-info", db_tables_info))

    env.define("db-commit", Prim("db-commit", db_commit))
    env.define("db-rollback", Prim("db-rollback", db_rollback))
    env.define("db-autocommit", Prim("db-autocommit", db_autocommit))

    env.define("db-last-insert-id", Prim("db-last-insert-id", db_last_insert_id))
    env.define("db-changes", Prim("db-changes", db_changes))
    env.define("db-driver-version", Prim("db-driver-version", db_driver_version))