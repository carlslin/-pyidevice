#!/usr/bin/env python3
"""pyidevice IDB自动化功能示例"""

from pyidevice import IDBAutomator, IDBWebViewAgent, DeviceManager
import time
import json


def main():
    print("===== pyidevice IDB自动化示例 =====")
    
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
        print("4. IDB Companion服务正在运行")
        return
    
    print("成功连接到IDB服务")
    
    try:
        # 获取设备信息
        print("\n----- 获取设备信息 -----")
        device_info = idb.get_device_info()
        print(f"设备名称: {device_info.get('name', 'Unknown')}")
        print(f"iOS版本: {device_info.get('os_version', 'Unknown')}")
        print(f"设备型号: {device_info.get('model', 'Unknown')}")
        print(f"电池电量: {device_info.get('battery_level', 'Unknown')}%")
        
        # 获取应用列表
        print("\n----- 获取应用列表 -----")
        apps = idb.app_list()
        print(f"设备上安装了 {len(apps)} 个应用")
        
        # 显示前5个应用
        for i, app in enumerate(apps[:5]):
            print(f"  {i+1}. {app.get('name', 'Unknown')} ({app.get('bundle_id', 'Unknown')})")
        
        # 示例：启动设置应用
        print("\n----- 启动设置应用 -----")
        if idb.app_start('com.apple.Preferences'):
            print("设置应用已启动")
            
            # 等待应用加载
            time.sleep(2)
            
            # 获取当前应用信息
            current_app = idb.app_current()
            print(f"当前应用: {current_app.get('name', 'Unknown')}")
            
            # 示例1：查找并点击通用设置
            print("\n----- 查找并点击通用设置 -----")
            element = idb.find_element("Button", label="通用")
            if element:
                print(f"找到通用按钮: {element.get('label')}")
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
            screenshot_path = 'idb_settings_screenshot.png'
            saved_path = idb.screenshot(screenshot_path)
            if saved_path:
                print(f"屏幕截图已保存到: {saved_path}")
            
            # 示例3：按键操作
            print("\n----- 按键操作示例 -----")
            print("按下Home键")
            idb.press_key("home")
            time.sleep(1)
            
            # 停止应用
            print("\n----- 停止设置应用 -----")
            idb.app_stop('com.apple.Preferences')
        
        # 示例4：文件操作
        print("\n----- 文件操作示例 -----")
        # 创建一个测试文件
        test_content = "Hello from IDB!"
        with open("test_file.txt", "w") as f:
            f.write(test_content)
        
        # 上传文件到设备
        if idb.file_push("test_file.txt", "/tmp/test_file.txt"):
            print("文件上传成功")
            
            # 从设备下载文件
            if idb.file_pull("/tmp/test_file.txt", "downloaded_file.txt"):
                print("文件下载成功")
                
                # 验证文件内容
                with open("downloaded_file.txt", "r") as f:
                    content = f.read()
                    if content == test_content:
                        print("文件内容验证成功")
                    else:
                        print("文件内容验证失败")
        
        # 示例5：性能监控
        print("\n----- 性能监控示例 -----")
        if idb.start_performance_monitoring():
            print("开始性能监控")
            time.sleep(2)
            
            perf_data = idb.get_performance_data()
            print(f"CPU使用率: {perf_data.get('cpu_usage', 'Unknown')}%")
            print(f"内存使用: {perf_data.get('memory_usage', 'Unknown')}MB")
            
            idb.stop_performance_monitoring()
            print("停止性能监控")
        
        # 示例6：网络监控
        print("\n----- 网络监控示例 -----")
        if idb.start_network_monitoring():
            print("开始网络监控")
            time.sleep(2)
            
            network_stats = idb.get_network_stats()
            print(f"发送字节: {network_stats.get('bytes_sent', 'Unknown')}")
            print(f"接收字节: {network_stats.get('bytes_received', 'Unknown')}")
            
            idb.stop_network_monitoring()
            print("停止网络监控")
        
        # 示例7：录屏功能
        print("\n----- 录屏功能示例 -----")
        video_path = "idb_recording.mp4"
        if idb.start_video_recording(video_path):
            print("开始录屏")
            time.sleep(3)
            
            if idb.stop_video_recording():
                print(f"录屏已保存到: {video_path}")
        
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
    
    print("\n===== IDB自动化示例结束 =====")
    
    # 提示用户IDB的安装方法
    print("\n\n重要提示：")
    print("要使用IDB自动化功能，需要安装IDB：")
    print("1. 安装IDB Companion: brew install idb-companion")
    print("2. 安装IDB Python客户端: pip install idb")
    print("3. 启动IDB Companion服务: idb_companion --udid YOUR_DEVICE_UDID")
    print("4. IDB支持iOS 17+设备，性能比WDA更好")


if __name__ == '__main__':
    main()
