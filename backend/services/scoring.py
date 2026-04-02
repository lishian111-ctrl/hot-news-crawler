"""
新闻热点打分服务
四维打分策略：时效性 25 分 + 信源权重 30 分 + 关键词 25 分 + 内容类型 20 分 = 总分 100 分
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class ScoringService:
    """新闻热点打分服务类"""
    
    TIMELINESS_WEIGHT = 25
    SOURCE_WEIGHT = 30
    KEYWORD_WEIGHT = 25
    CONTENT_TYPE_WEIGHT = 20
    
    HOT_KEYWORDS = {
        "urgent": ["突发", "紧急", "重磅", "快讯", "刚刚", "breaking"],
        "important": ["重要", "焦点", "关注", "热议", "曝光", "揭秘"],
        "policy": ["政策", "发布", "规定", "通知", "公告", "实施"],
        "social": ["社会", "民生", "百姓", "民众", "市民", "公众"],
        "tech": ["科技", "创新", "AI", "人工智能", "技术", "数码"],
        "finance": ["财经", "股票", "基金", "投资", "金融", "经济"],
    }
    
    CONTENT_TYPE_SCORES = {
        "exclusive": 20,
        "investigation": 18,
        "analysis": 16,
        "interview": 15,
        "live": 14,
        "video": 12,
        "normal": 10,
        "brief": 6,
    }
    
    def __init__(self):
        self._source_weights = {}
        self._keyword_cache = {}
    
    def calculate_score(self, news_item):
        result = {"timeliness_score": 0, "source_score": 0, "keyword_score": 0, 
                  "content_type_score": 0, "total_score": 0, "score_details": {}}
        
        timeliness = self.calculate_timeliness_score(news_item.get("publish_time"))
        result["timeliness_score"] = timeliness
        
        source_score = self.calculate_source_score(news_item.get("source_id"), 
                                                    news_item.get("source_weight", 1))
        result["source_score"] = source_score
        
        keyword_score = self.calculate_keyword_score(news_item.get("title", ""), 
                                                      news_item.get("content", ""))
        result["keyword_score"] = keyword_score
        
        content_type_score = self.calculate_content_type_score(
            news_item.get("title", ""), news_item.get("content", ""), 
            news_item.get("content_type"))
        result["content_type_score"] = content_type_score
        
        total = timeliness + source_score + keyword_score + content_type_score
        result["total_score"] = min(100, int(total))
        result["score_details"] = {"timeliness": timeliness, "source": source_score,
                                    "keyword": keyword_score, "content_type": content_type_score}
        return result
    
    def calculate_timeliness_score(self, publish_time):
        if not publish_time:
            return 10
        if isinstance(publish_time, str):
            try:
                publish_time = datetime.fromisoformat(publish_time.replace("Z", "+00:00"))
            except ValueError:
                return 10
        now = datetime.now()
        if hasattr(publish_time, "tzinfo") and publish_time.tzinfo is not None:
            publish_time = publish_time.replace(tzinfo=None)
        time_diff = now - publish_time
        if time_diff < timedelta(hours=1):
            return 25
        elif time_diff < timedelta(hours=6):
            return 20
        elif time_diff < timedelta(hours=12):
            return 15
        elif time_diff < timedelta(hours=24):
            return 10
        elif time_diff < timedelta(days=3):
            return 5
        return 0
    
    def calculate_source_score(self, source_id, source_weight=1):
        weight = source_weight or 1
        if weight >= 10: return 30
        elif weight >= 7: return 25
        elif weight >= 5: return 20
        elif weight >= 3: return 15
        elif weight >= 1: return 10
        return 5
    
    def calculate_keyword_score(self, title, content):
        if not title and not content:
            return 0
        text = f"{title} {content}".lower()
        score = 0
        matched_categories = 0
        for keyword in self.HOT_KEYWORDS["urgent"]:
            if keyword in text:
                score += 8
                matched_categories += 1
                break
        for keyword in self.HOT_KEYWORDS["important"]:
            if keyword in text:
                score += 6
                matched_categories += 1
                break
        for keyword in self.HOT_KEYWORDS["policy"]:
            if keyword in text:
                score += 5
                matched_categories += 1
                break
        for keyword in self.HOT_KEYWORDS["social"]:
            if keyword in text:
                score += 4
                matched_categories += 1
                break
        for keyword in self.HOT_KEYWORDS["tech"] + self.HOT_KEYWORDS["finance"]:
            if keyword in text:
                score += 3
                matched_categories += 1
                break
        extra_score = min(4, (matched_categories - 1) * 2) if matched_categories > 1 else 0
        score += extra_score
        return min(25, score)
    
    def calculate_content_type_score(self, title, content, content_type=None):
        if content_type:
            return self.CONTENT_TYPE_SCORES.get(content_type.lower(), 10)
        text = f"{title} {content}".lower()
        if any(kw in text for kw in ["独家", "exclusive", "首发"]):
            return 20
        if any(kw in text for kw in ["深度", "调查", "investigation", "揭秘"]):
            return 18
        if any(kw in text for kw in ["分析", "评论", "观点", "解读", "评"]):
            return 16
        if any(kw in text for kw in ["专访", "访谈", "对话", "interview"]):
            return 15
        if any(kw in text for kw in ["直播", "live", "进行中"]):
            return 14
        if any(kw in text for kw in ["视频", "video", "footage"]):
            return 12
        if any(kw in text for kw in ["快讯", "brief", "简讯"]) or len(content) < 100:
            return 6
        return 10
    
    def batch_calculate_scores(self, news_list):
        results = []
        for news in news_list:
            score_result = self.calculate_score(news)
            news_with_score = news.copy()
            news_with_score["score"] = score_result["total_score"]
            news_with_score["score_details"] = score_result["score_details"]
            results.append(news_with_score)
        return results
    
    def rank_news_by_score(self, news_list):
        scored_news = self.batch_calculate_scores(news_list)
        return sorted(scored_news, key=lambda x: x.get("score", 0), reverse=True)
    
    def get_hot_news(self, news_list, threshold=60, limit=10):
        ranked = self.rank_news_by_score(news_list)
        hot_news = [news for news in ranked if news.get("score", 0) >= threshold]
        return hot_news[:limit]
    
    def update_source_weight(self, source_id, weight):
        self._source_weights[source_id] = weight
    
    def clear_source_weight_cache(self):
        self._source_weights.clear()
    
    def extract_keywords(self, text):
        if not text:
            return []
        text = text.lower()
        matched_keywords = []
        for category, keywords in self.HOT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    matched_keywords.append(keyword)
        return matched_keywords
