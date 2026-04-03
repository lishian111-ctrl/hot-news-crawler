"""
海上风电采集规则
包含：国家能源局、国家发改委、国家海洋局、生态环境部、风能协会
"""

from typing import Dict, Any, List
from ..spider import GeneralSpider


class WindRules:
    """海上风电行业网站采集规则"""
    
    # 国家能源局 - 风电新闻（首页）
    NEA_WIND = {
        'name': '国家能源局 - 风电要闻',
        'base_url': 'http://www.nea.gov.cn',
        'list_url': 'http://www.nea.gov.cn',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }

    # 国家发改委 - 能源政策
    NDRC_WIND = {
        'name': '国家发改委 - 能源政策',
        'base_url': 'https://www.ndrc.gov.cn',
        'list_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/tz/',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article_content',
    }

    # 自然资源部（原国家海洋局）
    SOA_OCEAN = {
        'name': '自然资源部 - 海洋资讯',
        'base_url': 'http://www.mnr.gov.cn',
        'list_url': 'http://www.mnr.gov.cn',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.time',
        'content_selector': 'div.content',
    }

    # 生态环境部
    MEE_EIA = {
        'name': '生态环境部 - 新闻',
        'base_url': 'https://www.mee.gov.cn',
        'list_url': 'https://www.mee.gov.cn',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article-content',
    }

    # 风能协会
    CWA_NEWS = {
        'name': '风能协会 - 行业新闻',
        'base_url': 'http://www.cwea.org.cn',
        'list_url': 'http://www.cwea.org.cn',
        'list_item_selector': 'ul.news li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }

    # 北极星风力发电网
    CHINA_WIND = {
        'name': '北极星风力发电网',
        'base_url': 'https://news.bjx.com.cn',
        'list_url': 'https://news.bjx.com.cn/nl/',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.time',
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
            'nea_wind': cls.NEA_WIND,
            'ndrc_wind': cls.NDRC_WIND,
            'soa_ocean': cls.SOA_OCEAN,
            'mee_eia': cls.MEE_EIA,
            'cwa': cls.CWA_NEWS,
            'china_wind': cls.CHINA_WIND,
        }
        return rules.get(name, {})
    
    @classmethod
    def get_all_rules(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有海上风电行业规则"""
        return {
            'nea_wind': cls.NEA_WIND,
            'ndrc_wind': cls.NDRC_WIND,
            'soa_ocean': cls.SOA_OCEAN,
            'mee_eia': cls.MEE_EIA,
            'cwa': cls.CWA_NEWS,
            'china_wind': cls.CHINA_WIND,
        }


def get_wind_crawlers() -> Dict[str, GeneralSpider]:
    """
    获取海上风电行业爬虫实例
    :return: 爬虫实例字典
    """
    crawlers = {}
    rules = WindRules.get_all_rules()
    
    for name, config in rules.items():
        crawlers[name] = GeneralSpider(config)
    
    return crawlers


def create_wind_spider(rule_name: str) -> GeneralSpider:
    """
    创建海上风电爬虫
    :param rule_name: 规则名称
    :return: GeneralSpider 实例
    """
    config = WindRules.get_rule(rule_name)
    if not config:
        raise ValueError(f"Unknown rule: {rule_name}")
    return GeneralSpider(config)
