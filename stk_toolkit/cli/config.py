"""
配置文件处理

提供配置文件加载和组件解析功能。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    从配置文件加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典，加载失败返回空字典
    """
    if not config_path.exists():
        return {}
    
    try:
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ 加载配置文件失败: {e}")
        return {}


def resolve_components(
    args: Any,
    default_config: Path,
    operation: str = "create"
) -> Tuple[Optional[Dict[str, List[str]]], Dict[str, Any]]:
    """
    根据命令行参数和配置文件解析要处理的组件
    
    Args:
        args: 命令行参数对象
        default_config: 默认配置文件路径
        operation: 操作类型 ("create" 或 "delete")
        
    Returns:
        (components_dict, options)
        - components_dict: {"satellites": [...], "facilities": [...]} 或 None（表示所有）
        - options: 其他配置选项，如 {"delete_existing": True}
    """
    components = None
    options = {}
    
    if operation == "create":
        # 创建操作的特殊处理
        if hasattr(args, 'all') and args.all:
            # --all 参数：创建所有
            components = None
        elif args.satellites or args.facilities:
            # 命令行参数优先
            components = {}
            if args.satellites:
                components["satellites"] = args.satellites
            if args.facilities:
                components["facilities"] = args.facilities
        else:
            # 使用配置文件
            components, options = _load_from_config(args, default_config, "create")
        
        # 处理 delete_existing 选项
        if hasattr(args, 'no_delete'):
            options["delete_existing"] = not args.no_delete
        
    elif operation == "delete":
        # 删除操作
        if args.satellites or args.facilities:
            # 命令行参数优先
            components = {}
            if args.satellites:
                components["Satellite"] = args.satellites
            if args.facilities:
                components["Facility"] = args.facilities
        else:
            # 使用配置文件
            components, options = _load_from_config(args, default_config, "delete")
    
    return components, options


def _load_from_config(
    args: Any,
    default_config: Path,
    operation: str
) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    """
    从配置文件加载组件配置
    
    Args:
        args: 命令行参数对象
        default_config: 默认配置文件路径
        operation: 操作类型
        
    Returns:
        (components_dict, options)
    """
    config_path = args.config if args.config else default_config
    
    if not config_path.exists():
        print(f"⚠ 配置文件不存在: {config_path}")
        print("提示: 使用 --help 查看使用方式")
        return {}, {}
    
    config = load_config(config_path)
    
    if not config:
        print("⚠ 配置文件为空或无效")
        return {}, {}
    
    print(f"📄 使用配置文件: {config_path}")
    
    components = {}
    options = {}
    
    if operation == "create":
        # 创建操作的配置格式
        if "satellites" in config:
            components["satellites"] = config["satellites"]
        if "facilities" in config:
            components["facilities"] = config["facilities"]
        if "delete_existing" in config:
            options["delete_existing"] = config["delete_existing"]
    
    elif operation == "delete":
        # 删除操作的配置格式
        if "Satellite" in config:
            components["Satellite"] = config["Satellite"]
        if "Facility" in config:
            components["Facility"] = config["Facility"]
    
    return components, options

