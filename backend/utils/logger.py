"""
日志工具模块
使用 loguru 进行日志配置
"""
import sys
from loguru import logger
from config import LOGS_DIR


def setup_logger(
    log_level: str = "INFO",
    log_format: str = None,
    rotation: str = "500 MB",
    retention: str = "10 days",
    compression: str = "zip",
    backtrace: bool = True,
    diagnose: bool = True,
) -> None:
    """
    配置日志记录器
    
    Args:
        log_level: 日志级别，可选 DEBUG, INFO, WARNING, ERROR, CRITICAL
        log_format: 日志格式，默认使用预定义格式
        rotation: 日志文件轮转大小
        retention: 日志文件保留时间
        compression: 日志文件压缩格式
        backtrace: 是否显示回溯 traceback
        diagnose: 是否显示诊断信息
    """
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # 移除默认的处理器
    logger.remove()
    
    # 确保日志目录存在
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=backtrace,
        diagnose=diagnose,
    )
    
    # 添加文件处理器 - 所有日志
    logger.add(
        LOGS_DIR / "app.log",
        format=log_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression=compression,
        backtrace=backtrace,
        diagnose=diagnose,
        encoding="utf-8",
    )
    
    # 添加文件处理器 - 错误日志
    logger.add(
        LOGS_DIR / "error.log",
        format=log_format,
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression=compression,
        backtrace=backtrace,
        diagnose=diagnose,
        encoding="utf-8",
    )
    
    # 添加文件处理器 - 爬虫日志
    logger.add(
        LOGS_DIR / "crawler.log",
        format=log_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression=compression,
        backtrace=backtrace,
        diagnose=diagnose,
        encoding="utf-8",
        filter=lambda record: "crawler" in record["name"].lower() or "spider" in record["name"].lower(),
    )


# 导出配置好的 logger 实例
__all__ = ["logger", "setup_logger"]


# 自动初始化日志
setup_logger()
