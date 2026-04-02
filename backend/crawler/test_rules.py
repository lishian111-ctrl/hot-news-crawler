"""
爬虫规则加载测试
"""

import sys
sys.path.insert(0, 'E:\热点资讯\backend')

from crawler import CrawlResult, BaseCrawler, GeneralSpider
from crawler.rules import (
    get_oil_gas_crawlers,
    get_wind_crawlers,
    get_ffml_crawlers,
    get_all_rules
)
from crawler.rules.oil_gas import OilGasRules
from crawler.rules.wind import WindRules
from crawler.rules.ffml import FFMLRules


def test_crawl_result():
    """测试 CrawlResult 数据类"""
    print("=" * 50)
    print("测试 CrawlResult 数据类")
    print("=" * 50)
    
    from datetime import datetime
    result = CrawlResult(
        title="测试文章",
        content="测试内容",
        url="https://example.com/article/1",
        source="测试网站",
        publish_time=datetime.now(),
        author="测试作者",
        tags=["测试", "示例"]
    )
    
    print(f"标题：{result.title}")
    print(f"内容：{result.content}")
    print(f"URL: {result.url}")
    print(f"来源：{result.source}")
    print(f"发布时间：{result.publish_time}")
    print(f"作者：{result.author}")
    print(f"标签：{result.tags}")
    print(f"字典格式：{result.to_dict()}")
    print("CrawlResult 测试通过!\n")


def test_base_crawler():
    """测试 BaseCrawler 抽象基类"""
    print("=" * 50)
    print("测试 BaseCrawler 抽象基类")
    print("=" * 50)
    
    # 测试时间解析
    spider = GeneralSpider()
    
    test_times = [
        "2024-01-15 10:30:00",
        "2024-01-15",
        "2024/01/15",
        "2024 年 01 月 15 日",
        "今天 10:30",
        "昨天 15:00",
        "3 天前",
    ]
    
    print("时间解析测试:")
    for time_str in test_times:
        parsed = spider.parse_time(time_str)
        print(f"  '{time_str}' -> {parsed}")
    
    # 测试文本清理
    dirty_text = "  测试   文本  \n  内容  "
    cleaned = spider.clean_text(dirty_text)
    print(f"\n文本清理：'{dirty_text}' -> '{cleaned}'")
    
    # 测试 HTML 清理
    dirty_html = "<div><p>测试段落</p><script>alert(1)</script></div>"
    cleaned_html = spider.clean_html(dirty_html)
    print(f"HTML 清理：'{dirty_html}' -> '{cleaned_html}'")
    
    # 测试 URL 规范化
    test_urls = [
        ("/article/1", "https://example.com"),
        ("article/1", "https://example.com/"),
        ("//example.com/article/1", "https://example.com"),
        ("https://example.com/article/1", "https://example.com"),
    ]
    
    print("\nURL 规范化测试:")
    for url, base in test_urls:
        normalized = spider.normalize_url(url, base)
        print(f"  '{url}' (base: {base}) -> '{normalized}'")
    
    print("\nBaseCrawler 测试通过!\n")


def test_general_spider():
    """测试 GeneralSpider 通用爬虫"""
    print("=" * 50)
    print("测试 GeneralSpider 通用爬虫")
    print("=" * 50)
    
    # 创建配置
    config = {
        'base_url': 'https://example.com',
        'site_name': '示例网站',
        'list_item_selector': 'ul.news li',
        'title_selector': 'a.title',
        'link_selector': 'a',
        'link_attr': 'href',
        'time_selector': 'span.date',
        'content_selector': 'div.content',
    }
    
    spider = GeneralSpider(config)
    print(f"爬虫配置:")
    print(f"  base_url: {spider.base_url}")
    print(f"  site_name: {spider.site_name}")
    print(f"  list_item_selector: {spider.list_item_selector}")
    
    # 测试列表页解析
    list_html = """
    <html>
    <body>
        <ul class="news">
            <li><a href="/news/1" class="title">新闻标题 1</a><span class="date">2024-01-15</span></li>
            <li><a href="/news/2" class="title">新闻标题 2</a><span class="date">2024-01-14</span></li>
        </ul>
    </body>
    </html>
    """
    
    items = spider.parse_list(list_html)
    print(f"\n列表页解析结果：{len(items)} 条")
    for item in items:
        print(f"  - {item['title']}: {item['url']}")
    
    # 测试详情页解析
    detail_html = """
    <html>
    <body>
        <h1 class="title">文章标题</h1>
        <div class="content">
            <p>这是第一段内容。</p>
            <p>这是第二段内容。</p>
        </div>
        <span class="date">2024-01-15 10:30:00</span>
    </body>
    </html>
    """
    
    result = spider.parse_detail(detail_html, "https://example.com/news/1")
    if result:
        print(f"\n详情页解析结果:")
        print(f"  标题：{result.title}")
        print(f"  内容：{result.content}")
        print(f"  发布时间：{result.publish_time}")
        print(f"  来源：{result.source}")
    
    print("\nGeneralSpider 测试通过!\n")


def test_oil_gas_rules():
    """测试油气行业规则"""
    print("=" * 50)
    print("测试油气行业规则")
    print("=" * 50)
    
    rules = OilGasRules.get_all_rules()
    print(f"油气行业规则数量：{len(rules)}")
    for name, config in rules.items():
        print(f"  - {name}: {config['name']} ({config['base_url']})")
    
    crawlers = get_oil_gas_crawlers()
    print(f"\n油气行业爬虫实例数量：{len(crawlers)}")
    print("油气行业规则测试通过!\n")


def test_wind_rules():
    """测试海上风电规则"""
    print("=" * 50)
    print("测试海上风电规则")
    print("=" * 50)
    
    rules = WindRules.get_all_rules()
    print(f"海上风电规则数量：{len(rules)}")
    for name, config in rules.items():
        print(f"  - {name}: {config['name']} ({config['base_url']})")
    
    crawlers = get_wind_crawlers()
    print(f"\n海上风电爬虫实例数量：{len(crawlers)}")
    print("海上风电规则测试通过!\n")


def test_ffml_rules():
    """测试 FFML 规则"""
    print("=" * 50)
    print("测试 FFML 规则")
    print("=" * 50)
    
    rules = FFMLRules.get_all_rules()
    print(f"FFML 规则数量：{len(rules)}")
    for name, config in rules.items():
        print(f"  - {name}: {config['name']} ({config['base_url']})")
    
    crawlers = get_ffml_crawlers()
    print(f"\nFFML 爬虫实例数量：{len(crawlers)}")
    print("FFML 规则测试通过!\n")


def test_all_rules():
    """测试所有规则加载"""
    print("=" * 50)
    print("测试所有规则加载")
    print("=" * 50)
    
    all_rules = get_all_rules()
    print(f"总规则数量：{len(all_rules)}")
    for name, config in all_rules.items():
        print(f"  - {name}: {config['name']}")
    
    print("\n所有规则加载测试通过!\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("爬虫基础框架测试")
    print("=" * 60 + "\n")
    
    test_crawl_result()
    test_base_crawler()
    test_general_spider()
    test_oil_gas_rules()
    test_wind_rules()
    test_ffml_rules()
    test_all_rules()
    
    print("=" * 60)
    print("所有测试通过!")
    print("=" * 60)
