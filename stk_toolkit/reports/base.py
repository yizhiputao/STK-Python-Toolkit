"""
报告基类
定义报告生成的通用接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
import json


class ReportFormat(Enum):
    """报告格式枚举"""
    TEXT = "txt"
    JSON = "json"
    # 可扩展其他格式
    # HTML = "html"
    # CSV = "csv"
    # EXCEL = "xlsx"


class ReportBase(ABC):
    """
    报告基类
    
    所有报告类型的抽象基类
    """
    
    def __init__(self, title: str = "STK Report"):
        """
        初始化报告
        
        Args:
            title: 报告标题
        """
        self._title = title
        self._data: Dict[str, Any] = {}
        self._generated_time = None
    
    @property
    def title(self) -> str:
        """获取报告标题"""
        return self._title
    
    @property
    def data(self) -> Dict[str, Any]:
        """获取报告数据"""
        return self._data
    
    @property
    def generated_time(self) -> Optional[datetime]:
        """获取报告生成时间"""
        return self._generated_time
    
    @abstractmethod
    def collect_data(self) -> "ReportBase":
        """
        收集报告数据
        
        Returns:
            self: 返回自身以支持链式调用
        """
        pass
    
    def generate(self, format: ReportFormat = ReportFormat.TEXT) -> str:
        """
        生成报告内容
        
        Args:
            format: 报告格式
            
        Returns:
            str: 报告内容
        """
        self._generated_time = datetime.now()
        
        if format == ReportFormat.TEXT:
            return self._generate_text()
        elif format == ReportFormat.JSON:
            return self._generate_json()
        else:
            raise ValueError(f"不支持的报告格式: {format}")
    
    @abstractmethod
    def _generate_text(self) -> str:
        """生成文本格式报告"""
        pass
    
    def _generate_json(self) -> str:
        """生成 JSON 格式报告"""
        output = {
            "title": self._title,
            "generated_time": self._generated_time.isoformat() if self._generated_time else None,
            "data": self._data
        }
        return json.dumps(output, indent=2, ensure_ascii=False, default=str)
    
    def save(self, output_dir: str, filename: Optional[str] = None,
             format: ReportFormat = ReportFormat.TEXT,
             save_latest: bool = True) -> str:
        """
        保存报告到文件
        
        Args:
            output_dir: 输出目录
            filename: 文件名 (不含扩展名)，默认使用时间戳
            format: 报告格式
            save_latest: 是否同时保存 latest 副本
            
        Returns:
            str: 保存的文件路径
        """
        # 确保目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成报告内容
        content = self.generate(format)
        
        # 构建文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self._get_report_type()}_{timestamp}"
        
        file_ext = format.value
        file_path = output_path / f"{filename}.{file_ext}"
        
        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 保存 latest 副本
        if save_latest:
            latest_path = output_path / f"{self._get_report_type()}_latest.{file_ext}"
            with open(latest_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        return str(file_path)
    
    @abstractmethod
    def _get_report_type(self) -> str:
        """获取报告类型标识"""
        pass
    
    def _format_line(self, content: str, width: int = 70, char: str = "=") -> str:
        """格式化分隔线"""
        return char * width
    
    def _format_section(self, title: str, width: int = 70) -> str:
        """格式化章节标题"""
        return f"\n{self._format_line('', width)}\n【{title}】\n{self._format_line('', width)}"

