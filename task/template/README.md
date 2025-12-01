# Task Template

一组可直接运行的示例脚本，帮助你在 STK 场景里快速创建/删除组件（卫星、地面站等）并生成报告。可把这里当作"脚手架"：拷贝到新的任务目录后按需修改即可。

## 目录结构

```
task/template/
├── configs/                      # 配置文件目录
│   ├── satellites/               # 卫星配置
│   │   ├── satellite3_config.json
│   │   └── satellite4_config.json
│   └── facilities/               # 地面站配置
│       ├── Beijing_config.json
│       └── Shanghai_config.json
├── create_components_json.py     # 通用组件批量创建脚本
├── delete_components.py          # 通用组件批量删除脚本
├── report.py                     # 生成文本报告
└── report/                       # report.py 输出目录
```

## 使用说明

### 环境准备

1. Windows + Python 3.8+
2. AGI STK11 必须已启动并加载场景（脚本不会自行启动 STK）
3. 在仓库根目录执行 `python -m pip install comtypes`（若尚未安装）

### 批量创建：`create_components_json.py`

**通用组件创建脚本**，支持所有类型的组件（卫星、地面站等）。

**方式1：命令行参数（推荐）**
```bash
# 创建指定的卫星和地面站
python create_components_json.py --satellites satellite3 satellite4 --facilities Beijing

# 只创建所有卫星
python create_components_json.py --satellites ALL

# 创建所有组件
python create_components_json.py --all

# 不删除已存在的同名组件（默认会先删除）
python create_components_json.py --satellites satellite3 --no-delete
```

**方式2：配置文件**
```bash
# 使用默认配置文件（configs/create_config.json）
python create_components_json.py

# 使用指定配置文件
python create_components_json.py --config my_config.json
```

**配置文件格式（JSON）：**
```json
{
  "satellites": ["satellite3", "satellite4"],
  "facilities": ["Beijing", "Shanghai"],
  "delete_existing": true
}
```

**配置文件组织：**
- 卫星配置放在 `configs/satellites/`
- 地面站配置放在 `configs/facilities/`
- 自动识别子目录类型

**优先级：** 命令行参数 > --config 指定的文件 > 默认配置文件

### 批量删除：`delete_components.py`

**通用组件删除脚本**，支持混合删除多种类型的组件。

**方式1：命令行参数（推荐）**
```bash
# 删除指定的卫星和地面站
python delete_components.py --satellites Satellite3 Satellite4 --facilities Beijing

# 只删除卫星
python delete_components.py --satellites Satellite3 Satellite4
```

**方式2：配置文件**
```bash
# 使用默认配置文件（configs/delete_config.json）
python delete_components.py

# 使用指定配置文件
python delete_components.py --config my_delete_config.json
```

**配置文件格式（JSON）：**
```json
{
  "Satellite": ["Satellite2", "Satellite3"],
  "Facility": ["Beijing", "Shanghai"]
}
```

**优先级：** 命令行参数 > --config 指定的文件 > 默认配置文件

### 生成报告：`report.py`

- 将报告输出目录固定为 `task/template/report/`，便于查看最新结果。
- 会调用 `ReportGenerator` 输出文本报告并保存副本。

## 扩展建议

- **添加新配置**：在对应的 `configs/` 子目录下添加新的 JSON 文件即可，无需修改脚本。
- **添加新组件类型**：在 `create_components_json.py` 和 `delete_components.py` 的 `COMPONENT_TYPE_MAP` 中添加新类型映射。
- **混合配置**：可以在同一个 JSON 文件中配置多种类型的组件（参考 `example_scenario.json`）。
- **任务复制**：整个复制 `task/template` 到新任务目录，根据场景修改配置文件即可。
- **跨目录运行**：所有脚本使用 `sys.path` 注入项目根目录，从任何位置运行都能正确导入 `stk_toolkit`。

## 常见问题

- **执行脚本却没有输出？** 确认 STK11 已运行并加载场景。
- **找不到 JSON 文件？** 检查文件是否在正确的子目录下（satellites/ 或 facilities/），命名是否符合 `<Name>_config.json` 或 `<Name>.json`。
- **想保留已有对象不覆盖？** 将 `DELETE_EXISTING_BEFORE_CREATE` 设为 `False`，脚本会跳过已存在的对象。
- **多种类型一起操作？** 使用通用脚本可以同时创建/删除卫星和地面站，只需在配置中指定即可。
- **如何添加新的组件类型（如 Sensor）？** 在 `configs/` 下创建 `sensors/` 目录，然后在脚本的 `COMPONENT_TYPE_MAP` 中添加映射。

## 下一步

- 编辑 JSON 内容或 Python 脚本，即可快速搭建新的任务模板。
- 如果这些脚本需要共享给团队，建议复制到 `task/<your-task>/` 并在主 README 里说明。


