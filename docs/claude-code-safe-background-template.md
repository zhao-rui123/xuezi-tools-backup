# 本地 Claude Code 安全后台调用模板

> 目标：能后台跑、结束干净、不留 `claude / bash / login` 残进程。
> 结论基于 2026-04-28 本机实测：**只用 `screen -X quit` 关闭 screen，会稳定留下 Claude Code 残进程。**

---

## 一、结论先说

### ❌ 不推荐的方式
```bash
screen -dmS cc-task bash -lc "cd /path && claude --permission-mode bypassPermissions --print '任务' > /tmp/cc.log 2>&1"
# ...过一会儿
screen -S cc-task -X quit
```

**问题：**
- `screen` 关了，但里面的：
  - `claude`
  - `bash -lc`
  - `login -pflq`
- 可能不会退出干净
- 多跑几次会累积出几百 MB 残留内存

---

## 二、推荐原则

### 原则 1：短任务优先不用 screen
如果任务是几分钟内能结束的，优先直接前台跑，或者用 OpenClaw `exec(background:true)` 管理，不要手工 `screen`。

### 原则 2：如果必须后台，优先“让任务自然结束”
不要把 `screen -X quit` 当成任务结束方式。

### 原则 3：需要中止时，杀 Claude 进程，不只杀 screen
真正要结束的是 Claude 任务树，而不是只关 screen 外壳。

---

## 三、安全后台模板（推荐版）

## 模板 A：后台跑 + 等自然结束
适合：本地 Claude Code 一次性方案、文档、分析任务

```bash
TASK_NAME=cc-task-$(date +%Y%m%d-%H%M%S)
WORKDIR=/你的项目目录
LOG=~/.openclaw/workspace/logs/${TASK_NAME}.log
PIDFILE=~/.openclaw/workspace/logs/${TASK_NAME}.pid

mkdir -p ~/.openclaw/workspace/logs

screen -dmS "$TASK_NAME" bash -lc '
  cd "'"$WORKDIR"'" || exit 1
  claude --permission-mode bypassPermissions --print "你的任务" > "'"$LOG"'" 2>&1
  echo $? > "'"$PIDFILE"'".exit
'
```

### 查看状态
```bash
screen -ls | grep cc-task
ps aux | grep "claude --permission-mode bypassPermissions --print" | grep -v grep
```

### 看日志
```bash
tail -f ~/.openclaw/workspace/logs/任务名.log
```

### 正常完成后
- 不要手动 `screen -X quit`
- 让 Claude 自己跑完退出
- 跑完后再检查一次是否还有残留 Claude 进程

```bash
ps aux | grep "claude --permission-mode bypassPermissions --print" | grep -v grep
```

如果没有输出，说明干净退出。

---

## 四、安全中止模板（必须记住）

如果任务要提前停掉：

### 第一步：先找 Claude 主进程
```bash
ps aux | grep "claude --permission-mode bypassPermissions --print" | grep -v grep
```

### 第二步：杀 Claude，而不是只关 screen
```bash
pkill -f "claude --permission-mode bypassPermissions --print"
```

### 第三步：再收尾 screen
```bash
screen -S 任务名 -X quit || true
```

### 第四步：复查
```bash
ps aux | egrep 'claude --permission-mode bypassPermissions --print|bash -lc .*claude --permission-mode bypassPermissions --print|login -pflq .*claude --permission-mode bypassPermissions --print' | grep -v grep
```

如果没有输出，才算真正收干净。

---

## 五、一键清残留命令

适合：发现本地 Claude Code 跑完后还挂着

```bash
pkill -f "claude --permission-mode bypassPermissions --print" || true
pkill -f "bash -lc .*claude --permission-mode bypassPermissions --print" || true
pkill -f "login -pflq .*claude --permission-mode bypassPermissions --print" || true
```

复查：
```bash
ps aux | egrep 'claude --permission-mode bypassPermissions --print|bash -lc .*claude --permission-mode bypassPermissions --print|login -pflq .*claude --permission-mode bypassPermissions --print' | grep -v grep
```

---

## 六、推荐工作流（雪子本机版）

### 场景 1：快速任务（推荐）
直接前台跑：
```bash
cd /项目目录 && claude --permission-mode bypassPermissions --print "任务"
```

### 场景 2：长任务但想后台
用 screen 启动，**只看日志，不手动 quit**，让它自然结束：
```bash
screen -dmS cc-task bash -lc "cd /项目目录 && claude --permission-mode bypassPermissions --print '任务' > ~/.openclaw/workspace/logs/cc-task.log 2>&1"
tail -f ~/.openclaw/workspace/logs/cc-task.log
```

### 场景 3：任务失控/不想等了
直接按“安全中止模板”清：
```bash
pkill -f "claude --permission-mode bypassPermissions --print"
screen -S cc-task -X quit || true
```

---

## 七、不推荐动作清单

### 不推荐 1：只关 screen
```bash
screen -S cc-task -X quit
```
**原因：**实测会留 Claude 残进程。

### 不推荐 2：跑完不复查
后台任务结束后，至少检查一次：
```bash
ps aux | grep "claude --permission-mode bypassPermissions --print" | grep -v grep
```

### 不推荐 3：频繁叠加多个 screen 任务后不清残留
实测 2~3 次后，Claude 残留可叠到 **600MB+**。

---

## 八、最终建议

### 最稳方案
1. **短任务前台跑**
2. **长任务后台跑，但让它自然结束**
3. **中止时杀 Claude，不只关 screen**
4. **每次后台任务后复查残留**

### 一句话记忆版
> Claude Code 后台任务，**结束要盯 Claude 进程，不要只盯 screen。**

---

## 九、已落地脚本（2026-04-28）

已新增两个脚本：

```bash
scripts/agent-screen-run.sh
scripts/agent-screen-clean.sh
```

### 用法示例（Claude）
```bash
cat > /tmp/cc_prompt.txt <<'EOF'
请读取当前目录并输出 5 条总结，不要修改文件。
EOF

bash ~/.openclaw/workspace/scripts/agent-screen-run.sh \
  claude cc-task-demo ~/.openclaw/workspace/projects/railway-storage-5mwh /tmp/cc_prompt.txt

# 查看日志
cat ~/.openclaw/workspace/logs/cc-task-demo.log

# 结束并清残留
bash ~/.openclaw/workspace/scripts/agent-screen-clean.sh cc-task-demo
```

### 用法示例（Codex）
```bash
cat > /tmp/codex_prompt.txt <<'EOF'
Read the current directory and summarize the project. Do not modify files.
EOF

bash ~/.openclaw/workspace/scripts/agent-screen-run.sh \
  codex codex-task-demo ~/.openclaw/workspace/projects/railway-storage-5mwh /tmp/codex_prompt.txt

bash ~/.openclaw/workspace/scripts/agent-screen-clean.sh codex-task-demo
```

---

## 十、本次实测结论（2026-04-28）

- 连续 3 次 `screen + claude --print`
- 只 `screen -X quit`
- **稳定复现残留**
- 单次残留约 **330MB**
- 多次叠加后约 **675MB~681MB**
- OpenClaw 本体未同步异常膨胀

因此可判定：
> 本地 Claude Code 的后台 screen 调用链，需要单独做“安全回收”，不能默认 screen 关闭就代表任务进程结束。
