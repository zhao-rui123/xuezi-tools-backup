#!/usr/bin/env python3
"""
飞书每日总结推送
每晚22:00自动推送当日工作总结
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加tracker路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2')

try:
    from tracker import get_daily_summary
except ImportError:
    print("❌ tracker模块未找到")
    sys.exit(1)

def format_summary(data: dict) -> str:
    """格式化每日总结"""
    
    # 房间停留时间
    room_times = []
    for room_id, seconds in data['room_times']:
        minutes = seconds // 60
        if minutes > 0:
            room_name = {
                'study': '📚书房',
                'workspace': '💻工作室',
                'gameroom': '🎮游戏室',
                'bedroom': '🛏️休息室',
                'bathroom': '🚽卫生间',
                'kitchen': '🍜厨房',
                'playground': '🏃操场'
            }.get(room_id, room_id)
            room_times.append(f"{room_name} {minutes}分钟")
    
    room_text = " → ".join(room_times[:3]) if room_times else "今天没动..."
    
    # 最耗时任务
    longest = data.get('longest_task')
    longest_text = ""
    if longest:
        duration_min = longest['duration_seconds'] // 60
        longest_text = f"\n🏆 最耗时任务：\n{longest['name']} - {duration_min}分钟"
    
    # 组装消息
    message = f"""🦞 雪子助手今日总结 ({data['date']})

🏠 今日足迹：
{room_text}

📊 数据统计：
✅ 完成任务：{data['tasks_completed']}个
🔥 Token消耗：{data['tokens_used']:,}
⏱️ 工作时长：{data['work_time_formatted']}{longest_text}

💬 今日心情：
"{get_mood_message(data)}"

---
晚安，明天继续加油！🌙"""
    
    return message

def get_mood_message(data: dict) -> str:
    """根据数据生成心情文案"""
    tasks = data['tasks_completed']
    tokens = data['tokens_used']
    
    if tasks >= 10:
        return "今天效率爆表！超额完成任务~"
    elif tasks >= 5:
        return "今天状态不错，稳稳完成任务！"
    elif tokens > 10000:
        return "虽然任务不多，但思考很深入~"
    elif 'bathroom' in str(data.get('room_times', [])):
        return "今天搬了不少砖，但也偷偷摸了鱼~"
    else:
        return "轻松的一天，养精蓄锐明天继续！"

def send_feishu_message(message: str):
    """发送飞书消息（使用OpenClaw工具）"""
    print("📤 准备发送飞书消息...")
    print(message)
    
    # 实际使用时调用OpenClaw的消息发送功能
    # 这里先打印到控制台
    print("\n✅ 消息已生成（实际推送需要调用飞书API）")

def main():
    """主函数"""
    print("🦞 生成每日总结...")
    
    # 获取今日数据
    summary = get_daily_summary()
    
    # 格式化消息
    message = format_summary(summary)
    
    # 发送消息
    send_feishu_message(message)
    
    print("\n✅ 每日总结推送完成！")

if __name__ == '__main__':
    main()
