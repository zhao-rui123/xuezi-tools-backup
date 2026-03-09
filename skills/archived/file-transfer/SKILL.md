# 文件传递技能

## 用户首选文件传递方式

### 方式一：腾讯云服务器下载（推荐）

**适用场景**：大文件、Word/Excel/PDF等文档

**步骤**：
1. 上传文件到服务器 `/usr/share/nginx/html/downloads/` 目录
2. 设置文件权限为 644
3. 提供下载链接：`http://106.54.25.161/downloads/文件名`

**命令**：
```bash
# 复制文件到下载目录
scp -i ~/.ssh/zhaorui.pem 本地文件 root@106.54.25.161:/usr/share/nginx/html/downloads/

# 或本地复制后上传
cp 本地文件 /usr/share/nginx/html/downloads/

# 设置权限
ssh -i ~/.ssh/zhaorui.pem root@106.54.25.161 "chmod 644 /usr/share/nginx/html/downloads/文件名"
```

**下载链接格式**：
```
http://106.54.25.161/downloads/文件名
```

---

### 方式二：坚果云备份

**适用场景**：重要文件备份、长期存档

**账号信息**：
- WebDAV地址：https://dav.jianguoyun.com/dav/
- 账号：1034440765@qq.com
- 应用密码：Zr123456
- 备份路径：/OpenClaw/

**上传命令**：
```bash
curl -u "1034440765@qq.com:Zr123456" -T 本地文件 "https://dav.jianguoyun.com/dav/OpenClaw/文件名"
```

---

### 方式三：飞书直接发送

**适用场景**：小文件、快速传递

**工具**：`message` 工具的 `filePath` 参数

---

## 优先级

1. **腾讯云下载** - 大文件、需要稳定下载的场景
2. **坚果云** - 备份、多设备同步
3. **飞书直接发送** - 小文件、快速预览

## 注意事项

- 腾讯云 downloads 目录已创建，权限已设置
- 文件名避免特殊字符，建议使用英文或中文标准命名
- 大文件（>10MB）优先使用腾讯云下载