#!/usr/bin/env python3
"""
pyidevice并发功能示例
本示例展示了如何使用pyidevice库的并发功能来并行操作多个iOS设备
"""
import os
import time
from pyidevice import (
    Device,
    DeviceManager,
    ParallelDeviceExecutor,
    ConcurrentDeviceManager,
    parallel_run
)


# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pyidevice-concurrent-example')


# 定义一些测试用的任务函数
def get_device_info_task(udid):
    """获取设备基本信息的任务"""
    logger.info(f"开始获取设备 {udid} 的信息")
    device = Device(udid)
    info = device.info()
    logger.info(f"完成获取设备 {udid} 的信息")
    return info


def get_battery_info_task(udid):
    """获取设备电池信息的任务"""
    logger.info(f"开始获取设备 {udid} 的电池信息")
    device = Device(udid)
    battery_info = device.get_battery_info()
    logger.info(f"完成获取设备 {udid} 的电池信息")
    return battery_info


def take_screenshot_task(udid, output_dir):
    """截取设备屏幕截图的任务"""
    logger.info(f"开始截取设备 {udid} 的屏幕")
    device = Device(udid)
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    # 生成唯一的文件名
    timestamp = int(time.time())
    output_path = os.path.join(output_dir, f"screenshot_{udid[:8]}_{timestamp}.png")
    # 截取屏幕
    success = device.take_screenshot(output_path)
    logger.info(f"完成截取设备 {udid} 的屏幕，保存至 {output_path}")
    return output_path if success else None


def list_installed_apps_task(udid):
    """列出设备上已安装应用的任务"""
    logger.info(f"开始列出设备 {udid} 上的已安装应用")
    device = Device(udid)
    apps = device.list_installed_apps()
    logger.info(f"完成列出设备 {udid} 上的已安装应用，共 {len(apps)} 个")
    # 只返回应用名称和包名，避免返回过多信息
    return [{"name": app["name"], "bundle_id": app["bundle_id"]} for app in apps[:10]]  # 只返回前10个应用


def main():
    """主函数，展示各种并发操作示例"""
    # 获取所有已连接的设备
    device_manager = DeviceManager()
    udids = device_manager.get_devices()
    
    if not udids:
        logger.error("没有检测到已连接的iOS设备，请连接设备后再试")
        return
    
    logger.info(f"检测到 {len(udids)} 个已连接的iOS设备: {', '.join(udids)}")
    
    # 创建一个临时目录用于保存截图
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    
    print("\n" + "="*60)
    print("示例1: 使用parallel_run函数进行基本并发操作")
    print("="*60)
    # 示例1: 使用parallel_run函数进行基本并发操作
    results = parallel_run(
        udids,
        get_device_info_task,
        max_workers=3,
        executor_type='thread'
    )
    
    for udid, info in results.items():
        print(f"\n设备 {udid} 信息:")
        print(f"  设备名称: {info.get('DeviceName', 'N/A')}")
        print(f"  iOS版本: {info.get('ProductVersion', 'N/A')}")
        print(f"  设备型号: {info.get('ProductType', 'N/A')}")
    
    print("\n" + "="*60)
    print("示例2: 使用ParallelDeviceExecutor类进行高级并发操作")
    print("="*60)
    # 示例2: 使用ParallelDeviceExecutor类进行高级并发操作
    with ParallelDeviceExecutor(max_workers=2, executor_type='thread') as executor:
        # 提交多个不同的任务
        screenshot_tasks = executor.map_tasks(udids, take_screenshot_task, output_dir)
        battery_tasks = executor.map_tasks(udids, get_battery_info_task)
        
        # 等待所有任务完成
        executor.wait_for_completion(screenshot_tasks)
        executor.wait_for_completion(battery_tasks)
        
        # 获取结果
        screenshot_results = executor.get_results(screenshot_tasks)
        battery_results = executor.get_results(battery_tasks)
        
        # 打印结果
        print("\n屏幕截图结果:")
        for udid, path in screenshot_results.items():
            print(f"  设备 {udid}: {path}")
        
        print("\n电池信息结果:")
        for udid, info in battery_results.items():
            print(f"  设备 {udid}: {info}")
    
    print("\n" + "="*60)
    print("示例3: 使用ConcurrentDeviceManager类进行便捷的并发设备管理")
    print("="*60)
    # 示例3: 使用ConcurrentDeviceManager类进行便捷的并发设备管理
    concurrent_manager = ConcurrentDeviceManager(device_manager)
    
    # 1. 在所有设备上执行自定义任务
    custom_results = concurrent_manager.execute_on_all_devices(
        lambda udid: {
            'udid': udid,
            'name': Device(udid).info().get('DeviceName', 'N/A'),
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        max_workers=3
    )
    
    print("\n自定义任务结果:")
    for udid, result in custom_results.items():
        print(f"  设备 {udid}: {result}")
    
    # 2. 批量获取设备信息
    info_results = concurrent_manager.batch_get_info(max_workers=2)
    
    print("\n批量获取设备信息结果:")
    for udid, info in info_results.items():
        print(f"  设备 {udid} 型号: {info.get('ProductType', 'N/A')}")
        print(f"  设备 {udid} iOS版本: {info.get('ProductVersion', 'N/A')}")
    
    # 3. 批量截取屏幕截图
    screenshot_paths = concurrent_manager.batch_screenshot(udids, output_dir, max_workers=2)
    
    print("\n批量截取屏幕截图结果:")
    for udid, path in screenshot_paths.items():
        print(f"  设备 {udid}: {path}")
    
    print("\n" + "="*60)
    print("并发功能测试完成！")
    print("="*60)
    print("\n提示:")
    print("1. 对于IO密集型任务（如设备操作），推荐使用线程池执行器(executor_type='thread')")
    print("2. 对于CPU密集型任务，可考虑使用进程池执行器(executor_type='process')")
    print("3. 可根据实际设备数量和系统资源调整max_workers参数")
    print("4. 所有截图已保存到: " + output_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
        raise