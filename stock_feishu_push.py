#!/usr/bin/env python3
"""
飞书股票推送 - 修复版
使用 feishu-notify.sh 脚本发送消息
"""
import os
import subprocess
import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace')

from stock_analyzer_pro import generate_report

def send_to_feishu(message: str):
    """通过 feishu-notify.sh 脚本发送飞书消息"""
    try:
        notify_script = "/Users/zhaoruicn/.openclaw/workspace/scripts/feishu-notify.sh"
        
        # 设置环境变量
        env = os.environ.copy()
        env['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin'
        env['HOME'] = '/Users/zhaoruicn'
        
        # 使用脚本发送消息
        result = subprocess.run(
            [notify_script, "send", message],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            print(f"脚本错误: {result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False

if __name__ == "__main__":
    report = generate_report()

    # 分段发送（飞书消息长度限制）
    max_len = 3000
    if len(report) > max_len:
        # 发送摘要版本
        summary = report[:max_len] + "\n\n...(报告较长，已截断)"
        success = send_to_feishu(summary)
    else:
        success = send_to_feishu(report)

    if success:
        print("✅ 飞书推送成功")
    else:
        print("❌ 飞书推送失败")
        # 保存到文件
        with open('/tmp/stock_report.txt', 'w') as f:
            f.write(report)
        print("报告已保存到 /tmp/stock_report.txt")