"""
路由模块
"""
from .news import router as news_router
from .hot import router as hot_router
from .favorite import router as favorite_router
from .source import router as source_router
from .logs import router as logs_router

__all__ = [
    "news_router",
    "hot_router", 
    "favorite_router",
    "source_router",
    "logs_router"
]
