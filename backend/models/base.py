"""
共享的 Base 模型类
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """所有模型的基类"""
    pass
