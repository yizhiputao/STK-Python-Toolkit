"""
卫星组件模块
负责卫星的创建，配置和删除
"""

from typing import Any, Dict, Optional

from comtypes import COMError
from .base import ComponentBase, ComponentType
from ..core.connection import STKConnection
from ..core.exceptions import STKComponentError


class PropagatorType:
    """轨道传播器类型"""
    HPOP = 0  # High Precision Orbit Propagator
    J2_PERTURBATION = 1
    J4_PERTURBATION = 2
    SGP4 = 3
    SPK = 4
    TWO_BODY = 5
    
    NAMES = {
        0: "HPOP (High Precision)",
        1: "J2Perturbation",
        2: "J4Perturbation",
        3: "SGP4",
        4: "SPK",
        5: "TwoBody"
    }


class SatelliteComponent(ComponentBase):
    @staticmethod
    def _safe_qi(obj: Any, interface: Any) -> Any:
        """在 QueryInterface 不可用时返回原对象"""
        if obj is None or interface is None:
            return obj
        try:
            return obj.QueryInterface(interface)
        except (AttributeError, COMError):
            return obj

    """
    卫星组件类
    
    支持:
    - 创建卫星
    - 配置轨道参数（经典六根数）
    - 配置传播器
    - 获取卫星信息
    
    使用示例:
        # 代码方式创建
        sat = SatelliteComponent(connection, "MySat")
        sat.create(
            propagator=PropagatorType.J2_PERTURBATION,
            semi_major_axis=7000,
            eccentricity=0.001,
            inclination=98.0,
            raan=0,
            arg_of_perigee=0,
            true_anomaly=0
        )
        
        # JSON 方式创建
        config = {
            "name": "MySat",
            "propagator": "J2Perturbation",
            "orbit": {
                "semi_major_axis": 7000,
                "eccentricity": 0.001,
                "inclination": 98.0,
                "raan": 0,
                "arg_of_perigee": 0,
                "true_anomaly": 0
            }
        }
        sat = SatelliteComponent.from_dict(connection, config)
    """
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.SATELLITE
    
    def _get_stk_object_type(self) -> int:
        """返回 STK 卫星对象类型"""
        # eSatellite = 18
        return 18
    
    def _get_interface(self) -> Any:
        """获取 IAgSatellite 接口"""
        stk_objects = self._connection.stk_objects
        return self._stk_object.QueryInterface(stk_objects.IAgSatellite)
    
    @staticmethod
    def exists(connection: STKConnection, name: str) -> bool:
        """
        检查卫星是否存在
        
        Args:
            connection: STK 连接对象
            name: 卫星名称
            
        Returns:
            bool: 卫星是否存在
        """
        try:
            path = f"*/Satellite/{name}"
            connection.root.GetObjectFromPath(path)
            return True
        except:
            return False
    
    @staticmethod
    def delete_by_name(connection: STKConnection, name: str) -> bool:
        """
        按名称删除卫星
        
        Args:
            connection: STK 连接对象
            name: 卫星名称
            
        Returns:
            bool: 是否成功删除 (如果卫星不存在返回 False)
        """
        try:
            path = f"*/Satellite/{name}"
            obj = connection.root.GetObjectFromPath(path)
            obj.Unload()
            return True
        except:
            return False
    
    def _configure(self, **kwargs):
        """
        配置卫星参数
        
        Args:
            propagator: 传播器类型
            semi_major_axis: 半长轴 (km)
            eccentricity: 偏心率
            inclination: 轨道倾角 (deg)
            raan: 升交点赤经 (deg)
            arg_of_perigee: 近地点幅角 (deg)
            true_anomaly: 真近点角 (deg)
            step: 传播步长 (sec)
        """
        propagator = kwargs.get("propagator", PropagatorType.J2_PERTURBATION)
        
        # 设置传播器类型
        self._interface.SetPropagatorType(propagator)
        
        # 配置轨道参数
        if propagator == PropagatorType.J2_PERTURBATION:
            self._configure_j2_orbit(**kwargs)
        elif propagator == PropagatorType.TWO_BODY:
            self._configure_two_body_orbit(**kwargs)
        # 可以扩展其他传播器类型
    
    def _configure_j2_orbit(self, **kwargs):
        """配置 J2 传播器轨道参数（经典轨道根数）"""
        stk_objects = self._connection.stk_objects
        
        propagator = self._interface.Propagator
        j2 = self._safe_qi(propagator, stk_objects.IAgVePropagatorJ2Perturbation)
        
        # 设置步长
        step = kwargs.get("step", 60.0)
        j2.Step = step
        
        # 获取初始状态
        init_state = j2.InitialState
        rep = init_state.Representation
        
        # 转换为经典轨道根数
        classic = rep.ConvertTo(1)  # eOrbitStateClassical
        classic_orbit = self._safe_qi(classic, stk_objects.IAgOrbitStateClassical)
        
        # 设置坐标系
        classic_orbit.CoordinateSystemType = 0  # eCoordinateSystemJ2000
        
        # 设置半长轴和偏心率（必须先设置 SizeShapeType）
        semi_major_axis = kwargs.get("semi_major_axis", 7000)
        eccentricity = kwargs.get("eccentricity", 0.0)
        
        classic_orbit.SizeShapeType = 4  # eSizeShapeSemimajorAxis
        ss = self._safe_qi(classic_orbit.SizeShape, stk_objects.IAgClassicalSizeShapeSemimajorAxis)
        ss.SemiMajorAxis = semi_major_axis
        ss.Eccentricity = eccentricity
        
        # 设置轨道方向
        orientation = classic_orbit.Orientation
        orientation.Inclination = kwargs.get("inclination", 0.0)
        orientation.ArgOfPerigee = kwargs.get("arg_of_perigee", 0.0)
        
        # 设置 RAAN
        orientation.AscNodeType = 1  # eAscNodeRAAN
        ascnode = self._safe_qi(orientation.AscNode, stk_objects.IAgOrientationAscNodeRAAN)
        ascnode.Value = kwargs.get("raan", 0.0)
        
        # 设置真近点角
        classic_orbit.LocationType = 5  # eLocationTrueAnomaly
        location = self._safe_qi(classic_orbit.Location, stk_objects.IAgClassicalLocationTrueAnomaly)
        location.Value = kwargs.get("true_anomaly", 0.0)
        
        # 应用更改
        init_state.Representation.Assign(classic)
        j2.Propagate()
    
    def _configure_two_body_orbit(self, **kwargs):
        """配置 TwoBody 传播器轨道参数"""
        stk_objects = self._connection.stk_objects
        
        propagator = self._interface.Propagator
        two_body = self._safe_qi(propagator, stk_objects.IAgVePropagatorTwoBody)
        
        # 设置步长
        step = kwargs.get("step", 60.0)
        two_body.Step = step
        
        # 获取初始状态
        init_state = two_body.InitialState
        rep = init_state.Representation
        
        # 转换为经典轨道根数
        classic = rep.ConvertTo(1)
        classic_orbit = self._safe_qi(classic, stk_objects.IAgOrbitStateClassical)
        
        # 设置坐标系
        classic_orbit.CoordinateSystemType = 0
        
        # 设置轨道参数
        semi_major_axis = kwargs.get("semi_major_axis", 7000)
        eccentricity = kwargs.get("eccentricity", 0.0)
        
        classic_orbit.SizeShapeType = 4
        ss = self._safe_qi(classic_orbit.SizeShape, stk_objects.IAgClassicalSizeShapeSemimajorAxis)
        ss.SemiMajorAxis = semi_major_axis
        ss.Eccentricity = eccentricity
        
        orientation = classic_orbit.Orientation
        orientation.Inclination = kwargs.get("inclination", 0.0)
        orientation.ArgOfPerigee = kwargs.get("arg_of_perigee", 0.0)
        
        orientation.AscNodeType = 1
        ascnode = self._safe_qi(orientation.AscNode, stk_objects.IAgOrientationAscNodeRAAN)
        ascnode.Value = kwargs.get("raan", 0.0)
        
        classic_orbit.LocationType = 5
        location = self._safe_qi(classic_orbit.Location, stk_objects.IAgClassicalLocationTrueAnomaly)
        location.Value = kwargs.get("true_anomaly", 0.0)
        
        init_state.Representation.Assign(classic)
        two_body.Propagate()
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取卫星详细信息
        
        Returns:
            dict: 卫星信息
        """
        if not self._interface:
            return {"name": self._name, "status": "not_loaded"}
        
        info = {
            "name": self._name,
            "propagator": self._get_propagator_info(),
            "orbit": self._get_orbit_info(),
            "constraints": self._get_constraints_info()
        }
        return info
    
    def _get_propagator_info(self) -> Dict[str, Any]:
        """获取传播器信息"""
        prop_type = self._interface.PropagatorType
        return {
            "type": PropagatorType.NAMES.get(prop_type, f"Unknown ({prop_type})"),
            "type_id": prop_type
        }
    
    def _get_orbit_info(self) -> Dict[str, Any]:
        """获取轨道参数"""
        stk_objects = self._connection.stk_objects
        prop_type = self._interface.PropagatorType
        
        orbit_info = {}
        
        try:
            if prop_type == PropagatorType.J2_PERTURBATION:
                j2 = self._safe_qi(self._interface.Propagator, stk_objects.IAgVePropagatorJ2Perturbation)
                orbit_info["step"] = j2.Step
                
                init_state = j2.InitialState
                rep = init_state.Representation
                classic = rep.ConvertTo(1)
                classic_orbit = self._safe_qi(classic, stk_objects.IAgOrbitStateClassical)
                
                # 获取轨道参数
                size_shape = classic_orbit.SizeShape
                ss = self._safe_qi(size_shape, stk_objects.IAgClassicalSizeShapeSemimajorAxis)
                orbit_info["semi_major_axis"] = ss.SemiMajorAxis
                orbit_info["eccentricity"] = ss.Eccentricity
                
                orient = classic_orbit.Orientation
                orbit_info["inclination"] = orient.Inclination
                orbit_info["arg_of_perigee"] = orient.ArgOfPerigee
                
                try:
                    raan_if = self._safe_qi(orient.AscNode, stk_objects.IAgOrientationAscNodeRAAN)
                    orbit_info["raan"] = raan_if.Value
                except:
                    orbit_info["raan"] = None
                
                try:
                    loc = classic_orbit.Location
                    ta = self._safe_qi(loc, stk_objects.IAgClassicalLocationTrueAnomaly)
                    orbit_info["true_anomaly"] = ta.Value
                except:
                    orbit_info["true_anomaly"] = None
                    
        except Exception as e:
            orbit_info["error"] = str(e)
        
        return orbit_info
    
    def _get_constraints_info(self) -> list:
        """获取访问约束信息"""
        stk_objects = self._connection.stk_objects
        constraints = []
        
        try:
            ac = self._interface.AccessConstraints
            for i in range(ac.Count):
                c = ac.Item(i)
                try:
                    minmax = c.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
                    if minmax.EnableMin or minmax.EnableMax:
                        constraint = {"name": c.ConstraintName}
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
    def from_dict(cls, connection: STKConnection, config: Dict[str, Any]) -> "SatelliteComponent":
        """
        从字典配置创建卫星
        
        Args:
            connection: STK 连接
            config: 配置字典，格式如下:
                {
                    "name": "MySat",
                    "propagator": "J2Perturbation",  # 可选
                    "orbit": {
                        "semi_major_axis": 7000,
                        "eccentricity": 0.001,
                        "inclination": 98.0,
                        "raan": 0,
                        "arg_of_perigee": 0,
                        "true_anomaly": 0
                    },
                    "step": 60  # 可选
                }
        """
        name = config.get("name")
        if not name:
            raise STKComponentError("卫星配置必须包含 'name' 字段")
        
        # 解析传播器类型
        prop_str = config.get("propagator", "J2Perturbation")
        prop_map = {
            "HPOP": PropagatorType.HPOP,
            "J2Perturbation": PropagatorType.J2_PERTURBATION,
            "J4Perturbation": PropagatorType.J4_PERTURBATION,
            "SGP4": PropagatorType.SGP4,
            "SPK": PropagatorType.SPK,
            "TwoBody": PropagatorType.TWO_BODY,
        }
        propagator = prop_map.get(prop_str, PropagatorType.J2_PERTURBATION)
        
        # 解析轨道参数
        orbit = config.get("orbit", {})
        
        satellite = cls(connection, name)
        satellite.create(
            propagator=propagator,
            semi_major_axis=orbit.get("semi_major_axis", 7000),
            eccentricity=orbit.get("eccentricity", 0.0),
            inclination=orbit.get("inclination", 0.0),
            raan=orbit.get("raan", 0.0),
            arg_of_perigee=orbit.get("arg_of_perigee", 0.0),
            true_anomaly=orbit.get("true_anomaly", 0.0),
            step=config.get("step", 60.0)
        )
        
        return satellite

