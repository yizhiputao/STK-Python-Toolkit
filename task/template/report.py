"""
生成 STK 场景报告
"""

import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.reports import ReportGenerator, ReportFormat


def main():
    # 报告输出目录
    report_dir = os.path.join(os.path.dirname(__file__), "report")
    os.makedirs(report_dir, exist_ok=True)
    
    with STKConnection() as connection:
        print("已连接到 STK")
        
        # 生成报告
        generator = ReportGenerator(connection, output_dir=report_dir)
        report = generator.generate_scenario_report(format=ReportFormat.TEXT, save=True)
        
        # 打印报告
        print(report.generate(ReportFormat.TEXT))
        print(f"\n报告已保存到: {report_dir}")


if __name__ == "__main__":
    main()

