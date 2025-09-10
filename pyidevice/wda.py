"""
pyidevice WDA模块

这个模块提供了基于WebDriverAgent (WDA) 的iOS UI自动化功能。

主要功能：
- 设备连接和会话管理
- 元素查找和操作
- 手势操作（点击、滑动、输入等）
- 应用状态管理
- 屏幕截图和元素截图

主要类：
- WDAutomator: UI自动化控制器
- WebViewAgent: WebView自动化代理

依赖：
- facebook-wda: WebDriverAgent的Python客户端
- WebDriverAgent: 需要在设备上安装的自动化服务

使用示例：
    >>> from pyidevice import WDAutomator
    >>> wda = WDAutomator("00008020-0012345678901234")
    >>> wda.connect("http://localhost:8100")
    >>> element = wda.find_element("//XCUIElementTypeButton[@name='登录']")
    >>> element.click()
"""

import time
import logging
from typing import Optional, Dict, List, Any, Union
import wda
import os
import re

# 配置日志记录器
logger = logging.getLogger(__name__)


class WDAutomator:
    """
    iOS设备UI自动化控制器

    这个类提供了基于WebDriverAgent (WDA) 的iOS UI自动化功能。
    它封装了facebook-wda库，提供了更简洁的API接口。

    主要功能：
    1. 设备连接和会话管理
    2. 元素查找和操作
    3. 手势操作（点击、滑动、输入等）
    4. 应用状态管理
    5. 屏幕截图和元素截图

    特性：
    - 自动检测WebDriverAgent安装状态
    - 支持多种元素定位方式
    - 提供丰富的手势操作
    - 完善的错误处理和日志记录

    注意事项：
    - 需要先在设备上安装WebDriverAgent
    - 需要启动WDA服务（通常运行在8100端口）
    - 某些操作可能需要应用在前台运行
    """

    def __init__(self, udid: str, port: int = 8100):
        self.udid = udid
        self.port = port
        self.client = None
        self.session = None
        self._is_installed = False

    def _ensure_wdaproxy_installed(self) -> bool:
        """确保WebDriverAgent已安装"""
        if self._is_installed:
            return True

        try:
            # 检查WebDriverAgent是否已安装
            import subprocess

            result = subprocess.run(
                ["ideviceinstaller", "-u", self.udid, "-l"], capture_output=True, text=True
            )

            if "com.facebook.WebDriverAgentRunner.xctrunner" in result.stdout:
                self._is_installed = True
                return True

            # 如果没有安装，尝试通过libimobiledevice安装
            logger.info(f"WebDriverAgent not found on device {self.udid}, trying to install...")
            # 这里简化处理，实际使用时可能需要指定WebDriverAgent的路径
            # subprocess.run(['xcodebuild', '-project', 'WebDriverAgent.xcodeproj', ...])

            # 由于无法直接在此环境中构建WebDriverAgent，我们假设用户会手动安装
            logger.warning(
                "Please install WebDriverAgent manually before using UI automation features."
            )
            return False
        except Exception as e:
            logger.error(f"Failed to check/install WebDriverAgent: {e}")
            return False

    def connect(self, retry_count: int = 3, retry_interval: float = 2.0) -> bool:
        """连接到设备的WebDriverAgent服务"""
        if not self._ensure_wdaproxy_installed():
            return False

        for i in range(retry_count):
            try:
                # 启动iproxy端口转发
                import subprocess

                self.iproxy_process = subprocess.Popen(
                    ["iproxy", str(self.port), "8100", self.udid],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # 等待iproxy启动
                time.sleep(1)

                # 连接到WDA服务
                self.client = wda.Client(f"http://localhost:{self.port}")
                self.client.wait_ready(timeout=10.0)
                
                logger.info(f"Connected to device {self.udid} via WebDriverAgent")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {i+1} failed: {e}")
                if i < retry_count - 1:
                    time.sleep(retry_interval)

        logger.error(f"Failed to connect to device {self.udid} after {retry_count} attempts")
        return False


    def disconnect(self) -> None:
        """断开连接并清理资源"""
        if hasattr(self, "iproxy_process") and self.iproxy_process.poll() is None:
            self.iproxy_process.terminate()
            self.iproxy_process.wait(timeout=3.0)
            logger.info("iproxy process terminated")

        self.client = None
        self.session = None

    def app_start(self, bundle_id: str) -> bool:
        """启动应用并创建会话"""
        if not self.client:
            if not self.connect():
                return False

        try:
            self.session = self.client.session(bundle_id)
            logger.info(f"Started app {bundle_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start app {bundle_id}: {e}")
            return False

    def app_stop(self, bundle_id: str = None) -> bool:
        """停止应用"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            self.session.close()
            self.session = None
            logger.info(f"Stopped app")
            return True
        except Exception as e:
            logger.error(f"Failed to stop app: {e}")
            return False

    # UI操作方法，与uiautomater2对齐
    def find_element(self, selector: str, value: Any) -> Optional[wda.Element]:
        """查找单个元素"""
        if not self.session:
            logger.warning("No active session")
            return None

        try:
            if selector == "id":
                return self.session(id=value)
            elif selector == "xpath":
                return self.session(xpath=value)
            elif selector == "class":
                return self.session(className=value)
            elif selector == "text":
                return self.session(text=value)
            elif selector == "name":
                return self.session(name=value)
            else:
                logger.warning(f"Unsupported selector: {selector}")
                return None
        except Exception as e:
            logger.error(f"Failed to find element: {e}")
            return None

    def find_elements(self, selector: str, value: Any) -> List[wda.Element]:
        """查找多个元素"""
        if not self.session:
            logger.warning("No active session")
            return []

        try:
            if selector == "id":
                return self.session(id=value).find_elements()
            elif selector == "xpath":
                return self.session(xpath=value).find_elements()
            elif selector == "class":
                return self.session(className=value).find_elements()
            elif selector == "text":
                return self.session(text=value).find_elements()
            elif selector == "name":
                return self.session(name=value).find_elements()
            else:
                logger.warning(f"Unsupported selector: {selector}")
                return []
        except Exception as e:
            logger.error(f"Failed to find elements: {e}")
            return []

    def click(self, selector: str, value: Any) -> bool:
        """点击元素"""
        element = self.find_element(selector, value)
        if element:
            try:
                element.click()
                return True
            except Exception as e:
                logger.error(f"Failed to click element: {e}")
        return False

    def double_click(self, selector: str, value: Any) -> bool:
        """双击元素"""
        element = self.find_element(selector, value)
        if element:
            try:
                element.click()
                element.click()
                return True
            except Exception as e:
                logger.error(f"Failed to double click element: {e}")
        return False

    def long_click(self, selector: str, value: Any, duration: float = 1.0) -> bool:
        """长按元素"""
        element = self.find_element(selector, value)
        if element:
            try:
                element.tap_hold(duration)
                return True
            except Exception as e:
                logger.error(f"Failed to long click element: {e}")
        return False

    def set_text(self, selector: str, value: Any, text: str) -> bool:
        """设置元素文本"""
        element = self.find_element(selector, value)
        if element:
            try:
                element.set_text(text)
                return True
            except Exception as e:
                logger.error(f"Failed to set text: {e}")
        return False

    def get_text(self, selector: str, value: Any) -> Optional[str]:
        """获取元素文本"""
        element = self.find_element(selector, value)
        if element:
            try:
                return element.text
            except Exception as e:
                logger.error(f"Failed to get text: {e}")
        return None

    def swipe(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5
    ) -> bool:
        """滑动操作"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            self.session.swipe(start_x, start_y, end_x, end_y, duration)
            return True
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False

    def swipe_up(self, duration: float = 0.5) -> bool:
        """向上滑动"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            window_size = self.session.window_size()
            width, height = window_size["width"], window_size["height"]
            return self.swipe(width // 2, height * 3 // 4, width // 2, height // 4, duration)
        except Exception as e:
            logger.error(f"Failed to swipe up: {e}")
            return False

    def swipe_down(self, duration: float = 0.5) -> bool:
        """向下滑动"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            window_size = self.session.window_size()
            width, height = window_size["width"], window_size["height"]
            return self.swipe(width // 2, height // 4, width // 2, height * 3 // 4, duration)
        except Exception as e:
            logger.error(f"Failed to swipe down: {e}")
            return False

    def swipe_left(self, duration: float = 0.5) -> bool:
        """向左滑动"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            window_size = self.session.window_size()
            width, height = window_size["width"], window_size["height"]
            return self.swipe(width * 3 // 4, height // 2, width // 4, height // 2, duration)
        except Exception as e:
            logger.error(f"Failed to swipe left: {e}")
            return False

    def swipe_right(self, duration: float = 0.5) -> bool:
        """向右滑动"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            window_size = self.session.window_size()
            width, height = window_size["width"], window_size["height"]
            return self.swipe(width // 4, height // 2, width * 3 // 4, height // 2, duration)
        except Exception as e:
            logger.error(f"Failed to swipe right: {e}")
            return False

    def take_screenshot(self, filename: str) -> bool:
        """截取当前屏幕截图"""
        if not self.session:
            logger.warning("No active session")
            return False

        try:
            return self.session.screenshot().save(filename)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def get_current_package(self) -> Optional[str]:
        """获取当前包名"""
        if not self.session:
            logger.warning("No active session")
            return None

        try:
            # WDA中获取bundle_id的方式
            return self.session.bundle_id
        except Exception as e:
            logger.error(f"Failed to get current package: {e}")
            return None

    def get_current_activity(self) -> Optional[str]:
        """获取当前Activity（在iOS中对应场景）"""
        if not self.session:
            logger.warning("No active session")
            return None

        try:
            # iOS没有直接对应的Activity概念，返回当前页面的source
            return self.session.source
        except Exception as e:
            logger.error(f"Failed to get current activity: {e}")
            return None


class WebViewAgent:
    """WebView自动化控制器"""

    def __init__(self, wdautomator: WDAutomator):
        self.wda = wdautomator

    def switch_to_webview(self, webview_name: str = None) -> bool:
        """切换到WebView上下文"""
        if not self.wda.session:
            logger.warning("No active WDA session")
            return False

        try:
            contexts = self.wda.session.contexts
            webviews = [c for c in contexts if "WEBVIEW" in c]

            if not webviews:
                logger.warning("No WebView contexts found")
                return False

            # 如果指定了webview名称，则查找匹配的
            if webview_name:
                for wv in webviews:
                    if webview_name in wv:
                        self.wda.session._sessionId = wv
                        logger.info(f"Switched to WebView: {wv}")
                        return True
                logger.warning(f"WebView {webview_name} not found")
                return False

            # 否则切换到第一个WebView
            self.wda.session._sessionId = webviews[0]
            logger.info(f"Switched to WebView: {webviews[0]}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to WebView: {e}")
            return False

    def switch_to_native(self) -> bool:
        """切换回原生上下文"""
        if not self.wda.session:
            logger.warning("No active WDA session")
            return False

        try:
            contexts = self.wda.session.contexts
            native_contexts = [c for c in contexts if "NATIVE_APP" in c]

            if not native_contexts:
                logger.warning("No NATIVE_APP context found")
                return False

            self.wda.session._sessionId = native_contexts[0]
            logger.info("Switched back to NATIVE_APP context")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to native context: {e}")
            return False

    def find_element(self, selector: str, value: Any) -> Optional[wda.Element]:
        """在WebView中查找元素"""
        return self.wda.find_element(selector, value)

    def click(self, selector: str, value: Any) -> bool:
        """在WebView中点击元素"""
        return self.wda.click(selector, value)

    def set_text(self, selector: str, value: Any, text: str) -> bool:
        """在WebView中设置元素文本"""
        return self.wda.set_text(selector, value, text)

    def get_text(self, selector: str, value: Any) -> Optional[str]:
        """在WebView中获取元素文本"""
        return self.wda.get_text(selector, value)
