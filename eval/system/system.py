"""
System Info Module - Based on Python os, platform, sys, and psutil libraries.

System Info:
  (os-name)                        -> operating system name
  (os-version)                     -> OS version string
  (os-type)                        -> 'linux, 'windows, 'macos, 'unknown
  (machine)                        -> machine type (x86_64, arm64...)
  (processor)                      -> processor info
  (hostname)                       -> host name
  (python-version)                 -> Python version string

Process Info:
  (pid)                            -> current process ID
  (ppid)                           -> parent process ID
  (process-name)                   -> current process name
  (cpu-count)                      -> number of CPUs
  (uptime)                         -> system uptime in seconds

Environment:
  (getenv name)                    -> get env variable
  (getenv name default)            -> get with default
  (setenv name value)              -> set env variable
  (unsetenv name)                  -> unset env variable
  (environ)                        -> all env vars as alist

Memory & Disk:
  (memory-total)                   -> total physical memory (bytes)
  (memory-available)               -> available memory (bytes)
  (memory-used)                    -> used memory (bytes)
  (memory-percent)                 -> memory usage percent
  (disk-usage path)                -> disk usage as alist
  (disk-partitions)                -> list of disk partitions

Network:
  (hostname-fqdn)                  -> fully qualified hostname
  (ip-address)                     -> primary IP address
  (network-interfaces)             -> network interfaces

Users:
  (current-user)                   -> current username
  (user-home)                      -> user home directory path
  (user-shell)                     -> user shell path
  (user-info)                      -> user info as alist

Utility:
  (getcwd)                         -> current working directory
  (list-processes)                 -> list running processes
  (system-info)                    -> all info as alist
"""
import os
import sys
import platform
import socket
import getpass
import pwd
from typing import List
from dataclasses import dataclass

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


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


def _cons_alist(pairs: list) -> SchemeValue:
    """Build alist ((key . val) ...) from list of (Sym, value) pairs"""
    result = Nil()
    for k, v in reversed(pairs):
        result = Cons(Cons(k, v), result)
    return result


def _maybe(val_fn, default=Bool(False)):
    """Try to call val_fn, return default on failure"""
    try:
        return val_fn()
    except Exception:
        return default


# ==================== System Info ====================


def os_name(args: List) -> SchemeValue:
    return Str(platform.system())


def os_version(args: List) -> SchemeValue:
    return Str(platform.version())


def os_type(args: List) -> SchemeValue:
    s = platform.system().lower()
    if s == "linux":
        return Sym("linux")
    if s == "windows":
        return Sym("windows")
    if s == "darwin":
        return Sym("macos")
    return Sym(s)


def machine(args: List) -> SchemeValue:
    return Str(platform.machine())


def processor(args: List) -> SchemeValue:
    return Str(platform.processor())


def hostname(args: List) -> SchemeValue:
    return Str(socket.gethostname())


def python_version(args: List) -> SchemeValue:
    return Str(sys.version)


# ==================== Process Info ====================


def fn_pid(args: List) -> SchemeValue:
    return Num(os.getpid())


def fn_ppid(args: List) -> SchemeValue:
    return Num(os.getppid())


def process_name(args: List) -> SchemeValue:
    return Str(sys.argv[0] if sys.argv else "unknown")


def cpu_count(args: List) -> SchemeValue:
    return Num(os.cpu_count() or 1)


def uptime(args: List) -> SchemeValue:
    """System uptime in seconds (Linux only via /proc/uptime)"""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_secs = float(f.read().split()[0])
            return Num(uptime_secs)
    except Exception:
        return Num(-1)


# ==================== Environment ====================


def getenv(args: List) -> SchemeValue:
    if len(args) < 1:
        raise Exception("getenv: need 1 argument")
    name = _unwrap_str(args[0])
    default = _unwrap_str(args[1]) if len(args) > 1 else None
    val = os.environ.get(name, default)
    if val is None:
        return Bool(False)
    return Str(val)


def setenv(args: List) -> SchemeValue:
    if len(args) < 2:
        raise Exception("setenv: need 2 arguments (name value)")
    name = _unwrap_str(args[0])
    value = _unwrap_str(args[1])
    os.environ[name] = value
    return Bool(True)


def unsetenv(args: List) -> SchemeValue:
    if len(args) < 1:
        raise Exception("unsetenv: need 1 argument")
    name = _unwrap_str(args[0])
    os.environ.pop(name, None)
    return Bool(True)


def fn_environ(args: List) -> SchemeValue:
    result = Nil()
    for k, v in reversed(sorted(os.environ.items())):
        result = Cons(Cons(Str(k), Str(v)), result)
    return result


# ==================== Memory & Disk ====================


def _try_psutil():
    """Try to import psutil for memory/disk info"""
    try:
        import psutil as _psutil_mod
        return _psutil_mod
    except ImportError:
        return None


def memory_total(args: List) -> SchemeValue:
    psu = _try_psutil()
    if psu:
        return Num(psu.virtual_memory().total)
    # Fallback: Linux /proc/meminfo
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return Num(kb * 1024)
    except Exception:
        pass
    return Num(0)


def memory_available(args: List) -> SchemeValue:
    psu = _try_psutil()
    if psu:
        return Num(psu.virtual_memory().available)
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    return Num(kb * 1024)
    except Exception:
        pass
    return Num(0)


def memory_used(args: List) -> SchemeValue:
    psu = _try_psutil()
    if psu:
        vm = psu.virtual_memory()
        return Num(vm.used)
    return Num(memory_total([]).value - memory_available([]).value) if isinstance(memory_total([]), Num) and isinstance(memory_available([]), Num) else Num(0)


def memory_percent(args: List) -> SchemeValue:
    psu = _try_psutil()
    if psu:
        return Num(psu.virtual_memory().percent)
    t, a = memory_total([]).value, memory_available([]).value
    if t > 0:
        return Num(round((t - a) / t * 100, 1))
    return Num(0)


def disk_usage(args: List) -> SchemeValue:
    if len(args) < 1:
        raise Exception("disk-usage: need 1 argument (path)")
    path = _unwrap_str(args[0])
    psu = _try_psutil()
    if psu:
        du = psu.disk_usage(path)
        return _cons_alist([
            (Sym("total"), Num(du.total)),
            (Sym("used"), Num(du.used)),
            (Sym("free"), Num(du.free)),
            (Sym("percent"), Num(du.percent)),
        ])
    try:
        st = os.statvfs(path)
        total = st.f_frsize * st.f_blocks
        free = st.f_frsize * st.f_bfree
        used = total - free
        return _cons_alist([
            (Sym("total"), Num(total)),
            (Sym("used"), Num(used)),
            (Sym("free"), Num(free)),
            (Sym("percent"), Num(round(used / total * 100, 1) if total > 0 else 0)),
        ])
    except Exception:
        return Bool(False)


def disk_partitions(args: List) -> SchemeValue:
    psu = _try_psutil()
    if not psu:
        return Nil()
    result = Nil()
    for part in reversed(psu.disk_partitions()):
        info = _cons_alist([
            (Sym("device"), Str(part.device)),
            (Sym("mountpoint"), Str(part.mountpoint)),
            (Sym("fstype"), Str(part.fstype)),
            (Sym("opts"), Str(part.opts)),
        ])
        result = Cons(info, result)
    return result


# ==================== Network ====================


def hostname_fqdn(args: List) -> SchemeValue:
    return Str(socket.getfqdn())


def ip_address(args: List) -> SchemeValue:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return Str(ip)
    except Exception:
        return Str("127.0.0.1")


def network_interfaces(args: List) -> SchemeValue:
    psu = _try_psutil()
    if not psu:
        return Nil()
    result = Nil()
    for name, addrs in reversed(list(psu.net_if_addrs().items())):
        addr_list = Nil()
        for addr in addrs:
            addr_entry = _cons_alist([
                (Sym("family"), Str(str(addr.family))),
                (Sym("address"), Str(addr.address)),
            ])
            addr_list = Cons(addr_entry, addr_list)
        iface = Cons(Str(name), addr_list)
        result = Cons(iface, result)
    return result


# ==================== Users ====================


def current_user(args: List) -> SchemeValue:
    return Str(getpass.getuser())


def user_home(args: List) -> SchemeValue:
    return Str(os.path.expanduser("~"))


def user_shell(args: List) -> SchemeValue:
    try:
        return Str(pwd.getpwuid(os.getuid()).pw_shell)
    except Exception:
        return Str(os.environ.get("SHELL", "/bin/sh"))


def user_info(args: List) -> SchemeValue:
    try:
        pw = pwd.getpwuid(os.getuid())
        return _cons_alist([
            (Sym("name"), Str(pw.pw_name)),
            (Sym("uid"), Num(pw.pw_uid)),
            (Sym("gid"), Num(pw.pw_gid)),
            (Sym("home"), Str(pw.pw_dir)),
            (Sym("shell"), Str(pw.pw_shell)),
            (Sym("gecos"), Str(pw.pw_gecos)),
        ])
    except Exception:
        return _cons_alist([
            (Sym("name"), Str(getpass.getuser())),
            (Sym("home"), Str(os.path.expanduser("~"))),
            (Sym("shell"), Str(os.environ.get("SHELL", "/bin/sh"))),
        ])


# ==================== Utility ====================


def fn_getcwd(args: List) -> SchemeValue:
    return Str(os.getcwd())


def list_processes(args: List) -> SchemeValue:
    psu = _try_psutil()
    if not psu:
        return Nil()
    result = Nil()
    for proc in reversed(psu.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent'])):
        try:
            info = proc.info
            entry = _cons_alist([
                (Sym("pid"), Num(info['pid'])),
                (Sym("name"), Str(info['name'] or "")),
                (Sym("status"), Str(info['status'] or "")),
            ])
            result = Cons(entry, result)
        except Exception:
            pass
    return result


def system_info(args: List) -> SchemeValue:
    return _cons_alist([
        (Sym("os"), Str(platform.system())),
        (Sym("os-version"), Str(platform.version())),
        (Sym("hostname"), Str(socket.gethostname())),
        (Sym("machine"), Str(platform.machine())),
        (Sym("processor"), Str(platform.processor())),
        (Sym("python"), Str(sys.version)),
        (Sym("cpu-count"), Num(os.cpu_count() or 1)),
        (Sym("pid"), Num(os.getpid())),
        (Sym("user"), Str(getpass.getuser())),
        (Sym("cwd"), Str(os.getcwd())),
    ])


# ==================== Registration ====================


def register_system_primitives(env):
    env.define("os-name", Prim("os-name", os_name))
    env.define("os-version", Prim("os-version", os_version))
    env.define("os-type", Prim("os-type", os_type))
    env.define("machine", Prim("machine", machine))
    env.define("processor", Prim("processor", processor))
    env.define("hostname", Prim("hostname", hostname))
    env.define("python-version", Prim("python-version", python_version))

    env.define("pid", Prim("pid", fn_pid))
    env.define("ppid", Prim("ppid", fn_ppid))
    env.define("process-name", Prim("process-name", process_name))
    env.define("cpu-count", Prim("cpu-count", cpu_count))
    env.define("uptime", Prim("uptime", uptime))

    env.define("getenv", Prim("getenv", getenv))
    env.define("setenv", Prim("setenv", setenv))
    env.define("unsetenv", Prim("unsetenv", unsetenv))
    env.define("environ", Prim("environ", fn_environ))

    env.define("memory-total", Prim("memory-total", memory_total))
    env.define("memory-available", Prim("memory-available", memory_available))
    env.define("memory-used", Prim("memory-used", memory_used))
    env.define("memory-percent", Prim("memory-percent", memory_percent))
    env.define("disk-usage", Prim("disk-usage", disk_usage))
    env.define("disk-partitions", Prim("disk-partitions", disk_partitions))

    env.define("hostname-fqdn", Prim("hostname-fqdn", hostname_fqdn))
    env.define("ip-address", Prim("ip-address", ip_address))
    env.define("network-interfaces", Prim("network-interfaces", network_interfaces))

    env.define("current-user", Prim("current-user", current_user))
    env.define("user-home", Prim("user-home", user_home))
    env.define("user-shell", Prim("user-shell", user_shell))
    env.define("user-info", Prim("user-info", user_info))

    env.define("getcwd", Prim("getcwd", fn_getcwd))
    env.define("list-processes", Prim("list-processes", list_processes))
    env.define("system-info", Prim("system-info", system_info))