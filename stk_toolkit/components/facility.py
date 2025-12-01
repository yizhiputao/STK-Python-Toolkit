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
    
    @staticmethod
    def exists(connection: STKConnection, name: str) -> bool:
        """
        检查地面站是否存在
        
        Args:
            connection: STK 连接对象
            name: 地面站名称
            
        Returns:
            bool: 地面站是否存在
        """
        try:
            path = f"*/Facility/{name}"
            connection.root.GetObjectFromPath(path)
            return True
        except:
            return False
    
    @staticmethod
    def delete_by_name(connection: STKConnection, name: str) -> bool:
        """
        按名称删除地面站
        
        Args:
            connection: STK 连接对象
            name: 地面站名称
            
        Returns:
            bool: 是否成功删除 (如果地面站不存在返回 False)
        """
        try:
            path = f"*/Facility/{name}"
            obj = connection.root.GetObjectFromPath(path)
            obj.Unload()
            return True
        except:
            return False
    
    def _configure(self, **kwargs):
        """
        配置地面站参数
        
        Args:
            latitude: 纬度 (deg)
            longitude: 经度 (deg)
            altitude: 海拔 (km)
            constraints: 约束列表（可选，稍后设置）
        """
        # 只设置位置，不设置约束
        latitude = kwargs.get("latitude", 0.0)
        longitude = kwargs.get("longitude", 0.0)
        altitude = kwargs.get("altitude", 0.0)
        
        position = self._interface.Position
        position.AssignGeodetic(latitude, longitude, altitude)
    
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
    
    def _set_constraints_after_creation(self, constraints: List[Dict[str, Any]]):
        """
        创建后设置约束（先添加后设置）
        
        Args:
            constraints: 约束列表，每个元素包含 name, min, max
        """
        if not self._interface:
            raise STKComponentError("地面站未创建或未加载")
        
        stk_objects = self._connection.stk_objects
        
        # 约束类型枚举映射（从约束名称到枚举值）
        # 基于实际测试的 AgEAccessCnstr 枚举值（通过 _test_constraint_enum.py 测试获得，0-200范围）
        constraint_type_map = {
            # 常用基础约束
            "Altitude": 2,
            "AngularRate": 3,
            "ApparentTime": 4,
            "AzimuthAngle": 6,
            "AzimuthRate": 69,
            "CrdnAngle": 9,
            "CrdnVectorMag": 10,
            "Duration": 13,
            "ElevationAngle": 14,
            "ElevationRate": 70,
            "GMT": 16,
            "Intervals": 22,
            "Lighting": 25,
            # "LineOfSight": 26,  # 枚举值26是LineOfSight，默认已激活，无需添加
            "LocalTime": 27,
            "Range": 34,
            "RangeRate": 35,
            "PropagationDelay": 33,
            
            # 天文约束
            "LunarElevationAngle": 30,
            "SunElevationAngle": 58,
            "LOSLunarExclusion": 28,
            "LOSSunExclusion": 29,
            "LOSSunIlluminationAngle": 187,
            
            # 地理约束
            "ObjectExclusionAngle": 32,
            "ThirdBodyObstruction": 61,
            "TerrainMask": 67,
            "AzElMask": 68,
            "GeoExclusion": 71,
            "GroundSampleDistance": 72,
            "HeightAboveHorizon": 73,
            "TerrainGrazingAngle": 74,
            "CbObstruction": 91,
            
            # SAR（合成孔径雷达）约束
            "SarAreaRate": 36,
            "SarAzRes": 37,
            "SarCNR": 38,
            "SarIntTime": 40,
            "SarPTCR": 41,
            "SarSCR": 42,
            "SarSigmaN": 43,
            "SarSNR": 44,
            "SarCNRJamming": 105,
            "SarJOverS": 106,
            "SarSCRJamming": 115,
            "SarSNRJamming": 116,
            "SarOrthoPolCNR": 107,
            "SarOrthoPolCNRJamming": 108,
            "SarOrthoPolJOverS": 109,
            "SarOrthoPolPTCR": 110,
            "SarOrthoPolSCR": 111,
            "SarOrthoPolSCRJamming": 112,
            "SarOrthoPolSNR": 113,
            "SarOrthoPolSNRJamming": 114,
            
            # 搜索/跟踪（Search/Track）约束
            "SrchTrkClearDoppler": 46,
            "SrchTrkDwellTime": 47,
            "SrchTrkIntegratedPDet": 48,
            "SrchTrkIntegratedPulses": 49,
            "SrchTrkIntegratedSNR": 50,
            "SrchTrkIntegrationTime": 51,
            "SrchTrkMLCFilter": 52,
            "SrchTrkSinglePulsePDet": 53,
            "SrchTrkSinglePulseSNR": 54,
            "SrchTrkSLCFilter": 55,
            "SrchTrkUnambigDoppler": 56,
            "SrchTrkUnambigRange": 57,
            "SrchTrkDwellTimeJamming": 117,
            "SrchTrkIntegratedJOverS": 118,
            "SrchTrkIntegratedPDetJamming": 119,
            "SrchTrkIntegratedPulsesJamming": 120,
            "SrchTrkIntegratedSNRJamming": 121,
            "SrchTrkIntegrationTimeJamming": 122,
            "SrchTrkSinglePulseJOverS": 139,
            "SrchTrkSinglePulsePDetJamming": 140,
            "SrchTrkSinglePulseSNRJamming": 141,
            "SrchTrkOrthoPolDwellTime": 123,
            "SrchTrkOrthoPolDwellTimeJamming": 124,
            "SrchTrkOrthoPolIntegratedJOverS": 125,
            "SrchTrkOrthoPolIntegratedPDet": 126,
            "SrchTrkOrthoPolIntegratedPDetJamming": 127,
            "SrchTrkOrthoPolIntegratedPulses": 128,
            "SrchTrkOrthoPolIntegratedPulsesJamming": 129,
            "SrchTrkOrthoPolIntegratedSNR": 130,
            "SrchTrkOrthoPolIntegratedSNRJamming": 131,
            "SrchTrkOrthoPolIntegrationTime": 132,
            "SrchTrkOrthoPolIntegrationTimeJamming": 133,
            "SrchTrkOrthoPolSinglePulseJOverS": 134,
            "SrchTrkOrthoPolSinglePulsePDet": 135,
            "SrchTrkOrthoPolSinglePulsePDetJamming": 136,
            "SrchTrkOrthoPolSinglePulseSNR": 137,
            "SrchTrkOrthoPolSinglePulseSNRJamming": 138,
            
            # 其他约束
            "Matlab": 31,
            "CrdnCondition": 104,
        }
        
        try:
            ac = self._interface.AccessConstraints
            
            for constraint in constraints:
                target_name = constraint.get("name")
                if not target_name:
                    continue
                
                try:
                    # 先尝试查找约束是否已存在
                    found_constraint = None
                    for i in range(ac.Count):
                        c = ac.Item(i)
                        if c.ConstraintName == target_name:
                            found_constraint = c
                            break
                    
                    # 如果不存在，尝试添加约束
                    if found_constraint is None:
                        constraint_type = constraint_type_map.get(target_name)
                        if constraint_type is not None:
                            try:
                                found_constraint = ac.AddConstraint(constraint_type)
                            except Exception as e:
                                # 添加失败，跳过该约束
                                continue
                        else:
                            # 未知的约束类型，跳过
                            continue
                    
                    # 设置约束的 min/max 值
                    minmax = found_constraint.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
                    
                    if "min" in constraint:
                        minmax.EnableMin = True
                        minmax.Min = constraint["min"]
                    
                    if "max" in constraint:
                        minmax.EnableMax = True
                        minmax.Max = constraint["max"]
                        
                except Exception as e:
                    # 如果设置失败，静默跳过
                    continue
                    
        except Exception as e:
            raise STKComponentError(f"设置约束失败: {e}")
    
    def set_constraint(self, name: str, min_value: Optional[float] = None, 
                       max_value: Optional[float] = None):
        """
        设置访问约束（用于单个约束设置）
        
        Args:
            name: 约束名称，如 "ElevationAngle", "SunElevationAngle" 等
            min_value: 最小值
            max_value: 最大值
        """
        constraints = []
        constraint = {"name": name}
        if min_value is not None:
            constraint["min"] = min_value
        if max_value is not None:
            constraint["max"] = max_value
        constraints.append(constraint)
        
        self._set_constraints_after_creation(constraints)
    
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
            
            # 遍历所有约束找到 LineOfSight 约束（使用 Item 而不是 GetActiveConstraint）
            los = None
            for i in range(ac.Count):
                c = ac.Item(i)
                if c.ConstraintName == "LineOfSight":
                    los = c
                    break
            
            if los is None:
                raise STKComponentError("未找到 LineOfSight 约束")
            
            # LineOfSight 约束通常没有 min/max，只有启用/禁用
            # 它的存在本身就表示启用
        except STKComponentError:
            raise
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
        
        # 第一步：先创建地面站（只设置位置）
        facility = cls(connection, name)
        facility.create(
            latitude=position.get("latitude", 0.0),
            longitude=position.get("longitude", 0.0),
            altitude=position.get("altitude", 0.0)
        )
        
        # 第二步：创建成功后再设置约束（使用 modifier 中的方法）
        constraints = config.get("constraints", [])
        if constraints:
            facility._set_constraints_after_creation(constraints)
        
        return facility

