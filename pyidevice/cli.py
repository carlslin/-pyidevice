#!/usr/bin/env python3
import argparse
import sys
import json
import logging
from .core import DeviceManager
from .device import Device

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="pyidevice_cli.log",  # 日志文件
    filemode="a",
)
logger = logging.getLogger("pyidevice_cli")


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="pyidevice - A tool similar to tidevice based on libimobiledevice"
    )
    parser.add_argument("--version", action="store_true", help="Show version")

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list命令：列出设备
    list_parser = subparsers.add_parser("list", help="List connected devices")

    # info命令：获取设备信息
    info_parser = subparsers.add_parser("info", help="Get device information")
    info_parser.add_argument("-u", "--udid", help="Device UDID")

    # install命令：安装应用
    install_parser = subparsers.add_parser("install", help="Install IPA to device")
    install_parser.add_argument("-u", "--udid", help="Device UDID")
    install_parser.add_argument("ipa_path", help="Path to IPA file")

    # uninstall命令：卸载应用
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall app from device")
    uninstall_parser.add_argument("-u", "--udid", help="Device UDID")
    uninstall_parser.add_argument("bundle_id", help="App bundle ID")

    # apps命令：列出已安装的应用
    apps_parser = subparsers.add_parser("apps", help="List installed apps")
    apps_parser.add_argument("-u", "--udid", help="Device UDID")

    # screenshot命令：截取屏幕截图
    screenshot_parser = subparsers.add_parser("screenshot", help="Take screenshot")
    screenshot_parser.add_argument("-u", "--udid", help="Device UDID")
    screenshot_parser.add_argument("output_path", help="Output path for screenshot")

    # run命令：启动应用
    run_parser = subparsers.add_parser("run", help="Run app")
    run_parser.add_argument("-u", "--udid", help="Device UDID")
    run_parser.add_argument("bundle_id", help="App bundle ID")

    # reboot命令：重启设备
    reboot_parser = subparsers.add_parser("reboot", help="Reboot device")
    reboot_parser.add_argument("-u", "--udid", help="Device UDID")

    # shutdown命令：关机
    shutdown_parser = subparsers.add_parser("shutdown", help="Shutdown device")
    shutdown_parser.add_argument("-u", "--udid", help="Device UDID")

    # batch命令：批量操作
    batch_parser = subparsers.add_parser("batch", help="Batch operations")
    batch_subparsers = batch_parser.add_subparsers(dest="batch_command", help="Batch commands")

    # 批量安装
    batch_install_parser = batch_subparsers.add_parser("install", help="Batch install apps")
    batch_install_parser.add_argument("ipa_path", help="Path to IPA file")
    batch_install_parser.add_argument("--workers", type=int, default=3, help="Number of workers")

    # 批量卸载
    batch_uninstall_parser = batch_subparsers.add_parser("uninstall", help="Batch uninstall apps")
    batch_uninstall_parser.add_argument("bundle_id", help="App bundle ID")
    batch_uninstall_parser.add_argument("--workers", type=int, default=3, help="Number of workers")

    # 批量截图
    batch_screenshot_parser = batch_subparsers.add_parser(
        "screenshot", help="Batch take screenshots"
    )
    batch_screenshot_parser.add_argument("output_dir", help="Output directory for screenshots")
    batch_screenshot_parser.add_argument("--workers", type=int, default=3, help="Number of workers")

    # 批量获取信息
    batch_info_parser = batch_subparsers.add_parser("info", help="Batch get device info")
    batch_info_parser.add_argument("--workers", type=int, default=3, help="Number of workers")
    batch_info_parser.add_argument("--output", help="Output file for device info")

    # monitor命令：设备监控
    monitor_parser = subparsers.add_parser("monitor", help="Monitor devices")
    monitor_parser.add_argument(
        "--interval", type=int, default=5, help="Monitoring interval in seconds"
    )
    monitor_parser.add_argument("--duration", type=int, help="Monitoring duration in seconds")
    monitor_parser.add_argument("--alerts", action="store_true", help="Enable alerts")

    # idb命令：IDB操作
    idb_parser = subparsers.add_parser("idb", help="IDB (iOS Device Bridge) operations")
    idb_subparsers = idb_parser.add_subparsers(dest="idb_command", help="IDB commands")

    # IDB连接
    idb_connect_parser = idb_subparsers.add_parser("connect", help="Connect to IDB")
    idb_connect_parser.add_argument("-u", "--udid", help="Device UDID")
    idb_connect_parser.add_argument("--host", default="localhost", help="IDB Companion host")
    idb_connect_parser.add_argument("--port", type=int, default=8080, help="IDB Companion port")

    # IDB状态
    idb_status_parser = idb_subparsers.add_parser("status", help="Get IDB status")
    idb_status_parser.add_argument("-u", "--udid", help="Device UDID")
    idb_status_parser.add_argument("--host", default="localhost", help="IDB Companion host")
    idb_status_parser.add_argument("--port", type=int, default=8080, help="IDB Companion port")

    # IDB截图
    idb_screenshot_parser = idb_subparsers.add_parser("screenshot", help="Take IDB screenshot")
    idb_screenshot_parser.add_argument("-u", "--udid", help="Device UDID")
    idb_screenshot_parser.add_argument("--host", default="localhost", help="IDB Companion host")
    idb_screenshot_parser.add_argument("--port", type=int, default=8080, help="IDB Companion port")
    idb_screenshot_parser.add_argument("output_path", help="Output path for screenshot")

    # IDB应用操作
    idb_app_parser = idb_subparsers.add_parser("app", help="IDB app operations")
    idb_app_subparsers = idb_app_parser.add_subparsers(dest="app_command", help="App commands")
    
    # 启动应用
    idb_app_launch_parser = idb_app_subparsers.add_parser("launch", help="Launch app")
    idb_app_launch_parser.add_argument("-u", "--udid", help="Device UDID")
    idb_app_launch_parser.add_argument("bundle_id", help="App bundle ID")
    
    # 停止应用
    idb_app_stop_parser = idb_app_subparsers.add_parser("stop", help="Stop app")
    idb_app_stop_parser.add_argument("-u", "--udid", help="Device UDID")
    idb_app_stop_parser.add_argument("bundle_id", help="App bundle ID")
    
    # 获取当前应用
    idb_app_current_parser = idb_app_subparsers.add_parser("current", help="Get current app")
    idb_app_current_parser.add_argument("-u", "--udid", help="Device UDID")
    
    # 列出应用
    idb_app_list_parser = idb_app_subparsers.add_parser("list", help="List apps")
    idb_app_list_parser.add_argument("-u", "--udid", help="Device UDID")


    args = parser.parse_args()

    # 处理--version参数
    if args.version:
        from . import __version__

        print(f"pyidevice {__version__}")
        logger.info(f"pyidevice {__version__} started")
        return 0

    # 处理子命令
    if not args.command:
        parser.print_help()
        logger.warning("No command specified")
        return 1

    # 根据命令执行相应的操作
    if args.command == "list":
        devices = DeviceManager.get_devices()
        if not devices:
            print("No devices connected")
            logger.info("No devices connected")
        else:
            for device in devices:
                print(device)
            logger.info(f"Listed {len(devices)} connected devices")
        return 0

    # 对于需要设备的命令，获取设备UDID
    udid = args.udid
    if not udid:
        # 自动选择第一个设备
        udid = DeviceManager.get_first_device()
        if not udid:
            print("No devices connected")
            logger.error("No devices connected")
            return 1
        print(f"Using device: {udid}")
        logger.info(f"Auto-selected device: {udid}")
    elif not DeviceManager.is_device_connected(udid):
        print(f"Device with UDID {udid} is not connected")
        logger.error(f"Device with UDID {udid} is not connected")
        return 1

    device = Device(udid)
    logger.info(f"Using device: {udid}")

    # 执行具体命令
    if args.command == "info":
        info = device.info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
        logger.info(f"Retrieved device info for {udid}")
        return 0

    elif args.command == "install":
        success = device.install_app(args.ipa_path)
        print("Installation succeeded" if success else "Installation failed")
        logger.info(
            f"App installation {'succeeded' if success else 'failed'} for device {udid}, IPA: {args.ipa_path}"
        )
        return 0 if success else 1

    elif args.command == "uninstall":
        success = device.uninstall_app(args.bundle_id)
        print("Uninstallation succeeded" if success else "Uninstallation failed")
        logger.info(
            f"App uninstallation {'succeeded' if success else 'failed'} for device {udid}, bundle ID: {args.bundle_id}"
        )
        return 0 if success else 1

    elif args.command == "apps":
        apps = device.list_apps()
        print(json.dumps(apps, indent=2, ensure_ascii=False))
        logger.info(f"Listed {len(apps)} installed apps on device {udid}")
        return 0

    elif args.command == "screenshot":
        success = device.take_screenshot(args.output_path)
        print(f"Screenshot saved to {args.output_path}" if success else "Failed to take screenshot")
        logger.info(
            f"Screenshot {'saved to ' + args.output_path if success else 'failed'} for device {udid}"
        )
        return 0 if success else 1

    elif args.command == "run":
        success = device.start_app(args.bundle_id)
        print(f"App {args.bundle_id} started" if success else "Failed to start app")
        logger.info(
            f"App {args.bundle_id} {'started' if success else 'failed to start'} on device {udid}"
        )
        return 0 if success else 1

    elif args.command == "reboot":
        success = device.reboot()
        print("Device rebooting" if success else "Failed to reboot device")
        logger.info(f"Device {udid} {'rebooting' if success else 'failed to reboot'}")
        return 0 if success else 1

    elif args.command == "shutdown":
        success = device.shutdown()
        print("Device shutting down" if success else "Failed to shutdown device")
        logger.info(f"Device {udid} {'shutting down' if success else 'failed to shutdown'}")
        return 0 if success else 1

    elif args.command == "batch":
        return handle_batch_command(args)

    elif args.command == "monitor":
        return handle_monitor_command(args)

    elif args.command == "idb":
        return handle_idb_command(args)

    # 如果命令不在上述列表中
    logger.warning(f"Unknown command: {args.command}")
    print(f"Unknown command: {args.command}")
    parser.print_help()
    return 1


def handle_batch_command(args):
    """处理批量操作命令"""
    from .batch import BatchAppManager, BatchDeviceManager

    devices = DeviceManager.get_devices()
    if not devices:
        print("No devices connected")
        logger.error("No devices connected")
        return 1

    print(f"Found {len(devices)} devices for batch operation")

    if args.batch_command == "install":
        manager = BatchAppManager(max_workers=args.workers)
        results = manager.install_apps(devices, args.ipa_path)

        success_count = sum(1 for r in results if r.success)
        print(f"Batch install completed: {success_count}/{len(results)} successful")
        logger.info(f"Batch install completed: {success_count}/{len(results)} successful")
        return 0 if success_count == len(results) else 1

    elif args.batch_command == "uninstall":
        manager = BatchAppManager(max_workers=args.workers)
        results = manager.uninstall_apps(devices, args.bundle_id)

        success_count = sum(1 for r in results if r.success)
        print(f"Batch uninstall completed: {success_count}/{len(results)} successful")
        logger.info(f"Batch uninstall completed: {success_count}/{len(results)} successful")
        return 0 if success_count == len(results) else 1

    elif args.batch_command == "screenshot":
        import os

        os.makedirs(args.output_dir, exist_ok=True)

        manager = BatchDeviceManager(max_workers=args.workers)
        results = manager.take_screenshots(devices, args.output_dir)

        success_count = sum(1 for r in results if r.success)
        print(f"Batch screenshot completed: {success_count}/{len(results)} successful")
        logger.info(f"Batch screenshot completed: {success_count}/{len(results)} successful")
        return 0 if success_count == len(results) else 1

    elif args.batch_command == "info":
        manager = BatchDeviceManager(max_workers=args.workers)
        results = manager.get_device_info(devices)

        success_count = sum(1 for r in results if r.success)
        print(f"Batch info completed: {success_count}/{len(results)} successful")

        # 输出到文件或控制台
        if args.output:
            import json

            device_infos = []
            for result in results:
                if result.success:
                    device_infos.append({"udid": result.udid, "info": result.result})

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(device_infos, f, indent=2, ensure_ascii=False)
            print(f"Device info saved to {args.output}")
        else:
            for result in results:
                if result.success:
                    print(f"Device {result.udid}: {result.result.get('DeviceName', 'Unknown')}")

        logger.info(f"Batch info completed: {success_count}/{len(results)} successful")
        return 0 if success_count == len(results) else 1

    else:
        print(f"Unknown batch command: {args.batch_command}")
        return 1


def handle_monitor_command(args):
    """处理监控命令"""
    from .monitor import device_monitor, alert_manager
    import time
    import signal

    devices = DeviceManager.get_devices()
    if not devices:
        print("No devices connected")
        logger.error("No devices connected")
        return 1

    print(f"Starting monitoring for {len(devices)} devices...")
    print(f"Monitoring interval: {args.interval} seconds")
    if args.duration:
        print(f"Monitoring duration: {args.duration} seconds")
    if args.alerts:
        print("Alerts enabled")

    # 设置监控回调
    def on_device_update(metrics):
        print(f"Device {metrics.udid}: {metrics.status}, Battery: {metrics.battery_level}%")

    def on_alert(alert_name, severity, alert_data):
        print(f"🚨 ALERT: {alert_name} ({severity}) - {alert_data['message']}")

    device_monitor.add_callback(on_device_update)
    if args.alerts:
        alert_manager.add_alert_callback(on_alert)

    # 开始监控
    device_monitor.start_monitoring(devices)

    try:
        if args.duration:
            time.sleep(args.duration)
        else:
            # 无限监控直到用户中断
            while True:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        device_monitor.stop_monitoring()
        print("Monitoring stopped")

    return 0


def handle_idb_command(args):
    """处理IDB命令"""
    from .idb import IDBAutomator

    # 获取设备UDID
    udid = args.udid
    if not udid:
        udid = DeviceManager.get_first_device()
        if not udid:
            print("No devices connected")
            logger.error("No devices connected")
            return 1
        print(f"Using device: {udid}")

    idb = IDBAutomator(udid, host=args.host, port=args.port)

    if args.idb_command == "connect":
        try:
            success = idb.connect()
            if success:
                print(f"Connected to IDB at {args.host}:{args.port}")
                logger.info(f"Connected to IDB at {args.host}:{args.port} for device {udid}")
                return 0
            else:
                print("Failed to connect to IDB")
                logger.error(f"Failed to connect to IDB for device {udid}")
                return 1
        except Exception as e:
            print(f"Failed to connect to IDB: {e}")
            logger.error(f"Failed to connect to IDB: {e}")
            return 1

    elif args.idb_command == "status":
        try:
            success = idb.connect()
            if not success:
                print("Failed to connect to IDB")
                return 1
                
            info = idb.get_device_info()
            print(json.dumps(info, indent=2, ensure_ascii=False))
            logger.info(f"Retrieved IDB status for device {udid}")
            return 0
        except Exception as e:
            print(f"Failed to get IDB status: {e}")
            logger.error(f"Failed to get IDB status: {e}")
            return 1

    elif args.idb_command == "screenshot":
        try:
            success = idb.connect()
            if not success:
                print("Failed to connect to IDB")
                return 1
                
            screenshot_path = idb.screenshot(args.output_path)
            if screenshot_path:
                print(f"IDB screenshot saved to {screenshot_path}")
                logger.info(f"IDB screenshot saved to {screenshot_path} for device {udid}")
                return 0
            else:
                print("Failed to take IDB screenshot")
                logger.error(f"Failed to take IDB screenshot for device {udid}")
                return 1
        except Exception as e:
            print(f"Failed to take IDB screenshot: {e}")
            logger.error(f"Failed to take IDB screenshot: {e}")
            return 1

    elif args.idb_command == "app":
        return handle_idb_app_command(args, idb)

    else:
        print(f"Unknown IDB command: {args.idb_command}")
        return 1


def handle_idb_app_command(args, idb):
    """处理IDB应用命令"""
    try:
        if not idb.is_connected():
            success = idb.connect()
            if not success:
                print("Failed to connect to IDB")
                return 1

        if args.app_command == "launch":
            success = idb.app_start(args.bundle_id)
            if success:
                print(f"App {args.bundle_id} launched successfully")
                return 0
            else:
                print(f"Failed to launch app {args.bundle_id}")
                return 1

        elif args.app_command == "stop":
            success = idb.app_stop(args.bundle_id)
            if success:
                print(f"App {args.bundle_id} stopped successfully")
                return 0
            else:
                print(f"Failed to stop app {args.bundle_id}")
                return 1

        elif args.app_command == "current":
            current_app = idb.app_current()
            print(json.dumps(current_app, indent=2, ensure_ascii=False))
            return 0

        elif args.app_command == "list":
            apps = idb.app_list()
            print(f"Found {len(apps)} apps:")
            for app in apps:
                print(f"  {app.get('name', 'Unknown')} ({app.get('bundle_id', 'Unknown')})")
            return 0

        else:
            print(f"Unknown app command: {args.app_command}")
            return 1

    except Exception as e:
        print(f"Failed to execute app command: {e}")
        logger.error(f"Failed to execute app command: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
