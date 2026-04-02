"""
日志接口路由
提供日志查询、日志统计等 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from loguru import logger
import os
import re
from pathlib import Path

from database import get_db
from models.news import News
from models.source import Source
from models.favorite import Favorite

router = APIRouter(prefix="/logs", tags=["日志管理"])

LOGS_DIR = Path(__file__).parent.parent / "logs"


def parse_log_line(line: str) -> Optional[dict]:
    """解析单行日志"""
    try:
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \| (\w+) \| (.+)'
        match = re.match(pattern, line.strip())
        if match:
            return {
                "timestamp": match.group(1),
                "level": match.group(2),
                "message": match.group(3)
            }
    except:
        pass
    return None


def read_log_file(file_path: Path, lines_count: int = 100) -> List[dict]:
    """读取日志文件最后 N 行"""
    try:
        if not file_path.exists():
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines_count:] if len(all_lines) > lines_count else all_lines
            logs = []
            for line in last_lines:
                parsed = parse_log_line(line)
                if parsed:
                    logs.append(parsed)
            return logs
    except Exception:
        return []


@router.get("/recent", summary="获取最近日志")
async def get_recent_logs(
    lines: int = Query(default=100, ge=1, le=1000, description="返回日志行数"),
    level: Optional[str] = Query(default=None, description="日志级别筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近的日志记录
    """
    try:
        log_file = LOGS_DIR / "app.log"
        logs = read_log_file(log_file, lines)
        
        if level:
            logs = [log for log in logs if log["level"].upper() == level.upper()]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "count": len(logs),
                "logs": logs
            }
        }
    except Exception as e:
        logger.error("获取最近日志失败：" + str(e))
        raise HTTPException(status_code=500, detail="获取最近日志失败：" + str(e))


@router.get("/statistics", summary="获取日志统计")
async def get_log_statistics(
    days: int = Query(default=7, ge=1, le=30, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取日志统计信息
    """
    try:
        log_file = LOGS_DIR / "app.log"
        logs = read_log_file(log_file, 10000)
        
        level_counts = {}
        for log in logs:
            level = log["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        error_logs = [log for log in logs if log["level"] in ["ERROR", "CRITICAL"]]
        warning_logs = [log for log in logs if log["level"] == "WARNING"]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "period": {
                    "days": days
                },
                "level_distribution": level_counts,
                "error_count": len(error_logs),
                "warning_count": len(warning_logs),
                "recent_errors": error_logs[:20]
            }
        }
    except Exception as e:
        logger.error("获取日志统计失败：" + str(e))
        raise HTTPException(status_code=500, detail="获取日志统计失败：" + str(e))


@router.get("/system", summary="获取系统统计")
async def get_system_statistics(db: AsyncSession = Depends(get_db)):
    """
    获取系统统计数据（基于数据库）
    """
    try:
        news_count = await db.execute(select(func.count(News.id)))
        news_total = news_count.scalar()
        
        source_count = await db.execute(select(func.count(Source.id)))
        source_total = source_count.scalar()
        
        favorite_count = await db.execute(select(func.count(Favorite.id)))
        favorite_total = favorite_count.scalar()
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_news = await db.execute(
            select(func.count(News.id)).where(News.publish_time >= today)
        )
        today_total = today_news.scalar()
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "news": {"total": news_total, "today": today_total},
                "sources": {"total": source_total},
                "favorites": {"total": favorite_total}
            }
        }
    except Exception as e:
        logger.error("获取系统统计失败：" + str(e))
        raise HTTPException(status_code=500, detail="获取系统统计失败：" + str(e))


@router.get("/files", summary="获取日志文件列表")
async def get_log_files(db: AsyncSession = Depends(get_db)):
    """
    获取所有日志文件信息
    """
    try:
        if not LOGS_DIR.exists():
            return {"code": 200, "message": "success", "data": []}
        
        files = []
        for f in LOGS_DIR.glob("*.log"):
            stat = f.stat()
            files.append({
                "name": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {"code": 200, "message": "success", "data": files}
    except Exception as e:
        logger.error("获取日志文件列表失败：" + str(e))
        raise HTTPException(status_code=500, detail="获取日志文件列表失败：" + str(e))
