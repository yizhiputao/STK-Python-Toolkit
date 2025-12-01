"""
STK Python Toolkit
高内聚低耦合的 STK Python 工具包

模块结构:
- core: STK 连接管理
- components: 组件创建 (卫星、地面站等)
- modifiers: 组件修改
- conditions: 条件生成 (预留)
- reports: 报告生成
"""

from .core.connection import STKConnection
from .core.exceptions import STKError, STKConnectionError, STKComponentError

__version__ = "1.0.0"
__all__ = [
    "STKConnection",
    "STKError",
    "STKConnectionError",
    "STKComponentError",
]

