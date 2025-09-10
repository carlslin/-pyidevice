# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 添加更多 IDB 自动化示例
- 完善错误处理和日志记录

### 修复
- 修复 IDB 连接超时问题
- 修复元素查找的边界情况

## [0.1.0] - 2024-09-10

### 新增
- 🎉 初始版本发布
- 🚀 完整的 IDB (iOS Device Bridge) 集成
- 🔄 与 uiautomator2 API 对齐，便于迁移
- 📱 原生支持 iOS 17+ 设备
- ⚡ 性能提升 3-5 倍（相比 WDA）
- 🛠️ 完整的 CLI 工具支持
- 📊 实时设备监控和告警系统
- 🔧 批量操作和并发处理
- 📚 完整的文档和示例
- 🧪 196+ 测试用例，95%+ 代码覆盖率

### 核心功能
- **设备管理**: 设备发现、信息获取、应用管理
- **UI 自动化**: 基于 IDB 的现代化自动化操作
- **并发操作**: 多设备并行执行任务
- **实时监控**: 设备状态、电池、温度监控
- **缓存系统**: 提高操作性能
- **性能监控**: 操作性能跟踪和优化

### IDB 集成
- **IDBAutomator**: 主要的 UI 自动化控制器
- **IDBWebViewAgent**: WebView 自动化支持
- **完整 API**: 与 uiautomator2 对齐的 API 设计
- **错误处理**: 专门的 IDB 异常类

### uiautomator2 API 对齐
- `tap_coordinate(x, y)` - 坐标点击
- `swipe_left/right/up/down()` - 方向滑动
- `wait_for_element()` - 等待元素出现
- `element_exists()` - 检查元素存在
- `long_press_element()` - 长按操作
- `double_tap_element()` - 双击操作
- `drag()` - 拖拽操作
- `pinch()` - 多指操作
- `input_text_to_element()` - 向元素输入文本
- `get_screen_info()` - 获取屏幕信息

### CLI 工具
- `pyidevice list` - 列出设备
- `pyidevice info` - 获取设备信息
- `pyidevice screenshot` - 截图
- `pyidevice apps` - 应用管理
- `pyidevice batch` - 批量操作
- `pyidevice monitor` - 设备监控
- `pyidevice idb` - IDB 操作

### 文档
- **安装指南**: 详细的安装步骤
- **快速开始**: 5分钟快速上手
- **API 参考**: 完整的 API 文档
- **示例代码**: 实用的代码示例
- **IDB 指南**: IDB 使用指南
- **API 对比**: 与 uiautomator2 的对比
- **迁移指南**: 从 WDA 迁移到 IDB

### 测试
- **单元测试**: 196+ 测试用例
- **集成测试**: 端到端测试
- **代码覆盖率**: 95%+ 覆盖率
- **CI/CD**: GitHub Actions 自动化测试

### 开发工具
- **代码质量**: black, flake8, mypy
- **预提交钩子**: pre-commit hooks
- **类型注解**: 完整的类型支持
- **文档生成**: Sphinx 文档生成

## [0.0.1] - 2024-09-01

### 新增
- 🎯 项目初始化
- 📱 基础设备管理功能
- 🔧 libimobiledevice 集成
- 📝 基础文档结构

---

## 版本说明

### 版本号格式
- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 变更类型
- **新增**: 新功能
- **修复**: Bug 修复
- **变更**: 现有功能的变更
- **移除**: 移除的功能
- **安全**: 安全相关的修复

### 链接
- [Unreleased]: https://github.com/carlslin/-pyidevice/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/carlslin/-pyidevice/releases/tag/v0.1.0
- [0.0.1]: https://github.com/carlslin/-pyidevice/releases/tag/v0.0.1
