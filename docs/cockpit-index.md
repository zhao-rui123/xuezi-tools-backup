# 主控制台（驾驶台）导航索引

*最后更新：2026-05-01*

## 当前架构：V5 两级导航
```
主控制台 V5 Hub（一级）
├── ⚡ 执行链路
│   └── 执行中心 | 语义任务面板 | ACP | screen详情 | 重跑测试任务 | 任务历史 | 后台任务中心
├── 📋 任务与记忆
│   └── 任务面板 | 记忆面板 | 今日重点 | 阻塞 | 高优先级 | Inbox | 摘要
├── 🩺 系统与定时
│   └── 系统面板 | 定时任务中心 | 健康检查 | 备份状态
├── 🤖 模型与控制
│   └── 模型面板 | 切换CC模型 | 会话状态 | 轻控制入口 | 清理测试任务
└── 🔧 快捷
    └── 快捷动作面板 | 主控制台 | 帮助
```

**设计原则**：一级入口只放5个主题，每个主题下有二级标题说明（文字），用户点之前就知道里面有什么。

**无重复**：会话状态只在🤖，重跑测试任务只在⚡。

---

## 驾驶台体系架构

```
主控制台 V3（Hub）
├── 系统面板
├── 任务面板
├── 模型面板
├── 记忆面板
├── 今日重点建议
├── 快捷动作面板
├── 定时任务中心
├── 后台任务中心
├── 执行中心
│   ├── 语义任务面板
│   ├── ACP 语义面板
│   └── screen 详情
├── 任务历史中心
├── 轻控制入口
│   └── 控制动作分级
└── 重跑测试任务
    ├── 候选面板
    ├── 确认卡
    ├── 执行规范
    └── 命令处理器
```

---

## 所有面板/脚本清单（按功能分类）

### 入口
| 名称 | 脚本 | 说明 |
|------|------|------|
| 主控制台 | `cockpit_card.py` | 驾驶台首页 V3，所有专题入口 |
| 快捷动作 | `quick_actions_panel_card.py` | 快捷动作汇总 |

### 状态专题
| 名称 | 脚本 | 说明 |
|------|------|------|
| 系统面板 | `system_panel_card.py` | 健康检查/备份/Gateway/Tailscale/云服务器 |
| 任务面板 | `task_panel_card.py` | 阻塞/高优/收件箱/自动导入任务 |
| 模型面板 | `model_panel_card.py` | OpenClaw 会话模型 + Claude Code 模型及切换 |
| 记忆面板 | `memory_panel_card.py` | 候选人统计/风险/规则/TODO/进度 |
| 今日重点建议 | `focus_panel_card.py` | 规则驱动优先级建议 |
| 定时任务中心 | `scheduled_tasks_panel_card.py` | 每日备份/云同步/股票推送/会话快照/周清理 |
| 后台任务中心 | `runtime_tasks_panel_card.py` | 当前模型/token/上下文/活跃任务/子会话数 |

### 执行链路专题
| 名称 | 脚本 | 说明 |
|------|------|------|
| 执行中心 | `execution_center_card.py` | 总执行链路视图，Hub |
| 语义任务面板 | `semantic_execution_panel_card.py` | 任务名→业务名，执行状态 |
| ACP 语义面板 | `acp_semantic_panel_card.py` | ACP 线程业务含义 |
| ACP 详情 | `acp_detail_panel_card.py` | ACP sessionId/updatedAt/sessionFile |
| screen 详情 | `screen_detail_panel_card.py` | screen 会话状态 |

### 控制专题
| 名称 | 脚本 | 说明 |
|------|------|------|
| 轻控制入口 | `light_control_panel_card.py` | 低风险控制动作入口 |
| 控制动作分级 | `control_actions_policy_card.py` | P0/P1/P2 分级原则 |
| 重跑测试任务 | `rerun_test_tasks_panel_card.py` | 候选清单 |
| 重跑确认卡 | `rerun_test_confirm_card.py` | 二次确认 |
| 重跑执行规范 | `rerun_execution_policy_card.py` | 执行边界/规则 |
| 重跑结果卡 | `rerun_result_card.py` | 结果回显卡片 |

### 任务历史
| 名称 | 脚本 | 说明 |
|------|------|------|
| 任务历史中心 | `task_history_panel_card.py` | 项目/测试/定时任务统一历史 |

---

## 脚本文件路径
`~/.openclaw/workspace/scripts/`

---

## 命令处理
| 命令 | 处理器 | 说明 |
|------|--------|------|
| `rerun execute <task>` | `handle_rerun_cmd.py` | 重跑测试任务（仅 3 个白名单任务） |

---

## 重跑测试任务完整链路
```
候选面板
  → [确认重跑 xxx] → 确认卡
    → [确认并重跑] → handle_rerun_cmd.py
      → rerun-test-task.sh
        → rerun-test-task-result.sh
          → rerun_result_card.py（结果卡）
```

---

## Quick Action 路由注册清单
| action | 触发命令 | 面板 |
|--------|----------|------|
| `feishu.quick_actions.cockpit_home` | `cockpit card` | 主控制台 |
| `feishu.quick_actions.system_panel` | `system panel card` | 系统面板 |
| `feishu.quick_actions.task_panel` | `task panel card` | 任务面板 |
| `feishu.quick_actions.model_panel` | `model panel card` | 模型面板 |
| `feishu.quick_actions.memory_panel` | `memory panel card` | 记忆面板 |
| `feishu.quick_actions.focus_panel` | `focus panel card` | 今日重点 |
| `feishu.quick_actions.quick_actions_panel` | `quick actions panel card` | 快捷动作 |
| `feishu.quick_actions.scheduled_tasks_panel` | `scheduled tasks panel card` | 定时任务中心 |
| `feishu.quick_actions.runtime_tasks_panel` | `runtime tasks panel card` | 后台任务中心 |
| `feishu.quick_actions.execution_center` | `execution center card` | 执行中心 |
| `feishu.quick_actions.semantic_execution_panel` | `semantic execution panel card` | 语义任务面板 |
| `feishu.quick_actions.acp_semantic_panel` | `acp semantic panel card` | ACP 语义面板 |
| `feishu.quick_actions.acp_detail_panel` | `acp detail panel card` | ACP 详情 |
| `feishu.quick_actions.screen_detail_panel` | `screen detail panel card` | screen 详情 |
| `feishu.quick_actions.task_history_panel` | `task history panel card` | 任务历史中心 |
| `feishu.quick_actions.light_control_panel` | `light control panel card` | 轻控制入口 |
| `feishu.quick_actions.rerun_test_tasks_panel` | `rerun test tasks panel card` | 重跑测试任务 |
| `feishu.quick_actions.rerun_test_execute` | `rerun execute <task>` | 执行重跑命令 |

---

## 控制动作分级
| 级别 | 风险 | 内容 |
|------|------|------|
| P0 | 低 | 查看详情/跳转/返回/查看状态 |
| P1 | 中 | 清理测试任务/重跑测试任务/停止测试任务 |
| P2 | 高 | 停止正式任务/重跑正式任务/改定时任务 |

---

## 下一步工作
1. **A** → 扩控制动作：清理测试任务同 Pattern
2. **B** → 主控制台首页增强
3. **演示** → 完整演示重跑链路
