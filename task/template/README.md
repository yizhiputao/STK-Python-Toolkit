# Task Template

一组可直接运行的示例脚本，帮助你在 STK 场景里快速创建/删除卫星并生成报告。可把这里当作"脚手架"：拷贝到新的任务目录后按需修改即可。

## 目录结构

```
task/template/
├── create_satellite_json.py   # 读取 JSON 批量创建卫星
├── delete_satellite.py        # 批量删除卫星
├── report.py                  # 生成文本报告
├── satellite3_config.json     # 示例配置
├── satellite4_config.json     # 示例配置
└── report/                    # report.py 输出目录
```

## 使用说明

### 环境准备

1. Windows + Python 3.8+
2. AGI STK11 必须已启动并加载场景（脚本不会自行启动 STK）
3. 在仓库根目录执行 `python -m pip install comtypes`（若尚未安装）

### 批量创建：`create_satellite_json.py`

- `SATELLITES_TO_CREATE`：填入卫星名称列表，或设为 `["ALL"]`（大小写不敏感）按文件名顺序遍历当前目录下所有 `*.json`。
- JSON 命名推荐 `<Name>_config.json`，结构与 `example_scenario.json` 相同。
- `DELETE_EXISTING_BEFORE_CREATE`:
  - `True`（默认推荐）：遇到同名卫星先删除再创建，确保幂等。
  - `False`：检测到同名卫星会打印提示并跳过创建。
- 运行方式：
  ```bash
  python task/template/create_satellite_json.py
  ```

### 批量删除：`delete_satellite.py`

- 在 `SATELLITES_TO_DELETE` 中列出待删除的卫星。
- 运行脚本会逐个调用 `SatelliteComponent.delete_by_name`，多次执行安全。

### 生成报告：`report.py`

- 将报告输出目录固定为 `task/template/report/`，便于查看最新结果。
- 会调用 `ReportGenerator` 输出文本报告并保存副本。

## 扩展建议

- 复制 `satellite*_config.json` 改名即可新增模板；别忘了在 `SATELLITES_TO_CREATE` 中加入对应名称。
- 若要在其他任务中使用，可整个复制 `task/template`，然后根据场景修改脚本参数。
- 所有脚本都使用 `sys.path` 注入项目根目录，因此无论从仓库根目录还是子路径运行都能导入 `stk_toolkit`。

## 常见问题

- **执行脚本却没有输出？** 确认 STK11 已运行；若使用 `python -m trace` 等方式运行，标准输出可能被截断，可直接 `python task/template/create_satellite_json.py` 验证。
- **找不到 JSON 文件？** 检查文件命名是否为 `<Name>_config.json` 或 `<Name>.json`，脚本会在这些组合中寻找。
- **想保留已有卫星不覆盖？** 将 `DELETE_EXISTING_BEFORE_CREATE` 设为 `False`，脚本会跳过已存在的卫星。

## 下一步

- 编辑 JSON 内容或 Python 脚本，即可快速搭建新的任务模板。
- 如果这些脚本需要共享给团队，建议复制到 `task/<your-task>/` 并在主 README 里说明。


