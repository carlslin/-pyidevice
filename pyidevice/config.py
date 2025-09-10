"""配置管理模块"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        self.config_file = config_file or self._get_default_config_path()
        self._config = self._load_default_config()
        self._load_config()

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        home_dir = Path.home()
        config_dir = home_dir / ".pyidevice"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "timeouts": {
                "device_command": 30,  # 设备命令超时时间（秒）
                "idb_connection": 10,  # IDB连接超时时间（秒）
                "screenshot": 15,  # 截图超时时间（秒）
                "app_launch": 20,  # 应用启动超时时间（秒）
            },
            "idb": {
                "default_port": 8080,  # 默认IDB端口
                "retry_count": 3,  # 连接重试次数
                "retry_interval": 2.0,  # 重试间隔（秒）
            },
            "concurrent": {
                "max_workers": 4,  # 默认最大工作线程数
                "executor_type": "thread",  # 默认执行器类型
            },
            "logging": {
                "level": "INFO",  # 日志级别
                "file": None,  # 日志文件路径，None表示不写入文件
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "paths": {
                "screenshots": "./screenshots",  # 默认截图保存路径
                "logs": "./logs",  # 默认日志保存路径
            },
        }

    def _load_config(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    self._merge_config(self._config, user_config)
                logger.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")
                logger.info("Using default configuration")
        else:
            logger.info("No config file found, using default configuration")
            self.save_config()  # 保存默认配置到文件

    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]):
        """递归合并配置"""
        for key, value in user.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'timeouts.device_command'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split(".")
        config = self._config

        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Config saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")

    def get_timeout(self, operation: str) -> int:
        """获取指定操作的超时时间"""
        return self.get(f"timeouts.{operation}", 30)

    def get_idb_config(self) -> Dict[str, Any]:
        """获取IDB配置"""
        return self.get("idb", {})

    def get_concurrent_config(self) -> Dict[str, Any]:
        """获取并发配置"""
        return self.get("concurrent", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config
