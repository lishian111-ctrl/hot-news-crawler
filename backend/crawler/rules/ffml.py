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
        'list_item_selector': 'ul li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'time',
        'content_selector': 'article',
    }

    # DNV (Det Norske Veritas) - 挪威船级社
    DNV_NEWS = {
        'name': 'DNV - 新闻',
        'base_url': 'https://www.dnv.com',
        'list_url': 'https://www.dnv.com/news/',
        'list_item_selector': 'article',
        'title_selector': 'h2 a, h3 a',
        'link_selector': 'h2 a, h3 a',
        'link_attr': 'href',
        'time_selector': 'time',
        'content_selector': 'div.article-body, article',
    }

    # ABS (American Bureau of Shipping) - 美国船级社
    ABS_NEWS = {
        'name': 'ABS - 新闻',
        'base_url': 'https://ww2.eagle.org',
        'list_url': 'https://ww2.eagle.org/en/about/news-and-events/news.html',
        'list_item_selector': 'ul li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }

    # 中国船舶工业行业协会
    WORLD_SHIP = {
        'name': '中国船舶工业行业协会',
        'base_url': 'http://www.cansi.org.cn',
        'list_url': 'http://www.cansi.org.cn',
        'list_item_selector': 'ul li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }

    # 国际海事组织
    CHINA_SHIP = {
        'name': '国际海事组织 - 新闻',
        'base_url': 'https://www.imo.org',
        'list_url': 'https://www.imo.org/en/MediaCentre/Pages/WhatsNew-Expanded.aspx',
        'list_item_selector': 'ul li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }

    # 劳氏船级社
    LR_NEWS = {
        'name': '劳氏船级社 - 新闻',
        'base_url': 'https://www.lr.org',
        'list_url': 'https://www.lr.org/en/insights/articles/',
        'list_item_selector': 'article, ul li',
        'title_selector': 'h3 a, a',
        'link_selector': 'h3 a, a',
        'link_attr': 'href',
        'time_selector': 'time, span.date',
        'content_selector': 'div.article-content, article',
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
