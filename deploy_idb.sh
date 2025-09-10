#!/bin/bash

# IDB 部署脚本
# 基于 Facebook 官方 IDB 仓库: https://github.com/facebook/idb

set -e

echo "🚀 开始部署 IDB (iOS Device Bridge)"
echo "基于 Facebook 官方 IDB: https://github.com/facebook/idb"
echo ""

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误: IDB 只支持 macOS 系统"
    exit 1
fi

echo "✅ 检测到 macOS 系统"

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew 已安装"
fi

# 检查 Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo "📦 安装 Xcode Command Line Tools..."
    xcode-select --install
    echo "⚠️  请完成 Xcode Command Line Tools 安装后重新运行此脚本"
    exit 1
else
    echo "✅ Xcode Command Line Tools 已安装"
fi

# 检查 Python 3.6+
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.6"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version 已安装"
else
    echo "❌ 错误: 需要 Python 3.6 或更高版本，当前版本: $python_version"
    exit 1
fi

# 安装 IDB Companion
echo ""
echo "📦 安装 IDB Companion..."
if ! command -v idb_companion &> /dev/null; then
    brew tap facebook/fb
    brew install idb-companion
    echo "✅ IDB Companion 安装完成"
else
    echo "✅ IDB Companion 已安装"
fi

# 安装 IDB Python 客户端
echo ""
echo "📦 安装 IDB Python 客户端..."
if ! python3 -c "import idb" &> /dev/null; then
    pip3 install fb-idb
    echo "✅ IDB Python 客户端安装完成"
else
    echo "✅ IDB Python 客户端已安装"
fi

# 安装 pyidevice
echo ""
echo "📦 安装 pyidevice..."
if ! python3 -c "import pyidevice" &> /dev/null; then
    pip install pyidevice
    echo "✅ pyidevice 安装完成"
else
    echo "✅ pyidevice 已安装"
fi

# 验证安装
echo ""
echo "🔍 验证安装..."

echo "IDB Companion 版本:"
idb_companion --version

echo ""
echo "IDB Python 客户端测试:"
python3 -m idb.cli.main list-targets | head -5

echo ""
echo "pyidevice 导入测试:"
python3 -c "import pyidevice; print('✅ pyidevice 导入成功')"

# 检查设备连接
echo ""
echo "📱 检查连接的设备..."
if command -v idevice_id &> /dev/null; then
    devices=$(idevice_id -l)
    if [ -n "$devices" ]; then
        echo "✅ 找到连接的设备:"
        echo "$devices"
    else
        echo "⚠️  未找到连接的设备，请连接 iOS 设备后重试"
    fi
else
    echo "⚠️  idevice_id 命令未找到，请安装 libimobiledevice"
fi

echo ""
echo "🎉 IDB 部署完成！"
echo ""
echo "📚 使用指南:"
echo "1. 启动 IDB Companion 服务:"
echo "   idb_companion --udid YOUR_DEVICE_UDID"
echo ""
echo "2. 使用 IDB 命令行工具:"
echo "   idb list-targets"
echo "   idb list-apps --udid YOUR_DEVICE_UDID"
echo ""
echo "3. 使用 pyidevice Python API:"
echo "   python3 -c \"from pyidevice import IDBAutomator; print('IDB 集成成功')\""
echo ""
echo "📖 更多信息:"
echo "- Facebook IDB 官方仓库: https://github.com/facebook/idb"
echo "- IDB 官方文档: https://fbidb.io"
echo "- pyidevice 文档: 查看项目 README.md"
