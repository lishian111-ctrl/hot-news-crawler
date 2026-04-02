"""
收藏接口路由
提供收藏列表、添加收藏、取消收藏、更新标签等 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from loguru import logger
import json

from database import get_db
from models.favorite import Favorite
from models.news import News

router = APIRouter(prefix="/favorite", tags=["收藏管理"])


@router.get("/list", summary="获取收藏列表")
async def get_favorite_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    tag: Optional[str] = Query(default=None, description="标签筛选"),
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Favorite).order_by(Favorite.created_at.desc())
        
        if tag:
            stmt = stmt.where(Favorite.tags.contains(tag))
        
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await db.execute(stmt)
        favorites = result.scalars().all()
        
        count_stmt = select(func.count(Favorite.id))
        if tag:
            count_stmt = count_stmt.where(Favorite.tags.contains(tag))
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        favorite_data = []
        for fav in favorites:
            fav_dict = fav.to_dict()
            if fav.news:
                fav_dict["news_info"] = fav.news.to_dict()
                if fav.news.source:
                    fav_dict["news_info"]["source_name"] = fav.news.source.name
            try:
                fav_dict["tags_list"] = json.loads(fav.tags) if fav.tags else []
            except:
                fav_dict["tags_list"] = []
            favorite_data.append(fav_dict)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "list": favorite_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"获取收藏列表失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败：{str(e)}")


@router.post("/add", summary="添加收藏")
async def add_favorite(
    news_id: int = Body(..., embed=True, description="新闻 ID"),
    tags: Optional[List[str]] = Body(default=[], description="标签列表"),
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(News).where(News.id == news_id)
        result = await db.execute(stmt)
        news = result.scalar_one_or_none()
        
        if not news:
            raise HTTPException(status_code=404, detail="新闻不存在")
        
        stmt = select(Favorite).where(Favorite.news_id == news_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="该新闻已在收藏中")
        
        tags_json = json.dumps(tags) if tags else "[]"
        favorite = Favorite(
            news_id=news_id,
            tags=tags_json,
            created_at=datetime.utcnow()
        )
        
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "id": favorite.id,
                "news_id": favorite.news_id,
                "tags": tags,
                "created_at": favorite.created_at.isoformat() if favorite.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加收藏失败：{e}")
        raise HTTPException(status_code=500, detail=f"添加收藏失败：{str(e)}")


@router.delete("/{favorite_id}", summary="取消收藏")
async def remove_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Favorite).where(Favorite.id == favorite_id)
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="收藏记录不存在")
        
        await db.delete(favorite)
        await db.commit()
        
        return {
            "code": 200,
            "message": "success",
            "data": {"deleted_id": favorite_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消收藏失败：{e}")
        raise HTTPException(status_code=500, detail=f"取消收藏失败：{str(e)}")


@router.delete("/by_news/{news_id}", summary="通过新闻 ID 取消收藏")
async def remove_favorite_by_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Favorite).where(Favorite.news_id == news_id)
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="收藏记录不存在")
        
        await db.delete(favorite)
        await db.commit()
        
        return {
            "code": 200,
            "message": "success",
            "data": {"deleted_news_id": news_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消收藏失败：{e}")
        raise HTTPException(status_code=500, detail=f"取消收藏失败：{str(e)}")


@router.put("/{favorite_id}/tags", summary="更新收藏标签")
async def update_favorite_tags(
    favorite_id: int,
    tags: List[str] = Body(..., embed=True, description="标签列表"),
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Favorite).where(Favorite.id == favorite_id)
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="收藏记录不存在")
        
        favorite.tags = json.dumps(tags)
        await db.commit()
        await db.refresh(favorite)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "id": favorite.id,
                "news_id": favorite.news_id,
                "tags": tags,
                "updated_at": favorite.created_at.isoformat() if favorite.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新标签失败：{e}")
        raise HTTPException(status_code=500, detail=f"更新标签失败：{str(e)}")


@router.get("/tags", summary="获取所有收藏标签")
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Favorite.tags).where(Favorite.tags.isnot(None))
        result = await db.execute(stmt)
        rows = result.scalars().all()
        
        tag_count = {}
        for tags_json in rows:
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    tag_count[tag] = tag_count.get(tag, 0) + 1
            except:
                continue
        
        tags_list = [
            {"tag": tag, "count": count}
            for tag, count in tag_count.items()
        ]
        tags_list.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "code": 200,
            "message": "success",
            "data": tags_list
        }
    except Exception as e:
        logger.error(f"获取标签列表失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取标签列表失败：{str(e)}")
