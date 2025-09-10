# WebDriverAgent (WDA) 编译和使用指南

## 📋 目录

- [概述](#概述)
- [iOS 17+ 兼容性问题](#ios-17-兼容性问题)
- [解决方案对比](#解决方案对比)
- [Appium WebDriverAgent 编译指南](#appium-webdriveragent-编译指南)
- [facebook-wda 源码编译](#facebook-wda-源码编译)
- [使用 pyidevice 连接 WDA](#使用-pyidevice-连接-wda)
- [常见问题解决](#常见问题解决)
- [最佳实践](#最佳实践)

## 概述

WebDriverAgent (WDA) 是 Facebook 开源的 iOS 自动化测试框架，但原项目已被归档。目前主要有两个维护版本：

1. **Appium WebDriverAgent** - Appium 团队维护，支持最新 iOS 版本
2. **facebook-wda** - 社区维护的 Python 客户端库

## iOS 17+ 兼容性问题

### 问题描述

- facebook-wda 默认版本对 iOS 17+ 支持有限
- 某些自动化操作可能失败
- 元素定位可能不准确
- 手势操作可能异常

### 根本原因

- WebDriverAgent 核心代码需要适配新的 iOS API
- XCUITest 框架在 iOS 17+ 有变化
- 权限和安全策略更新

## 解决方案对比

| 方案 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| Appium WDA | 最新支持、持续维护 | 配置复杂 | ⭐⭐⭐⭐⭐ |
| facebook-wda 源码编译 | 轻量级、简单 | 维护滞后 | ⭐⭐⭐ |
| 降级 iOS 版本 | 兼容性好 | 不现实 | ⭐ |

## Appium WebDriverAgent 编译指南

### 1. 环境准备

#### 系统要求
- macOS 10.15+ (推荐 macOS 12+)
- Xcode 14+ (推荐 Xcode 15+)
- 有效的 Apple Developer 账号

#### 安装依赖
```bash
# 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装必要工具
brew install libimobiledevice
brew install ideviceinstaller
```

### 2. 获取源码

```bash
# 克隆 Appium WebDriverAgent
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent

# 切换到稳定版本 (推荐)
git checkout v2.16.1

# 安装依赖
./Scripts/bootstrap.sh
```

### 3. Xcode 配置

#### 3.1 打开项目
```bash
open WebDriverAgent.xcodeproj
```

#### 3.2 配置签名
1. 选择 `WebDriverAgentRunner` target
2. 在 `Signing & Capabilities` 中：
   - 选择你的开发团队
   - 修改 `Bundle Identifier` 为唯一标识符，如：`com.yourname.WebDriverAgentRunner`
3. 确保 `Automatically manage signing` 已勾选

#### 3.3 配置设备
1. 连接 iOS 设备到 Mac
2. 在设备上信任开发者证书：
   - 设置 → 通用 → VPN与设备管理 → 开发者 App → 信任

### 4. 编译和安装

#### 4.1 获取设备信息
```bash
# 列出连接的设备
idevice_id -l

# 获取设备详细信息
ideviceinfo -u YOUR_DEVICE_UDID
```

#### 4.2 编译安装
```bash
# 设置设备 UDID
UDID="YOUR_DEVICE_UDID"

# 编译并安装到设备
xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination "id=$UDID" \
           test
```

#### 4.3 启动服务
```bash
# 启动 WDA 服务
xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination "id=$UDID" \
           test-without-building
```

### 5. 验证安装

```bash
# 检查 WDA 是否运行
curl http://localhost:8100/status

# 预期输出类似：
# {
#   "value": {
#     "state": "success",
#     "os": {
#       "name": "iOS",
#       "version": "17.0"
#     },
#     "ios": {
#       "simulatorVersion": "17.0",
#       "ip": "192.168.1.100"
#     }
#   }
# }
```

## facebook-wda 源码编译

### 1. 获取源码

```bash
# 克隆 facebook-wda
git clone https://github.com/openatx/facebook-wda.git
cd facebook-wda

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 2. 本地安装

```bash
# 从源码安装
pip3 install -e .

# 或者直接使用源码
python3 -c "import wda; print('facebook-wda 安装成功')"
```

### 3. 使用示例

```python
import wda

# 创建客户端
c = wda.Client('http://localhost:8100')

# 等待服务就绪
c.wait_ready(timeout=30)

# 获取设备状态
status = c.status()
print(f"设备状态: {status}")

# 启动应用
s = c.session('com.apple.Health')
print(f"应用已启动: {s.bundle_id}")
```

## 使用 pyidevice 连接 WDA

### 1. 基本连接

```python
from pyidevice import WDAutomator

# 创建 WDA 客户端
wda = WDAutomator("YOUR_DEVICE_UDID")

# 连接到 WDA 服务
if wda.connect("http://localhost:8100"):
    print("✅ 成功连接到 WDA")
    
    # 启动应用
    wda.app_start("com.apple.Health")
    
    # 执行操作
    wda.click("xpath", "//XCUIElementTypeButton[@name='开始使用']")
    
    # 断开连接
    wda.disconnect()
else:
    print("❌ 连接失败")
```

### 2. 高级用法

```python
from pyidevice import WDAutomator

wda = WDAutomator("YOUR_DEVICE_UDID")

if wda.connect():
    # 启动应用
    wda.app_start("com.apple.Health")
    
    # 等待元素出现并点击
    element = wda.find_element("xpath", "//XCUIElementTypeButton[@name='开始使用']")
    if element:
        element.click()
    
    # 滑动操作
    wda.swipe_up()
    wda.swipe_down()
    
    # 截图
    wda.take_screenshot("screenshot.png")
    
    # 获取当前应用信息
    package = wda.get_current_package()
    print(f"当前应用: {package}")
    
    wda.disconnect()
```

### 3. 批量操作

```python
from pyidevice import WDAutomator, DeviceManager

# 获取所有设备
devices = DeviceManager.get_devices()

# 为每个设备创建 WDA 连接
wda_clients = []
for device_udid in devices:
    wda = WDAutomator(device_udid)
    if wda.connect():
        wda_clients.append(wda)
        print(f"✅ 设备 {device_udid} 连接成功")

# 并行执行操作
for wda in wda_clients:
    wda.app_start("com.apple.Health")
    wda.take_screenshot(f"screenshot_{wda.udid}.png")
    wda.disconnect()
```

## 常见问题解决

### 1. 连接失败

**问题**: `Connection refused` 或 `Timeout`

**解决方案**:
```bash
# 检查 WDA 是否运行
curl http://localhost:8100/status

# 检查端口转发
iproxy 8100 8100 YOUR_DEVICE_UDID

# 重启 WDA 服务
xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination "id=$UDID" \
           test-without-building
```

### 2. 签名问题

**问题**: `Code signing error` 或 `Provisioning profile`

**解决方案**:
1. 检查开发者账号是否有效
2. 重新生成 Provisioning Profile
3. 清理 Xcode 缓存：
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```

### 3. 权限问题

**问题**: 应用无法启动或操作失败

**解决方案**:
1. 在设备上信任开发者证书
2. 检查应用权限设置
3. 重启设备

### 4. iOS 17+ 特定问题

**问题**: 元素定位失败或操作异常

**解决方案**:
1. 使用最新的 Appium WebDriverAgent
2. 更新 XCUITest 相关代码
3. 检查元素属性变化

## 最佳实践

### 1. 开发环境

- 使用真机测试，避免模拟器兼容性问题
- 保持 Xcode 和 iOS 版本相对较新
- 定期更新 WebDriverAgent 版本

### 2. 代码规范

```python
# 使用上下文管理器
with WDAutomator("device_udid") as wda:
    if wda.connect():
        wda.app_start("com.example.app")
        # 执行操作
        wda.click("xpath", "//Button[@name='OK']")

# 添加错误处理
try:
    wda = WDAutomator("device_udid")
    if wda.connect():
        # 执行操作
        pass
except Exception as e:
    print(f"WDA 操作失败: {e}")
finally:
    wda.disconnect()
```

### 3. 性能优化

- 使用连接池管理多个设备连接
- 实现重试机制处理网络问题
- 缓存设备信息减少重复查询

### 4. 监控和日志

```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在操作中添加日志
logger.info(f"连接到设备: {device_udid}")
if wda.connect():
    logger.info("WDA 连接成功")
else:
    logger.error("WDA 连接失败")
```

## 总结

通过编译最新版本的 WebDriverAgent，可以完美支持 iOS 17-18+ 设备。推荐使用 Appium 维护的版本，它提供了最好的兼容性和稳定性。

关键步骤：
1. ✅ 使用 Appium WebDriverAgent 源码
2. ✅ 正确配置 Xcode 签名
3. ✅ 在真机上测试
4. ✅ 使用 pyidevice 进行自动化操作

这样就能在 iOS 17+ 设备上实现稳定的自动化测试了！
