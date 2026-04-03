"""
能源行业热点资讯系统 - 主入口
FastAPI 应用启动文件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
import uvicorn

from config import (
    HOST, PORT, DEBUG,
    CORS_ORIGINS, API_PREFIX, API_TITLE,
    API_VERSION, API_DESCRIPTION,
    LOGS_DIR, FRONTEND_DIST_DIR
)
from database import init_db, close_db
from scheduler import start_scheduler, stop_scheduler

# 导入路由
from routes import (
    news_router,
    hot_router,
    favorite_router,
    source_router,
    logs_router,
    crawl_router,
    translate_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    # 启动定时任务调度器
    logger.info("正在启动定时任务调度器...")
    start_scheduler()

    logger.info("能源行业热点资讯系统启动成功")
    logger.info(f"访问地址：http://localhost:{PORT}")
    logger.info(f"API 文档：http://localhost:{PORT}/docs")

    yield

    # 关闭时执行
    logger.info("正在停止定时任务调度器...")
    stop_scheduler()

    logger.info("正在关闭数据库连接...")
    await close_db()
    logger.info("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
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

# 注册 API 路由
app.include_router(news_router, prefix=API_PREFIX)
app.include_router(hot_router, prefix=API_PREFIX)
app.include_router(favorite_router, prefix=API_PREFIX)
app.include_router(source_router, prefix=API_PREFIX)
app.include_router(logs_router, prefix=API_PREFIX)
app.include_router(crawl_router, prefix=API_PREFIX)
app.include_router(translate_router, prefix=API_PREFIX)


@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


@app.api_route("/", methods=["HEAD"])
async def root_head():
    """根路径 HEAD 支持（健康检查）"""
    from fastapi.responses import Response
    return Response(status_code=200)


# 挂载前端静态文件（放在 API 路由之后）
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """SPA 前端路由回退：所有非 API 请求返回 index.html"""
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "能源行业热点资讯系统 API",
            "version": API_VERSION,
            "docs": "/docs",
            "note": "前端未构建，请先执行 cd frontend && npm run build"
        }


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
