"""
STK 场景报告生成工具
可作为独立脚本运行，也可作为模块导入复用
"""

import os
from stk_toolkit import STKConnection
from stk_toolkit.reports import ReportGenerator, ReportFormat


def generate_report(output_dir=None, verbose=True, format=ReportFormat.TEXT):
    """
    生成STK场景报告（核心函数）
    
    Args:
        output_dir: 报告输出目录，默认为当前工作目录下的 report/
        verbose: 是否显示详细输出信息
        format: 报告格式，默认为 TEXT
        
    Returns:
        str: 报告内容
        
    Raises:
        STKConnectionError: STK连接失败
        STKReportError: 报告生成失败
    """
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "report")
    
    # 创建目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    if verbose:
        print(f"✓ 报告输出目录: {output_dir}")
    
    # 连接STK并生成报告
    with STKConnection() as connection:
        if verbose:
            print("✓ 已连接到 STK11")
            print("✓ 已获取 STK Root 对象")
        
        # 创建报告生成器
        generator = ReportGenerator(connection, output_dir=output_dir)
        
        # 生成场景报告
        report = generator.generate_scenario_report(format=format, save=True)
        
        return report.generate(format)


def generate_report_safe(output_dir=None, verbose=True, format=ReportFormat.TEXT):
    """
    生成STK场景报告（安全版本，自动处理异常）
    
    Args:
        output_dir: 报告输出目录，默认为当前工作目录下的 report/
        verbose: 是否显示详细输出信息
        format: 报告格式，默认为 TEXT
        
    Returns:
        tuple: (success: bool, content_or_error: str)
            - success: True表示成功，False表示失败
            - content_or_error: 成功时返回报告内容，失败时返回错误信息
    """
    try:
        content = generate_report(output_dir, verbose, format)
        return True, content
    except Exception as e:
        error_msg = f"✗ 错误: {e}\n请确保 STK11 正在运行并已打开场景"
        if verbose:
            print(error_msg)
        return False, str(e)


def main():
    """命令行入口：从项目根目录运行"""
    print("=" * 60)
    print("       STK 场景详细信息读取工具")
    print("=" * 60)
    
    print("\n【连接 STK】")
    
    # 使用安全版本生成报告（默认在当前目录的 report/ 下）
    success, content = generate_report_safe(verbose=True)
    
    if success:
        # 打印报告内容
        print(content)
        print("\n[OK] 报告生成完成")
    else:
        # 错误信息已在 generate_report_safe 中打印
        pass


if __name__ == "__main__":
    main()

