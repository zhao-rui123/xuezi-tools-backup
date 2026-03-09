#!/bin/bash
# System Guard - 定期系统扫描
# 每周扫描所有技能包，检查安全和完整性

set -e

WORKSPACE="$HOME/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
GUARD_DIR="$WORKSPACE/skills/system-guard"
REPORT_FILE="/tmp/system-guard-scan-$(date '+%Y%m%d_%H%M%S').log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================" > "$REPORT_FILE"
echo "  System Guard - 定期系统扫描报告" >> "$REPORT_FILE"
echo "  扫描时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 计数器
TOTAL_SKILLS=0
SAFE_SKILLS=0
WARNING_SKILLS=0
DANGEROUS_SKILLS=0

# 1. 统计技能包数量
echo "📊 技能包统计" >> "$REPORT_FILE"
echo "--------------" >> "$REPORT_FILE"
TOTAL_SKILLS=$(find "$SKILLS_DIR" -maxdepth 1 -type d ! -name "*.tar.gz" | wc -l)
echo "技能包总数: $TOTAL_SKILLS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 2. 扫描每个技能包
echo "🔍 开始安全扫描..." >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    
    # 跳过非目录项和压缩包
    [[ "$skill_name" == *.tar.gz ]] && continue
    [[ ! -d "$skill_dir" ]] && continue
    
    echo "扫描: $skill_name" >> "$REPORT_FILE"
    
    # 检查清单
    CHECKS_PASSED=0
    CHECKS_FAILED=0
    WARNINGS=0
    
    # 2.1 检查 SKILL.md 存在
    if [[ -f "$skill_dir/SKILL.md" ]]; then
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo "  ⚠️ 缺少 SKILL.md" >> "$REPORT_FILE"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 2.2 检查危险代码模式
    DANGER_PATTERNS=(
        "rm -rf /"
        "rm -rf ~"
        "rm -rf \\$HOME"
        "> /dev/sda"
        "mkfs."
        "dd if=/dev/zero"
        ":(){ :|:& };:"
        "curl.*|.*sh"
        "wget.*|.*sh"
        "eval.*\$(curl"
        "eval.*\$(wget"
        "import.*subprocess.*shell=True"
        "os.system.*rm"
        "shutil.rmtree.*~"
    )
    
    for pattern in "${DANGEROSE_PATTERNS[@]}"; do
        if grep -r "$pattern" "$skill_dir" --include="*.py" --include="*.sh" --include="*.js" 2>/dev/null; then
            echo "  ❌ 发现危险代码: $pattern" >> "$REPORT_FILE"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
        fi
    done
    
    # 2.3 检查可疑文件操作
    SUSPICIOUS_PATTERNS=(
        "openclaw.json"
        "agent/models.json"
        "agent/auth"
        ".ssh/"
        ".bashrc"
        ".zshrc"
        "/etc/"
    )
    
    for pattern in "${SUSPICIOUS_PATTERNS[@]}"; do
        if grep -r "$pattern" "$skill_dir" --include="*.py" --include="*.sh" 2>/dev/null | grep -v "SKILL.md" | grep -v "README"; then
            echo "  ⚠️ 可疑文件操作: $pattern" >> "$REPORT_FILE"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
    
    # 2.4 检查硬编码凭证
    if grep -rE "(api_key|apikey|password|token|secret)['\"]?\s*[:=]\s*['\"][a-zA-Z0-9]{20,}" "$skill_dir" --include="*.py" --include="*.json" 2>/dev/null; then
        echo "  ⚠️ 发现可能的硬编码凭证" >> "$REPORT_FILE"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 2.5 检查网络外泄
    if grep -rE "(requests\.(post|get)|urllib|curl|wget).*http" "$skill_dir" --include="*.py" --include="*.sh" 2>/dev/null | grep -v "# " | head -5; then
        echo "  ℹ️ 发现网络请求（需审查）" >> "$REPORT_FILE"
    fi
    
    # 统计结果
    if [[ $CHECKS_FAILED -gt 0 ]]; then
        DANGEROUS_SKILLS=$((DANGEROUS_SKILLS + 1))
        echo "  ❌ 状态: 危险 ($CHECKS_FAILED 个严重问题)" >> "$REPORT_FILE"
    elif [[ $WARNINGS -gt 0 ]]; then
        WARNING_SKILLS=$((WARNING_SKILLS + 1))
        echo "  ⚠️ 状态: 警告 ($WARNINGS 个警告)" >> "$REPORT_FILE"
    else
        SAFE_SKILLS=$((SAFE_SKILLS + 1))
        echo "  ✅ 状态: 安全" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
done

# 3. OpenClaw 配置检查
echo "" >> "$REPORT_FILE"
echo "🔧 OpenClaw 配置检查" >> "$REPORT_FILE"
echo "---------------------" >> "$REPORT_FILE"

# 3.1 检查配置文件
if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
    echo "✅ openclaw.json 存在" >> "$REPORT_FILE"
else
    echo "❌ openclaw.json 缺失" >> "$REPORT_FILE"
fi

# 3.2 检查 Gateway 状态
if pgrep -f "openclaw" > /dev/null; then
    echo "✅ Gateway 运行中" >> "$REPORT_FILE"
else
    echo "⚠️ Gateway 未运行" >> "$REPORT_FILE"
fi

# 4. 生成摘要
echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "  扫描摘要" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "技能包总数:    $TOTAL_SKILLS" >> "$REPORT_FILE"
echo "✅ 安全:       $SAFE_SKILLS" >> "$REPORT_FILE"
echo "⚠️  警告:       $WARNING_SKILLS" >> "$REPORT_FILE"
echo "❌ 危险:       $DANGEROUS_SKILLS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "详细报告: $REPORT_FILE" >> "$REPORT_FILE"

# 输出到控制台
cat "$REPORT_FILE"

# 如果有危险，发送警报
if [[ $DANGEROUS_SKILLS -gt 0 ]]; then
    echo ""
    echo -e "${RED}⚠️  发现 $DANGEROUS_SKILLS 个危险技能包，请立即检查！${NC}"
    
    # 可以在这里添加飞书通知
    # 例如: 发送报告到飞书
fi

echo ""
echo "✅ 扫描完成"
