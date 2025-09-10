#!/bin/bash

# IDB 命令别名脚本
# 由于 fb-idb 包没有提供 idb 命令，我们创建一个别名

# 检查是否已经设置了别名
if ! command -v idb &> /dev/null; then
    echo "设置 IDB 命令别名..."
    
    # 创建 idb 函数
    idb() {
        python3 -m idb.cli.main "$@"
    }
    
    # 导出函数
    export -f idb
    
    echo "✅ IDB 命令别名已设置"
    echo "现在可以使用 'idb' 命令了"
    echo ""
    echo "示例:"
    echo "  idb list-targets"
    echo "  idb list-apps --udid YOUR_UDID"
    echo "  idb launch com.apple.Health --udid YOUR_UDID"
else
    echo "✅ IDB 命令已可用"
fi

# 测试 IDB 命令
echo ""
echo "🔍 测试 IDB 命令..."
idb list-targets | head -3
