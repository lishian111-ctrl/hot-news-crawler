"""
数据库配置模块
提供 SQLAlchemy 引擎、会话工厂和基础模型
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from typing import AsyncGenerator

from config import DATABASE_URL, DATABASE_SYNC_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT

# ==================== 异步引擎配置 ====================
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    echo=False,  # 开发环境可设为 True 以查看 SQL 日志
    future=True
)

# ==================== 同步引擎配置 ====================
sync_engine = create_engine(
    DATABASE_SYNC_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    echo=False,
    future=True
)

# ==================== 异步会话工厂 ====================
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# ==================== 同步会话工厂 ====================
SessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# ==================== 基类模型 ====================
class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于 FastAPI 路由中的数据库连接
    
    Yields:
        AsyncSession: 异步数据库会话
        
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """
    获取同步数据库会话的函数
    用于非异步上下文中的数据库操作
    
    Yields:
        Session: 同步数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """
    初始化数据库，创建所有表
    在应用启动时调用
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    关闭数据库连接
    在应用关闭时调用
    """
    await async_engine.dispose()
    sync_engine.dispose()
