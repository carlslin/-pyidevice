"""
pyidevice 批量操作模块

这个模块提供了批量操作iOS设备的功能，支持多设备并行执行任务，
大大提高工作效率。适用于需要同时对多个设备进行相同操作的场景。

主要功能：
- 多设备并行操作
- 批量应用管理（安装、卸载、启动）
- 批量设备信息获取
- 批量截图操作
- 操作结果统计和报告生成
- 错误处理和重试机制

主要类：
- BatchOperator: 批量操作器，提供通用的批量操作功能
- BatchAppManager: 批量应用管理器，专门处理应用相关操作
- BatchDeviceManager: 批量设备管理器，处理设备信息获取
- BatchReportGenerator: 批量报告生成器，生成操作结果报告

技术特性：
- 使用ThreadPoolExecutor实现并发执行
- 支持自定义并发数和超时时间
- 提供详细的操作结果和错误信息
- 支持操作进度监控和统计
- 完善的异常处理和日志记录

使用示例：
    >>> from pyidevice import BatchAppManager
    >>> manager = BatchAppManager(max_workers=3)
    >>> devices = ["udid1", "udid2", "udid3"]
    >>> results = manager.install_apps(devices, "app.ipa")
    >>> for result in results:
    ...     print(f"设备 {result.udid}: {'成功' if result.success else '失败'}")

依赖：
- concurrent.futures: 并发执行支持
- dataclasses: 数据类支持
- typing: 类型注解支持
- logging: 日志记录
"""

import time  # 时间相关功能
import logging  # 日志记录
from typing import List, Dict, Any, Optional, Callable, Union  # 类型注解
from concurrent.futures import ThreadPoolExecutor, as_completed  # 并发执行
from dataclasses import dataclass  # 数据类
from .exceptions import DeviceError  # 设备异常
from .device import Device  # 设备操作类

# 配置日志记录器
logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """批量操作结果"""

    udid: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration: float = 0.0


class BatchOperationError(DeviceError):
    """批量操作异常"""

    def __init__(self, message: str, results: List[BatchResult] = None, **kwargs):
        super().__init__(message, error_code="BATCH_OPERATION_ERROR", **kwargs)
        self.results = results or []


class BatchOperator:
    """批量操作器"""

    def __init__(self, max_workers: int = 5, timeout: float = 300.0):
        """
        初始化批量操作器

        Args:
            max_workers: 最大并发工作线程数
            timeout: 操作超时时间（秒）
        """
        self.max_workers = max_workers
        self.timeout = timeout

    def execute_batch(
        self,
        udids: List[str],
        operation: Callable[[Device], Any],
        operation_name: str = "batch_operation",
    ) -> List[BatchResult]:
        """
        执行批量操作

        Args:
            udids: 设备UDID列表
            operation: 操作函数，接受Device对象作为参数
            operation_name: 操作名称

        Returns:
            List[BatchResult]: 操作结果列表
        """
        logger.info(f"开始批量操作 '{operation_name}'，设备数量: {len(udids)}")

        results = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_udid = {
                executor.submit(self._execute_single, udid, operation): udid for udid in udids
            }

            # 收集结果
            for future in as_completed(future_to_udid, timeout=self.timeout):
                udid = future_to_udid[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"设备 {udid} 操作失败: {e}")
                    results.append(
                        BatchResult(
                            udid=udid, success=False, result=None, error=str(e), duration=0.0
                        )
                    )

        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r.success)

        logger.info(
            f"批量操作 '{operation_name}' 完成: {success_count}/{len(udids)} 成功，耗时 {total_duration:.2f}s"
        )

        return results

    def _execute_single(self, udid: str, operation: Callable[[Device], Any]) -> BatchResult:
        """执行单个设备操作"""
        start_time = time.time()

        try:
            device = Device(udid)
            result = operation(device)
            duration = time.time() - start_time

            return BatchResult(udid=udid, success=True, result=result, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            return BatchResult(
                udid=udid, success=False, result=None, error=str(e), duration=duration
            )


class BatchAppManager:
    """批量应用管理器"""

    def __init__(self, max_workers: int = 3):
        """
        初始化批量应用管理器

        Args:
            max_workers: 最大并发工作线程数
        """
        self.operator = BatchOperator(max_workers=max_workers, timeout=600.0)

    def install_apps(self, udids: List[str], ipa_path: str) -> List[BatchResult]:
        """
        批量安装应用

        Args:
            udids: 设备UDID列表
            ipa_path: IPA文件路径

        Returns:
            List[BatchResult]: 安装结果列表
        """

        def install_operation(device: Device) -> bool:
            return device.install_app(ipa_path)

        return self.operator.execute_batch(udids, install_operation, "install_app")

    def uninstall_apps(self, udids: List[str], bundle_id: str) -> List[BatchResult]:
        """
        批量卸载应用

        Args:
            udids: 设备UDID列表
            bundle_id: 应用包ID

        Returns:
            List[BatchResult]: 卸载结果列表
        """

        def uninstall_operation(device: Device) -> bool:
            return device.uninstall_app(bundle_id)

        return self.operator.execute_batch(udids, uninstall_operation, "uninstall_app")

    def start_apps(self, udids: List[str], bundle_id: str) -> List[BatchResult]:
        """
        批量启动应用

        Args:
            udids: 设备UDID列表
            bundle_id: 应用包ID

        Returns:
            List[BatchResult]: 启动结果列表
        """

        def start_operation(device: Device) -> bool:
            return device.start_app(bundle_id)

        return self.operator.execute_batch(udids, start_operation, "start_app")

    def take_screenshots(self, udids: List[str], output_dir: str) -> List[BatchResult]:
        """
        批量截取屏幕截图

        Args:
            udids: 设备UDID列表
            output_dir: 输出目录

        Returns:
            List[BatchResult]: 截图结果列表
        """
        import os

        def screenshot_operation(device: Device) -> str:
            timestamp = int(time.time())
            filename = f"{device.udid}_{timestamp}.png"
            output_path = os.path.join(output_dir, filename)

            success = device.take_screenshot(output_path)
            if success:
                return output_path
            else:
                raise Exception("截图失败")

        return self.operator.execute_batch(udids, screenshot_operation, "take_screenshot")


class BatchDeviceManager:
    """批量设备管理器"""

    def __init__(self, max_workers: int = 5):
        """
        初始化批量设备管理器

        Args:
            max_workers: 最大并发工作线程数
        """
        self.operator = BatchOperator(max_workers=max_workers, timeout=300.0)

    def get_device_info(self, udids: List[str]) -> List[BatchResult]:
        """
        批量获取设备信息

        Args:
            udids: 设备UDID列表

        Returns:
            List[BatchResult]: 设备信息结果列表
        """

        def info_operation(device: Device) -> Dict[str, Any]:
            return device.info()

        return self.operator.execute_batch(udids, info_operation, "get_device_info")

    def reboot_devices(self, udids: List[str]) -> List[BatchResult]:
        """
        批量重启设备

        Args:
            udids: 设备UDID列表

        Returns:
            List[BatchResult]: 重启结果列表
        """

        def reboot_operation(device: Device) -> bool:
            return device.reboot()

        return self.operator.execute_batch(udids, reboot_operation, "reboot_device")

    def shutdown_devices(self, udids: List[str]) -> List[BatchResult]:
        """
        批量关机设备

        Args:
            udids: 设备UDID列表

        Returns:
            List[BatchResult]: 关机结果列表
        """

        def shutdown_operation(device: Device) -> bool:
            return device.shutdown()

        return self.operator.execute_batch(udids, shutdown_operation, "shutdown_device")

    def check_device_status(self, udids: List[str]) -> List[BatchResult]:
        """
        批量检查设备状态

        Args:
            udids: 设备UDID列表

        Returns:
            List[BatchResult]: 设备状态结果列表
        """

        def status_operation(device: Device) -> Dict[str, Any]:
            return {
                "udid": device.udid,
                "connected": device.is_connected(),
                "name": device.name(),
                "version": device.version(),
                "battery_level": device.battery_level(),
            }

        return self.operator.execute_batch(udids, status_operation, "check_device_status")


class BatchReportGenerator:
    """批量操作报告生成器"""

    @staticmethod
    def generate_summary_report(results: List[BatchResult], operation_name: str) -> Dict[str, Any]:
        """
        生成汇总报告

        Args:
            results: 批量操作结果列表
            operation_name: 操作名称

        Returns:
            Dict[str, Any]: 汇总报告
        """
        total_count = len(results)
        success_count = sum(1 for r in results if r.success)
        failure_count = total_count - success_count
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        total_duration = sum(r.duration for r in results)
        avg_duration = total_duration / total_count if total_count > 0 else 0

        failed_devices = [r.udid for r in results if not r.success]

        return {
            "operation_name": operation_name,
            "total_count": total_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": round(success_rate, 2),
            "total_duration": round(total_duration, 2),
            "avg_duration": round(avg_duration, 2),
            "failed_devices": failed_devices,
            "timestamp": time.time(),
        }

    @staticmethod
    def generate_detailed_report(results: List[BatchResult], operation_name: str) -> Dict[str, Any]:
        """
        生成详细报告

        Args:
            results: 批量操作结果列表
            operation_name: 操作名称

        Returns:
            Dict[str, Any]: 详细报告
        """
        summary = BatchReportGenerator.generate_summary_report(results, operation_name)

        detailed_results = []
        for result in results:
            detailed_results.append(
                {
                    "udid": result.udid,
                    "success": result.success,
                    "result": result.result,
                    "error": result.error,
                    "duration": round(result.duration, 2),
                }
            )

        summary["detailed_results"] = detailed_results
        return summary

    @staticmethod
    def save_report_to_file(report: Dict[str, Any], filename: str):
        """
        保存报告到文件

        Args:
            report: 报告数据
            filename: 文件名
        """
        import json

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"报告已保存到: {filename}")


# 便捷函数
def batch_install_app(udids: List[str], ipa_path: str, max_workers: int = 3) -> List[BatchResult]:
    """批量安装应用"""
    manager = BatchAppManager(max_workers=max_workers)
    return manager.install_apps(udids, ipa_path)


def batch_uninstall_app(
    udids: List[str], bundle_id: str, max_workers: int = 3
) -> List[BatchResult]:
    """批量卸载应用"""
    manager = BatchAppManager(max_workers=max_workers)
    return manager.uninstall_apps(udids, bundle_id)


def batch_take_screenshots(
    udids: List[str], output_dir: str, max_workers: int = 3
) -> List[BatchResult]:
    """批量截取屏幕截图"""
    manager = BatchAppManager(max_workers=max_workers)
    return manager.take_screenshots(udids, output_dir)


def batch_get_device_info(udids: List[str], max_workers: int = 5) -> List[BatchResult]:
    """批量获取设备信息"""
    manager = BatchDeviceManager(max_workers=max_workers)
    return manager.get_device_info(udids)
