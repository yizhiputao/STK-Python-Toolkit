"""
地面站组件模块
负责地面站的创建和配置
"""

from typing import Any, Dict, Optional, List
from .base import ComponentBase, ComponentType
from ..core.connection import STKConnection
from ..core.exceptions import STKComponentError


class FacilityComponent(ComponentBase):
    """
    地面站组件类
    
    支持:
    - 创建地面站
    - 配置位置（经纬度、海拔）
    - 配置访问约束
    - 获取地面站信息
    
    使用示例:
        # 代码方式创建
        fac = FacilityComponent(connection, "Beijing")
        fac.create(
            latitude=40.0,
            longitude=116.0,
            altitude=0.05  # km
        )
        
        # 添加约束
        fac.set_constraint("ElevationAngle", min_value=10.0)
        
        # JSON 方式创建
        config = {
            "name": "Beijing",
            "position": {
                "latitude": 40.0,
                "longitude": 116.0,
                "altitude": 0.05
            },
            "constraints": [
                {"name": "ElevationAngle", "min": 10.0},
                {"name": "SunElevationAngle", "min": -90.0, "max": 0.0}
            ]
        }
        fac = FacilityComponent.from_dict(connection, config)
    """
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.FACILITY
    
    def _get_stk_object_type(self) -> int:
        """返回 STK 地面站对象类型"""
        # eFacility = 8
        return 8
    
    def _get_interface(self) -> Any:
        """获取 IAgFacility 接口"""
        stk_objects = self._connection.stk_objects
        return self._stk_object.QueryInterface(stk_objects.IAgFacility)
    
    def _configure(self, **kwargs):
        """
        配置地面站参数
        
        Args:
            latitude: 纬度 (deg)
            longitude: 经度 (deg)
            altitude: 海拔 (km)
            constraints: 约束列表
        """
        # 设置位置
        latitude = kwargs.get("latitude", 0.0)
        longitude = kwargs.get("longitude", 0.0)
        altitude = kwargs.get("altitude", 0.0)
        
        position = self._interface.Position
        position.AssignGeodetic(latitude, longitude, altitude)
        
        # 设置约束
        constraints = kwargs.get("constraints", [])
        for constraint in constraints:
            self.set_constraint(
                constraint.get("name"),
                min_value=constraint.get("min"),
                max_value=constraint.get("max")
            )
    
    def set_position(self, latitude: float, longitude: float, altitude: float = 0.0):
        """
        设置地面站位置
        
        Args:
            latitude: 纬度 (deg)
            longitude: 经度 (deg)
            altitude: 海拔 (km)
        """
        if not self._interface:
            raise STKComponentError("地面站未创建或未加载")
        
        position = self._interface.Position
        position.AssignGeodetic(latitude, longitude, altitude)
    
    def set_constraint(self, name: str, min_value: Optional[float] = None, 
                       max_value: Optional[float] = None):
        """
        设置访问约束
        
        Args:
            name: 约束名称，如 "ElevationAngle", "SunElevationAngle" 等
            min_value: 最小值
            max_value: 最大值
        """
        if not self._interface:
            raise STKComponentError("地面站未创建或未加载")
        
        stk_objects = self._connection.stk_objects
        
        try:
            ac = self._interface.AccessConstraints
            constraint = ac.GetActiveConstraint(name)
            minmax = constraint.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
            
            if min_value is not None:
                minmax.EnableMin = True
                minmax.Min = min_value
            
            if max_value is not None:
                minmax.EnableMax = True
                minmax.Max = max_value
                
        except Exception as e:
            raise STKComponentError(f"设置约束 '{name}' 失败: {e}")
    
    def enable_line_of_sight(self, enabled: bool = True):
        """
        启用/禁用视线约束
        
        Args:
            enabled: 是否启用
        """
        if not self._interface:
            raise STKComponentError("地面站未创建或未加载")
        
        try:
            ac = self._interface.AccessConstraints
            los = ac.GetActiveConstraint("LineOfSight")
            # LineOfSight 约束通常没有 min/max，只有启用/禁用
            # 它的存在本身就表示启用
        except Exception as e:
            raise STKComponentError(f"设置 LineOfSight 约束失败: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取地面站详细信息
        
        Returns:
            dict: 地面站信息
        """
        if not self._interface:
            return {"name": self._name, "status": "not_loaded"}
        
        info = {
            "name": self._name,
            "position": self._get_position_info(),
            "constraints": self._get_constraints_info()
        }
        return info
    
    def _get_position_info(self) -> Dict[str, Any]:
        """获取位置信息"""
        position_info = {}
        
        try:
            position = self._interface.Position
            coords = position.QueryPlanetodetic()
            position_info = {
                "latitude": coords[0],
                "longitude": coords[1],
                "altitude": coords[2]
            }
        except Exception as e:
            position_info["error"] = str(e)
        
        return position_info
    
    def _get_constraints_info(self) -> List[Dict[str, Any]]:
        """获取访问约束信息"""
        stk_objects = self._connection.stk_objects
        constraints = []
        
        try:
            ac = self._interface.AccessConstraints
            for i in range(ac.Count):
                c = ac.Item(i)
                name = c.ConstraintName
                ctype = c.ConstraintType
                
                # LineOfSight 约束 (type 26)
                if ctype == 26:
                    constraints.append({
                        "name": name,
                        "type": "LineOfSight",
                        "enabled": True
                    })
                    continue
                
                # MinMax 类型约束
                try:
                    minmax = c.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
                    if minmax.EnableMin or minmax.EnableMax:
                        constraint = {"name": name}
                        if minmax.EnableMin:
                            constraint["min"] = minmax.Min
                        if minmax.EnableMax:
                            constraint["max"] = minmax.Max
                        constraints.append(constraint)
                except:
                    pass
                    
        except:
            pass
        
        return constraints
    
    @classmethod
    def from_dict(cls, connection: STKConnection, config: Dict[str, Any]) -> "FacilityComponent":
        """
        从字典配置创建地面站
        
        Args:
            connection: STK 连接
            config: 配置字典，格式如下:
                {
                    "name": "Beijing",
                    "position": {
                        "latitude": 40.0,
                        "longitude": 116.0,
                        "altitude": 0.05  # km, 可选
                    },
                    "constraints": [  # 可选
                        {"name": "ElevationAngle", "min": 10.0},
                        {"name": "SunElevationAngle", "min": -90.0, "max": 0.0}
                    ]
                }
        """
        name = config.get("name")
        if not name:
            raise STKComponentError("地面站配置必须包含 'name' 字段")
        
        # 解析位置
        position = config.get("position", {})
        
        facility = cls(connection, name)
        facility.create(
            latitude=position.get("latitude", 0.0),
            longitude=position.get("longitude", 0.0),
            altitude=position.get("altitude", 0.0),
            constraints=config.get("constraints", [])
        )
        
        return facility

