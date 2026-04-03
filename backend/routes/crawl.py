"""
手动采集触发接口
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

router = APIRouter(prefix="/crawl", tags=["采集管理"])

_crawl_running = False


@router.post("/run", summary="立即触发采集任务")
async def trigger_crawl(background_tasks: BackgroundTasks):
    """在后台立即运行一次完整采集任务"""
    global _crawl_running
    if _crawl_running:
        raise HTTPException(status_code=409, detail="采集任务正在运行中，请稍后再试")

    async def _run():
        global _crawl_running
        _crawl_running = True
        try:
            from scheduler.tasks import run_crawl_task
            result = await run_crawl_task()
            logger.info(f"手动采集完成: {result}")
        finally:
            _crawl_running = False

    background_tasks.add_task(_run)
    return {"code": 200, "message": "采集任务已启动，请稍后刷新查看结果"}


@router.get("/status", summary="获取采集任务状态")
async def crawl_status():
    return {"code": 200, "data": {"running": _crawl_running}}
