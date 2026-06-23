from typing import Optional, Any


class ContinuationException(Exception):
    """通过调用续体跳出当前执行流时抛出的异常"""
    def __init__(self, value: Optional[Any] = None):
        super().__init__()
        self.value = value


class SchemeRaiseException(Exception):
    """Scheme 用户层主动抛出的异常"""
    def __init__(self, value: Any):
        super().__init__()
        self.value = value


class SchemeRaiseContinuableException(Exception):
    """R7RS 可继续抛出的异常流包装"""
    def __init__(self, value: Any):
        super().__init__()
        self.value = value
