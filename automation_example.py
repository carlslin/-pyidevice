#!/usr/bin/env python3
"""pyidevice UI自动化功能示例"""

from pyidevice import IDBAutomator, IDBWebViewAgent, DeviceManager
import time


def main():
    print("===== pyidevice UI自动化示例 =====")
    
    # 创建设备管理器并获取设备
    manager = DeviceManager()
    devices = manager.get_devices()
    
    if not devices:
        print("错误: 没有检测到已连接的iOS设备")
        return
    
    udid = devices[0]
    print(f"使用设备: {udid}")
    
    # 初始化IDBAutomator实例
    idb = IDBAutomator(udid=udid)
    
    print("\n正在连接到IDB服务...")
    if not idb.connect():
        print("错误: 无法连接到IDB服务")
        print("请确保:")
        print("1. 已安装IDB Companion: brew install idb-companion")
        print("2. 已安装IDB Python客户端: pip install idb")
        print("3. 设备已信任此计算机")
        return
    
    print("成功连接到IDB服务")
    
    try:
        # 示例：启动设置应用
        print("\n----- 启动设置应用 -----")
        if idb.app_start('com.apple.Preferences'):
            print("设置应用已启动")
            
            # 等待应用加载
            time.sleep(2)
            
            # 示例1：查找并点击通用设置
            print("\n----- 查找并点击通用设置 -----")
            element = idb.find_element("Button", label="通用")
            if element:
                if idb.tap_element(element):
                    print("已点击通用设置")
                    time.sleep(1)
                    
                    # 滑动操作示例
                    print("\n----- 执行向上滑动操作 -----")
                    idb.swipe(200, 400, 200, 200, 1.0)
                    time.sleep(1)
                    
                    print("\n----- 执行向下滑动操作 -----")
                    idb.swipe(200, 200, 200, 400, 1.0)
                    time.sleep(1)
                    
                    # 返回上一页
                    print("\n----- 返回上一页 -----")
                    # iOS设备的返回操作通常是从左边缘向右滑动
                    idb.swipe(10, 300, 100, 300, 0.3)
                    time.sleep(1)
                else:
                    print("点击通用设置失败")
            else:
                print("未找到通用设置选项")
            
            # 示例2：截取屏幕截图
            print("\n----- 截取屏幕截图 -----")
            screenshot_path = 'settings_screenshot.png'
            saved_path = idb.screenshot(screenshot_path)
            if saved_path:
                print(f"屏幕截图已保存到: {saved_path}")
            
            # 停止应用
            print("\n----- 停止设置应用 -----")
            idb.app_stop('com.apple.Preferences')
            
        # 注意：WebView自动化需要有包含WebView的应用，这里仅展示代码结构
        print("\n----- WebView自动化示例（需要有包含WebView的应用）-----")
        print("以下代码展示了如何使用IDBWebViewAgent，但不会实际执行")
        print("\n# 初始化IDBWebViewAgent")
        print("webview_agent = IDBWebViewAgent(idb)")
        print("\n# 启动包含WebView的应用")
        print("# idb.app_start('com.example.webapp')")
        print("\n# 切换到WebView上下文")
        print("# if webview_agent.switch_to_webview():")
        print("#     # 在WebView中查找元素并操作")
        print("#     webview_agent.execute_webview_script('document.getElementById(\"search_input\").value = \"测试\"')")
        print("#     webview_agent.execute_webview_script('document.getElementById(\"search_button\").click()')")
        
    finally:
        # 断开连接
        print("\n断开IDB连接")
        idb.disconnect()
    
    print("\n===== UI自动化示例结束 =====")
    
    # 提示用户IDB的安装方法
    print("\n\n重要提示：")
    print("要使用UI自动化功能，需要安装IDB：")
    print("1. 安装IDB Companion: brew install idb-companion")
    print("2. 安装IDB Python客户端: pip install idb")
    print("3. 启动IDB Companion服务: idb_companion --udid YOUR_DEVICE_UDID")
    print("3. 需要通过Xcode编译并安装到您的设备上")


if __name__ == '__main__':
    main()