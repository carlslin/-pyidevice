"""pyidevice - A comprehensive iOS device automation library based on libimobiledevice

This library provides a Python interface for managing and automating iOS devices
using libimobiledevice tools. It supports device management, UI automation,
and concurrent operations across multiple devices.

Key Features:
- Device management (connection, info, app installation/uninstallation)
- UI automation based on IDB (iOS Device Bridge)
- Concurrent operations for multiple devices
- Command-line interface
- Comprehensive error handling and logging

Example:
    >>> from pyidevice import DeviceManager, Device
    >>> devices = DeviceManager.get_devices()
    >>> device = Device(devices[0])
    >>> info = device.info()
    >>> print(f"Device: {device.name()}")
"""

__version__ = "0.1.0"
__author__ = "pyidevice contributors"
__email__ = "pyidevice@example.com"
__license__ = "MIT"

# 核心模块导入
from .core import DeviceManager
from .exceptions import (
    DeviceError,
    DeviceConnectionError,
    DeviceCommandError,
    DeviceNotFoundError,
    DeviceTimeoutError,
    DevicePermissionError,
    AppError,
    AppInstallError,
    AppUninstallError,
    AppLaunchError,
    WDAError,
    WDAConnectionError,
    WDAElementError,
    WDAOperationError,
    IDBError,
    IDBConnectionError,
    IDBElementError,
    IDBOperationError,
    ConfigurationError,
    EnvironmentError,
    CacheError,
    PerformanceError,
    PyIDeviceError,
)
from .device import Device
from .idb import IDBAutomator, IDBWebViewAgent
from .parallel import ParallelDeviceExecutor, ConcurrentDeviceManager, parallel_run
from .config import Config, get_config
from .utils import EnvironmentChecker, format_bytes, safe_filename, retry_on_failure
from .performance import (
    PerformanceMonitor,
    performance_tracker,
    monitor_performance,
    optimize_memory_usage,
)
from .cache import CacheManager, cache_manager, cached, DeviceCache, device_cache
from .types import DeviceStatus, ExecutorType, LogLevel
from .monitor import DeviceMonitor, AlertManager, device_monitor, alert_manager
from .batch import BatchOperator, BatchAppManager, BatchDeviceManager, BatchReportGenerator

# 定义公共API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # 核心类
    "DeviceManager",
    "Device",
    "IDBAutomator",
    "IDBWebViewAgent",
    # 并发功能
    "ParallelDeviceExecutor",
    "ConcurrentDeviceManager",
    "parallel_run",
    # 配置管理
    "Config",
    "get_config",
    # 工具函数
    "EnvironmentChecker",
    "format_bytes",
    "safe_filename",
    "retry_on_failure",
    # 性能监控
    "PerformanceMonitor",
    "performance_tracker",
    "monitor_performance",
    "optimize_memory_usage",
    # 缓存管理
    "CacheManager",
    "cache_manager",
    "cached",
    "DeviceCache",
    "device_cache",
    # 类型定义
    "DeviceStatus",
    "ExecutorType",
    "LogLevel",
    # 监控功能
    "DeviceMonitor",
    "AlertManager",
    "device_monitor",
    "alert_manager",
    # 批量操作
    "BatchOperator",
    "BatchAppManager",
    "BatchDeviceManager",
    "BatchReportGenerator",
    # 异常类
    "PyIDeviceError",
    "DeviceError",
    "DeviceConnectionError",
    "DeviceCommandError",
    "DeviceNotFoundError",
    "DeviceTimeoutError",
    "DevicePermissionError",
    "AppError",
    "AppInstallError",
    "AppUninstallError",
    "AppLaunchError",
    "WDAError",
    "WDAConnectionError",
    "WDAElementError",
    "WDAOperationError",
    "IDBError",
    "IDBConnectionError",
    "IDBElementError",
    "IDBOperationError",
    "ConfigurationError",
    "EnvironmentError",
    "CacheError",
    "PerformanceError",
]


# 环境检查
def check_environment():
    """检查运行环境是否满足要求"""
    is_valid, errors = EnvironmentChecker.validate_environment()
    if not is_valid:
        import warnings

        warning_msg = "Environment validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        warnings.warn(warning_msg, UserWarning)
    return is_valid, errors


# 自动检查环境（可选）
try:
    check_environment()
except Exception:
    # 如果环境检查失败，不影响库的导入
    pass
