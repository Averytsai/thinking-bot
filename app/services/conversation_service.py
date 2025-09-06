"""
對話管理服務
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import User, Conversation, Message, PromptCategory
from app.core.exceptions import (
    ConversationServiceError,
    ConversationNotFoundError,
    UserNotFoundError,
    DatabaseError
)


class ConversationService:
    """對話管理服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_user(self, line_user_id: str, display_name: str) -> User:
        """創建新用戶"""
        try:
            # 檢查用戶是否已存在
            existing_user = User.get_by_line_user_id(self.db_session, line_user_id)
            if existing_user:
                return existing_user
            
            # 創建新用戶
            user = User(
                line_user_id=line_user_id,
                display_name=display_name
            )
            
            self.db_session.add(user)
            self.db_session.commit()
            
            return user
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"創建用戶失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"創建用戶失敗: {e}")
    
    def get_user_by_line_id(self, line_user_id: str) -> Optional[User]:
        """根據LINE用戶ID獲取用戶"""
        try:
            return User.get_by_line_user_id(self.db_session, line_user_id)
        except Exception as e:
            raise DatabaseError(f"獲取用戶失敗: {e}")
    
    def create_conversation(
        self, 
        user_id: str, 
        category_key: Optional[str] = None,
        ai_model: str = "chatgpt"
    ) -> Conversation:
        """創建新對話"""
        try:
            # 檢查用戶是否存在
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(f"找不到用戶 ID: {user_id}")
            
            # 創建新對話
            conversation = Conversation(
                user_id=user_id,
                category_key=category_key,
                ai_model=ai_model,
                status="active",
                state="initial"
            )
            
            self.db_session.add(conversation)
            self.db_session.commit()
            
            return conversation
            
        except UserNotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"創建對話失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"創建對話失敗: {e}")
    
    def get_active_conversation(self, user_id: str) -> Optional[Conversation]:
        """獲取用戶的活躍對話"""
        try:
            return Conversation.get_active_conversation(self.db_session, user_id)
        except Exception as e:
            raise DatabaseError(f"獲取活躍對話失敗: {e}")
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """根據ID獲取對話"""
        try:
            return self.db_session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
        except Exception as e:
            raise DatabaseError(f"獲取對話失敗: {e}")
    
    def get_user_conversations(
        self, 
        user_id: str, 
        limit: int = 10,
        offset: int = 0
    ) -> List[Conversation]:
        """獲取用戶的對話列表"""
        try:
            return Conversation.get_conversations_by_user(
                self.db_session, user_id, limit
            )
        except Exception as e:
            raise DatabaseError(f"獲取用戶對話列表失敗: {e}")
    
    def add_message(
        self,
        conversation_id: str,
        message_type: str,
        content: str,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> Message:
        """添加訊息到對話"""
        try:
            # 檢查對話是否存在
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                raise ConversationNotFoundError(f"找不到對話 ID: {conversation_id}")
            
            # 創建訊息
            message = Message(
                conversation_id=conversation_id,
                message_type=message_type,
                content=content,
                tokens_used=tokens_used,
                processing_time_ms=processing_time_ms
            )
            
            self.db_session.add(message)
            
            # 更新對話統計
            conversation.message_count += 1
            if tokens_used:
                conversation.total_tokens += tokens_used
            conversation.last_activity_at = datetime.utcnow()
            
            self.db_session.commit()
            
            return message
            
        except ConversationNotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"添加訊息失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"添加訊息失敗: {e}")
    
    def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """獲取對話的訊息列表"""
        try:
            return Message.get_conversation_messages(
                self.db_session, conversation_id, limit
            )
        except Exception as e:
            raise DatabaseError(f"獲取對話訊息失敗: {e}")
    
    def get_recent_messages(
        self, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[Message]:
        """獲取對話的最近訊息"""
        try:
            return Message.get_recent_messages(
                self.db_session, conversation_id, limit
            )
        except Exception as e:
            raise DatabaseError(f"獲取最近訊息失敗: {e}")
    
    def update_conversation_state(
        self, 
        conversation_id: str, 
        state: str
    ) -> bool:
        """更新對話狀態"""
        try:
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                return False
            
            conversation.state = state
            conversation.last_activity_at = datetime.utcnow()
            self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"更新對話狀態失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"更新對話狀態失敗: {e}")
    
    def update_conversation_status(
        self, 
        conversation_id: str, 
        status: str
    ) -> bool:
        """更新對話狀態"""
        try:
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                return False
            
            conversation.status = status
            conversation.last_activity_at = datetime.utcnow()
            self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"更新對話狀態失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"更新對話狀態失敗: {e}")
    
    def expire_inactive_conversations(self, inactivity_minutes: int = 30) -> int:
        """過期不活躍的對話"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=inactivity_minutes)
            
            # 查找不活躍的對話
            inactive_conversations = self.db_session.query(Conversation).filter(
                Conversation.status == "active",
                Conversation.last_activity_at < cutoff_time
            ).all()
            
            expired_count = 0
            for conversation in inactive_conversations:
                conversation.status = "expired"
                expired_count += 1
            
            self.db_session.commit()
            
            return expired_count
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"過期不活躍對話失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"過期不活躍對話失敗: {e}")
    
    def reset_conversation(self, conversation_id: str) -> bool:
        """重置對話"""
        try:
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                return False
            
            # 更新對話狀態
            conversation.status = "reset"
            conversation.state = "initial"
            conversation.category_key = None
            conversation.selected_category_id = None
            conversation.last_activity_at = datetime.utcnow()
            
            self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"重置對話失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"重置對話失敗: {e}")
    
    def get_conversation_statistics(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶的對話統計"""
        try:
            conversations = self.get_user_conversations(user_id, limit=1000)
            
            stats = {
                "total_conversations": len(conversations),
                "active_conversations": 0,
                "expired_conversations": 0,
                "reset_conversations": 0,
                "total_messages": 0,
                "total_tokens": 0,
                "by_category": {},
                "by_model": {}
            }
            
            for conversation in conversations:
                # 按狀態統計
                if conversation.status == "active":
                    stats["active_conversations"] += 1
                elif conversation.status == "expired":
                    stats["expired_conversations"] += 1
                elif conversation.status == "reset":
                    stats["reset_conversations"] += 1
                
                # 累計訊息和token
                stats["total_messages"] += conversation.message_count
                stats["total_tokens"] += conversation.total_tokens
                
                # 按分類統計
                if conversation.category_key:
                    if conversation.category_key not in stats["by_category"]:
                        stats["by_category"][conversation.category_key] = 0
                    stats["by_category"][conversation.category_key] += 1
                
                # 按模型統計
                if conversation.ai_model not in stats["by_model"]:
                    stats["by_model"][conversation.ai_model] = 0
                stats["by_model"][conversation.ai_model] += 1
            
            return stats
            
        except Exception as e:
            raise DatabaseError(f"獲取對話統計失敗: {e}")
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """獲取對話摘要"""
        try:
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                return {}
            
            # 獲取用戶資訊
            user = self.db_session.query(User).filter(
                User.id == conversation.user_id
            ).first()
            
            # 獲取分類資訊
            category = None
            if conversation.category_key:
                category = self.db_session.query(PromptCategory).filter(
                    PromptCategory.category_key == conversation.category_key
                ).first()
            
            summary = {
                "conversation_id": conversation.id,
                "user": {
                    "id": user.id if user else None,
                    "line_user_id": user.line_user_id if user else None,
                    "display_name": user.display_name if user else None
                },
                "category": {
                    "key": conversation.category_key,
                    "name": category.name if category else None,
                    "description": category.description if category else None
                },
                "ai_model": conversation.ai_model,
                "status": conversation.status,
                "state": conversation.state,
                "message_count": conversation.message_count,
                "total_tokens": conversation.total_tokens,
                "created_at": conversation.created_at,
                "last_activity_at": conversation.last_activity_at
            }
            
            return summary
            
        except Exception as e:
            raise DatabaseError(f"獲取對話摘要失敗: {e}")
    
    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """清理舊對話（僅標記為已刪除，不實際刪除）"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_old)
            
            # 查找舊的過期對話
            old_conversations = self.db_session.query(Conversation).filter(
                Conversation.status == "expired",
                Conversation.last_activity_at < cutoff_time
            ).all()
            
            cleaned_count = 0
            for conversation in old_conversations:
                conversation.status = "archived"
                cleaned_count += 1
            
            self.db_session.commit()
            
            return cleaned_count
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"清理舊對話失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise ConversationServiceError(f"清理舊對話失敗: {e}")
