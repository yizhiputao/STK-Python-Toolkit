"""
通用组件批量创建脚本

支持从 JSON 配置文件批量创建任意类型的 STK 组件（卫星、地面站等）。

目录结构：
  configs/
    satellites/*.json    → 自动识别为卫星配置
    facilities/*.json    → 自动识别为地面站配置
    
使用方式：
1. 命令行参数（推荐）：
   python create_components_json.py --satellites satellite3 satellite4 --facilities Beijing
   python create_components_json.py --satellites ALL
   python create_components_json.py --all
   
2. 使用配置文件：
   python create_components_json.py --config configs/create_config.json
   python create_components_json.py  # 使用默认配置文件
   
优先级：命令行参数 > --config指定的配置文件 > 默认配置文件
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components.factory import ComponentFactory
from stk_toolkit.components.satellite import SatelliteComponent
from stk_toolkit.components.facility import FacilityComponent
from stk_toolkit.cli import parse_create_args, resolve_components

# ============ 默认配置 ============

# 默认配置文件路径
DEFAULT_CONFIG_FILE = Path(SCRIPT_DIR) / "configs" / "create_config.json"

# 配置文件根目录
CONFIG_ROOT = Path(SCRIPT_DIR) / "configs"

# ================================

# 组件类型映射
COMPONENT_TYPE_MAP = {
    "satellites": {
        "class": SatelliteComponent,
        "type_name": "Satellite",
        "config_dir": "satellites"
    },
    "facilities": {
        "class": FacilityComponent,
        "type_name": "Facility",
        "config_dir": "facilities"
    }
}


def _resolve_config_path(component_type: str, name: str) -> Optional[Path]:
    """
    根据组件类型和名称推导 JSON 配置文件路径
    
    Args:
        component_type: 组件类型 (satellites/facilities)
        name: 组件名称
        
    Returns:
        配置文件路径，未找到返回 None
    """
    config_dir = CONFIG_ROOT / COMPONENT_TYPE_MAP[component_type]["config_dir"]
    
    # 尝试多种命名模式
    candidates = [
        config_dir / f"{name}_config.json",
        config_dir / f"{name.lower()}_config.json",
        config_dir / f"{name}.json",
        config_dir / f"{name.lower()}.json",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return None


def _list_all_configs_in_dir(component_type: str) -> List[Path]:
    """列出指定类型目录下的所有 JSON 配置文件"""
    config_dir = CONFIG_ROOT / COMPONENT_TYPE_MAP[component_type]["config_dir"]
    if not config_dir.exists():
        return []
    
    return sorted(config_dir.glob("*.json"))


def _load_config(config_path: Path) -> Dict[str, Any]:
    """读取 JSON 配置为字典"""
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _prepare_components(
    connection: STKConnection,
    component_type: str,
    config: Dict[str, Any],
    delete_existing: bool = True
) -> List[Dict[str, Any]]:
    """
    根据 delete_existing 选项处理配置
    """
    components = config.get("components", []) or []
    ready: List[Dict[str, Any]] = []
    
    component_class = COMPONENT_TYPE_MAP[component_type]["class"]
    type_name = COMPONENT_TYPE_MAP[component_type]["type_name"]
    
    for component in components:
        comp_type = component.get("type", "")
        if comp_type.lower() != type_name.lower():
            ready.append(component)
            continue
        
        name = component.get("name")
        if not name:
            continue
        
        exists = component_class.exists(connection, name)
        if not exists:
            ready.append(component)
            continue
        
        if delete_existing:
            if component_class.delete_by_name(connection, name):
                print(f"✓ 已删除存在的{type_name}：{name}")
            ready.append(component)
        else:
            print(f"⊙ {type_name} {name} 已存在，跳过创建")
    
    return ready


def _create_components(factory: ComponentFactory, config: Dict[str, Any]) -> None:
    """通过组件工厂创建配置中的所有组件"""
    components = config.get("components")
    if not components:
        print("  配置中未找到 components，跳过")
        return
    factory.create_many(components)




def main():
    # 解析命令行参数
    args = parse_create_args(DEFAULT_CONFIG_FILE)
    
    # 确定要创建的组件和配置
    components_to_create, options = resolve_components(args, DEFAULT_CONFIG_FILE, operation="create")
    delete_existing = options.get("delete_existing", True)
    
    # 确定要创建的组件
    targets: List[tuple[str, str, Path]] = []  # (component_type, name, config_path)
    
    # 如果为空或 None，处理所有类型的所有配置
    if not components_to_create:
        for comp_type in COMPONENT_TYPE_MAP.keys():
            for path in _list_all_configs_in_dir(comp_type):
                targets.append((comp_type, path.stem, path))
    else:
        # 处理指定的组件类型和名称
        for comp_type, names in components_to_create.items():
            if comp_type not in COMPONENT_TYPE_MAP:
                print(f"⚠ 未知的组件类型: {comp_type}，跳过")
                continue
            
            if len(names) == 1 and names[0].upper() == "ALL":
                # 处理该类型的所有配置
                for path in _list_all_configs_in_dir(comp_type):
                    targets.append((comp_type, path.stem, path))
            else:
                # 处理指定名称的配置
                for name in names:
                    path = _resolve_config_path(comp_type, name)
                    if path:
                        targets.append((comp_type, name, path))
                    else:
                        available = [p.name for p in _list_all_configs_in_dir(comp_type)]
                        print(f"⚠ 未找到 {comp_type}/{name} 的配置文件")
                        print(f"  可用配置: {', '.join(available) if available else '无'}")
    
    if not targets:
        print("没有找到需要创建的组件配置")
        return
    
    print(f"找到 {len(targets)} 个配置文件，开始创建...\n")
    
    with STKConnection() as connection:
        factory = ComponentFactory(connection)
        
        for comp_type, name, config_path in targets:
            type_name = COMPONENT_TYPE_MAP[comp_type]["type_name"]
            print(f"[{type_name}] 开始创建 {name}")
            print(f"  配置文件: {config_path.relative_to(SCRIPT_DIR)}")
            
            try:
                config = _load_config(config_path)
                components_to_create_list = _prepare_components(connection, comp_type, config, delete_existing)
                
                if not components_to_create_list:
                    print(f"  {name} 无需创建（所有组件均被跳过）\n")
                    continue
                
                _create_components(factory, {"components": components_to_create_list})
                print(f"  ✓ {name} 创建完成\n")
                
            except Exception as e:
                print(f"  ✗ 创建失败: {e}\n")


if __name__ == "__main__":
    main()

