"""
采集规则模块
包含各行业的网站采集规则配置
"""

from .oil_gas import OilGasRules, get_oil_gas_crawlers
from .wind import WindRules, get_wind_crawlers
from .ffml import FFMLRules, get_ffml_crawlers

__all__ = [
    'OilGasRules',
    'get_oil_gas_crawlers',
    'WindRules',
    'get_wind_crawlers',
    'FFMLRules',
    'get_ffml_crawlers',
]


def get_all_rules():
    """获取所有规则"""
    rules = {}
    rules.update(get_oil_gas_crawlers())
    rules.update(get_wind_crawlers())
    rules.update(get_ffml_crawlers())
    return rules
