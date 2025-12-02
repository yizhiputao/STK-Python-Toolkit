"""
STK 场景报告生成工具 - 命令行入口
快速生成场景报告并导出组件配置
"""

from stk_toolkit.reports import generate_report_and_export


def main():
    """命令行入口：从项目根目录运行"""
    print("=" * 60)
    print("       STK 场景详细信息读取工具")
    print("=" * 60)
    
    print("\n【连接 STK】")
    
    # 生成报告并导出组件
    success, content, export_result = generate_report_and_export(
        verbose=True,
        export_enabled=True
    )
    
    if success:
        # 打印报告内容
        print(content)
        print("\n[OK] 报告生成完成")
    else:
        # 错误信息已在 generate_report_safe 中打印
        pass


if __name__ == "__main__":
    main()

