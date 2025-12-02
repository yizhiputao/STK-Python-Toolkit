"""
组件导出器
负责将STK场景中的所有组件导出为JSON文件并打包
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from zipfile import ZipFile

from ..core.connection import STKConnection
from ..components.satellite import SatelliteComponent
from ..components.facility import FacilityComponent
from ..components.base import ComponentBase


class ComponentExporter:
    """
    组件导出器类
    
    负责:
    - 从STK场景中获取所有组件
    - 将组件导出为JSON文件
    - 打包JSON文件到zip压缩包
    """
    
    # 组件类型映射（从STK ClassName到组件类）
    _component_class_map = {
        "Satellite": SatelliteComponent,
        "Facility": FacilityComponent,
    }
    
    def __init__(self, connection: STKConnection):
        """
        初始化组件导出器
        
        Args:
            connection: STK连接对象
        """
        self._connection = connection
    
    def export_all_components(self, output_dir: str) -> str:
        """
        导出场景中的所有组件为JSON文件
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            str: 实际创建的输出目录路径（带时间戳）
        """
        # 创建带时间戳的输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = os.path.join(output_dir, f"components_{timestamp}")
        os.makedirs(export_dir, exist_ok=True)
        
        # 获取所有组件
        components = self._load_all_components()
        
        if not components:
            print("提示: 场景中没有找到可导出的组件")
            # 创建空的汇总文件
            summary = {
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_components": 0,
                "components_by_type": {},
                "exported_files": []
            }
            summary_path = os.path.join(export_dir, "summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            return export_dir
        
        # 按类型分组
        components_by_type: Dict[str, List[ComponentBase]] = {}
        for comp in components:
            comp_type = comp.component_type.value
            if comp_type not in components_by_type:
                components_by_type[comp_type] = []
            components_by_type[comp_type].append(comp)
        
        # 导出每个组件为独立的JSON文件
        exported_files = []
        for comp_type, comp_list in components_by_type.items():
            type_dir = os.path.join(export_dir, comp_type.lower())
            os.makedirs(type_dir, exist_ok=True)
            
            for comp in comp_list:
                try:
                    comp_dict = comp.to_dict()
                    # 转换为与from_dict兼容的格式
                    normalized_dict = self._normalize_component_dict(comp_dict, comp.component_type.value)
                    
                    # 包装为配置文件格式（包含components数组）
                    config_format = {
                        "components": [normalized_dict]
                    }
                    
                    # 可选：添加description（根据组件类型）
                    if comp.component_type.value == "Facility":
                        config_format["description"] = f"{comp.name}地面站配置"
                    # 卫星可以不加description，保持简洁
                    
                    filename = f"{comp.name}_config.json"
                    filepath = os.path.join(type_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(config_format, f, indent=2, ensure_ascii=False)
                    
                    exported_files.append(filepath)
                except Exception as e:
                    print(f"警告: 导出组件 {comp.name} 失败: {e}")
        
        # 创建汇总文件
        summary = {
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_components": len(components),
            "components_by_type": {
                comp_type: len(comp_list) 
                for comp_type, comp_list in components_by_type.items()
            },
            "exported_files": [
                os.path.relpath(f, export_dir) for f in exported_files
            ]
        }
        
        summary_path = os.path.join(export_dir, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return export_dir
    
    def _load_all_components(self) -> List[ComponentBase]:
        """
        从STK场景中加载所有组件
        
        Returns:
            list: 组件列表
        """
        components = []
        try:
            children = self._connection.get_children()
        except Exception as e:
            print(f"警告: 获取场景子对象失败: {e}")
            return components
        
        for child in children:
            try:
                class_name = child.ClassName
                inst_name = child.InstanceName
            except Exception as e:
                print(f"警告: 获取对象信息失败: {e}")
                continue
            
            # 检查是否支持该类型
            component_class = self._component_class_map.get(class_name)
            if component_class is None:
                # 不支持的组件类型，跳过
                continue
            
            try:
                # 创建组件实例并加载
                comp = component_class(self._connection, inst_name)
                comp.load_from_existing()
                components.append(comp)
            except Exception as e:
                print(f"警告: 加载组件 {class_name}/{inst_name} 失败: {e}")
        
        return components
    
    def package_components(self, export_dir: str, output_dir: Optional[str] = None) -> str:
        """
        将导出的组件目录打包为zip文件
        
        Args:
            export_dir: 要打包的目录路径
            output_dir: zip文件输出目录，默认为export_dir的父目录
            
        Returns:
            str: zip文件路径
        """
        if output_dir is None:
            output_dir = os.path.dirname(export_dir)
        
        # 生成zip文件名（使用目录名）
        dir_name = os.path.basename(export_dir)
        zip_filename = f"{dir_name}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        # 创建zip文件
        with ZipFile(zip_path, "w") as zipf:
            # 遍历目录中的所有文件
            for root, dirs, files in os.walk(export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径（相对于export_dir）
                    arcname = os.path.relpath(file_path, export_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def _normalize_component_dict(self, comp_dict: Dict[str, Any], comp_type: str) -> Dict[str, Any]:
        """
        将组件字典转换为与from_dict兼容的格式
        
        Args:
            comp_dict: 组件字典（来自to_dict）
            comp_type: 组件类型（"Satellite"或"Facility"）
            
        Returns:
            dict: 标准化后的组件字典
        """
        normalized = {
            "type": comp_dict.get("type", comp_type),
            "name": comp_dict.get("name")
        }
        
        if comp_type == "Satellite":
            # 卫星格式转换
            info = comp_dict.get("propagator", {})
            if info:
                prop_type = info.get("type", "J2Perturbation")
                # 提取传播器类型名称（去掉括号中的内容）
                if "(" in prop_type:
                    prop_type = prop_type.split("(")[0].strip()
                normalized["propagator"] = prop_type
            
            orbit_info = comp_dict.get("orbit", {})
            if orbit_info:
                # 先提取step（即使orbit有错误，step也可能存在）
                if "step" in orbit_info:
                    step_val = orbit_info["step"]
                    # 保持step为浮点数格式（如60.0）
                    normalized["step"] = float(step_val) if step_val is not None else 60.0
                
                # 如果orbit没有错误，提取轨道参数
                if "error" not in orbit_info:
                    orbit = {}
                    if "semi_major_axis" in orbit_info:
                        orbit["semi_major_axis"] = orbit_info["semi_major_axis"]
                    if "eccentricity" in orbit_info:
                        orbit["eccentricity"] = orbit_info["eccentricity"]
                    if "inclination" in orbit_info:
                        orbit["inclination"] = orbit_info["inclination"]
                    if "raan" in orbit_info and orbit_info["raan"] is not None:
                        orbit["raan"] = orbit_info["raan"]
                    if "arg_of_perigee" in orbit_info:
                        orbit["arg_of_perigee"] = orbit_info["arg_of_perigee"]
                    if "true_anomaly" in orbit_info and orbit_info["true_anomaly"] is not None:
                        orbit["true_anomaly"] = orbit_info["true_anomaly"]
                    
                    if orbit:
                        normalized["orbit"] = orbit
        
        elif comp_type == "Facility":
            # 地面站格式转换
            position_info = comp_dict.get("position", {})
            if position_info and "error" not in position_info:
                lat = position_info.get("latitude", 0.0)
                lon = position_info.get("longitude", 0.0)
                alt = position_info.get("altitude", 0.0)
                
                # 格式化数值：如果altitude是整数，保持为整数
                normalized["position"] = {
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": int(alt) if alt == int(alt) else alt
                }
            
            constraints = comp_dict.get("constraints", [])
            if constraints:
                # 过滤掉LineOfSight约束（默认存在，不需要导出）
                normalized_constraints = []
                for c in constraints:
                    if c.get("type") != "LineOfSight":
                        constraint = {"name": c.get("name")}
                        if "min" in c:
                            constraint["min"] = c["min"]
                        if "max" in c:
                            constraint["max"] = c["max"]
                        if constraint:
                            normalized_constraints.append(constraint)
                
                if normalized_constraints:
                    normalized["constraints"] = normalized_constraints
        
        return normalized


def export_components_to_json(
    connection: STKConnection,
    output_dir: str,
    package: bool = True
) -> Dict[str, str]:
    """
    便捷函数：导出所有组件为JSON并打包
    
    Args:
        connection: STK连接对象
        output_dir: 输出目录
        package: 是否打包为zip文件
        
    Returns:
        dict: 包含导出目录和zip文件路径的字典
            - "export_dir": 导出目录路径
            - "zip_path": zip文件路径（如果package=True）
    """
    exporter = ComponentExporter(connection)
    export_dir = exporter.export_all_components(output_dir)
    
    result = {"export_dir": export_dir}
    
    if package:
        zip_path = exporter.package_components(export_dir)
        result["zip_path"] = zip_path
    
    return result

