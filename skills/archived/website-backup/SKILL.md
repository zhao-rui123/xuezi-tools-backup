# 网站备份技能

## 备份命令（标准版）

```bash
# 进入网站目录
cd /usr/share/nginx/html

# 打包备份（排除 downloads 目录下的 tar.gz 文件，避免循环备份）
tar -czvf /tmp/xuezi-tools-backup-$(date +%Y-%m-%d).tar.gz \
  --exclude='downloads/*.tar.gz' \
  --exclude='node_modules' \
  .
```

## 说明

| 排除项 | 原因 |
|--------|------|
| `downloads/*.tar.gz` | 避免备份文件包含自身，造成循环嵌套 |
| `node_modules` | 依赖包可通过 package.json 重新安装 |

## 恢复命令

```bash
tar -xzvf xuezi-tools-backup-YYYY-MM-DD.tar.gz -C /usr/share/nginx/html/
```

## 当前备份文件

- **文件名**: `xuezi-tools-backup-2026-02-27.tar.gz`
- **大小**: 89 MB
- **位置**: 云服务器 `/usr/share/nginx/html/downloads/`
- **状态**: 🔒 已锁定
- **密码**: `zr041412150`

## 历史备份

| 日期 | 文件名 | 大小 | 状态 |
|------|--------|------|------|
| 2026-02-27 | xuezi-tools-backup-2026-02-27.tar.gz | 89 MB | ✅ 当前 |
| 2026-02-26 | 全部技能包备份_20250226.tar.gz | 101 KB | ✅ 保留 |
