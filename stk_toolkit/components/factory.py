"""
组件工厂模块
统一的组件创建接口，支持从 JSON/字典配置批量创建组件
"""

import json
from typing import Any, Dict, List, Union
from pathlib import Path
from .base import ComponentBase, ComponentType
from .satellite import SatelliteComponent
from .facility import FacilityComponent
from ..core.connection import STKConnection
from ..core.exceptions import STKComponentError


class ComponentFactory:
    """
    组件工厂类
    
    提供统一的组件创建接口，支持:
    - 从字典创建单个组件
    - 从 JSON 文件批量创建组件
    - 注册自定义组件类型
    
    使用示例:
        factory = ComponentFactory(connection)
        
        # 创建单个组件
        sat = factory.create({
            "type": "Satellite",
            "name": "MySat",
            "orbit": {"semi_major_axis": 7000, ...}
        })
        
        # 从 JSON 文件创建
        components = factory.create_from_json("scenario_config.json")
    """
    
    # 组件类型注册表
    _component_classes = {
        ComponentType.SATELLITE: SatelliteComponent,
        ComponentType.FACILITY: FacilityComponent,
        # 预留其他组件类型
        # ComponentType.SENSOR: SensorComponent,
        # ComponentType.TRANSMITTER: TransmitterComponent,
        # ComponentType.RECEIVER: ReceiverComponent,
        # ComponentType.ANTENNA: AntennaComponent,
        # ComponentType.TARGET: TargetComponent,
        # ComponentType.AREA_TARGET: AreaTargetComponent,
        # ComponentType.AIRCRAFT: AircraftComponent,
        # ComponentType.SHIP: ShipComponent,
        # ComponentType.GROUND_VEHICLE: GroundVehicleComponent,
        # ComponentType.LAUNCH_VEHICLE: LaunchVehicleComponent,
        # ComponentType.MISSILE: MissileComponent,
    }
    
    # 类型名称映射
    _type_name_map = {
        "Satellite": ComponentType.SATELLITE,
        "satellite": ComponentType.SATELLITE,
        "Facility": ComponentType.FACILITY,
        "facility": ComponentType.FACILITY,
        "GroundStation": ComponentType.FACILITY,
        "ground_station": ComponentType.FACILITY,
        # 预留其他类型映射
        # "Sensor": ComponentType.SENSOR,
        # "Target": ComponentType.TARGET,
        # ...
    }
    
    def __init__(self, connection: STKConnection):
        """
        初始化工厂
        
        Args:
            connection: STK 连接对象
        """
        self._connection = connection
        self._created_components: List[ComponentBase] = []
    
    @classmethod
    def register_component(cls, component_type: ComponentType, component_class: type):
        """
        注册新的组件类型
        
        Args:
            component_type: 组件类型枚举
            component_class: 组件类
        """
        cls._component_classes[component_type] = component_class
    
    @classmethod
    def register_type_name(cls, name: str, component_type: ComponentType):
        """
        注册类型名称映射
        
        Args:
            name: 类型名称字符串
            component_type: 组件类型枚举
        """
        cls._type_name_map[name] = component_type
    
    def create(self, config: Dict[str, Any]) -> ComponentBase:
        """
        从配置字典创建组件
        
        Args:
            config: 配置字典，必须包含 "type" 和 "name" 字段
            
        Returns:
            ComponentBase: 创建的组件
        """
        type_str = config.get("type")
        if not type_str:
            raise STKComponentError("组件配置必须包含 'type' 字段")
        
        component_type = self._type_name_map.get(type_str)
        if component_type is None:
            raise STKComponentError(f"未知的组件类型: {type_str}")
        
        component_class = self._component_classes.get(component_type)
        if component_class is None:
            raise STKComponentError(f"组件类型 '{type_str}' 尚未实现")
        
        component = component_class.from_dict(self._connection, config)
        self._created_components.append(component)
        
        return component
    
    def create_many(self, configs: List[Dict[str, Any]]) -> List[ComponentBase]:
        """
        批量创建组件
        
        Args:
            configs: 配置字典列表
            
        Returns:
            list: 创建的组件列表
        """
        components = []
        for config in configs:
            component = self.create(config)
            components.append(component)
        return components
    
    def create_from_json(self, json_path: Union[str, Path]) -> List[ComponentBase]:
        """
        从 JSON 文件创建组件
        
        JSON 文件格式:
        {
            "components": [
                {
                    "type": "Satellite",
                    "name": "Sat1",
                    ...
                },
                {
                    "type": "Facility",
                    "name": "Beijing",
                    ...
                }
            ]
        }
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            list: 创建的组件列表
        """
        path = Path(json_path)
        if not path.exists():
            raise STKComponentError(f"JSON 文件不存在: {json_path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise STKComponentError(f"JSON 解析失败: {e}")
        
        configs = data.get("components", [])
        if not configs:
            raise STKComponentError("JSON 文件中没有找到 'components' 字段")
        
        return self.create_many(configs)
    
    def create_from_json_string(self, json_str: str) -> List[ComponentBase]:
        """
        从 JSON 字符串创建组件
        
        Args:
            json_str: JSON 字符串
            
        Returns:
            list: 创建的组件列表
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise STKComponentError(f"JSON 解析失败: {e}")
        
        configs = data.get("components", [])
        return self.create_many(configs)
    
    def get_created_components(self) -> List[ComponentBase]:
        """获取已创建的组件列表"""
        return self._created_components.copy()
    
    def clear_created_components(self):
        """清空已创建组件记录（不删除 STK 中的组件）"""
        self._created_components.clear()
    
    def delete_all_created(self):
        """删除所有已创建的组件"""
        for component in self._created_components:
            try:
                component.delete()
            except:
                pass
        self._created_components.clear()
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """获取支持的组件类型列表"""
        return list(cls._type_name_map.keys())

