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
| **Notification** | **Kilo (广播专员)** | **系统通知、定时任务报告** | **Python脚本** |

### Kilo (广播专员) - 通知专家

**角色**: Notification Agent (通知消息专家)  
**别名**: 广播专员  
**职责**: 统一发送所有定时任务通知、系统状态报告、每日汇总  
**状态**: ✅ 已配置，运行正常

**关键配置**:
- **群聊ID**: `oc_b14195eb990ab57ea573e696758ae3d5`
- **用户ID**: `ou_5a7b7ec0339ffe0c1d5bb6c5bc162579` (雪子)
- **主脚本**: `~/.openclaw/workspace/agents/kilo/broadcaster.py`
- **技能包**: `~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py`

**通知类型**:
1. **每日备份通知** (22:00) - 备份完成状态、文件统计
2. **健康检查报告** (09:00) - 系统状态、磁盘空间、服务检查
3. **定时任务汇总** (01:00) - 夜间任务执行状态
4. **系统告警** - 异常事件实时推送
5. **任务提醒** - 到期任务通知

**使用方式**:
```bash
# 发送通知到群聊
python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
  --task send_notification \
  --message "通知内容" \
  --target group

# 检查定时任务并报告
python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
  --task daily_report
```

**验证状态**: ✅ 2026-03-10 测试通过，消息可正常发送到群聊

## 标准开发流程

```
需求确认 → 需求评审 → 任务分配 → 并行开发 → 开发完成预览 → 审查验证 → 用户验收 → 备份回滚 → 统一部署 → 交付文档 → 迭代优化
```

### 1. 需求确认（Orchestrator）
- 整理功能清单
- 评估任务等级
- 确定技术方案
- **输出**: 需求文档 (requirements.md)

### 2. 需求评审（用户确认）
- 用户审阅需求文档
- 确认功能范围
- 调整优先级
- **通过标准**: 用户回复"确认"或"开始开发"

### 3. 任务分配（Orchestrator）
- 拆解任务模块
- 明确输出路径
- 设定验收标准
- **输出**: 任务分配表

### 4. 并行开发（Builders）
- 子Agent在本地创建文件
- 按模块分工协作
- 实时同步进度

### 5. 开发完成预览（Orchestrator → 用户）
- 所有模块开发完成后，启动本地预览服务器
- 提供临时访问链接
- 用户整体体验后提出修改意见
- **输出**: 修改清单

### 6. 审查验证（Reviewers）
- 功能测试
- 代码审查
- 文件完整性检查
- **输出**: 测试报告

### 7. 用户验收（用户确认）
- 本地预览完整功能
- 用户测试核心流程
- **通过标准**: 用户确认"可以部署"

### 8. 备份回滚（Ops - Echo）
- 部署前备份服务器旧版本
- 保存到 `backups/项目名_日期/`
- **输出**: 备份确认

### 9. 统一部署（Orchestrator）
```bash
# 1. 备份旧版本
sshpass -p 'Zr123456' ssh root@106.54.25.161 "cp -r /usr/share/nginx/html/project /usr/share/nginx/html/backups/project_$(date +%Y%m%d_%H%M%S)"

# 2. 上传新版本
sshpass -p 'Zr123456' scp -r localdir/ root@106.54.25.161:/usr/share/nginx/html/

# 3. 验证部署
 curl -s http://106.54.25.161/project/ | head -20
```

### 10. 交付文档（Orchestrator）
- **README.md**: 功能说明、使用方法
- **部署文档**: 技术栈、目录结构
- **更新日志**: 版本变更记录
- **输出**: 完整文档包

### 11. 迭代优化
- 根据反馈继续完善
- 循环上述流程
- 小改动走"快速修复通道"（无需完整流程）

## 快速修复通道
对于小改动（< 30分钟）：
1. 用户描述问题
2. Orchestrator 直接修复
3. 本地测试
4. 用户确认
5. 部署

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
