"""
地面站修改器模块
提供修改地面站参数的功能
"""

from typing import Any, Dict, Optional, List
from .base import ModifierBase
from ..core.connection import STKConnection
from ..core.exceptions import STKModifyError


class FacilityModifier(ModifierBase):
    """
    地面站修改器
    
    支持修改:
    - 位置信息
    - 访问约束
    
    使用示例:
        modifier = FacilityModifier(connection)
        modifier.load("Facility1")
        
        # 方式1: 批量修改
        modifier.apply({
            "position": {
                "latitude": 39.9,
                "longitude": 116.4
            },
            "constraints": [
                {"name": "ElevationAngle", "min": 15.0}
            ]
        })
        
        # 方式2: 单个修改
        modifier.set("position.latitude", 39.9)
        
        # 方式3: 直接调用方法
        modifier.set_position(latitude=39.9, longitude=116.4, altitude=0.1)
        modifier.set_constraint("ElevationAngle", min_value=15.0)
    """
    
    def load(self, name: str) -> "FacilityModifier":
        """
        加载地面站对象
        
        Args:
            name: 地面站名称
        """
        stk_objects = self._connection.stk_objects
        
        try:
            path = f"*/Facility/{name}"
            self._target = self._connection.root.GetObjectFromPath(path)
            self._interface = self._target.QueryInterface(stk_objects.IAgFacility)
        except Exception as e:
            raise STKModifyError(f"加载地面站 '{name}' 失败: {e}")
        
        return self
    
    def apply(self, changes: Dict[str, Any]) -> "FacilityModifier":
        """
        应用修改
        
        Args:
            changes: 修改内容，支持的键:
                - position: 位置 (latitude, longitude, altitude)
                - constraints: 约束列表
        """
        self._ensure_loaded()
        
        if "position" in changes:
            self._apply_position_changes(changes["position"])
        
        if "constraints" in changes:
            self._apply_constraint_changes(changes["constraints"])
        
        return self
    
    def set_position(self, latitude: Optional[float] = None, 
                     longitude: Optional[float] = None,
                     altitude: Optional[float] = None) -> "FacilityModifier":
        """
        设置位置
        
        Args:
            latitude: 纬度 (deg)
            longitude: 经度 (deg)
            altitude: 海拔 (km)
        """
        self._ensure_loaded()
        
        # 获取当前位置
        try:
            position = self._interface.Position
            coords = position.QueryPlanetodetic()
            current_lat = coords[0]
            current_lon = coords[1]
            current_alt = coords[2]
        except:
            current_lat = 0.0
            current_lon = 0.0
            current_alt = 0.0
        
        # 合并修改
        new_lat = latitude if latitude is not None else current_lat
        new_lon = longitude if longitude is not None else current_lon
        new_alt = altitude if altitude is not None else current_alt
        
        try:
            position.AssignGeodetic(new_lat, new_lon, new_alt)
        except Exception as e:
            raise STKModifyError(f"设置位置失败: {e}")
        
        return self
    
    def set_constraint(self, name: str, 
                       min_value: Optional[float] = None,
                       max_value: Optional[float] = None,
                       disable_min: bool = False,
                       disable_max: bool = False) -> "FacilityModifier":
        """
        设置单个约束
        
        Args:
            name: 约束名称
            min_value: 最小值
            max_value: 最大值
            disable_min: 是否禁用最小值约束
            disable_max: 是否禁用最大值约束
        """
        self._ensure_loaded()
        
        constraint = {"name": name}
        if min_value is not None:
            constraint["min"] = min_value
        if max_value is not None:
            constraint["max"] = max_value
        if disable_min:
            constraint["disable_min"] = True
        if disable_max:
            constraint["disable_max"] = True
        
        self._apply_constraint_changes([constraint])
        return self
    
    def set_constraints(self, constraints: List[Dict[str, Any]]) -> "FacilityModifier":
        """
        批量设置约束
        
        Args:
            constraints: 约束列表，每个约束是一个字典:
                {"name": "ElevationAngle", "min": 10.0, "max": 90.0}
        """
        return self.apply({"constraints": constraints})
    
    def _apply_position_changes(self, position_params: Dict[str, Any]):
        """应用位置修改"""
        self.set_position(
            latitude=position_params.get("latitude"),
            longitude=position_params.get("longitude"),
            altitude=position_params.get("altitude")
        )
    
    def _apply_constraint_changes(self, constraints: List[Dict[str, Any]]):
        """应用约束修改"""
        stk_objects = self._connection.stk_objects
        
        try:
            ac = self._interface.AccessConstraints
            
            for constraint in constraints:
                name = constraint.get("name")
                if not name:
                    continue
                
                try:
                    c = ac.GetActiveConstraint(name)
                    minmax = c.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
                    
                    if "min" in constraint:
                        minmax.EnableMin = True
                        minmax.Min = constraint["min"]
                    elif constraint.get("disable_min"):
                        minmax.EnableMin = False
                    
                    if "max" in constraint:
                        minmax.EnableMax = True
                        minmax.Max = constraint["max"]
                    elif constraint.get("disable_max"):
                        minmax.EnableMax = False
                        
                except Exception as e:
                    # 某些约束可能不支持 MinMax 接口，跳过
                    continue
                    
        except Exception as e:
            raise STKModifyError(f"修改约束失败: {e}")

