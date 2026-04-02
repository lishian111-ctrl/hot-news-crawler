"""
能源行业热点资讯系统 - 主入口
FastAPI 应用启动文件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from config import (
    HOST, PORT, DEBUG,
    CORS_ORIGINS, API_PREFIX, API_TITLE, 
    API_VERSION, API_DESCRIPTION,
    LOGS_DIR
)
from database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    
    logger.info(f"能源行业热点资讯系统启动成功")
    logger.info(f"API 文档地址：http://{HOST}:{PORT}/docs")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭数据库连接...")
    await close_db()
    logger.info("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    root_path=API_PREFIX,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用能源行业热点资讯系统",
        "version": API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # 确保日志目录存在
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
