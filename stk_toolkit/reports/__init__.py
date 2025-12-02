"""
STK 报告生成模块
支持生成多种类型的报告
"""

from .base import ReportBase, ReportFormat
from .scenario_report import ScenarioReport
from .generator import ReportGenerator
from .utils import generate_report, generate_report_safe, generate_report_and_export

__all__ = [
    "ReportBase",
    "ReportFormat",
    "ScenarioReport",
    "ReportGenerator",
    "generate_report",
    "generate_report_safe",
    "generate_report_and_export",
]

