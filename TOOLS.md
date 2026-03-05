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

## 常用命令
```bash
# 查看网站文件
sshpass -p 'Zr123456' ssh root@106.54.25.161 "ls -la /usr/share/nginx/html/"

# 上传文件
sshpass -p 'Zr123456' scp localfile.txt root@106.54.25.161:/usr/share/nginx/html/

# 重启nginx
sshpass -p 'Zr123456' ssh root@106.54.25.161 "nginx -s reload"
```
