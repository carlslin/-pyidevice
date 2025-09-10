#!/usr/bin/env python3
"""
pyidevice 基本使用示例

这个示例展示了 pyidevice 的基本功能，包括：
- 设备发现和信息获取
- 应用管理
- 屏幕截图
- 设备控制
- IDB UI自动化（推荐）
"""

from pyidevice import DeviceManager, Device, IDBAutomator


def main():
    """主函数"""
    print("=== pyidevice 基本使用示例 ===\n")
    
    # 1. 获取设备列表
    print("1. 获取设备列表...")
    devices = DeviceManager.get_devices()
    
    if not devices:
        print("❌ 没有找到连接的设备")
        print("请确保：")
        print("  - 设备已通过USB连接")
        print("  - 设备已信任计算机")
        print("  - 设备已解锁")
        return
    
    print(f"✅ 找到 {len(devices)} 个设备")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # 2. 选择第一个设备
    device_udid = devices[0]
    device = Device(device_udid)
    
    print(f"\n2. 使用设备: {device_udid}")
    
    # 3. 获取设备基本信息
    print("\n3. 获取设备基本信息...")
    try:
        name = device.name()
        model = device.model()
        version = device.version()
        battery = device.battery_level()
        
        print(f"✅ 设备名称: {name}")
        print(f"✅ 设备型号: {model}")
        print(f"✅ iOS版本: {version}")
        print(f"✅ 电池电量: {battery}%")
    except Exception as e:
        print(f"❌ 获取设备信息失败: {e}")
    
    # 4. 获取详细设备信息
    print("\n4. 获取详细设备信息...")
    try:
        info = device.info()
        print("✅ 设备详细信息:")
        for key, value in list(info.items())[:10]:  # 显示前10个属性
            print(f"  {key}: {value}")
        if len(info) > 10:
            print(f"  ... 还有 {len(info) - 10} 个属性")
    except Exception as e:
        print(f"❌ 获取详细设备信息失败: {e}")
    
    # 5. 列出已安装应用
    print("\n5. 列出已安装应用...")
    try:
        apps = device.list_apps()
        print(f"✅ 已安装 {len(apps)} 个应用")
        
        # 显示前5个应用
        for i, app in enumerate(apps[:5], 1):
            print(f"  {i}. {app['name']} ({app['bundle_id']})")
        
        if len(apps) > 5:
            print(f"  ... 还有 {len(apps) - 5} 个应用")
    except Exception as e:
        print(f"❌ 获取应用列表失败: {e}")
    
    # 6. 截取屏幕截图
    print("\n6. 截取屏幕截图...")
    try:
        screenshot_path = f"/tmp/{device.name()}_screenshot.png"
        success = device.take_screenshot(screenshot_path)
        
        if success:
            print(f"✅ 截图已保存到: {screenshot_path}")
        else:
            print("❌ 截图失败")
    except Exception as e:
        print(f"❌ 截图失败: {e}")
    
    # 7. 获取电池详细信息
    print("\n7. 获取电池详细信息...")
    try:
        battery_info = device.get_battery_info()
        print("✅ 电池详细信息:")
        for key, value in battery_info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ 获取电池信息失败: {e}")
    
    # 8. IDB UI自动化示例（推荐）
    print("\n8. IDB UI自动化示例...")
    try:
        # 初始化IDB自动化器（类似uiautomator2.Device）
        idb = IDBAutomator(device_udid)
        
        # 连接到设备
        if idb.connect():
            print("✅ IDB连接成功")
            
            # 获取屏幕信息（类似uiautomator2的d.info）
            screen_info = idb.get_screen_info()
            if screen_info:
                print(f"✅ 屏幕尺寸: {screen_info['width']}x{screen_info['height']}")
            
            # 启动应用（类似d.app_start）
            app_bundle_id = "com.apple.Health"  # 示例应用
            if idb.app_start(app_bundle_id):
                print(f"✅ 应用启动成功: {app_bundle_id}")
                
                # 坐标点击（类似d.click(x, y)）
                if idb.tap_coordinate(200, 400):
                    print("✅ 坐标点击成功")
                
                # 方向滑动（类似d.swipe_up()）
                if idb.swipe_up():
                    print("✅ 上滑成功")
                
                # 截图（类似d.screenshot()）
                screenshot_path = f"/tmp/{device.name()}_idb_screenshot.png"
                if idb.screenshot(screenshot_path):
                    print(f"✅ IDB截图成功: {screenshot_path}")
                
                # 停止应用（类似d.app_stop()）
                idb.app_stop(app_bundle_id)
                print("✅ 应用停止成功")
            
            # 断开连接
            idb.disconnect()
            print("✅ IDB连接已断开")
        else:
            print("❌ IDB连接失败")
            print("请确保：")
            print("  - IDB Companion服务正在运行")
            print("  - 运行命令: idb_companion --udid YOUR_DEVICE_UDID")
    except Exception as e:
        print(f"❌ IDB自动化失败: {e}")
        print("请参考IDB安装指南: https://github.com/facebook/idb")
    
    print("\n=== 示例完成 ===")
    print("\n📚 更多信息:")
    print("- IDB快速入门指南: ../IDB快速入门指南.md")
    print("- uiautomator2 API对比: ../uiautomator2_API对比.md")
    print("- 完整API文档: ../api/README.md")


if __name__ == "__main__":
    main()
