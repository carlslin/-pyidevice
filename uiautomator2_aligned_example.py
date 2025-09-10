#!/usr/bin/env python3
"""
与uiautomator2对齐的UI自动化示例
基于IDB实现，提供与uiautomator2相似的API

这个脚本展示了如何使用pyidevice的IDB集成功能，
实现与uiautomator2相似的UI自动化操作
"""

import time
import sys
from pyidevice import IDBAutomator

def main():
    """主函数"""
    print("🚀 与uiautomator2对齐的UI自动化示例")
    print("基于IDB实现，提供与uiautomator2相似的API")
    print("=" * 60)
    
    # 设备UDID（请替换为你的设备UDID）
    device_udid = "00008112-001159210CA3401E"  # 示例UDID
    
    try:
        # 初始化IDBAutomator实例（类似uiautomator2.Device）
        print(f"📱 初始化IDBAutomator实例...")
        idb = IDBAutomator(udid=device_udid)
        
        # 连接到设备
        print("🔗 连接到设备...")
        if not idb.connect():
            print("❌ 设备连接失败")
            return 1
        
        print("✅ 设备连接成功")
        
        # 获取屏幕信息（类似uiautomator2的d.info）
        print("\n📊 获取屏幕信息...")
        screen_info = idb.get_screen_info()
        if screen_info:
            print(f"屏幕尺寸: {screen_info['width']}x{screen_info['height']}")
            print(f"屏幕缩放: {screen_info['scale']}")
            print(f"屏幕方向: {screen_info['orientation']}")
        
        # 启动应用（类似uiautomator2的d.app_start）
        app_bundle_id = "com.apple.Health"  # 示例应用
        print(f"\n🚀 启动应用: {app_bundle_id}")
        if idb.app_start(app_bundle_id):
            print("✅ 应用启动成功")
            time.sleep(2)  # 等待应用加载
        else:
            print("❌ 应用启动失败")
            return 1
        
        # 1. 通过坐标点击（类似uiautomator2的d.click(x, y)）
        print("\n👆 坐标点击测试...")
        if idb.tap_coordinate(200, 400):
            print("✅ 坐标点击成功")
            time.sleep(1)
        
        # 2. 滑动操作（类似uiautomator2的d.swipe()）
        print("\n👆 滑动操作测试...")
        
        # 上滑
        if idb.swipe_up(duration=1.0):
            print("✅ 上滑成功")
            time.sleep(1)
        
        # 下滑
        if idb.swipe_down(duration=1.0):
            print("✅ 下滑成功")
            time.sleep(1)
        
        # 左滑
        if idb.swipe_left(duration=1.0):
            print("✅ 左滑成功")
            time.sleep(1)
        
        # 右滑
        if idb.swipe_right(duration=1.0):
            print("✅ 右滑成功")
            time.sleep(1)
        
        # 3. 按键操作（类似uiautomator2的d.press()）
        print("\n⌨️ 按键操作测试...")
        if idb.press_key("home"):
            print("✅ Home键按下成功")
            time.sleep(2)
        
        # 重新启动应用
        if idb.app_start(app_bundle_id):
            print("✅ 应用重新启动成功")
            time.sleep(2)
        
        # 4. 元素查找和操作
        print("\n🔍 元素查找和操作测试...")
        
        # 查找按钮元素（类似uiautomator2的d(className="UIButton")）
        button = idb.find_element("UIButton", index=0)
        if button:
            print("✅ 找到按钮元素")
            
            # 点击按钮（类似uiautomator2的d(className="UIButton").click()）
            if idb.tap_element(button):
                print("✅ 按钮点击成功")
                time.sleep(1)
            
            # 长按按钮（类似uiautomator2的d(className="UIButton").long_click()）
            if idb.long_press_element(button, duration=2.0):
                print("✅ 按钮长按成功")
                time.sleep(1)
            
            # 双击按钮
            if idb.double_tap_element(button):
                print("✅ 按钮双击成功")
                time.sleep(1)
        else:
            print("⚠️ 未找到按钮元素")
        
        # 5. 等待元素出现（类似uiautomator2的d(text="登录").wait()）
        print("\n⏳ 等待元素出现测试...")
        element = idb.wait_for_element("Button", label="登录", timeout=5.0)
        if element:
            print("✅ 等待到登录按钮")
            if idb.tap_element(element):
                print("✅ 登录按钮点击成功")
        else:
            print("⚠️ 未找到登录按钮")
        
        # 6. 检查元素是否存在（类似uiautomator2的d(text="登录").exists）
        print("\n🔍 检查元素是否存在...")
        exists = idb.element_exists("Button", label="登录")
        print(f"登录按钮存在: {exists}")
        
        # 7. 获取元素信息（类似uiautomator2的d(text="登录").info）
        print("\n📋 获取元素信息...")
        element_info = idb.get_element_info("Button", label="登录")
        if element_info:
            print(f"元素信息: {element_info}")
        else:
            print("⚠️ 未找到元素")
        
        # 8. 文本输入（类似uiautomator2的d(text="输入框").set_text()）
        print("\n📝 文本输入测试...")
        text_field = idb.find_element("UITextField", index=0)
        if text_field:
            if idb.input_text_to_element(text_field, "测试文本"):
                print("✅ 文本输入成功")
                time.sleep(1)
        else:
            print("⚠️ 未找到文本输入框")
        
        # 9. 拖拽操作（类似uiautomator2的d.drag()）
        print("\n👆 拖拽操作测试...")
        if idb.drag(100, 200, 300, 400, duration=1.0):
            print("✅ 拖拽操作成功")
            time.sleep(1)
        
        # 10. 多指操作（类似uiautomator2的d.pinch()）
        print("\n👆 多指操作测试...")
        if idb.pinch(200, 300, scale=1.5, duration=1.0):
            print("✅ 放大操作成功")
            time.sleep(1)
        
        if idb.pinch(200, 300, scale=0.5, duration=1.0):
            print("✅ 缩小操作成功")
            time.sleep(1)
        
        # 11. 截图（类似uiautomator2的d.screenshot()）
        print("\n📸 截图测试...")
        screenshot_path = idb.screenshot("uiautomator2_aligned_screenshot.png")
        if screenshot_path:
            print(f"✅ 截图保存成功: {screenshot_path}")
        
        # 12. 停止应用（类似uiautomator2的d.app_stop()）
        print("\n🛑 停止应用...")
        if idb.app_stop(app_bundle_id):
            print("✅ 应用停止成功")
        
        # 断开连接
        print("\n🔌 断开设备连接...")
        idb.disconnect()
        print("✅ 设备连接已断开")
        
        print("\n🎉 与uiautomator2对齐的UI自动化示例完成！")
        print("\n📚 主要功能对比:")
        print("✅ 坐标点击: idb.tap_coordinate(x, y)")
        print("✅ 滑动操作: idb.swipe_up/down/left/right()")
        print("✅ 按键操作: idb.press_key(key)")
        print("✅ 元素查找: idb.find_element(type, **kwargs)")
        print("✅ 元素点击: idb.tap_element(element)")
        print("✅ 长按操作: idb.long_press_element(element)")
        print("✅ 双击操作: idb.double_tap_element(element)")
        print("✅ 等待元素: idb.wait_for_element(type, **kwargs)")
        print("✅ 元素存在: idb.element_exists(type, **kwargs)")
        print("✅ 元素信息: idb.get_element_info(type, **kwargs)")
        print("✅ 文本输入: idb.input_text_to_element(element, text)")
        print("✅ 拖拽操作: idb.drag(start_x, start_y, end_x, end_y)")
        print("✅ 多指操作: idb.pinch(center_x, center_y, scale)")
        print("✅ 截图功能: idb.screenshot(path)")
        print("✅ 应用管理: idb.app_start/stop(bundle_id)")
        print("✅ 屏幕信息: idb.get_screen_info()")
        
        return 0
        
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
