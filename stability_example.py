#!/usr/bin/env python3
"""
pyidevice 稳定性功能使用示例

这个示例展示了如何使用pyidevice的稳定性增强功能：
- 智能重试机制
- 连接池管理
- 健康检查
- 熔断器模式
- 超时处理
- 输入验证
- 资源管理

运行示例：
    python3 stability_example.py
"""

import time
import random
import logging
from pyidevice import (
    Device,
    DeviceManager,
    RetryManager,
    ConnectionPool,
    HealthChecker,
    CircuitBreaker,
    TimeoutManager,
    InputValidator,
    ResourceManager,
    with_retry,
    with_timeout,
    with_circuit_breaker,
    validate_input,
    RetryConfig,
    RetryStrategy,
    HealthCheck,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_retry_manager():
    """演示重试管理器功能"""
    print("\n=== 重试管理器演示 ===")
    
    # 创建重试管理器
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=0.5,
        backoff_factor=2.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=True
    )
    retry_manager = RetryManager(retry_config)
    
    # 模拟不稳定的操作
    def unstable_operation():
        if random.random() < 0.7:  # 70%的失败率
            raise RuntimeError("操作失败")
        return "操作成功"
    
    # 使用重试管理器执行操作
    try:
        result = retry_manager.execute(unstable_operation)
        print(f"重试结果: {result}")
    except RuntimeError as e:
        print(f"重试失败: {e}")
    
    # 显示重试统计
    stats = retry_manager.get_stats()
    print(f"重试统计: {stats}")


def demo_connection_pool():
    """演示连接池功能"""
    print("\n=== 连接池演示 ===")
    
    # 创建连接池
    pool = ConnectionPool(
        max_connections=3,
        connection_timeout=10.0,
        idle_timeout=30.0,
        cleanup_interval=10.0
    )
    
    # 模拟连接操作
    def simulate_connection_work(conn_id):
        print(f"使用连接 {conn_id} 执行操作")
        time.sleep(0.1)
        return f"连接 {conn_id} 操作完成"
    
    # 并发使用连接
    results = []
    for i in range(5):
        with pool.get_connection() as conn_id:
            result = simulate_connection_work(conn_id)
            results.append(result)
    
    print(f"连接池操作结果: {results}")
    
    # 显示连接池统计
    stats = pool.get_stats()
    print(f"连接池统计: {stats}")
    
    # 清理连接池
    pool.close()


def demo_health_checker():
    """演示健康检查器功能"""
    print("\n=== 健康检查器演示 ===")
    
    # 创建健康检查器
    checker = HealthChecker()
    
    # 添加健康检查
    def device_connectivity_check():
        """模拟设备连接检查"""
        return random.random() > 0.3  # 70%的健康率
    
    def service_availability_check():
        """模拟服务可用性检查"""
        return random.random() > 0.2  # 80%的健康率
    
    def memory_usage_check():
        """模拟内存使用检查"""
        return random.random() > 0.1  # 90%的健康率
    
    # 注册健康检查
    checker.add_check(HealthCheck("设备连接", device_connectivity_check, timeout=2.0))
    checker.add_check(HealthCheck("服务可用性", service_availability_check, timeout=1.0))
    checker.add_check(HealthCheck("内存使用", memory_usage_check, timeout=1.0))
    
    # 执行多次健康检查
    for i in range(3):
        status = checker.check_health()
        print(f"健康检查 {i+1}: {status.value}")
        
        # 显示检查统计
        stats = checker.get_check_stats()
        print(f"检查统计: {stats}")
        
        time.sleep(1)


def demo_circuit_breaker():
    """演示熔断器功能"""
    print("\n=== 熔断器演示 ===")
    
    # 创建熔断器
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2.0,
        expected_exception=RuntimeError
    )
    
    # 模拟不稳定的服务
    def unstable_service():
        if random.random() < 0.8:  # 80%的失败率
            raise RuntimeError("服务不可用")
        return "服务正常"
    
    # 测试熔断器
    for i in range(8):
        try:
            result = breaker.call(unstable_service)
            print(f"调用 {i+1}: {result}")
        except RuntimeError as e:
            print(f"调用 {i+1}: {e}")
        
        # 显示熔断器状态
        state = breaker.get_state()
        print(f"熔断器状态: {state.value}")
        
        time.sleep(0.5)


def demo_timeout_manager():
    """演示超时管理器功能"""
    print("\n=== 超时管理器演示 ===")
    
    # 创建超时管理器
    timeout_manager = TimeoutManager(default_timeout=1.0)
    
    # 快速操作
    @timeout_manager.with_timeout(0.5)
    def fast_operation():
        time.sleep(0.1)
        return "快速操作完成"
    
    # 慢速操作
    @timeout_manager.with_timeout(0.5)
    def slow_operation():
        time.sleep(1.0)
        return "慢速操作完成"
    
    # 测试快速操作
    try:
        result = fast_operation()
        print(f"快速操作: {result}")
    except TimeoutError as e:
        print(f"快速操作超时: {e}")
    
    # 测试慢速操作
    try:
        result = slow_operation()
        print(f"慢速操作: {result}")
    except TimeoutError as e:
        print(f"慢速操作超时: {e}")
    
    # 显示超时统计
    stats = timeout_manager.get_stats()
    print(f"超时统计: {stats}")


def demo_input_validator():
    """演示输入验证器功能"""
    print("\n=== 输入验证器演示 ===")
    
    # 创建输入验证器
    validator = InputValidator()
    
    # 测试UDID验证
    test_udids = [
        "00008020" + "0" * 32,  # 有效UDID
        "invalid_udid",         # 无效UDID
        "123",                  # 太短
        "x" * 41,              # 太长
    ]
    
    print("UDID验证测试:")
    for udid in test_udids:
        is_valid = validator.validate_udid(udid)
        print(f"  {udid[:20]}... : {'✓' if is_valid else '✗'}")
    
    # 测试端口验证
    test_ports = [8080, 3000, 65535, 0, 99999, "invalid"]
    print("\n端口验证测试:")
    for port in test_ports:
        is_valid = validator.validate_port(port)
        print(f"  {port} : {'✓' if is_valid else '✗'}")
    
    # 测试Bundle ID验证
    test_bundles = [
        "com.example.app",
        "com.example.my-app",
        "invalid..bundle",
        "com.example.",
        "com.example.app.",
    ]
    
    print("\nBundle ID验证测试:")
    for bundle in test_bundles:
        is_valid = validator.validate_bundle_id(bundle)
        print(f"  {bundle} : {'✓' if is_valid else '✗'}")


def demo_resource_manager():
    """演示资源管理器功能"""
    print("\n=== 资源管理器演示 ===")
    
    # 创建资源管理器
    manager = ResourceManager()
    
    # 模拟资源
    class MockResource:
        def __init__(self, name):
            self.name = name
            self.data = f"资源数据: {name}"
        
        def cleanup(self):
            print(f"清理资源: {self.name}")
    
    # 注册资源
    resource1 = MockResource("资源1")
    resource2 = MockResource("资源2")
    
    manager.register_resource("resource1", resource1, lambda r: r.cleanup())
    manager.register_resource("resource2", resource2, lambda r: r.cleanup())
    
    # 使用资源
    res1 = manager.get_resource("resource1")
    if res1:
        print(f"获取资源1: {res1.data}")
    
    res2 = manager.get_resource("resource2")
    if res2:
        print(f"获取资源2: {res2.data}")
    
    # 显示资源统计
    stats = manager.get_stats()
    print(f"资源统计: {stats}")
    
    # 清理资源
    manager.unregister_resource("resource1")
    manager.unregister_resource("resource2")


def demo_decorators():
    """演示装饰器功能"""
    print("\n=== 装饰器演示 ===")
    
    # 重试装饰器
    @with_retry()
    def retry_function():
        if random.random() < 0.6:
            raise RuntimeError("随机失败")
        return "重试成功"
    
    # 超时装饰器
    @with_timeout(0.5)
    def timeout_function():
        time.sleep(0.2)
        return "超时测试完成"
    
    # 熔断器装饰器
    @with_circuit_breaker()
    def circuit_function():
        if random.random() < 0.7:
            raise RuntimeError("熔断测试失败")
        return "熔断测试成功"
    
    # 输入验证装饰器
    @validate_input(udid=InputValidator.validate_udid, port=InputValidator.validate_port)
    def validation_function(udid, port):
        return f"验证通过: {udid[:10]}..., {port}"
    
    # 测试重试装饰器
    try:
        result = retry_function()
        print(f"重试装饰器: {result}")
    except RuntimeError as e:
        print(f"重试装饰器失败: {e}")
    
    # 测试超时装饰器
    try:
        result = timeout_function()
        print(f"超时装饰器: {result}")
    except TimeoutError as e:
        print(f"超时装饰器失败: {e}")
    
    # 测试熔断器装饰器
    for i in range(3):
        try:
            result = circuit_function()
            print(f"熔断器装饰器 {i+1}: {result}")
        except RuntimeError as e:
            print(f"熔断器装饰器 {i+1}: {e}")
    
    # 测试输入验证装饰器
    try:
        result = validation_function("00008020" + "0" * 32, 8080)
        print(f"输入验证装饰器: {result}")
    except ValueError as e:
        print(f"输入验证装饰器失败: {e}")


def demo_integration():
    """演示集成使用"""
    print("\n=== 集成使用演示 ===")
    
    # 模拟设备操作
    def simulate_device_operation(udid):
        """模拟设备操作，包含各种可能的失败"""
        # 模拟网络延迟
        time.sleep(random.uniform(0.1, 0.3))
        
        # 模拟各种失败情况
        failure_type = random.choice(["success", "timeout", "connection", "permission"])
        
        if failure_type == "success":
            return f"设备 {udid[:10]}... 操作成功"
        elif failure_type == "timeout":
            time.sleep(1.0)  # 模拟超时
            return f"设备 {udid[:10]}... 操作超时"
        elif failure_type == "connection":
            raise ConnectionError("设备连接失败")
        else:  # permission
            raise PermissionError("设备权限不足")
    
    # 使用多个稳定性功能
    retry_manager = RetryManager(RetryConfig(max_retries=2, base_delay=0.2))
    timeout_manager = TimeoutManager(default_timeout=0.5)
    validator = InputValidator()
    
    # 测试设备列表
    test_devices = [
        "00008020" + "0" * 32,
        "00008021" + "0" * 32,
        "invalid_udid",
        "00008022" + "0" * 32,
    ]
    
    print("集成稳定性测试:")
    for udid in test_devices:
        print(f"\n测试设备: {udid[:15]}...")
        
        # 输入验证
        if not validator.validate_udid(udid):
            print("  ✗ UDID格式无效")
            continue
        
        # 使用重试和超时
        try:
            @timeout_manager.with_timeout(0.8)
            def safe_operation():
                return retry_manager.execute(simulate_device_operation, udid)
            
            result = safe_operation()
            print(f"  ✓ {result}")
            
        except (ConnectionError, PermissionError) as e:
            print(f"  ✗ 操作失败: {e}")
        except TimeoutError as e:
            print(f"  ✗ 操作超时: {e}")


def main():
    """主函数"""
    print("pyidevice 稳定性功能演示")
    print("=" * 50)
    
    try:
        # 运行各种演示
        demo_retry_manager()
        demo_connection_pool()
        demo_health_checker()
        demo_circuit_breaker()
        demo_timeout_manager()
        demo_input_validator()
        demo_resource_manager()
        demo_decorators()
        demo_integration()
        
        print("\n" + "=" * 50)
        print("稳定性功能演示完成！")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
