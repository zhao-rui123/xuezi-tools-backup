# BOOTSTRAP.md - Session Startup

启动新会话时，先恢复上下文，再回复用户。

## Startup Sequence

按顺序读取并执行：

1. `SOUL.md`
2. `USER.md`
3. `python3 ~/.openclaw/workspace/scripts/session-snapshot.py load`
4. 当天 `memory/YYYY-MM-DD.md`
5. 最近的 sessions 历史
6. `MEMORY.md`

## First Response

恢复完成后，先告诉用户：

- 上次做到什么
- 当前还没完成什么
- 问一句“继续吗？”

不要先讲内部步骤，不要讲工具细节。

## /new Or /reset

当用户触发 `/new` 或 `/reset` 时，应该先执行：

```bash
python3 ~/.openclaw/workspace/scripts/session-snapshot.py save
```

然后在新会话启动时执行上面的 Startup Sequence。
