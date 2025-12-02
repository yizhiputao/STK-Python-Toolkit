"""
报告生成工具函数
提供便捷的报告生成和组件导出功能
"""

import os
from stk_toolkit import STKConnection
from .generator import ReportGenerator
from .base import ReportFormat
from ..exports import export_components_to_json


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


def generate_report_and_export(
    report_output_dir=None,
    export_output_dir=None,
    verbose=True,
    format=ReportFormat.TEXT,
    export_enabled=True
):
    """
    生成报告并导出组件配置（完整流程）
    
    Args:
        report_output_dir: 报告输出目录，默认为当前工作目录下的 report/
        export_output_dir: 导出输出目录，默认为 report_output_dir 的父目录下的 exports/
        verbose: 是否显示详细输出信息
        format: 报告格式，默认为 TEXT
        export_enabled: 是否启用组件导出
        
    Returns:
        tuple: (success: bool, report_content: str, export_result: dict or None)
            - success: True表示成功，False表示失败
            - report_content: 报告内容（成功时）或错误信息（失败时）
            - export_result: 导出结果字典（如果启用导出）或 None
    """
    # 生成报告
    success, content = generate_report_safe(
        output_dir=report_output_dir,
        verbose=verbose,
        format=format
    )
    
    export_result = None
    
    if success and export_enabled:
        # 导出组件配置
        if verbose:
            print("\n【导出组件配置】")
        
        try:
            # 确定导出目录
            if export_output_dir is None:
                if report_output_dir:
                    # 使用报告目录的父目录作为导出基础目录
                    report_abs = os.path.abspath(report_output_dir)
                    export_base_dir = os.path.dirname(report_abs)
                else:
                    export_base_dir = os.getcwd()
                export_output_dir = os.path.join(export_base_dir, "exports")
            
            with STKConnection() as connection:
                result = export_components_to_json(
                    connection=connection,
                    output_dir=export_output_dir,
                    package=True
                )
                export_result = result
                
                if verbose:
                    print(f"✓ 组件已导出到: {result['export_dir']}")
                    if 'zip_path' in result:
                        print(f"✓ 已打包为: {result['zip_path']}")
        except Exception as e:
            if verbose:
                print(f"✗ 组件导出失败: {e}")
                import traceback
                traceback.print_exc()
            export_result = {"error": str(e)}
    
    return success, content, export_result

