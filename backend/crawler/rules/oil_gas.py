"""
油气行业采集规则
包含：国家能源局、国家发改委、国资委、中石油、中石化、中海油
"""

from typing import Dict, Any, List
from ..spider import GeneralSpider


class OilGasRules:
    """油气行业网站采集规则"""
    
    # 国家能源局 - 油气要闻
    NEA_OIL_NEWS = {
        'name': '国家能源局 - 油气要闻',
        'base_url': 'http://www.nea.gov.cn',
        'list_url': 'http://www.nea.gov.cn/list/xw/xyyw/index.htm',
        'list_item_selector': 'ul.list-content li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }
    
    # 国家发改委 - 能源新闻
    NDRC_ENERGY = {
        'name': '国家发改委 - 能源新闻',
        'base_url': 'https://www.ndrc.gov.cn',
        'list_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghwb/',
        'list_item_selector': 'ul.list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article_content',
    }
    
    # 国资委 - 央企新闻
    SASAC_NEWS = {
        'name': '国资委 - 央企新闻',
        'base_url': 'http://www.sasac.gov.cn',
        'list_url': 'http://www.sasac.gov.cn/n4470048/n20043293/index.html',
        'list_item_selector': 'ul.new-list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.time',
        'content_selector': 'div.content',
    }
    
    # 中石油 - 公司新闻
    CNPC_NEWS = {
        'name': '中石油 - 公司新闻',
        'base_url': 'https://www.cnpc.com.cn',
        'list_url': 'https://www.cnpc.com.cn/cnpc/xwzx/gsyw/index.shtml',
        'list_item_selector': 'ul.news-list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.article-content',
    }
    
    # 中石化 - 新闻动态
    SINOPEC_NEWS = {
        'name': '中石化 - 新闻动态',
        'base_url': 'http://www.sinopecgroup.com',
        'list_url': 'http://www.sinopecgroup.com/group/xwpd/index.shtml',
        'list_item_selector': 'ul.news_list li',
        'title_selector': 'a',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }
    
    # 中海油 - 新闻中心
    CNOOC_NEWS = {
        'name': '中海油 - 新闻中心',
        'base_url': 'https://www.cnooc.com.cn',
        'list_url': 'https://www.cnooc.com.cn/art/2017/art_35/index.html',
        'list_item_selector': 'ul.news-list li',
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
            'nea_oil': cls.NEA_OIL_NEWS,
            'ndrc_energy': cls.NDRC_ENERGY,
            'sasac': cls.SASAC_NEWS,
            'cnpc': cls.CNPC_NEWS,
            'sinopec': cls.SINOPEC_NEWS,
            'cnooc': cls.CNOOC_NEWS,
        }
        return rules.get(name, {})
    
    @classmethod
    def get_all_rules(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有油气行业规则"""
        return {
            'nea_oil': cls.NEA_OIL_NEWS,
            'ndrc_energy': cls.NDRC_ENERGY,
            'sasac': cls.SASAC_NEWS,
            'cnpc': cls.CNPC_NEWS,
            'sinopec': cls.SINOPEC_NEWS,
            'cnooc': cls.CNOOC_NEWS,
        }


def get_oil_gas_crawlers() -> Dict[str, GeneralSpider]:
    """
    获取油气行业爬虫实例
    :return: 爬虫实例字典
    """
    crawlers = {}
    rules = OilGasRules.get_all_rules()
    
    for name, config in rules.items():
        crawlers[name] = GeneralSpider(config)
    
    return crawlers


def create_oil_gas_spider(rule_name: str) -> GeneralSpider:
    """
    创建油气行业爬虫
    :param rule_name: 规则名称
    :return: GeneralSpider 实例
    """
    config = OilGasRules.get_rule(rule_name)
    if not config:
        raise ValueError(f"Unknown rule: {rule_name}")
    return GeneralSpider(config)
