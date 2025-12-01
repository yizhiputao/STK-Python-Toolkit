"""
按名称批量删除地面站
"""

import os
import sys
from typing import Iterable

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components import FacilityComponent

# 需要删除的地面站名称列表，可按需修改
FACILITIES_TO_DELETE = ["Beijing", "Shanghai"]


def _delete_facilities(connection: STKConnection, names: Iterable[str]) -> None:
    """逐个删除给定名称列表中的地面站。"""
    for name in names:
        if not name:
            continue
        if FacilityComponent.delete_by_name(connection, name):
            print(f"已删除地面站: {name}")
        else:
            print(f"地面站不存在: {name}")


def main():
    if not FACILITIES_TO_DELETE:
        print("FACILITIES_TO_DELETE 为空，未执行删除操作。")
        return

    with STKConnection() as connection:
        print("已连接到 STK")
        _delete_facilities(connection, FACILITIES_TO_DELETE)


if __name__ == "__main__":
    main()

