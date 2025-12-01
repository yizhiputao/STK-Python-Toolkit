"""
修改器基类
定义组件修改的通用接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..core.connection import STKConnection
from ..core.exceptions import STKModifyError


class ModifierBase(ABC):
    """
    修改器基类
    
    所有组件修改器的抽象基类
    """
    
    def __init__(self, connection: STKConnection):
        """
        初始化修改器
        
        Args:
            connection: STK 连接对象
        """
        self._connection = connection
        self._target = None
        self._interface = None
    
    @abstractmethod
    def load(self, name: str) -> "ModifierBase":
        """
        加载要修改的对象
        
        Args:
            name: 对象名称
            
        Returns:
            self: 返回自身以支持链式调用
        """
        pass
    
    @abstractmethod
    def apply(self, changes: Dict[str, Any]) -> "ModifierBase":
        """
        应用修改
        
        Args:
            changes: 修改内容字典
            
        Returns:
            self: 返回自身以支持链式调用
        """
        pass
    
    def set(self, property_path: str, value: Any) -> "ModifierBase":
        """
        设置单个属性
        
        Args:
            property_path: 属性路径，如 "orbit.semi_major_axis"
            value: 属性值
            
        Returns:
            self: 返回自身以支持链式调用
        """
        changes = self._build_nested_dict(property_path, value)
        return self.apply(changes)
    
    def _build_nested_dict(self, path: str, value: Any) -> Dict[str, Any]:
        """
        构建嵌套字典
        
        Args:
            path: 点分隔的路径
            value: 值
            
        Returns:
            dict: 嵌套字典
        """
        keys = path.split(".")
        result = {}
        current = result
        
        for key in keys[:-1]:
            current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return result
    
    def _ensure_loaded(self):
        """确保对象已加载"""
        if self._target is None:
            raise STKModifyError("未加载目标对象，请先调用 load() 方法")

