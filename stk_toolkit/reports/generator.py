"""
报告生成器
统一的报告生成入口，支持注册和生成多种类型的报告
"""

from typing import Any, Dict, List, Optional, Type
from pathlib import Path
from .base import ReportBase, ReportFormat
from .scenario_report import ScenarioReport
from ..core.connection import STKConnection


class ReportGenerator:
    """
    报告生成器
    
    统一管理各类报告的生成:
    - 注册自定义报告类型
    - 批量生成报告
    - 统一的输出目录管理
    
    使用示例:
        generator = ReportGenerator(connection, output_dir="./reports")
        
        # 生成场景报告
        report = generator.generate_scenario_report()
        
        # 注册自定义报告
        generator.register("access", AccessReport)
        report = generator.generate("access")
    """
    
    # 内置报告类型注册表
    _report_classes: Dict[str, Type[ReportBase]] = {
        "scenario": ScenarioReport,
        # 预留其他报告类型
        # "access": AccessReport,
        # "coverage": CoverageReport,
        # "orbit": OrbitReport,
    }
    
    def __init__(self, connection: STKConnection, output_dir: str = "./reports"):
        """
        初始化报告生成器
        
        Args:
            connection: STK 连接对象
            output_dir: 报告输出目录
        """
        self._connection = connection
        self._output_dir = Path(output_dir)
        self._generated_reports: List[ReportBase] = []
    
    @property
    def output_dir(self) -> Path:
        """获取输出目录"""
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, value: str):
        """设置输出目录"""
        self._output_dir = Path(value)
    
    @classmethod
    def register(cls, name: str, report_class: Type[ReportBase]):
        """
        注册报告类型
        
        Args:
            name: 报告类型名称
            report_class: 报告类
        """
        cls._report_classes[name] = report_class
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """获取可用的报告类型列表"""
        return list(cls._report_classes.keys())
    
    def generate(self, report_type: str, 
                 format: ReportFormat = ReportFormat.TEXT,
                 save: bool = True,
                 **kwargs) -> ReportBase:
        """
        生成指定类型的报告
        
        Args:
            report_type: 报告类型
            format: 报告格式
            save: 是否保存到文件
            **kwargs: 传递给报告类的额外参数
            
        Returns:
            ReportBase: 生成的报告对象
        """
        report_class = self._report_classes.get(report_type)
        if report_class is None:
            raise ValueError(f"未知的报告类型: {report_type}，"
                           f"可用类型: {self.get_available_types()}")
        
        # 创建报告实例
        report = report_class(self._connection, **kwargs)
        report.collect_data()
        
        # 保存报告
        if save:
            report.save(str(self._output_dir), format=format)
        
        self._generated_reports.append(report)
        return report
    
    def generate_scenario_report(self, 
                                  format: ReportFormat = ReportFormat.TEXT,
                                  save: bool = True,
                                  title: str = "STK 场景详细信息报告") -> ScenarioReport:
        """
        生成场景报告 (便捷方法)
        
        Args:
            format: 报告格式
            save: 是否保存到文件
            title: 报告标题
            
        Returns:
            ScenarioReport: 场景报告对象
        """
        return self.generate("scenario", format=format, save=save, title=title)
    
    def generate_all(self, 
                     types: Optional[List[str]] = None,
                     format: ReportFormat = ReportFormat.TEXT) -> List[ReportBase]:
        """
        批量生成多种报告
        
        Args:
            types: 要生成的报告类型列表，默认生成所有可用类型
            format: 报告格式
            
        Returns:
            list: 生成的报告列表
        """
        if types is None:
            types = self.get_available_types()
        
        reports = []
        for report_type in types:
            try:
                report = self.generate(report_type, format=format)
                reports.append(report)
            except Exception as e:
                print(f"生成 {report_type} 报告失败: {e}")
        
        return reports
    
    def get_generated_reports(self) -> List[ReportBase]:
        """获取已生成的报告列表"""
        return self._generated_reports.copy()
    
    def clear_history(self):
        """清空报告历史"""
        self._generated_reports.clear()


# ============================================================
# 预留的报告类框架
# ============================================================

# class AccessReport(ReportBase):
#     """
#     访问分析报告
#     
#     报告卫星与地面站之间的访问情况
#     """
#     
#     def __init__(self, connection: STKConnection, 
#                  satellite_name: str,
#                  facility_name: str,
#                  title: str = "访问分析报告"):
#         super().__init__(title)
#         self._connection = connection
#         self._satellite_name = satellite_name
#         self._facility_name = facility_name
#     
#     def _get_report_type(self) -> str:
#         return "access_report"
#     
#     def collect_data(self) -> "AccessReport":
#         # TODO: 实现访问数据收集
#         pass
#     
#     def _generate_text(self) -> str:
#         # TODO: 实现文本格式生成
#         pass


# class OrbitReport(ReportBase):
#     """
#     轨道分析报告
#     """
#     pass


# class CoverageReport(ReportBase):
#     """
#     覆盖分析报告
#     """
#     pass

