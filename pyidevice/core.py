"""
pyidevice 核心模块

这个模块提供了iOS设备管理的核心功能，包括：
- 设备发现和连接管理
- 设备信息获取
- 设备状态检查

主要类：
- DeviceManager: 设备管理器，提供静态方法进行设备操作

依赖：
- libimobiledevice工具套件 (idevice_id, ideviceinfo, idevicediagnostics等)
- subprocess: 用于执行系统命令
- logging: 用于日志记录

使用示例：
    >>> from pyidevice.core import DeviceManager
    >>> devices = DeviceManager.get_devices()
    >>> print(f"找到 {len(devices)} 个设备")
    >>> if devices:
    ...     info = DeviceManager.get_device_info(devices[0])
    ...     print(f"设备名称: {info.get('DeviceName', 'Unknown')}")
"""

import subprocess
import re
import logging
from typing import List, Optional, Dict, Union
from .exceptions import (
    DeviceCommandError,
    DeviceTimeoutError,
    handle_exception,
    retry_on_failure,
)

# 配置日志记录器
logger = logging.getLogger(__name__)


class DeviceManager:
    """
    iOS设备管理器

    这个类提供了管理iOS设备的核心功能，包括设备发现、信息获取和状态检查。
    所有方法都是静态方法，可以直接通过类名调用。

    主要功能：
    1. 获取已连接的设备列表
    2. 获取设备详细信息
    3. 检查设备连接状态
    4. 获取第一个可用设备

    注意事项：
    - 需要先安装libimobiledevice工具套件
    - 设备需要信任计算机才能获取信息
    - 某些操作可能需要设备解锁

    异常处理：
    - 使用装饰器自动处理异常和重试
    - 提供详细的错误信息和日志记录
    """

    @staticmethod
    @handle_exception
    @retry_on_failure(max_retries=2, delay=0.5)
    def get_devices() -> List[str]:
        """
        获取所有已连接的iOS设备UDID列表

        这个方法通过执行idevice_id命令来获取当前连接的iOS设备列表。
        使用装饰器提供异常处理和自动重试功能。

        Returns:
            List[str]: 设备UDID列表，每个UDID是一个40位的十六进制字符串

        Raises:
            DeviceCommandError: 当无法执行idevice_id命令时
            DeviceTimeoutError: 当命令执行超时时

        Example:
            >>> devices = DeviceManager.get_devices()
            >>> print(f"找到 {len(devices)} 个设备")
            >>> for device in devices:
            ...     print(f"设备UDID: {device}")

        Note:
            - 需要安装libimobiledevice工具套件
            - 设备必须通过USB连接并信任计算机
            - 返回的UDID列表可能为空（没有设备连接时）
        """
        try:
            # 执行idevice_id命令获取设备列表
            # idevice_id是libimobiledevice工具套件的一部分，用于获取设备标识符
            # -l 参数表示列出所有连接的设备
            result = subprocess.check_output(
                ["idevice_id", "-l"],
                universal_newlines=True,  # 以文本模式返回结果，便于处理
                stderr=subprocess.PIPE,  # 捕获错误输出，用于调试
                timeout=10,  # 设置10秒超时，避免命令卡死
            )

            # 解析命令输出，每行一个UDID
            # idevice_id命令的输出格式：每行一个40位的十六进制UDID
            devices = result.strip().split("\n")
            # 过滤掉空行，确保返回的都是有效的UDID
            valid_devices = [d for d in devices if d.strip()]
            
            logger.info(f"发现 {len(valid_devices)} 个已连接的iOS设备")
            return valid_devices

        except subprocess.CalledProcessError as e:
            # 命令执行失败（非零退出码）
            error_msg = f"Failed to get devices: {e}"
            if e.stderr:
                error_msg += f" Error details: {e.stderr}"
            logger.error(error_msg)
            raise DeviceCommandError(
                error_msg,
                error_code="DEVICE_LIST_FAILED",
                details={"exit_code": e.returncode, "stderr": e.stderr},
            ) from e

        except subprocess.TimeoutExpired as e:
            # 命令执行超时
            error_msg = "Timeout while getting device list"
            logger.error(error_msg)
            raise DeviceTimeoutError(
                error_msg, error_code="DEVICE_LIST_TIMEOUT", details={"timeout": e.timeout}
            ) from e

        except FileNotFoundError:
            # idevice_id命令不存在
            error_msg = "idevice_id command not found. Please install libimobiledevice"
            logger.error(error_msg)
            raise DeviceCommandError(
                error_msg, error_code="COMMAND_NOT_FOUND", details={"command": "idevice_id"}
            )

    @staticmethod
    @handle_exception
    def get_device_info(udid: str) -> Dict[str, Union[str, int, float, bool]]:
        """
        获取指定设备的详细信息

        这个方法通过执行多个libimobiledevice命令来获取设备的完整信息，
        包括基本设备信息、电池状态和设备名称。

        Args:
            udid (str): 设备的唯一标识符（40位十六进制字符串）

        Returns:
            Dict[str, Any]: 包含设备信息的字典，可能包含以下键：
                - DeviceName: 设备名称
                - ProductType: 产品型号（如iPhone12,1）
                - ProductVersion: iOS版本
                - BatteryLevel: 电池电量百分比
                - 其他设备属性...

        Raises:
            DeviceCommandError: 当无法获取设备信息时
            DeviceNotFoundError: 当指定的设备不存在时

        Example:
            >>> info = DeviceManager.get_device_info("00008020-0012345678901234")
            >>> print(f"设备名称: {info.get('DeviceName', 'Unknown')}")
            >>> print(f"iOS版本: {info.get('ProductVersion', 'Unknown')}")
            >>> print(f"电池电量: {info.get('BatteryLevel', 'Unknown')}%")

        Note:
            - 设备必须已连接并信任计算机
            - 某些信息可能需要设备解锁才能获取
            - 电池信息获取可能失败，但不影响其他信息的获取
        """
        info = {}
        try:
            # 获取基本设备信息
            # ideviceinfo命令可以获取设备的各种属性
            result = subprocess.check_output(["ideviceinfo", "-u", udid], universal_newlines=True)

            # 解析输出结果，格式为 key=value
            for line in result.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    info[key.strip()] = value.strip()

            # 获取电池信息（可选，可能失败）
            try:
                # idevicediagnostics命令可以获取诊断信息，包括电池状态
                battery_result = subprocess.check_output(
                    ["idevicediagnostics", "-u", udid, "battery"], universal_newlines=True
                )
                # 使用正则表达式提取电池电量
                battery_match = re.search(r"BatteryCurrentCapacity: (\d+)", battery_result)
                if battery_match:
                    info["BatteryLevel"] = int(battery_match.group(1))
            except Exception as e:
                # 电池信息获取失败不影响主要功能
                logger.warning(f"Failed to get battery info for device {udid}: {e}")

            # 获取设备名称（备用方法）
            try:
                # 如果ideviceinfo没有返回设备名称，尝试使用idevicename命令
                if "DeviceName" not in info:
                    name_result = subprocess.check_output(
                        ["idevicename", "-u", udid], universal_newlines=True
                    )
                    info["DeviceName"] = name_result.strip()
            except Exception as e:
                logger.warning(f"Failed to get device name for {udid}: {e}")

        except subprocess.CalledProcessError as e:
            # 记录错误但不抛出异常，让装饰器处理
            logger.error(f"Failed to get device info for {udid}: {e}")

        return info

    @staticmethod
    def is_device_connected(udid: str) -> bool:
        """
        检查指定UDID的设备是否已连接

        Args:
            udid (str): 要检查的设备UDID

        Returns:
            bool: 如果设备已连接返回True，否则返回False

        Example:
            >>> is_connected = DeviceManager.is_device_connected("00008020-0012345678901234")
            >>> print(f"设备连接状态: {is_connected}")
        """
        devices = DeviceManager.get_devices()
        return udid in devices

    @staticmethod
    def get_first_device() -> Optional[str]:
        """
        获取第一个连接的设备UDID

        这个方法返回当前连接的设备列表中的第一个设备UDID。
        如果没有设备连接，返回None。

        Returns:
            Optional[str]: 第一个设备的UDID，如果没有设备连接则返回None

        Example:
            >>> first_device = DeviceManager.get_first_device()
            >>> if first_device:
            ...     print(f"第一个设备: {first_device}")
            ... else:
            ...     print("没有连接的设备")
        """
        devices = DeviceManager.get_devices()
        return devices[0] if devices else None
