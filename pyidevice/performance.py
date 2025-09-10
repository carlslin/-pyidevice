"""性能监控模块"""

import time
import psutil
import logging
from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager
from .types import DeviceOperationResult

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.operation_times = []

    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.metrics = {
            "cpu_percent": [],
            "memory_percent": [],
            "operation_count": 0,
            "total_operations": 0,
        }
        logger.info("性能监控已启动")

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控并返回统计信息"""
        if not self.start_time:
            return {}

        duration = time.time() - self.start_time
        stats = {
            "duration": duration,
            "avg_cpu": (
                sum(self.metrics["cpu_percent"]) / len(self.metrics["cpu_percent"])
                if self.metrics["cpu_percent"]
                else 0
            ),
            "max_cpu": max(self.metrics["cpu_percent"]) if self.metrics["cpu_percent"] else 0,
            "avg_memory": (
                sum(self.metrics["memory_percent"]) / len(self.metrics["memory_percent"])
                if self.metrics["memory_percent"]
                else 0
            ),
            "max_memory": (
                max(self.metrics["memory_percent"]) if self.metrics["memory_percent"] else 0
            ),
            "operation_count": self.metrics["operation_count"],
            "avg_operation_time": (
                sum(self.operation_times) / len(self.operation_times) if self.operation_times else 0
            ),
            "total_operations": self.metrics["total_operations"],
        }

        logger.info(f"性能监控结束: {stats}")
        return stats

    def record_operation(self, operation_time: float):
        """记录操作时间"""
        self.operation_times.append(operation_time)
        self.metrics["operation_count"] += 1
        self.metrics["total_operations"] += 1

    def record_system_metrics(self):
        """记录系统指标"""
        self.metrics["cpu_percent"].append(psutil.cpu_percent())
        self.metrics["memory_percent"].append(psutil.virtual_memory().percent)


def monitor_performance(func: Callable) -> Callable:
    """性能监控装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            operation_time = time.time() - start_time
            logger.debug(f"{func.__name__} 执行时间: {operation_time:.3f}秒")

    return wrapper


@contextmanager
def performance_context(operation_name: str):
    """性能监控上下文管理器"""
    start_time = time.time()
    logger.debug(f"开始执行: {operation_name}")
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation_name} 完成，耗时: {duration:.3f}秒")


class DevicePerformanceTracker:
    """设备性能跟踪器"""

    def __init__(self):
        self.device_metrics = {}

    def track_device_operation(self, udid: str, operation: str, duration: float, success: bool):
        """跟踪设备操作"""
        if udid not in self.device_metrics:
            self.device_metrics[udid] = {
                "operations": [],
                "total_time": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        metrics = self.device_metrics[udid]
        metrics["operations"].append(
            {
                "operation": operation,
                "duration": duration,
                "success": success,
                "timestamp": time.time(),
            }
        )

        metrics["total_time"] += duration
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1

    def get_device_stats(self, udid: str) -> Dict[str, Any]:
        """获取设备统计信息"""
        if udid not in self.device_metrics:
            return {}

        metrics = self.device_metrics[udid]
        total_ops = metrics["success_count"] + metrics["failure_count"]

        return {
            "total_operations": total_ops,
            "success_rate": metrics["success_count"] / total_ops if total_ops > 0 else 0,
            "avg_operation_time": metrics["total_time"] / total_ops if total_ops > 0 else 0,
            "total_time": metrics["total_time"],
            "recent_operations": metrics["operations"][-10:],  # 最近10次操作
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有设备统计信息"""
        return {udid: self.get_device_stats(udid) for udid in self.device_metrics}


# 全局性能跟踪器实例
performance_tracker = DevicePerformanceTracker()


def track_device_operation(udid: str, operation: str):
    """设备操作跟踪装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"设备操作失败 {operation}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_tracker.track_device_operation(udid, operation, duration, success)

        return wrapper

    return decorator


class ResourceMonitor:
    """资源监控器"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss
        self.start_cpu = self.process.cpu_percent()

    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent(),
        }

    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        return self.process.cpu_percent()

    def get_resource_summary(self) -> Dict[str, Any]:
        """获取资源使用摘要"""
        return {
            "memory": self.get_memory_usage(),
            "cpu_percent": self.get_cpu_usage(),
            "threads": self.process.num_threads(),
            "open_files": len(self.process.open_files()),
        }


def optimize_memory_usage():
    """内存使用优化建议"""
    import gc

    # 强制垃圾回收
    collected = gc.collect()
    logger.info(f"垃圾回收完成，释放了 {collected} 个对象")

    # 获取当前内存使用情况
    monitor = ResourceMonitor()
    memory_info = monitor.get_memory_usage()

    if memory_info["percent"] > 80:
        logger.warning(f"内存使用率过高: {memory_info['percent']:.1f}%")
        return {
            "status": "warning",
            "message": "内存使用率过高，建议减少并发操作或重启程序",
            "memory_percent": memory_info["percent"],
        }

    return {"status": "ok", "message": "内存使用正常", "memory_percent": memory_info["percent"]}
