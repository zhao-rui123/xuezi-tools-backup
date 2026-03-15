"""
定时任务调度器
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from config import settings
from services.screening_service import screening_service
from services.feishu_pusher import feishu_pusher
from utils.logger import logger

# 中国时区
china_tz = pytz.timezone('Asia/Shanghai')


def run_screening_job():
    """执行选股任务"""
    logger.info("=" * 50)
    logger.info("开始执行定时选股任务")
    logger.info("=" * 50)
    
    try:
        start_time = datetime.now()
        
        # 执行完整筛选（月线 + 周线）
        results = screening_service.screen_all()
        
        # 推送月线A级股票
        monthly_a = results.get('monthly', {}).get('A', [])
        if monthly_a:
            logger.info(f"准备推送 {len(monthly_a)} 只月线A级股票到飞书")
            feishu_pusher.push_grade_stocks(monthly_a, 'A', '月线')
        
        # 推送周线A级股票
        weekly_a = results.get('weekly', {}).get('A', [])
        if weekly_a:
            logger.info(f"准备推送 {len(weekly_a)} 只周线A级股票到飞书")
            feishu_pusher.push_grade_stocks(weekly_a, 'A', '周线')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 50)
        logger.info(f"选股任务完成！耗时: {duration:.1f}秒")
        logger.info(f"月线A级: {len(monthly_a)} 只")
        logger.info(f"周线A级: {len(weekly_a)} 只")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"选股任务执行失败: {e}", exc_info=True)


def start_scheduler():
    """启动定时任务"""
    scheduler = BlockingScheduler(timezone=china_tz)
    
    # 每天20:00执行
    scheduler.add_job(
        run_screening_job,
        CronTrigger(hour=20, minute=0),
        id='daily_screening',
        name='每日选股任务',
        replace_existing=True
    )
    
    logger.info("定时任务已启动，每天20:00执行选股")
    logger.info(f"东财API Key: {settings.DONGFANG_CAIWU_API_KEY[:20]}...")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("定时任务已停止")
        scheduler.shutdown()


if __name__ == '__main__':
    # 测试运行
    run_screening_job()
