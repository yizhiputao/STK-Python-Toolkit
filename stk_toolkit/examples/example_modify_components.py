"""
示例: 修改 STK 组件
演示如何修改已存在的卫星和地面站参数
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stk_toolkit import STKConnection
from stk_toolkit.modifiers import SatelliteModifier, FacilityModifier


def example_modify_satellite():
    """修改卫星参数"""
    print("\n" + "=" * 60)
    print("示例 1: 修改卫星参数")
    print("=" * 60)
    
    with STKConnection() as connection:
        modifier = SatelliteModifier(connection)
        
        # 加载已存在的卫星
        satellite_name = input("\n请输入要修改的卫星名称 (如 Satellite1): ").strip()
        if not satellite_name:
            satellite_name = "Satellite1"
        
        try:
            modifier.load(satellite_name)
            print(f"✓ 已加载卫星: {satellite_name}")
        except Exception as e:
            print(f"✗ 加载失败: {e}")
            return
        
        # 方式1: 使用 apply 批量修改
        print("\n使用 apply 方法修改轨道参数...")
        modifier.apply({
            "orbit": {
                "semi_major_axis": 7100,  # 修改半长轴
                "inclination": 98.0       # 修改倾角
            }
        })
        print("✓ 轨道参数已修改")
        
        # 方式2: 使用 set 方法单独修改
        # modifier.set("orbit.semi_major_axis", 7200)
        
        # 方式3: 使用直接方法
        # modifier.set_orbit(semi_major_axis=7200, eccentricity=0.001)
        
        # 修改传播器步长
        modifier.set_propagator_step(120)
        print("✓ 传播器步长已修改为 120 秒")


def example_modify_facility():
    """修改地面站参数"""
    print("\n" + "=" * 60)
    print("示例 2: 修改地面站参数")
    print("=" * 60)
    
    with STKConnection() as connection:
        modifier = FacilityModifier(connection)
        
        # 加载已存在的地面站
        facility_name = input("\n请输入要修改的地面站名称 (如 Facility1): ").strip()
        if not facility_name:
            facility_name = "Facility1"
        
        try:
            modifier.load(facility_name)
            print(f"✓ 已加载地面站: {facility_name}")
        except Exception as e:
            print(f"✗ 加载失败: {e}")
            return
        
        # 方式1: 修改位置
        print("\n修改地面站位置...")
        modifier.set_position(
            latitude=39.9,
            longitude=116.4,
            altitude=0.1
        )
        print("✓ 位置已修改")
        
        # 方式2: 修改约束
        print("\n修改仰角约束...")
        modifier.set_constraint("ElevationAngle", min_value=15.0)
        print("✓ 仰角约束已修改为 >= 15 度")
        
        # 方式3: 批量修改
        # modifier.apply({
        #     "position": {"latitude": 40.0, "longitude": 116.0},
        #     "constraints": [
        #         {"name": "ElevationAngle", "min": 10.0},
        #         {"name": "SunElevationAngle", "max": -6.0}
        #     ]
        # })


def main():
    """运行示例"""
    print("=" * 60)
    print("       STK 组件修改示例")
    print("=" * 60)
    print("\n注意: 此示例会修改 STK 中已存在的对象")
    print("请确保 STK 已打开并且场景中有相应的对象\n")
    
    print("请选择要运行的示例:")
    print("1. 修改卫星参数")
    print("2. 修改地面站参数")
    print("3. 运行所有示例")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-3): ").strip()
    
    if choice == "1":
        example_modify_satellite()
    elif choice == "2":
        example_modify_facility()
    elif choice == "3":
        example_modify_satellite()
        example_modify_facility()
    else:
        print("已退出")


if __name__ == "__main__":
    main()

