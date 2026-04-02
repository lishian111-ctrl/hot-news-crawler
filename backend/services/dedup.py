"""
新闻去重服务
基于标题相似度和内容相似度判断重复新闻
"""
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher


class DedupService:
    """新闻去重服务类"""
    
    # 相似度阈值
    TITLE_SIMILARITY_THRESHOLD = 0.80  # 标题相似度 > 80% 判定重复
    CONTENT_SIMILARITY_THRESHOLD = 0.70  # 内容相似度 > 70% 判定重复
    
    def __init__(self):
        """初始化去重服务"""
        self._news_cache: Dict[str, Dict[str, Any]] = {}  # 缓存已处理的新闻
    
    def compute_content_hash(self, content: str) -> str:
        """
        计算内容哈希值
        
        Args:
            content: 内容字符串
            
        Returns:
            SHA256 哈希值
        """
        if not content:
            return hashlib.sha256(b"").hexdigest()
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def compute_title_hash(self, title: str) -> str:
        """
        计算标题哈希值
        
        Args:
            title: 标题字符串
            
        Returns:
            SHA256 哈希值
        """
        if not title:
            return hashlib.sha256(b"").hexdigest()
        return hashlib.sha256(title.encode("utf-8")).hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（0-1 之间）
        
        Args:
            text1: 文本 1
            text2: 文本 2
            
        Returns:
            相似度分数
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用 SequenceMatcher 计算相似度
        return SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        计算标题相似度
        
        Args:
            title1: 标题 1
            title2: 标题 2
            
        Returns:
            相似度分数（0-1）
        """
        if not title1 or not title2:
            return 0.0
        
        # 预处理：去除特殊字符、空白符
        t1 = self._preprocess_text(title1)
        t2 = self._preprocess_text(title2)
        
        return self.calculate_similarity(t1, t2)
    
    def calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        计算内容相似度
        
        Args:
            content1: 内容 1
            content2: 内容 2
            
        Returns:
            相似度分数（0-1）
        """
        if not content1 or not content2:
            return 0.0
        
        # 预处理
        c1 = self._preprocess_text(content1)
        c2 = self._preprocess_text(content2)
        
        # 对于长文本，可以分段比较取平均值
        if len(c1) > 5000 or len(c2) > 5000:
            return self._calculate_long_text_similarity(c1, c2)
        
        return self.calculate_similarity(c1, c2)
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本：去除特殊字符、多余空白等
        
        Args:
            text: 原始文本
            
        Returns:
            预处理后的文本
        """
        if not text:
            return ""
        
        # 去除首尾空白
        text = text.strip()
        
        # 去除常见特殊字符（保留中文、英文、数字）
        import re
        text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        
        return text
    
    def _calculate_long_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算长文本相似度（分块比较）
        
        Args:
            text1: 文本 1
            text2: 文本 2
            
        Returns:
            相似度分数
        """
        # 将长文本分块
        chunk_size = 2000
        chunks1 = [text1[i:i+chunk_size] for i in range(0, len(text1), chunk_size)]
        chunks2 = [text2[i:i+chunk_size] for i in range(0, len(text2), chunk_size)]
        
        similarities = []
        for chunk1 in chunks1[:5]:  # 限制比较的块数
            best_match = 0.0
            for chunk2 in chunks2[:5]:
                sim = self.calculate_similarity(chunk1, chunk2)
                best_match = max(best_match, sim)
            similarities.append(best_match)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def is_duplicate(self, title1: str, content1: str, 
                     title2: str, content2: str) -> Tuple[bool, str]:
        """
        判断两篇新闻是否重复
        
        Args:
            title1: 新闻 1 标题
            content1: 新闻 1 内容
            title2: 新闻 2 标题
            content2: 新闻 2 内容
            
        Returns:
            (是否重复，重复原因)
        """
        # 检查标题相似度
        title_sim = self.calculate_title_similarity(title1, title2)
        if title_sim >= self.TITLE_SIMILARITY_THRESHOLD:
            return True, f"title_similar:{title_sim:.2f}"
        
        # 检查内容相似度
        content_sim = self.calculate_content_similarity(content1, content2)
        if content_sim >= self.CONTENT_SIMILARITY_THRESHOLD:
            return True, f"content_similar:{content_sim:.2f}"
        
        return False, ""
    
    def check_duplicates(self, news_item: Dict[str, Any], 
                        existing_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检查新闻是否与现有新闻重复
        
        Args:
            news_item: 待检查的新闻项（包含 title, content 等字段）
            existing_news: 现有新闻列表
            
        Returns:
            重复的新闻列表
        """
        duplicates = []
        
        title = news_item.get("title", "")
        content = news_item.get("content", "")
        
        for existing in existing_news:
            is_dup, reason = self.is_duplicate(
                title, content,
                existing.get("title", ""),
                existing.get("content", "")
            )
            
            if is_dup:
                duplicates.append({
                    "news": existing,
                    "reason": reason
                })
        
        return duplicates
    
    def deduplicate_news_list(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对新闻列表进行去重
        
        Args:
            news_list: 新闻列表
            
        Returns:
            去重后的新闻列表
        """
        if not news_list:
            return []
        
        unique_news = []
        
        for news in news_list:
            duplicates = self.check_duplicates(news, unique_news)
            if not duplicates:
                unique_news.append(news)
        
        return unique_news
    
    def find_best_match(self, news_item: Dict[str, Any], 
                       existing_news: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        找到最匹配的现有新闻
        
        Args:
            news_item: 待匹配的新闻项
            existing_news: 现有新闻列表
            
        Returns:
            最匹配的新闻项，如果没有则返回 None
        """
        title = news_item.get("title", "")
        content = news_item.get("content", "")
        
        best_match = None
        best_score = 0.0
        
        for existing in existing_news:
            title_sim = self.calculate_title_similarity(title, existing.get("title", ""))
            content_sim = self.calculate_content_similarity(content, existing.get("content", ""))
            
            # 综合评分（标题权重更高）
            combined_score = title_sim * 0.6 + content_sim * 0.4
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = existing
        
        # 只有超过阈值才返回
        if best_score >= self.TITLE_SIMILARITY_THRESHOLD:
            return best_match
        
        return None
    
    def add_to_cache(self, news_id: str, news_data: Dict[str, Any]) -> None:
        """
        添加新闻到缓存
        
        Args:
            news_id: 新闻 ID
            news_data: 新闻数据
        """
        self._news_cache[news_id] = news_data
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._news_cache.clear()
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self._news_cache)
