# 贡献指南

欢迎为 pyidevice 项目做出贡献！我们感谢所有形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例

## 🚀 快速开始

### 1. Fork 项目

1. 访问 [pyidevice GitHub 仓库](https://github.com/carlslin/-pyidevice)
2. 点击右上角的 "Fork" 按钮
3. 克隆你的 Fork 到本地：

```bash
git clone git@github.com:YOUR_USERNAME/-pyidevice.git
cd -pyidevice
```

### 2. 设置开发环境

```bash
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

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

## 📝 贡献类型

### 🐛 Bug 报告

如果你发现了一个 Bug，请：

1. 检查 [Issues](https://github.com/carlslin/-pyidevice/issues) 确认问题未被报告
2. 创建新的 Issue，包含：
   - 清晰的标题
   - 详细的复现步骤
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、Python版本、设备信息等）
   - 相关的日志或截图

### 💡 功能建议

我们欢迎新功能的建议！请：

1. 检查 [Issues](https://github.com/carlslin/-pyidevice/issues) 确认功能未被建议
2. 创建新的 Issue，包含：
   - 功能描述
   - 使用场景
   - 可能的实现方案
   - 相关的参考资料

### 🔧 代码贡献

#### 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 使用类型注解
- 添加详细的文档字符串
- 编写单元测试

#### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(idb): add swipe gesture support

Add support for swipe gestures in IDBAutomator class:
- swipe_left()
- swipe_right() 
- swipe_up()
- swipe_down()

Closes #123
```

#### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_idb.py

# 运行测试并生成覆盖率报告
pytest --cov=pyidevice --cov-report=html
```

#### 代码质量检查

```bash
# 代码格式检查
flake8 pyidevice/

# 类型检查
mypy pyidevice/

# 代码格式化
black pyidevice/
```

### 📚 文档贡献

#### 文档类型

- **API 文档**: 更新 `docs/api/README.md`
- **使用指南**: 更新 `docs/quickstart.md`
- **安装指南**: 更新 `docs/installation.md`
- **示例代码**: 在 `docs/examples/` 中添加新示例

#### 文档规范

- 使用 Markdown 格式
- 包含代码示例
- 添加适当的链接
- 保持内容更新

## 🔄 提交流程

### 1. 提交代码

```bash
# 添加修改的文件
git add .

# 提交更改
git commit -m "feat: add new feature"

# 推送到你的 Fork
git push origin feature/your-feature-name
```

### 2. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述，包括：
   - 更改的概述
   - 相关的 Issue 编号
   - 测试说明
   - 截图（如果适用）

### 3. 代码审查

- 维护者会审查你的代码
- 根据反馈进行修改
- 确保所有检查通过

## 🏗️ 项目结构

```
pyidevice/
├── pyidevice/           # 核心代码
│   ├── __init__.py     # 包初始化
│   ├── core.py         # 核心功能
│   ├── device.py       # 设备管理
│   ├── idb.py          # IDB 集成
│   ├── cli.py          # 命令行工具
│   └── ...
├── tests/              # 测试代码
├── docs/               # 文档
├── examples/           # 示例代码
├── .github/            # GitHub 配置
└── README.md           # 项目说明
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_idb.py

# 运行测试并显示覆盖率
pytest --cov=pyidevice --cov-report=term-missing
```

### 编写测试

- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`
- 使用 `pytest` 框架
- 包含正面和负面测试用例
- 使用 Mock 对象隔离外部依赖

示例：
```python
import pytest
from unittest.mock import Mock, patch
from pyidevice import IDBAutomator

def test_idb_connect_success():
    """测试 IDB 连接成功"""
    with patch('pyidevice.idb.idb.Client') as mock_client:
        mock_device = Mock()
        mock_client.return_value.get_device.return_value = mock_device
        
        idb = IDBAutomator("test-udid")
        result = idb.connect()
        
        assert result is True
        assert idb.is_connected() is True
```

## 🐛 调试指南

### 常见问题

1. **IDB 连接失败**
   - 确保 IDB Companion 服务正在运行
   - 检查设备是否信任计算机
   - 验证设备 UDID 是否正确

2. **测试失败**
   - 检查测试环境设置
   - 确保所有依赖已安装
   - 查看测试日志获取详细信息

3. **导入错误**
   - 确保在虚拟环境中
   - 检查 Python 路径设置
   - 验证包是否正确安装

### 调试工具

```bash
# 启用调试日志
export PYIDEVICE_LOG_LEVEL=DEBUG

# 运行特定测试并显示详细输出
pytest -v -s tests/test_idb.py::test_specific_function

# 使用 pdb 调试
python -m pdb your_script.py
```

## 📞 获取帮助

- 📧 创建 [Issue](https://github.com/carlslin/-pyidevice/issues)
- 💬 参与 [Discussions](https://github.com/carlslin/-pyidevice/discussions)
- 📖 查看 [文档](https://github.com/carlslin/-pyidevice/tree/main/docs)

## 📄 许可证

通过贡献代码，你同意你的贡献将在 [MIT 许可证](LICENSE) 下发布。

## 🙏 致谢

感谢所有为 pyidevice 项目做出贡献的开发者！

---

**Happy Contributing! 🎉**
