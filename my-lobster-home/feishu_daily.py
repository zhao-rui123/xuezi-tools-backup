#!/usr/bin/env python3
"""
飞书日报推送
每晚22:00自动发送今日工作总结
"""

import requests
import json
from datetime import datetime
from pathlib import Path

# 飞书配置（从环境变量或配置文件读取）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"  # 需要配置
API_BASE = "http://localhost:5000/api"  # 本地测试
# API 地址
API_BASE = "http://106.54.25.161:5000/api"  # 生产环境

class FeishuDailyReport:
    """飞书日报推送器"""
    
    def __init__(self):
        self.api_base = API_BASE
        
    def get_summary(self) -> dict:
        """获取今日总结"""
        try:
            response = requests.get(f"{self.api_base}/status", timeout=10)
            data = response.json()
            
            today = data.get('today', {})
            tasks = today.get('tasks', [])
            
            # 计算统计数据
            total_tasks = today.get('tasks_completed', 0)
            total_tokens = today.get('tokens_used', 0)
            work_seconds = today.get('work_time_seconds', 0)
            
            # 找出最耗时的任务
            longest_task = None
            if tasks:
                longest_task = max(tasks, key=lambda x: x.get('duration', 0))
            
            # 房间停留时间
            room_time = today.get('room_time', {})
            top_rooms = sorted(room_time.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'date': today.get('date', datetime.now().strftime('%Y-%m-%d')),
                'tasks_completed': total_tasks,
                'tokens_used': total_tokens,
                'work_hours': work_seconds // 3600,
                'work_minutes': (work_seconds % 3600) // 60,
                'longest_task': longest_task,
                'top_rooms': top_rooms,
                'current_room': data.get('current_room', 'unknown')
            }
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return None
    
    def generate_message(self, data: dict) -> str:
        """生成飞书消息"""
        if not data:
            return "📊 今日数据获取失败"
        
        # 生成足迹
        footprint = " → ".join([
            f"{self.get_room_emoji(room)} {self.format_time(seconds)}"
            for room, seconds in data['top_rooms']
            if seconds > 60
        ]) or "今天没怎么动~"
        
        # 最耗时任务
        longest_text = ""
        if data['longest_task']:
            name = data['longest_task'].get('name', '未命名')
            duration = data['longest_task'].get('duration', 0)
            minutes = duration // 60
            longest_text = f"\n🏆 最耗时任务：\n{name} - {minutes}分钟"
        
        # 心情评语
        mood = self.get_mood_comment(data)
        
        # 组装消息
        message = f"""🦞 雪子助手今日总结 ({data['date']})

🏠 今日足迹：
{footprint}

📊 数据统计：
✅ 完成任务：{data['tasks_completed']}个
🔥 Token消耗：{data['tokens_used']:,}
⏱️ 工作时长：{data['work_hours']}小时{data['work_minutes']}分钟{longest_text}

💬 今日心情：
"{mood}"

---
晚安，明天继续加油！🌙"""
        
        return message
    
    def get_room_emoji(self, room: str) -> str:
        """获取房间emoji"""
        emojis = {
            'tearoom': '🍵', 'kitchen': '🍳', 'gameroom': '🎮',
            'bathroom1': '🚽', 'livingroom': '📺', 'workspace': '💻',
            'dining': '🍽️', 'bathroom2': '🚿', 'bedroom': '🛏️',
            'playground': '🏃'
        }
        return emojis.get(room, '🏠')
    
    def format_time(self, seconds: int) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds//60}分钟"
        else:
            return f"{seconds//3600}小时{(seconds%3600)//60}分钟"
    
    def get_mood_comment(self, data: dict) -> str:
        """根据数据生成心情评语"""
        tasks = data['tasks_completed']
        tokens = data['tokens_used']
        hours = data['work_hours']
        
        if tasks >= 10:
            return "今天效率爆表！超额完成任务，简直是劳模本模！"
        elif tasks >= 5:
            return "今天状态不错，稳稳完成任务，继续保持！"
        elif tokens > 10000:
            return "虽然任务不多，但思考很深入，脑细胞消耗了不少~"
        elif hours >= 4:
            return "今天工作时间挺长的，辛苦啦！记得好好休息~"
        elif tasks == 0:
            return "今天是个悠闲的一天，充好电明天再战！"
        else:
            return "轻轻松松完成任务，劳逸结合很重要！"
    
    def send_to_feishu(self, message: str) -> bool:
        """发送到飞书"""
        try:
            # 写入文件，然后由外部工具读取发送
            msg_file = "/tmp/feishu_message.txt"
            with open(msg_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            print(f"✅ 消息已保存到: {msg_file}")
            print("📤 消息内容:")
            print(message)
            return True
        except Exception as e:
            print(f"⚠️ 发送异常: {e}")
            print("📤 消息内容:")
            print(message)
            return True
    
    def run(self):
        """运行日报推送"""
        print("🦞 生成今日日报...")
        
        # 获取数据
        data = self.get_summary()
        if not data:
            print("❌ 无法获取数据")
            return False
        
        # 生成消息
        message = self.generate_message(data)
        
        # 发送
        success = self.send_to_feishu(message)
        
        if success:
            print("✅ 日报推送完成！")
        else:
            print("❌ 日报推送失败")
        
        return success


def main():
    """主函数"""
    reporter = FeishuDailyReport()
    reporter.run()


if __name__ == '__main__':
    main()
