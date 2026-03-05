#!/bin/bash

# 每日英文新闻推送脚本
# 新能源 + 科技板块
# 每天 08:30 执行

FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/8c3b0f1e-2d4a-4b5c-9e6f-7a8b9c0d1e2f"
REPORT_FILE="/tmp/daily-english-news-$(date '+%Y%m%d').txt"

echo "📰 Daily English News - $(date '+%Y-%m-%d')" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 这里可以接入 RSS 或 API 获取真实新闻
# 目前使用示例内容，后续可替换为真实数据源

cat >> "$REPORT_FILE" << 'EOF'

🔋 NEW ENERGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title: Tesla Announces New Battery Technology Breakthrough

Tesla has unveiled a revolutionary battery cell design that promises to 
reduce production costs by 50% while increasing energy density by 40%. 
The company plans to begin mass production at its Nevada facility by 
early 2027.

Key Vocabulary:
• breakthrough (n.) - 突破
• revolutionary (adj.) - 革命性的
• energy density - 能量密度
• mass production - 大规模生产
• facility (n.) - 设施，工厂

中文摘要：
特斯拉发布革命性电池技术，生产成本降低50%，能量密度提升40%，
计划2027年初在内华达工厂量产。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 TECHNOLOGY  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title: AI Models Show Significant Improvement in Coding Tasks

Latest research from leading tech companies indicates that large 
language models have achieved human-level performance on standard 
coding benchmarks. The models demonstrate particular strength in 
debugging and code optimization.

Key Vocabulary:
• significant (adj.) - 显著的
• improvement (n.) - 改进，提升
• benchmark (n.) - 基准测试
• demonstrate (v.) - 展示，证明
• debugging (n.) - 调试
• optimization (n.) - 优化

中文摘要：
最新研究表明，大语言模型在编程任务上达到人类水平，
尤其在代码调试和优化方面表现突出。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Reading Tips:
1. 先通读英文，理解大意
2. 对照中文摘要验证理解
3. 记录生词到个人词汇本
4. 尝试用英文复述主要内容

Have a great day of learning! 🚀
EOF

# 发送报告（通过飞书 webhook）
report_content=$(cat "$REPORT_FILE")

# 由于 webhook 可能未配置，先保存到文件供手动查看
# 实际使用时取消下面注释并配置正确的 webhook
# curl -s -X POST "$FEISHU_WEBHOOK" \
#     -H "Content-Type: application/json" \
#     -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$report_content\"}}" \
#     > /dev/null 2>&1

# 输出到日志
cat "$REPORT_FILE" >> /tmp/english-news.log

# 保留最近30天的新闻
find /tmp -name "daily-english-news-*.txt" -mtime +30 -delete 2>/dev/null

echo "✅ Daily English News prepared for $(date '+%Y-%m-%d')"
