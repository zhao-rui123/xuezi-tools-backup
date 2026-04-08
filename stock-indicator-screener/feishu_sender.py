#!/usr/bin/env python3
"""飞书消息推送模块"""
import os
import requests


class FeishuSender:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.environ.get(
            "FEISHU_WEBHOOK_URL",
            "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"
        )

    def _post(self, payload):
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            result = resp.json()
            if result.get("code") != 0:
                print("Feishu push failed: " + str(result.get("msg")))
                return False
            return True
        except Exception as e:
            print("Feishu push error: " + str(e))
            return False

    def send_text(self, text):
        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }
        return self._post(payload)

    def send_card(self, title, content, fields=None):
        elements = [{"tag": "div", "text": {"tag": "lark_md", "content": content}}]
        if fields:
            field_elements = []
            for f in fields:
                field_elements.append({"tag": "field", "text": {"tag": "lark_md", "content": f}})
            elements.append({"tag": "div", "fields": field_elements})
        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": "blue"
                },
                "elements": elements
            }
        }
        return self._post(card)

    def send_stock_report(self, df):
        lines = ["📊 技术指标筛选报告\n"]
        lines.append("共找到 **" + str(len(df)) + "** 只股票\n")
        lines.append("-" * 30)
        for _, row in df.iterrows():
            name = row.get("name", row.get("code", "未知"))
            code = row.get("code", "")
            close = row.get("close", 0)
            signals = row.get("signals", [])
            indicator_names = [s.get("indicator", "?") for s in signals[:3]]
            signal_str = " | ".join(["✅" + n for n in indicator_names])
            lines.append("**" + name + "**(" + code + ") $" + ("%.2f" % close))
            lines.append("信号: " + signal_str + "\n")
        return self.send_text("\n".join(lines))
