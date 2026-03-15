#!/usr/bin/env python3
"""
优化版每日备份脚本 v3.1
核心优化:
- Python重写，更健壮
- 内置完整PATH和HOME环境变量，解决Crontab问题
- 失败自动重试3次
- MD5+解压测试完整性校验
- 整合备份+检查为单一流程
- 精简单行通知格式
- YAML配置化

可靠性增强 (v3.1):
- 磁盘空间检查
- 锁文件机制防止并发
- 备份前源目录检查
- 信号处理(优雅退出)
- MD5校验文件存储
- 备份元数据统计
- 备份前环境预检
"""

import os
import sys
import time
import json
import shutil
import tarfile
import hashlib
import subprocess
import tempfile
import traceback
import signal
import fcntl
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Optional, Tuple, Callable, Any, Dict

try:
    import yaml
except ImportError:
    print("错误: 需要pyyaml库。请运行: pip install pyyaml")
    sys.exit(1)


# ============ 环境初始化 (解决Crontab问题) ============
def init_environment():
    """初始化环境变量，解决Crontab环境问题"""
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:' + os.environ.get('PATH', '')
    os.environ['HOME'] = os.path.expanduser('~')
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['LC_ALL'] = 'en_US.UTF-8'


init_environment()


# ============ 配置加载 ============
class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            script_dir = Path(__file__).parent.parent
            config_path = script_dir / 'config' / 'backup_config.yaml'
        
        with open(os.path.expanduser(config_path), 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        
        self.target_dir = self.data['backup']['target_dir']
        self.memory_source = os.path.expanduser(self.data['backup']['source']['memory'])
        self.skills_source = os.path.expanduser(self.data['backup']['source']['skills'])
        self.retention_days = self.data['backup']['retention_days']
        self.archive_prefix = self.data['backup']['archive_prefix']
        self.max_attempts = self.data['retry']['max_attempts']
        self.retry_delay = self.data['retry']['delay_seconds']
        self.verify_md5 = self.data['verify']['md5_enabled']
        self.verify_decompress = self.data['verify']['decompress_test_enabled']
        self.notification_enabled = self.data['notification']['enabled']
        self.notification_method = self.data['notification']['method']
        self.kilo_path = os.path.expanduser(self.data['notification']['kilo_path'])
        self.log_file = self.data['logging']['log_file']
        self.exclude_patterns = self.data['exclude']['patterns']
        
        self.min_free_space_gb = self.data.get('safety', {}).get('min_free_space_gb', 1)
        self.lock_file = os.path.expanduser(self.data.get('safety', {}).get('lock_file', '/tmp/backup.lock'))


config = Config()


# ============ 日志系统 ============
class Logger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logs = []
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} [{level}] {message}"
        self.logs.append(line)
        print(line)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        except:
            pass
    
    def info(self, msg):
        self.log(msg, "INFO")
    
    def error(self, msg):
        self.log(msg, "ERROR")
    
    def warning(self, msg):
        self.log(msg, "WARNING")


logger = Logger(config.log_file)


# ============ 锁文件机制 ============
class LockFile:
    """防止并发备份的锁文件机制"""
    def __init__(self, lock_path: str):
        self.lock_path = lock_path
        self.lock_fd = None
    
    def acquire(self) -> bool:
        try:
            self.lock_fd = open(self.lock_path, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            return True
        except (IOError, OSError):
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            return False
    
    def release(self):
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
            except:
                pass
            self.lock_fd = None
            try:
                os.remove(self.lock_path)
            except:
                pass


# ============ 全局变量 ============
lock_file = None
shutdown_requested = False


# ============ 信号处理 ============
def setup_signal_handlers():
    """设置信号处理器"""
    def signal_handler(signum, frame):
        global shutdown_requested
        logger.warning(f"收到信号 {signum}，准备优雅退出...")
        shutdown_requested = True
        if lock_file:
            lock_file.release()
        sys.exit(130)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# ============ 重试装饰器 ============
def retry_on_failure(max_attempts: int = 3, delay_seconds: int = 5):
    """失败自动重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"尝试 {attempt}/{max_attempts} 失败: {e}, {delay_seconds}秒后重试...")
                        time.sleep(delay_seconds)
                    else:
                        logger.error(f"所有 {max_attempts} 次尝试均失败: {e}")
            raise last_exception
        return wrapper
    return decorator


# ============ 校验函数 ============
def check_disk_space(path: str, required_gb: float) -> Tuple[bool, str]:
    """检查磁盘空间是否足够"""
    try:
        stat = shutil.disk_usage(path)
        free_gb = stat.free / (1024 ** 3)
        if free_gb < required_gb:
            return False, f"磁盘空间不足: {free_gb:.2f}GB < {required_gb}GB"
        return True, f"可用空间: {free_gb:.2f}GB"
    except Exception as e:
        return False, f"检查磁盘空间失败: {e}"


def check_source_directories() -> Tuple[bool, str]:
    """检查源目录是否存在且可访问"""
    errors = []
    
    if not os.path.exists(config.memory_source):
        errors.append(f"Memory源目录不存在: {config.memory_source}")
    elif not os.access(config.memory_source, os.R_OK):
        errors.append(f"Memory源目录不可读: {config.memory_source}")
    
    if not os.path.exists(config.skills_source):
        errors.append(f"Skills源目录不存在: {config.skills_source}")
    elif not os.access(config.skills_source, os.R_OK):
        errors.append(f"Skills源目录不可读: {config.skills_source}")
    
    if errors:
        return False, "; ".join(errors)
    return True, "源目录检查通过"


def preflight_checks() -> bool:
    """备份前环境预检"""
    logger.info("执行备份前预检...")
    
    global lock_file
    lock_file = LockFile(config.lock_file)
    if not lock_file.acquire():
        logger.error("无法获取锁文件，可能有其他备份进程正在运行")
        return False
    
    space_ok, space_msg = check_disk_space(config.target_dir, config.min_free_space_gb)
    logger.info(f"磁盘空间: {space_msg}")
    if not space_ok:
        logger.error(space_msg)
        return False
    
    dirs_ok, dirs_msg = check_source_directories()
    logger.info(f"源目录: {dirs_msg}")
    if not dirs_ok:
        logger.error(dirs_msg)
        return False
    
    logger.info("✅ 预检全部通过")
    return True

def calculate_md5(file_path: str) -> str:
    """计算文件的MD5值"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def verify_decompress(archive_path: str) -> bool:
    """解压测试 - 验证压缩包完整性"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(archive_path, 'r:gz') as tar:
                members = tar.getmembers()
                if len(members) == 0:
                    logger.warning("压缩包为空")
                    return False
                tar.extractall(tmpdir)
                extracted_count = sum(1 for _ in Path(tmpdir).rglob('*') if _.is_file())
                logger.info(f"解压测试成功，提取了 {extracted_count} 个文件")
                return True
    except Exception as e:
        logger.error(f"解压测试失败: {e}")
        return False


@retry_on_failure(max_attempts=3, delay_seconds=2)
def verify_archive(archive_path: str) -> Tuple[bool, str]:
    """综合校验: MD5 + 解压测试"""
    if not os.path.exists(archive_path):
        return False, "文件不存在"
    
    results = []
    status = "✅检查通过"
    
    md5 = None
    if config.verify_md5:
        md5 = calculate_md5(archive_path)
        results.append(f"MD5:{md5[:8]}")
        logger.info(f"MD5: {md5}")
        
        checksum_file = archive_path + '.md5'
        with open(checksum_file, 'w') as f:
            f.write(f"{md5}  {os.path.basename(archive_path)}\n")
        logger.info(f"MD5校验文件已保存: {checksum_file}")
    
    if config.verify_decompress:
        if not verify_decompress(archive_path):
            status = "❌解压测试失败"
            return False, status
    
    return True, status


def save_backup_metadata(archive_path: str, memory_count: int, skills_count: int, 
                          size_str: str, status: str, duration: float) -> None:
    """保存备份元数据"""
    date_str = datetime.now().strftime("%Y%m%d")
    metadata_file = os.path.join(config.target_dir, f'backup-metadata-{date_str}.json')
    
    md5 = calculate_md5(archive_path) if config.verify_md5 else None
    
    metadata = {
        "date": date_str,
        "time": datetime.now().strftime("%H:%M:%S"),
        "archive_name": os.path.basename(archive_path),
        "archive_size": size_str,
        "archive_md5": md5,
        "memory_files": memory_count,
        "skills_files": skills_count,
        "status": status,
        "duration_seconds": round(duration, 2),
        "version": "3.1-optimized"
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"备份元数据已保存: {metadata_file}")


# ============ 备份核心函数 ============
def setup_backup_structure() -> None:
    """创建备份目录结构"""
    logger.info("创建备份目录结构...")
    
    dirs = [
        'memory-backup/daily',
        'memory-backup/archive',
        'memory-backup/snapshots',
        'memory-backup/evolution',
        'memory-backup/reports',
        'memory-backup/knowledge',
        'memory-backup/index',
        'memory-backup/config',
        'skills-backup/core',
        'skills-backup/archived',
        'skills-backup/suites',
        'full-backups',
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(config.target_dir, d), exist_ok=True)
    
    logger.info("✅ 目录结构创建完成")


def backup_memory() -> int:
    """备份Memory文件，返回文件数量"""
    logger.info("开始备份 Memory...")
    
    memory_src = config.memory_source
    memory_dst = os.path.join(config.target_dir, 'memory-backup')
    file_count = 0
    
    if not os.path.exists(memory_src):
        logger.warning(f"Memory源目录不存在: {memory_src}")
        return 0
    
    for pattern in ['2*.md']:
        for src_file in Path(memory_src).glob(pattern):
            if src_file.is_file():
                dst_file = Path(memory_dst) / 'daily' / src_file.name
                shutil.copy2(src_file, dst_file)
                file_count += 1
    
    for subdir in ['archive', 'session_states', 'evolution', 'knowledge_graph', 'index']:
        src_dir = Path(memory_src) / subdir
        if src_dir.exists():
            dst_dir = Path(memory_dst) / subdir.replace('session_states', 'snapshots').replace('knowledge_graph', 'knowledge').replace('index', 'index')
            if src_dir.is_dir():
                for item in src_dir.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(src_dir)
                        dst_path = dst_dir / rel_path
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst_path)
                        file_count += 1
    
    for pattern in ['*report*.json', '*report*.md', '*.json']:
        for src_file in Path(memory_src).glob(pattern):
            if src_file.is_file():
                if 'report' in src_file.name:
                    dst_dir = Path(memory_dst) / 'reports'
                else:
                    dst_dir = Path(memory_dst) / 'config'
                dst_file = dst_dir / src_file.name
                dst_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                file_count += 1
    
    logger.info(f"✅ Memory 备份完成: {file_count} 个文件")
    return file_count


def backup_skills() -> int:
    """备份Skills文件，返回文件数量"""
    logger.info("开始备份 Skills...")
    
    skills_src = config.skills_source
    skills_dst = os.path.join(config.target_dir, 'skills-backup')
    total_count = 0
    
    if not os.path.exists(skills_src):
        logger.warning(f"Skills源目录不存在: {skills_src}")
        return 0
    
    for skill_dir in Path(skills_src).iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_name = skill_dir.name
        
        if skill_name == 'archived':
            dst_dir = Path(skills_dst) / 'archived'
        elif skill_name.endswith('-suite'):
            dst_dir = Path(skills_dst) / 'suites'
        else:
            dst_dir = Path(skills_dst) / 'core'
        
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        
        file_count = 0
        for item in skill_dir.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(skill_dir)
                dst_path = dst_dir / rel_path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if not any(excl in str(item) for excl in config.exclude_patterns):
                    shutil.copy2(item, dst_path)
                    file_count += 1
        
        total_count += file_count
        logger.info(f"  📦 [{'归档' if skill_name == 'archived' else '套件' if skill_name.endswith('-suite') else '核心'}] {skill_name}: {file_count} 个文件")
    
    logger.info(f"✅ Skills 备份完成: {total_count} 个文件")
    return total_count


def generate_manifest(memory_count: int, skills_count: int) -> str:
    """生成备份清单"""
    logger.info("生成备份清单...")
    
    date_str = datetime.now().strftime("%Y%m%d")
    manifest_file = os.path.join(config.target_dir, f'backup-manifest-{date_str}.json')
    
    manifest = {
        "backup_date": date_str,
        "backup_time": datetime.now().strftime("%H:%M:%S"),
        "version": "3.0-optimized",
        "statistics": {
            "memory_files": memory_count,
            "skills_files": skills_count,
            "total_files": memory_count + skills_count
        }
    }
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ 备份清单生成: {manifest_file}")
    return manifest_file


@retry_on_failure(max_attempts=3, delay_seconds=5)
def create_archive() -> Tuple[str, str]:
    """创建压缩包，返回(归档路径, 大小)"""
    logger.info("创建压缩包...")
    
    date_str = datetime.now().strftime("%Y%m%d")
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{config.archive_prefix}-{time_str}.tar.gz"
    archive_path = os.path.join(config.target_dir, 'full-backups', archive_name)
    
    memory_backup = os.path.join(config.target_dir, 'memory-backup')
    skills_backup = os.path.join(config.target_dir, 'skills-backup')
    
    if os.path.exists(archive_path):
        os.remove(archive_path)
    
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(memory_backup, arcname='memory-backup')
        tar.add(skills_backup, arcname='skills-backup')
        
        manifest_pattern = f"backup-manifest-{date_str}.json"
        manifest_path = os.path.join(config.target_dir, manifest_pattern)
        if os.path.exists(manifest_path):
            tar.add(manifest_path, arcname=manifest_pattern)
    
    size_bytes = os.path.getsize(archive_path)
    size_str = format_size(size_bytes)
    
    latest_link = os.path.join(config.target_dir, 'full-backups', 'latest')
    if os.path.islink(latest_link):
        os.remove(latest_link)
    os.symlink(archive_path, latest_link)
    
    logger.info(f"✅ 压缩包创建: {archive_name}, 大小: {size_str}")
    
    return archive_path, size_str


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'K', 'M', 'G']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}T"


def cleanup_old_backups() -> None:
    """清理旧备份"""
    logger.info("清理旧备份...")
    
    backup_dir = os.path.join(config.target_dir, 'full-backups')
    pattern = f"{config.archive_prefix}-*.tar.gz"
    
    backups = sorted(
        Path(backup_dir).glob(pattern),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if len(backups) > config.retention_days:
        for old_backup in backups[config.retention_days:]:
            if old_backup.name != 'latest' and not old_backup.is_symlink():
                os.remove(old_backup)
                logger.info(f"  🗑️ 删除旧备份: {old_backup.name}")
    
    logger.info("✅ 清理完成")


def send_notification(memory_count: int, skills_count: int, size_str: str, status: str) -> None:
    """发送精简单行通知"""
    if not config.notification_enabled:
        return
    
    logger.info("发送通知...")
    
    date_str = datetime.now().strftime("%m-%d %H:%M")
    message = f"💾 备份完成 | {date_str} | Memory:{memory_count} | Skills:{skills_count} | {size_str} | {status}"
    
    if config.notification_method == "kilo":
        try:
            subprocess.run(
                ['python3', config.kilo_path, '--backup', 'success', '--backup-details', message],
                capture_output=True,
                timeout=30
            )
            logger.info("✅ Kilo 通知已发送")
        except Exception as e:
            logger.warning(f"Kilo通知失败: {e}")
            simple_notify(message)
    else:
        simple_notify(message)


def simple_notify(message: str) -> None:
    """简单通知 - 打印到stdout"""
    print(f"\n{'='*60}")
    print(f" {message}")
    print(f"{'='*60}\n")


# ============ 主程序 ============
def main():
    """主函数 - 整合备份+检查为单一流程"""
    global lock_file
    
    start_time = time.time()
    
    setup_signal_handlers()
    
    logger.info("=" * 50)
    logger.info("每日备份开始 (v3.1 - 可靠性增强版)")
    logger.info("=" * 50)
    
    if not os.path.exists(config.target_dir):
        logger.error(f"FATAL: 备份目录未挂载: {config.target_dir}")
        sys.exit(1)
    
    if not preflight_checks():
        logger.error("预检失败，退出")
        if lock_file:
            lock_file.release()
        sys.exit(1)
    
    try:
        setup_backup_structure()
        
        if shutdown_requested:
            logger.warning("收到退出信号，终止备份")
            lock_file.release()
            return 130
        
        memory_count = backup_memory()
        skills_count = backup_skills()
        
        if shutdown_requested:
            logger.warning("收到退出信号，终止备份")
            lock_file.release()
            return 130
        
        generate_manifest(memory_count, skills_count)
        
        archive_path, size_str = create_archive()
        
        logger.info("执行完整性校验...")
        verify_passed, status = verify_archive(archive_path)
        
        if not verify_passed:
            logger.error("校验失败，备份可能不完整")
            status = "❌校验失败"
        
        cleanup_old_backups()
        
        duration = time.time() - start_time
        
        save_backup_metadata(archive_path, memory_count, skills_count, size_str, status, duration)
        
        total_size = sum(
            f.stat().st_size 
            for f in Path(os.path.join(config.target_dir, 'full-backups')).glob('*.tar.gz')
        )
        total_size_str = format_size(total_size)
        
        final_message = f"💾 备份完成 | {datetime.now().strftime('%m-%d %H:%M')} | Memory:{memory_count} | Skills:{skills_count} | {size_str} | {status}\n总大小: {total_size_str} | 耗时: {duration:.1f}秒"
        
        send_notification(memory_count, skills_count, size_str, status)
        
        logger.info("=" * 50)
        logger.info("备份完成")
        logger.info(final_message)
        logger.info("=" * 50)
        
        if lock_file:
            lock_file.release()
        
        return 0 if verify_passed else 1
        
    except KeyboardInterrupt:
        logger.warning("用户中断")
        if lock_file:
            lock_file.release()
        return 130
    except Exception as e:
        logger.error(f"备份失败: {e}")
        traceback.print_exc()
        if lock_file:
            lock_file.release()
        return 1


if __name__ == "__main__":
    sys.exit(main())
