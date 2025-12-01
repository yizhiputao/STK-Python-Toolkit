"""
STK 核心模块
包含连接管理和异常定义
"""

from .connection import STKConnection
from .exceptions import STKError, STKConnectionError, STKComponentError

__all__ = [
    "STKConnection",
    "STKError",
    "STKConnectionError",
    "STKComponentError",
]

