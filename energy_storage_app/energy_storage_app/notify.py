# -*- coding: utf-8 -*-
"""
飞书通知模块
"""

import requests
import json
import os

# 飞书配置
FEISHU_APP_ID = "cli_a928644411785bdf"
FEISHU_APP_SECRET = ""  # 会从openclaw.json读取

def get_feishu_token():
    """获取飞书tenant_access_token"""
    global FEISHU_APP_SECRET
    if not FEISHU_APP_SECRET:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
            FEISHU_APP_SECRET = config.get('channels', {}).get('feishu', {}).get('appSecret', '')
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result.get('tenant_access_token', '')


def send_feishu_notification(submission):
    """发送提交通知到飞书"""
    token = get_feishu_token()
    if not token:
        print("[ERROR] 无法获取飞书Token")
        return False
    
    # 构造消息
    company = submission.get('company_name', '未填写')
    project = submission.get('project_name', '未填写')
    location = submission.get('project_location', '未填写')
    contact = submission.get('contact_person', '未填写')
    phone = submission.get('contact_phone', '未填写')
    submit_time = submission.get('submit_time', '未知')
    
    message = f"""📋 **新储能项目收资提交**

🏢 公司：{company}
📍 项目：{project}
📌 地点：{location}
👤 对接人：{contact}
📞 联系方式：{phone}

⏰ 提交时间：{submit_time}

🔗 请登录后台查看详情和附件"""

    # 发送消息给雪子
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 雪子的open_id
    receiver_id = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"
    
    data = {
        "receive_id": receiver_id,
        "msg_type": "text",
        "content": json.dumps({"text": message})
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if result.get('code') == 0:
            print(f"[OK] 飞书通知已发送")
            return True
        else:
            print(f"[ERROR] 飞书通知失败: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] 发送异常: {e}")
        return False
