"""
场景状态报告
读取并报告当前 STK 场景的详细信息
"""

from typing import Any, Dict, List
from datetime import datetime
from .base import ReportBase, ReportFormat
from ..core.connection import STKConnection
from ..components.satellite import PropagatorType


class ScenarioReport(ReportBase):
    """
    场景状态报告
    
    报告内容包括:
    - 场景基本信息
    - 卫星信息 (轨道参数、约束)
    - 地面站信息 (位置、约束)
    - 其他对象信息
    
    使用示例:
        with STKConnection() as connection:
            report = ScenarioReport(connection)
            report.collect_data()
            
            # 生成文本报告
            text = report.generate(ReportFormat.TEXT)
            
            # 保存到文件
            report.save("./reports")
            
            # 生成 JSON 格式
            json_str = report.generate(ReportFormat.JSON)
    """
    
    def __init__(self, connection: STKConnection, title: str = "STK 场景详细信息报告"):
        """
        初始化场景报告
        
        Args:
            connection: STK 连接对象
            title: 报告标题
        """
        super().__init__(title)
        self._connection = connection
    
    def _get_report_type(self) -> str:
        return "scenario_report"
    
    def collect_data(self) -> "ScenarioReport":
        """
        收集场景数据
        """
        # 收集场景基本信息
        self._data["scenario"] = self._collect_scenario_info()
        
        # 收集所有对象信息
        self._data["objects"] = self._collect_objects_info()
        
        return self
    
    def _collect_scenario_info(self) -> Dict[str, Any]:
        """收集场景基本信息"""
        info = self._connection.get_scenario_info()
        return info
    
    def _collect_objects_info(self) -> List[Dict[str, Any]]:
        """收集所有对象信息"""
        objects = []
        stk_objects = self._connection.stk_objects
        
        children = self._connection.get_children()
        
        for child in children:
            class_name = child.ClassName
            inst_name = child.InstanceName
            
            obj_info = {
                "type": class_name,
                "name": inst_name,
                "path": child.Path
            }
            
            if class_name == "Satellite":
                obj_info["details"] = self._collect_satellite_info(child)
            elif class_name == "Facility":
                obj_info["details"] = self._collect_facility_info(child)
            
            objects.append(obj_info)
        
        return objects
    
    def _collect_satellite_info(self, sat_obj: Any) -> Dict[str, Any]:
        """收集卫星详细信息"""
        stk_objects = self._connection.stk_objects
        info = {}
        
        try:
            sat = sat_obj.QueryInterface(stk_objects.IAgSatellite)
            
            # 传播器信息
            prop_type = sat.PropagatorType
            info["propagator"] = {
                "type": PropagatorType.NAMES.get(prop_type, f"Unknown ({prop_type})"),
                "type_id": prop_type
            }
            
            # 轨道参数
            if prop_type == PropagatorType.J2_PERTURBATION:
                info["orbit"] = self._collect_j2_orbit_info(sat)
            
            # 约束
            info["constraints"] = self._collect_constraints_info(sat.AccessConstraints)
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def _collect_j2_orbit_info(self, sat: Any) -> Dict[str, Any]:
        """收集 J2 传播器轨道信息"""
        stk_objects = self._connection.stk_objects
        orbit = {}
        
        try:
            j2 = sat.Propagator.QueryInterface(stk_objects.IAgVePropagatorJ2Perturbation)
            orbit["step"] = j2.Step
            
            init_state = j2.InitialState
            rep = init_state.Representation
            classic = rep.ConvertTo(1)
            classic_orbit = classic.QueryInterface(stk_objects.IAgOrbitStateClassical)
            
            # 轨道根数
            size_shape = classic_orbit.SizeShape
            ss = size_shape.QueryInterface(stk_objects.IAgClassicalSizeShapeSemimajorAxis)
            orbit["semi_major_axis"] = ss.SemiMajorAxis
            orbit["eccentricity"] = ss.Eccentricity
            
            orient = classic_orbit.Orientation
            orbit["inclination"] = orient.Inclination
            orbit["arg_of_perigee"] = orient.ArgOfPerigee
            
            try:
                raan_if = orient.AscNode.QueryInterface(stk_objects.IAgOrientationAscNodeRAAN)
                orbit["raan"] = raan_if.Value
            except:
                orbit["raan"] = None
            
            try:
                loc = classic_orbit.Location
                ta = loc.QueryInterface(stk_objects.IAgClassicalLocationTrueAnomaly)
                orbit["true_anomaly"] = ta.Value
            except:
                orbit["true_anomaly"] = None
                
        except Exception as e:
            orbit["error"] = str(e)
        
        return orbit
    
    def _collect_facility_info(self, fac_obj: Any) -> Dict[str, Any]:
        """收集地面站详细信息"""
        stk_objects = self._connection.stk_objects
        info = {}
        
        try:
            fac = fac_obj.QueryInterface(stk_objects.IAgFacility)
            
            # 位置信息
            try:
                position = fac.Position
                coords = position.QueryPlanetodetic()
                info["position"] = {
                    "latitude": coords[0],
                    "longitude": coords[1],
                    "altitude": coords[2]
                }
            except Exception as e:
                info["position"] = {"error": str(e)}
            
            # 约束
            info["constraints"] = self._collect_facility_constraints(fac.AccessConstraints)
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def _collect_constraints_info(self, ac: Any) -> List[Dict[str, Any]]:
        """收集卫星访问约束信息"""
        stk_objects = self._connection.stk_objects
        constraints = []
        
        try:
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
    
    def _collect_facility_constraints(self, ac: Any) -> List[Dict[str, Any]]:
        """收集地面站访问约束信息"""
        stk_objects = self._connection.stk_objects
        constraints = []
        
        try:
            for i in range(ac.Count):
                c = ac.Item(i)
                name = c.ConstraintName
                ctype = c.ConstraintType
                
                # LineOfSight 约束
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
    
    def _generate_text(self) -> str:
        """生成文本格式报告"""
        lines = []
        
        # 报告头
        lines.append("=" * 70)
        lines.append(f"                    {self._title}")
        lines.append("=" * 70)
        lines.append(f"  生成时间: {self._generated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        
        # 场景信息
        scenario = self._data.get("scenario", {})
        lines.append(self._format_section("场景基本信息"))
        lines.append(f"  场景名称: {scenario.get('name', 'N/A')}")
        lines.append(f"  场景路径: {scenario.get('path', 'N/A')}")
        lines.append(f"  开始时间: {scenario.get('start_time', 'N/A')}")
        lines.append(f"  结束时间: {scenario.get('stop_time', 'N/A')}")
        lines.append(f"  历元时间: {scenario.get('epoch', 'N/A')}")
        
        # 对象信息
        objects = self._data.get("objects", [])
        lines.append(self._format_section("场景对象详细信息"))
        lines.append(f"  对象总数: {len(objects)}")
        
        for obj in objects:
            obj_type = obj.get("type")
            obj_name = obj.get("name")
            details = obj.get("details", {})
            
            lines.append(f"\n{'-' * 70}")
            
            if obj_type == "Satellite":
                lines.extend(self._format_satellite_text(obj_name, details))
            elif obj_type == "Facility":
                lines.extend(self._format_facility_text(obj_name, details))
            else:
                lines.append(f"  [{obj_type}] {obj_name}")
                lines.append(f"    路径: {obj.get('path', 'N/A')}")
        
        # 报告尾
        lines.append(f"\n{'=' * 70}")
        lines.append("                         报告结束")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_satellite_text(self, name: str, details: Dict) -> List[str]:
        """格式化卫星文本输出"""
        lines = []
        lines.append(f"  [Satellite] 卫星: {name}")
        lines.append("-" * 70)
        
        # 传播器
        prop = details.get("propagator", {})
        lines.append(f"\n  【轨道传播器】")
        lines.append(f"    类型: {prop.get('type', 'N/A')}")
        
        # 轨道参数
        orbit = details.get("orbit", {})
        lines.append(f"\n  【轨道参数 (经典轨道根数)】")
        if "step" in orbit:
            lines.append(f"    步长: {orbit['step']} sec")
        if "semi_major_axis" in orbit:
            lines.append(f"    半长轴 (a): {orbit['semi_major_axis']:.4f} km")
        if "eccentricity" in orbit:
            lines.append(f"    偏心率 (e): {orbit['eccentricity']:.10e}")
        if "inclination" in orbit:
            lines.append(f"    轨道倾角 (i): {orbit['inclination']:.4f} deg")
        if "arg_of_perigee" in orbit:
            lines.append(f"    近地点幅角 (AoP): {orbit['arg_of_perigee']:.4f} deg")
        if orbit.get("raan") is not None:
            lines.append(f"    升交点赤经 (RAAN): {orbit['raan']:.4f} deg")
        if orbit.get("true_anomaly") is not None:
            lines.append(f"    真近点角 (TA): {orbit['true_anomaly']:.10e} deg")
        
        # 约束
        constraints = details.get("constraints", [])
        lines.append(f"\n  【访问约束】")
        if constraints:
            for c in constraints:
                lines.append(f"    * {c.get('name')}")
                if "min" in c:
                    lines.append(f"        Min: {c['min']}")
                if "max" in c:
                    lines.append(f"        Max: {c['max']}")
        else:
            lines.append(f"    (无启用的约束)")
        
        return lines
    
    def _format_facility_text(self, name: str, details: Dict) -> List[str]:
        """格式化地面站文本输出"""
        lines = []
        lines.append(f"  [Facility] 地面站: {name}")
        lines.append("-" * 70)
        
        # 位置
        position = details.get("position", {})
        lines.append(f"\n  【位置信息】")
        if "error" not in position:
            lines.append(f"    纬度: {position.get('latitude', 0):.6f} deg")
            lines.append(f"    经度: {position.get('longitude', 0):.6f} deg")
            lines.append(f"    海拔: {position.get('altitude', 0):.3f} km")
        else:
            lines.append(f"    位置获取失败: {position['error']}")
        
        # 约束
        constraints = details.get("constraints", [])
        lines.append(f"\n  【访问约束条件】")
        if constraints:
            for c in constraints:
                lines.append(f"\n    * {c.get('name')}")
                if c.get("type") == "LineOfSight":
                    lines.append(f"        状态: 已启用")
                else:
                    if "min" in c:
                        lines.append(f"        最小值 (Min): {c['min']} deg")
                    if "max" in c:
                        lines.append(f"        最大值 (Max): {c['max']} deg")
        else:
            lines.append(f"    (无启用的约束)")
        
        return lines

