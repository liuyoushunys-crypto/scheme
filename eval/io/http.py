"""
HTTP Client - Based on Python requests library.

First-class citizen features:
  - Response objects with status, headers, body
  - Session support for cookies and connection reuse
  - JSON, text, and binary response handling

HTTP Methods:
  (http-get url)                     -> response
  (http-get url headers)             -> response with headers
  (http-post url data)               -> POST with form data
  (http-post-json url json-data)     -> POST with JSON
  (http-put url data)                -> PUT request
  (http-delete url)                  -> DELETE request
  (http-head url)                    -> HEAD request
  (http-options url)                 -> OPTIONS request
  (http-patch url data)              -> PATCH request

Response operations:
  (http-status response)             -> status code
  (http-ok? response)                -> 2xx check
  (http-headers response)            -> headers alist
  (http-text response)               -> response body as text
  (http-json response)               -> parse response as JSON
  (http-content response)            -> response bytes

URL operations:
  (url "base" "path")                -> construct URL
  (url-join url "path")              -> join URL paths
  (url-query url alist)              -> add query params
  (url-parse url)                    -> parse URL into components

Session:
  (http-session)                     -> create new session
  (http-session-get session url)     -> GET with session
  (http-session-post session u d)    -> POST with session
  (http-session-close session)       -> close session

Download:
  (http-download url path)           -> download file to path

Utility:
  (http-encode-params alist)         -> URL-encode params
  (user-agent)                       -> default user agent
"""

import json
from typing import List, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


@dataclass(frozen=True, slots=True)
class HttpResponse(SchemeValue):
    """HTTP Response object"""
    status: int
    text_body: str
    raw_body: bytes
    headers: dict
    url: str
    encoding: str

    def __str__(self):
        return f"#<http-response {self.status} {self.url}>"


@dataclass(frozen=True, slots=True)
class HttpSession(SchemeValue):
    """HTTP Session object"""
    session: object

    def __str__(self):
        return "#<http-session>"


_requests_imported = False
_requests = None


def _get_requests():
    global _requests, _requests_imported
    if not _requests_imported:
        try:
            import requests as m
            _requests = m
            _requests_imported = True
        except ImportError:
            raise Exception("requests not installed - run: pip install requests")
    return _requests


def _unwrap_str(val: SchemeValue) -> str:
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


def _unwrap_dict(val: SchemeValue) -> dict:
    result = {}
    if isinstance(val, HashTable):
        for k, v in val.table.items():
            if isinstance(k, str):
                key = k
            elif isinstance(k, Str):
                key = k.get_str()
            else:
                key = str(k)
            if isinstance(v, Bool):
                result[key] = v.value
            elif isinstance(v, Num):
                result[key] = int(v.value) if isinstance(v.value, (int, float)) else v.value
            elif isinstance(v, Integer):
                result[key] = v.value
            elif isinstance(v, Str):
                result[key] = v.get_str()
            elif isinstance(v, Sym):
                result[key] = v.name
            else:
                result[key] = str(v)
    elif isinstance(val, Cons):
        current = val
        while isinstance(current, Cons):
            pair = current.car
            if isinstance(pair, Cons):
                k = str(pair.car) if hasattr(pair.car, '__str__') else str(pair.car)
                v = str(pair.cdr) if isinstance(pair.cdr, (Str, Sym)) else str(pair.cdr)
                result[k] = v
            current = current.cdr
    return result


def _build_response(resp) -> HttpResponse:
    return HttpResponse(
        status=resp.status_code,
        text_body=resp.text,
        raw_body=resp.content,
        headers=dict(resp.headers),
        url=resp.url,
        encoding=resp.encoding or "utf-8"
    )


# ==================== HTTP Methods ====================


def http_get(args: List[SchemeValue]) -> SchemeValue:
    """(http-get url) or (http-get url headers)"""
    if len(args) < 1:
        raise Exception("http-get: need 1 argument (url)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    headers = {}
    if len(args) > 1 and isinstance(args[1], (HashTable, Cons)):
        headers = _unwrap_dict(args[1])
    try:
        resp = req.get(url, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP GET failed: {e}")


def http_post(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("http-post: need 2 arguments (url data)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    data = _unwrap_str(args[1]) if isinstance(args[1], Str) else _unwrap_dict(args[1])
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = req.post(url, data=data, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP POST failed: {e}")


def http_post_json(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("http-post-json: need 2 arguments (url json-data)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    if isinstance(args[1], (HashTable, Cons)):
        json_data = _unwrap_dict(args[1])
    else:
        json_data = json.loads(_unwrap_str(args[1]))
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = req.post(url, json=json_data, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP POST JSON failed: {e}")


def http_put(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("http-put: need 2 arguments (url data)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    data = _unwrap_str(args[1]) if isinstance(args[1], Str) else _unwrap_dict(args[1])
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = req.put(url, data=data, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP PUT failed: {e}")


def http_delete(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("http-delete: need 1 argument (url)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    headers = _unwrap_dict(args[1]) if len(args) > 1 else {}
    try:
        resp = req.delete(url, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP DELETE failed: {e}")


def http_head(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("http-head: need 1 argument (url)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    headers = _unwrap_dict(args[1]) if len(args) > 1 else {}
    try:
        resp = req.head(url, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP HEAD failed: {e}")


def http_options(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("http-options: need 1 argument (url)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    try:
        resp = req.options(url, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP OPTIONS failed: {e}")


def http_patch(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("http-patch: need 2 arguments (url data)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    data = _unwrap_str(args[1]) if isinstance(args[1], Str) else _unwrap_dict(args[1])
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = req.patch(url, data=data, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"HTTP PATCH failed: {e}")


# ==================== Response Operations ====================


def http_status(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-status: need response object")
    return Num(args[0].status)


def http_ok(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-ok?: need response object")
    return Bool(200 <= args[0].status < 300)


def http_headers_fn(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-headers: need response object")
    resp = args[0]
    result = Nil()
    for k, v in resp.headers.items():
        result = Cons(Cons(Str(k), Str(v)), result)
    return result


def http_text(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-text: need response object")
    return Str(args[0].text_body)


def http_json_val(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-json: need response object")
    try:
        data = json.loads(args[0].text_body)
        return wrap_python_value(data)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {e}")


def http_content(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpResponse):
        raise Exception("http-content: need response object")
    return Bytevector(bytearray(args[0].raw_body))


# ==================== URL Operations ====================


def url_create(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("url: need at least 1 argument")
    result = _unwrap_str(args[0])
    for arg in args[1:]:
        segment = _unwrap_str(arg)
        result = urljoin(result.rstrip('/') + '/', segment.lstrip('/'))
    return Str(result)


def url_join_fn(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("url-join: need 2 arguments")
    base = _unwrap_str(args[0])
    path = _unwrap_str(args[1])
    result = urljoin(base.rstrip('/') + '/', path.lstrip('/'))
    return Str(result)


def url_query(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("url-query: need 2 arguments (url params)")
    base_url = _unwrap_str(args[0])
    params = _unwrap_dict(args[1])
    if params:
        sep = '&' if '?' in base_url else '?'
        result = base_url + sep + urlencode(params)
    else:
        result = base_url
    return Str(result)


def url_parse_fn(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("url-parse: need 1 argument")
    url_str = _unwrap_str(args[0])
    parsed = urlparse(url_str)
    components = [
        Cons(Sym("scheme"), Str(parsed.scheme)),
        Cons(Sym("netloc"), Str(parsed.netloc)),
        Cons(Sym("path"), Str(parsed.path)),
        Cons(Sym("params"), Str(parsed.params)),
        Cons(Sym("query"), Str(parsed.query)),
        Cons(Sym("fragment"), Str(parsed.fragment)),
        Cons(Sym("hostname"), Str(parsed.hostname or "")),
        Cons(Sym("port"), Num(parsed.port or 0)),
    ]
    result = Nil()
    for c in reversed(components):
        result = Cons(c, result)
    return result


# ==================== Session ====================


def http_session_create(args: List[SchemeValue]) -> SchemeValue:
    req = _get_requests()
    session = req.Session()
    return HttpSession(session=session)


def http_session_get(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2 or not isinstance(args[0], HttpSession):
        raise Exception("http-session-get: need session and url")
    session = args[0].session
    url = _unwrap_str(args[1])
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = session.get(url, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"Session GET failed: {e}")


def http_session_post(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 3 or not isinstance(args[0], HttpSession):
        raise Exception("http-session-post: need session, url, data")
    session = args[0].session
    url = _unwrap_str(args[1])
    data = _unwrap_str(args[2]) if isinstance(args[2], Str) else _unwrap_dict(args[2])
    headers = _unwrap_dict(args[3]) if len(args) > 3 else {}
    try:
        resp = session.post(url, data=data, headers=headers, timeout=30)
        return _build_response(resp)
    except Exception as e:
        raise Exception(f"Session POST failed: {e}")


def http_session_close(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1 or not isinstance(args[0], HttpSession):
        raise Exception("http-session-close: need session")
    args[0].session.close()
    return Bool(True)


# ==================== Download ====================


def http_download(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 2:
        raise Exception("http-download: need 2 arguments (url path)")
    req = _get_requests()
    url = _unwrap_str(args[0])
    filepath = _unwrap_str(args[1])
    headers = _unwrap_dict(args[2]) if len(args) > 2 else {}
    try:
        resp = req.get(url, headers=headers, stream=True, timeout=30)
        resp.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return Str(filepath)
    except Exception as e:
        raise Exception(f"HTTP download failed: {e}")


# ==================== Utility ====================


def http_encode_params(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1:
        raise Exception("http-encode-params: need 1 argument")
    params = _unwrap_dict(args[0])
    return Str(urlencode(params))


def http_user_agent(args: List[SchemeValue]) -> SchemeValue:
    return Str("HermesScheme-Client/1.0")


def register_http_primitives(env):
    env.define("http-get", Prim("http-get", http_get))
    env.define("http-post", Prim("http-post", http_post))
    env.define("http-post-json", Prim("http-post-json", http_post_json))
    env.define("http-put", Prim("http-put", http_put))
    env.define("http-delete", Prim("http-delete", http_delete))
    env.define("http-head", Prim("http-head", http_head))
    env.define("http-options", Prim("http-options", http_options))
    env.define("http-patch", Prim("http-patch", http_patch))

    env.define("http-status", Prim("http-status", http_status))
    env.define("http-ok?", Prim("http-ok?", http_ok))
    env.define("http-headers", Prim("http-headers", http_headers_fn))
    env.define("http-text", Prim("http-text", http_text))
    env.define("http-json", Prim("http-json", http_json_val))
    env.define("http-content", Prim("http-content", http_content))

    env.define("url", Prim("url", url_create))
    env.define("url-join", Prim("url-join", url_join_fn))
    env.define("url-query", Prim("url-query", url_query))
    env.define("url-parse", Prim("url-parse", url_parse_fn))

    env.define("http-session", Prim("http-session", http_session_create))
    env.define("http-session-get", Prim("http-session-get", http_session_get))
    env.define("http-session-post", Prim("http-session-post", http_session_post))
    env.define("http-session-close", Prim("http-session-close", http_session_close))

    env.define("http-download", Prim("http-download", http_download))
    env.define("http-encode-params", Prim("http-encode-params", http_encode_params))
    env.define("user-agent", Prim("user-agent", http_user_agent))