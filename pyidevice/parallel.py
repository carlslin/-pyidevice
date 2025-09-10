"""
pyidevice 并发操作模块

这个模块提供了多设备并行执行任务的功能，支持线程和进程两种并发模式。

主要功能：
- 多设备并行操作
- 任务管理和结果收集
- 并发执行器（线程/进程）
- 批量操作支持
- 性能监控和统计

主要类：
- DeviceTask: 设备任务封装类
- ParallelDeviceExecutor: 并行设备执行器
- ConcurrentDeviceManager: 并发设备管理器

使用示例：
    >>> from pyidevice import ParallelDeviceExecutor, Device
    >>> def process_device(udid):
    ...     device = Device(udid)
    ...     return device.info()
    >>> executor = ParallelDeviceExecutor(max_workers=3)
    >>> results = executor.map(process_device, device_list)
"""

import concurrent.futures
from typing import List, Dict, Any, Callable, Tuple, Optional, Union
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 配置日志记录器
logger = logging.getLogger(__name__)


class DeviceTask:
    """
    设备任务封装类

    这个类封装了要在设备上执行的操作，包括任务信息、执行状态和结果。

    属性：
    - udid: 设备唯一标识符
    - task_id: 任务唯一标识符
    - result: 任务执行结果
    - exception: 任务执行异常
    - start_time: 任务开始时间
    - end_time: 任务结束时间

    用途：
    - 跟踪任务执行状态
    - 收集任务执行结果
    - 处理任务执行异常
    - 计算任务执行时间
    """

    def __init__(self, udid: str, task_id: str = None):
        self.udid = udid
        self.task_id = task_id or f"task_{int(time.time() * 1000)}_{udid[:8]}"
        self.result = None
        self.exception = None
        self.start_time = None
        self.end_time = None

    def __str__(self):
        status = "completed" if self.end_time else "running" if self.start_time else "pending"
        return f"Task {self.task_id} (device: {self.udid}) - {status}"


class ParallelDeviceExecutor:
    """多设备并行执行器"""

    def __init__(self, max_workers: int = None, executor_type: str = "thread"):
        """
        初始化并行执行器

        Args:
            max_workers: 最大工作线程/进程数，默认为设备数量
            executor_type: 执行器类型，'thread' 或 'process'
        """
        self.max_workers = max_workers
        self.executor_type = executor_type.lower()
        self.executor = None
        self.tasks = []

        if self.executor_type not in ["thread", "process"]:
            raise ValueError("executor_type must be 'thread' or 'process'")

    def _create_executor(self):
        """创建执行器实例"""
        if self.executor_type == "thread":
            return ThreadPoolExecutor(max_workers=self.max_workers)
        else:
            return ProcessPoolExecutor(max_workers=self.max_workers)

    def submit_task(self, udid: str, func: Callable, *args, **kwargs) -> DeviceTask:
        """提交单个任务到指定设备"""
        task = DeviceTask(udid)

        def task_wrapper():
            task.start_time = time.time()
            try:
                result = func(udid, *args, **kwargs)
                task.result = result
                return result
            except Exception as e:
                task.exception = e
                logger.error(f"Task {task.task_id} failed: {e}")
                raise
            finally:
                task.end_time = time.time()

        self.tasks.append(task)

        # 如果执行器还未创建，先返回任务，等待执行时创建
        if not self.executor:
            return task

        # 提交任务到执行器
        future = self.executor.submit(task_wrapper)
        task.future = future
        return task

    def map_tasks(self, udids: List[str], func: Callable, *args, **kwargs) -> List[DeviceTask]:
        """为多个设备映射相同的任务"""
        tasks = []

        # 创建执行器
        if not self.executor:
            self.executor = self._create_executor()

        # 为每个设备提交任务
        for udid in udids:
            task = self.submit_task(udid, func, *args, **kwargs)
            tasks.append(task)

        return tasks

    def wait_for_completion(
        self, tasks: List[DeviceTask] = None, timeout: float = None
    ) -> List[DeviceTask]:
        """等待所有任务完成"""
        if tasks is None:
            tasks = self.tasks

        # 确保所有任务都已提交到执行器
        if not self.executor:
            self.executor = self._create_executor()
            for task in tasks:
                if not hasattr(task, "future"):
                    # 重新提交任务
                    self.submit_task(
                        task.udid, lambda: None
                    )  # 这只是示例，实际应该重新提交原始函数

        # 等待所有任务完成
        futures = [task.future for task in tasks if hasattr(task, "future")]
        if futures:
            concurrent.futures.wait(futures, timeout=timeout)

        return tasks

    def get_results(self, tasks: List[DeviceTask] = None) -> Dict[str, Any]:
        """获取所有任务的结果"""
        if tasks is None:
            tasks = self.tasks

        results = {}
        for task in tasks:
            if hasattr(task, "future"):
                try:
                    results[task.udid] = task.future.result()
                except Exception as e:
                    results[task.udid] = {"error": str(e)}
            else:
                # 如果任务还没有future，说明还没执行
                results[task.udid] = {"status": "pending"}

        return results

    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        if self.executor:
            self.executor.shutdown(wait=wait)
            self.executor = None

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时关闭执行器"""
        self.shutdown()


def parallel_run(
    udids: List[str],
    func: Callable,
    *args,
    max_workers: int = None,
    executor_type: str = "thread",
    timeout: float = None,
    **kwargs,
) -> Dict[str, Any]:
    """并行在多个设备上执行任务的便捷函数"""
    with ParallelDeviceExecutor(max_workers=max_workers, executor_type=executor_type) as executor:
        # 映射任务到设备
        tasks = executor.map_tasks(udids, func, *args, **kwargs)

        # 等待任务完成
        executor.wait_for_completion(tasks, timeout=timeout)

        # 返回结果
        return executor.get_results(tasks)


class ConcurrentDeviceManager:
    """并发设备管理器，提供更高级的并发操作接口"""

    def __init__(self, device_manager=None):
        """
        初始化并发设备管理器

        Args:
            device_manager: 设备管理器实例，如果为None则创建新实例
        """
        if device_manager is None:
            from .core import DeviceManager

            self.device_manager = DeviceManager()
        else:
            self.device_manager = device_manager

    def execute_on_all_devices(
        self,
        func: Callable,
        *args,
        max_workers: int = None,
        executor_type: str = "thread",
        timeout: float = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """在所有已连接的设备上执行任务"""
        # 获取所有设备UDID
        udids = self.device_manager.get_devices()
        if not udids:
            logger.warning("No devices connected")
            return {}

        # 使用parallel_run执行任务
        return parallel_run(
            udids,
            func,
            *args,
            max_workers=max_workers,
            executor_type=executor_type,
            timeout=timeout,
            **kwargs,
        )

    def execute_on_devices(
        self,
        udids: List[str],
        func: Callable,
        *args,
        max_workers: int = None,
        executor_type: str = "thread",
        timeout: float = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """在指定的设备上执行任务"""
        if not udids:
            logger.warning("No devices specified")
            return {}

        # 验证设备是否已连接
        connected_udids = self.device_manager.get_devices()
        valid_udids = [udid for udid in udids if udid in connected_udids]

        if not valid_udids:
            logger.warning("No valid devices specified")
            return {}

        if len(valid_udids) < len(udids):
            invalid_udids = set(udids) - set(valid_udids)
            logger.warning(f"Some devices are not connected: {invalid_udids}")

        # 使用parallel_run执行任务
        return parallel_run(
            valid_udids,
            func,
            *args,
            max_workers=max_workers,
            executor_type=executor_type,
            timeout=timeout,
            **kwargs,
        )

    def batch_install(
        self, udids: List[str], ipa_path: str, max_workers: int = None, timeout: float = None
    ) -> Dict[str, bool]:
        """批量安装应用到多个设备"""

        def install_task(udid):
            from .device import Device

            device = Device(udid)
            return device.install_app(ipa_path)

        return self.execute_on_devices(
            udids, install_task, max_workers=max_workers, timeout=timeout
        )

    def batch_uninstall(
        self, udids: List[str], bundle_id: str, max_workers: int = None, timeout: float = None
    ) -> Dict[str, bool]:
        """批量卸载多个设备上的应用"""

        def uninstall_task(udid):
            from .device import Device

            device = Device(udid)
            return device.uninstall_app(bundle_id)

        return self.execute_on_devices(
            udids, uninstall_task, max_workers=max_workers, timeout=timeout
        )

    def batch_get_info(
        self, udids: List[str] = None, max_workers: int = None, timeout: float = None
    ) -> Dict[str, Dict]:
        """批量获取设备信息"""

        def get_info_task(udid):
            from .device import Device

            device = Device(udid)
            return device.info()

        if udids is None:
            # 获取所有设备的信息
            return self.execute_on_all_devices(
                get_info_task, max_workers=max_workers, timeout=timeout
            )
        else:
            # 获取指定设备的信息
            return self.execute_on_devices(
                udids, get_info_task, max_workers=max_workers, timeout=timeout
            )

    def batch_screenshot(
        self,
        udids: List[str],
        output_dir: str = ".",
        max_workers: int = None,
        timeout: float = None,
    ) -> Dict[str, str]:
        """批量截取设备屏幕截图"""
        import os

        os.makedirs(output_dir, exist_ok=True)

        def screenshot_task(udid):
            from .device import Device

            device = Device(udid)
            output_path = os.path.join(output_dir, f"screenshot_{udid[:8]}.png")
            success = device.take_screenshot(output_path)
            return output_path if success else None

        return self.execute_on_devices(
            udids, screenshot_task, max_workers=max_workers, timeout=timeout
        )
