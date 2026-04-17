# 飞书机器人 + Claude Code 连接教程

## 架构图

```
飞书用户 ←→ 飞书机器人 ←→ Claude Code（本地/服务器）
     ↓
   WebSocket 长连接（无需公网IP）
```

---

## 前置要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Node.js | ≥18.0.0 | |
| Claude Code | 任意 | 需已登录 |
| Git | 任意 | 用于克隆 |

---

## 第一步：创建飞书自建应用

### 1. 创建应用

进入 [飞书开放平台](https://open.feishu.cn) → 创建企业自建应用

记录 **App ID** 和 **App Secret**

### 2. 申请权限

在「权限管理」中添加：

```json
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message:send_as_bot",
      "im:message:readonly",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:resource"
    ]
  }
}
```

### 3. 开启机器人能力

「应用功能」→「机器人」→ 保存

### 4. 订阅事件

「事件订阅」→ 选择「**使用长连接接收事件**」（无需公网IP）

添加事件：`im.message.receive_v1`

### 5. 发布应用

「版本管理与发布」→ 创建版本 → 申请发布

---

## 第二步：部署服务

### 1. 克隆项目

```bash
git clone <feishu-claude-code仓库地址>
cd feishu-claude-code
npm install
npm run build
```

### 2. 配置

创建 `.env` 文件：

```bash
# 飞书应用凭证（必填）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# 飞书域名
FEISHU_DOMAIN=feishu  # feishu=国内版，lark=国际版

# Claude Code 工作目录
CLAUDE_WORKDIR=/home/用户名/claude_workspace

# 权限模式
CLAUDE_PERMISSION_MODE=bypassPermissions
```

### 3. 启动服务

```bash
npm start
```

看到以下输出表示成功：
```
[INFO] Claude CLI found
[INFO] feishu-claude-code starting ...
[INFO] ✅ Feishu WebSocket connected. Listening for messages…
```

### 4. 后台运行

```bash
nohup npm start > ~/feishu-cc.log 2>&1 &
echo "PID: $!"
```

查看日志：
```bash
tail -f ~/feishu-cc.log
```

停止服务：
```bash
pkill -f "node dist/index.js"
```

---

## 第三步：开机自启（可选）

### systemd

```bash
sudo tee /etc/systemd/system/feishu-cc.service << 'EOF'
[Unit]
Description=Feishu Claude Code Bridge
After=network.target

[Service]
Type=simple
User=用户名
WorkingDirectory=你的项目路径
EnvironmentFile=你的项目路径/.env
ExecStart=/usr/bin/node 你的项目路径/dist/index.js
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable feishu-cc
sudo systemctl start feishu-cc
```

查看状态：
```bash
sudo systemctl status feishu-cc
sudo journalctl -u feishu-cc -f
```

---

## 配置参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `FEISHU_APP_ID` | **必填** | 飞书应用ID |
| `FEISHU_APP_SECRET` | **必填** | 飞书应用密钥 |
| `FEISHU_DOMAIN` | feishu | feishu/lark |
| `CLAUDE_BIN` | claude | Claude可执行文件路径 |
| `CLAUDE_WORKDIR` | 当前目录 | 工作目录/附件下载目录 |
| `CLAUDE_PERMISSION_MODE` | bypassPermissions | bypassPermissions/acceptEdits/default |
| `CLAUDE_SESSION_TIMEOUT` | 1800000 | 会话超时(毫秒) |
| `CLAUDE_MAX_SESSIONS` | 50 | 最大并发会话数 |
| `BOT_REQUIRE_MENTION` | true | 群聊是否需要@机器人 |
| `BOT_ALLOWED_USER_IDS` | 空 | 用户白名单(open_id逗号分隔) |

---

## 验证是否正常工作

### 1. 确认服务在运行

```bash
ps aux | grep "node dist/index" | grep -v grep
```

### 2. 测试文本对话

- **私聊**：直接给机器人发消息
- **群聊**：@机器人 发消息

预期：机器人先发出「⏳ 思考中…」卡片，随后实时更新，完成后变为绿色「✅」。

### 3. 测试发送附件

向机器人发送图片+文字「描述一下这张图片」

预期：能识别图片并回复描述。

---

## 常见问题

### Q：启动报错 `Claude CLI not found`

```bash
which claude  # 查看路径
# 或在.env中设置完整路径
CLAUDE_BIN=/usr/local/bin/claude
```

### Q：消息发出但机器人没反应

1. 确认事件订阅为「长连接」
2. 检查服务日志：`tail -f ~/feishu-cc.log`

### Q：卡片能发但内容一直是「等待输出…」

通常是 Claude 子进程启动失败，开 debug 日志：
```bash
LOG_LEVEL=debug npm start
```

### Q：发送图片后 Claude 说没有收到

1. 确认已申请 `im:resource` 权限
2. 查看日志是否出现 `File downloaded from message`
3. 确认 `CLAUDE_WORKDIR` 目录存在且有写入权限

---

## 多台机器使用

可以共用同一个飞书应用，消息会随机分发给其中一个客户端。

如需指定路由，建议每台机器使用独立的飞书应用。
