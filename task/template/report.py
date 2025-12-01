"""
模板脚本：在 task/template 目录下生成报告
快捷使用：cd task/template && python report.py
"""

import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from run_report import generate_report_safe


def main():
    """在当前目录下生成报告"""
    # 报告输出目录：脚本所在目录的 report/ 子目录
    report_dir = os.path.join(os.path.dirname(__file__), "report")
    
    print("【生成报告】")
    
    # 使用安全版本生成报告
    success, content = generate_report_safe(output_dir=report_dir, verbose=True)
    
    if success:
        # 打印报告内容
        print(content)
        print(f"\n✓ 报告已保存到: {report_dir}")
    else:
        # 错误信息已在 generate_report_safe 中打印
        pass


if __name__ == "__main__":
    main()

