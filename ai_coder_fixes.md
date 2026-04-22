# AI Coder 修复清单

## 修复 1：use_direct_codex 错误处理（紧急）

**文件**：`ai_coder/executors/remote.py`

**问题**：direct codex 模式下 SESSION_NEW/SESSION_CLOSE/STATUS 返回 echo 命令，退出码是 0，CLI 误认为成功

**修复**：把 echo 改成 `echo ... && exit 1`，返回非 0 退出码

**找到方法 `_build_direct_codex_argv`**，约在第 268 行：

```python
# 原来的代码（错误）：
def _build_direct_codex_argv(self, task: Task) -> list[str]:
    if task.type == TaskType.SESSION_NEW:
        return ["echo", "Direct mode does not support session management"]
    if task.type == TaskType.SESSION_CLOSE:
        return ["echo", "Direct mode does not support session management"]
    if task.type == TaskType.STATUS:
        return ["echo", "Direct mode does not support status check"]
```

**替换为**：
```python
def _build_direct_codex_argv(self, task: Task) -> list[str]:
    if task.type == TaskType.SESSION_NEW:
        return ["bash", "-c", "echo 'Error: Direct mode does not support session management' && exit 1"]
    if task.type == TaskType.SESSION_CLOSE:
        return ["bash", "-c", "echo 'Error: Direct mode does not support session management' && exit 1"]
    if task.type == TaskType.STATUS:
        return ["bash", "-c", "echo 'Error: Direct mode does not support status check' && exit 1"]
```

---

## 修复 2：BackgroundTaskManager 注入 executor

### 2.1 修改 BackgroundTaskManager __init__

**文件**：`ai_coder/background/manager.py`

**找到 `__init__` 方法**（约第 32 行）：

```python
# 原来的代码
def __init__(self, store: TaskStore) -> None:
    self._store = store
```

**替换为**：
```python
def __init__(self, store: TaskStore, executor: Any = None) -> None:
    self._store = store
    self._executor = executor
```

### 2.2 修改 cli.py 中的调用

**文件**：`ai_coder/cli.py`

**找到创建 BackgroundTaskManager 的地方**（约第 40 行）：

```python
# 原来的代码
background_manager = BackgroundTaskManager(store)
```

**替换为**：
```python
background_manager = BackgroundTaskManager(store, executor=executor)
```

**注意**：需要先创建 executor 才能传入。找到 `background_manager = BackgroundTaskManager(store)` 的位置，在它之前添加：

```python
# Create executor for background task polling
executor = executor_factory.create(ExecutorType.LOCAL if runtime["provider"] == "local" else ExecutorType.REMOTE)
```

---

## 修复 3：doctor 支持 --config

**文件**：`ai_coder/cli.py`

**找到 `_run_doctor` 函数定义**（约第 332 行）：

```python
# 原来的代码
def _run_doctor() -> list[DoctorCheck]:
    settings = load_settings()  # 无参数！
```

**替换为**：
```python
def _run_doctor(config_path: str | None = None) -> list[DoctorCheck]:
    settings = load_settings(config_path)
```

**同时找到 `@cli.command("doctor")` 下的 doctor 函数**，修改为：

```python
@click.option("--config", "-c", "config_path", help="Path to config file")
@click.pass_obj
def doctor(runtime: dict[str, Any], config_path: str | None) -> None:
    # ... 
    checks = _run_doctor(config_path)
```

---

## 修复 4：README 删除不存在的命令

**文件**：`README.md`

**删除或注释这些行**（约 225-237 行区域）：

这些命令在 README 里写了但 CLI 里没有实现：
- `workflow inject` → 实际存在，保留
- `workflow log` → 不存在，删除
- `workflow pending` → 不存在，删除  
- `workflow runs` → 不存在，删除
- `workflow export` → 不存在，删除
- `workflow import` → 不存在，删除
- `ceo decompose` → 不存在，删除

---

## 修复 5：测试文件

**文件**：
- `ai_coder/tests/test_local_executor.py`
- `ai_coder/tests/test_remote_executor.py`

**问题**：测试调用了不存在的方法 `_build_command`、`_build_remote_argv`

**解决方案**：删除或注释这些调用了不存在方法的测试用例

---

## 验证

修复后运行：
```bash
python3 -m py_compile ai_coder/executors/remote.py
python3 -m py_compile ai_coder/background/manager.py
python3 -m py_compile ai_coder/cli.py
python3 -m ai_coder doctor
```
