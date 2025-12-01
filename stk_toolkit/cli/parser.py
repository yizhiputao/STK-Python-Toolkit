"""
命令行参数解析器

提供创建和删除脚本的通用参数解析功能。
"""

import argparse
from pathlib import Path
from typing import Any


def parse_create_args(default_config: Path) -> Any:
    """
    解析创建脚本的命令行参数
    
    Args:
        default_config: 默认配置文件路径
        
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description='批量创建 STK 组件（卫星、地面站等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建指定的卫星和地面站
  %(prog)s --satellites satellite3 satellite4 --facilities Beijing
  
  # 创建所有卫星
  %(prog)s --satellites ALL
  
  # 创建所有组件
  %(prog)s --all
  
  # 使用指定配置文件
  %(prog)s --config my_config.json
  
  # 使用默认配置文件（无参数）
  %(prog)s
        """
    )
    
    parser.add_argument(
        '--satellites', '-s',
        nargs='+',
        metavar='NAME',
        help='要创建的卫星名称列表，或使用 ALL 创建所有卫星'
    )
    
    parser.add_argument(
        '--facilities', '-f',
        nargs='+',
        metavar='NAME',
        help='要创建的地面站名称列表，或使用 ALL 创建所有地面站'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='创建所有类型的所有组件'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        metavar='FILE',
        help=f'配置文件路径（默认: {default_config}）'
    )
    
    parser.add_argument(
        '--no-delete',
        action='store_true',
        help='不删除已存在的同名组件（默认会先删除再创建）'
    )
    
    return parser.parse_args()


def parse_delete_args(default_config: Path) -> Any:
    """
    解析删除脚本的命令行参数
    
    Args:
        default_config: 默认配置文件路径
        
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description='批量删除 STK 组件（卫星、地面站等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 删除指定的卫星和地面站
  %(prog)s --satellites Satellite3 Satellite4 --facilities Beijing
  
  # 只删除卫星
  %(prog)s --satellites Satellite3 Satellite4
  
  # 使用指定配置文件
  %(prog)s --config my_delete_config.json
  
  # 使用默认配置文件（无参数）
  %(prog)s
        """
    )
    
    parser.add_argument(
        '--satellites', '-s',
        nargs='+',
        metavar='NAME',
        help='要删除的卫星名称列表'
    )
    
    parser.add_argument(
        '--facilities', '-f',
        nargs='+',
        metavar='NAME',
        help='要删除的地面站名称列表'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        metavar='FILE',
        help=f'配置文件路径（默认: {default_config}）'
    )
    
    return parser.parse_args()

