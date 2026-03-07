#!/usr/bin/env python3
"""
电价数据自动抓取器
自动抓取各省发改委/电网公司最新电价政策
"""

import json
import argparse
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install httpx beautifulsoup4")
    raise

# 省份代码映射
PROVINCE_MAP = {
    "北京": "beijing", "天津": "tianjin", "河北": "hebei", "山西": "shanxi",
    "内蒙古": "neimenggu", "辽宁": "liaoning", "吉林": "jilin", "黑龙江": "heilongjiang",
    "上海": "shanghai", "江苏": "jiangsu", "浙江": "zhejiang", "安徽": "anhui",
    "福建": "fujian", "江西": "jiangxi", "山东": "shandong", "河南": "henan",
    "湖北": "hubei", "湖南": "hunan", "广东": "guangdong", "广西": "guangxi",
    "海南": "hainan", "重庆": "chongqing", "四川": "sichuan", "贵州": "guizhou",
    "云南": "yunnan", "西藏": "xizang", "陕西": "shaanxi", "甘肃": "gansu",
    "青海": "qinghai", "宁夏": "ningxia", "新疆": "xinjiang", "兵团": "bingtuan"
}

# 数据源配置
DATA_SOURCES = {
    "河南": {
        "name": "河南省发改委",
        "base_url": "https://fgw.henan.gov.cn",
        "search_url": "https://fgw.henan.gov.cn/search/search.jsp",
        "keywords": ["电价", "分时电价", "工商业电价"],
        "enabled": True
    },
    "山东": {
        "name": "山东省发改委",
        "base_url": "https://fgw.shandong.gov.cn",
        "search_url": "https://fgw.shandong.gov.cn/search/",
        "keywords": ["电价", "分时电价"],
        "enabled": True
    },
    "浙江": {
        "name": "浙江省发改委",
        "base_url": "https://fzggw.zj.gov.cn",
        "search_url": "https://fzggw.zj.gov.cn/search/",
        "keywords": ["电价", "分时电价"],
        "enabled": True
    },
    "广东": {
        "name": "广东省发改委",
        "base_url": "https://drc.gd.gov.cn",
        "search_url": "https://drc.gd.gov.cn/search/",
        "keywords": ["电价", "分时电价"],
        "enabled": True
    },
    "江苏": {
        "name": "江苏省发改委",
        "base_url": "https://fzggw.jiangsu.gov.cn",
        "search_url": "https://fzggw.jiangsu.gov.cn/search/",
        "keywords": ["电价", "分时电价"],
        "enabled": True
    }
}

class ElectricityPriceCrawler:
    """电价数据抓取器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "~/.openclaw/workspace/data/electricity-prices").expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def search_price_docs(self, province: str, year: int = None) -> List[Dict]:
        """搜索电价政策文件"""
        source = DATA_SOURCES.get(province)
        if not source or not source.get("enabled"):
            print(f"⚠️ {province} 暂不支持自动抓取")
            return []
        
        results = []
        year_str = str(year) if year else "2026"
        
        try:
            # 尝试从搜索页面获取
            print(f"🔍 正在搜索 {province} {year_str}年电价政策...")
            
            # 模拟搜索 - 实际实现需要针对每个网站定制
            search_keywords = f"{year_str} 工商业 分时电价"
            
            # 这里使用简单的HTTP请求示例
            # 实际开发时需要针对每个网站编写专门的解析逻辑
            response = await self.session.get(
                source["base_url"],
                follow_redirects=True
            )
            
            if response.status_code == 200:
                # 解析HTML查找电价相关信息
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取可能的政策链接（简化示例）
                links = soup.find_all('a', href=True)
                for link in links:
                    text = link.get_text(strip=True)
                    if any(kw in text for kw in source["keywords"]):
                        if year_str in text or str(int(year_str)-1) in text:
                            results.append({
                                "title": text,
                                "url": link['href'] if link['href'].startswith('http') else source["base_url"] + link['href'],
                                "date": None  # 需要进一步解析
                            })
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        return results[:5]  # 返回前5个结果
    
    def extract_price_data(self, html_content: str) -> Dict:
        """从HTML内容中提取电价数据"""
        data = {
            "time_of_use": {},
            "capacity_price": None,
            "transmission_price": None
        }
        
        # 使用正则表达式提取电价数据
        # 这是一个简化版本，实际开发需要更复杂的解析
        
        # 提取峰时电价
        peak_pattern = r'峰.*?电.*?价.*?([0-9.]+).*?元'
        valley_pattern = r'谷.*?电.*?价.*?([0-9.]+).*?元'
        flat_pattern = r'平.*?电.*?价.*?([0-9.]+).*?元'
        
        peak_match = re.search(peak_pattern, html_content)
        if peak_match:
            data["time_of_use"]["peak"] = {"price": float(peak_match.group(1))}
        
        valley_match = re.search(valley_pattern, html_content)
        if valley_match:
            data["time_of_use"]["valley"] = {"price": float(valley_match.group(1))}
        
        flat_match = re.search(flat_pattern, html_content)
        if flat_match:
            data["time_of_use"]["flat"] = {"price": float(flat_match.group(1))}
        
        return data
    
    async def fetch_province(self, province: str, year: int = 2026, dry_run: bool = False) -> Optional[Dict]:
        """抓取单个省份的电价数据"""
        
        print(f"\n📍 正在处理: {province}")
        
        # 搜索政策文件
        docs = await self.search_price_docs(province, year)
        
        if not docs:
            print(f"⚠️ 未找到 {province} {year}年电价政策")
            return None
        
        # 显示搜索结果
        print(f"📄 找到 {len(docs)} 个可能相关的政策文件:")
        for i, doc in enumerate(docs, 1):
            print(f"  {i}. {doc['title']}")
            print(f"     URL: {doc['url']}")
        
        # 简化版本：返回基础数据结构
        result = {
            "province": province,
            "province_code": PROVINCE_MAP.get(province, ""),
            "year": year,
            "month": datetime.now().month,
            "source_docs": docs,
            "fetch_time": datetime.now().isoformat(),
            "time_of_use": {
                "peak": {"hours": ["08:00-12:00", "18:00-22:00"], "price": None},
                "valley": {"hours": ["00:00-08:00"], "price": None},
                "flat": {"hours": ["12:00-18:00", "22:00-24:00"], "price": None}
            },
            "capacity_price": None,
            "transmission_price": None,
            "notes": "需要人工确认价格数据"
        }
        
        if dry_run:
            print(f"\n🔍 [测试模式] 数据预览:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        
        # 保存数据
        filename = f"{PROVINCE_MAP.get(province, province)}_{year}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据已保存: {filepath}")
        return result
    
    async def fetch_all(self, year: int = 2026, dry_run: bool = False):
        """抓取所有省份数据"""
        enabled_provinces = [p for p, s in DATA_SOURCES.items() if s.get("enabled")]
        
        print(f"\n🚀 开始抓取 {len(enabled_provinces)} 个省份的电价数据...")
        print(f"年份: {year}")
        print(f"模式: {'测试' if dry_run else '正式'}")
        print("=" * 50)
        
        results = []
        for province in enabled_provinces:
            result = await self.fetch_province(province, year, dry_run)
            if result:
                results.append(result)
            await asyncio.sleep(1)  # 避免请求过快
        
        print("\n" + "=" * 50)
        print(f"✅ 完成! 成功抓取 {len(results)}/{len(enabled_provinces)} 个省份")
        return results


def list_sources():
    """列出所有支持的数据源"""
    print("\n📋 支持的数据源:")
    print("-" * 60)
    for province, config in DATA_SOURCES.items():
        status = "✅ 启用" if config.get("enabled") else "❌ 禁用"
        print(f"{province:8s} | {config['name']:20s} | {status}")
    print("-" * 60)
    enabled = sum(1 for s in DATA_SOURCES.values() if s.get("enabled"))
    print(f"总计: {len(DATA_SOURCES)} 个省份, {enabled} 个已启用")


async def main():
    parser = argparse.ArgumentParser(description="电价数据自动抓取器")
    parser.add_argument("--province", "-p", help="指定省份")
    parser.add_argument("--year", "-y", type=int, default=2026, help="年份")
    parser.add_argument("--all", "-a", action="store_true", help="抓取所有省份")
    parser.add_argument("--dry-run", "-d", action="store_true", help="测试模式（不保存）")
    parser.add_argument("--list-sources", "-l", action="store_true", help="列出数据源")
    parser.add_argument("--output", "-o", help="输出目录")
    
    args = parser.parse_args()
    
    if args.list_sources:
        list_sources()
        return
    
    async with ElectricityPriceCrawler(output_dir=args.output) as crawler:
        if args.all:
            await crawler.fetch_all(args.year, args.dry_run)
        elif args.province:
            await crawler.fetch_province(args.province, args.year, args.dry_run)
        else:
            parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
