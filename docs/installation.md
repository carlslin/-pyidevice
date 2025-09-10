# 安装指南

本指南将帮助您在 macOS 和 Linux 系统上安装 pyidevice。

## 系统要求

### 操作系统
- **macOS**: 10.14+ (推荐)
- **Linux**: Ubuntu 18.04+ 或其他现代发行版

### Python版本
- Python 3.6+
- pip 包管理器

## 安装系统依赖

### macOS（推荐使用IDB）
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 IDB（推荐，支持iOS 17+）
brew tap facebook/fb
brew install idb-companion

# 安装 IDB Python 客户端
pip3 install fb-idb

# 安装传统依赖（可选）
brew install libimobiledevice ideviceinstaller

# 或者使用 MacPorts
sudo port install libimobiledevice ideviceinstaller
```

### Ubuntu/Debian
```bash
# 更新包列表
sudo apt-get update

# 安装依赖
sudo apt-get install libimobiledevice-utils ideviceinstaller

# 安装开发工具（可选）
sudo apt-get install libimobiledevice-dev
```

### CentOS/RHEL
```bash
# 安装 EPEL 仓库
sudo yum install epel-release

# 安装依赖
sudo yum install libimobiledevice ideviceinstaller
```

## 安装 pyidevice

### 从 PyPI 安装（推荐）
```bash
pip install pyidevice
```

### 从源码安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/pyidevice.git
cd pyidevice

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 开发环境安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/pyidevice.git
cd pyidevice

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装包（开发模式）
pip install -e .
```

## 验证安装

### 检查版本
```bash
pyidevice --version
```

### 验证IDB安装（推荐）
```bash
# 检查IDB Companion
idb_companion --version

# 检查IDB Python客户端
python3 -m idb.cli.main list-targets

# 验证pyidevice IDB集成
python3 -c "from pyidevice import IDBAutomator; print('✅ IDB集成正常')"
```

### 检查环境
```python
import pyidevice

# 检查环境是否满足要求
is_valid, errors = pyidevice.check_environment()
if is_valid:
    print("✅ 环境检查通过")
else:
    print("❌ 环境检查失败:")
    for error in errors:
        print(f"  - {error}")
```

### 测试基本功能
```python
from pyidevice import DeviceManager, IDBAutomator

# 获取设备列表
devices = DeviceManager.get_devices()
print(f"找到 {len(devices)} 个设备")

# 测试IDB连接（如果设备已连接）
if devices:
    idb = IDBAutomator(devices[0])
    if idb.connect():
        print("✅ IDB连接成功")
        idb.disconnect()
    else:
        print("⚠️ IDB连接失败，请启动IDB Companion服务")
```

## 常见问题

### Q: 提示 "idevice_id command not found"
**A**: 请确保已正确安装 libimobiledevice：
```bash
# macOS
brew install libimobiledevice

# Ubuntu/Debian
sudo apt-get install libimobiledevice-utils
```

### Q: 设备连接失败
**A**: 检查以下几点：
1. 设备是否通过USB连接
2. 设备是否信任计算机
3. 设备是否解锁
4. 是否安装了正确的驱动

### Q: 权限错误
**A**: 在 Linux 上可能需要添加用户到相关组：
```bash
sudo usermod -a -G plugdev $USER
```

### Q: Python 版本不兼容
**A**: pyidevice 需要 Python 3.6+，请升级 Python 版本：
```bash
# 使用 pyenv 管理 Python 版本
pyenv install 3.9.0
pyenv global 3.9.0
```

## 卸载

### 卸载 pyidevice
```bash
pip uninstall pyidevice
```

### 卸载系统依赖
```bash
# macOS
brew uninstall libimobiledevice ideviceinstaller

# Ubuntu/Debian
sudo apt-get remove libimobiledevice-utils ideviceinstaller
```

## 下一步

安装完成后，您可以：

1. 查看 [快速开始指南](quickstart.md)
2. 阅读 [IDB快速入门指南](../IDB快速入门指南.md)
3. 查看 [uiautomator2 API对比](../uiautomator2_API对比.md)
4. 阅读 [API 文档](api/)
5. 运行 [示例代码](examples/)

---

*如果遇到其他问题，请查看 [故障排除指南](troubleshooting.md) 或提交 [Issue](https://github.com/yourusername/pyidevice/issues)。*
