"""
卫星修改器模块
提供修改卫星参数的功能
"""

from typing import Any, Dict, Optional
from .base import ModifierBase
from ..core.connection import STKConnection
from ..core.exceptions import STKModifyError
from ..components.satellite import PropagatorType


class SatelliteModifier(ModifierBase):
    """
    卫星修改器
    
    支持修改:
    - 轨道参数
    - 传播器设置
    - 访问约束
    
    使用示例:
        modifier = SatelliteModifier(connection)
        modifier.load("Satellite1")
        
        # 方式1: 批量修改
        modifier.apply({
            "orbit": {
                "semi_major_axis": 7200,
                "inclination": 98.5
            }
        })
        
        # 方式2: 单个修改
        modifier.set("orbit.semi_major_axis", 7200)
        
        # 方式3: 直接调用方法
        modifier.set_orbit(semi_major_axis=7200, inclination=98.5)
    """
    
    def load(self, name: str) -> "SatelliteModifier":
        """
        加载卫星对象
        
        Args:
            name: 卫星名称
        """
        stk_objects = self._connection.stk_objects
        
        try:
            path = f"*/Satellite/{name}"
            self._target = self._connection.root.GetObjectFromPath(path)
            self._interface = self._target.QueryInterface(stk_objects.IAgSatellite)
        except Exception as e:
            raise STKModifyError(f"加载卫星 '{name}' 失败: {e}")
        
        return self
    
    def apply(self, changes: Dict[str, Any]) -> "SatelliteModifier":
        """
        应用修改
        
        Args:
            changes: 修改内容，支持的键:
                - orbit: 轨道参数 (semi_major_axis, eccentricity, inclination, raan, arg_of_perigee, true_anomaly)
                - propagator: 传播器设置 (type, step)
                - constraints: 约束设置
        """
        self._ensure_loaded()
        
        if "orbit" in changes:
            self._apply_orbit_changes(changes["orbit"])
        
        if "propagator" in changes:
            self._apply_propagator_changes(changes["propagator"])
        
        if "constraints" in changes:
            self._apply_constraint_changes(changes["constraints"])
        
        return self
    
    def set_orbit(self, **kwargs) -> "SatelliteModifier":
        """
        设置轨道参数
        
        Args:
            semi_major_axis: 半长轴 (km)
            eccentricity: 偏心率
            inclination: 轨道倾角 (deg)
            raan: 升交点赤经 (deg)
            arg_of_perigee: 近地点幅角 (deg)
            true_anomaly: 真近点角 (deg)
        """
        return self.apply({"orbit": kwargs})
    
    def set_propagator_step(self, step: float) -> "SatelliteModifier":
        """
        设置传播器步长
        
        Args:
            step: 步长 (秒)
        """
        return self.apply({"propagator": {"step": step}})
    
    def _apply_orbit_changes(self, orbit_params: Dict[str, Any]):
        """应用轨道参数修改"""
        stk_objects = self._connection.stk_objects
        prop_type = self._interface.PropagatorType
        
        if prop_type == PropagatorType.J2_PERTURBATION:
            self._modify_j2_orbit(orbit_params)
        elif prop_type == PropagatorType.TWO_BODY:
            self._modify_two_body_orbit(orbit_params)
        else:
            raise STKModifyError(f"不支持的传播器类型: {prop_type}")
    
    def _modify_j2_orbit(self, params: Dict[str, Any]):
        """修改 J2 传播器轨道"""
        stk_objects = self._connection.stk_objects
        
        try:
            j2 = self._interface.Propagator.QueryInterface(stk_objects.IAgVePropagatorJ2Perturbation)
            
            init_state = j2.InitialState
            rep = init_state.Representation
            classic = rep.ConvertTo(1)
            classic_orbit = classic.QueryInterface(stk_objects.IAgOrbitStateClassical)
            
            # 修改半长轴和偏心率
            if "semi_major_axis" in params or "eccentricity" in params:
                ss = classic_orbit.SizeShape.QueryInterface(stk_objects.IAgClassicalSizeShapeSemimajorAxis)
                if "semi_major_axis" in params:
                    ss.SemiMajorAxis = params["semi_major_axis"]
                if "eccentricity" in params:
                    ss.Eccentricity = params["eccentricity"]
            
            # 修改轨道方向
            orientation = classic_orbit.Orientation
            if "inclination" in params:
                orientation.Inclination = params["inclination"]
            if "arg_of_perigee" in params:
                orientation.ArgOfPerigee = params["arg_of_perigee"]
            if "raan" in params:
                ascnode = orientation.AscNode.QueryInterface(stk_objects.IAgOrientationAscNodeRAAN)
                ascnode.Value = params["raan"]
            
            # 修改真近点角
            if "true_anomaly" in params:
                location = classic_orbit.Location.QueryInterface(stk_objects.IAgClassicalLocationTrueAnomaly)
                location.Value = params["true_anomaly"]
            
            # 应用更改
            init_state.Representation.Assign(classic)
            j2.Propagate()
            
        except Exception as e:
            raise STKModifyError(f"修改 J2 轨道参数失败: {e}")
    
    def _modify_two_body_orbit(self, params: Dict[str, Any]):
        """修改 TwoBody 传播器轨道"""
        stk_objects = self._connection.stk_objects
        
        try:
            two_body = self._interface.Propagator.QueryInterface(stk_objects.IAgVePropagatorTwoBody)
            
            init_state = two_body.InitialState
            rep = init_state.Representation
            classic = rep.ConvertTo(1)
            classic_orbit = classic.QueryInterface(stk_objects.IAgOrbitStateClassical)
            
            if "semi_major_axis" in params or "eccentricity" in params:
                ss = classic_orbit.SizeShape.QueryInterface(stk_objects.IAgClassicalSizeShapeSemimajorAxis)
                if "semi_major_axis" in params:
                    ss.SemiMajorAxis = params["semi_major_axis"]
                if "eccentricity" in params:
                    ss.Eccentricity = params["eccentricity"]
            
            orientation = classic_orbit.Orientation
            if "inclination" in params:
                orientation.Inclination = params["inclination"]
            if "arg_of_perigee" in params:
                orientation.ArgOfPerigee = params["arg_of_perigee"]
            if "raan" in params:
                ascnode = orientation.AscNode.QueryInterface(stk_objects.IAgOrientationAscNodeRAAN)
                ascnode.Value = params["raan"]
            
            if "true_anomaly" in params:
                location = classic_orbit.Location.QueryInterface(stk_objects.IAgClassicalLocationTrueAnomaly)
                location.Value = params["true_anomaly"]
            
            init_state.Representation.Assign(classic)
            two_body.Propagate()
            
        except Exception as e:
            raise STKModifyError(f"修改 TwoBody 轨道参数失败: {e}")
    
    def _apply_propagator_changes(self, prop_params: Dict[str, Any]):
        """应用传播器设置修改"""
        stk_objects = self._connection.stk_objects
        
        if "step" in prop_params:
            prop_type = self._interface.PropagatorType
            
            try:
                if prop_type == PropagatorType.J2_PERTURBATION:
                    j2 = self._interface.Propagator.QueryInterface(stk_objects.IAgVePropagatorJ2Perturbation)
                    j2.Step = prop_params["step"]
                    j2.Propagate()
                elif prop_type == PropagatorType.TWO_BODY:
                    two_body = self._interface.Propagator.QueryInterface(stk_objects.IAgVePropagatorTwoBody)
                    two_body.Step = prop_params["step"]
                    two_body.Propagate()
            except Exception as e:
                raise STKModifyError(f"修改传播器步长失败: {e}")
    
    def _apply_constraint_changes(self, constraints: list):
        """应用约束修改"""
        stk_objects = self._connection.stk_objects
        
        try:
            ac = self._interface.AccessConstraints
            
            for constraint in constraints:
                name = constraint.get("name")
                if not name:
                    continue
                
                c = ac.GetActiveConstraint(name)
                minmax = c.QueryInterface(stk_objects.IAgAccessCnstrMinMax)
                
                if "min" in constraint:
                    minmax.EnableMin = True
                    minmax.Min = constraint["min"]
                elif "disable_min" in constraint and constraint["disable_min"]:
                    minmax.EnableMin = False
                
                if "max" in constraint:
                    minmax.EnableMax = True
                    minmax.Max = constraint["max"]
                elif "disable_max" in constraint and constraint["disable_max"]:
                    minmax.EnableMax = False
                    
        except Exception as e:
            raise STKModifyError(f"修改约束失败: {e}")

