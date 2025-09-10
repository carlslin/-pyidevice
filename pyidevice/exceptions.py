"""自定义异常类模块"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PyIDeviceError(Exception):
    """pyidevice基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

        # 记录错误日志
        logger.error(f"PyIDeviceError: {message} (Code: {error_code})")
        if details:
            logger.error(f"Error details: {details}")


class DeviceError(PyIDeviceError):
    """设备操作异常基类"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        """
        初始化设备异常

        Args:
            message: 错误消息
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, **kwargs)
        self.udid = udid
        if udid:
            self.details["udid"] = udid


class DeviceConnectionError(DeviceError):
    """设备连接异常"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        super().__init__(message, udid, error_code="DEVICE_CONNECTION_ERROR", **kwargs)


class DeviceCommandError(DeviceError):
    """设备命令执行异常"""

    def __init__(
        self, message: str, command: Optional[str] = None, udid: Optional[str] = None, **kwargs
    ):
        """
        初始化设备命令异常

        Args:
            message: 错误消息
            command: 执行的命令
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="DEVICE_COMMAND_ERROR", **kwargs)
        self.command = command
        if command:
            self.details["command"] = command


class DeviceNotFoundError(DeviceError):
    """设备未找到异常"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        super().__init__(message, udid, error_code="DEVICE_NOT_FOUND", **kwargs)


class DeviceTimeoutError(DeviceError):
    """设备操作超时异常"""

    def __init__(
        self, message: str, timeout: Optional[float] = None, udid: Optional[str] = None, **kwargs
    ):
        """
        初始化设备超时异常

        Args:
            message: 错误消息
            timeout: 超时时间（秒）
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="DEVICE_TIMEOUT", **kwargs)
        self.timeout = timeout
        if timeout:
            self.details["timeout"] = timeout


class DevicePermissionError(DeviceError):
    """设备权限异常"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        super().__init__(message, udid, error_code="DEVICE_PERMISSION_ERROR", **kwargs)


class AppError(PyIDeviceError):
    """应用操作异常基类"""

    def __init__(self, message: str, bundle_id: Optional[str] = None, **kwargs):
        """
        初始化应用异常

        Args:
            message: 错误消息
            bundle_id: 应用包ID
            **kwargs: 其他参数
        """
        super().__init__(message, **kwargs)
        self.bundle_id = bundle_id
        if bundle_id:
            self.details["bundle_id"] = bundle_id


class AppInstallError(AppError):
    """应用安装异常"""

    def __init__(
        self,
        message: str,
        bundle_id: Optional[str] = None,
        ipa_path: Optional[str] = None,
        **kwargs,
    ):
        """
        初始化应用安装异常

        Args:
            message: 错误消息
            bundle_id: 应用包ID
            ipa_path: IPA文件路径
            **kwargs: 其他参数
        """
        super().__init__(message, bundle_id, error_code="APP_INSTALL_ERROR", **kwargs)
        self.ipa_path = ipa_path
        if ipa_path:
            self.details["ipa_path"] = ipa_path


class AppUninstallError(AppError):
    """应用卸载异常"""

    def __init__(self, message: str, bundle_id: Optional[str] = None, **kwargs):
        super().__init__(message, bundle_id, error_code="APP_UNINSTALL_ERROR", **kwargs)


class AppLaunchError(AppError):
    """应用启动异常"""

    def __init__(self, message: str, bundle_id: Optional[str] = None, **kwargs):
        super().__init__(message, bundle_id, error_code="APP_LAUNCH_ERROR", **kwargs)


class WDAError(PyIDeviceError):
    """WebDriverAgent异常基类"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        """
        初始化WDA异常

        Args:
            message: 错误消息
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, **kwargs)
        self.udid = udid
        if udid:
            self.details["udid"] = udid


class WDAConnectionError(WDAError):
    """WDA连接异常"""

    def __init__(
        self, message: str, udid: Optional[str] = None, url: Optional[str] = None, **kwargs
    ):
        """
        初始化WDA连接异常

        Args:
            message: 错误消息
            udid: 设备UDID
            url: WDA服务URL
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="WDA_CONNECTION_ERROR", **kwargs)
        self.url = url
        if url:
            self.details["url"] = url


class WDAElementError(WDAError):
    """WDA元素操作异常"""

    def __init__(
        self,
        message: str,
        element_info: Optional[Dict[str, Any]] = None,
        udid: Optional[str] = None,
        **kwargs,
    ):
        """
        初始化WDA元素异常

        Args:
            message: 错误消息
            element_info: 元素信息
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="WDA_ELEMENT_ERROR", **kwargs)
        self.element_info = element_info
        if element_info:
            self.details["element_info"] = element_info


class WDAOperationError(WDAError):
    """WDA操作异常"""

    def __init__(
        self, message: str, operation: Optional[str] = None, udid: Optional[str] = None, **kwargs
    ):
        """
        初始化WDA操作异常

        Args:
            message: 错误消息
            operation: 操作类型
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="WDA_OPERATION_ERROR", **kwargs)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class IDBError(PyIDeviceError):
    """IDB异常基类"""

    def __init__(self, message: str, udid: Optional[str] = None, **kwargs):
        """
        初始化IDB异常

        Args:
            message: 错误消息
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, **kwargs)
        self.udid = udid
        if udid:
            self.details["udid"] = udid


class IDBConnectionError(IDBError):
    """IDB连接异常"""

    def __init__(
        self, message: str, udid: Optional[str] = None, host: Optional[str] = None, 
        port: Optional[int] = None, **kwargs
    ):
        """
        初始化IDB连接异常

        Args:
            message: 错误消息
            udid: 设备UDID
            host: IDB服务主机
            port: IDB服务端口
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="IDB_CONNECTION_ERROR", **kwargs)
        self.host = host
        self.port = port
        if host:
            self.details["host"] = host
        if port:
            self.details["port"] = port


class IDBElementError(IDBError):
    """IDB元素操作异常"""

    def __init__(
        self,
        message: str,
        element_info: Optional[Dict[str, Any]] = None,
        udid: Optional[str] = None,
        **kwargs,
    ):
        """
        初始化IDB元素异常

        Args:
            message: 错误消息
            element_info: 元素信息
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="IDB_ELEMENT_ERROR", **kwargs)
        self.element_info = element_info
        if element_info:
            self.details["element_info"] = element_info


class IDBOperationError(IDBError):
    """IDB操作异常"""

    def __init__(
        self, message: str, operation: Optional[str] = None, udid: Optional[str] = None, **kwargs
    ):
        """
        初始化IDB操作异常

        Args:
            message: 错误消息
            operation: 操作类型
            udid: 设备UDID
            **kwargs: 其他参数
        """
        super().__init__(message, udid, error_code="IDB_OPERATION_ERROR", **kwargs)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class ConfigurationError(PyIDeviceError):
    """配置异常"""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        初始化配置异常

        Args:
            message: 错误消息
            config_key: 配置键
            **kwargs: 其他参数
        """
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class EnvironmentError(PyIDeviceError):
    """环境异常"""

    def __init__(self, message: str, missing_tools: Optional[list] = None, **kwargs):
        """
        初始化环境异常

        Args:
            message: 错误消息
            missing_tools: 缺失的工具列表
            **kwargs: 其他参数
        """
        super().__init__(message, error_code="ENVIRONMENT_ERROR", **kwargs)
        self.missing_tools = missing_tools or []
        if missing_tools:
            self.details["missing_tools"] = missing_tools


class CacheError(PyIDeviceError):
    """缓存异常"""

    def __init__(self, message: str, cache_key: Optional[str] = None, **kwargs):
        """
        初始化缓存异常

        Args:
            message: 错误消息
            cache_key: 缓存键
            **kwargs: 其他参数
        """
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)
        self.cache_key = cache_key
        if cache_key:
            self.details["cache_key"] = cache_key


class PerformanceError(PyIDeviceError):
    """性能异常"""

    def __init__(
        self, message: str, metric: Optional[str] = None, value: Optional[float] = None, **kwargs
    ):
        """
        初始化性能异常

        Args:
            message: 错误消息
            metric: 性能指标
            value: 指标值
            **kwargs: 其他参数
        """
        super().__init__(message, error_code="PERFORMANCE_ERROR", **kwargs)
        self.metric = metric
        self.value = value
        if metric:
            self.details["metric"] = metric
        if value is not None:
            self.details["value"] = value


def handle_exception(func):
    """异常处理装饰器"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PyIDeviceError:
            # 重新抛出已知异常
            raise
        except Exception as e:
            # 包装未知异常
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise PyIDeviceError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={"original_error": str(e), "function": func.__name__},
            ) from e

    # 保留原函数的文档字符串和属性
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__module__ = func.__module__
    wrapper.__annotations__ = func.__annotations__

    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (DeviceError,)):
    """重试装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s..."
                        )
                        import time

                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
                        raise e

            # 这行代码理论上不会执行到
            raise last_exception

        # 保留原函数的文档字符串和属性
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        wrapper.__module__ = func.__module__
        wrapper.__annotations__ = func.__annotations__

        return wrapper

    return decorator
