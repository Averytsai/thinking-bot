"""
訊息資料模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Message(Base):
    """訊息資料模型"""
    __tablename__ = "messages"
    
    # 主鍵
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 外鍵關聯
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 訊息內容
    message_type = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # AI相關資訊
    tokens_used = Column(Integer, nullable=True, index=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    # 關聯關係
    conversation = relationship("Conversation", back_populates="messages")
    
    # 約束條件
    __table_args__ = (
        CheckConstraint("message_type IN ('user', 'assistant')", name="check_message_type"),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, type='{self.message_type}', content='{self.content[:50]}...')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "message_type": self.message_type,
            "content": self.content,
            "tokens_used": self.tokens_used,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_user_message(cls, conversation_id: str, content: str, processing_time_ms: Optional[int] = None):
        """創建用戶訊息"""
        return cls(
            conversation_id=conversation_id,
            message_type="user",
            content=content,
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def create_assistant_message(cls, conversation_id: str, content: str, tokens_used: Optional[int] = None, processing_time_ms: Optional[int] = None):
        """創建AI助手訊息"""
        return cls(
            conversation_id=conversation_id,
            message_type="assistant",
            content=content,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def get_conversation_messages(cls, db_session, conversation_id: str, limit: Optional[int] = None):
        """獲取會話的所有訊息"""
        query = db_session.query(cls).filter(cls.conversation_id == conversation_id).order_by(cls.created_at.asc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_recent_messages(cls, db_session, conversation_id: str, limit: int = 10):
        """獲取會話的最近訊息"""
        return db_session.query(cls).filter(
            cls.conversation_id == conversation_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
