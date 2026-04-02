"""
通用爬虫模块
支持 CSS 选择器的通用网页爬虫
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup, Tag

from .base import CrawlResult, BaseCrawler


class GeneralSpider(BaseCrawler):
    """
    通用爬虫
    使用 CSS 选择器解析网页内容
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化通用爬虫
        :param config: 配置字典
        """
        super().__init__(config)
        self._soup: Optional[BeautifulSoup] = None
    
    def get_list_url(self, page: int = 1) -> str:
        """
        获取列表页 URL
        :param page: 页码
        :return: 列表页 URL
        """
        if '{page}' in self.base_url:
            return self.base_url.format(page=page)
        if page > 1:
            if '?' in self.base_url:
                return f"{self.base_url}&page={page}"
            else:
                return f"{self.base_url}?page={page}"
        return self.base_url
    
    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析列表页
        :param html: 列表页 HTML
        :return: 文章信息列表，包含 url, title, time 等
        """
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        # 查找列表项
        list_items = soup.select(self.list_item_selector)
        
        for item in list_items:
            article_info = {}
            
            # 提取链接
            link_elem = item.select_one(self.link_selector)
            if link_elem:
                url = link_elem.get(self.link_attr, '')
                article_info['url'] = self.normalize_url(url, self.base_url)
                article_info['title'] = self.clean_text(link_elem.get_text())
            
            # 提取标题（如果有独立的标题选择器）
            if self.title_selector:
                title_elem = item.select_one(self.title_selector)
                if title_elem:
                    article_info['title'] = self.clean_text(title_elem.get_text())
                elif link_elem:
                    article_info['title'] = self.clean_text(link_elem.get_text())
            
            # 提取时间
            if self.time_selector:
                time_elem = item.select_one(self.time_selector)
                if time_elem:
                    time_str = self.clean_text(time_elem.get_text())
                    article_info['time_str'] = time_str
                    article_info['publish_time'] = self.parse_time(time_str)
            
            # 提取作者
            if self.author_selector:
                author_elem = item.select_one(self.author_selector)
                if author_elem:
                    article_info['author'] = self.clean_text(author_elem.get_text())
            
            if article_info.get('url') and article_info.get('title'):
                items.append(article_info)
        
        return items
    
    def parse_detail(self, html: str, url: str) -> Optional[CrawlResult]:
        """
        解析详情页
        :param html: 详情页 HTML
        :param url: 文章 URL
        :return: CrawlResult 对象
        """
        soup = BeautifulSoup(html, 'html.parser')
        self._soup = soup
        
        # 提取标题
        title = ""
        if self.title_selector:
            title_elem = soup.select_one(self.title_selector)
            if title_elem:
                title = self.clean_text(title_elem.get_text())
        else:
            # 尝试常见的标题标签
            for tag in ['h1', 'h2', '.title', '#title']:
                title_elem = soup.select_one(tag)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    break
        
        if not title:
            title = self.clean_text(soup.title.string) if soup.title else ""
        
        # 提取内容
        content = ""
        if self.content_selector:
            content_elem = soup.select_one(self.content_selector)
            if content_elem:
                content = self.clean_html(str(content_elem))
        else:
            # 尝试常见的内容容器
            for tag in ['.article-content', '#content', '.content', 'article']:
                content_elem = soup.select_one(tag)
                if content_elem:
                    content = self.clean_html(str(content_elem))
                    break
        
        if not content:
            # 提取所有段落
            paragraphs = soup.find_all('p')
            content = '\n'.join([self.clean_text(p.get_text()) for p in paragraphs])
        
        # 提取时间
        publish_time = None
        if self.time_selector:
            time_elem = soup.select_one(self.time_selector)
            if time_elem:
                time_str = self.clean_text(time_elem.get_text())
                publish_time = self.parse_time(time_str)
        
        # 提取作者
        author = None
        if self.author_selector:
            author_elem = soup.select_one(self.author_selector)
            if author_elem:
                author = self.clean_text(author_elem.get_text())
        
        # 提取标签
        tags = []
        tag_elems = soup.select('.tag, .tags, .keyword, .category')
        for tag_elem in tag_elems:
            tag_text = self.clean_text(tag_elem.get_text())
            if tag_text:
                tags.append(tag_text)
        
        return CrawlResult(
            title=title,
            content=content,
            url=url,
            source=self.get_site_name(),
            publish_time=publish_time,
            author=author,
            tags=tags,
            raw_html=html
        )
    
    def select(self, selector: str) -> List[Tag]:
        """
        使用 CSS 选择器查找元素
        :param selector: CSS 选择器
        :return: 元素列表
        """
        if self._soup is None:
            return []
        return self._soup.select(selector)
    
    def select_one(self, selector: str) -> Optional[Tag]:
        """
        使用 CSS 选择器查找第一个元素
        :param selector: CSS 选择器
        :return: 元素或 None
        """
        if self._soup is None:
            return None
        return self._soup.select_one(selector)
    
    def set_html(self, html: str):
        """
        设置 HTML 内容
        :param html: HTML 字符串
        """
        self._soup = BeautifulSoup(html, 'html.parser')


def create_spider(config: Dict[str, Any]) -> GeneralSpider:
    """
    工厂函数：创建爬虫实例
    :param config: 爬虫配置
    :return: GeneralSpider 实例
    """
    return GeneralSpider(config)
