"""
使用 JSON 配置批量创建地面站。

1. 通过 FACILITIES_TO_CREATE 指定要创建的地面站列表，自动匹配对应的 xxx.json 文件；
   也可以填写 ["ALL"]，遍历配置目录下所有 JSON。
2. 可通过 DELETE_EXISTING_BEFORE_CREATE 控制遇到同名地面站的行为：
   - True: 先删除旧地面站再重新创建
   - False: 不删除也不创建，打印提示
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components.factory import ComponentFactory
from stk_toolkit.components.facility import FacilityComponent

# 需要创建的地面站名称列表，可在此扩展，例如 ["Beijing", "Shanghai"]
# 若设置为 ["ALL"]（大小写不敏感），将遍历 CONFIG_DIR 下所有 JSON 文件
FACILITIES_TO_CREATE: List[str] = ["Beijing", "Shanghai"]
#FACILITIES_TO_CREATE: List[str] = ["all"]

# 若为 True，遇到同名地面站时将先删除再创建；若为 False，则跳过创建并打印提示
DELETE_EXISTING_BEFORE_CREATE = True

# 配置文件所在目录，默认为脚本同目录
CONFIG_DIR = Path(SCRIPT_DIR)


def _resolve_config_path(facility_name: str) -> Path:
    """
    根据地面站名称推导 JSON 配置文件路径。
    优先匹配 `<Name>_config.json`，若不存在则回退到大小写变体及 `<Name>.json`。
    """
    candidates = [
        CONFIG_DIR / f"{facility_name}_config.json",
        CONFIG_DIR / f"{facility_name.lower()}_config.json",
        CONFIG_DIR / f"{facility_name}.json",
        CONFIG_DIR / f"{facility_name.lower()}.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    available = ", ".join(str(p.name) for p in CONFIG_DIR.glob("*.json"))
    raise FileNotFoundError(
        f"未找到 {facility_name} 对应的 JSON 配置文件，已检查: "
        f"{', '.join(str(p) for p in candidates)}。当前目录下可用文件: {available or '无'}"
    )


def _list_all_config_paths() -> List[Path]:
    """遍历配置目录中的所有 JSON 文件，按名称排序返回。"""
    paths = sorted(CONFIG_DIR.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"{CONFIG_DIR} 下未找到任何 JSON 配置文件")
    return paths


def _load_config(config_path: Path) -> Dict[str, Any]:
    """读取 JSON 配置为字典。"""
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _prepare_components(
    connection: STKConnection, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    根据 DELETE_EXISTING_BEFORE_CREATE 选项处理配置：
    - True: 删除已存在的同名地面站，并保留在待创建列表中
    - False: 跳过已存在的地面站
    非地面站组件不受影响
    """
    components = config.get("components", []) or []
    ready: List[Dict[str, Any]] = []

    for component in components:
        comp_type = component.get("type", "")
        if comp_type.lower() != "facility":
            ready.append(component)
            continue

        name = component.get("name")
        if not name:
            continue

        exists = FacilityComponent.exists(connection, name)
        if not exists:
            ready.append(component)
            continue

        if DELETE_EXISTING_BEFORE_CREATE:
            if FacilityComponent.delete_by_name(connection, name):
                print(f"已删除存在的地面站：{name}")
            ready.append(component)
        else:
            print(f"检测到已存在地面站 {name}，跳过创建（DELETE_EXISTING_BEFORE_CREATE=False）")

    return ready


def _create_components(factory: ComponentFactory, config: Dict[str, Any]) -> None:
    """通过组件工厂创建配置中的所有组件。"""
    components = config.get("components")
    if not components:
        print("配置中未找到 components，跳过。")
        return
    factory.create_many(components)


def main():
    targets: List[tuple[str, Path]] = []
    if not FACILITIES_TO_CREATE:
        print("FACILITIES_TO_CREATE 为空，未执行任何创建操作。")
        return

    if len(FACILITIES_TO_CREATE) == 1 and FACILITIES_TO_CREATE[0].lower() == "all":
        for path in _list_all_config_paths():
            targets.append((path.stem, path))
    else:
        for facility_name in FACILITIES_TO_CREATE:
            path = _resolve_config_path(facility_name)
            targets.append((facility_name, path))

    with STKConnection() as connection:
        factory = ComponentFactory(connection)
        for facility_name, config_path in targets:
            print(f"开始创建 {facility_name}，配置文件: {config_path}", flush=True)
            config = _load_config(config_path)
            components_to_create = _prepare_components(connection, config)
            if not components_to_create:
                print(f"{facility_name} 无需创建（所有组件均被跳过）", flush=True)
                continue
            _create_components(factory, {"components": components_to_create})
            print(f"{facility_name} 已通过 {config_path.name} 创建完成", flush=True)


if __name__ == "__main__":
    main()


