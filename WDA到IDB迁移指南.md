# WDA到IDB迁移指南

## 🚀 迁移概述

本指南将帮助你将现有的WDA (WebDriverAgent) 代码迁移到IDB (iOS Device Bridge)。IDB是Facebook开发的现代化iOS自动化工具，具有更好的性能和iOS 17+支持。

## 📊 迁移对比

| 功能 | WDA | IDB | 迁移难度 |
|------|-----|-----|----------|
| 设备连接 | `wda.Client('http://localhost:8100')` | `idb.Device(udid='YOUR_UDID')` | ⭐⭐ |
| 应用启动 | `session.app_launch(bundle_id)` | `device.app_launch(bundle_id)` | ⭐ |
| 元素查找 | `session(name='按钮')` | `device.find_elements('Button', label='按钮')` | ⭐⭐⭐ |
| 点击操作 | `element.click()` | `device.tap(element.bounds.center)` | ⭐⭐ |
| 截图 | `session.screenshot().save(path)` | `device.screenshot().save(path)` | ⭐ |
| iOS 17+支持 | ⚠️ 需要额外配置 | ✅ 原生支持 | ⭐⭐⭐⭐⭐ |

## 🔄 代码迁移示例

### 1. 基本连接

#### WDA代码
```python
from wda import Client

# 连接到WDA服务
client = Client('http://localhost:8100')
client.wait_ready()

# 创建会话
session = client.session('com.apple.Health')
```

#### IDB代码
```python
import idb

# 连接到IDB服务
device = idb.Device(udid='YOUR_DEVICE_UDID')

# 启动应用
device.app_launch('com.apple.Health')
```

### 2. 元素查找和操作

#### WDA代码
```python
# 查找元素
element = session(name='开始使用')
element.click()

# 输入文本
text_field = session(type='TextField')
text_field.set_text('Hello World')

# 滑动操作
session.swipe(100, 200, 100, 100)
```

#### IDB代码
```python
# 查找元素
elements = device.find_elements('Button', label='开始使用')
if elements:
    device.tap(elements[0].bounds.center)

# 输入文本
device.input_text('Hello World')

# 滑动操作
device.swipe(100, 200, 100, 100, 1.0)
```

### 3. 应用管理

#### WDA代码
```python
# 启动应用
session = client.session('com.apple.Health')

# 获取当前应用
current_app = session.app_current()

# 停止应用
session.app_terminate()
```

#### IDB代码
```python
# 启动应用
device.app_launch('com.apple.Health')

# 获取当前应用
current_app = device.app_current()

# 停止应用
device.app_terminate('com.apple.Health')
```

### 4. 截图和录屏

#### WDA代码
```python
# 截图
screenshot = session.screenshot()
screenshot.save('screenshot.png')
```

#### IDB代码
```python
# 截图
screenshot = device.screenshot()
screenshot.save('screenshot.png')

# 录屏（IDB独有功能）
device.video_start('recording.mp4')
# ... 执行操作 ...
device.video_stop()
```

## 🛠️ 迁移步骤

### 步骤1：安装IDB

```bash
# 安装IDB Companion
brew install idb-companion

# 安装IDB Python客户端
pip install idb
```

### 步骤2：启动IDB服务

```bash
# 获取设备UDID
idevice_id -l

# 启动IDB Companion服务
idb_companion --udid YOUR_DEVICE_UDID
```

### 步骤3：更新导入语句

```python
# 旧代码
from wda import Client

# 新代码
import idb
```

### 步骤4：更新连接代码

```python
# 旧代码
client = Client('http://localhost:8100')
client.wait_ready()
session = client.session('com.apple.Health')

# 新代码
device = idb.Device(udid='YOUR_DEVICE_UDID')
device.app_launch('com.apple.Health')
```

### 步骤5：更新元素操作代码

```python
# 旧代码
element = session(name='按钮')
element.click()

# 新代码
elements = device.find_elements('Button', label='按钮')
if elements:
    device.tap(elements[0].bounds.center)
```

## 📝 迁移检查清单

- [ ] 安装IDB Companion和Python客户端
- [ ] 启动IDB Companion服务
- [ ] 更新导入语句
- [ ] 更新连接代码
- [ ] 更新元素查找代码
- [ ] 更新元素操作代码
- [ ] 更新应用管理代码
- [ ] 测试所有功能
- [ ] 更新文档和注释

## 🚨 常见问题

### 1. 连接失败

**问题**：无法连接到IDB服务

**解决方案**：
```bash
# 检查IDB Companion是否运行
ps aux | grep idb_companion

# 重启IDB Companion服务
pkill idb_companion
idb_companion --udid YOUR_DEVICE_UDID
```

### 2. 元素查找失败

**问题**：找不到元素

**解决方案**：
```python
# 使用更灵活的元素查找
elements = device.find_elements('Button')  # 查找所有按钮
for element in elements:
    if '登录' in element.get('label', ''):
        device.tap(element.bounds.center)
        break
```

### 3. 应用启动失败

**问题**：应用无法启动

**解决方案**：
```python
# 检查应用是否已安装
apps = device.list_apps()
for app in apps:
    if app['bundle_id'] == 'com.apple.Health':
        print("应用已安装")
        break
else:
    print("应用未安装")
```

## 🎯 性能优化建议

### 1. 使用批量操作

```python
# 批量查找元素
elements = device.find_elements('Button')
for element in elements:
    if element.get('label') in ['登录', '注册', '设置']:
        device.tap(element.bounds.center)
```

### 2. 使用性能监控

```python
# 开始性能监控
device.performance_start_monitoring()

# 执行操作
device.app_launch('com.apple.Health')

# 获取性能数据
perf_data = device.performance_get_data()
print(f"CPU使用率: {perf_data['cpu_usage']}%")

# 停止性能监控
device.performance_stop_monitoring()
```

### 3. 使用网络监控

```python
# 开始网络监控
device.network_start_monitoring()

# 执行网络相关操作
device.app_launch('com.apple.Safari')

# 获取网络统计
network_stats = device.network_get_stats()
print(f"发送字节: {network_stats['bytes_sent']}")

# 停止网络监控
device.network_stop_monitoring()
```

## 📚 参考资源

- [IDB官方文档](https://fbidb.io/)
- [IDB GitHub仓库](https://github.com/facebook/idb)
- [IDB Python客户端](https://github.com/facebook/idb/tree/main/python)
- [pyidevice IDB模块文档](pyidevice/idb.py)

## 🎉 迁移完成

完成迁移后，你将获得：

- ✅ 更好的iOS 17+支持
- ✅ 更高的性能和稳定性
- ✅ 更丰富的功能（录屏、性能监控等）
- ✅ 更现代的API设计
- ✅ 更好的错误处理

如果遇到问题，请参考[IDB快速入门指南](IDB快速入门指南.md)或[故障排除指南](IDB安装指南.md)。
