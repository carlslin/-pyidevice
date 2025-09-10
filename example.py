#!/usr/bin/env python3
"""pyidevice库的使用示例"""

from pyidevice import DeviceManager, Device


def main():
    print("===== pyidevice 示例程序 =====")
    
    # 创建设备管理器
    manager = DeviceManager()
    
    # 列出所有已连接的设备
    devices = manager.get_devices()
    
    if not devices:
        print("没有检测到已连接的iOS设备")
        return
    
    print(f"已检测到 {len(devices)} 个设备:")
    for i, udid in enumerate(devices, 1):
        print(f"{i}. {udid}")
    
    # 选择第一个设备
    selected_udid = devices[0]
    print(f"\n选择设备: {selected_udid}")
    
    # 创建设备实例
    device = Device(selected_udid)
    
    # 获取并显示设备信息
    print("\n----- 设备信息 -----")
    print(f"设备名称: {device.name()}")
    print(f"设备型号: {device.model()}")
    print(f"iOS版本: {device.version()}")
    
    # 获取电池电量
    battery_level = device.battery_level()
    if battery_level >= 0:
        print(f"电池电量: {battery_level}%")
    else:
        print("无法获取电池电量")
    
    # 列出已安装的应用（仅显示前5个）
    print("\n----- 已安装应用（前5个） -----")
    apps = device.list_apps()
    print(f"共安装了 {len(apps)} 个应用")
    
    for i, app in enumerate(apps[:5], 1):
        print(f"{i}. {app['name']} ({app['bundle_id']})")
    
    if len(apps) > 5:
        print(f"... 还有 {len(apps) - 5} 个应用未显示")
    
    print("\n===== 示例程序结束 =====")


if __name__ == '__main__':
    main()