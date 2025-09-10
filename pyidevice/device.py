"""
pyidevice 设备模块

这个模块提供了Device类，用于对单个iOS设备进行各种操作。

主要功能：
- 设备信息获取（名称、型号、版本、电池等）
- 应用管理（安装、卸载、启动、列表）
- 屏幕截图
- 设备控制（重启、关机）
- 智能缓存和性能监控

主要类：
- Device: 设备操作类，提供单个设备的所有操作接口

依赖：
- libimobiledevice工具套件
- 缓存系统（device_cache）
- 性能监控（monitor_performance）

使用示例：
    >>> from pyidevice import Device
    >>> device = Device("00008020-0012345678901234")
    >>> print(f"设备名称: {device.name()}")
    >>> print(f"iOS版本: {device.version()}")
    >>> print(f"电池电量: {device.battery_level()}%")
    >>> device.take_screenshot("/tmp/screenshot.png")
"""

import subprocess
import time
import os
import logging
from typing import Dict, Union
from .cache import device_cache
from .performance import monitor_performance
from .stability import (
    get_retry_manager,
    get_timeout_manager,
    get_input_validator,
    with_retry,
    with_timeout,
    validate_input,
)

# 配置日志记录器
logger = logging.getLogger(__name__)


class Device:
    """
    iOS设备操作类

    这个类提供了对单个iOS设备进行各种操作的接口，包括：
    1. 设备信息获取（名称、型号、版本、电池等）
    2. 应用管理（安装、卸载、启动、列表）
    3. 屏幕截图
    4. 设备控制（重启、关机）
    5. 智能缓存和性能监控

    特性：
    - 自动缓存设备信息，提高性能
    - 性能监控，跟踪操作耗时
    - 完善的错误处理和日志记录
    - 支持强制刷新缓存

    注意事项：
    - 需要先安装libimobiledevice工具套件
    - 设备必须信任计算机
    - 某些操作可能需要设备解锁
    - 应用安装需要有效的IPA文件
    """

    def __init__(self, udid: str):
        """
        初始化设备对象

        创建一个新的Device实例，用于对指定UDID的iOS设备进行操作。
        UDID是设备的唯一标识符，用于区分不同的iOS设备。

        Args:
            udid (str): 设备的唯一标识符（40位十六进制字符串）
                       例如："00008020-0012345678901234"

        Attributes:
            udid (str): 设备的唯一标识符
            _info_cache (dict): 本地缓存（已弃用，现在使用全局缓存系统）
            _last_info_update (float): 最后更新时间戳，用于缓存失效判断

        Example:
            >>> device = Device("00008020-0012345678901234")
            >>> print(f"设备UDID: {device.udid}")
            
        Note:
            - UDID必须是有效的40位十六进制字符串
            - 设备必须已连接并信任计算机
            - 初始化不会验证设备是否真的存在，实际验证在调用方法时进行
        """
        # 验证UDID格式
        validator = get_input_validator()
        if not validator.validate_udid(udid):
            raise ValueError(f"无效的UDID格式: {udid}")
        
        self.udid = udid  # 设备唯一标识符，用于所有后续操作
        self._info_cache = None  # 本地缓存（已弃用，使用全局缓存）
        self._last_info_update = 0  # 最后更新时间戳，用于缓存失效判断

    @monitor_performance
    def info(self, refresh: bool = False) -> Dict[str, Union[str, int, float, bool]]:
        """
        获取设备信息，支持智能缓存

        这个方法获取设备的详细信息，包括名称、型号、版本、电池等。
        使用智能缓存机制，避免重复获取相同信息，提高性能。

        Args:
            refresh (bool, optional): 是否强制刷新缓存。默认为False。

        Returns:
            Dict[str, str]: 包含设备信息的字典，可能包含以下键：
                - DeviceName: 设备名称
                - ProductType: 产品型号
                - ProductVersion: iOS版本
                - BatteryLevel: 电池电量
                - 其他设备属性...

        Example:
            >>> device = Device("00008020-0012345678901234")
            >>> info = device.info()
            >>> print(f"设备名称: {info.get('DeviceName')}")
            >>>
            >>> # 强制刷新缓存
            >>> fresh_info = device.info(refresh=True)

        Note:
            - 首次调用会从设备获取信息并缓存
            - 后续调用会从缓存返回，提高性能
            - 使用refresh=True可以强制刷新缓存
        """
        if refresh:
            # 强制刷新，清除缓存
            device_cache.invalidate_device(self.udid)

        # 尝试从全局缓存获取
        cached_info = device_cache.get_device_info(self.udid)
        if cached_info is not None:
            return cached_info

        # 获取新信息并缓存
        from .core import DeviceManager

        info = DeviceManager.get_device_info(self.udid)
        device_cache.set_device_info(self.udid, info)
        return info

    def name(self) -> str:
        """获取设备名称"""
        info = self.info()
        return info.get("DeviceName", "Unknown Device")

    def model(self) -> str:
        """获取设备型号"""
        info = self.info()
        return info.get("ProductType", "Unknown Model")

    def version(self) -> str:
        """获取iOS版本"""
        info = self.info()
        return info.get("ProductVersion", "Unknown Version")

    def battery_level(self) -> int:
        """获取电池电量百分比"""
        info = self.info()
        battery_str = info.get("BatteryLevel", "-1")
        try:
            return int(battery_str)
        except (ValueError, TypeError):
            return -1

    def get_battery_info(self) -> dict:
        """获取电池详细信息"""
        info = self.info()
        battery_str = info.get("BatteryLevel", "-1")
        try:
            level = int(battery_str)
        except (ValueError, TypeError):
            level = -1

        charging_str = info.get("BatteryCharging", "false")
        charging = charging_str.lower() in ("true", "1", "yes")

        temp_str = info.get("BatteryTemperature", None)
        temperature = None
        if temp_str:
            try:
                temperature = float(temp_str)
            except (ValueError, TypeError):
                temperature = None

        return {"level": level, "charging": charging, "temperature": temperature}

    def install_app(self, ipa_path: str) -> bool:
        """安装IPA应用"""
        if not os.path.exists(ipa_path):
            print(f"IPA file not found: {ipa_path}")
            return False

        try:
            subprocess.check_output(
                ["ideviceinstaller", "-u", self.udid, "-i", ipa_path],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install app: {e.output}")
            return False

    def uninstall_app(self, bundle_id: str) -> bool:
        """卸载应用"""
        try:
            subprocess.check_output(
                ["ideviceinstaller", "-u", self.udid, "-U", bundle_id],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall app: {e.output}")
            return False

    def list_apps(self) -> list:
        """列出已安装的应用"""
        apps = []
        try:
            result = subprocess.check_output(
                ["ideviceinstaller", "-u", self.udid, "-l"], universal_newlines=True
            )

            # 解析应用列表
            for line in result.split("\n"):
                if " - " in line:
                    parts = line.strip().split(" - ", 1)
                    if len(parts) == 2:
                        apps.append({"bundle_id": parts[0], "name": parts[1]})
        except subprocess.CalledProcessError:
            pass

        return apps

    def list_installed_apps(self) -> list:
        """列出已安装的应用（别名方法）"""
        return self.list_apps()

    def take_screenshot(self, output_path: str) -> bool:
        """截取屏幕截图"""
        try:
            subprocess.check_output(
                ["idevicescreenshot", "-u", self.udid, output_path],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to take screenshot: {e.output}")
            return False

    def start_app(self, bundle_id: str) -> bool:
        """启动应用

        优化说明：改进了应用启动的判断逻辑，不再依赖于特定字符串，
        而是使用subprocess.Popen并设置超时，更加健壮和可靠。
        """
        try:
            # 使用Popen而不是check_output，因为idevicedebug会持续运行
            process = subprocess.Popen(
                ["idevicedebug", "-u", self.udid, "run", bundle_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            # 设置一个超时时间，检查前几行输出
            timeout = 5  # 5秒超时
            start_time = time.time()

            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if not line:
                    break

                # 检查是否有成功启动的迹象
                if any(
                    phrase in line
                    for phrase in [
                        "Waiting for app to launch",
                        "Attaching to process",
                        "Launching",  # 增加更多可能的成功标识
                    ]
                ):
                    # 应用已经开始启动，此时可以终止进程
                    process.terminate()
                    return True

            # 如果超时，终止进程
            process.terminate()

            # 检查应用是否在运行（作为后备检查）
            time.sleep(2)  # 给应用一些时间启动
            try:
                running_apps = subprocess.check_output(
                    ["idevicesyslog", "-u", self.udid, "-c", "10"], universal_newlines=True
                )
                return bundle_id in running_apps
            except Exception:
                # 如果无法检查，返回默认的判断结果
                return False
        except Exception as e:
            print(f"Failed to start app: {str(e)}")
            return False

    def reboot(self) -> bool:
        """重启设备"""
        try:
            subprocess.check_output(
                ["idevicediagnostics", "-u", self.udid, "restart"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to reboot device: {e.output}")
            return False

    def shutdown(self) -> bool:
        """关机"""
        try:
            subprocess.check_output(
                ["idevicediagnostics", "-u", self.udid, "shutdown"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to shutdown device: {e.output}")
            return False
