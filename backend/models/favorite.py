"""
收藏模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import Base


class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, unique=True, comment="新闻 ID")
    tags = Column(Text, comment="标签（JSON 格式）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="收藏时间")

    # 关联关系
    news = relationship("News", back_populates="favorite")

    # 索引
    __table_args__ = (
        Index("idx_favorite_news_id", "news_id"),
        Index("idx_favorite_created_at", "created_at"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "news_id": self.news_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, news_id={self.news_id})>"
