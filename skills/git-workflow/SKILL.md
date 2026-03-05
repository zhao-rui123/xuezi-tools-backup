---
name: git-workflow
description: Git version control workflow for the workspace. Use when committing changes, creating branches, managing versions, or collaborating on code. Covers commit conventions, branching strategy, and release process.
---

# Git 工作流技能

## 仓库信息

**本地仓库**: `~/.openclaw/workspace/`  
**远程仓库**: https://github.com/zhao-rui123/xuezi-tools-backup  
**主要分支**: `main`

## 提交规范

### 提交信息格式
```
<type>: <subject>

<body> (optional)
```

### 类型说明
| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加储能项目测算报告导出` |
| `fix` | 修复bug | `fix: 修复电价数据更新失败问题` |
| `docs` | 文档更新 | `docs: 更新API使用说明` |
| `refactor` | 重构 | `refactor: 优化股票分析算法` |
| `chore` | 杂项 | `chore: 更新依赖版本` |

### 提交示例
```bash
# 添加新功能
git add -A
git commit -m "feat: 添加飞书文件发送技能包"

# 修复问题
git add backup_memory.sh
git commit -m "fix: 修复备份脚本rsync检测逻辑"

# 更新文档
git add knowledge-base/
git commit -m "docs: 重构知识库管理体系"
```

## 标准工作流

### 日常提交
```bash
# 1. 查看变更
git status

# 2. 添加文件
git add -A
# 或选择性添加
git add specific-file.md

# 3. 提交
git commit -m "type: 描述信息"

# 4. 推送到远程
git push origin main
```

### 重要变更前备份
```bash
# 提交当前工作
git add -A
git commit -m "chore: 变更前备份"

# 然后执行可能破坏性的操作
```

## 分支策略（简化版）

当前使用 **主干开发** 模式：
- 所有开发在 `main` 分支进行
- 重要变更先本地测试再推送
- 大型功能考虑临时分支

### 创建临时分支（大型功能）
```bash
# 创建并切换分支
git checkout -b feature/new-tool

# 开发完成后合并回main
git checkout main
git merge feature/new-tool
git branch -d feature/new-tool
```

## 与云服务器同步

GitHub 仓库作为中转：
```
本地 workspace → GitHub → 云服务器(可选)
```

云服务器拉取更新：
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "cd /path/to/repo && git pull"
```

## 常用命令速查

| 命令 | 用途 |
|------|------|
| `git status` | 查看变更状态 |
| `git log --oneline -10` | 查看最近10条提交 |
| `git diff` | 查看未提交的变更 |
| `git restore file` | 撤销文件变更 |
| `git reset --soft HEAD~1` | 撤销最近提交（保留变更） |

## 最佳实践

1. **频繁提交**: 小步快跑，每次提交一个逻辑单元
2. **写清楚提交信息**: 方便日后查找
3. **推送前检查**: `git status` 确认无误再 push
4. **重要变更备份**: 大改前先提交当前状态

---
*创建于: 2026-03-04*
