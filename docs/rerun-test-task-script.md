# 重跑测试任务脚本 V1

## 脚本
- `scripts/rerun-test-task.sh`

## 当前能力
- 只允许重跑：
  - `cc-min-test`
  - `cc-wrapper-test`
  - `codex-wrapper-test`
- 必须存在原 meta 文件
- 必须存在原 prompt 文件
- 通过 `agent-screen-run.sh` 复用原 `AGENT / WORKDIR / PROMPT_FILE`
- 每次重跑都会生成新的任务名：
  - `原任务名-rerun-MMDD-HHMMSS`

## 风险边界
- 不支持正式项目任务
- 不支持 ACP 线程
- 不支持定时任务
- 当前是最小真实执行版，仅限测试任务试点
