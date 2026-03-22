# TOOLS.md - Local Notes

## 腾讯云服务器
- **IP**: 106.54.25.161
- **用户名**: root
- **密码**: Zr123456
- **网站目录**: /usr/share/nginx/html/
- **网站地址**: http://106.54.25.161/

## SSH连接
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161
```

## 飞书群ID（重要！）
- **广播专员群**: oc_b14195eb990ab57ea573e696758ae3d5 ← 股票推送发这里！
- **小说大作手群**: oc_0c0c985c9ed4a8e98030d848240ac6bf
```bash
# 查看网站文件
sshpass -p 'Zr123456' ssh root@106.54.25.161 "ls -la /usr/share/nginx/html/"

# 上传文件
sshpass -p 'Zr123456' scp localfile.txt root@106.54.25.161:/usr/share/nginx/html/

# 重启nginx
sshpass -p 'Zr123456' ssh root@106.54.25.161 "nginx -s reload"
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
