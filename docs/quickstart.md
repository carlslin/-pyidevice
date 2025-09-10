# 快速开始

本指南将帮助您在5分钟内开始使用 pyidevice。

## 前提条件

- 已安装 pyidevice（参考 [安装指南](installation.md)）
- 已连接 iOS 设备并信任计算机
- 设备已解锁

## 基本使用

### 1. 获取设备列表

```python
from pyidevice import DeviceManager

# 获取所有连接的设备
devices = DeviceManager.get_devices()
print(f"找到 {len(devices)} 个设备")

# 显示设备UDID
for device in devices:
    print(f"设备: {device}")
```

### 1.1 IDB UI自动化（推荐）

```python
from pyidevice import IDBAutomator

# 初始化IDB自动化器（类似uiautomator2.Device）
idb = IDBAutomator("YOUR_DEVICE_UDID")
idb.connect()

# 启动应用
idb.app_start("com.apple.Health")

# 坐标点击（类似uiautomator2的d.click(x, y)）
idb.tap_coordinate(200, 400)

# 方向滑动（类似uiautomator2的d.swipe_up()）
idb.swipe_up()
idb.swipe_down()

# 元素操作（类似uiautomator2的d(text="登录").click()）
element = idb.find_element("Button", label="登录")
if element:
    idb.tap_element(element)

# 截图
idb.screenshot("screenshot.png")

# 停止应用
idb.app_stop("com.apple.Health")
idb.disconnect()
```

### 2. 获取设备信息

```python
from pyidevice import Device

# 创建设备对象
device = Device("00008020-0012345678901234")  # 替换为实际UDID

# 获取基本信息
print(f"设备名称: {device.name()}")
print(f"设备型号: {device.model()}")
print(f"iOS版本: {device.version()}")
print(f"电池电量: {device.battery_level()}%")

# 获取详细信息
info = device.info()
for key, value in info.items():
    print(f"{key}: {value}")
```

### 3. 应用管理

```python
# 列出已安装的应用
apps = device.list_apps()
print(f"已安装 {len(apps)} 个应用")

for app in apps[:5]:  # 显示前5个应用
    print(f"应用: {app['name']} ({app['bundle_id']})")

# 安装应用（需要IPA文件）
# success = device.install_app("/path/to/your/app.ipa")
# print(f"安装结果: {'成功' if success else '失败'}")

# 启动应用
# success = device.start_app("com.example.app")
# print(f"启动结果: {'成功' if success else '失败'}")
```

### 4. 屏幕截图

```python
# 截取屏幕截图
screenshot_path = "/tmp/device_screenshot.png"
success = device.take_screenshot(screenshot_path)

if success:
    print(f"截图已保存到: {screenshot_path}")
else:
    print("截图失败")
```

## 命令行使用

### 基本命令

```bash
# 列出设备
pyidevice list

# 获取设备信息
pyidevice info -u 00008020-0012345678901234

# 截取屏幕截图
pyidevice screenshot -u 00008020-0012345678901234 screenshot.png

# 列出已安装应用
pyidevice apps -u 00008020-0012345678901234
```

### IDB 命令（推荐）

```bash
# 连接IDB
pyidevice idb connect -u YOUR_DEVICE_UDID

# 获取IDB状态
pyidevice idb status -u YOUR_DEVICE_UDID

# IDB截图
pyidevice idb screenshot -u YOUR_DEVICE_UDID screenshot.png

# 应用操作
pyidevice idb app launch -u YOUR_DEVICE_UDID com.apple.Health
pyidevice idb app stop -u YOUR_DEVICE_UDID com.apple.Health
pyidevice idb app current -u YOUR_DEVICE_UDID
pyidevice idb app list -u YOUR_DEVICE_UDID
```

### 批量操作

```bash
# 批量获取设备信息
pyidevice batch info --output device_info.json

# 批量截图
pyidevice batch screenshot /tmp/screenshots/

# 批量安装应用
pyidevice batch install /path/to/app.ipa --workers 3
```

### 设备监控

```bash
# 监控设备状态
pyidevice monitor --interval 5 --alerts

# 监控指定时间
pyidevice monitor --duration 60 --interval 10
```

## 完整示例

```python
#!/usr/bin/env python3
"""
pyidevice 快速开始示例
"""

from pyidevice import DeviceManager, Device

def main():
    # 1. 获取设备列表
    devices = DeviceManager.get_devices()
    if not devices:
        print("没有找到连接的设备")
        return
    
    print(f"找到 {len(devices)} 个设备")
    
    # 2. 选择第一个设备
    device_udid = devices[0]
    device = Device(device_udid)
    
    print(f"使用设备: {device.name()}")
    
    # 3. 获取设备信息
    print(f"设备型号: {device.model()}")
    print(f"iOS版本: {device.version()}")
    print(f"电池电量: {device.battery_level()}%")
    
    # 4. 截取屏幕截图
    screenshot_path = f"/tmp/{device.name()}_screenshot.png"
    if device.take_screenshot(screenshot_path):
        print(f"截图已保存: {screenshot_path}")
    
    # 5. 列出应用
    apps = device.list_apps()
    print(f"已安装 {len(apps)} 个应用")
    
    # 显示前5个应用
    for app in apps[:5]:
        print(f"  - {app['name']} ({app['bundle_id']})")

if __name__ == "__main__":
    main()
```

## 下一步

现在您已经掌握了 pyidevice 的基本用法，可以：

1. 查看 [API 文档](api/) 了解更多功能
2. 运行 [示例代码](examples/) 学习最佳实践
3. 阅读 [uiautomator2 API对比](../uiautomator2_API对比.md) 了解迁移指南
4. 查看 [IDB快速入门指南](../IDB快速入门指南.md) 学习IDB使用
5. 阅读 [故障排除指南](troubleshooting.md) 解决常见问题

## 常见问题

### Q: 如何获取设备UDID？
**A**: 使用以下命令：
```bash
pyidevice list
```

### Q: 设备连接失败怎么办？
**A**: 检查：
1. 设备是否通过USB连接
2. 设备是否信任计算机
3. 设备是否解锁

### Q: 如何安装应用？
**A**: 需要IPA文件：
```python
success = device.install_app("/path/to/app.ipa")
```

### Q: 如何批量操作多个设备？
**A**: 使用批量命令：
```bash
pyidevice batch info --output all_devices.json
```

---

*需要更多帮助？查看 [完整文档](README.md) 或提交 [Issue](https://github.com/yourusername/pyidevice/issues)。*
