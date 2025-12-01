"""
通用组件批量删除脚本

支持批量删除任意类型的 STK 组件（卫星、地面站等）。

使用方式：
1. 命令行参数（推荐）：
   python delete_components.py --satellites Satellite3 Satellite4 --facilities Beijing
   
2. 使用配置文件：
   python delete_components.py --config configs/delete_config.json
   python delete_components.py  # 使用默认配置文件
   
优先级：命令行参数 > --config指定的配置文件 > 默认配置文件
"""

import os
import sys
from pathlib import Path
from typing import Dict, Iterable, List

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components.satellite import SatelliteComponent
from stk_toolkit.components.facility import FacilityComponent
from stk_toolkit.cli import parse_delete_args, resolve_components

# ============ 默认配置 ============

# 默认配置文件路径
DEFAULT_CONFIG_FILE = Path(SCRIPT_DIR) / "configs" / "delete_config.json"

# ==================================

# 组件类型映射
COMPONENT_CLASS_MAP = {
    "Satellite": SatelliteComponent,
    "Facility": FacilityComponent,
}


def _delete_components(
    connection: STKConnection,
    component_type: str,
    names: Iterable[str]
) -> None:
    """
    逐个删除给定名称列表中的组件
    
    Args:
        connection: STK 连接对象
        component_type: 组件类型 (Satellite/Facility)
        names: 组件名称列表
    """
    if component_type not in COMPONENT_CLASS_MAP:
        print(f"⚠ 未知的组件类型: {component_type}")
        return
    
    component_class = COMPONENT_CLASS_MAP[component_type]
    
    for name in names:
        if not name:
            continue
        
        if component_class.delete_by_name(connection, name):
            print(f"✓ 已删除 {component_type}: {name}")
        else:
            print(f"⊙ {component_type} 不存在: {name}")


def main():
    # 解析命令行参数
    args = parse_delete_args(DEFAULT_CONFIG_FILE)
    
    # 确定要删除的组件
    components_to_delete, _ = resolve_components(args, DEFAULT_CONFIG_FILE, operation="delete")
    
    if not components_to_delete:
        print("没有指定要删除的组件")
        return
    
    # 统计要删除的组件数量
    total = sum(len(names) for names in components_to_delete.values())
    print(f"准备删除 {total} 个组件\n")
    
    with STKConnection() as connection:
        print("✓ 已连接到 STK\n")
        
        for component_type, names in components_to_delete.items():
            if not names:
                continue
            
            print(f"[{component_type}] 开始删除...")
            _delete_components(connection, component_type, names)
            print()
    
    print("删除操作完成")


if __name__ == "__main__":
    main()
