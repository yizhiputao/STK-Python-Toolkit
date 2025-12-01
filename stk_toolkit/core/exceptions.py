"""
STK 自定义异常类
"""


class STKError(Exception):
    """STK 基础异常类"""
    pass


class STKConnectionError(STKError):
    """STK 连接异常"""
    pass


class STKComponentError(STKError):
    """STK 组件操作异常"""
    pass


class STKModifyError(STKError):
    """STK 组件修改异常"""
    pass


class STKReportError(STKError):
    """STK 报告生成异常"""
    pass

