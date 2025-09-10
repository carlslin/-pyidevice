"""
pyidevice IDB模块

这个模块提供了基于IDB (iOS Device Bridge) 的iOS UI自动化功能。

主要功能：
- 设备连接和会话管理
- 元素查找和操作
- 手势操作（点击、滑动、输入等）
- 应用状态管理
- 屏幕截图和元素截图
- 文件操作和网络监控
- 性能监控和日志记录

主要类：
- IDBAutomator: UI自动化控制器
- IDBWebViewAgent: WebView自动化代理

依赖：
- idb: IDB的Python客户端
- idb-companion: 需要在设备上运行的IDB服务

使用示例：
    >>> from pyidevice import IDBAutomator
    >>> idb = IDBAutomator("00008020-0012345678901234")
    >>> idb.connect()
    >>> element = idb.find_element("Button", label="登录")
    >>> element.click()
"""

import time
import logging
from typing import Optional, Dict, List, Any, Union, Tuple
import os
import re
import subprocess
import threading

# 配置日志记录器
logger = logging.getLogger(__name__)

# 尝试导入IDB，如果失败则提供友好的错误信息
try:
    import idb
    IDB_AVAILABLE = True
except ImportError:
    IDB_AVAILABLE = False
    logger.warning("IDB模块未安装，请运行: pip install idb")


class IDBError(Exception):
    """IDB相关错误"""
    pass


class IDBAutomator:
    """
    iOS设备UI自动化控制器

    这个类提供了基于IDB (iOS Device Bridge) 的iOS UI自动化功能。
    它封装了idb库，提供了更简洁的API接口。

    主要功能：
    1. 设备连接和会话管理
    2. 元素查找和操作
    3. 手势操作（点击、滑动、输入等）
    4. 应用状态管理
    5. 屏幕截图和元素截图
    6. 文件操作和网络监控
    7. 性能监控和日志记录

    特性：
    - 自动检测IDB Companion安装状态
    - 支持多种元素定位方式
    - 提供丰富的手势操作
    - 完善的错误处理和日志记录
    - 支持iOS 17+设备

    注意事项：
    - 需要先在设备上安装IDB Companion
    - 需要启动IDB Companion服务
    - 某些操作可能需要应用在前台运行
    """

    def __init__(self, udid: str, host: str = "localhost", port: int = 8080):
        """
        初始化IDB自动化控制器

        Args:
            udid: 设备UDID
            host: IDB Companion服务主机地址
            port: IDB Companion服务端口
        """
        if not IDB_AVAILABLE:
            raise IDBError("IDB模块未安装，请运行: pip install idb")
            
        self.udid = udid
        self.host = host
        self.port = port
        self.device = None
        self._is_connected = False
        self._companion_process = None

    def _ensure_idb_companion_installed(self) -> bool:
        """
        检查IDB Companion是否已安装

        Returns:
            bool: 如果已安装返回True，否则返回False
        """
        try:
            result = subprocess.run(
                ["idb_companion", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"IDB Companion已安装，版本: {result.stdout.strip()}")
                return True
            else:
                logger.error("IDB Companion未正确安装")
                return False
        except FileNotFoundError:
            logger.error("IDB Companion未安装，请运行: brew install idb-companion")
            return False
        except subprocess.TimeoutExpired:
            logger.error("IDB Companion响应超时")
            return False
        except Exception as e:
            logger.error(f"检查IDB Companion时出错: {e}")
            return False

    def _start_idb_companion(self) -> bool:
        """
        启动IDB Companion服务

        Returns:
            bool: 如果启动成功返回True，否则返回False
        """
        try:
            # 检查是否已有服务在运行
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True
            )
            if "idb_companion" in result.stdout:
                logger.info("IDB Companion服务已在运行")
                return True

            # 启动IDB Companion服务
            self._companion_process = subprocess.Popen(
                ["idb_companion", "--udid", self.udid],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            time.sleep(3)
            
            if self._companion_process.poll() is None:
                logger.info("IDB Companion服务启动成功")
                return True
            else:
                logger.error("IDB Companion服务启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动IDB Companion服务时出错: {e}")
            return False

    def connect(self, retry_count: int = 3, retry_interval: float = 2.0) -> bool:
        """
        连接到设备的IDB服务

        Args:
            retry_count: 重试次数
            retry_interval: 重试间隔（秒）

        Returns:
            bool: 连接成功返回True，否则返回False
        """
        if not self._ensure_idb_companion_installed():
            return False

        # 启动IDB Companion服务
        if not self._start_idb_companion():
            return False

        for i in range(retry_count):
            try:
                # 连接到IDB设备
                self.device = idb.Device(udid=self.udid, host=self.host, port=self.port)
                
                # 测试连接
                info = self.device.info()
                logger.info(f"成功连接到设备 {self.udid}")
                logger.info(f"设备信息: {info.get('name', 'Unknown')} - iOS {info.get('os_version', 'Unknown')}")
                
                self._is_connected = True
                return True
                
            except Exception as e:
                logger.warning(f"连接尝试 {i+1} 失败: {e}")
                if i < retry_count - 1:
                    time.sleep(retry_interval)

        logger.error(f"连接设备 {self.udid} 失败，已重试 {retry_count} 次")
        return False

    def disconnect(self) -> None:
        """断开连接并清理资源"""
        if self._companion_process and self._companion_process.poll() is None:
            self._companion_process.terminate()
            self._companion_process.wait(timeout=3.0)
            logger.info("IDB Companion服务已终止")

        self.device = None
        self._is_connected = False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._is_connected and self.device is not None

    def get_device_info(self) -> Dict[str, Any]:
        """
        获取设备信息

        Returns:
            Dict[str, Any]: 设备信息字典
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.info()
        except Exception as e:
            logger.error(f"获取设备信息失败: {e}")
            raise IDBError(f"获取设备信息失败: {e}")

    def app_start(self, bundle_id: str) -> bool:
        """
        启动应用

        Args:
            bundle_id: 应用包ID

        Returns:
            bool: 启动成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.app_launch(bundle_id)
            time.sleep(2)  # 等待应用启动
            logger.info(f"应用 {bundle_id} 启动成功")
            return True
        except Exception as e:
            logger.error(f"启动应用 {bundle_id} 失败: {e}")
            return False

    def app_stop(self, bundle_id: str) -> bool:
        """
        停止应用

        Args:
            bundle_id: 应用包ID

        Returns:
            bool: 停止成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.app_terminate(bundle_id)
            logger.info(f"应用 {bundle_id} 停止成功")
            return True
        except Exception as e:
            logger.error(f"停止应用 {bundle_id} 失败: {e}")
            return False

    def app_current(self) -> Dict[str, Any]:
        """
        获取当前应用信息

        Returns:
            Dict[str, Any]: 当前应用信息
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.app_current()
        except Exception as e:
            logger.error(f"获取当前应用信息失败: {e}")
            raise IDBError(f"获取当前应用信息失败: {e}")

    def app_list(self) -> List[Dict[str, Any]]:
        """
        获取应用列表

        Returns:
            List[Dict[str, Any]]: 应用列表
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.list_apps()
        except Exception as e:
            logger.error(f"获取应用列表失败: {e}")
            raise IDBError(f"获取应用列表失败: {e}")

    def find_element(self, element_type: str, label: Optional[str] = None, 
                    name: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """
        查找元素

        Args:
            element_type: 元素类型（如Button、TextField等）
            label: 元素标签
            name: 元素名称
            **kwargs: 其他查找条件

        Returns:
            Optional[Dict[str, Any]]: 找到的元素信息，未找到返回None
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            elements = self.device.find_elements(element_type)
            
            # 根据条件过滤元素
            for element in elements:
                if label and element.get('label') != label:
                    continue
                if name and element.get('name') != name:
                    continue
                
                # 检查其他条件
                match = True
                for key, value in kwargs.items():
                    if element.get(key) != value:
                        match = False
                        break
                
                if match:
                    return element
            
            return None
            
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            raise IDBError(f"查找元素失败: {e}")

    def find_elements(self, element_type: str, **kwargs) -> List[Dict[str, Any]]:
        """
        查找多个元素

        Args:
            element_type: 元素类型
            **kwargs: 查找条件

        Returns:
            List[Dict[str, Any]]: 找到的元素列表
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            elements = self.device.find_elements(element_type)
            
            # 根据条件过滤元素
            filtered_elements = []
            for element in elements:
                match = True
                for key, value in kwargs.items():
                    if element.get(key) != value:
                        match = False
                        break
                
                if match:
                    filtered_elements.append(element)
            
            return filtered_elements
            
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            raise IDBError(f"查找元素失败: {e}")

    def tap(self, x: int, y: int) -> bool:
        """
        点击指定坐标

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.tap((x, y))
            logger.info(f"点击坐标 ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"点击坐标 ({x}, {y}) 失败: {e}")
            return False

    def tap_element(self, element: Dict[str, Any]) -> bool:
        """
        点击元素

        Args:
            element: 元素信息

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            bounds = element.get('bounds', {})
            center_x = bounds.get('x', 0) + bounds.get('width', 0) // 2
            center_y = bounds.get('y', 0) + bounds.get('height', 0) // 2
            
            self.device.tap((center_x, center_y))
            logger.info(f"点击元素: {element.get('label', element.get('name', 'Unknown'))}")
            return True
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return False

    def long_press(self, x: int, y: int, duration: float = 2.0) -> bool:
        """
        长按指定坐标

        Args:
            x: X坐标
            y: Y坐标
            duration: 长按持续时间（秒）

        Returns:
            bool: 长按成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.long_press((x, y), duration=duration)
            logger.info(f"长按坐标 ({x}, {y}) {duration}秒")
            return True
        except Exception as e:
            logger.error(f"长按坐标 ({x}, {y}) 失败: {e}")
            return False

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, 
              duration: float = 1.0) -> bool:
        """
        滑动操作

        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 滑动持续时间（秒）

        Returns:
            bool: 滑动成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.swipe((start_x, start_y), (end_x, end_y), duration=duration)
            logger.info(f"滑动从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
            return True
        except Exception as e:
            logger.error(f"滑动操作失败: {e}")
            return False

    def input_text(self, text: str) -> bool:
        """
        输入文本

        Args:
            text: 要输入的文本

        Returns:
            bool: 输入成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.input_text(text)
            logger.info(f"输入文本: {text}")
            return True
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False

    def clear_text(self) -> bool:
        """
        清除文本

        Returns:
            bool: 清除成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.clear_text()
            logger.info("清除文本")
            return True
        except Exception as e:
            logger.error(f"清除文本失败: {e}")
            return False

    def press_key(self, key: str) -> bool:
        """
        按键操作

        Args:
            key: 按键名称（如home、volume_up等）

        Returns:
            bool: 按键成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.press_key(key)
            logger.info(f"按键: {key}")
            return True
        except Exception as e:
            logger.error(f"按键 {key} 失败: {e}")
            return False

    def screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """
        截图

        Args:
            save_path: 保存路径，如果为None则自动生成

        Returns:
            Optional[str]: 保存的文件路径，失败返回None
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            screenshot = self.device.screenshot()
            
            if save_path is None:
                timestamp = int(time.time())
                save_path = f"screenshot_{timestamp}.png"
            
            screenshot.save(save_path)
            logger.info(f"截图保存到: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def file_push(self, local_path: str, device_path: str) -> bool:
        """
        上传文件到设备

        Args:
            local_path: 本地文件路径
            device_path: 设备文件路径

        Returns:
            bool: 上传成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.file_push(local_path, device_path)
            logger.info(f"文件上传成功: {local_path} -> {device_path}")
            return True
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return False

    def file_pull(self, device_path: str, local_path: str) -> bool:
        """
        从设备下载文件

        Args:
            device_path: 设备文件路径
            local_path: 本地文件路径

        Returns:
            bool: 下载成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.file_pull(device_path, local_path)
            logger.info(f"文件下载成功: {device_path} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return False

    def file_list(self, device_path: str) -> List[Dict[str, Any]]:
        """
        列出设备文件

        Args:
            device_path: 设备路径

        Returns:
            List[Dict[str, Any]]: 文件列表
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.file_list(device_path)
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise IDBError(f"列出文件失败: {e}")

    def start_video_recording(self, output_path: str) -> bool:
        """
        开始录屏

        Args:
            output_path: 输出文件路径

        Returns:
            bool: 开始录屏成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.video_start(output_path)
            logger.info(f"开始录屏: {output_path}")
            return True
        except Exception as e:
            logger.error(f"开始录屏失败: {e}")
            return False

    def stop_video_recording(self) -> bool:
        """
        停止录屏

        Returns:
            bool: 停止录屏成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.video_stop()
            logger.info("停止录屏")
            return True
        except Exception as e:
            logger.error(f"停止录屏失败: {e}")
            return False

    def start_network_monitoring(self) -> bool:
        """
        开始网络监控

        Returns:
            bool: 开始监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.network_start_monitoring()
            logger.info("开始网络监控")
            return True
        except Exception as e:
            logger.error(f"开始网络监控失败: {e}")
            return False

    def stop_network_monitoring(self) -> bool:
        """
        停止网络监控

        Returns:
            bool: 停止监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.network_stop_monitoring()
            logger.info("停止网络监控")
            return True
        except Exception as e:
            logger.error(f"停止网络监控失败: {e}")
            return False

    def get_network_stats(self) -> Dict[str, Any]:
        """
        获取网络统计信息

        Returns:
            Dict[str, Any]: 网络统计信息
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.network_get_stats()
        except Exception as e:
            logger.error(f"获取网络统计失败: {e}")
            raise IDBError(f"获取网络统计失败: {e}")

    def start_performance_monitoring(self) -> bool:
        """
        开始性能监控

        Returns:
            bool: 开始监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.performance_start_monitoring()
            logger.info("开始性能监控")
            return True
        except Exception as e:
            logger.error(f"开始性能监控失败: {e}")
            return False

    def stop_performance_monitoring(self) -> bool:
        """
        停止性能监控

        Returns:
            bool: 停止监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.performance_stop_monitoring()
            logger.info("停止性能监控")
            return True
        except Exception as e:
            logger.error(f"停止性能监控失败: {e}")
            return False

    def get_performance_data(self) -> Dict[str, Any]:
        """
        获取性能数据

        Returns:
            Dict[str, Any]: 性能数据
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.performance_get_data()
        except Exception as e:
            logger.error(f"获取性能数据失败: {e}")
            raise IDBError(f"获取性能数据失败: {e}")

    def start_log_monitoring(self) -> bool:
        """
        开始日志监控

        Returns:
            bool: 开始监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.log_start_monitoring()
            logger.info("开始日志监控")
            return True
        except Exception as e:
            logger.error(f"开始日志监控失败: {e}")
            return False

    def stop_log_monitoring(self) -> bool:
        """
        停止日志监控

        Returns:
            bool: 停止监控成功返回True，否则返回False
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            self.device.log_stop_monitoring()
            logger.info("停止日志监控")
            return True
        except Exception as e:
            logger.error(f"停止日志监控失败: {e}")
            return False

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        获取日志

        Returns:
            List[Dict[str, Any]]: 日志列表
        """
        if not self.is_connected():
            raise IDBError("设备未连接")

        try:
            return self.device.log_get_logs()
        except Exception as e:
            logger.error(f"获取日志失败: {e}")
            raise IDBError(f"获取日志失败: {e}")


class IDBWebViewAgent:
    """
    IDB WebView自动化代理

    这个类提供了基于IDB的WebView自动化功能。
    主要用于在iOS应用中的WebView组件进行自动化操作。
    """

    def __init__(self, idb_automator: IDBAutomator):
        """
        初始化WebView代理

        Args:
            idb_automator: IDB自动化控制器实例
        """
        self.idb = idb_automator

    def find_webview(self) -> Optional[Dict[str, Any]]:
        """
        查找WebView元素

        Returns:
            Optional[Dict[str, Any]]: WebView元素信息，未找到返回None
        """
        try:
            return self.idb.find_element("WebView")
        except Exception as e:
            logger.error(f"查找WebView失败: {e}")
            return None

    def switch_to_webview(self) -> bool:
        """
        切换到WebView上下文

        Returns:
            bool: 切换成功返回True，否则返回False
        """
        try:
            webview = self.find_webview()
            if webview:
                # 点击WebView以激活
                self.idb.tap_element(webview)
                time.sleep(1)
                logger.info("已切换到WebView上下文")
                return True
            else:
                logger.warning("未找到WebView元素")
                return False
        except Exception as e:
            logger.error(f"切换到WebView失败: {e}")
            return False

    def execute_webview_script(self, script: str) -> Optional[Any]:
        """
        在WebView中执行JavaScript脚本

        Args:
            script: JavaScript脚本

        Returns:
            Optional[Any]: 脚本执行结果
        """
        try:
            # 注意：IDB可能不直接支持WebView中的JavaScript执行
            # 这里提供一个基础实现，实际使用可能需要其他方法
            logger.warning("IDB WebView JavaScript执行功能可能需要额外实现")
            return None
        except Exception as e:
            logger.error(f"执行WebView脚本失败: {e}")
            return None

    # ==================== 与uiautomator2对齐的方法 ====================
    
    def tap_coordinate(self, x: int, y: int) -> bool:
        """
        点击指定坐标（类似uiautomator2的d.click(x, y)）
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            self.device.tap(x, y)
            logger.info(f"点击坐标: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"坐标点击失败: {e}")
            return False

    def swipe_left(self, duration: float = 1.0) -> bool:
        """
        左滑（类似uiautomator2的d.swipe_left()）
        
        Args:
            duration: 滑动持续时间
            
        Returns:
            bool: 操作是否成功
        """
        screen_info = self.get_screen_info()
        if not screen_info:
            return False
            
        width = screen_info['width']
        height = screen_info['height']
        start_x = int(width * 0.8)
        end_x = int(width * 0.2)
        start_y = int(height * 0.5)
        
        return self.swipe(start_x, start_y, end_x, start_y, duration)

    def swipe_right(self, duration: float = 1.0) -> bool:
        """
        右滑（类似uiautomator2的d.swipe_right()）
        
        Args:
            duration: 滑动持续时间
            
        Returns:
            bool: 操作是否成功
        """
        screen_info = self.get_screen_info()
        if not screen_info:
            return False
            
        width = screen_info['width']
        height = screen_info['height']
        start_x = int(width * 0.2)
        end_x = int(width * 0.8)
        start_y = int(height * 0.5)
        
        return self.swipe(start_x, start_y, end_x, start_y, duration)

    def swipe_up(self, duration: float = 1.0) -> bool:
        """
        上滑（类似uiautomator2的d.swipe_up()）
        
        Args:
            duration: 滑动持续时间
            
        Returns:
            bool: 操作是否成功
        """
        screen_info = self.get_screen_info()
        if not screen_info:
            return False
            
        width = screen_info['width']
        height = screen_info['height']
        start_x = int(width * 0.5)
        start_y = int(height * 0.8)
        end_y = int(height * 0.2)
        
        return self.swipe(start_x, start_y, start_x, end_y, duration)

    def swipe_down(self, duration: float = 1.0) -> bool:
        """
        下滑（类似uiautomator2的d.swipe_down()）
        
        Args:
            duration: 滑动持续时间
            
        Returns:
            bool: 操作是否成功
        """
        screen_info = self.get_screen_info()
        if not screen_info:
            return False
            
        width = screen_info['width']
        height = screen_info['height']
        start_x = int(width * 0.5)
        start_y = int(height * 0.2)
        end_y = int(height * 0.8)
        
        return self.swipe(start_x, start_y, start_x, end_y, duration)

    def wait_for_element(self, element_type: str, timeout: float = 10.0, **kwargs) -> Optional[Dict]:
        """
        等待元素出现（类似uiautomator2的d(text="登录").wait()）
        
        Args:
            element_type: 元素类型
            timeout: 超时时间（秒）
            **kwargs: 元素查找条件
            
        Returns:
            Optional[Dict]: 找到的元素信息，未找到返回None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self.find_element(element_type, **kwargs)
            if element:
                return element
            time.sleep(0.5)
        
        logger.warning(f"等待元素超时: {element_type}, {kwargs}")
        return None

    def element_exists(self, element_type: str, **kwargs) -> bool:
        """
        检查元素是否存在（类似uiautomator2的d(text="登录").exists）
        
        Args:
            element_type: 元素类型
            **kwargs: 元素查找条件
            
        Returns:
            bool: 元素是否存在
        """
        element = self.find_element(element_type, **kwargs)
        return element is not None

    def get_element_info(self, element_type: str, **kwargs) -> Optional[Dict]:
        """
        获取元素信息（类似uiautomator2的d(text="登录").info）
        
        Args:
            element_type: 元素类型
            **kwargs: 元素查找条件
            
        Returns:
            Optional[Dict]: 元素信息
        """
        return self.find_element(element_type, **kwargs)

    def get_screen_info(self) -> Optional[Dict]:
        """
        获取屏幕信息（类似uiautomator2的d.info）
        
        Returns:
            Optional[Dict]: 屏幕信息
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            # 获取设备信息
            device_info = self.get_device_info()
            return {
                'width': device_info.get('screen_width', 0),
                'height': device_info.get('screen_height', 0),
                'scale': device_info.get('screen_scale', 1.0),
                'orientation': device_info.get('orientation', 'portrait')
            }
        except Exception as e:
            logger.error(f"获取屏幕信息失败: {e}")
            return None

    def long_press_element(self, element: Dict, duration: float = 2.0) -> bool:
        """
        长按元素（类似uiautomator2的d.long_click()）
        
        Args:
            element: 元素信息
            duration: 长按持续时间
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            x = element.get('x', 0)
            y = element.get('y', 0)
            
            # 使用IDB的长按功能
            self.device.long_press(x, y, duration)
            logger.info(f"长按元素: ({x}, {y}), 持续时间: {duration}秒")
            return True
        except Exception as e:
            logger.error(f"长按元素失败: {e}")
            return False

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        拖拽操作（类似uiautomator2的d.drag()）
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖拽持续时间
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            # 使用IDB的拖拽功能
            self.device.drag(start_x, start_y, end_x, end_y, duration)
            logger.info(f"拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 持续时间: {duration}秒")
            return True
        except Exception as e:
            logger.error(f"拖拽操作失败: {e}")
            return False

    def double_tap_element(self, element: Dict) -> bool:
        """
        双击元素
        
        Args:
            element: 元素信息
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            x = element.get('x', 0)
            y = element.get('y', 0)
            
            # 双击操作
            self.device.double_tap(x, y)
            logger.info(f"双击元素: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"双击元素失败: {e}")
            return False

    def pinch(self, center_x: int, center_y: int, scale: float, duration: float = 1.0) -> bool:
        """
        多指操作（类似uiautomator2的d.pinch()）
        
        Args:
            center_x: 中心点X坐标
            center_y: 中心点Y坐标
            scale: 缩放比例（>1放大，<1缩小）
            duration: 操作持续时间
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            # 使用IDB的多指操作功能
            self.device.pinch(center_x, center_y, scale, duration)
            logger.info(f"多指操作: 中心({center_x}, {center_y}), 缩放: {scale}, 持续时间: {duration}秒")
            return True
        except Exception as e:
            logger.error(f"多指操作失败: {e}")
            return False

    def input_text_to_element(self, element: Dict, text: str) -> bool:
        """
        向指定元素输入文本（类似uiautomator2的d(text="输入框").set_text()）
        
        Args:
            element: 元素信息
            text: 要输入的文本
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise IDBError("设备未连接")
            
        try:
            x = element.get('x', 0)
            y = element.get('y', 0)
            
            # 先点击元素
            self.device.tap(x, y)
            time.sleep(0.5)
            
            # 输入文本
            self.input_text(text)
            logger.info(f"向元素输入文本: {text}")
            return True
        except Exception as e:
            logger.error(f"向元素输入文本失败: {e}")
            return False
