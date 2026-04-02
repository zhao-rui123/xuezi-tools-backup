#!/usr/bin/env python3
"""
Claude Code 图像理解 Skill
通过 Claude Code + MiniMax MCP 的 understand_image 工具进行图像识别
比本地 OCR 准确率高很多，特别适合复杂图表、截图、手写文字等

用法:
  python3 image_understand.py <图片路径> [问题]

示例:
  python3 image_understand.py screenshot.png "请提取图中所有文字"
  python3 image_understand.py table.jpg "这是一个表格，请提取所有行列数据"
"""

import subprocess
import sys
import json
import os

MINIMAX_MCP_PATH = os.path.expanduser("~/.claude/plugins/minimax-mcp/index.js")

def understand_image(image_path: str, question: str = "请详细描述这张图片的所有内容") -> str:
    """调用 Claude Code + MiniMax MCP 进行图像理解"""
    
    prompt = f"""用understand_image分析{image_path}，问题：{question}

请直接输出识别结果，不需要其他解释。"""

    cmd = [
        "claude",
        "--print",
        "--dangerously-skip-permissions",
        prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.expanduser("~/.openclaw/workspace")
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # 去掉可能的 thinking 日志
            if "### 图像识别结果" in output:
                output = output.split("### 图像识别结果")[-1].strip()
            return output
        else:
            return f"❌ Claude Code 执行失败: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "❌ 图像理解超时（120秒）"
    except Exception as e:
        return f"❌ 执行出错: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    image_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "请详细描述这张图片的所有内容"
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        sys.exit(1)
    
    print(f"🖼️  正在识别: {os.path.basename(image_path)}")
    print(f"📝 问题: {question}")
    print("-" * 50)
    
    result = understand_image(image_path, question)
    print(result)
