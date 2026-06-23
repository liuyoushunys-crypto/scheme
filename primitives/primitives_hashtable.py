from typing import List
from core.schemevalue import *
from core.tail_call import apply


def prim_make_hash_table(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 0:
        raise Exception("make-hash-table: arity mismatch")
    return HashTable({})


def prim_hash_table_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("hash-table?: arity mismatch")
    return Bool(isinstance(args[0], HashTable))


def prim_hash_table_set_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 3:
        raise Exception("hash-table-set!: arity mismatch")
    ht, key, val = args
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-set!: first argument must be a hash-table")
    ht.table[key] = val
    return Sym("undefined")


def prim_hash_table_delete_bang(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("hash-table-delete!: arity mismatch")
    ht, key = args
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-delete!: first argument must be a hash-table")
    ht.table.pop(key, None)
    return Sym("undefined")


def prim_hash_table_contains_p(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("hash-table-contains?: arity mismatch")
    ht, key = args
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-contains?: first argument must be a hash-table")
    return Bool(key in ht.table)


def prim_hash_table_keys(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("hash-table-keys: arity mismatch")
    ht = args[0]
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-keys: argument must be a hash-table")
    return to_lisp_list(list(ht.table.keys()))


def prim_hash_table_values(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1:
        raise Exception("hash-table-values: arity mismatch")
    ht = args[0]
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-values: argument must be a hash-table")
    return to_lisp_list(list(ht.table.values()))


def prim_hash_table_to_alist(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 1 or not isinstance(args[0], HashTable):
        raise Exception("hash-table->alist: expected a hash-table")
    ht = args[0]
    pairs = [Cons(k, v) for k, v in ht.table.items()]
    return to_lisp_list(pairs)


import primitives.primitives_shared as _shared


def prim_hash_table_map(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("hash-table-map: arity mismatch")
    proc, ht = args
    if not isinstance(ht, HashTable):
        raise Exception("hash-table-map: second argument must be a hash-table")
    res = []
    for k, v in ht.table.items():
        res.append(apply(proc, [k, v], _shared.registering_env))
    return to_lisp_list(res)


def prim_hash_table_for_each(args: List[SchemeValue]) -> SchemeValue:
    if len(args) != 2:
        raise Exception("hash-for-each: arity mismatch")
    if isinstance(args[0], HashTable):
        ht, proc = args[0], args[1]
    else:
        proc, ht = args[0], args[1]
    if not isinstance(ht, HashTable):
        raise Exception("hash-for-each: expected a hash-table")
    for k, v in ht.table.items():
        apply(proc, [k, v], _shared.registering_env)
    return Sym("undefined")


def prim_hash_table_ref(args: List[SchemeValue]) -> SchemeValue:
    if not (2 <= len(args) <= 3):
        raise Exception("hash-ref: arity mismatch")
    ht, key = args[0], args[1]
    if not isinstance(ht, HashTable):
        raise Exception("hash-ref: first argument must be a hash-table")
    if key in ht.table:
        return ht.table[key]
    if len(args) == 3:
        default = args[2]
        if isinstance(default, (Closure, Prim)):
            return apply(default, [], _shared.registering_env)
        return default
    raise Exception("hash-ref: key not found")


def register_hashtable(env: 'Env') -> None:
    from core.tail_call import apply
    env.define("make-hash-table", Prim("make-hash-table", prim_make_hash_table))
    env.define("hash-table?", Prim("hash-table?", prim_hash_table_p))
    env.define("hash-table-ref", Prim("hash-table-ref", prim_hash_table_ref))
    env.define("hash-table-set!", Prim("hash-table-set!", prim_hash_table_set_bang))
    env.define("hash-table-delete!", Prim("hash-table-delete!", prim_hash_table_delete_bang))
    env.define("hash-table-contains?", Prim("hash-table-contains?", prim_hash_table_contains_p))
    env.define("hash-table-keys", Prim("hash-table-keys", prim_hash_table_keys))
    env.define("hash-table-values", Prim("hash-table-values", prim_hash_table_values))
    env.define("hash-table-map", Prim("hash-table-map", prim_hash_table_map))
    env.define("hash-table-for-each", Prim("hash-table-for-each", prim_hash_table_for_each))
    env.define("hash-set!", Prim("hash-set!", prim_hash_table_set_bang))
    env.define("hash-ref", Prim("hash-ref", prim_hash_table_ref))
    env.define("hash-for-each", Prim("hash-for-each", prim_hash_table_for_each))
    env.define("hash-table->alist", Prim("hash-table->alist", prim_hash_table_to_alist))
