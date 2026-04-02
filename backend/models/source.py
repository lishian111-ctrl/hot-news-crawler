"""
信源模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship

from .base import Base


class Source(Base):
    """信源表"""
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    name = Column(String(200), nullable=False, comment="信源名称")
    url = Column(String(2000), nullable=False, comment="信源 URL")
    category = Column(String(100), comment="分类")
    weight = Column(Integer, default=1, comment="权重（数值越大优先级越高）")
    board = Column(String(100), comment="板块")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    news = relationship("News", back_populates="source")

    # 索引
    __table_args__ = (
        Index("idx_source_category", "category"),
        Index("idx_source_board", "board"),
        Index("idx_source_weight", "weight"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "category": self.category,
            "weight": self.weight,
            "board": self.board,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name='{self.name}', category='{self.category}')>"
