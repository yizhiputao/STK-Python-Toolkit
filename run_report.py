"""
快速运行: 生成 STK 场景报告
使用新的模块化架构
"""

import os
from stk_toolkit import STKConnection
from stk_toolkit.reports import ReportGenerator, ReportFormat


def get_report_dir():
    """
    获取报告输出目录
    检查当前工作目录下是否有 report 文件夹，没有则创建
    
    Returns:
        str: 报告目录的绝对路径
    """
    # 获取当前工作目录
    cwd = os.getcwd()
    report_dir = os.path.join(cwd, "report")
    
    # 如果不存在则创建
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"✓ 已创建报告目录: {report_dir}")
    
    return report_dir


def main():
    print("=" * 60)
    print("       STK 场景详细信息读取工具 (模块化版本)")
    print("=" * 60)
    
    print("\n【连接 STK】")
    
    try:
        with STKConnection() as connection:
            print("✓ 已连接到 STK11")
            print("✓ 已获取 STK Root 对象")
            
            # 获取报告输出目录 (当前工作目录下的 report 文件夹)
            report_dir = get_report_dir()
            
            # 创建报告生成器
            generator = ReportGenerator(connection, output_dir=report_dir)
            
            # 生成场景报告 (文本格式)
            report = generator.generate_scenario_report(
                format=ReportFormat.TEXT,
                save=True
            )
            
            # 打印报告内容
            print(report.generate(ReportFormat.TEXT))
            
            print(f"\n[OK] 报告已保存到: {report_dir}")
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        print("请确保 STK11 正在运行并已打开场景")


if __name__ == "__main__":
    main()

