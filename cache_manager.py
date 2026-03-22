#!/usr/bin/env python3
"""
股票数据缓存管理器 v2
直接使用自定义API
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# API配置
TOKEN = "d8d89556f8638c1d83426b6038fc04ea96b5da04841a07d99706f10027f3"
API_URL = "http://lianghua.nanyangqiankun.top"
BASE_DIR = Path("/opt/stock-screener-v2")
CACHE_DIR = BASE_DIR / "cache"
DATA_DIR = CACHE_DIR / "data"
METADATA_FILE = CACHE_DIR / "metadata.json"

# 缓存配置
KEEP_DAYS = 730  # 2年
BATCH_SIZE = 100  # 每批获取100只股票
MAX_WORKERS = 5  # 并发数

# 会话管理
session = requests.Session()

def api_call(api_name: str, params: dict = None) -> dict:
    """调用API"""
    data = {
        "token": TOKEN,
        "api_name": api_name,
        "params": params or {}
    }
    resp = session.post(API_URL, json=data, timeout=60)
    result = resp.json()
    if result.get("code") != 0:
        raise Exception(f"API错误: {result.get('msg', '未知错误')}")
    return result.get("data", {})

def ensure_dirs():
    """确保目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_metadata():
    """加载元数据"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_full_update": None,
        "last_daily_update": None,
        "stock_count": 0,
        "total_records": 0
    }

def save_metadata(metadata):
    """保存元数据"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_stock_list():
    """获取A股上市股票列表"""
    print("📋 获取A股股票列表...")
    data = api_call("stock_basic", {
        "exchange": "",
        "list_status": "L",
        "fields": "ts_code,symbol,name,industry,list_date"
    })
    items = data.get("items", [])
    # 转换格式
    fields = data.get("fields", [])
    stocks = []
    for item in items:
        stock = dict(zip(fields, item))
        stocks.append(stock)
    print(f"   共 {len(stocks)} 只股票")
    return stocks

def get_date_range():
    """计算日期范围"""
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=KEEP_DAYS)).strftime('%Y%m%d')
    return start_date, end_date

def get_stock_data(ts_code: str, start_date: str, end_date: str) -> dict:
    """获取单只股票数据"""
    result = {"daily": [], "weekly": [], "monthly": []}
    
    try:
        # 日线
        data = api_call("daily", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})
        items = data.get("items", [])
        if items:
            fields = data.get("fields", [])
            result["daily"] = [dict(zip(fields, item)) for item in items]
    except Exception as e:
        pass
    
    try:
        # 周线
        data = api_call("weekly", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})
        items = data.get("items", [])
        if items:
            fields = data.get("fields", [])
            result["weekly"] = [dict(zip(fields, item)) for item in items]
    except:
        pass
    
    try:
        # 月线
        data = api_call("monthly", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})
        items = data.get("items", [])
        if items:
            fields = data.get("fields", [])
            result["monthly"] = [dict(zip(fields, item)) for item in items]
    except:
        pass
    
    return result

def fetch_single_stock(stock: dict, start_date: str, end_date: str) -> tuple:
    """获取单只股票数据（线程安全）"""
    ts_code = stock['ts_code']
    try:
        data = get_stock_data(ts_code, start_date, end_date)
        return ts_code, {
            "ts_code": ts_code,
            "symbol": stock.get('symbol', ''),
            "name": stock.get('name', ''),
            "industry": stock.get('industry', ''),
            "list_date": stock.get('list_date', ''),
            "daily": data["daily"],
            "weekly": data["weekly"],
            "monthly": data["monthly"],
            "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return ts_code, None

def fetch_all_stocks():
    """全量获取所有股票数据"""
    print("\n🚀 开始全量更新...")
    ensure_dirs()
    
    # 获取股票列表
    stocks = get_stock_list()
    
    # 保存股票列表
    with open(DATA_DIR / "stock_list.json", 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)
    
    start_date, end_date = get_date_range()
    total_records = 0
    success_count = 0
    
    # 分批获取
    total_batches = (len(stocks) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(stocks), BATCH_SIZE):
        batch = stocks[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\n📦 处理批次 {batch_num}/{total_batches} ({(i+BATCH_SIZE)//len(stocks)*100}%)")
        
        # 并发获取
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_single_stock, s, start_date, end_date): s for s in batch}
            for future in as_completed(futures):
                ts_code, cache_data = future.result()
                if cache_data:
                    # 保存到文件
                    cache_file = DATA_DIR / f"{ts_code}.json"
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False)
                    
                    total_records += len(cache_data["daily"]) + len(cache_data["weekly"]) + len(cache_data["monthly"])
                    success_count += 1
        
        print(f"   ✅ 已处理 {min(i+BATCH_SIZE, len(stocks))}/{len(stocks)} 只股票")
    
    # 更新元数据
    metadata = load_metadata()
    metadata["last_full_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata["last_daily_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata["stock_count"] = success_count
    metadata["total_records"] = total_records
    save_metadata(metadata)
    
    print(f"\n✅ 全量更新完成!")
    print(f"   成功股票: {success_count}/{len(stocks)}")
    print(f"   总记录数: {total_records}")
    
    return success_count, total_records

def incremental_update():
    """增量更新"""
    print("\n🔄 开始增量更新...")
    ensure_dirs()
    
    metadata = load_metadata()
    
    # 加载股票列表
    stock_list_file = DATA_DIR / "stock_list.json"
    if not stock_list_file.exists():
        print("   ⚠️ 股票列表不存在，执行全量更新")
        return fetch_all_stocks()
    
    with open(stock_list_file, 'r', encoding='utf-8') as f:
        stocks = json.load(f)
    
    # 计算增量日期范围
    last_update = metadata.get("last_daily_update")
    if last_update:
        last_date = datetime.strptime(last_update[:10], '%Y-%m-%d')
        start_date = (last_date + timedelta(days=1)).strftime('%Y%m%d')
    else:
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    
    end_date = datetime.now().strftime('%Y%m%d')
    print(f"   增量范围: {start_date} ~ {end_date}")
    
    total_records = 0
    success_count = 0
    
    for stock in stocks:
        ts_code = stock['ts_code']
        
        # 检查现有缓存
        cache_file = DATA_DIR / f"{ts_code}.json"
        existing_data = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass
        
        # 获取增量数据
        new_data = get_stock_data(ts_code, start_date, end_date)
        
        if new_data["daily"]:
            # 合并数据
            old_daily = existing_data.get('daily', [])
            existing_daily_dates = {d.get('trade_date', '') for d in old_daily}
            
            # 只添加不存在的日期
            new_daily = [d for d in new_data["daily"] if d.get('trade_date', '') not in existing_daily_dates]
            
            if new_daily:
                # 合并
                all_daily = old_daily + new_daily
                all_daily.sort(key=lambda x: x.get('trade_date', ''))
                
                # 只保留最近2年
                cutoff_date = (datetime.now() - timedelta(days=KEEP_DAYS)).strftime('%Y%m%d')
                all_daily = [d for d in all_daily if d.get('trade_date', '') >= cutoff_date]
                
                # 保存
                cache_data = {
                    "ts_code": ts_code,
                    "symbol": stock.get('symbol', ''),
                    "name": stock.get('name', ''),
                    "industry": stock.get('industry', ''),
                    "list_date": stock.get('list_date', ''),
                    "daily": all_daily,
                    "weekly": existing_data.get('weekly', []),
                    "monthly": existing_data.get('monthly', []),
                    "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False)
                
                total_records += len(new_daily)
                success_count += 1
    
    # 更新元数据
    metadata["last_daily_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_metadata(metadata)
    
    print(f"\n✅ 增量更新完成!")
    print(f"   更新股票: {success_count}")
    print(f"   新增记录: {total_records}")
    
    return success_count, total_records

def get_cache_size():
    """获取缓存大小"""
    total_size = 0
    file_count = 0
    
    if DATA_DIR.exists():
        for f in DATA_DIR.iterdir():
            if f.is_file():
                total_size += f.stat().st_size
                file_count += 1
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total_size < 1024:
            size_str = f"{total_size:.2f} {unit}"
            break
        total_size /= 1024
    else:
        size_str = f"{total_size:.2f} TB"
    
    return size_str, file_count

def status():
    """显示缓存状态"""
    print("\n📊 缓存状态:")
    
    metadata = load_metadata()
    size_str, file_count = get_cache_size()
    
    print(f"   数据目录: {DATA_DIR}")
    print(f"   缓存大小: {size_str}")
    print(f"   股票文件: {file_count}")
    print(f"   股票数量: {metadata.get('stock_count', 0)}")
    print(f"   总记录数: {metadata.get('total_records', 0)}")
    print(f"   最后全量更新: {metadata.get('last_full_update', '从未')}")
    print(f"   最后增量更新: {metadata.get('last_daily_update', '从未')}")

if __name__ == "__main__":
    ensure_dirs()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "full":
            fetch_all_stocks()
        elif cmd == "inc" or cmd == "incremental":
            incremental_update()
        elif cmd == "status":
            status()
        else:
            print(f"未知命令: {cmd}")
            print("用法: python cache_manager.py [full|inc|status]")
    else:
        status()
