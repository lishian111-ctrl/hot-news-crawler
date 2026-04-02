#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立运行采集任务脚本
可通过 Windows 任务计划程序定时执行
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from scheduler.tasks import run_crawl_task


async def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始执行独立采集任务")
    logger.info(f"脚本路径：{current_dir}")
    logger.info(f"工作目录：{backend_dir}")
    logger.info("=" * 50)
    
    try:
        result = await run_crawl_task()
        logger.info("=" * 50)
        logger.info("采集任务执行成功")
        logger.info(f"结果：{result}")
        logger.info("=" * 50)
        return 0
    except Exception as e:
        logger.error(f"采集任务执行失败：{e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
