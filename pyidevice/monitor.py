"""设备监控模块"""

import time
import threading
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from .exceptions import DeviceError, DeviceConnectionError
from .types import DeviceStatus

logger = logging.getLogger(__name__)


@dataclass
class DeviceMetrics:
    """设备指标数据类"""

    udid: str
    timestamp: datetime
    status: DeviceStatus
    battery_level: int
    memory_usage: float
    cpu_usage: float
    network_status: str
    temperature: Optional[float] = None
    storage_free: Optional[int] = None
    storage_total: Optional[int] = None


class DeviceMonitor:
    """设备监控器"""

    def __init__(self, interval: float = 30.0):
        """
        初始化设备监控器

        Args:
            interval: 监控间隔（秒）
        """
        self.interval = interval
        self.monitoring = False
        self.monitor_thread = None
        self.devices: Dict[str, DeviceMetrics] = {}
        self.callbacks: List[Callable[[DeviceMetrics], None]] = []
        self._lock = threading.Lock()

    def add_callback(self, callback: Callable[[DeviceMetrics], None]):
        """添加监控回调函数"""
        with self._lock:
            self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[DeviceMetrics], None]):
        """移除监控回调函数"""
        with self._lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)

    def start_monitoring(self, udids: List[str]):
        """
        开始监控设备

        Args:
            udids: 要监控的设备UDID列表
        """
        if self.monitoring:
            logger.warning("监控已在运行中")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(udids,), daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"开始监控设备: {udids}")

    def stop_monitoring(self):
        """停止监控"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("设备监控已停止")

    def _monitor_loop(self, udids: List[str]):
        """监控循环"""
        while self.monitoring:
            try:
                for udid in udids:
                    if not self.monitoring:
                        break

                    try:
                        metrics = self._collect_device_metrics(udid)
                        if metrics:
                            self._update_device_metrics(metrics)
                            self._notify_callbacks(metrics)
                    except Exception as e:
                        logger.error(f"收集设备 {udid} 指标失败: {e}")

                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                time.sleep(self.interval)

    def _collect_device_metrics(self, udid: str) -> Optional[DeviceMetrics]:
        """收集设备指标"""
        try:
            from .device import Device

            device = Device(udid)

            # 检查设备连接状态
            if not device.is_connected():
                return DeviceMetrics(
                    udid=udid,
                    timestamp=datetime.now(),
                    status=DeviceStatus.DISCONNECTED,
                    battery_level=-1,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    network_status="unknown",
                )

            # 获取设备信息
            info = device.info()

            # 解析指标
            battery_level = int(info.get("BatteryLevel", -1))
            memory_usage = float(info.get("MemoryUsage", 0.0))
            cpu_usage = float(info.get("CPUUsage", 0.0))
            network_status = info.get("NetworkStatus", "unknown")
            temperature = info.get("Temperature")
            if temperature:
                temperature = float(temperature)

            storage_free = info.get("StorageFree")
            if storage_free:
                storage_free = int(storage_free)

            storage_total = info.get("StorageTotal")
            if storage_total:
                storage_total = int(storage_total)

            return DeviceMetrics(
                udid=udid,
                timestamp=datetime.now(),
                status=DeviceStatus.CONNECTED,
                battery_level=battery_level,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                network_status=network_status,
                temperature=temperature,
                storage_free=storage_free,
                storage_total=storage_total,
            )

        except Exception as e:
            logger.error(f"收集设备 {udid} 指标时出错: {e}")
            return None

    def _update_device_metrics(self, metrics: DeviceMetrics):
        """更新设备指标"""
        with self._lock:
            self.devices[metrics.udid] = metrics

    def _notify_callbacks(self, metrics: DeviceMetrics):
        """通知回调函数"""
        with self._lock:
            for callback in self.callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(f"回调函数执行失败: {e}")

    def get_device_metrics(self, udid: str) -> Optional[DeviceMetrics]:
        """获取设备指标"""
        with self._lock:
            return self.devices.get(udid)

    def get_all_metrics(self) -> Dict[str, DeviceMetrics]:
        """获取所有设备指标"""
        with self._lock:
            return self.devices.copy()

    def get_device_history(self, udid: str, hours: int = 24) -> List[DeviceMetrics]:
        """获取设备历史指标（模拟实现）"""
        # 这里应该从数据库或文件系统读取历史数据
        # 目前返回空列表作为占位符
        return []


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_callbacks: List[Callable[[str, str, Dict[str, Any]], None]] = []

    def add_alert_rule(
        self,
        name: str,
        condition: Callable[[DeviceMetrics], bool],
        message: str,
        severity: str = "warning",
    ):
        """
        添加告警规则

        Args:
            name: 告警规则名称
            condition: 告警条件函数
            message: 告警消息
            severity: 告警严重程度
        """
        self.alerts[name] = {
            "condition": condition,
            "message": message,
            "severity": severity,
            "triggered": False,
        }

    def add_alert_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    def check_alerts(self, metrics: DeviceMetrics):
        """检查告警条件"""
        for name, alert in self.alerts.items():
            try:
                if alert["condition"](metrics):
                    if not alert["triggered"]:
                        self._trigger_alert(name, alert, metrics)
                        alert["triggered"] = True
                else:
                    alert["triggered"] = False
            except Exception as e:
                logger.error(f"检查告警 {name} 时出错: {e}")

    def _trigger_alert(self, name: str, alert: Dict[str, Any], metrics: DeviceMetrics):
        """触发告警"""
        alert_data = {
            "name": name,
            "message": alert["message"],
            "severity": alert["severity"],
            "device_udid": metrics.udid,
            "timestamp": metrics.timestamp,
            "metrics": metrics,
        }

        for callback in self.alert_callbacks:
            try:
                callback(name, alert["severity"], alert_data)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")

        logger.warning(f"告警触发: {name} - {alert['message']} (设备: {metrics.udid})")


# 预定义的告警条件
def low_battery_alert(threshold: int = 20):
    """低电量告警"""

    def condition(metrics: DeviceMetrics) -> bool:
        return metrics.battery_level > 0 and metrics.battery_level < threshold

    return condition


def high_temperature_alert(threshold: float = 40.0):
    """高温告警"""

    def condition(metrics: DeviceMetrics) -> bool:
        return metrics.temperature is not None and metrics.temperature > threshold

    return condition


def high_memory_usage_alert(threshold: float = 80.0):
    """高内存使用率告警"""

    def condition(metrics: DeviceMetrics) -> bool:
        return metrics.memory_usage > threshold

    return condition


def device_disconnected_alert():
    """设备断开连接告警"""

    def condition(metrics: DeviceMetrics) -> bool:
        return metrics.status == DeviceStatus.DISCONNECTED

    return condition


# 全局监控器实例
device_monitor = DeviceMonitor()
alert_manager = AlertManager()

# 设置默认告警规则
alert_manager.add_alert_rule("low_battery", low_battery_alert(), "设备电量过低", "warning")
alert_manager.add_alert_rule(
    "high_temperature", high_temperature_alert(), "设备温度过高", "critical"
)
alert_manager.add_alert_rule(
    "high_memory", high_memory_usage_alert(), "设备内存使用率过高", "warning"
)
alert_manager.add_alert_rule(
    "device_disconnected", device_disconnected_alert(), "设备连接断开", "critical"
)

# 将告警检查添加到监控器
device_monitor.add_callback(alert_manager.check_alerts)
