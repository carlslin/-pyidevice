"""
pyidevice 工具函数模块

这个模块提供了各种实用工具函数和类，用于环境检查、文件处理、格式化等。

主要功能：
- 环境检查和验证
- 文件路径处理
- 数据格式化
- 重试机制
- 系统信息获取

主要类：
- EnvironmentChecker: 环境检查器
- 各种工具函数

使用示例：
    >>> from pyidevice import EnvironmentChecker, format_bytes, safe_filename
    >>> is_valid, errors = EnvironmentChecker.validate_environment()
    >>> print(f"环境检查: {is_valid}")
    >>> size_str = format_bytes(1024 * 1024)  # "1.0 MB"
    >>> safe_name = safe_filename("My Device")  # "My_Device"
"""

import subprocess
import shutil
import platform
import logging
import re
import time
from typing import List, Dict, Optional, Tuple, Callable, Any
from pathlib import Path
from functools import wraps

# 配置日志记录器
logger = logging.getLogger(__name__)


class EnvironmentChecker:
    """
    环境检查器

    这个类提供了检查pyidevice运行环境的功能，包括：
    1. 系统兼容性检查
    2. libimobiledevice工具检查
    3. Python版本检查
    4. 必需工具检查
    5. 可选工具检查

    用途：
    - 安装前环境验证
    - 运行时环境检查
    - 故障排除和诊断
    - 环境配置指导
    """

    # 必需的libimobiledevice工具
    REQUIRED_TOOLS = [
        "idevice_id",
        "ideviceinfo",
        "ideviceinstaller",
        "idevicescreenshot",
        "idevicedebug",
        "idevicediagnostics",
        "idevicename",
        "iproxy",
    ]

    # 可选的工具
    OPTIONAL_TOOLS = ["idevicesyslog"]

    @classmethod
    def check_system_requirements(cls) -> Dict[str, bool]:
        """
        检查系统要求

        Returns:
            Dict[str, bool]: 检查结果字典
        """
        results = {
            "system_supported": cls._check_system_support(),
            "libimobiledevice_installed": cls._check_libimobiledevice(),
            "python_version_ok": cls._check_python_version(),
            "required_tools": cls._check_required_tools(),
            "optional_tools": cls._check_optional_tools(),
        }

        return results

    @classmethod
    def _check_system_support(cls) -> bool:
        """检查系统是否支持"""
        system = platform.system().lower()
        return system in ["darwin", "linux"]

    @classmethod
    def _check_python_version(cls) -> bool:
        """检查Python版本"""
        import sys

        return sys.version_info >= (3, 6)

    @classmethod
    def _check_libimobiledevice(cls) -> bool:
        """检查libimobiledevice是否安装"""
        try:
            result = subprocess.run(
                ["idevice_id", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @classmethod
    def _check_required_tools(cls) -> Dict[str, bool]:
        """检查必需工具是否可用"""
        results = {}
        for tool in cls.REQUIRED_TOOLS:
            results[tool] = shutil.which(tool) is not None
        return results

    @classmethod
    def _check_optional_tools(cls) -> Dict[str, bool]:
        """检查可选工具是否可用"""
        results = {}
        for tool in cls.OPTIONAL_TOOLS:
            results[tool] = shutil.which(tool) is not None
        return results

    @classmethod
    def get_installation_instructions(cls) -> str:
        """获取安装说明"""
        system = platform.system().lower()

        if system == "darwin":
            return """
macOS 安装说明:
1. 安装 Homebrew (如果尚未安装):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. 安装 libimobiledevice:
   brew install libimobiledevice

3. 安装 ideviceinstaller:
   brew install ideviceinstaller
"""
        elif system == "linux":
            return """
Linux 安装说明:
Ubuntu/Debian:
   sudo apt-get update
   sudo apt-get install libimobiledevice-utils ideviceinstaller

CentOS/RHEL/Fedora:
   sudo yum install libimobiledevice-utils ideviceinstaller
   # 或者使用 dnf (较新版本):
   sudo dnf install libimobiledevice-utils ideviceinstaller
"""
        else:
            return f"不支持的操作系统: {system}"

    @classmethod
    def validate_environment(cls) -> Tuple[bool, List[str]]:
        """
        验证环境是否满足要求

        Returns:
            Tuple[bool, List[str]]: (是否满足要求, 错误信息列表)
        """
        results = cls.check_system_requirements()
        errors = []

        if not results["system_supported"]:
            errors.append("不支持的操作系统")

        if not results["python_version_ok"]:
            errors.append("Python版本需要3.6或更高")

        if not results["libimobiledevice_installed"]:
            errors.append("libimobiledevice未安装或不可用")

        # 检查必需工具
        missing_tools = [
            tool for tool, available in results["required_tools"].items() if not available
        ]
        if missing_tools:
            errors.append(f"缺少必需工具: {', '.join(missing_tools)}")

        return len(errors) == 0, errors


def format_bytes(bytes_value: int) -> str:
    """格式化字节数为可读格式"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    import re

    # 移除或替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # 限制长度
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name


def ensure_directory(path: str) -> bool:
    """确保目录存在"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
    """

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
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                        )
                        import time

                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")

            raise last_exception

        return wrapper

    return decorator


def get_device_udid_from_name(device_name: str) -> Optional[str]:
    """
    根据设备名称获取UDID

    Args:
        device_name: 设备名称

    Returns:
        设备UDID，如果未找到则返回None
    """
    try:
        from .core import DeviceManager

        devices = DeviceManager.get_devices()

        for udid in devices:
            try:
                result = subprocess.check_output(
                    ["idevicename", "-u", udid], universal_newlines=True, timeout=5
                )
                if result.strip() == device_name:
                    return udid
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue

        return None
    except Exception as e:
        logger.error(f"Failed to get device UDID from name {device_name}: {e}")
        return None


def validate_udid(udid: str) -> bool:
    """
    验证UDID格式是否正确

    Args:
        udid: 设备UDID

    Returns:
        是否为有效的UDID格式
    """
    import re

    # UDID通常是40个字符的十六进制字符串
    pattern = r"^[0-9A-Fa-f]{40}$"
    return bool(re.match(pattern, udid))


def get_available_ports(start_port: int = 8100, count: int = 10) -> List[int]:
    """
    获取可用的端口列表

    Args:
        start_port: 起始端口
        count: 需要检查的端口数量

    Returns:
        可用端口列表
    """
    import socket

    available_ports = []

    for port in range(start_port, start_port + count):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                available_ports.append(port)
        except OSError:
            # 端口被占用
            continue

    return available_ports
