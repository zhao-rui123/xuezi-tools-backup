# 项目知识库 - 多Agent开发框架

## 框架概述

**核心技能包**:
- `multi-agent-cn` — 5个固定子Agent并行开发
- `agent-team-orchestration` — 任务生命周期和质量控制

## 团队角色

| 角色 | 代号 | 职责 | 模型建议 |
|------|------|------|---------|
| Orchestrator | - | 路由任务、跟踪状态、统一部署 | 当前主模型 |
| Builder | Alpha | HTML/CSS界面开发 | kimi-for-coding |
| Builder | Bravo | JavaScript/算法开发 | kimi-for-coding |
| Builder | Charlie | 功能完善、修复问题 | kimi-for-coding |
| Reviewer | Delta | 代码审查、测试验证 | kimi-for-coding |
| Ops | Echo | 部署运维、质量检查 | kimi-for-coding |

## 标准开发流程

```
需求确认 → 任务分配 → 并行开发 → 审查验证 → 统一部署 → 迭代优化
```

### 1. 需求确认（Orchestrator）
- 整理功能清单
- 评估任务等级
- 确定技术方案

### 2. 任务分配（Orchestrator）
- 拆解任务模块
- 明确输出路径
- 设定验收标准

### 3. 并行开发（Builders）
- 子Agent在本地创建文件
- 按模块分工协作
- 实时同步进度

### 4. 审查验证（Reviewers）
- 功能测试
- 代码审查
- 文件完整性检查

### 5. 统一部署（Orchestrator）
```bash
# 上传到云服务器
sshpass -p 'Zr123456' scp -r localdir/ root@106.54.25.161:/usr/share/nginx/html/
```

### 6. 迭代优化
- 根据反馈继续完善
- 循环上述流程

## 成功案例

### 1. 储能电站不规则土地智能排布系统
- **网址**: http://106.54.25.161/storage-layout-ai/
- **功能**: 不规则土地上的储能设备智能布局
- **技术**: HTML5 Canvas + 遗传算法

### 2. 国网电费清单处理系统
- **网址**: http://106.54.25.161/energy-bill-processor/
- **功能**: 自动处理国网电费清单和负荷曲线
- **技术**: 纯前端 + 本地计算

## 开发规范

### 文件结构
```
project-name/
├── index.html      # 主页面
├── css/
├── js/
├── assets/         # 图片、字体等
└── README.md       # 项目说明
```

### 代码规范
- 使用语义化 HTML
- CSS 使用 Flexbox/Grid 布局
- JavaScript 模块化组织
- 添加必要注释

### 部署检查清单
- [ ] 所有文件已上传
- [ ] 路径引用正确
- [ ] 功能测试通过
- [ ] 移动端适配（如需要）

## 最佳实践

1. **任务粒度**: 每个子任务控制在30分钟内可完成
2. **沟通频率**: 每完成一个模块同步一次
3. **版本控制**: 重要节点提交 Git
4. **备份策略**: 开发中定期备份到本地

---
*创建于: 2026-03-04*  
*更新: 随流程优化更新*
