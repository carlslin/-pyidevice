"""缓存管理模块"""

import time
import json
import hashlib
import logging
from typing import Any, Dict, Optional, Callable, Union, List
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 300):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            default_ttl: 默认缓存时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache = {}

    def _get_cache_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 缓存时间（秒），None使用默认值

        Returns:
            是否设置成功
        """
        try:
            ttl = ttl or self.default_ttl
            cache_data = {"value": value, "timestamp": time.time(), "ttl": ttl}

            # 内存缓存
            self.memory_cache[key] = cache_data

            # 文件缓存
            cache_path = self._get_cache_path(key)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"缓存已设置: {key}")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        try:
            # 先检查内存缓存
            if key in self.memory_cache:
                cache_data = self.memory_cache[key]
                if self._is_valid(cache_data):
                    logger.debug(f"从内存缓存获取: {key}")
                    return cache_data["value"]
                else:
                    del self.memory_cache[key]

            # 检查文件缓存
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                if self._is_valid(cache_data):
                    # 更新内存缓存
                    self.memory_cache[key] = cache_data
                    logger.debug(f"从文件缓存获取: {key}")
                    return cache_data["value"]
                else:
                    # 删除过期缓存
                    cache_path.unlink()

            return None
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None

    def _is_valid(self, cache_data: Dict[str, Any]) -> bool:
        """检查缓存是否有效"""
        if not cache_data:
            return False

        timestamp = cache_data.get("timestamp", 0)
        ttl = cache_data.get("ttl", 0)

        return time.time() - timestamp < ttl

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]

            # 删除文件缓存
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()

            logger.debug(f"缓存已删除: {key}")
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False

    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            # 清空内存缓存
            self.memory_cache.clear()

            # 清空文件缓存
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()

            logger.info("所有缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        cleaned_count = 0

        try:
            # 清理内存缓存
            expired_keys = []
            for key, cache_data in self.memory_cache.items():
                if not self._is_valid(cache_data):
                    expired_keys.append(key)

            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1

            # 清理文件缓存
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)

                    if not self._is_valid(cache_data):
                        cache_file.unlink()
                        cleaned_count += 1
                except Exception:
                    # 如果文件损坏，直接删除
                    cache_file.unlink()
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期缓存")

        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")

        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        memory_count = len(self.memory_cache)
        file_count = len(list(self.cache_dir.glob("*.json")))

        return {
            "memory_cache_count": memory_count,
            "file_cache_count": file_count,
            "total_count": memory_count + file_count,
            "cache_dir": str(self.cache_dir),
            "default_ttl": self.default_ttl,
        }


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    缓存装饰器

    Args:
        ttl: 缓存时间（秒）
        key_func: 自定义缓存键生成函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成：函数名 + 参数
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {func.__name__}")
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


class DeviceCache:
    """设备缓存管理器"""

    def __init__(self, ttl: int = 30):
        """
        初始化设备缓存

        Args:
            ttl: 设备信息缓存时间（秒）
        """
        self.ttl = ttl
        self.cache = CacheManager(cache_dir=".device_cache", default_ttl=ttl)

    def get_device_info(self, udid: str) -> Optional[Dict[str, Any]]:
        """获取缓存的设备信息"""
        return self.cache.get(f"device_info:{udid}")

    def set_device_info(self, udid: str, info: Dict[str, Any]) -> bool:
        """设置设备信息缓存"""
        return self.cache.set(f"device_info:{udid}", info, self.ttl)

    def get_device_list(self) -> Optional[List[str]]:
        """获取缓存的设备列表"""
        return self.cache.get("device_list")

    def set_device_list(self, devices: List[str]) -> bool:
        """设置设备列表缓存"""
        return self.cache.set("device_list", devices, 10)  # 设备列表缓存10秒

    def invalidate_device(self, udid: str) -> bool:
        """使设备缓存失效"""
        return self.cache.delete(f"device_info:{udid}")

    def invalidate_all(self) -> bool:
        """使所有设备缓存失效"""
        return self.cache.clear()


# 全局设备缓存实例
device_cache = DeviceCache()


def cache_device_info(ttl: int = 30):
    """设备信息缓存装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(udid: str, *args, **kwargs) -> Any:
            # 尝试从缓存获取
            cached_info = device_cache.get_device_info(udid)
            if cached_info is not None:
                logger.debug(f"设备信息缓存命中: {udid}")
                return cached_info

            # 执行函数并缓存结果
            result = func(udid, *args, **kwargs)
            if isinstance(result, dict):
                device_cache.set_device_info(udid, result)

            return result

        return wrapper

    return decorator
