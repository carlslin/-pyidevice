# IDB安装指南

## 🚀 安装IDB (iOS Device Bridge)

### 1. 安装IDB Companion

#### macOS (推荐)
```bash
# 使用Homebrew安装
brew install idb-companion

# 验证安装
idb_companion --version
```

#### 手动安装
```bash
# 从GitHub下载最新版本
# https://github.com/facebook/idb/releases

# 下载后解压并添加到PATH
export PATH=$PATH:/path/to/idb-companion
```

### 2. 安装Python客户端

```bash
# 安装IDB Python客户端
pip install idb

# 或者安装开发版本
pip install git+https://github.com/facebook/idb.git#subdirectory=python

# 验证安装
python3 -c "import idb; print('IDB安装成功')"
```

### 3. 启动IDB服务

```bash
# 获取设备UDID
idevice_id -l

# 启动IDB Companion
idb_companion --udid YOUR_DEVICE_UDID

# 服务将在端口8080上运行
# 可以通过 http://localhost:8080 访问
```

### 4. 测试安装

```bash
# 运行测试脚本
python3 test_idb_basic.py
```

## 🔧 故障排除

### 1. IDB Companion安装失败

```bash
# 更新Homebrew
brew update

# 重新安装
brew uninstall idb-companion
brew install idb-companion

# 检查依赖
brew doctor
```

### 2. Python客户端安装失败

```bash
# 升级pip
pip install --upgrade pip

# 使用conda安装
conda install -c conda-forge idb

# 或者使用虚拟环境
python3 -m venv idb_env
source idb_env/bin/activate
pip install idb
```

### 3. 设备连接问题

```bash
# 检查设备连接
idevice_id -l

# 检查设备信任状态
ideviceinfo

# 重启设备
idevice restart

# 重新信任证书
# 在设备上：设置 -> 通用 -> VPN与设备管理 -> 信任开发者
```

### 4. 服务启动失败

```bash
# 检查端口占用
lsof -i :8080

# 杀死占用进程
kill -9 $(lsof -t -i:8080)

# 重新启动服务
idb_companion --udid YOUR_DEVICE_UDID
```

## 📚 相关文档

- [IDB官方文档](https://fbidb.io/)
- [GitHub仓库](https://github.com/facebook/idb)
- [Python客户端文档](https://github.com/facebook/idb/tree/main/python)
- [示例项目](https://github.com/facebook/idb/tree/main/python/examples)

## 🎯 下一步

安装完成后，你可以：

1. 运行测试脚本验证安装
2. 查看IDB快速入门指南
3. 开始使用IDB进行iOS自动化测试

```bash
# 验证安装
python3 test_idb_basic.py

# 查看快速入门
cat IDB快速入门指南.md
```
