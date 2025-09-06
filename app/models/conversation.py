"""
會話資料模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Conversation(Base):
    """會話資料模型"""
    __tablename__ = "conversations"
    
    # 主鍵
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 外鍵關聯
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_category_id = Column(UUID(as_uuid=True), ForeignKey("prompt_categories.id"), nullable=True)
    
    # 會話狀態
    status = Column(String(20), default="active", nullable=False, index=True)
    state = Column(String(50), default="initial", nullable=False, index=True)
    
    # 分類資訊
    category_key = Column(String(100), nullable=True, index=True)
    
    # AI模型資訊
    ai_model = Column(String(50), default="chatgpt", nullable=False)
    
    # 統計資訊
    message_count = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # 時間戳
    last_activity_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 關聯關係
    user = relationship("User", back_populates="conversations")
    prompt_category = relationship("PromptCategory", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, state='{self.state}', category_key='{self.category_key}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "selected_category_id": str(self.selected_category_id) if self.selected_category_id else None,
            "status": self.status,
            "state": self.state,
            "category_key": self.category_key,
            "ai_model": self.ai_model,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_activity(self):
        """更新最後活動時間"""
        self.last_activity_at = func.now()
    
    def increment_message_count(self):
        """增加訊息計數"""
        self.message_count += 1
    
    def add_tokens(self, tokens: int):
        """增加token使用量"""
        self.total_tokens += tokens
    
    def reset_conversation(self):
        """重置會話"""
        self.state = "reset"
        self.category_key = None
        self.selected_category_id = None
        self.message_count = 0
        self.total_tokens = 0
    
    def expire_conversation(self):
        """過期會話"""
        self.status = "expired"
    
    @classmethod
    def get_active_conversation(cls, db_session, user_id: str):
        """獲取用戶的活躍會話"""
        return db_session.query(cls).filter(
            cls.user_id == user_id,
            cls.status == "active"
        ).order_by(cls.last_activity_at.desc()).first()
    
    @classmethod
    def get_conversations_by_user(cls, db_session, user_id: str, limit: int = 10):
        """獲取用戶的會話歷史"""
        return db_session.query(cls).filter(
            cls.user_id == user_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
