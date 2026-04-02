"""
新闻接口路由
提供新闻列表、新闻详情等 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from loguru import logger

from database import get_db
from models.news import News
from models.source import Source
from models.favorite import Favorite

router = APIRouter(prefix="/news", tags=["新闻管理"])


@router.get("/list", summary="获取新闻列表")
async def get_news_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(default=None, description="分类筛选"),
    source_id: Optional[int] = Query(default=None, description="信源 ID 筛选"),
    keyword: Optional[str] = Query(default=None, description="关键词搜索"),
    start_time: Optional[datetime] = Query(default=None, description="开始时间"),
    end_time: Optional[datetime] = Query(default=None, description="结束时间"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表，支持分页、分类筛选、信源筛选、关键词搜索、时间范围筛选
    """
    try:
        # 构建查询
        stmt = select(News).order_by(News.publish_time.desc())
        
        # 分类筛选
        if category:
            stmt = stmt.where(News.category == category)
        
        # 信源筛选
        if source_id:
            stmt = stmt.where(News.source_id == source_id)
        
        # 关键词搜索（标题或摘要）
        if keyword:
            search_pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    News.title.like(search_pattern),
                    News.summary.like(search_pattern)
                )
            )
        
        # 时间范围筛选
        if start_time:
            stmt = stmt.where(News.publish_time >= start_time)
        if end_time:
            stmt = stmt.where(News.publish_time <= end_time)
        
        # 分页
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(stmt)
        news_list = result.scalars().all()
        
        # 获取总数
        count_stmt = select(func.count(News.id))
        if category:
            count_stmt = count_stmt.where(News.category == category)
        if source_id:
            count_stmt = count_stmt.where(News.source_id == source_id)
        if keyword:
            search_pattern = f"%{keyword}%"
            count_stmt = count_stmt.where(
                or_(
                    News.title.like(search_pattern),
                    News.summary.like(search_pattern)
                )
            )
        if start_time:
            count_stmt = count_stmt.where(News.publish_time >= start_time)
        if end_time:
            count_stmt = count_stmt.where(News.publish_time <= end_time)
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 转换为字典
        news_data = []
        for news in news_list:
            news_dict = news.to_dict()
            # 关联信源信息
            if news.source:
                news_dict["source_name"] = news.source.name
            # 关联收藏信息
            news_dict["is_favorite"] = news.favorite is not None
            news_data.append(news_dict)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "list": news_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"获取新闻列表失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取新闻列表失败：{str(e)}")


@router.get("/{news_id}", summary="获取新闻详情")
async def get_news_detail(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据 ID 获取新闻详细信息
    """
    try:
        stmt = select(News).where(News.id == news_id)
        result = await db.execute(stmt)
        news = result.scalar_one_or_none()
        
        if not news:
            raise HTTPException(status_code=404, detail="新闻不存在")
        
        news_dict = news.to_dict()
        # 关联信源信息
        if news.source:
            news_dict["source_info"] = news.source.to_dict()
        # 关联收藏信息
        if news.favorite:
            news_dict["favorite_info"] = news.favorite.to_dict()
        
        return {
            "code": 200,
            "message": "success",
            "data": news_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取新闻详情失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取新闻详情失败：{str(e)}")


@router.get("/categories", summary="获取新闻分类列表")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    获取所有新闻分类及其数量
    """
    try:
        stmt = select(
            News.category,
            func.count(News.id).label("count")
        ).group_by(News.category).order_by(func.count(News.id).desc())
        
        result = await db.execute(stmt)
        categories = [
            {"category": row[0] or "未分类", "count": row[1]}
            for row in result.all()
        ]
        
        return {
            "code": 200,
            "message": "success",
            "data": categories
        }
    except Exception as e:
        logger.error(f"获取分类列表失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败：{str(e)}")


@router.delete("/{news_id}", summary="删除新闻")
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定新闻
    """
    try:
        stmt = select(News).where(News.id == news_id)
        result = await db.execute(stmt)
        news = result.scalar_one_or_none()
        
        if not news:
            raise HTTPException(status_code=404, detail="新闻不存在")
        
        await db.delete(news)
        await db.commit()
        
        return {
            "code": 200,
            "message": "success",
            "data": {"deleted_id": news_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除新闻失败：{e}")
        raise HTTPException(status_code=500, detail=f"删除新闻失败：{str(e)}")
