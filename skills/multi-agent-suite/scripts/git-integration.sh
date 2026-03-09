#!/bin/bash
#
# 版本控制集成脚本
# 自动Git提交、分支管理
#

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

echo "🔧 Git版本控制集成"
echo "=================="

# 检查git仓库
if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
fi

# 获取当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 自动提交
if [ -n "$2" ]; then
    COMMIT_MSG="$2"
else
    COMMIT_MSG="Auto commit: $(date '+%Y-%m-%d %H:%M')"
fi

echo "添加文件..."
git add -A

echo "提交: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || echo "无更改需要提交"

# 推送
if git remote > /dev/null 2>&1; then
    echo "推送到远程..."
    git push origin "$CURRENT_BRANCH"
fi

echo "✅ Git操作完成"
