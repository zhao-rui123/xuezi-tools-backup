---
name: skill-version-control
description: Skill package version management and changelog tracking. Use when updating skills, creating new versions, or rolling back to previous versions.
---

# 技能包版本管理

## 版本规范

### 版本号格式
```
主版本.次版本.修订号
例如：1.2.3
```

| 位置 | 含义 | 何时增加 |
|------|------|---------|
| 主版本 | 重大变更，不兼容 | 架构重构、API变更 |
| 次版本 | 功能新增，兼容 | 新功能、新场景 |
| 修订号 | Bug修复，优化 | 修复问题、性能优化 |

### 版本记录位置
每个技能包的 `SKILL.md` 头部：
```yaml
---
name: skill-name
version: 1.2.3
last_updated: 2026-03-04
changelog:
  - 1.2.3: 修复xxx问题
  - 1.2.2: 添加xxx功能
  - 1.2.0: 重构xxx模块
---
```

## 版本管理流程

### 1. 修改前检查
```bash
# 查看当前版本
grep "^version:" skills/skill-name/SKILL.md

# 查看历史变更
grep -A10 "changelog:" skills/skill-name/SKILL.md
```

### 2. 确定版本类型
- **Bug修复** → 修订号+1 (1.2.3 → 1.2.4)
- **新功能** → 次版本+1 (1.2.3 → 1.3.0)
- **重大重构** → 主版本+1 (1.2.3 → 2.0.0)

### 3. 更新版本信息
```bash
# 更新版本号和变更日志
# 在 SKILL.md 的 frontmatter 中修改
```

### 4. 提交到Git
```bash
git add skills/skill-name/
git commit -m "feat(skill-name): 版本1.2.4，修复xxx问题"
```

## 回滚操作

### 查看历史版本
```bash
# 查看技能包修改历史
git log --oneline skills/skill-name/

# 查看特定版本的文件
git show COMMIT_ID:skills/skill-name/SKILL.md
```

### 回滚到指定版本
```bash
# 方法1：直接检出旧版本
git checkout COMMIT_ID -- skills/skill-name/

# 方法2：撤销最近修改
git revert HEAD -- skills/skill-name/
```

## 关键技能包版本现状

| 技能包 | 当前版本 | 最后更新 |
|--------|---------|---------|
| knowledge-base | 1.0.0 | 2026-03-04 |
| git-workflow | 1.0.0 | 2026-03-04 |
| data-processor | 1.0.0 | 2026-03-04 |
| system-maintenance | 1.0.0 | 2026-03-04 |
| file-management | 1.0.0 | 2026-03-04 |

---
*创建于: 2026-03-04*
