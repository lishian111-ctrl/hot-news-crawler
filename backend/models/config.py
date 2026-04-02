"""
配置模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import relationship

from .base import Base


class Config(Base):
    """配置表"""
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 ID")
    key = Column(String(100), nullable=False, unique=True, comment="配置键")
    value = Column(Text, comment="配置值")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 索引
    __table_args__ = (
        Index("idx_config_key", "key"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Config(id={self.id}, key='{self.key}', value='{self.value}')>"
