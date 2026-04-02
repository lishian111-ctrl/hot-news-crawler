"""
爬虫基类模块
定义爬虫结果数据类和爬虫抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


@dataclass
class CrawlResult:
    """
    爬虫抓取结果数据类
    """
    title: str                              # 文章标题
    content: str                            # 文章内容
    url: str                                # 文章 URL
    source: str                             # 来源网站
    publish_time: Optional[datetime] = None  # 发布时间
    author: Optional[str] = None            # 作者
    tags: List[str] = field(default_factory=list)  # 标签
    raw_html: Optional[str] = None          # 原始 HTML
    extra_data: Dict[str, Any] = field(default_factory=dict)  # 额外数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'author': self.author,
            'tags': self.tags,
            'extra_data': self.extra_data
        }


class BaseCrawler(ABC):
    """
    爬虫抽象基类
    定义爬虫的基本接口和通用方法
    """
    
    # 网站配置
    base_url: str = ""
    site_name: str = ""
    
    # 选择器配置
    list_item_selector: str = ""          # 列表项选择器
    title_selector: str = ""              # 标题选择器
    content_selector: str = ""            # 内容选择器
    time_selector: str = ""               # 时间选择器
    author_selector: str = ""             # 作者选择器
    link_selector: str = "a"              # 链接选择器
    link_attr: str = "href"               # 链接属性
    
    # 时间格式配置
    time_formats: List[str] = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%Y年%m月%d日 %H:%M:%S",
        "%Y年%m月%d日 %H:%M",
        "%Y年%m月%d日",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d %b %Y %H:%M:%S",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化爬虫
        :param config: 配置字典，可覆盖默认配置
        """
        if config:
            self._apply_config(config)
    
    def _apply_config(self, config: Dict[str, Any]):
        """应用配置"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @abstractmethod
    def get_list_url(self, page: int = 1) -> str:
        """
        获取列表页 URL
        :param page: 页码
        :return: 列表页 URL
        """
        pass
    
    @abstractmethod
    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析列表页
        :param html: 列表页 HTML
        :return: 文章信息列表
        """
        pass
    
    @abstractmethod
    def parse_detail(self, html: str, url: str) -> Optional[CrawlResult]:
        """
        解析详情页
        :param html: 详情页 HTML
        :param url: 文章 URL
        :return: 抓取结果
        """
        pass
    
    def parse_time(self, time_str: str) -> Optional[datetime]:
        """
        解析时间字符串
        支持多种时间格式
        :param time_str: 时间字符串
        :return: datetime 对象
        """
        if not time_str:
            return None
        
        time_str = time_str.strip()
        
        # 处理相对时间
        now = datetime.now()
        if '分钟前' in time_str or '分钟' in time_str:
            match = re.search(r'(\d+)', time_str)
            if match:
                minutes = int(match.group(1))
                return now
        elif '小时前' in time_str or '小时' in time_str:
            match = re.search(r'(\d+)', time_str)
            if match:
                hours = int(match.group(1))
                return now
        elif '今天' in time_str or '今日' in time_str:
            time_str = time_str.replace('今天', '').replace('今日', '').strip()
            time_str = now.strftime('%Y-%m-%d') + ' ' + time_str
        elif '昨天' in time_str or '昨日' in time_str:
            time_str = time_str.replace('昨天', '').replace('昨日', '').strip()
            yesterday = now.strftime('%Y-%m-%d')
            time_str = yesterday + ' ' + time_str
        elif '天前' in time_str:
            match = re.search(r'(\d+)', time_str)
            if match:
                days = int(match.group(1))
                from datetime import timedelta
                date = now - timedelta(days=days)
                time_str = date.strftime('%Y-%m-%d')
        
        # 尝试各种时间格式
        for fmt in self.time_formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        # 尝试提取数字日期
        match = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', time_str)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        return None
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        :param text: 原始文本
        :return: 清理后的文本
        """
        if not text:
            return ""
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def clean_html(self, html: str) -> str:
        """
        清理 HTML 标签，提取纯文本
        :param html: HTML 字符串
        :return: 纯文本
        """
        if not html:
            return ""
        # 去除 script 和 style 标签
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 去除 HTML 标签
        text = re.sub(r'<[^>]+>', '', html)
        return self.clean_text(text)
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """
        规范化 URL
        :param url: 原始 URL
        :param base_url: 基础 URL
        :return: 完整的 URL
        """
        if not url:
            return ""
        url = url.strip()
        if url.startswith('http://') or url.startswith('https://'):
            return url
        if url.startswith('//'):
            return 'https:' + url
        if url.startswith('/'):
            # 绝对路径
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        # 相对路径
        if not base_url.endswith('/'):
            base_url += '/'
        return base_url + url
    
    def get_site_name(self) -> str:
        """获取网站名称"""
        return self.site_name or self.base_url
