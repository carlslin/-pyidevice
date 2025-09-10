# uiautomator2 API 对比文档

## 📋 概述

本文档展示了 `pyidevice` 的 IDB 集成如何提供与 `uiautomator2` 相似的 API，让 Android 自动化开发者可以轻松迁移到 iOS 自动化。

## 🔄 API 对比表

| 功能 | uiautomator2 | pyidevice (IDB) | 说明 |
|------|-------------|-----------------|------|
| **设备初始化** | `d = u2.connect()` | `idb = IDBAutomator(udid)` | 都需要指定设备标识 |
| **连接设备** | `d = u2.connect()` | `idb.connect()` | 建立与设备的连接 |
| **坐标点击** | `d.click(x, y)` | `idb.tap_coordinate(x, y)` | 点击指定坐标 |
| **元素点击** | `d(text="登录").click()` | `idb.tap_element(element)` | 点击找到的元素 |
| **滑动操作** | `d.swipe(x1, y1, x2, y2)` | `idb.swipe(x1, y1, x2, y2, duration)` | 滑动操作 |
| **方向滑动** | `d.swipe_up()` | `idb.swipe_up()` | 方向性滑动 |
| | `d.swipe_down()` | `idb.swipe_down()` | |
| | `d.swipe_left()` | `idb.swipe_left()` | |
| | `d.swipe_right()` | `idb.swipe_right()` | |
| **按键操作** | `d.press("home")` | `idb.press_key("home")` | 按键操作 |
| **长按操作** | `d.long_click(x, y)` | `idb.long_press_element(element)` | 长按操作 |
| **双击操作** | `d.double_click(x, y)` | `idb.double_tap_element(element)` | 双击操作 |
| **拖拽操作** | `d.drag(x1, y1, x2, y2)` | `idb.drag(x1, y1, x2, y2, duration)` | 拖拽操作 |
| **多指操作** | `d.pinch_in()` | `idb.pinch(x, y, scale=0.5)` | 多指操作 |
| | `d.pinch_out()` | `idb.pinch(x, y, scale=1.5)` | |
| **文本输入** | `d(text="输入框").set_text("文本")` | `idb.input_text_to_element(element, "文本")` | 文本输入 |
| **等待元素** | `d(text="登录").wait()` | `idb.wait_for_element("Button", label="登录")` | 等待元素出现 |
| **元素存在** | `d(text="登录").exists` | `idb.element_exists("Button", label="登录")` | 检查元素是否存在 |
| **元素信息** | `d(text="登录").info` | `idb.get_element_info("Button", label="登录")` | 获取元素信息 |
| **截图** | `d.screenshot("path.png")` | `idb.screenshot("path.png")` | 截图功能 |
| **屏幕信息** | `d.info` | `idb.get_screen_info()` | 获取屏幕信息 |
| **应用启动** | `d.app_start("包名")` | `idb.app_start("bundle_id")` | 启动应用 |
| **应用停止** | `d.app_stop("包名")` | `idb.app_stop("bundle_id")` | 停止应用 |

## 📝 代码示例对比

### 1. 基本设备操作

#### uiautomator2
```python
import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 获取屏幕信息
info = d.info
print(f"屏幕尺寸: {info['displayWidth']}x{info['displayHeight']}")

# 截图
d.screenshot("screenshot.png")
```

#### pyidevice (IDB)
```python
from pyidevice import IDBAutomator

# 连接设备
idb = IDBAutomator("YOUR_DEVICE_UDID")
idb.connect()

# 获取屏幕信息
screen_info = idb.get_screen_info()
print(f"屏幕尺寸: {screen_info['width']}x{screen_info['height']}")

# 截图
idb.screenshot("screenshot.png")
```

### 2. 元素查找和操作

#### uiautomator2
```python
# 通过文本查找并点击
d(text="登录").click()

# 通过类名查找
d(className="android.widget.Button").click()

# 通过坐标点击
d.click(200, 400)

# 等待元素出现
d(text="登录").wait()

# 检查元素是否存在
exists = d(text="登录").exists

# 获取元素信息
info = d(text="登录").info
```

#### pyidevice (IDB)
```python
# 通过文本查找并点击
element = idb.find_element("Button", label="登录")
if element:
    idb.tap_element(element)

# 通过类名查找
button = idb.find_element("UIButton", index=0)
if button:
    idb.tap_element(button)

# 通过坐标点击
idb.tap_coordinate(200, 400)

# 等待元素出现
element = idb.wait_for_element("Button", label="登录", timeout=10)

# 检查元素是否存在
exists = idb.element_exists("Button", label="登录")

# 获取元素信息
info = idb.get_element_info("Button", label="登录")
```

### 3. 手势操作

#### uiautomator2
```python
# 滑动操作
d.swipe(200, 400, 200, 200)  # 向上滑动
d.swipe_up()
d.swipe_down()
d.swipe_left()
d.swipe_right()

# 长按操作
d.long_click(200, 400)

# 双击操作
d.double_click(200, 400)

# 拖拽操作
d.drag(100, 200, 300, 400)

# 多指操作
d.pinch_in()
d.pinch_out()
```

#### pyidevice (IDB)
```python
# 滑动操作
idb.swipe(200, 400, 200, 200, 1.0)  # 向上滑动
idb.swipe_up()
idb.swipe_down()
idb.swipe_left()
idb.swipe_right()

# 长按操作
element = idb.find_element("Button", label="长按我")
if element:
    idb.long_press_element(element, duration=2.0)

# 双击操作
element = idb.find_element("Button", label="双击我")
if element:
    idb.double_tap_element(element)

# 拖拽操作
idb.drag(100, 200, 300, 400, duration=1.0)

# 多指操作
idb.pinch(200, 300, scale=0.5)  # 缩小
idb.pinch(200, 300, scale=1.5)  # 放大
```

### 4. 文本输入

#### uiautomator2
```python
# 输入文本
d(text="用户名").set_text("test_user")
d(className="android.widget.EditText").set_text("password")
```

#### pyidevice (IDB)
```python
# 输入文本
text_field = idb.find_element("UITextField", index=0)
if text_field:
    idb.input_text_to_element(text_field, "test_user")
```

### 5. 应用管理

#### uiautomator2
```python
# 启动应用
d.app_start("com.example.app")

# 停止应用
d.app_stop("com.example.app")
```

#### pyidevice (IDB)
```python
# 启动应用
idb.app_start("com.example.app")

# 停止应用
idb.app_stop("com.example.app")
```

## 🔄 迁移指南

### 从 uiautomator2 迁移到 pyidevice (IDB)

1. **导入模块**
   ```python
   # 旧代码
   import uiautomator2 as u2
   
   # 新代码
   from pyidevice import IDBAutomator
   ```

2. **设备连接**
   ```python
   # 旧代码
   d = u2.connect()
   
   # 新代码
   idb = IDBAutomator("YOUR_DEVICE_UDID")
   idb.connect()
   ```

3. **元素查找**
   ```python
   # 旧代码
   d(text="登录").click()
   
   # 新代码
   element = idb.find_element("Button", label="登录")
   if element:
       idb.tap_element(element)
   ```

4. **错误处理**
   ```python
   # 旧代码
   if d(text="登录").exists:
       d(text="登录").click()
   
   # 新代码
   if idb.element_exists("Button", label="登录"):
       element = idb.find_element("Button", label="登录")
       if element:
           idb.tap_element(element)
   ```

## 🎯 优势对比

### pyidevice (IDB) 的优势

1. **iOS 17+ 支持**: 原生支持最新的 iOS 版本
2. **更好的性能**: 比 WDA 快 3-5 倍
3. **更稳定的连接**: 减少连接超时和重连问题
4. **丰富的功能**: 录屏、性能监控、网络监控等
5. **持续更新**: Facebook 团队持续维护

### uiautomator2 的优势

1. **Android 专用**: 专为 Android 设计
2. **简单易用**: API 设计简洁
3. **成熟稳定**: 经过长期验证
4. **社区支持**: 活跃的社区和文档

## 📚 总结

`pyidevice` 的 IDB 集成提供了与 `uiautomator2` 相似的 API 设计，让开发者可以：

- ✅ 使用熟悉的 API 风格
- ✅ 轻松迁移现有的自动化脚本
- ✅ 享受 iOS 17+ 的原生支持
- ✅ 获得更好的性能和稳定性

通过这种 API 对齐，开发者可以无缝地从 Android 自动化迁移到 iOS 自动化，或者同时维护两套自动化脚本。
