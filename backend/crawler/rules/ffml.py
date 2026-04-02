"""
FFML 采集规则
包含：API、DNV、ABS、国际船舶网
"""

from typing import Dict, Any, List
from ..spider import GeneralSpider


class FFMLRules:
    """FFML 相关网站采集规则"""
    
    # API (American Petroleum Institute) - 美国石油学会
    API_NEWS = {
        'name': 'API - 新闻',
        'base_url': 'https://www.api.org',
        'list_url': 'https://www.api.org/news-policy-and-issues/news',
        'list_item_selector': 'div.news-item',
        'title_selector': 'h3 a',
        'link_selector': 'h3 a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article-content',
    }
    
    # DNV (Det Norske Veritas) - 挪威船级社
    DNV_NEWS = {
        'name': 'DNV - 新闻',
        'base_url': 'https://www.dnv.com',
        'list_url': 'https://www.dnv.com/news/',
        'list_item_selector': 'article.teaser',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
        'link_attr': 'href',
        'time_selector': 'time',
        'content_selector': 'div.article-body',
    }
    
    # ABS (American Bureau of Shipping) - 美国船级社
    ABS_NEWS = {
        'name': 'ABS - 新闻',
        'base_url': 'https://www.eagle.org',
        'list_url': 'https://www.eagle.org/en/about-us/media-room/news.html',
        'list_item_selector': 'div.news-item',
        'title_selector': 'h4 a',
        'link_selector': 'h4 a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }
    
    # 国际船舶网
    WORLD_SHIP = {
        'name': '国际船舶网',
        'base_url': 'https://www.worldship.com',
        'list_url': 'https://www.worldship.com/news/',
        'list_item_selector': 'ul.news-list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article-content',
    }
    
    # 中国船舶工业行业协会
    CHINA_SHIP = {
        'name': '中国船舶工业行业协会',
        'base_url': 'http://www.cansi.org.cn',
        'list_url': 'http://www.cansi.org.cn/xhdt/',
        'list_item_selector': 'ul.news-list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.time',
        'content_selector': 'div.content',
    }
    
    # 劳氏船级社
    LR_NEWS = {
        'name': '劳氏船级社 - 新闻',
        'base_url': 'https://www.lr.org',
        'list_url': 'https://www.lr.org/en/insights/articles/',
        'list_item_selector': 'article.card',
        'title_selector': 'h3 a',
        'link_selector': 'h3 a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article-content',
    }
    
    @classmethod
    def get_rule(cls, name: str) -> Dict[str, Any]:
        """
        获取指定规则
        :param name: 规则名称
        :return: 规则配置字典
        """
        rules = {
            'api': cls.API_NEWS,
            'dnv': cls.DNV_NEWS,
            'abs': cls.ABS_NEWS,
            'world_ship': cls.WORLD_SHIP,
            'china_ship': cls.CHINA_SHIP,
            'lr': cls.LR_NEWS,
        }
        return rules.get(name, {})
    
    @classmethod
    def get_all_rules(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有 FFML 相关规则"""
        return {
            'api': cls.API_NEWS,
            'dnv': cls.DNV_NEWS,
            'abs': cls.ABS_NEWS,
            'world_ship': cls.WORLD_SHIP,
            'china_ship': cls.CHINA_SHIP,
            'lr': cls.LR_NEWS,
        }


def get_ffml_crawlers() -> Dict[str, GeneralSpider]:
    """
    获取 FFML 行业爬虫实例
    :return: 爬虫实例字典
    """
    crawlers = {}
    rules = FFMLRules.get_all_rules()
    
    for name, config in rules.items():
        crawlers[name] = GeneralSpider(config)
    
    return crawlers


def create_ffml_spider(rule_name: str) -> GeneralSpider:
    """
    创建 FFML 爬虫
    :param rule_name: 规则名称
    :return: GeneralSpider 实例
    """
    config = FFMLRules.get_rule(rule_name)
    if not config:
        raise ValueError(f"Unknown rule: {rule_name}")
    return GeneralSpider(config)
