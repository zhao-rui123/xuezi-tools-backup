#!/usr/bin/env python3
"""
FTS-Jieba同步监听器 v3.0
监控OpenClaw FTS索引文件变化（事件驱动），自动触发jieba索引更新

真正的FTS更新时触发，而非轮询。
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ========== 配置 ==========
FTS_DIR = Path.home() / ".openclaw" / "memory"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
SKILL_DIR = WORKSPACE_DIR / "skills" / "memory-suite-v4"
LOG_FILE = Path.home() / ".openclaw" / "ops" / "logs" / "fts_watcher.log"
DEBOUNCE_SECONDS = 10

# ========== 日志 ==========
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

_last_trigger = 0
_observer = None

class FTSHandler(FileSystemEventHandler):
    """FTS文件变化处理器"""
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if 'claude.sqlite' in event.src_path:
            self._handle_change(event.src_path, "修改")
    
    def on_created(self, event):
        if event.is_directory:
            return
        if 'claude.sqlite' in event.src_path:
            self._handle_change(event.src_path, "创建")

    def _handle_change(self, file_path, action):
        global _last_trigger
        
        logger.info(f"📝 检测到FTS文件{action}: {Path(file_path).name}")
        
        # 防抖
        now = time.time()
        if now - _last_trigger < DEBOUNCE_SECONDS:
            logger.debug(f"⏳ 防抖跳过")
            return
        
        _last_trigger = now
        trigger_rebuild()

def trigger_rebuild():
    """触发jieba索引重建"""
    try:
        logger.info("🔄 触发jieba中文索引重建...")
        
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "cli.py"), "build-cn-index"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(WORKSPACE_DIR)
        )
        
        if result.returncode == 0:
            logger.info("✅ jieba索引重建成功")
        else:
            logger.error(f"❌ 索引重建失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ 索引重建超时(120s)")
    except Exception as e:
        logger.error(f"❌ 触发重建失败: {e}")

def main():
    global _observer
    
    logger.info("=" * 50)
    logger.info("🚀 FTS-Jieba同步监听器 v3.0 启动")
    logger.info(f"   监控目录: {FTS_DIR}")
    logger.info(f"   防抖间隔: {DEBOUNCE_SECONDS}秒")
    logger.info("=" * 50)
    
    # 启动监听
    event_handler = FTSHandler()
    _observer = Observer()
    _observer.schedule(event_handler, str(FTS_DIR), recursive=True)
    _observer.start()
    
    logger.info("✅ 监听器已启动，按Ctrl+C停止")
    
    try:
        while True:
            time.sleep(30)
            logger.debug("💓 监听中...")
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号")
        _observer.stop()
    
    _observer.join()
    logger.info("👋 监听器已停止")

if __name__ == "__main__":
    main()
