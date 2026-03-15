"""
FastAPI主程序
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from config import settings
from services.screening_service import screening_service
from utils.logger import logger

# 创建FastAPI应用
app = FastAPI(
    title="股票筛选系统V2",
    description="基于东方财富API的智能选股系统",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class StockResponse(BaseModel):
    code: str
    name: str
    grade: str
    price: float = 0
    change_pct: float = 0
    industry: str = ""
    screen_time: str = ""


class ScreeningResponse(BaseModel):
    grade: str
    count: int
    stocks: List[StockResponse]
    update_time: str


class HealthResponse(BaseModel):
    status: str
    time: str
    version: str


# API路由
@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {"message": "股票筛选系统V2 API", "version": "2.0.0"}


@app.get("/health", tags=["system"], response_model=HealthResponse)
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0.0"
    }


@app.get("/api/v1/stocks", tags=["stocks"], response_model=List[StockResponse])
async def get_stocks(
    grade: Optional[str] = Query(None, description="股票等级 A/B/C"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """获取股票列表"""
    try:
        # 加载缓存数据
        from utils.data_cache import cache
        data = cache.load_screening_results()
        
        if not data:
            raise HTTPException(status_code=404, detail="暂无筛选数据")
        
        # 筛选等级
        if grade:
            grade = grade.upper()
            if grade not in ['A', 'B', 'C']:
                raise HTTPException(status_code=400, detail="等级必须是 A/B/C")
            stocks = data.get(grade, [])
        else:
            # 返回所有
            stocks = []
            for g in ['A', 'B', 'C']:
                stocks.extend(data.get(g, []))
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        stocks = stocks[start:end]
        
        return [
            StockResponse(
                code=s.code,
                name=s.name,
                grade=s.grade,
                price=getattr(s, 'stock_info', {}).get('price', 0),
                change_pct=getattr(s, 'stock_info', {}).get('change_pct', 0),
                industry=getattr(s, 'stock_info', {}).get('industry', ''),
                screen_time=s.screen_time
            )
            for s in stocks
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/screen", tags=["stocks"], response_model=ScreeningResponse)
async def screen_stocks(
    grade: str = Query(..., description="股票等级 A/B/C"),
    limit: int = Query(50, ge=1, le=100, description="返回数量")
):
    """筛选股票"""
    try:
        grade = grade.upper()
        if grade not in ['A', 'B', 'C']:
            raise HTTPException(status_code=400, detail="等级必须是 A/B/C")
        
        # 重新执行筛选
        results = screening_service.screen_all_stocks()
        stocks = results.get(grade, [])[:limit]
        
        return ScreeningResponse(
            grade=grade,
            count=len(stocks),
            stocks=[
                StockResponse(
                    code=s.code,
                    name=s.name,
                    grade=s.grade,
                    price=getattr(s, 'stock_info', {}).get('price', 0),
                    change_pct=getattr(s, 'stock_info', {}).get('change_pct', 0),
                    industry=getattr(s, 'stock_info', {}).get('industry', ''),
                    screen_time=s.screen_time
                )
                for s in stocks
            ],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"筛选股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/detail/{code}", tags=["stocks"])
async def get_stock_detail(code: str):
    """获取股票详情"""
    try:
        detail = screening_service.get_stock_detail(code)
        
        if not detail:
            raise HTTPException(status_code=404, detail=f"股票 {code} 不存在")
        
        return detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/latest", tags=["system"])
async def get_latest():
    """获取最新筛选日期"""
    from utils.data_cache import cache
    data = cache.load_screening_results()
    
    if not data:
        return {"latest": None, "message": "暂无数据"}
    
    # 获取最新时间
    latest_time = None
    for grade in ['A', 'B', 'C']:
        for stock in data.get(grade, []):
            t = getattr(stock, 'screen_time', '')
            if t and (not latest_time or t > latest_time):
                latest_time = t
    
    return {"latest": latest_time}


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """启动API服务"""
    logger.info(f"启动API服务: {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
