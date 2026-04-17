"""CLI entrypoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

from .background.manager import BackgroundTaskManager
from .background.store import BackgroundTaskStore
from .config.loader import load_settings
from .core.dispatcher import Dispatcher
from .core.models import ExecutorType, Task, TaskType
from .exceptions import AICoderError, ConfigError
from .executors.factory import ExecutorFactory
from .security.audit import JsonLineAuditLogger
from .security.sanitizer import InputSanitizer
from .skills.builtin import build_omc_skill, build_omx_skill
from .skills.loader import SkillLoader
from .skills.registry import SkillRegistry
from .skills.runner import SkillRunner


def _provider_to_executor(provider: str) -> ExecutorType:
    return ExecutorType.LOCAL if provider == "local" else ExecutorType.REMOTE


def _build_runtime(config_path: str | None) -> dict[str, Any]:
    settings = load_settings(config_path)
    sanitizer = InputSanitizer(settings.security.max_task_length)
    audit_logger = JsonLineAuditLogger(
        enabled=settings.security.enable_audit,
        path=settings.security.resolved_audit_log_path,
    )
    store = BackgroundTaskStore()
    background_manager = BackgroundTaskManager(store)
    factory = ExecutorFactory(settings)
    registry = SkillRegistry()
    registry.register(build_omc_skill())
    registry.register(build_omx_skill())
    registry.load_many(SkillLoader().load_directory(Path("skills")))
    runner = SkillRunner(registry, factory)
    dispatcher = Dispatcher(
        factory,
        skill_runner=runner,
        background_manager=background_manager,
        audit_logger=audit_logger,
    )
    return {
        "settings": settings,
        "sanitizer": sanitizer,
        "background_manager": background_manager,
        "factory": factory,
        "registry": registry,
        "dispatcher": dispatcher,
    }


def _ensure_remote_if_needed(runtime: dict[str, Any], provider: str) -> None:
    if provider == "kr":
        runtime["settings"].remote


def _validate_task_text(sanitizer: InputSanitizer, text: str) -> str:
    result = sanitizer.sanitize(text)
    if not result.is_valid:
        raise click.ClickException("; ".join(result.violations))
    return result.value


def _validate_session(sanitizer: InputSanitizer, session_name: str) -> str:
    result = sanitizer.validate_session_name(session_name)
    if not result.is_valid:
        raise click.ClickException("; ".join(result.violations))
    return result.value


def _print_result(result: Any) -> None:
    if result.output:
        click.echo(result.output.rstrip("\n"))
    if result.error:
        click.echo(result.error.rstrip("\n"), err=True)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None) -> None:
    """AI Coder."""

    try:
        ctx.obj = _build_runtime(str(config_path) if config_path else None)
    except (AICoderError, ConfigError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("exec")
@click.argument("task")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--wait/--no-wait", default=False)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def exec_command(runtime: dict[str, Any], task: str, provider: str, session: str | None, wait: bool, timeout: int) -> None:
    sanitizer = runtime["sanitizer"]
    _ensure_remote_if_needed(runtime, provider)
    command = _validate_task_text(sanitizer, task)
    session_name = _validate_session(sanitizer, session) if session else None
    task_obj = Task(
        type=TaskType.EXEC,
        executor=_provider_to_executor(provider),
        command=command,
        session_name=session_name,
        no_wait=not wait,
        timeout=timeout,
    )
    result = runtime["dispatcher"].dispatch(task_obj)
    _print_result(result)
    if not result.success:
        raise SystemExit(result.exit_code)


@cli.command("session-new")
@click.argument("name")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def session_new(runtime: dict[str, Any], name: str, provider: str, timeout: int) -> None:
    sanitizer = runtime["sanitizer"]
    _ensure_remote_if_needed(runtime, provider)
    session_name = _validate_session(sanitizer, name)
    result = runtime["dispatcher"].dispatch(
        Task(
            type=TaskType.SESSION_NEW,
            executor=_provider_to_executor(provider),
            session_name=session_name,
            no_wait=False,
            timeout=timeout,
        )
    )
    _print_result(result)
    if not result.success:
        raise SystemExit(result.exit_code)


@cli.command("session-close")
@click.argument("name")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def session_close(runtime: dict[str, Any], name: str, provider: str, timeout: int) -> None:
    sanitizer = runtime["sanitizer"]
    _ensure_remote_if_needed(runtime, provider)
    session_name = _validate_session(sanitizer, name)
    result = runtime["dispatcher"].dispatch(
        Task(
            type=TaskType.SESSION_CLOSE,
            executor=_provider_to_executor(provider),
            session_name=session_name,
            no_wait=False,
            timeout=timeout,
        )
    )
    _print_result(result)
    if not result.success:
        raise SystemExit(result.exit_code)


@cli.command("status")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--task-id")
@click.option("--json-output", is_flag=True, default=False)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def status_command(
    runtime: dict[str, Any],
    provider: str,
    session: str | None,
    task_id: str | None,
    json_output: bool,
    timeout: int,
) -> None:
    sanitizer = runtime["sanitizer"]
    if task_id:
        record = runtime["background_manager"].get_status(task_id)
        if record is None:
            raise click.ClickException(f"Task not found: {task_id}")
        click.echo(json.dumps(record, ensure_ascii=False, indent=2) if json_output else f"{record['id']} {record['status']}")
        return
    if not session:
        raise click.ClickException("Either --task-id or --session is required")
    _ensure_remote_if_needed(runtime, provider)
    session_name = _validate_session(sanitizer, session)
    result = runtime["dispatcher"].dispatch(
        Task(
            type=TaskType.STATUS,
            executor=_provider_to_executor(provider),
            session_name=session_name,
            no_wait=False,
            timeout=timeout,
        )
    )
    _print_result(result)
    if not result.success:
        raise SystemExit(result.exit_code)


@cli.command("skill")
@click.argument("skill_name")
@click.argument("task")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--wait/--no-wait", default=False)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def skill_command(
    runtime: dict[str, Any],
    skill_name: str,
    task: str,
    provider: str,
    session: str | None,
    wait: bool,
    timeout: int,
) -> None:
    sanitizer = runtime["sanitizer"]
    _ensure_remote_if_needed(runtime, provider)
    command = _validate_task_text(sanitizer, task)
    session_name = _validate_session(sanitizer, session) if session else None
    result = runtime["dispatcher"].dispatch(
        Task(
            type=TaskType.OMC,
            executor=_provider_to_executor(provider),
            command=command,
            session_name=session_name,
            skill_name=skill_name,
            no_wait=not wait,
            timeout=timeout,
        )
    )
    _print_result(result)
    if not result.success:
        raise SystemExit(result.exit_code)


@cli.command("skills")
@click.pass_obj
def list_skills(runtime: dict[str, Any]) -> None:
    for skill in runtime["registry"].list():
        click.echo(f"{skill.name}\t{skill.description}")


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except BrokenPipeError:
        sys.exit(1)
