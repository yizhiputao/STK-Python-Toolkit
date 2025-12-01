"""
按名称批量删除卫星
"""

import os
import sys
from typing import Iterable

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components import SatelliteComponent

# 需要删除的卫星名称列表，可按需修改
SATELLITES_TO_DELETE = ["Satellite2", "Satellite3", "Satellite4"]


def _delete_satellites(connection: STKConnection, names: Iterable[str]) -> None:
    """逐个删除给定名称列表中的卫星。"""
    for name in names:
        if not name:
            continue
        if SatelliteComponent.delete_by_name(connection, name):
            print(f"已删除卫星: {name}")
        else:
            print(f"卫星不存在: {name}")


def main():
    if not SATELLITES_TO_DELETE:
        print("SATELLITES_TO_DELETE 为空，未执行删除操作。")
        return

    with STKConnection() as connection:
        print("已连接到 STK")
        _delete_satellites(connection, SATELLITES_TO_DELETE)


if __name__ == "__main__":
    main()
