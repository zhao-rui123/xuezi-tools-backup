# Memory Suite v3.0 - 完整测试计划

## 测试目标
确保 Memory Suite v3.0 所有功能正常运行，数据不丢失，系统稳定可靠。

---

## 测试环境

### 硬件/软件要求
- macOS/Linux 系统
- Python 3.11+
- 标准库（无外部依赖）

### 测试目录
```
~/.openclaw/workspace/skills/memory-suite-v3/
```

### 测试数据
- 使用现有 memory/ 目录的真实数据
- 创建测试用的临时记忆文件

---

## 测试阶段

### Phase 1: 单元测试（每个模块单独测试）

#### 1.1 Core 模块测试

**real_time.py 测试**
```bash
# 测试1: 立即保存
python3 -c "from core.real_time import RealTimeSaver; r = RealTimeSaver(); r.save_snapshot()"
# 预期: 在 memory/snapshots/ 生成 current_session.json

# 测试2: 加载快照
python3 -c "from core.real_time import RealTimeSaver; r = RealTimeSaver(); print(r.load_snapshot())"
# 预期: 成功加载并打印快照内容

# 测试3: 快照完整性检查
ls -la ~/.openclaw/workspace/memory/snapshots/current_session.json
# 预期: 文件存在，大小合理
```

**archiver.py 测试**
```bash
# 测试1: 归档检查（模拟7天前的文件）
touch -d "7 days ago" ~/.openclaw/workspace/memory/test_archive_$(date -d "7 days ago" +%Y-%m-%d).md
python3 -c "from core.archiver import Archiver; a = Archiver(); a.run()"
# 预期: 7天前的文件被移动到 archive/

# 测试2: 归档目录结构检查
ls -la ~/.openclaw/workspace/memory/archive/$(date +%Y/%m)/
# 预期: 存在按年月组织的归档文件

# 测试3: 永久记录检查
ls -la ~/.openclaw/workspace/memory/permanent/
# 预期: 存在永久记录文件
```

**indexer.py 测试**
```bash
# 测试1: 索引构建
python3 -c "from core.indexer import Indexer; i = Indexer(); i.build_index()"
# 预期: 在 memory/index/ 生成索引文件

# 测试2: 搜索功能
python3 -c "from core.indexer import Indexer; i = Indexer(); results = i.search('测试'); print(results)"
# 预期: 返回相关记忆文件列表

# 测试3: 索引更新
ls -la ~/.openclaw/workspace/memory/index/
# 预期: 存在 keyword_index.json 等索引文件
```

**analyzer.py 测试**
```bash
# 测试1: 月度分析
python3 -c "from core.analyzer import Analyzer; a = Analyzer(); print(a.analyze_month('2026-03'))"
# 预期: 返回月度分析报告

# 测试2: 主题提取
python3 -c "from core.analyzer import Analyzer; a = Analyzer(); print(a.extract_topics())"
# 预期: 返回提取的主题列表

# 测试3: 关键词统计
python3 -c "from core.analyzer import Analyzer; a = Analyzer(); print(a.keyword_stats())"
# 预期: 返回关键词统计结果
```

#### 1.2 Apps 模块测试

**qa.py 测试**
```bash
# 测试1: 问答功能
python3 -c "from apps.qa import MemoryQA; qa = MemoryQA(); print(qa.answer('最近做了什么？'))"
# 预期: 返回答案和相关记忆引用

# 测试2: 空问题处理
python3 -c "from apps.qa import MemoryQA; qa = MemoryQA(); print(qa.answer(''))"
# 预期: 优雅处理，不报错
```

**advisor.py 测试**
```bash
# 测试1: 决策建议
python3 -c "from apps.advisor import DecisionAdvisor; d = DecisionAdvisor(); print(d.get_advice('备份策略'))"
# 预期: 返回相关决策建议

# 测试2: 决策历史
python3 -c "from apps.advisor import DecisionAdvisor; d = DecisionAdvisor(); print(d.get_decision_history())"
# 预期: 返回历史决策列表
```

**recommender.py 测试**
```bash
# 测试1: 记忆推荐
python3 -c "from apps.recommender import Recommender; r = Recommender(); print(r.recommend_memories())"
# 预期: 返回推荐记忆列表

# 测试2: 任务推荐
python3 -c "from apps.recommender import Recommender; r = Recommender(); print(r.recommend_tasks())"
# 预期: 返回推荐任务列表
```

**profiler.py 测试**
```bash
# 测试1: 用户画像
python3 -c "from apps.profiler import UserProfiler; p = UserProfiler(); print(p.generate_profile())"
# 预期: 返回用户画像报告

# 测试2: 兴趣分析
python3 -c "from apps.profiler import UserProfiler; p = UserProfiler(); print(p.analyze_interests())"
# 预期: 返回兴趣分析结果
```

#### 1.3 Integration 模块测试

**kb_sync.py 测试**
```bash
# 测试1: 知识库同步
python3 -c "from integration.kb_sync import KBSync; k = KBSync(); k.sync_to_kb()"
# 预期: 同步记忆到 knowledge-base/

# 测试2: 检查同步结果
ls -la ~/.openclaw/workspace/knowledge-base/pending/
# 预期: 存在同步的知识项
```

**notifier.py 测试**
```bash
# 测试1: 通知功能（模拟）
python3 -c "from integration.notifier import Notifier; n = Notifier(); n.notify('测试通知', '这是一条测试消息')"
# 预期: 成功发送通知（或记录到日志）
```

---

### Phase 2: 集成测试（模块间协作测试）

#### 2.1 Scheduler 集成测试
```bash
# 测试1: 调度器列出任务
python3 scheduler.py list
# 预期: 显示所有可用任务

# 测试2: 运行实时保存任务
python3 scheduler.py run real-time
# 预期: 成功执行，生成快照

# 测试3: 运行归档任务
python3 scheduler.py run archive
# 预期: 成功执行，归档旧文件

# 测试4: 运行索引任务
python3 scheduler.py run index
# 预期: 成功执行，更新索引

# 测试5: 运行分析任务
python3 scheduler.py run analyze-daily
# 预期: 成功执行，生成分析报告
```

#### 2.2 CLI 集成测试
```bash
# 测试1: CLI 帮助
python3 cli.py --help
# 预期: 显示所有子命令

# 测试2: 保存命令
python3 cli.py save
# 预期: 成功保存会话

# 测试3: 恢复命令
python3 cli.py restore
# 预期: 成功恢复会话

# 测试4: 状态命令
python3 cli.py status
# 预期: 显示系统状态

# 测试5: 搜索命令
python3 cli.py search "测试"
# 预期: 返回搜索结果

# 测试6: QA命令
python3 cli.py qa "最近做了什么？"
# 预期: 返回答案

# 测试7: 归档列表
python3 cli.py archive list
# 预期: 列出所有归档

# 测试8: 报告生成
python3 cli.py report daily
# 预期: 生成日报

# 测试9: 配置查看
python3 cli.py config show
# 预期: 显示当前配置

# 测试10: Doctor检查
python3 cli.py doctor
# 预期: 运行诊断，显示健康状况
```

#### 2.3 配置系统测试
```bash
# 测试1: 配置读取
cat config/config.json | python3 -m json.tool
# 预期: 有效的JSON格式

# 测试2: 配置热更新
# 修改 config.json 中的某个值
python3 cli.py config show
# 预期: 显示更新后的配置
```

---

### Phase 3: 系统测试（端到端测试）

#### 3.1 完整工作流程测试
```bash
# 步骤1: 清理测试环境
mkdir -p ~/.openclaw/workspace/memory/test_workflow
cd ~/.openclaw/workspace/memory/test_workflow

# 步骤2: 创建测试记忆文件
echo "# 测试记忆 $(date)
今天完成了Memory Suite v3.0的开发。
这是一个重要的项目里程碑。
" > 2026-03-11-test.md

# 步骤3: 运行完整流程
python3 ~/.openclaw/workspace/skills/memory-suite-v3/scheduler.py run real-time
python3 ~/.openclaw/workspace/skills/memory-suite-v3/scheduler.py run index
python3 ~/.openclaw/workspace/skills/memory-suite-v3/scheduler.py run analyze-daily

# 步骤4: 验证结果
ls -la ~/.openclaw/workspace/memory/snapshots/
ls -la ~/.openclaw/workspace/memory/index/
# 预期: 生成快照和索引
```

#### 3.2 数据完整性测试
```bash
# 测试1: 原始数据备份
cp -r ~/.openclaw/workspace/memory ~/.openclaw/workspace/memory_backup_test

# 测试2: 运行所有任务
for task in real-time archive index analyze-daily; do
    python3 ~/.openclaw/workspace/skills/memory-suite-v3/scheduler.py run $task
done

# 测试3: 验证数据完整性
diff -r ~/.openclaw/workspace/memory_backup_test ~/.openclaw/workspace/memory --exclude=snapshots --exclude=index --exclude=archive
# 预期: 原始记忆文件未被修改

# 测试4: 清理
rm -rf ~/.openclaw/workspace/memory_backup_test
```

#### 3.3 性能测试
```bash
# 测试1: 索引构建性能
time python3 -c "from core.indexer import Indexer; i = Indexer(); i.build_index()"
# 预期: 100个记忆文件 < 5秒

# 测试2: 搜索性能
time python3 -c "from core.indexer import Indexer; i = Indexer(); i.search('测试')"
# 预期: 搜索 < 1秒

# 测试3: 归档性能
time python3 -c "from core.archiver import Archiver; a = Archiver(); a.run()"
# 预期: 归档 < 3秒
```

---

### Phase 4: 验收测试（用户场景测试）

#### 4.1 日常场景测试
```bash
# 场景1: 用户查看今天的工作状态
python3 cli.py status

# 场景2: 用户搜索之前的决策
python3 cli.py search "备份策略"

# 场景3: 用户询问之前做了什么
python3 cli.py qa "上周完成了什么项目？"

# 场景4: 用户查看归档
python3 cli.py archive list

# 场景5: 用户生成周报
python3 cli.py report weekly
```

#### 4.2 故障恢复测试
```bash
# 场景1: 模拟配置错误
echo "invalid json" > ~/.openclaw/workspace/skills/memory-suite-v3/config/config.json
python3 cli.py doctor
# 预期: 检测到配置错误，提供修复建议

# 恢复配置
cp ~/.openclaw/workspace/skills/memory-suite-v3/config/config.json.bak ~/.openclaw/workspace/skills/memory-suite-v3/config/config.json

# 场景2: 模拟数据损坏
echo "corrupted" > ~/.openclaw/workspace/memory/snapshots/current_session.json
python3 cli.py restore
# 预期: 优雅处理错误，不崩溃
```

#### 4.3 定时任务模拟测试
```bash
# 模拟一天的定时任务运行
for i in {1..144}; do  # 144个10分钟 = 24小时
    python3 scheduler.py run real-time
    sleep 0.1
done
# 预期: 系统稳定运行，无内存泄漏
```

---

## 测试检查清单

### 功能检查
- [ ] real_time.py - 保存/加载正常
- [ ] archiver.py - 归档/永久记录正常
- [ ] indexer.py - 索引/搜索正常
- [ ] analyzer.py - 分析/报告正常
- [ ] qa.py - 问答正常
- [ ] advisor.py - 决策支持正常
- [ ] recommender.py - 推荐正常
- [ ] profiler.py - 画像正常
- [ ] kb_sync.py - 同步正常
- [ ] notifier.py - 通知正常
- [ ] cli.py - 所有命令可用
- [ ] scheduler.py - 所有任务可调度
- [ ] doctor.py - 诊断正常

### 集成检查
- [ ] 模块间调用正常
- [ ] 配置系统正常
- [ ] 日志系统正常
- [ ] 错误处理正常

### 系统检查
- [ ] 数据不丢失
- [ ] 性能达标
- [ ] 内存无泄漏
- [ ] 定时任务稳定

### 验收检查
- [ ] 用户场景通过
- [ ] 故障恢复通过
- [ ] 文档完整

---

## 测试报告模板

```markdown
# Memory Suite v3.0 测试报告

## 测试日期
2026-03-XX

## 测试人员
AI Agent Team

## 测试结果摘要
- 通过: XX / XX
- 失败: XX / XX
- 跳过: XX / XX

## 详细结果

### Phase 1: 单元测试
| 模块 | 状态 | 备注 |
|------|------|------|
| real_time.py | ✅/❌ | |
| archiver.py | ✅/❌ | |
| ... | | |

### Phase 2: 集成测试
| 功能 | 状态 | 备注 |
|------|------|------|
| scheduler | ✅/❌ | |
| cli | ✅/❌ | |
| ... | | |

### Phase 3: 系统测试
| 场景 | 状态 | 备注 |
|------|------|------|
| 完整流程 | ✅/❌ | |
| 数据完整性 | ✅/❌ | |
| 性能 | ✅/❌ | |

### Phase 4: 验收测试
| 场景 | 状态 | 备注 |
|------|------|------|
| 日常场景 | ✅/❌ | |
| 故障恢复 | ✅/❌ | |
| 定时任务 | ✅/❌ | |

## 问题列表
1. XXX
2. XXX

## 建议
1. XXX
2. XXX

## 结论
✅ 测试通过，可以上线
❌ 测试未通过，需要修复
```

---

## 自动化测试脚本

```bash
#!/bin/bash
# run_all_tests.sh

echo "=== Memory Suite v3.0 自动化测试 ==="

# Phase 1: 单元测试
echo "Phase 1: 单元测试..."
python3 tests/test_core.py
python3 tests/test_apps.py
python3 tests/test_integration.py

# Phase 2: 集成测试
echo "Phase 2: 集成测试..."
python3 tests/test_cli.py
python3 tests/test_scheduler.py

# Phase 3: 系统测试
echo "Phase 3: 系统测试..."
python3 tests/test_system.py

# Phase 4: 验收测试
echo "Phase 4: 验收测试..."
python3 tests/test_acceptance.py

echo "=== 测试完成 ==="
```

---

*测试计划版本: 1.0*
*最后更新: 2026-03-11*
