"""
示例: 生成场景报告
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stk_toolkit import STKConnection
from stk_toolkit.reports import ReportGenerator, ReportFormat


def main():
    """生成场景报告示例"""
    print("=" * 60)
    print("       STK 场景报告生成示例")
    print("=" * 60)
    
    # 使用上下文管理器连接 STK
    with STKConnection() as connection:
        print(f"\n✓ 已连接到 STK")
        
        # 获取场景信息
        info = connection.get_scenario_info()
        print(f"✓ 当前场景: {info['name']}")
        
        # 创建报告生成器
        generator = ReportGenerator(connection, output_dir="./report")
        
        # 生成文本格式报告
        print("\n生成文本格式报告...")
        report = generator.generate_scenario_report(format=ReportFormat.TEXT)
        print(f"✓ 报告已生成")
        
        # 也可以生成 JSON 格式
        print("\n生成 JSON 格式报告...")
        json_report = generator.generate_scenario_report(
            format=ReportFormat.JSON,
            title="STK 场景信息 (JSON)"
        )
        print(f"✓ JSON 报告已生成")
        
        # 打印报告内容预览
        print("\n" + "=" * 60)
        print("报告内容预览:")
        print("=" * 60)
        print(report.generate(ReportFormat.TEXT))


if __name__ == "__main__":
    main()

