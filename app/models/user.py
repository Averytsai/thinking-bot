"""
用戶資料模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    """用戶資料模型"""
    __tablename__ = "users"
    
    # 主鍵
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # LINE用戶資訊
    line_user_id = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 關聯關係
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, line_user_id='{self.line_user_id}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "line_user_id": self.line_user_id,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_from_line_user(cls, line_user_id: str, display_name: Optional[str] = None):
        """從LINE用戶資訊創建用戶"""
        return cls(
            line_user_id=line_user_id,
            display_name=display_name
        )
    
    @classmethod
    def get_by_line_user_id(cls, db_session, line_user_id: str):
        """根據LINE用戶ID獲取用戶"""
        return db_session.query(cls).filter(cls.line_user_id == line_user_id).first()
    
    @classmethod
    def get_by_id(cls, db_session, user_id: str):
        """根據ID獲取用戶"""
        return db_session.query(cls).filter(cls.id == user_id).first()
    
    @classmethod
    def get_all_users(cls, db_session, limit: int = 100, offset: int = 0):
        """獲取所有用戶"""
        return db_session.query(cls).offset(offset).limit(limit).all()
