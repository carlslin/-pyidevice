#!/usr/bin/env python3
"""
pyidevice 批量操作示例

这个示例展示了如何使用 pyidevice 进行批量操作，包括：
- 批量获取设备信息
- 批量截图
- 批量应用管理
- 批量操作结果处理
"""

from pyidevice import DeviceManager, BatchDeviceManager, BatchAppManager
import json
import os
from datetime import datetime


def main():
    """主函数"""
    print("=== pyidevice 批量操作示例 ===\n")
    
    # 1. 获取所有设备
    print("1. 获取设备列表...")
    devices = DeviceManager.get_devices()
    
    if not devices:
        print("❌ 没有找到连接的设备")
        return
    
    print(f"✅ 找到 {len(devices)} 个设备")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # 2. 批量获取设备信息
    print("\n2. 批量获取设备信息...")
    try:
        batch_manager = BatchDeviceManager(max_workers=3)
        results = batch_manager.get_device_info(devices)
        
        print(f"✅ 批量获取完成: {len(results)} 个结果")
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        print(f"  - 成功: {success_count}")
        print(f"  - 失败: {failed_count}")
        
        # 显示成功的结果
        for result in results:
            if result.success:
                info = result.result
                name = info.get('DeviceName', 'Unknown')
                version = info.get('ProductVersion', 'Unknown')
                print(f"  ✅ {result.udid}: {name} (iOS {version})")
            else:
                print(f"  ❌ {result.udid}: {result.error}")
        
        # 保存结果到文件
        output_file = f"/tmp/device_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        device_infos = []
        for result in results:
            if result.success:
                device_infos.append({
                    'udid': result.udid,
                    'info': result.result,
                    'timestamp': datetime.now().isoformat()
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(device_infos, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 设备信息已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 批量获取设备信息失败: {e}")
    
    # 3. 批量截图
    print("\n3. 批量截图...")
    try:
        # 创建截图目录
        screenshot_dir = "/tmp/batch_screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        batch_manager = BatchDeviceManager(max_workers=2)  # 减少并发数避免资源竞争
        results = batch_manager.take_screenshots(devices, screenshot_dir)
        
        print(f"✅ 批量截图完成: {len(results)} 个结果")
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        print(f"  - 成功: {success_count}")
        print(f"  - 失败: {failed_count}")
        
        # 显示结果
        for result in results:
            if result.success:
                print(f"  ✅ {result.udid}: 截图成功")
            else:
                print(f"  ❌ {result.udid}: {result.error}")
        
        print(f"✅ 截图已保存到: {screenshot_dir}")
        
    except Exception as e:
        print(f"❌ 批量截图失败: {e}")
    
    # 4. 批量应用管理示例（需要实际的应用文件）
    print("\n4. 批量应用管理示例...")
    print("注意: 以下操作需要实际的应用文件，这里仅演示API用法")
    
    # 示例：批量获取应用列表
    try:
        app_manager = BatchAppManager(max_workers=2)
        
        # 这里演示如何批量获取应用列表
        # 注意：BatchAppManager 可能没有 list_apps 方法，这里仅作演示
        print("  - 批量获取应用列表（演示）")
        print("  - 批量安装应用（演示）")
        print("  - 批量卸载应用（演示）")
        
        # 实际使用示例（需要IPA文件）:
        # results = app_manager.install_apps(devices, "/path/to/app.ipa")
        # results = app_manager.uninstall_apps(devices, "com.example.app")
        
    except Exception as e:
        print(f"❌ 批量应用管理失败: {e}")
    
    # 5. 性能统计
    print("\n5. 性能统计...")
    try:
        # 这里可以添加性能统计代码
        print("  - 总操作数: 根据实际执行的操作统计")
        print("  - 平均操作时间: 根据实际执行时间计算")
        print("  - 成功率: 根据成功/失败结果计算")
        
    except Exception as e:
        print(f"❌ 性能统计失败: {e}")
    
    print("\n=== 批量操作示例完成 ===")


def demonstrate_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理示例 ===")
    
    # 使用无效的设备UDID
    invalid_devices = ["invalid_udid_1", "invalid_udid_2"]
    
    try:
        batch_manager = BatchDeviceManager(max_workers=2)
        results = batch_manager.get_device_info(invalid_devices)
        
        print("处理无效设备UDID的结果:")
        for result in results:
            if result.success:
                print(f"  ✅ {result.udid}: {result.result}")
            else:
                print(f"  ❌ {result.udid}: {result.error}")
                
    except Exception as e:
        print(f"❌ 错误处理示例失败: {e}")


if __name__ == "__main__":
    main()
    
    # 运行错误处理示例
    demonstrate_error_handling()
