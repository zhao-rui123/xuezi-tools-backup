# HEARTBEAT.md - 每日自动任务

## 每日记忆整理流程

### 执行时间
每天首次heartbeat时执行

### 任务清单

1. **读取当日记忆文件**
   - 检查 memory/YYYY-MM-DD.md 是否存在
   - 提取关键信息

2. **更新长期记忆 MEMORY.md**
   - 新增重要决策 → [DECISION] 区块
   - 新增待办事项 → [TODO] 区块
   - 新增项目信息 → [PROJECT] 区块
   - 新增关键数据 → [DATA] 区块

3. **清理临时信息**
   - 标记已完成的TODO
   - 归档过期临时数据

4. **生成每日摘要**
   - 今日完成事项
   - 明日待办提醒
   - 重要决策回顾

### 输出
- 更新后的 MEMORY.md
- 归档旧记忆到 memory/archive/
- 生成 summary/daily/YYYY-MM-DD-summary.md

---
*此文件由系统自动维护*
