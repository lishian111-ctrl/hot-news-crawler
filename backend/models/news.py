"""
新闻模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Index, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class News(Base):
    """新闻表"""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    title = Column(String(500), nullable=False, comment="新闻标题")
    content = Column(Text, comment="新闻内容")
    summary = Column(Text, comment="新闻摘要")
    source_url = Column(String(2000), nullable=False, unique=True, comment="来源 URL")
    source_id = Column(Integer, ForeignKey("source.id"), nullable=True, comment="信源 ID")
    category = Column(String(100), comment="分类")
    publish_time = Column(DateTime, comment="发布时间")
    score = Column(Integer, default=0, comment="评分")
    content_hash = Column(String(64), nullable=False, index=True, comment="内容哈希值（用于去重）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    source = relationship("Source", back_populates="news", foreign_keys=[source_id])
    favorite = relationship("Favorite", back_populates="news", uselist=False)

    # 索引
    __table_args__ = (
        Index("idx_news_category", "category"),
        Index("idx_news_publish_time", "publish_time"),
        Index("idx_news_source_id", "source_id"),
        Index("idx_news_score", "score"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "category": self.category,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "score": self.score,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<News(id={self.id}, title='{self.title}', source_id={self.source_id})>"
