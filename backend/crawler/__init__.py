"""
爬虫模块
提供爬虫基类、通用爬虫和采集规则配置
"""

from .base import CrawlResult, BaseCrawler
from .spider import GeneralSpider

__all__ = [
    'CrawlResult',
    'BaseCrawler',
    'GeneralSpider',
]
