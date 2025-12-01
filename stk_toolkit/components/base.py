"""
组件基类
定义所有 STK 组件的通用接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from ..core.connection import STKConnection
from ..core.exceptions import STKComponentError


class ComponentType(Enum):
    """STK 组件类型枚举"""
    SATELLITE = "Satellite"
    FACILITY = "Facility"
    SENSOR = "Sensor"
    TRANSMITTER = "Transmitter"
    RECEIVER = "Receiver"
    ANTENNA = "Antenna"
    TARGET = "Target"
    AREA_TARGET = "AreaTarget"
    AIRCRAFT = "Aircraft"
    SHIP = "Ship"
    GROUND_VEHICLE = "GroundVehicle"
    LAUNCH_VEHICLE = "LaunchVehicle"
    MISSILE = "Missile"
    PLANET = "Planet"
    STAR = "Star"
    # 可以继续扩展其他类型


class ComponentBase(ABC):
    """
    组件基类
    
    所有 STK 组件的抽象基类，定义通用接口
    """
    
    def __init__(self, connection: STKConnection, name: str):
        """
        初始化组件
        
        Args:
            connection: STK 连接对象
            name: 组件名称
        """
        self._connection = connection
        self._name = name
        self._stk_object = None
        self._interface = None
    
    @property
    @abstractmethod
    def component_type(self) -> ComponentType:
        """返回组件类型"""
        pass
    
    @property
    def name(self) -> str:
        """获取组件名称"""
        return self._name
    
    @property
    def stk_object(self) -> Any:
        """获取 STK 原生对象"""
        return self._stk_object
    
    @property
    def interface(self) -> Any:
        """获取组件特定接口"""
        return self._interface
    
    @property
    def path(self) -> str:
        """获取组件完整路径"""
        if self._stk_object:
            return self._stk_object.Path
        return f"{self.component_type.value}/{self._name}"
    
    def create(self, **kwargs) -> "ComponentBase":
        """
        在 STK 中创建组件
        
        Returns:
            self: 返回自身以支持链式调用
        """
        try:
            scenario = self._connection.current_scenario
            self._stk_object = scenario.Children.New(
                self._get_stk_object_type(),
                self._name
            )
            self._interface = self._get_interface()
            self._configure(**kwargs)
        except Exception as e:
            raise STKComponentError(f"创建 {self.component_type.value} '{self._name}' 失败: {e}")
        return self
    
    def load_from_existing(self) -> "ComponentBase":
        """
        从已存在的 STK 对象加载
        
        Returns:
            self: 返回自身以支持链式调用
        """
        try:
            path = f"*/{self.component_type.value}/{self._name}"
            self._stk_object = self._connection.root.GetObjectFromPath(path)
            self._interface = self._get_interface()
        except Exception as e:
            raise STKComponentError(f"加载 {self.component_type.value} '{self._name}' 失败: {e}")
        return self
    
    @abstractmethod
    def _get_stk_object_type(self) -> int:
        """返回 STK 对象类型常量"""
        pass
    
    @abstractmethod
    def _get_interface(self) -> Any:
        """获取组件特定接口"""
        pass
    
    def _configure(self, **kwargs):
        """
        配置组件参数，子类可重写
        
        Args:
            **kwargs: 配置参数
        """
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        获取组件信息
        
        Returns:
            dict: 组件信息字典
        """
        pass
    
    def delete(self):
        """删除组件"""
        if self._stk_object:
            try:
                self._stk_object.Unload()
                self._stk_object = None
                self._interface = None
            except Exception as e:
                raise STKComponentError(f"删除 {self.component_type.value} '{self._name}' 失败: {e}")
    
    @classmethod
    @abstractmethod
    def from_dict(cls, connection: STKConnection, config: Dict[str, Any]) -> "ComponentBase":
        """
        从字典配置创建组件
        
        Args:
            connection: STK 连接
            config: 配置字典
            
        Returns:
            ComponentBase: 组件实例
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将组件导出为字典配置
        
        Returns:
            dict: 配置字典
        """
        return {
            "type": self.component_type.value,
            "name": self._name,
            **self.get_info()
        }

