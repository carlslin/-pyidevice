# IDB (iOS Device Bridge) 快速入门指南

## 🚀 什么是IDB？

**IDB (iOS Device Bridge)** 是Facebook开发的现代化iOS设备桥接工具，专门用于iOS自动化测试。它比传统的WDA更快、更稳定，并且原生支持iOS 17+。

## ✨ 主要优势

- ✅ **原生支持iOS 17+**：完全支持最新iOS版本
- ✅ **高性能**：比WDA快3-5倍
- ✅ **现代架构**：基于Swift开发
- ✅ **丰富的API**：提供完整的设备控制功能
- ✅ **活跃维护**：Facebook团队持续更新

## 📦 安装步骤

### 1. 安装IDB Companion

```bash
# 使用Homebrew安装
brew install idb-companion

# 或者从GitHub下载
# https://github.com/facebook/idb/releases
```

### 2. 安装Python客户端

```bash
# 安装IDB Python客户端
pip install idb

# 或者安装开发版本
pip install git+https://github.com/facebook/idb.git#subdirectory=python
```

### 3. 启动IDB服务

```bash
# 获取设备UDID
idevice_id -l

# 启动IDB Companion
idb_companion --udid YOUR_DEVICE_UDID

# 服务将在端口8080上运行
```

## 🎯 基本使用

### 1. 连接设备

```python
import idb

# 连接到设备
device = idb.Device(udid="YOUR_DEVICE_UDID")

# 或者连接到本地服务
device = idb.Device(host="localhost", port=8080)
```

### 2. 获取设备信息

```python
# 获取设备基本信息
info = device.info()
print(f"设备名称: {info['name']}")
print(f"iOS版本: {info['os_version']}")
print(f"设备型号: {info['model']}")
print(f"电池电量: {info['battery_level']}%")

# 获取应用列表
apps = device.list_apps()
for app in apps:
    print(f"应用: {app['name']} ({app['bundle_id']})")
```

### 3. 应用操作

```python
# 启动应用
device.app_launch("com.apple.Health")

# 获取当前应用
current_app = device.app_current()
print(f"当前应用: {current_app['name']}")

# 终止应用
device.app_terminate("com.apple.Health")

# 安装应用
device.app_install("/path/to/app.ipa")

# 卸载应用
device.app_uninstall("com.example.app")
```

### 4. 截图和录屏

```python
# 截图
screenshot = device.screenshot()
screenshot.save("screenshot.png")

# 录屏
device.video_start("/path/to/recording.mp4")
# ... 执行操作 ...
device.video_stop()
```

### 5. 元素查找和操作

```python
# 查找元素
elements = device.find_elements("Button")
print(f"找到 {len(elements)} 个按钮")

# 按标签查找
elements = device.find_elements("Button", label="开始使用")
if elements:
    button = elements[0]
    print(f"按钮位置: {button.bounds}")
    
    # 点击元素
    device.tap(button.bounds.center)
    
    # 长按
    device.long_press(button.bounds.center, duration=2.0)

# 按坐标点击
device.tap((100, 200))

# 滑动
device.swipe((100, 200), (300, 400), duration=1.0)
```

### 6. 文本输入

```python
# 输入文本
device.input_text("Hello World")

# 清除文本
device.clear_text()

# 按键操作
device.press_key("home")
device.press_key("volume_up")
device.press_key("volume_down")
```

## 🔧 高级功能

### 1. 文件操作

```python
# 上传文件到设备
device.file_push("/local/file.txt", "/device/path/file.txt")

# 从设备下载文件
device.file_pull("/device/path/file.txt", "/local/file.txt")

# 列出设备文件
files = device.file_list("/device/path/")
for file in files:
    print(f"文件: {file['name']}, 大小: {file['size']}")
```

### 2. 网络监控

```python
# 开始网络监控
device.network_start_monitoring()

# 获取网络统计
stats = device.network_get_stats()
print(f"发送字节: {stats['bytes_sent']}")
print(f"接收字节: {stats['bytes_received']}")

# 停止网络监控
device.network_stop_monitoring()
```

### 3. 性能监控

```python
# 开始性能监控
device.performance_start_monitoring()

# 获取性能数据
perf_data = device.performance_get_data()
print(f"CPU使用率: {perf_data['cpu_usage']}%")
print(f"内存使用: {perf_data['memory_usage']}MB")

# 停止性能监控
device.performance_stop_monitoring()
```

### 4. 日志监控

```python
# 开始日志监控
device.log_start_monitoring()

# 获取日志
logs = device.log_get_logs()
for log in logs:
    print(f"时间: {log['timestamp']}, 级别: {log['level']}, 消息: {log['message']}")

# 停止日志监控
device.log_stop_monitoring()
```

## 🧪 实际测试示例

### 健康应用自动化测试

```python
import idb
import time

def test_health_app():
    # 连接设备
    device = idb.Device(udid="YOUR_DEVICE_UDID")
    
    # 启动健康应用
    device.app_launch("com.apple.Health")
    time.sleep(2)
    
    # 截图
    device.screenshot().save("health_app_start.png")
    
    # 查找并点击"开始使用"按钮
    elements = device.find_elements("Button", label="开始使用")
    if elements:
        device.tap(elements[0].bounds.center)
        time.sleep(1)
    
    # 查找并点击"健康"标签
    elements = device.find_elements("Button", label="健康")
    if elements:
        device.tap(elements[0].bounds.center)
        time.sleep(1)
    
    # 截图验证
    device.screenshot().save("health_app_after.png")
    
    # 返回主屏幕
    device.press_key("home")
    
    print("健康应用测试完成")

if __name__ == "__main__":
    test_health_app()
```

### 批量应用测试

```python
import idb
import time

def test_multiple_apps():
    device = idb.Device(udid="YOUR_DEVICE_UDID")
    
    # 要测试的应用列表
    apps = [
        "com.apple.Health",
        "com.apple.Preferences", 
        "com.apple.Maps"
    ]
    
    for app in apps:
        print(f"测试应用: {app}")
        
        # 启动应用
        device.app_launch(app)
        time.sleep(2)
        
        # 截图
        device.screenshot().save(f"{app}_screenshot.png")
        
        # 获取应用信息
        current_app = device.app_current()
        print(f"当前应用: {current_app['name']}")
        
        # 返回主屏幕
        device.press_key("home")
        time.sleep(1)
    
    print("批量应用测试完成")

if __name__ == "__main__":
    test_multiple_apps()
```

## 🔍 与WDA对比

| 功能 | IDB | WDA |
|------|-----|-----|
| iOS 17+支持 | ✅ 原生支持 | ⚠️ 需要额外配置 |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 学习难度 | ⭐⭐⭐ | ⭐⭐⭐ |
| 社区支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 文档质量 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🚨 常见问题

### 1. 连接失败
```bash
# 检查设备是否连接
idevice_id -l

# 检查IDB服务是否运行
ps aux | grep idb_companion

# 重启IDB服务
pkill idb_companion
idb_companion --udid YOUR_DEVICE_UDID
```

### 2. 应用启动失败
```python
# 检查应用是否已安装
apps = device.list_apps()
for app in apps:
    if app['bundle_id'] == "com.apple.Health":
        print("应用已安装")
        break
else:
    print("应用未安装")
```

### 3. 元素查找失败
```python
# 等待元素出现
import time
for i in range(10):
    elements = device.find_elements("Button", label="开始使用")
    if elements:
        break
    time.sleep(1)
else:
    print("元素未找到")
```

## 📚 学习资源

- [IDB官方文档](https://fbidb.io/)
- [GitHub仓库](https://github.com/facebook/idb)
- [Python客户端文档](https://github.com/facebook/idb/tree/main/python)
- [示例项目](https://github.com/facebook/idb/tree/main/python/examples)

## 🎉 总结

IDB是一个现代化的iOS自动化工具，特别适合：

1. **新项目**：追求性能和现代化
2. **iOS 17+项目**：原生支持最新iOS版本
3. **高性能需求**：比WDA快3-5倍
4. **企业级应用**：稳定可靠

如果你正在寻找WDA的替代方案，特别是对于iOS 17+项目，**IDB**是一个优秀的选择！
