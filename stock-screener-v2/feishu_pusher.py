"""
飞书推送服务
"""
import requests
from typing import List
from config import settings
from utils.logger import logger


class FeishuPusher:
    """飞书推送服务"""
    
    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self.chat_id = settings.FEISHU_CHAT_ID
        self._access_token = None
    
    def get_access_token(self) -> str:
        """获取飞书access_token"""
        if self._access_token:
            return self._access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            result = resp.json()
            
            if result.get('code') == 0:
                self._access_token = result['tenant_access_token']
                logger.info("获取飞书access_token成功")
                return self._access_token
            else:
                logger.error(f"获取飞书access_token失败: {result}")
                return None
        except Exception as e:
            logger.error(f"获取飞书access_token异常: {e}")
            return None
    
    def send_message(self, message: str) -> bool:
        """发送文本消息到群聊"""
        token = self.get_access_token()
        if not token:
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "receive_id_type": "open_id",
            "receive_id": self.chat_id,
            "msg_type": "text",
            "content": f'{{"text":"{message}"}}'
        }
        
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            result = resp.json()
            
            if result.get('code') == 0:
                logger.info("飞书消息发送成功")
                return True
            else:
                logger.error(f"飞书消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书消息发送异常: {e}")
            return False
    
    def push_grade_stocks(self, stocks: List, grade: str, cycle: str = '') -> bool:
        """推送评级股票列表"""
        if not stocks:
            logger.info(f"没有{grade}级股票需要推送")
            return True
        
        # 构建消息
        grade_name = {'A': 'A级', 'B': 'B级', 'C': 'C级'}.get(grade, grade)
        cycle_name = f"【{cycle}】" if cycle else ""
        
        title = f"📈 {cycle_name}{grade_name}股票筛选结果 ({len(stocks)}只)"
        
        # 添加标题
        message = f"**{title}**\n\n"
        message += f"筛选时间: 20:00\n"
        message += f"-" * 30 + "\n\n"
        
        # 添加股票列表（最多20只）
        display_stocks = stocks[:20]
        for i, stock in enumerate(display_stocks, 1):
            code = stock.code if hasattr(stock, 'code') else stock.get('code', '')
            name = stock.name if hasattr(stock, 'name') else stock.get('name', '')
            price = stock.stock_info.get('price', 0) if hasattr(stock, 'stock_info') else stock.get('price', 0)
            change = stock.stock_info.get('change_pct', 0) if hasattr(stock, 'stock_info') else stock.get('change_pct', 0)
            
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            message += f"{i}. {code} {name} {price:.2f} ({change_str})\n"
        
        if len(stocks) > 20:
            message += f"\n... 还有 {len(stocks) - 20} 只"
        
        message += f"\n\n{'-' * 30}\n"
        message += "数据来源: 东方财富API"
        
        return self.send_message(message)


# 全局实例
feishu_pusher = FeishuPusher()
