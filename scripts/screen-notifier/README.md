# Screen Notifier

用 bash 监控 `screen` 任务完成，并在完成后读取日志摘要，通过飞书开放平台发群通知。

## 目录

- `screen-notifier.sh`: daemon/单次扫描
- `screen-launch.sh`: 启动 `screen` 任务并创建 job 配置
- `state/`: 已通知状态
- `runtime/`: 运行锁

## Job 文件格式

存放目录：`~/.openclaw/workspace/.screen-jobs/`

格式：

```text
screen名称|日志路径|任务描述
```

示例：

```text
demo-task|/Users/zhaoruicn/.openclaw/workspace/logs/screen-notifier/jobs/demo-task.log|测试任务
```

## 环境变量

必须：

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

可选：

```bash
export SCREEN_NOTIFIER_GROUP_ID="oc_b14195eb990ab57ea573e696758ae3d5"
export SCREEN_NOTIFIER_INTERVAL=30
export SCREEN_JOB_DIR="$HOME/.openclaw/workspace/.screen-jobs"
```

## 启动 daemon

前台运行：

```bash
bash ~/.openclaw/workspace/scripts/screen-notifier/screen-notifier.sh daemon
```

推荐用 `screen` 后台运行：

```bash
screen -dmS screen-notifier-daemon bash -lc '~/.openclaw/workspace/scripts/screen-notifier/screen-notifier.sh daemon'
```

## 启动任务

自动生成日志路径：

```bash
~/.openclaw/workspace/scripts/screen-notifier/screen-launch.sh \
  demo-task \
  "示例任务" \
  bash -lc 'echo start; sleep 5; echo done'
```

自定义日志路径：

```bash
~/.openclaw/workspace/scripts/screen-notifier/screen-launch.sh \
  demo-task \
  ~/.openclaw/workspace/logs/screen-notifier/jobs/demo.log \
  "示例任务" \
  -- \
  bash -lc 'echo start; sleep 5; echo done'
```

## 工作机制

1. `screen-launch.sh` 启动任务并写入 `.screen-jobs/*.job`
2. daemon 每 30 秒扫描一次 job 文件
3. 对应 `screen` 会话不存在时，视为任务完成
4. 读取日志尾部生成摘要
5. 发送飞书群消息
6. 发送成功后删除 job 文件，并记录 `state/*.sent`
