"""
pyidevice 稳定性增强模块

这个模块提供了各种稳定性增强功能，包括：
- 智能重试机制
- 连接池管理
- 健康检查
- 熔断器模式
- 超时处理
- 输入验证
- 资源管理

主要类：
- RetryManager: 智能重试管理器
- ConnectionPool: 连接池管理器
- HealthChecker: 健康检查器
- CircuitBreaker: 熔断器
- TimeoutManager: 超时管理器
- InputValidator: 输入验证器
- ResourceManager: 资源管理器

技术特性：
- 指数退避重试策略
- 连接池复用和自动清理
- 实时健康状态监控
- 自动熔断和恢复机制
- 智能超时调整
- 严格的输入验证
- 资源自动释放

使用示例：
    >>> from pyidevice.stability import RetryManager, ConnectionPool
    >>> retry_manager = RetryManager(max_retries=3, backoff_factor=2.0)
    >>> connection_pool = ConnectionPool(max_connections=10)
    >>> 
    >>> # 使用重试机制
    >>> result = retry_manager.execute(risky_operation, args, kwargs)
    >>> 
    >>> # 使用连接池
    >>> with connection_pool.get_connection() as conn:
    ...     result = conn.perform_operation()

依赖：
- asyncio: 异步操作支持
- threading: 线程安全支持
- time: 时间相关功能
- typing: 类型注解支持
- logging: 日志记录
- functools: 函数工具
- contextlib: 上下文管理
"""

import asyncio
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Tuple, Type
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
import weakref
import gc

# 配置日志记录器
logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略枚举"""
    FIXED = "fixed"  # 固定间隔重试
    EXPONENTIAL = "exponential"  # 指数退避重试
    LINEAR = "linear"  # 线性增长重试
    CUSTOM = "custom"  # 自定义重试


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True  # 是否添加随机抖动
    exceptions: Tuple[Type[Exception], ...] = (Exception,)


class RetryManager:
    """
    智能重试管理器
    
    提供多种重试策略和智能重试机制，支持：
    - 指数退避重试
    - 固定间隔重试
    - 线性增长重试
    - 自定义重试策略
    - 随机抖动避免雷群效应
    - 异常类型过滤
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        初始化重试管理器
        
        Args:
            config: 重试配置，如果为None则使用默认配置
        """
        self.config = config or RetryConfig()
        self._retry_stats = {}  # 重试统计信息
        
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            最后一次重试的异常
        """
        func_name = getattr(func, '__name__', str(func))
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # 记录成功统计
                if func_name not in self._retry_stats:
                    self._retry_stats[func_name] = {'success': 0, 'failure': 0, 'retries': 0}
                self._retry_stats[func_name]['success'] += 1
                
                return result
                
            except self.config.exceptions as e:
                last_exception = e
                
                # 记录失败统计
                if func_name not in self._retry_stats:
                    self._retry_stats[func_name] = {'success': 0, 'failure': 0, 'retries': 0}
                self._retry_stats[func_name]['failure'] += 1
                
                if attempt < self.config.max_retries:
                    # 计算重试延迟
                    delay = self._calculate_delay(attempt)
                    
                    logger.warning(
                        f"尝试 {attempt + 1}/{self.config.max_retries + 1} 失败: {func_name} - {e}. "
                        f"将在 {delay:.2f}s 后重试..."
                    )
                    
                    time.sleep(delay)
                    self._retry_stats[func_name]['retries'] += 1
                else:
                    logger.error(f"所有 {self.config.max_retries + 1} 次尝试都失败了: {func_name}")
                    break
        
        # 所有重试都失败了
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数（从0开始）
            
        Returns:
            延迟时间（秒）
        """
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * (attempt + 1)
        else:  # CUSTOM
            delay = self.config.base_delay
        
        # 限制最大延迟
        delay = min(delay, self.config.max_delay)
        
        # 添加随机抖动
        if self.config.jitter:
            import random
            jitter = random.uniform(0.1, 0.3) * delay
            delay += jitter
        
        return delay
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        获取重试统计信息
        
        Returns:
            重试统计信息字典
        """
        return self._retry_stats.copy()
    
    def reset_stats(self):
        """重置重试统计信息"""
        self._retry_stats.clear()


@dataclass
class ConnectionInfo:
    """连接信息"""
    id: str
    created_at: float
    last_used: float
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectionPool:
    """
    连接池管理器
    
    提供连接复用、自动清理和负载均衡功能：
    - 连接复用减少创建开销
    - 自动清理过期连接
    - 负载均衡分配连接
    - 连接健康检查
    - 线程安全操作
    """
    
    def __init__(
        self,
        max_connections: int = 10,
        connection_timeout: float = 30.0,
        idle_timeout: float = 300.0,
        cleanup_interval: float = 60.0
    ):
        """
        初始化连接池
        
        Args:
            max_connections: 最大连接数
            connection_timeout: 连接超时时间（秒）
            idle_timeout: 空闲超时时间（秒）
            cleanup_interval: 清理间隔时间（秒）
        """
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.cleanup_interval = cleanup_interval
        
        self._connections: Dict[str, ConnectionInfo] = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        
        # 启动清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动清理线程"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name="ConnectionPool-Cleanup"
            )
            self._cleanup_thread.start()
    
    def _cleanup_worker(self):
        """清理工作线程"""
        while not self._stop_cleanup.wait(self.cleanup_interval):
            try:
                self._cleanup_expired_connections()
            except Exception as e:
                logger.error(f"连接池清理过程中发生错误: {e}")
    
    def _cleanup_expired_connections(self):
        """清理过期连接"""
        current_time = time.time()
        expired_connections = []
        
        with self._lock:
            for conn_id, conn_info in self._connections.items():
                if (current_time - conn_info.last_used) > self.idle_timeout:
                    expired_connections.append(conn_id)
        
        # 清理过期连接
        for conn_id in expired_connections:
            self._remove_connection(conn_id)
            logger.info(f"清理过期连接: {conn_id}")
    
    def _remove_connection(self, conn_id: str):
        """移除连接"""
        with self._lock:
            if conn_id in self._connections:
                del self._connections[conn_id]
    
    def get_connection(self, connection_factory: Optional[Callable] = None) -> 'ConnectionContext':
        """
        获取连接上下文管理器
        
        Args:
            connection_factory: 连接工厂函数
            
        Returns:
            连接上下文管理器
        """
        return ConnectionContext(self, connection_factory)
    
    def _acquire_connection(self, connection_factory: Optional[Callable] = None) -> str:
        """
        获取连接ID
        
        Args:
            connection_factory: 连接工厂函数
            
        Returns:
            连接ID
        """
        with self._lock:
            # 检查是否有可用连接
            for conn_id, conn_info in self._connections.items():
                if conn_info.is_active:
                    conn_info.last_used = time.time()
                    return conn_id
            
            # 创建新连接
            if len(self._connections) < self.max_connections:
                conn_id = f"conn_{int(time.time() * 1000)}_{id(self)}"
                conn_info = ConnectionInfo(
                    id=conn_id,
                    created_at=time.time(),
                    last_used=time.time()
                )
                self._connections[conn_id] = conn_info
                return conn_id
            
            # 连接池已满，等待或抛出异常
            raise RuntimeError(f"连接池已满，最大连接数: {self.max_connections}")
    
    def _release_connection(self, conn_id: str):
        """
        释放连接
        
        Args:
            conn_id: 连接ID
        """
        with self._lock:
            if conn_id in self._connections:
                self._connections[conn_id].last_used = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            连接池统计信息
        """
        with self._lock:
            active_connections = sum(1 for conn in self._connections.values() if conn.is_active)
            return {
                'total_connections': len(self._connections),
                'active_connections': active_connections,
                'max_connections': self.max_connections,
                'utilization': active_connections / self.max_connections if self.max_connections > 0 else 0
            }
    
    def close(self):
        """关闭连接池"""
        self._stop_cleanup.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)
        
        with self._lock:
            self._connections.clear()


class ConnectionContext:
    """连接上下文管理器"""
    
    def __init__(self, pool: ConnectionPool, connection_factory: Optional[Callable] = None):
        self.pool = pool
        self.connection_factory = connection_factory
        self.conn_id: Optional[str] = None
    
    def __enter__(self) -> str:
        """进入上下文"""
        self.conn_id = self.pool._acquire_connection(self.connection_factory)
        return self.conn_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.conn_id:
            self.pool._release_connection(self.conn_id)


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """健康检查配置"""
    name: str
    check_func: Callable[[], bool]
    timeout: float = 5.0
    interval: float = 30.0
    failure_threshold: int = 3
    recovery_threshold: int = 2


class HealthChecker:
    """
    健康检查器
    
    提供实时健康状态监控功能：
    - 多种健康检查策略
    - 自动故障检测和恢复
    - 健康状态历史记录
    - 告警和通知机制
    """
    
    def __init__(self):
        self._checks: Dict[str, HealthCheck] = {}
        self._status_history: List[Tuple[float, str, HealthStatus]] = []
        self._current_status = HealthStatus.UNKNOWN
        self._failure_counts: Dict[str, int] = {}
        self._recovery_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def add_check(self, check: HealthCheck):
        """
        添加健康检查
        
        Args:
            check: 健康检查配置
        """
        with self._lock:
            self._checks[check.name] = check
            self._failure_counts[check.name] = 0
            self._recovery_counts[check.name] = 0
    
    def remove_check(self, name: str):
        """
        移除健康检查
        
        Args:
            name: 检查名称
        """
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                del self._failure_counts[name]
                del self._recovery_counts[name]
    
    def check_health(self) -> HealthStatus:
        """
        执行健康检查
        
        Returns:
            当前健康状态
        """
        with self._lock:
            if not self._checks:
                self._current_status = HealthStatus.UNKNOWN
                return self._current_status
            
            healthy_checks = 0
            total_checks = len(self._checks)
            
            for name, check in self._checks.items():
                try:
                    # 执行健康检查
                    result = self._execute_check(check)
                    
                    if result:
                        # 检查成功
                        self._failure_counts[name] = 0
                        self._recovery_counts[name] += 1
                        healthy_checks += 1
                    else:
                        # 检查失败
                        self._failure_counts[name] += 1
                        self._recovery_counts[name] = 0
                        
                except Exception as e:
                    logger.error(f"健康检查失败: {name} - {e}")
                    self._failure_counts[name] += 1
                    self._recovery_counts[name] = 0
            
            # 确定整体健康状态
            health_ratio = healthy_checks / total_checks
            
            if health_ratio >= 0.9:
                self._current_status = HealthStatus.HEALTHY
            elif health_ratio >= 0.5:
                self._current_status = HealthStatus.DEGRADED
            else:
                self._current_status = HealthStatus.UNHEALTHY
            
            # 记录状态历史
            self._status_history.append((time.time(), "overall", self._current_status))
            
            # 限制历史记录长度
            if len(self._status_history) > 1000:
                self._status_history = self._status_history[-500:]
            
            return self._current_status
    
    def _execute_check(self, check: HealthCheck) -> bool:
        """
        执行单个健康检查
        
        Args:
            check: 健康检查配置
            
        Returns:
            检查结果
        """
        try:
            # 使用超时执行检查
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"健康检查超时: {check.name}")
            
            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(check.timeout))
            
            try:
                result = check.check_func()
                return bool(result)
            finally:
                # 恢复原信号处理器
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                
        except Exception as e:
            logger.error(f"健康检查执行异常: {check.name} - {e}")
            return False
    
    def get_status(self) -> HealthStatus:
        """
        获取当前健康状态
        
        Returns:
            当前健康状态
        """
        with self._lock:
            return self._current_status
    
    def get_status_history(self, limit: int = 100) -> List[Tuple[float, str, HealthStatus]]:
        """
        获取健康状态历史
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            健康状态历史记录
        """
        with self._lock:
            return self._status_history[-limit:] if limit > 0 else self._status_history.copy()
    
    def get_check_stats(self) -> Dict[str, Dict[str, int]]:
        """
        获取检查统计信息
        
        Returns:
            检查统计信息
        """
        with self._lock:
            return {
                name: {
                    'failures': self._failure_counts.get(name, 0),
                    'recoveries': self._recovery_counts.get(name, 0)
                }
                for name in self._checks.keys()
            }


class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"  # 正常状态
    OPEN = "open"  # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态


class CircuitBreaker:
    """
    熔断器
    
    提供自动熔断和恢复机制：
    - 故障检测和自动熔断
    - 半开状态测试
    - 自动恢复机制
    - 熔断统计和监控
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间（秒）
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._success_count = 0
        self._lock = threading.RLock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用函数
        
        Args:
            func: 要调用的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            熔断器异常或函数异常
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time > self.recovery_timeout:
                    # 进入半开状态
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("熔断器进入半开状态，开始测试恢复")
                else:
                    # 熔断器仍然打开
                    raise RuntimeError("熔断器处于打开状态，拒绝调用")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 执行成功
                self._on_success()
                return result
                
            except self.expected_exception as e:
                # 执行失败
                self._on_failure()
                raise e
    
    def _on_success(self):
        """处理成功情况"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= 2:  # 连续成功2次才关闭熔断器
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("熔断器关闭，服务恢复正常")
            else:
                # 正常状态，重置失败计数
                self._failure_count = 0
    
    def _on_failure(self):
        """处理失败情况"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"熔断器打开，失败次数: {self._failure_count}")
    
    def get_state(self) -> CircuitState:
        """
        获取熔断器状态
        
        Returns:
            熔断器状态
        """
        with self._lock:
            return self._state
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取熔断器统计信息
        
        Returns:
            熔断器统计信息
        """
        with self._lock:
            return {
                'state': self._state.value,
                'failure_count': self._failure_count,
                'success_count': self._success_count,
                'last_failure_time': self._last_failure_time
            }
    
    def reset(self):
        """重置熔断器"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = 0


class TimeoutManager:
    """
    超时管理器
    
    提供智能超时处理功能：
    - 动态超时调整
    - 超时统计和分析
    - 超时预警机制
    - 自适应超时策略
    """
    
    def __init__(self, default_timeout: float = 30.0):
        """
        初始化超时管理器
        
        Args:
            default_timeout: 默认超时时间（秒）
        """
        self.default_timeout = default_timeout
        self._timeout_stats: Dict[str, List[float]] = {}
        self._lock = threading.RLock()
    
    def with_timeout(self, timeout: Optional[float] = None):
        """
        超时装饰器
        
        Args:
            timeout: 超时时间，如果为None则使用默认值
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                actual_timeout = timeout or self.default_timeout
                func_name = getattr(func, '__name__', str(func))
                
                start_time = time.time()
                try:
                    # 使用信号实现超时
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError(f"操作超时: {func_name} ({actual_timeout}s)")
                    
                    # 设置超时信号
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(actual_timeout))
                    
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        # 恢复原信号处理器
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                        
                except TimeoutError:
                    logger.error(f"操作超时: {func_name} ({actual_timeout}s)")
                    raise
                finally:
                    # 记录执行时间
                    execution_time = time.time() - start_time
                    self._record_execution_time(func_name, execution_time)
                
            return wrapper
        return decorator
    
    def _record_execution_time(self, func_name: str, execution_time: float):
        """
        记录执行时间
        
        Args:
            func_name: 函数名称
            execution_time: 执行时间
        """
        with self._lock:
            if func_name not in self._timeout_stats:
                self._timeout_stats[func_name] = []
            
            self._timeout_stats[func_name].append(execution_time)
            
            # 限制统计记录数量
            if len(self._timeout_stats[func_name]) > 100:
                self._timeout_stats[func_name] = self._timeout_stats[func_name][-50:]
    
    def get_suggested_timeout(self, func_name: str) -> float:
        """
        获取建议的超时时间
        
        Args:
            func_name: 函数名称
            
        Returns:
            建议的超时时间
        """
        with self._lock:
            if func_name not in self._timeout_stats:
                return self.default_timeout
            
            times = self._timeout_stats[func_name]
            if not times:
                return self.default_timeout
            
            # 计算平均执行时间
            avg_time = sum(times) / len(times)
            
            # 建议超时时间为平均时间的3倍，但不超过默认超时的2倍
            suggested = min(avg_time * 3, self.default_timeout * 2)
            return max(suggested, 1.0)  # 至少1秒
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """
        获取超时统计信息
        
        Returns:
            超时统计信息
        """
        with self._lock:
            stats = {}
            for func_name, times in self._timeout_stats.items():
                if times:
                    stats[func_name] = {
                        'avg_time': sum(times) / len(times),
                        'max_time': max(times),
                        'min_time': min(times),
                        'count': len(times),
                        'suggested_timeout': self.get_suggested_timeout(func_name)
                    }
            return stats


class InputValidator:
    """
    输入验证器
    
    提供严格的输入验证功能：
    - 类型检查
    - 范围验证
    - 格式验证
    - 自定义验证规则
    """
    
    @staticmethod
    def validate_udid(udid: str) -> bool:
        """
        验证UDID格式
        
        Args:
            udid: 设备UDID
            
        Returns:
            是否有效
        """
        if not isinstance(udid, str):
            return False
        
        # UDID应该是40位十六进制字符串
        if len(udid) != 40:
            return False
        
        try:
            int(udid, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """
        验证端口号
        
        Args:
            port: 端口号
            
        Returns:
            是否有效
        """
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_timeout(timeout: Union[int, float]) -> bool:
        """
        验证超时时间
        
        Args:
            timeout: 超时时间
            
        Returns:
            是否有效
        """
        try:
            timeout_num = float(timeout)
            return timeout_num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_bundle_id(bundle_id: str) -> bool:
        """
        验证Bundle ID格式
        
        Args:
            bundle_id: 应用包ID
            
        Returns:
            是否有效
        """
        if not isinstance(bundle_id, str):
            return False
        
        # Bundle ID应该符合反向域名格式
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, bundle_id))


class ResourceManager:
    """
    资源管理器
    
    提供资源自动管理和清理功能：
    - 资源注册和跟踪
    - 自动清理机制
    - 资源使用统计
    - 内存泄漏检测
    """
    
    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._resource_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def register_resource(self, name: str, resource: Any, cleanup_func: Optional[Callable] = None):
        """
        注册资源
        
        Args:
            name: 资源名称
            resource: 资源对象
            cleanup_func: 清理函数
        """
        with self._lock:
            self._resources[name] = resource
            self._resource_metadata[name] = {
                'created_at': time.time(),
                'cleanup_func': cleanup_func,
                'ref_count': 0
            }
    
    def unregister_resource(self, name: str):
        """
        注销资源
        
        Args:
            name: 资源名称
        """
        with self._lock:
            if name in self._resources:
                # 执行清理
                metadata = self._resource_metadata.get(name, {})
                cleanup_func = metadata.get('cleanup_func')
                if cleanup_func:
                    try:
                        cleanup_func(self._resources[name])
                    except Exception as e:
                        logger.error(f"资源清理失败: {name} - {e}")
                
                # 移除资源
                del self._resources[name]
                del self._resource_metadata[name]
    
    def get_resource(self, name: str) -> Optional[Any]:
        """
        获取资源
        
        Args:
            name: 资源名称
            
        Returns:
            资源对象
        """
        with self._lock:
            if name in self._resources:
                self._resource_metadata[name]['ref_count'] += 1
                return self._resources[name]
            return None
    
    def release_resource(self, name: str):
        """
        释放资源引用
        
        Args:
            name: 资源名称
        """
        with self._lock:
            if name in self._resource_metadata:
                self._resource_metadata[name]['ref_count'] = max(0, 
                    self._resource_metadata[name]['ref_count'] - 1)
    
    def cleanup_unused_resources(self, max_age: float = 3600.0):
        """
        清理未使用的资源
        
        Args:
            max_age: 最大存活时间（秒）
        """
        current_time = time.time()
        unused_resources = []
        
        with self._lock:
            for name, metadata in self._resource_metadata.items():
                if (metadata['ref_count'] == 0 and 
                    current_time - metadata['created_at'] > max_age):
                    unused_resources.append(name)
        
        # 清理未使用的资源
        for name in unused_resources:
            self.unregister_resource(name)
            logger.info(f"清理未使用的资源: {name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取资源统计信息
        
        Returns:
            资源统计信息
        """
        with self._lock:
            total_resources = len(self._resources)
            total_refs = sum(meta['ref_count'] for meta in self._resource_metadata.values())
            
            return {
                'total_resources': total_resources,
                'total_references': total_refs,
                'resources': {
                    name: {
                        'ref_count': meta['ref_count'],
                        'age': time.time() - meta['created_at']
                    }
                    for name, meta in self._resource_metadata.items()
                }
            }


# 全局稳定性管理器实例
_retry_manager = RetryManager()
_connection_pool = ConnectionPool()
_health_checker = HealthChecker()
_circuit_breaker = CircuitBreaker()
_timeout_manager = TimeoutManager()
_input_validator = InputValidator()
_resource_manager = ResourceManager()


def get_retry_manager() -> RetryManager:
    """获取全局重试管理器"""
    return _retry_manager


def get_connection_pool() -> ConnectionPool:
    """获取全局连接池"""
    return _connection_pool


def get_health_checker() -> HealthChecker:
    """获取全局健康检查器"""
    return _health_checker


def get_circuit_breaker() -> CircuitBreaker:
    """获取全局熔断器"""
    return _circuit_breaker


def get_timeout_manager() -> TimeoutManager:
    """获取全局超时管理器"""
    return _timeout_manager


def get_input_validator() -> InputValidator:
    """获取全局输入验证器"""
    return _input_validator


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器"""
    return _resource_manager


# 便捷装饰器
def with_retry(config: Optional[RetryConfig] = None):
    """重试装饰器"""
    retry_manager = RetryManager(config) if config else _retry_manager
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_manager.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def with_timeout(timeout: Optional[float] = None):
    """超时装饰器"""
    return _timeout_manager.with_timeout(timeout)


def with_circuit_breaker(circuit_breaker: Optional[CircuitBreaker] = None):
    """熔断器装饰器"""
    cb = circuit_breaker or _circuit_breaker
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


def validate_input(**validators):
    """输入验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 验证参数
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    if not validator(kwargs[param_name]):
                        raise ValueError(f"参数验证失败: {param_name}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
