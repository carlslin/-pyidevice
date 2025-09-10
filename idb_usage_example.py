#!/usr/bin/env python3
"""
IDB 使用示例
基于 Facebook 官方 IDB: https://github.com/facebook/idb

这个脚本展示了如何使用 pyidevice 的 IDB 集成功能
"""

import time
import sys
import os

def check_idb_installation():
    """检查 IDB 安装状态"""
    print("🔍 检查 IDB 安装状态...")
    
    try:
        import idb
        print("✅ IDB Python 客户端已安装")
    except ImportError:
        print("❌ IDB Python 客户端未安装")
        print("请运行: pip3 install fb-idb")
        return False
    
    try:
        from pyidevice import IDBAutomator
        print("✅ pyidevice IDB 集成已安装")
    except ImportError:
        print("❌ pyidevice 未安装")
        print("请运行: pip install pyidevice")
        return False
    
    return True

def list_devices():
    """列出连接的设备"""
    print("\n📱 列出连接的设备...")
    
    try:
        from pyidevice import DeviceManager
        devices = DeviceManager.get_devices()
        
        if devices:
            print(f"✅ 找到 {len(devices)} 个设备:")
            for i, device in enumerate(devices):
                print(f"  {i+1}. {device}")
            return devices[0]  # 返回第一个设备
        else:
            print("❌ 未找到连接的设备")
            return None
    except Exception as e:
        print(f"❌ 获取设备列表失败: {e}")
        return None

def test_idb_connection(udid):
    """测试 IDB 连接"""
    print(f"\n🔗 测试 IDB 连接到设备: {udid}")
    
    try:
        from pyidevice import IDBAutomator
        
        # 创建 IDB 实例
        idb = IDBAutomator(udid)
        
        # 尝试连接
        if idb.connect():
            print("✅ IDB 连接成功")
            
            # 获取设备信息
            device_info = idb.get_device_info()
            print(f"📊 设备信息:")
            print(f"  名称: {device_info.get('name', 'Unknown')}")
            print(f"  iOS版本: {device_info.get('os_version', 'Unknown')}")
            print(f"  型号: {device_info.get('model', 'Unknown')}")
            
            # 断开连接
            idb.disconnect()
            return True
        else:
            print("❌ IDB 连接失败")
            print("请确保:")
            print("1. IDB Companion 服务正在运行")
            print("2. 设备已信任此计算机")
            print("3. 运行命令: idb_companion --udid YOUR_DEVICE_UDID")
            return False
            
    except Exception as e:
        print(f"❌ IDB 连接测试失败: {e}")
        return False

def test_idb_commands():
    """测试 IDB 命令行工具"""
    print("\n🛠️ 测试 IDB 命令行工具...")
    
    import subprocess
    
    try:
        # 测试 idb list-targets
        result = subprocess.run(['python3', '-m', 'idb.cli.main', 'list-targets'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ IDB 命令行工具正常")
            if result.stdout.strip():
                print("📱 找到的目标设备:")
                print(result.stdout)
            else:
                print("⚠️  未找到目标设备")
        else:
            print("❌ IDB 命令行工具测试失败")
            return False
            
        # 测试 idb list-targets (使用别名)
        try:
            result = subprocess.run(['idb', 'list-targets'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ IDB 别名命令正常")
            else:
                print("⚠️  IDB 别名命令失败，但 Python 模块正常")
        except FileNotFoundError:
            print("ℹ️  IDB 别名未设置，但 Python 模块正常")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ IDB 命令执行超时")
        return False
    except FileNotFoundError:
        print("❌ IDB 命令行工具未找到")
        print("请确保已安装 IDB: pip3 install fb-idb")
        return False
    except Exception as e:
        print(f"❌ IDB 命令测试失败: {e}")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📚 IDB 使用示例:")
    print("=" * 50)
    
    print("\n1. 启动 IDB Companion 服务:")
    print("   idb_companion --udid YOUR_DEVICE_UDID")
    
    print("\n2. 使用 IDB 命令行工具:")
    print("   idb list-targets                    # 列出所有目标")
    print("   idb list-apps --udid YOUR_UDID     # 列出应用")
    print("   idb launch com.apple.Health        # 启动应用")
    print("   idb screenshot screenshot.png      # 截图")
    
    print("\n3. 使用 pyidevice Python API:")
    print("""
from pyidevice import IDBAutomator

# 创建 IDB 实例
idb = IDBAutomator("YOUR_DEVICE_UDID")

# 连接设备
if idb.connect():
    # 启动应用
    idb.app_start("com.apple.Health")
    
    # 查找元素
    element = idb.find_element("Button", label="开始使用")
    if element:
        idb.tap_element(element)
    
    # 截图
    idb.screenshot("screenshot.png")
    
    # 断开连接
    idb.disconnect()
""")

def main():
    """主函数"""
    print("🚀 IDB 使用示例")
    print("基于 Facebook 官方 IDB: https://github.com/facebook/idb")
    print("=" * 60)
    
    # 检查安装
    if not check_idb_installation():
        print("\n❌ 安装检查失败，请先完成 IDB 安装")
        print("运行部署脚本: ./deploy_idb.sh")
        return 1
    
    # 测试命令行工具
    if not test_idb_commands():
        print("\n❌ IDB 命令行工具测试失败")
        return 1
    
    # 列出设备
    device_udid = list_devices()
    if not device_udid:
        print("\n⚠️  未找到设备，跳过连接测试")
    else:
        # 测试连接
        test_idb_connection(device_udid)
    
    # 显示使用示例
    show_usage_examples()
    
    print("\n🎉 IDB 使用示例完成！")
    print("\n📖 更多信息:")
    print("- Facebook IDB 官方仓库: https://github.com/facebook/idb")
    print("- IDB 官方文档: https://fbidb.io")
    print("- pyidevice 文档: 查看项目 README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
