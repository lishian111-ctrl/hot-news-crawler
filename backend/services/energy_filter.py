"""
能源行业内容筛选服务
基于关键词匹配和规则判断，过滤与能源无关的内容
"""
import re
from typing import List, Dict, Tuple


class EnergyContentFilter:
    """能源内容过滤器"""

    # 能源行业核心关键词（高优先级）
    ENERGY_KEYWORDS = {
        # 油气类
        '油气': ['石油', '天然气', '原油', '成品油', '油气田', '炼油', '石化', '化工', '管道', '储罐'],
        '煤炭': ['煤炭', '煤矿', '焦煤', '动力煤', '煤制油', '煤化工', '采煤'],

        # 电力类
        '电力': ['电力', '电网', '发电', '供电', '输电', '配电', '电站', '电厂', '电压', '电流'],
        '核电': ['核电', '核能', '反应堆', '原子能', '核燃料'],
        '水电': ['水电', '水力发电', '水电站', '水利'],

        # 新能源类
        '风电': ['风电', '风力发电', '风机', '海上风电', '陆上风电', '风轮机'],
        '光伏': ['光伏', '太阳能', '太阳能电池', '光伏板', '光电'],
        '储能': ['储能', '电池', '锂电池', '氢能', '燃料电池', '充电桩', '蓄能'],
        '生物质': ['生物质', '生物燃料', '沼气', '垃圾发电'],

        # 能源政策类
        '政策': ['能源政策', '碳达峰', '碳中和', '双碳', '能耗', '节能', '减排', '绿色低碳'],
    }

    # 政府机构关键词
    GOVERNMENT_KEYWORDS = [
        '国家能源局', '发改委', '国家发展', '国务院', '能源局',
        '生态环境部', '自然资源部', '应急管理部', '市场监管',
        '财政部', '科技部', '工信部', '住房和城乡建设',
        '省级能源', '省能源', '市能源', '县能源'
    ]

    # 非能源类排除关键词（出现这些词的内容要过滤）
    EXCLUDE_KEYWORDS = [
        # 娱乐类
        '明星', '娱乐', '八卦', '绯闻', '综艺', '电视剧', '电影', '歌手', '演员',
        # 体育类（除非与能源相关）
        '足球', '篮球', '比赛', '运动员', '奥运会', '世界杯',
        # 生活类
        '美食', '旅游', '购物', '房产', '家居', '装修', '婚姻', '恋爱',
        # 财经类（过于宽泛的）
        '股票', '基金', '理财', '银行', '保险', '证券',
        # 其他无关
        '游戏', '手机', '数码', '汽车', ' fashion', '时尚', '美容', '化妆'
    ]

    # 政府网站域名白名单
    GOVERNMENT_DOMAINS = [
        '.gov.cn', '.org.cn', 'nea.gov.cn', 'ndrc.gov.cn', 'sasac.gov.cn',
        'xinhuanet.com', 'people.com.cn', 'cntv.cn'
    ]

    def __init__(self):
        # 编译正则表达式
        self._exclude_pattern = re.compile(
            '|'.join(re.escape(k) for k in self.EXCLUDE_KEYWORDS),
            re.IGNORECASE
        )

        # 所有能源关键词的扁平列表
        self._all_energy_keywords = []
        for category, keywords in self.ENERGY_KEYWORDS.items():
            self._all_energy_keywords.extend(keywords)

        self._energy_pattern = re.compile(
            '|'.join(re.escape(k) for k in self._all_energy_keywords),
            re.IGNORECASE
        )

    def is_energy_related(self, title: str, content: str) -> Tuple[bool, str]:
        """
        判断内容是否与能源行业相关
        :param title: 文章标题
        :param content: 文章内容
        :return: (是否相关，相关类别)
        """
        text = f"{title} {content}"
        text_lower = text.lower()

        # 1. 首先检查是否包含排除关键词
        if self._exclude_pattern.search(text):
            return False, "exclude"

        # 2. 检查是否包含能源关键词
        energy_matches = self._energy_pattern.findall(text)
        if energy_matches:
            # 找到匹配的能源类别
            category = self._find_energy_category(energy_matches)
            return True, category

        # 3. 检查是否来自政府网站且包含发展/政策等词
        gov_words = ['发展', '政策', '规划', '建设', '项目', '投资', '产业', '行业']
        if any(word in text for word in gov_words):
            if any(gov in text for gov in self.GOVERNMENT_KEYWORDS):
                return True, "policy"

        return False, "not_related"

    def _find_energy_category(self, matches: List[str]) -> str:
        """根据匹配的关键词找出能源类别"""
        for category, keywords in self.ENERGY_KEYWORDS.items():
            for match in matches:
                if match in keywords:
                    return category
        return "energy"

    def is_government_source(self, source_name: str, url: str = "") -> bool:
        """
        判断是否来自政府/官方来源
        :param source_name: 来源名称
        :param url: 来源 URL
        :return: 是否政府/官方来源
        """
        # 检查来源名称
        for gov_key in self.GOVERNMENT_KEYWORDS:
            if gov_key in source_name:
                return True

        # 检查域名
        if url:
            for gov_domain in self.GOVERNMENT_DOMAINS:
                if gov_domain in url.lower():
                    return True

        return False

    def calculate_relevance_score(self, title: str, content: str, source_name: str) -> int:
        """
        计算内容相关性得分
        :param title: 标题
        :param content: 内容
        :param source_name: 来源名称
        :return: 相关性得分 (0-100)
        """
        score = 0
        text = f"{title} {content}"

        # 能源关键词匹配得分（最高 50 分）
        energy_matches = self._energy_pattern.findall(text)
        energy_score = min(len(energy_matches) * 3, 50)
        score += energy_score

        # 政府来源得分（最高 30 分）
        if self.is_government_source(source_name):
            score += 30

        # 政策相关得分（最高 20 分）
        policy_words = ['政策', '规划', '通知', '意见', '方案', '办法', '规定']
        if any(word in title for word in policy_words):
            score += 20

        return min(score, 100)

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        批量过滤文章
        :param articles: 文章列表，每项包含 title, content, source_name 等
        :return: 过滤后的文章列表
        """
        filtered = []

        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            source_name = article.get('source', '')

            # 检查是否能源相关
            is_related, category = self.is_energy_related(title, content)

            if not is_related:
                continue

            # 计算相关性得分
            score = self.calculate_relevance_score(title, content, source_name)

            # 只保留得分达到阈值的内容
            if score >= 10:
                article['energy_category'] = category
                article['relevance_score'] = score
                filtered.append(article)

        # 按得分排序
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return filtered


# 创建全局实例
energy_filter = EnergyContentFilter()


def is_energy_content(title: str, content: str) -> bool:
    """便捷函数：判断是否为能源内容"""
    is_related, _ = energy_filter.is_energy_related(title, content)
    return is_related


def filter_energy_articles(articles: List[Dict]) -> List[Dict]:
    """便捷函数：过滤能源文章"""
    return energy_filter.filter_articles(articles)
