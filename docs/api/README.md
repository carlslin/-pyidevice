# API 参考

pyidevice 提供了丰富的 API 用于 iOS 设备管理和自动化。

## 核心模块

### DeviceManager
设备管理器，提供静态方法进行设备操作。

```python
from pyidevice import DeviceManager

# 获取设备列表
devices = DeviceManager.get_devices()

# 获取设备信息
info = DeviceManager.get_device_info(device_udid)

# 检查设备连接状态
is_connected = DeviceManager.is_device_connected(device_udid)

# 获取第一个可用设备
first_device = DeviceManager.get_first_device()
```

### Device
设备操作类，提供单个设备的所有操作接口。

```python
from pyidevice import Device

device = Device("00008020-0012345678901234")

# 设备信息
name = device.name()
model = device.model()
version = device.version()
battery = device.battery_level()

# 应用管理
apps = device.list_apps()
success = device.install_app("app.ipa")
success = device.uninstall_app("com.example.app")
success = device.start_app("com.example.app")

# 屏幕操作
success = device.take_screenshot("screenshot.png")

# 设备控制
success = device.reboot()
success = device.shutdown()
```

## 并发操作

### ParallelDeviceExecutor
并行设备执行器，支持多设备并发操作。

```python
from pyidevice import ParallelDeviceExecutor

executor = ParallelDeviceExecutor(max_workers=3)

# 并行执行任务
def process_device(udid):
    device = Device(udid)
    return device.info()

results = executor.map(process_device, device_list)
```

### BatchAppManager
批量应用管理器，支持批量应用操作。

```python
from pyidevice import BatchAppManager

manager = BatchAppManager(max_workers=3)

# 批量安装应用
results = manager.install_apps(devices, "app.ipa")

# 批量卸载应用
results = manager.uninstall_apps(devices, "com.example.app")
```

## UI自动化

### IDBAutomator（推荐）
基于 IDB (iOS Device Bridge) 的现代化 UI 自动化控制器，与 uiautomator2 API 对齐。

```python
from pyidevice import IDBAutomator

# 初始化IDB自动化器（类似uiautomator2.Device）
idb = IDBAutomator("00008020-0012345678901234")
idb.connect()

# 启动应用（类似d.app_start）
idb.app_start("com.example.app")

# 坐标点击（类似d.click(x, y)）
idb.tap_coordinate(200, 400)

# 方向滑动（类似d.swipe_up()）
idb.swipe_up()
idb.swipe_down()
idb.swipe_left()
idb.swipe_right()

# 元素查找和操作（类似d(text="登录").click()）
element = idb.find_element("Button", label="登录")
if element:
    idb.tap_element(element)

# 等待元素出现（类似d(text="登录").wait()）
element = idb.wait_for_element("Button", label="登录", timeout=10)

# 检查元素是否存在（类似d(text="登录").exists）
exists = idb.element_exists("Button", label="登录")

# 长按操作（类似d.long_click()）
if element:
    idb.long_press_element(element, duration=2.0)

# 双击操作
if element:
    idb.double_tap_element(element)

# 拖拽操作（类似d.drag()）
idb.drag(100, 200, 300, 400, duration=1.0)

# 多指操作（类似d.pinch()）
idb.pinch(200, 300, scale=1.5, duration=1.0)  # 放大
idb.pinch(200, 300, scale=0.5, duration=1.0)  # 缩小

# 文本输入（类似d(text="输入框").set_text()）
text_field = idb.find_element("UITextField", index=0)
if text_field:
    idb.input_text_to_element(text_field, "test_user")

# 截图（类似d.screenshot()）
idb.screenshot("screenshot.png")

# 获取屏幕信息（类似d.info）
screen_info = idb.get_screen_info()

# 停止应用（类似d.app_stop()）
idb.app_stop("com.example.app")
idb.disconnect()
```

### WDAutomator（传统方式）
基于 WebDriverAgent 的 UI 自动化控制器。

```python
from pyidevice import WDAutomator

wda = WDAutomator("00008020-0012345678901234")
wda.connect("http://localhost:8100")

# 查找元素
element = wda.find_element("//XCUIElementTypeButton[@name='登录']")

# 操作元素
element.click()
element.send_keys("用户名")

# 手势操作
wda.tap(100, 200)
wda.swipe(100, 200, 300, 400)
```

## 监控功能

### DeviceMonitor
设备监控器，实时监控设备状态。

```python
from pyidevice import device_monitor

# 添加监控回调
def on_device_update(metrics):
    print(f"设备 {metrics.udid}: 电池 {metrics.battery_level}%")

device_monitor.add_callback(on_device_update)

# 开始监控
device_monitor.start_monitoring(devices)

# 停止监控
device_monitor.stop_monitoring()
```

### AlertManager
告警管理器，处理设备告警。

```python
from pyidevice import alert_manager

# 添加告警回调
def on_alert(alert_name, severity, alert_data):
    print(f"告警: {alert_name} - {alert_data['message']}")

alert_manager.add_alert_callback(on_alert)

# 添加告警规则
def battery_rule(metrics):
    return metrics.battery_level < 20

alert_manager.add_alert_rule("low_battery", battery_rule, "warning")
```

## 缓存系统

### DeviceCache
设备信息缓存，提高操作性能。

```python
from pyidevice import device_cache

# 获取缓存的设备信息
cached_info = device_cache.get_device_info(device_udid)

# 设置设备信息缓存
device_cache.set_device_info(device_udid, device_info)

# 失效设备缓存
device_cache.invalidate_device(device_udid)
```

### 缓存装饰器
```python
from pyidevice import cached

@cached(ttl=60)  # 缓存60秒
def get_device_name(udid):
    device = Device(udid)
    return device.name()
```

## 性能监控

### PerformanceMonitor
性能监控器，跟踪操作性能。

```python
from pyidevice import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring()

# 执行操作
device.info()

# 获取统计信息
stats = monitor.stop_monitoring()
print(f"总操作数: {stats['total_operations']}")
print(f"平均操作时间: {stats['avg_operation_time']:.3f}秒")
```

### 性能装饰器
```python
from pyidevice import monitor_performance

@monitor_performance
def my_device_operation(device):
    return device.info()
```

## 配置管理

### Config
配置类，管理 pyidevice 配置。

```python
from pyidevice import Config, get_config

# 获取默认配置
config = get_config()

# 自定义配置
config = Config(
    timeout=60,
    retry_count=5,
    log_level="DEBUG"
)

# 从字典创建配置
config = Config.from_dict({
    "timeout": 45,
    "retry_count": 4
})
```

## 工具函数

### EnvironmentChecker
环境检查器，验证运行环境。

```python
from pyidevice import EnvironmentChecker

checker = EnvironmentChecker()

# 验证环境
is_valid, errors = checker.validate_environment()

# 获取系统信息
info = checker.get_system_info()
```

### 工具函数
```python
from pyidevice import format_bytes, safe_filename

# 格式化字节大小
size_str = format_bytes(1024 * 1024)  # "1.0 MB"

# 安全文件名
safe_name = safe_filename("My Device")  # "My_Device"
```

## 异常处理

### 异常层次结构
```python
from pyidevice import (
    PyIDeviceError,
    DeviceError,
    DeviceConnectionError,
    DeviceCommandError,
    AppError,
    WDAError,
    IDBError,
    IDBConnectionError,
    IDBElementError,
    IDBOperationError
)

try:
    device = Device("invalid_udid")
    info = device.info()
except DeviceConnectionError as e:
    print(f"设备连接错误: {e}")
except DeviceError as e:
    print(f"设备操作错误: {e}")
except PyIDeviceError as e:
    print(f"pyidevice错误: {e}")
```

### 重试装饰器
```python
from pyidevice import retry_on_failure

@retry_on_failure(max_retries=3, delay=1.0)
def install_app_with_retry(device, ipa_path):
    return device.install_app(ipa_path)
```

## 类型定义

### 设备状态
```python
from pyidevice import DeviceStatus

# 设备状态枚举
DeviceStatus.CONNECTED
DeviceStatus.DISCONNECTED
DeviceStatus.UNKNOWN
```

### 执行器类型
```python
from pyidevice import ExecutorType

# 执行器类型
ExecutorType.THREAD
ExecutorType.PROCESS
```

### 日志级别
```python
from pyidevice import LogLevel

# 日志级别
LogLevel.DEBUG
LogLevel.INFO
LogLevel.WARNING
LogLevel.ERROR
```

## 完整示例

```python
#!/usr/bin/env python3
"""
pyidevice API 使用示例
"""

from pyidevice import (
    DeviceManager, Device, ParallelDeviceExecutor,
    device_monitor, alert_manager, cached
)

@cached(ttl=300)  # 缓存5分钟
def get_device_info_cached(udid):
    device = Device(udid)
    return device.info()

def main():
    # 获取设备列表
    devices = DeviceManager.get_devices()
    if not devices:
        print("没有找到设备")
        return
    
    # 并行获取设备信息
    executor = ParallelDeviceExecutor(max_workers=3)
    results = executor.map(get_device_info_cached, devices)
    
    # 处理结果
    for result in results:
        print(f"设备: {result.get('DeviceName', 'Unknown')}")
    
    # 设置监控
    def on_device_update(metrics):
        print(f"设备 {metrics.udid}: 电池 {metrics.battery_level}%")
    
    def on_alert(alert_name, severity, alert_data):
        print(f"🚨 告警: {alert_name}")
    
    device_monitor.add_callback(on_device_update)
    alert_manager.add_alert_callback(on_alert)
    
    # 开始监控
    device_monitor.start_monitoring(devices)
    
    try:
        import time
        time.sleep(30)  # 监控30秒
    finally:
        device_monitor.stop_monitoring()

if __name__ == "__main__":
    main()
```

---

*更多详细信息请查看各个模块的文档字符串，或运行 `help()` 函数查看帮助信息。*