#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件发送技能
自动发送文件到指定群聊
"""

import subprocess
import os
import sys

# 默认群聊ID（雪子和我的专属群聊）
DEFAULT_GROUP_CHAT = "chat:oc_aff1ecbfd382d2235daf1d60c922f041"

def send_file(file_path, caption="", channel="feishu", target=None):
    """
    发送文件到指定群聊
    
    Args:
        file_path: 文件路径
        caption: 文件说明文字
        channel: 渠道（默认feishu）
        target: 目标群聊（默认使用配置的群聊）
    
    Returns:
        dict: 发送结果
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"文件不存在: {file_path}"}
    
    target = target or DEFAULT_GROUP_CHAT
    
    # 构建message命令
    cmd = [
        "message", "send",
        "--channel", channel,
        "--target", target,
        "--file", file_path
    ]
    
    if caption:
        cmd.extend(["--message", caption])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_files(file_list, channel="feishu", target=None):
    """
    批量发送多个文件
    
    Args:
        file_list: 文件列表，每个元素是dict包含path和caption
        channel: 渠道
        target: 目标群聊
    
    Returns:
        list: 每个文件的发送结果
    """
    results = []
    for item in file_list:
        path = item.get("path") if isinstance(item, dict) else item
        caption = item.get("caption", "") if isinstance(item, dict) else ""
        result = send_file(path, caption, channel, target)
        results.append({"file": path, "result": result})
    return results

def get_file_info(file_path):
    """获取文件信息"""
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    size_mb = stat.st_size / (1024 * 1024)
    
    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size_bytes": stat.st_size,
        "size_mb": round(size_mb, 2),
        "exists": True
    }

if __name__ == "__main__":
    # 命令行用法
    if len(sys.argv) < 2:
        print("用法: python file-sender.py <文件路径> [说明文字]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) > 2 else ""
    
    result = send_file(file_path, caption)
    
    if result["success"]:
        print(f"✅ 文件发送成功: {file_path}")
    else:
        print(f"❌ 文件发送失败: {result.get('error', '未知错误')}")
        sys.exit(1)
