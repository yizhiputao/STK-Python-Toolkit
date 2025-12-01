"""
示例: 创建 STK 组件
演示如何使用代码和 JSON 方式创建卫星和地面站
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stk_toolkit import STKConnection
from stk_toolkit.components import (
    SatelliteComponent,
    FacilityComponent,
    ComponentFactory
)
from stk_toolkit.components.satellite import PropagatorType


def example_code_creation():
    """代码方式创建组件"""
    print("\n" + "=" * 60)
    print("示例 1: 代码方式创建组件")
    print("=" * 60)
    
    with STKConnection() as connection:
        # 创建卫星
        print("\n创建卫星 MySatellite...")
        satellite = SatelliteComponent(connection, "MySatellite")
        satellite.create(
            propagator=PropagatorType.J2_PERTURBATION,
            semi_major_axis=7000,  # km
            eccentricity=0.001,
            inclination=98.0,      # deg (太阳同步轨道)
            raan=45.0,
            arg_of_perigee=0,
            true_anomaly=0,
            step=60.0              # 传播步长 60 秒
        )
        print(f"✓ 卫星已创建: {satellite.path}")
        
        # 获取卫星信息
        info = satellite.get_info()
        print(f"  轨道倾角: {info['orbit'].get('inclination', 'N/A')} deg")
        
        # 创建地面站
        print("\n创建地面站 Beijing...")
        facility = FacilityComponent(connection, "Beijing")
        facility.create(
            latitude=40.0,
            longitude=116.0,
            altitude=0.05,  # km
            constraints=[
                {"name": "ElevationAngle", "min": 10.0},
                {"name": "SunElevationAngle", "min": -90.0, "max": 0.0}
            ]
        )
        print(f"✓ 地面站已创建: {facility.path}")
        
        # 获取地面站信息
        fac_info = facility.get_info()
        print(f"  位置: ({fac_info['position']['latitude']:.2f}, "
              f"{fac_info['position']['longitude']:.2f})")


def example_json_creation():
    """JSON 方式创建组件"""
    print("\n" + "=" * 60)
    print("示例 2: JSON 方式创建组件")
    print("=" * 60)
    
    # JSON 配置
    config = {
        "components": [
            {
                "type": "Satellite",
                "name": "JsonSatellite",
                "propagator": "J2Perturbation",
                "orbit": {
                    "semi_major_axis": 7200,
                    "eccentricity": 0.0001,
                    "inclination": 45.0,
                    "raan": 90.0,
                    "arg_of_perigee": 0,
                    "true_anomaly": 0
                },
                "step": 120
            },
            {
                "type": "Facility",
                "name": "Shanghai",
                "position": {
                    "latitude": 31.2,
                    "longitude": 121.5,
                    "altitude": 0.01
                },
                "constraints": [
                    {"name": "ElevationAngle", "min": 5.0}
                ]
            }
        ]
    }
    
    with STKConnection() as connection:
        factory = ComponentFactory(connection)
        
        # 从配置创建组件
        import json
        components = factory.create_from_json_string(json.dumps(config))
        
        print(f"\n✓ 已创建 {len(components)} 个组件:")
        for comp in components:
            print(f"  - {comp.component_type.value}: {comp.name}")


def example_from_json_file():
    """从 JSON 文件创建组件"""
    print("\n" + "=" * 60)
    print("示例 3: 从 JSON 文件创建组件")
    print("=" * 60)
    
    # 创建示例 JSON 文件
    import json
    config = {
        "components": [
            {
                "type": "Satellite",
                "name": "FileSatellite",
                "propagator": "J2Perturbation",
                "orbit": {
                    "semi_major_axis": 6800,
                    "eccentricity": 0,
                    "inclination": 97.0,
                    "raan": 180.0,
                    "arg_of_perigee": 0,
                    "true_anomaly": 0
                }
            }
        ]
    }
    
    json_file = "example_config.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"\n已创建示例配置文件: {json_file}")
    
    with STKConnection() as connection:
        factory = ComponentFactory(connection)
        components = factory.create_from_json(json_file)
        
        print(f"✓ 从文件创建了 {len(components)} 个组件")
    
    # 清理示例文件
    os.remove(json_file)


def main():
    """运行所有示例"""
    print("=" * 60)
    print("       STK 组件创建示例")
    print("=" * 60)
    print("\n注意: 运行此示例会在 STK 中创建新对象")
    print("请确保 STK 已打开并加载了场景\n")
    
    # 选择要运行的示例
    print("请选择要运行的示例:")
    print("1. 代码方式创建组件")
    print("2. JSON 方式创建组件")
    print("3. 从 JSON 文件创建组件")
    print("4. 运行所有示例")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == "1":
        example_code_creation()
    elif choice == "2":
        example_json_creation()
    elif choice == "3":
        example_from_json_file()
    elif choice == "4":
        example_code_creation()
        example_json_creation()
        example_from_json_file()
    else:
        print("已退出")


if __name__ == "__main__":
    main()

