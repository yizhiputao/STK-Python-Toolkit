# STK Python Toolkit

一个高内聚低耦合的 STK (Systems Tool Kit) Python 工具包，用于与 AGI STK11 进行交互。

## 功能特性

- **STK 连接管理**: 连接到已运行的 STK 实例，执行命令和读取数据
- **组件管理**: 支持代码和 JSON 两种方式创建、删除、查询卫星、地面站等组件
- **组件修改**: 修改已存在组件的参数（轨道、位置、约束等）
- **报告生成**: 生成场景状态报告，支持 TXT 和 JSON 格式
- **条件分析**: 预留访问分析、覆盖分析等功能接口

## 项目结构

```
.
├── stk_toolkit/                # 工具包核心
│   ├── core/                   # 连接、异常
│   ├── components/             # 组件创建/删除
│   ├── modifiers/              # 组件修改
│   ├── conditions/             # 预留条件模块
│   └── reports/                # 报告生成
├── task/
│   └── template/               # 可直接运行的任务模板
│       ├── create_satellite_json.py
│       ├── create_satellite.py
│       ├── delete_satellite.py
│       ├── report.py
│       ├── satellite*_config.json
│       └── report/
├── examples/                   # 其他示例脚本
├── run_report.py               # 快速生成场景报告
├── example_scenario.json       # JSON 配置样例
└── README.md / llm.txt         # 文档与 LLM 指南
```

## 任务模板 (`task/template/`)

- `create_satellite_json.py`: 读取目录内的 `*.json` 批量创建卫星，支持 `["ALL"]` 与是否覆盖的开关。
- `delete_satellite.py`: 依据列表批量删除卫星，确保重复执行幂等。
- `report.py`: 生成并保存最新的场景文本报告。
- `create_satellite.py`: 直接按照脚本常量创建单颗卫星，可设置是否覆盖同名对象。
- `satellite*_config.json`: 可复制扩展的配置模板。

> 详细使用说明请见 `task/template/README.md`。

## 环境要求

- Python 3.8+
- AGI STK 11 (需要已安装并运行)
- Windows 操作系统 (STK COM 接口仅支持 Windows)

## 依赖安装

```bash
pip install comtypes
```

## 快速开始

### 1. 使用模板脚本（推荐）

```bash
python task/template/create_satellite_json.py   # 按配置批量创建卫星
python task/template/report.py                 # 输出最新场景报告
python task/template/delete_satellite.py       # 清理不需要的卫星
```

> 修改 `task/template/satellite*_config.json` 或脚本内的列表，即可快速适配自己的场景。更多细节见 `task/template/README.md`。

### 2. 生成场景报告

```python
from stk_toolkit import STKConnection
from stk_toolkit.reports import ReportGenerator, ReportFormat

with STKConnection() as connection:
    generator = ReportGenerator(connection, output_dir="./reports")
    report = generator.generate_scenario_report(format=ReportFormat.TEXT)
```

也可以直接运行 `python run_report.py`（或 `task/template/report.py`）快速获取报告文件。

### 3. 自定义代码（可选）

```python
from stk_toolkit import STKConnection
from stk_toolkit.components import ComponentFactory

with STKConnection() as connection:
    factory = ComponentFactory(connection)
    factory.create_from_json("example_scenario.json")
```

更多示例与高级用法可参考 `stk_toolkit/examples/` 与模板脚本。

## API 参考

### STKConnection

| 方法/属性 | 说明 |
|-----------|------|
| `connect()` | 连接到 STK |
| `root` | 获取 STK Root 对象 |
| `current_scenario` | 获取当前场景 |
| `get_scenario_info()` | 获取场景基本信息 |
| `get_children()` | 获取场景子对象 |
| `execute_command(cmd)` | 执行 STK Connect 命令 |

### SatelliteComponent

| 方法 | 说明 |
|------|------|
| `create(**kwargs)` | 创建卫星 |
| `delete()` | 删除卫星 (实例方法) |
| `exists(connection, name)` | 检查卫星是否存在 (静态方法) |
| `delete_by_name(connection, name)` | 按名称删除卫星 (静态方法) |
| `get_info()` | 获取卫星信息 |
| `from_dict(config)` | 从字典创建 |
| `to_dict()` | 导出为字典 |

**轨道参数:**
- `semi_major_axis`: 半长轴 (km)
- `eccentricity`: 偏心率
- `inclination`: 轨道倾角 (deg)
- `raan`: 升交点赤经 (deg)
- `arg_of_perigee`: 近地点幅角 (deg)
- `true_anomaly`: 真近点角 (deg)

### FacilityComponent

| 方法 | 说明 |
|------|------|
| `create(**kwargs)` | 创建地面站 |
| `set_constraint(name, min, max)` | 设置约束 |
| `get_info()` | 获取地面站信息 |

**位置参数:**
- `latitude`: 纬度 (deg)
- `longitude`: 经度 (deg)
- `altitude`: 海拔 (km)

### 支持的约束类型

- `ElevationAngle`: 仰角约束
- `SunElevationAngle`: 太阳仰角约束
- `LunarElevationAngle`: 月球仰角约束
- `LineOfSight`: 视线约束

## 扩展开发

### 添加新的组件类型

1. 在 `components/` 下创建新文件 (如 `sensor.py`)
2. 继承 `ComponentBase` 类
3. 实现必要的抽象方法
4. 在 `ComponentFactory` 中注册新类型

```python
from stk_toolkit.components import ComponentFactory, ComponentType

# 注册新组件
ComponentFactory.register_component(ComponentType.SENSOR, SensorComponent)
ComponentFactory.register_type_name("Sensor", ComponentType.SENSOR)
```

### 添加新的报告类型

1. 在 `reports/` 下创建新文件
2. 继承 `ReportBase` 类
3. 在 `ReportGenerator` 中注册

```python
from stk_toolkit.reports import ReportGenerator

ReportGenerator.register("access", AccessReport)
```

## 注意事项

1. **STK 必须已经运行**: 本工具包假设 STK 已经打开，不会自动启动 STK
2. **场景必须已加载**: 连接前需要确保 STK 中已打开场景
3. **Windows 限制**: STK COM 接口仅在 Windows 上可用

## 示例文件

| 文件 | 说明 |
|------|------|
| `run_report.py` | 快速生成场景报告 |
| `example_scenario.json` | JSON 配置示例 |
| `stk_toolkit/examples/` | 更多示例代码 |
| `task/template/` | 任务模板脚本（批量创建/删除/报告示例） |

## Git 版本控制

本项目已配置 Git 版本控制。

### 初始化 Git 仓库

**首次使用（需要重启 PowerShell）：**

1. 重启 PowerShell 或 Cursor IDE
2. 运行初始化脚本：
   ```bash
   .\init_git.ps1
   ```

### 常用 Git 命令

```bash
# 查看当前状态
git status

# 添加文件到暂存区
git add <文件名>              # 添加单个文件
git add .                     # 添加所有更改

# 提交更改
git commit -m "提交说明"

# 查看提交历史
git log

# 查看文件差异
git diff                      # 查看未暂存的更改
git diff --staged             # 查看已暂存的更改

# 分支操作
git branch                    # 查看分支
git checkout -b <分支名>      # 创建并切换分支
git checkout <分支名>         # 切换分支

# 远程仓库（如果需要）
git remote add origin <仓库URL>
git push -u origin main
```

### .gitignore 说明

项目已配置 `.gitignore` 文件，自动忽略：
- Python 缓存文件 (`__pycache__`, `*.pyc`)
- 虚拟环境目录 (`venv/`, `env/`)
- IDE 配置文件 (`.vscode/`, `.idea/`)
- 生成的报告文件（除了 `scenario_report_latest.txt`）
- 归档文件 (`archive/`)

## License

MIT License

