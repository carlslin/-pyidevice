"""类型定义模块"""

from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum


class DeviceStatus(Enum):
    """设备状态枚举"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"


class ExecutorType(Enum):
    """执行器类型枚举"""

    THREAD = "thread"
    PROCESS = "process"


class LogLevel(Enum):
    """日志级别枚举"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# 类型别名
DeviceInfo = Dict[str, Any]
AppInfo = Dict[str, str]
BatteryInfo = Dict[str, Union[int, bool, None]]
ScreenshotResult = bool
InstallResult = bool
UninstallResult = bool
StartResult = bool

# 回调函数类型
DeviceCallback = Callable[[str], Any]
TaskCallback = Callable[[str, ...], Any]

# 配置类型
ConfigDict = Dict[str, Any]
TimeoutConfig = Dict[str, int]
WDAConfig = Dict[str, Union[int, float, str]]
ConcurrentConfig = Dict[str, Union[int, str]]
LoggingConfig = Dict[str, Optional[str]]
PathsConfig = Dict[str, str]

# 设备操作结果
DeviceOperationResult = Union[bool, Dict[str, Any], List[Any], str, None]
