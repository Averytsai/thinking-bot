"""
問題分類資料模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class PromptCategory(Base):
    """問題分類資料模型"""
    __tablename__ = "prompt_categories"
    
    # 主鍵
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 分類資訊
    category_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    example = Column(Text, nullable=True)
    prompt_template = Column(Text, nullable=False)
    
    # 狀態
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 關聯關係
    conversations = relationship("Conversation", back_populates="prompt_category")
    
    def __repr__(self):
        return f"<PromptCategory(id={self.id}, category_key='{self.category_key}', name='{self.name}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "category_key": self.category_key,
            "name": self.name,
            "description": self.description,
            "example": self.example,
            "prompt_template": self.prompt_template,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_categories(cls, db_session):
        """獲取所有啟用的分類"""
        return db_session.query(cls).filter(cls.is_active == True).all()
    
    @classmethod
    def get_by_key(cls, db_session, category_key: str):
        """根據分類鍵值獲取分類"""
        return db_session.query(cls).filter(cls.category_key == category_key, cls.is_active == True).first()
