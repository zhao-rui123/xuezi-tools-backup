---
name: feishu-file-send
description: 飞书文件发送指南。Use when sending any files (images, documents, text files) via Feishu message tool. Covers correct file paths, screenshot workflows, and document sharing.
---

# 飞书文件发送技能

## 核心规则

**✅ 正确路径**:
- `~/.openclaw/workspace/` —— 生成的文件、截图
- `~/.openclaw/media/inbound/` —— 转发用户发送的文件

**❌ 错误路径**:
- `/tmp/` —— 飞书接收会失败
- `~` 展开路径 —— 可能有解析问题
- 相对路径 `./` —— 可能失效

## 图片发送

### 转发用户图片
```javascript
{
  "action": "send",
  "caption": "图片说明",
  "media": "/Users/zhaoruicn/.openclaw/media/inbound/xxx.png"
}
```

### 屏幕截图并发送
```bash
# 截图保存到 workspace
/usr/sbin/screencapture -x ~/.openclaw/workspace/screenshot.png

# 发送
{
  "action": "send",
  "caption": "屏幕截图",
  "media": "/Users/zhaoruicn/.openclaw/workspace/screenshot.png"
}
```

## 文档发送

### 文本文件 / Word / Excel
```bash
# 创建或复制文件到 workspace
cp document.docx ~/.openclaw/workspace/
```

```javascript
{
  "action": "send",
  "caption": "文档名称",
  "media": "/Users/zhaoruicn/.openclaw/workspace/document.docx"
}
```

## 使用建议

| 场景 | 推荐方案 |
|------|---------|
| 转发用户发的图 | 直接用 inbound 路径 |
| 生成新图片/文档 | 先保存到 workspace，再发 |
| 屏幕截图 | screencapture → workspace → message |
| 紧急发送 | 用飞书 API 脚本 |
| 大图/多图/大文件 | 传网站发 URL |

## 相关配置

- **App ID**: `cli_a928644411785bdf`
- **权限**: `im:resource`, `im:message:send_as_bot`
- **版本**: OpenClaw 2026.2.26

## 更新记录

- 2026-03-03: 发现并验证图片发送解决方案
- 2026-03-04: 扩展支持文档发送（txt/docx/xlsx等）

## 问题描述
OpenClaw 的 `message` 工具在 Mac 上发送本地图片文件存在 bug，返回成功但实际未发送。

## 解决方案

### ✅ 正确方式（已验证）

**方法1：转发用户发送的图片**
```javascript
// 使用 inbound 目录中已存在的图片
{
  "action": "send",
  "target": "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579",
  "caption": "图片说明文字",
  "media": "/Users/zhaoruicn/.openclaw/media/inbound/xxx.png"
}
```

**方法2：通过飞书 API 直接发送**
```bash
#!/bin/bash
# send-feishu-image.sh

APP_ID="cli_a928644411785bdf"
APP_SECRET="qmgZWQq9SQxoiKDOzzsNLfyHr8jBEyLe"
RECEIVE_ID="ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"
IMAGE_PATH="$1"

# 获取 token
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

# 上传图片
UPLOAD_RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@$IMAGE_PATH" \
  "https://open.feishu.cn/open-apis/im/v1/images")

IMAGE_KEY=$(echo "$UPLOAD_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('image_key',''))")

# 发送消息
python3 << PYEOF
import json
import subprocess

content = json.dumps({"image_key": "$IMAGE_KEY"})
data = {
    "receive_id": "$RECEIVE_ID",
    "msg_type": "image",
    "content": content
}

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "-H", "Authorization: Bearer $TOKEN",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(data),
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
], capture_output=True, text=True)

print(result.stdout)
PYEOF
```

**方法3：上传到网站后发 URL**
```bash
# 上传到服务器
sshpass -p 'Zr123456' scp image.png root@106.54.25.161:/usr/share/nginx/html/

# 然后发送 URL 给用户
http://106.54.25.161/image.png
```

### ❌ 错误方式

```javascript
// 这些路径会失败
{ "media": "/tmp/test.png" }           // ❌ /tmp 目录
{ "media": "~/workspace/image.png" }   // ❌ ~ 展开问题
{ "media": "./relative/path.png" }     // ❌ 相对路径可能失效
```

## 关键发现

1. **inbound 目录有效**: `~/.openclaw/media/inbound/` 中的图片可以正常转发
2. **临时目录无效**: `/tmp/` 目录下的图片发送失败
3. **API 调用始终有效**: 直接调用飞书 API 不受此限制

## 截图发送流程

### Mac 屏幕截图并发送

```bash
# 1. 截图保存到 workspace（不要用 /tmp）
/usr/sbin/screencapture -x ~/.openclaw/workspace/screenshot.png

# 2. 使用 message 工具发送
{
  "action": "send",
  "caption": "屏幕截图",
  "media": "/Users/zhaoruicn/.openclaw/workspace/screenshot.png"
}
```

**关键要点：**
- 使用 `/usr/sbin/screencapture`（macOS 内置命令）
- 保存路径必须是 `~/.openclaw/workspace/` 或其子目录
- **绝对不要用** `/tmp/` 目录 —— 飞书会接收失败

## 使用建议

| 场景 | 推荐方案 |
|------|---------|
| 转发用户发的图 | 直接用 inbound 路径 |
| 生成新图片 | 先保存到 workspace，再发 |
| 屏幕截图 | 用 screencapture → workspace → message |
| 紧急发送 | 用 API 脚本 |
| 大图/多图 | 传网站发 URL |

## 相关配置

- **App ID**: `cli_a928644411785bdf`
- **权限**: `im:resource`, `im:message:send_as_bot`
- **版本**: OpenClaw 2026.2.26

## 更新记录

- 2026-03-03: 发现并验证解决方案
