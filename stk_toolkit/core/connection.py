"""
STK 连接模块
负责与 STK 建立连接、管理连接状态、提供基础交互接口
"""

import comtypes.client
from typing import Optional, Any
from .exceptions import STKConnectionError


class STKConnection:
    """
    STK 连接管理类
    
    负责:
    - 连接到已运行的 STK 实例
    - 获取 STK 根对象
    - 获取当前场景
    - 执行 STK Connect 命令
    
    使用示例:
        with STKConnection() as stk:
            scenario = stk.current_scenario
            print(f"场景名称: {scenario.InstanceName}")
    """
    
    # STK 版本常量
    STK11 = "STK11.Application"
    STK12 = "STK12.Application"
    
    def __init__(self, version: str = STK11):
        """
        初始化 STK 连接
        
        Args:
            version: STK 版本标识符，默认为 STK11
        """
        self._version = version
        self._app = None
        self._root = None
        self._stk_objects = None
        
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 注意：不主动关闭 STK，只断开连接
        self._app = None
        self._root = None
        return False
    
    def connect(self) -> "STKConnection":
        """
        连接到已运行的 STK 实例
        
        Returns:
            self: 返回自身以支持链式调用
            
        Raises:
            STKConnectionError: 连接失败时抛出
        """
        try:
            self._app = comtypes.client.GetActiveObject(self._version)
            self._root = self._app.Personality2
            # 动态导入 STKObjects
            self._stk_objects = comtypes.gen.STKObjects
        except Exception as e:
            raise STKConnectionError(
                f"无法连接到 {self._version}，请确保 STK 正在运行并已打开场景。\n"
                f"错误详情: {e}"
            )
        return self
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._app is not None and self._root is not None
    
    @property
    def app(self) -> Any:
        """获取 STK Application 对象"""
        self._ensure_connected()
        return self._app
    
    @property
    def root(self) -> Any:
        """获取 STK Root 对象"""
        self._ensure_connected()
        return self._root
    
    @property
    def stk_objects(self) -> Any:
        """获取 STKObjects 模块引用"""
        self._ensure_connected()
        return self._stk_objects
    
    @property
    def current_scenario(self) -> Any:
        """
        获取当前场景对象
        
        Returns:
            IAgScenario: 当前场景对象
        """
        self._ensure_connected()
        return self._root.CurrentScenario
    
    @property
    def scenario_interface(self) -> Any:
        """
        获取当前场景的 IAgScenario 接口
        
        Returns:
            IAgScenario: 场景接口
        """
        scenario = self.current_scenario
        return scenario.QueryInterface(self._stk_objects.IAgScenario)
    
    def _ensure_connected(self):
        """确保已连接到 STK"""
        if not self.is_connected:
            raise STKConnectionError("未连接到 STK，请先调用 connect() 方法")
    
    def execute_command(self, command: str) -> str:
        """
        执行 STK Connect 命令
        
        Args:
            command: STK Connect 命令字符串
            
        Returns:
            str: 命令执行结果
        """
        self._ensure_connected()
        try:
            result = self._root.ExecuteCommand(command)
            return str(result)
        except Exception as e:
            raise STKConnectionError(f"执行命令失败: {command}\n错误: {e}")
    
    def get_children(self, parent: Optional[Any] = None) -> list:
        """
        获取子对象列表
        
        Args:
            parent: 父对象，默认为当前场景
            
        Returns:
            list: 子对象列表
        """
        self._ensure_connected()
        if parent is None:
            parent = self.current_scenario
        
        children = []
        child_collection = parent.Children
        for i in range(child_collection.Count):
            children.append(child_collection.Item(i))
        return children
    
    def get_object_by_path(self, path: str) -> Any:
        """
        根据路径获取对象
        
        Args:
            path: 对象路径，如 "Satellite/MySat"
            
        Returns:
            对象引用
        """
        self._ensure_connected()
        return self._root.GetObjectFromPath(path)
    
    def get_scenario_info(self) -> dict:
        """
        获取场景基本信息
        
        Returns:
            dict: 包含场景信息的字典
        """
        self._ensure_connected()
        scenario = self.current_scenario
        scenario2 = self.scenario_interface
        
        return {
            "name": scenario.InstanceName,
            "path": scenario.Path,
            "start_time": scenario2.StartTime,
            "stop_time": scenario2.StopTime,
            "epoch": scenario2.Epoch,
        }

