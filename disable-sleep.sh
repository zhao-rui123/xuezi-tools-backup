#!/bin/bash
# Mac mini 禁用休眠设置脚本

echo "当前电源设置："
pmset -g | grep -E "(sleep|disksleep|displaysleep)"

echo ""
echo "正在设置永不休眠..."

# 禁用系统睡眠
sudo pmset -a sleep 0

# 禁用硬盘休眠
sudo pmset -a disksleep 0

# 禁用显示器睡眠（可选，保留10分钟）
sudo pmset -a displaysleep 10

# 插电时永不休眠
sudo pmset -c sleep 0

echo ""
echo "设置完成！新的电源设置："
pmset -g | grep -E "(sleep|disksleep|displaysleep)"

echo ""
echo "✅ Mac mini 现在不会自动休眠了"
echo "💡 提示：可以手动让显示器睡眠（Ctrl+Shift+电源键），但系统会继续运行"
