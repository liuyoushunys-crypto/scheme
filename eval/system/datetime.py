"""
DateTime Module - Based on Python datetime, time, and calendar libraries.

Date/Time Creation:
  (now)                            -> current datetime
  (date year month day)            -> date object
  (time hour minute second)        -> time object
  (datetime year month day h m s)  -> datetime object

Formatting & Parsing:
  (date-format dt "fmt")           -> formatted string
  (date-parse str "fmt")           -> parse string to datetime
  (date-iso dt)                    -> ISO 8601 string
  (date-iso-date dt)               -> ISO date string
  (date-iso-time dt)               -> ISO time string

Components:
  (date-year dt)                   -> year component
  (date-month dt)                  -> month (1-12)
  (date-day dt)                    -> day (1-31)
  (date-hour dt)                   -> hour (0-23)
  (date-minute dt)                 -> minute (0-59)
  (date-second dt)                 -> second (0-59)
  (date-weekday dt)                -> weekday (0=Mon, 6=Sun)
  (date-weekday-name dt)           -> weekday name string

Arithmetic:
  (date+ dt n unit)                -> add n units
  (date- dt n unit)                -> subtract n units
  (date-delta t1 t2)               -> difference in seconds
  (date-days-between d1 d2)        -> days between dates

Units for arithmetic:
  'years 'months 'days 'hours 'minutes 'seconds

Timestamps:
  (timestamp)                      -> current Unix timestamp
  (from-timestamp ts)              -> datetime from Unix timestamp
  (sleep n)                        -> sleep n seconds

Time Zones:
  (date-utc dt)                    -> convert to UTC
  (date-local dt)                  -> convert to local time
  (utc-now)                        -> current UTC datetime

Calendar:
  (days-in-month y m)              -> days in given month
  (is-leap-year? y)                -> leap year check
  (date->list y m)                 -> list of dates in month
  (week-of-year dt)                -> ISO week number
"""
import time as _time_module
import datetime
import calendar
from typing import List, Optional, Union
from dataclasses import dataclass

from core.schemevalue import *
from eval.eval_python_import import unwrap_python_value, wrap_python_value


@dataclass(frozen=True, slots=True)
class DateValue(SchemeValue):
    value: datetime.date

    def __str__(self):
        return f"#<date {self.value.isoformat()}>"


@dataclass(frozen=True, slots=True)
class DateTimeValue(SchemeValue):
    value: datetime.datetime

    def __str__(self):
        return f"#<datetime {self.value.isoformat()}>"


@dataclass(frozen=True, slots=True)
class TimeValue(SchemeValue):
    value: datetime.time

    def __str__(self):
        return f"#<time {self.value.isoformat()}>"


_UNITS = {
    'years': 'years', 'year': 'years',
    'months': 'months', 'month': 'months',
    'days': 'days', 'day': 'days',
    'hours': 'hours', 'hour': 'hours',
    'minutes': 'minutes', 'minute': 'minutes',
    'seconds': 'seconds', 'second': 'seconds',
    'weeks': 'weeks', 'week': 'weeks',
}


def _unwrap_int(val: SchemeValue) -> int:
    if isinstance(val, Integer):
        return val.value
    if isinstance(val, Num):
        return int(val.value)
    return int(unwrap_python_value(val))


def _unwrap_num(val: SchemeValue) -> Union[int, float]:
    if isinstance(val, Integer):
        return float(val.value)
    if isinstance(val, Num):
        v = val.value
        return float(v) if isinstance(v, (int, float)) else float(str(v))
    return float(unwrap_python_value(val))


def _unwrap_str(val: SchemeValue) -> str:
    if isinstance(val, Str):
        return val.get_str()
    if isinstance(val, Sym):
        return val.name
    raise Exception(f"Expected string, got {type(val).__name__}")


# ==================== Creation ====================


def fn_now(args: List[SchemeValue]) -> SchemeValue:
    """(now) -> current datetime"""
    return DateTimeValue(value=datetime.datetime.now())


def fn_date(args: List[SchemeValue]) -> SchemeValue:
    """(date year month day) -> date object"""
    if len(args) < 3:
        raise Exception("date: need 3 arguments (year month day)")
    y, m, d = _unwrap_int(args[0]), _unwrap_int(args[1]), _unwrap_int(args[2])
    return DateValue(value=datetime.date(y, m, d))


def fn_time(args: List[SchemeValue]) -> SchemeValue:
    """(time hour minute second) -> time object"""
    if len(args) < 3:
        raise Exception("time: need at least 3 arguments (hour minute second)")
    h, m, s = _unwrap_int(args[0]), _unwrap_int(args[1]), _unwrap_int(args[2])
    return TimeValue(value=datetime.time(h, m, s))


def fn_datetime(args: List[SchemeValue]) -> SchemeValue:
    """(datetime year month day hour minute second) -> datetime object"""
    if len(args) < 3:
        raise Exception("datetime: need at least 3 arguments")
    y = _unwrap_int(args[0])
    mo = _unwrap_int(args[1])
    d = _unwrap_int(args[2])
    h = _unwrap_int(args[3]) if len(args) > 3 else 0
    mi = _unwrap_int(args[4]) if len(args) > 4 else 0
    s = _unwrap_int(args[5]) if len(args) > 5 else 0
    return DateTimeValue(value=datetime.datetime(y, mo, d, h, mi, s))


# ==================== Formatting & Parsing ====================


def date_format(args: List[SchemeValue]) -> SchemeValue:
    """(date-format dt "fmt") -> formatted string"""
    if len(args) < 2:
        raise Exception("date-format: need 2 arguments (datetime fmt)")
    val = args[0]
    fmt = _unwrap_str(args[1])
    if isinstance(val, DateTimeValue):
        return Str(val.value.strftime(fmt))
    elif isinstance(val, DateValue):
        return Str(val.value.strftime(fmt))
    elif isinstance(val, TimeValue):
        return Str(val.value.strftime(fmt))
    raise Exception(f"date-format: expected date/datetime/time, got {type(val).__name__}")


def date_parse(args: List[SchemeValue]) -> SchemeValue:
    """(date-parse str "fmt") -> parse string to datetime"""
    if len(args) < 2:
        raise Exception("date-parse: need 2 arguments (string fmt)")
    s = _unwrap_str(args[0])
    fmt = _unwrap_str(args[1])
    return DateTimeValue(value=datetime.datetime.strptime(s, fmt))


def date_iso(args: List[SchemeValue]) -> SchemeValue:
    """(date-iso dt) -> ISO 8601 string"""
    if len(args) < 1:
        raise Exception("date-iso: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return Str(val.value.isoformat())
    elif isinstance(val, DateValue):
        return Str(val.value.isoformat())
    raise Exception(f"date-iso: expected datetime or date, got {type(val).__name__}")


def date_iso_date(args: List[SchemeValue]) -> SchemeValue:
    """(date-iso-date dt) -> ISO date string"""
    if len(args) < 1:
        raise Exception("date-iso-date: need 1 argument")
    val = args[0]
    if isinstance(val, (DateTimeValue, DateValue)):
        if isinstance(val, DateTimeValue):
            return Str(val.value.date().isoformat())
        return Str(val.value.isoformat())
    raise Exception(f"date-iso-date: expected datetime or date")


def date_iso_time(args: List[SchemeValue]) -> SchemeValue:
    """(date-iso-time dt) -> ISO time string"""
    if len(args) < 1:
        raise Exception("date-iso-time: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return Str(val.value.time().isoformat())
    elif isinstance(val, TimeValue):
        return Str(val.value.isoformat())
    raise Exception(f"date-iso-time: expected datetime or time")


# ==================== Components ====================


def _get_dt(val: SchemeValue) -> Union[datetime.datetime, datetime.date]:
    if isinstance(val, DateTimeValue):
        return val.value
    if isinstance(val, DateValue):
        return val.value
    raise Exception(f"Expected datetime or date, got {type(val).__name__}")


def date_year(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-year: need 1 argument")
    return Num(_get_dt(args[0]).year)


def date_month(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-month: need 1 argument")
    return Num(_get_dt(args[0]).month)


def date_day(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-day: need 1 argument")
    return Num(_get_dt(args[0]).day)


def date_hour(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-hour: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return Num(val.value.hour)
    raise Exception("date-hour: expected datetime")


def date_minute(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-minute: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return Num(val.value.minute)
    raise Exception("date-minute: expected datetime")


def date_second(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-second: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return Num(val.value.second)
    raise Exception("date-second: expected datetime")


def date_weekday(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-weekday: need 1 argument")
    return Num(_get_dt(args[0]).weekday())


def date_weekday_name(args: List[SchemeValue]) -> SchemeValue:
    if len(args) < 1: raise Exception("date-weekday-name: need 1 argument")
    return Str(_get_dt(args[0]).strftime("%A"))


# ==================== Arithmetic ====================


def _relativedelta_fn(amount: int, unit: str):
    """Create a relative delta based on unit name"""
    unit = _UNITS.get(unit, unit)
    if unit == 'years':
        return datetime.timedelta(days=amount * 365)
    elif unit == 'months':
        return datetime.timedelta(days=amount * 30)
    elif unit == 'weeks':
        return datetime.timedelta(weeks=amount)
    elif unit == 'days':
        return datetime.timedelta(days=amount)
    elif unit == 'hours':
        return datetime.timedelta(hours=amount)
    elif unit == 'minutes':
        return datetime.timedelta(minutes=amount)
    elif unit == 'seconds':
        return datetime.timedelta(seconds=amount)
    raise Exception(f"Unknown unit: {unit}")


def date_add(args: List[SchemeValue]) -> SchemeValue:
    """(date+ dt n unit)"""
    if len(args) < 3:
        raise Exception("date+: need 3 arguments (dt n unit)")
    val = args[0]
    n = _unwrap_int(args[1])
    unit = _unwrap_str(args[2])
    delta = _relativedelta_fn(n, unit)
    if isinstance(val, DateTimeValue):
        return DateTimeValue(value=val.value + delta)
    elif isinstance(val, DateValue):
        return DateValue(value=val.value + delta)
    raise Exception("date+: expected datetime or date")


def date_sub(args: List[SchemeValue]) -> SchemeValue:
    """(date- dt n unit)"""
    if len(args) < 3:
        raise Exception("date-: need 3 arguments (dt n unit)")
    val = args[0]
    n = _unwrap_int(args[1])
    unit = _unwrap_str(args[2])
    delta = _relativedelta_fn(n, unit)
    if isinstance(val, DateTimeValue):
        return DateTimeValue(value=val.value - delta)
    elif isinstance(val, DateValue):
        return DateValue(value=val.value - delta)
    raise Exception("date-: expected datetime or date")


def date_delta(args: List[SchemeValue]) -> SchemeValue:
    """(date-delta t1 t2) -> difference in seconds"""
    if len(args) < 2:
        raise Exception("date-delta: need 2 arguments")
    val1, val2 = args[0], args[1]
    v1 = val1.value if isinstance(val1, (DateTimeValue, DateValue)) else None
    v2 = val2.value if isinstance(val2, (DateTimeValue, DateValue)) else None
    if v1 is None or v2 is None:
        raise Exception("date-delta: arguments must be datetime or date")
    delta = v1 - v2
    return Num(delta.total_seconds())


def date_days_between(args: List[SchemeValue]) -> SchemeValue:
    """(date-days-between d1 d2) -> days between dates"""
    if len(args) < 2:
        raise Exception("date-days-between: need 2 arguments")
    val1, val2 = args[0], args[1]
    v1 = val1.value if isinstance(val1, DateValue) else None
    v2 = val2.value if isinstance(val2, DateValue) else None
    if v1 is None or v2 is None:
        raise Exception("date-days-between: arguments must be dates")
    delta = v1 - v2
    return Num(abs(delta.days))


# ==================== Timestamps ====================


def fn_timestamp(args: List[SchemeValue]) -> SchemeValue:
    """(timestamp) -> current Unix timestamp"""
    return Num(_time_module.time())


def from_timestamp(args: List[SchemeValue]) -> SchemeValue:
    """(from-timestamp ts) -> datetime"""
    if len(args) < 1:
        raise Exception("from-timestamp: need 1 argument")
    ts = _unwrap_num(args[0])
    return DateTimeValue(value=datetime.datetime.fromtimestamp(ts))


def fn_sleep(args: List[SchemeValue]) -> SchemeValue:
    """(sleep n) -> sleep n seconds"""
    if len(args) < 1:
        raise Exception("sleep: need 1 argument")
    n = _unwrap_num(args[0])
    _time_module.sleep(n)
    return Bool(True)


# ==================== Time Zones ====================


def date_utc(args: List[SchemeValue]) -> SchemeValue:
    """(date-utc dt) -> convert to UTC"""
    if len(args) < 1:
        raise Exception("date-utc: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        return DateTimeValue(value=val.value.astimezone(datetime.timezone.utc))
    raise Exception("date-utc: expected datetime")


def date_local(args: List[SchemeValue]) -> SchemeValue:
    """(date-local dt) -> convert to local time"""
    if len(args) < 1:
        raise Exception("date-local: need 1 argument")
    val = args[0]
    if isinstance(val, DateTimeValue):
        local = val.value.astimezone().astimezone()
        return DateTimeValue(value=local.replace(tzinfo=None))
    raise Exception("date-local: expected datetime")


def utc_now(args: List[SchemeValue]) -> SchemeValue:
    """(utc-now) -> current UTC datetime"""
    return DateTimeValue(value=datetime.datetime.now(datetime.timezone.utc))


# ==================== Calendar ====================


def days_in_month(args: List[SchemeValue]) -> SchemeValue:
    """(days-in-month y m) -> days in month"""
    if len(args) < 2:
        raise Exception("days-in-month: need 2 arguments (year month)")
    y, m = _unwrap_int(args[0]), _unwrap_int(args[1])
    return Num(calendar.monthrange(y, m)[1])


def is_leap_year(args: List[SchemeValue]) -> SchemeValue:
    """(is-leap-year? y) -> leap year check"""
    if len(args) < 1:
        raise Exception("is-leap-year?: need 1 argument")
    y = _unwrap_int(args[0])
    return Bool(calendar.isleap(y))


def date_to_list(args: List[SchemeValue]) -> SchemeValue:
    """(date->list y m) -> list of date objects in month"""
    if len(args) < 2:
        raise Exception("date->list: need 2 arguments (year month)")
    y, m = _unwrap_int(args[0]), _unwrap_int(args[1])
    _, days = calendar.monthrange(y, m)
    result = Nil()
    for d in reversed(range(1, days + 1)):
        result = Cons(DateValue(value=datetime.date(y, m, d)), result)
    return result


def week_of_year(args: List[SchemeValue]) -> SchemeValue:
    """(week-of-year dt) -> ISO week number"""
    if len(args) < 1:
        raise Exception("week-of-year: need 1 argument")
    dt = _get_dt(args[0])
    if isinstance(dt, datetime.datetime):
        return Num(dt.isocalendar()[1])
    return Num(dt.isocalendar()[1])


# ==================== Registration ====================


def register_datetime_primitives(env):
    env.define("now", Prim("now", fn_now))
    env.define("date", Prim("date", fn_date))
    env.define("time", Prim("time", fn_time))
    env.define("datetime", Prim("datetime", fn_datetime))

    env.define("date-format", Prim("date-format", date_format))
    env.define("date-parse", Prim("date-parse", date_parse))
    env.define("date-iso", Prim("date-iso", date_iso))
    env.define("date-iso-date", Prim("date-iso-date", date_iso_date))
    env.define("date-iso-time", Prim("date-iso-time", date_iso_time))

    env.define("date-year", Prim("date-year", date_year))
    env.define("date-month", Prim("date-month", date_month))
    env.define("date-day", Prim("date-day", date_day))
    env.define("date-hour", Prim("date-hour", date_hour))
    env.define("date-minute", Prim("date-minute", date_minute))
    env.define("date-second", Prim("date-second", date_second))
    env.define("date-weekday", Prim("date-weekday", date_weekday))
    env.define("date-weekday-name", Prim("date-weekday-name", date_weekday_name))

    env.define("date+", Prim("date+", date_add))
    env.define("date-", Prim("date-", date_sub))
    env.define("date-delta", Prim("date-delta", date_delta))
    env.define("date-days-between", Prim("date-days-between", date_days_between))

    env.define("timestamp", Prim("timestamp", fn_timestamp))
    env.define("from-timestamp", Prim("from-timestamp", from_timestamp))
    env.define("sleep", Prim("sleep", fn_sleep))

    env.define("date-utc", Prim("date-utc", date_utc))
    env.define("date-local", Prim("date-local", date_local))
    env.define("utc-now", Prim("utc-now", utc_now))

    env.define("days-in-month", Prim("days-in-month", days_in_month))
    env.define("is-leap-year?", Prim("is-leap-year?", is_leap_year))
    env.define("date->list", Prim("date->list", date_to_list))
    env.define("week-of-year", Prim("week-of-year", week_of_year))