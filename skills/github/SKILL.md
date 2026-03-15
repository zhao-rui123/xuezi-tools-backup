---
name: github
description: "Git版本控制 - 本地git操作+GitHub CLI操作。整合了git-workflow的功能。"
---

# Git 版本控制技能

本技能包整合了本地 git 操作和 GitHub CLI 操作。

## 仓库信息

**本地仓库**: `~/.openclaw/workspace/`  
**远程仓库**: https://github.com/zhao-rui123/xuezi-tools-backup  
**主要分支**: `main`

---

## 本地 Git 操作

### 提交规范

```
<type>: <subject>

<body> (optional)
```

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加储能项目测算报告导出` |
| `fix` | 修复bug | `fix: 修复电价数据更新失败问题` |
| `docs` | 文档更新 | `docs: 更新API使用说明` |
| `refactor` | 重构 | `refactor: 优化股票分析算法` |
| `chore` | 杂项 | `chore: 更新依赖版本` |

### 日常操作

```bash
# 查看变更
git status

# 添加文件
git add -A
# 或选择性添加
git add specific-file.md

# 提交
git commit -m "type: 描述信息"

# 推送到远程
git push origin main
```

### 分支操作

```bash
# 创建并切换分支
git checkout -b feature/new-tool

# 开发完成后合并回main
git checkout main
git merge feature/new-tool
git branch -d feature/new-tool
```

### 常用命令

| 命令 | 用途 |
|------|------|
| `git status` | 查看变更状态 |
| `git log --oneline -10` | 查看最近10条提交 |
| `git diff` | 查看未提交的变更 |
| `git restore file` | 撤销文件变更 |
| `git reset --soft HEAD~1` | 撤销最近提交（保留变更） |

---

## GitHub CLI 操作

使用 `gh` CLI 与 GitHub 平台交互。

### Pull Requests

检查 PR 的 CI 状态：
```bash
gh pr checks 55 --repo owner/repo
```

列出最近的 workflow 运行：
```bash
gh run list --repo owner/repo --limit 10
```

查看运行详情：
```bash
gh run view <run-id> --repo owner/repo
```

查看失败步骤日志：
```bash
gh run view <run-id> --repo owner/repo --log-failed
```

### API 高级查询

```bash
# 获取 PR 信息
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# 列出 issue
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

---

## 与云服务器同步

```
本地 workspace → GitHub → 云服务器(可选)
```

服务器拉取更新：
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "cd /path/to/repo && git pull"
```

---

## 最佳实践

1. **频繁提交**: 小步快跑，每次提交一个逻辑单元
2. **写清楚提交信息**: 方便日后查找
3. **推送前检查**: `git status` 确认无误再 push
4. **重要变更备份**: 大改前先提交当前状态
