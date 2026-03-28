# TOOLS.md - Local Notes

## 腾讯云服务器
- **IP**: 106.54.25.161
- **用户名**: root
- **密码**: Zr123456
- **网站目录**: /usr/share/nginx/html/
- **网站地址**: http://106.54.25.161/

## SSH连接（免密）

### Mac mini（我的机器）
```bash
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161
```
私钥：`~/.ssh/id_ed25519`（Mac mini本地生成）

### 雪子笔记本（Windows）
```cmd
ssh -i C:\Users\zhaor\.ssh\id_ed25519 root@106.54.25.161
```
私钥：`C:\Users\zhaor\.ssh\id_ed25519`

**2026-03-26 已添加两台机器的公钥到服务器**

## 飞书群ID（重要！）
- **广播专员群**: oc_b14195eb990ab57ea573e696758ae3d5 ← 股票推送发这里！
- **小说大作手群**: oc_0c0c985c9ed4a8e98030d848240ac6bf
```bash
# 查看网站文件
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "ls -la /usr/share/nginx/html/"

# 上传文件
scp -i ~/.ssh/id_ed25519 localfile.txt root@106.54.25.161:/usr/share/nginx/html/

# 重启nginx
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "nginx -s reload"
```

## Agent-Reach（云服务器）
```bash
# 通过SSH在云服务器上执行agent-reach命令
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "agent-reach doctor"

# 常用命令
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "agent-reach search '关键词'"  # 全网搜索
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "agent-reach read 'URL'"       # 读网页
```
**已安装版本**: v1.3.0
**可用渠道**: YouTube、RSS、全网搜索(Exa)、B站、微信公众号、Jina Reader读网页

## 股票技术分析（云服务器）
```bash
# 在云服务器上运行技术分析脚本
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "python3 /tmp/stock_technical_analysis.py [代码]"

# 支持: MACD、KDJ、RSI、布林带、均线、成交量
# 自动识别沪深市场（6开头=上海，其他=深圳）
```

## Tushare API
- **Token**: d8d89556f8638c1d83426b6038fc04ea96b5da04841a07d99706f10027f3

## MiniMax图片生成API（2026-03-21 新增）

### API地址
- **URL**: `https://api.minimaxi.com/v1/image_generation`
- **模型**: `image-01`
- **认证**: Bearer Token（直接用Token Plan的Key）

### 调用方式
```bash
curl -X POST "https://api.minimaxi.com/v1/image_generation" \
  -H "Authorization: Bearer <TokenPlan Key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"image-01","prompt":"描述","aspect_ratio":"16:9","response_format":"url","n":1}'
```

### 支持参数
- `aspect_ratio`: 1:1, 16:9, 4:3, 3:2, 9:16, 21:9
- `style_type`: 漫画、元气、中世纪、水彩
- `n`: 1-9张
- `prompt_optimizer`: true/false

## 🎨 MiniMax图生图（2026-03-21 新增）

### API地址
- **URL**: `https://api.minimaxi.com/v1/image_generation`

### 图生图调用（subject_reference）
```python
import requests, base64

with open('photo.jpg', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode()

requests.post(
    "https://api.minimaxi.com/v1/image_generation",
    headers={"Authorization": "Bearer <Key>"},
    json={
        "model": "image-01",
        "prompt": "场景描述",
        "subject_reference": [{"type": "character", "image_file": f"data:image/jpeg;base64,{img_base64}"}]
    }
)
```

### 限制
- 只支持1张照片（不能多张）
- base64需小于10MB
- 用最清晰单人正面照效果最好
