#!/usr/bin/env python3
"""
IDB 部署验证脚本
基于 Facebook 官方 IDB: https://github.com/facebook/idb

验证 IDB 和 pyidevice 的集成是否正确部署
"""

import sys
import subprocess
import importlib
import platform

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查操作系统
    if platform.system() != "Darwin":
        print("❌ 错误: IDB 只支持 macOS 系统")
        return False
    print("✅ macOS 系统")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print(f"❌ 错误: 需要 Python 3.6+，当前版本: {python_version.major}.{python_version.minor}")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}")
    
    return True

def check_homebrew():
    """检查 Homebrew"""
    print("\n🍺 检查 Homebrew...")
    
    try:
        result = subprocess.run(['brew', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ Homebrew 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ Homebrew 未安装")
        print("请安装 Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    except Exception as e:
        print(f"❌ 检查 Homebrew 失败: {e}")
        return False

def check_xcode_tools():
    """检查 Xcode Command Line Tools"""
    print("\n🛠️ 检查 Xcode Command Line Tools...")
    
    try:
        result = subprocess.run(['xcode-select', '-p'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Xcode Command Line Tools: {result.stdout.strip()}")
            return True
        else:
            print("❌ Xcode Command Line Tools 未安装")
            print("请安装: xcode-select --install")
            return False
    except Exception as e:
        print(f"❌ 检查 Xcode Command Line Tools 失败: {e}")
        return False

def check_idb_companion():
    """检查 IDB Companion"""
    print("\n📱 检查 IDB Companion...")
    
    try:
        result = subprocess.run(['idb_companion', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ IDB Companion: {result.stdout.strip()}")
            return True
        else:
            print("❌ IDB Companion 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ IDB Companion 未安装")
        print("请安装: brew tap facebook/fb && brew install idb-companion")
        return False
    except Exception as e:
        print(f"❌ 检查 IDB Companion 失败: {e}")
        return False

def check_idb_python_client():
    """检查 IDB Python 客户端"""
    print("\n🐍 检查 IDB Python 客户端...")
    
    try:
        import idb
        print("✅ IDB Python 客户端已安装")
        
        # 检查版本
        try:
            result = subprocess.run(['idb', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ IDB 命令行工具: {result.stdout.strip()}")
            else:
                print("⚠️  IDB 命令行工具版本检查失败")
        except Exception as e:
            print(f"⚠️  IDB 命令行工具检查失败: {e}")
        
        return True
    except ImportError:
        print("❌ IDB Python 客户端未安装")
        print("请安装: pip3 install fb-idb")
        return False
    except Exception as e:
        print(f"❌ 检查 IDB Python 客户端失败: {e}")
        return False

def check_pyidevice():
    """检查 pyidevice"""
    print("\n📦 检查 pyidevice...")
    
    try:
        import pyidevice
        print("✅ pyidevice 已安装")
        
        # 检查 IDB 集成
        try:
            from pyidevice import IDBAutomator, IDBWebViewAgent
            print("✅ pyidevice IDB 集成已安装")
            return True
        except ImportError as e:
            print(f"❌ pyidevice IDB 集成未安装: {e}")
            return False
            
    except ImportError:
        print("❌ pyidevice 未安装")
        print("请安装: pip install pyidevice")
        return False
    except Exception as e:
        print(f"❌ 检查 pyidevice 失败: {e}")
        return False

def check_libimobiledevice():
    """检查 libimobiledevice"""
    print("\n📱 检查 libimobiledevice...")
    
    tools = ['idevice_id', 'ideviceinfo', 'ideviceinstaller']
    all_installed = True
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {tool} 已安装")
            else:
                print(f"❌ {tool} 未正确安装")
                all_installed = False
        except FileNotFoundError:
            print(f"❌ {tool} 未安装")
            all_installed = False
        except Exception as e:
            print(f"⚠️  检查 {tool} 失败: {e}")
            all_installed = False
    
    if not all_installed:
        print("请安装 libimobiledevice: brew install libimobiledevice")
    
    return all_installed

def check_device_connection():
    """检查设备连接"""
    print("\n📱 检查设备连接...")
    
    try:
        result = subprocess.run(['idevice_id', '-l'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            devices = result.stdout.strip().split('\n')
            print(f"✅ 找到 {len(devices)} 个连接的设备:")
            for device in devices:
                print(f"  - {device}")
            return devices[0]  # 返回第一个设备
        else:
            print("⚠️  未找到连接的设备")
            print("请确保:")
            print("1. iOS 设备已连接到电脑")
            print("2. 设备已信任此计算机")
            print("3. 设备未锁定")
            return None
    except FileNotFoundError:
        print("❌ idevice_id 命令未找到")
        return None
    except Exception as e:
        print(f"❌ 检查设备连接失败: {e}")
        return None

def test_idb_integration(device_udid):
    """测试 IDB 集成"""
    if not device_udid:
        print("\n⚠️  跳过 IDB 集成测试（无设备连接）")
        return True
    
    print(f"\n🔗 测试 IDB 集成 (设备: {device_udid})...")
    
    try:
        from pyidevice import IDBAutomator
        
        # 创建 IDB 实例
        idb = IDBAutomator(device_udid)
        print("✅ IDBAutomator 实例创建成功")
        
        # 注意：这里不实际连接，因为需要 IDB Companion 服务运行
        print("ℹ️  IDB 集成测试完成（需要手动启动 IDB Companion 服务进行完整测试）")
        print("启动命令: idb_companion --udid YOUR_DEVICE_UDID")
        
        return True
        
    except Exception as e:
        print(f"❌ IDB 集成测试失败: {e}")
        return False

def generate_report(results):
    """生成验证报告"""
    print("\n" + "=" * 60)
    print("📊 IDB 部署验证报告")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"总检查项: {total_checks}")
    print(f"通过检查: {passed_checks}")
    print(f"失败检查: {total_checks - passed_checks}")
    print(f"成功率: {passed_checks/total_checks*100:.1f}%")
    
    print("\n详细结果:")
    for check, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check}: {status}")
    
    if passed_checks == total_checks:
        print("\n🎉 所有检查通过！IDB 部署成功！")
        print("\n下一步:")
        print("1. 启动 IDB Companion 服务: idb_companion --udid YOUR_DEVICE_UDID")
        print("2. 运行使用示例: python3 idb_usage_example.py")
    else:
        print("\n⚠️  部分检查失败，请根据上述提示完成安装")
        print("\n快速修复:")
        print("1. 运行部署脚本: ./deploy_idb.sh")
        print("2. 或手动安装缺失的组件")

def main():
    """主函数"""
    print("🔍 IDB 部署验证")
    print("基于 Facebook 官方 IDB: https://github.com/facebook/idb")
    print("=" * 60)
    
    results = {}
    
    # 执行各项检查
    results["系统要求"] = check_system_requirements()
    results["Homebrew"] = check_homebrew()
    results["Xcode Command Line Tools"] = check_xcode_tools()
    results["IDB Companion"] = check_idb_companion()
    results["IDB Python 客户端"] = check_idb_python_client()
    results["pyidevice"] = check_pyidevice()
    results["libimobiledevice"] = check_libimobiledevice()
    
    # 检查设备连接
    device_udid = check_device_connection()
    results["设备连接"] = device_udid is not None
    
    # 测试 IDB 集成
    results["IDB 集成"] = test_idb_integration(device_udid)
    
    # 生成报告
    generate_report(results)
    
    # 返回退出码
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
