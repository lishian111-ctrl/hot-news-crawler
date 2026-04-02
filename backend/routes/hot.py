"""
热点接口路由
提供每日热点、热点统计等 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from database import get_db
from models.news import News
from models.source import Source

router = APIRouter(prefix="/hot", tags=["热点管理"])


@router.get("/daily", summary="获取每日热点")
async def get_daily_hot(
    limit: int = Query(default=30, ge=1, le=100, description="返回热点数量"),
    category: Optional[str] = Query(default=None, description="分类筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日热点资讯，默认返回 30 条
    按分数和发布时间综合排序
    """
    try:
        # 获取今日零点
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 构建查询
        stmt = select(News).where(
            News.publish_time >= today
        )
        
        # 分类筛选
        if category:
            stmt = stmt.where(News.category == category)
        
        # 按分数和发布时间排序
        stmt = stmt.order_by(
            desc(News.score),
            desc(News.publish_time)
        ).limit(limit)
        
        result = await db.execute(stmt)
        news_list = result.scalars().all()
        
        # 转换为字典
        hot_news = []
        for news in news_list:
            news_dict = news.to_dict()
            if news.source:
                news_dict["source_name"] = news.source.name
            hot_news.append(news_dict)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "date": today.strftime("%Y-%m-%d"),
                "count": len(hot_news),
                "list": hot_news
            }
        }
    except Exception as e:
        logger.error(f"获取每日热点失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取每日热点失败：{str(e)}")


@router.get("/statistics", summary="获取热点统计")
async def get_hot_statistics(
    days: int = Query(default=7, ge=1, le=30, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热点统计数据，包括分类分布、信源分布、趋势等
    """
    try:
        # 计算起始时间
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 1. 分类统计
        category_stmt = select(
            News.category,
            func.count(News.id).label("count"),
            func.avg(News.score).label("avg_score")
        ).where(
            News.publish_time >= start_date,
            News.publish_time <= end_date
        ).group_by(News.category).order_by(func.count(News.id).desc())
        
        result = await db.execute(category_stmt)
        category_stats = [
            {
                "category": row[0] or "未分类",
                "count": row[1],
                "avg_score": round(row[2], 2) if row[2] else 0
            }
            for row in result.all()
        ]
        
        # 2. 信源统计
        source_stmt = select(
            Source.name,
            Source.id.label("source_id"),
            func.count(News.id).label("count")
        ).join(
            News, News.source_id == Source.id
        ).where(
            News.publish_time >= start_date,
            News.publish_time <= end_date
        ).group_by(Source.id, Source.name).order_by(func.count(News.id).desc()).limit(10)
        
        result = await db.execute(source_stmt)
        source_stats = [
            {
                "source_id": row[1],
                "source_name": row[0],
                "count": row[2]
            }
            for row in result.all()
        ]
        
        # 3. 每日趋势
        daily_stmt = select(
            func.date(News.publish_time).label("date"),
            func.count(News.id).label("count"),
            func.avg(News.score).label("avg_score")
        ).where(
            News.publish_time >= start_date,
            News.publish_time <= end_date
        ).group_by(func.date(News.publish_time)).order_by(func.date(News.publish_time))
        
        result = await db.execute(daily_stmt)
        daily_stats = [
            {
                "date": row[0].strftime("%Y-%m-%d") if row[0] else None,
                "count": row[1],
                "avg_score": round(row[2], 2) if row[2] else 0
            }
            for row in result.all()
        ]
        
        # 4. 总体统计
        total_stmt = select(
            func.count(News.id).label("total"),
            func.avg(News.score).label("avg_score"),
            func.max(News.score).label("max_score")
        ).where(
            News.publish_time >= start_date,
            News.publish_time <= end_date
        )
        
        result = await db.execute(total_stmt)
        row = result.first()
        total_stats = {
            "total_count": row[0] if row[0] else 0,
            "avg_score": round(row[1], 2) if row[1] else 0,
            "max_score": row[2] if row[2] else 0
        }
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "period": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                "category_distribution": category_stats,
                "source_distribution": source_stats,
                "daily_trend": daily_stats,
                "overview": total_stats
            }
        }
    except Exception as e:
        logger.error(f"获取热点统计失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取热点统计失败：{str(e)}")


@router.get("/trend", summary="获取热点趋势")
async def get_hot_trend(
    days: int = Query(default=7, ge=1, le=30, description="统计天数"),
    category: Optional[str] = Query(default=None, description="分类筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热点趋势数据，用于图表展示
    """
    try:
        # 计算起始时间
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        stmt = select(
            func.date(News.publish_time).label("date"),
            func.count(News.id).label("count"),
            func.avg(News.score).label("avg_score"),
            func.sum(News.score).label("total_score")
        ).where(
            News.publish_time >= start_date,
            News.publish_time <= end_date
        )
        
        if category:
            stmt = stmt.where(News.category == category)
        
        stmt = stmt.group_by(func.date(News.publish_time)).order_by(func.date(News.publish_time))
        
        result = await db.execute(stmt)
        trend_data = [
            {
                "date": row[0].strftime("%Y-%m-%d") if row[0] else None,
                "count": row[1],
                "avg_score": round(row[2], 2) if row[2] else 0,
                "total_score": row[3] if row[3] else 0
            }
            for row in result.all()
        ]
        
        return {
            "code": 200,
            "message": "success",
            "data": trend_data
        }
    except Exception as e:
        logger.error(f"获取热点趋势失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取热点趋势失败：{str(e)}")
