"""
Prompt管理服務
"""
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import PromptCategory, Conversation, Message, User
from app.prompts.manager import PromptManager
from app.core.exceptions import (
    PromptServiceError,
    CategoryNotFoundError,
    InvalidCategorySelectionError,
    DatabaseError
)


class PromptService:
    """Prompt管理服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.prompt_manager = PromptManager(db_session)
    
    def get_category_menu(self) -> str:
        """獲取問題分類選單"""
        try:
            return self.prompt_manager.get_category_menu()
        except Exception as e:
            raise PromptServiceError(f"獲取分類選單失敗: {e}")
    
    def validate_category_selection(self, user_input: str) -> Optional[Dict[str, Any]]:
        """驗證用戶的分類選擇"""
        try:
            return self.prompt_manager.validate_category_selection(user_input)
        except Exception as e:
            raise InvalidCategorySelectionError(f"分類選擇驗證失敗: {e}")
    
    def get_category_confirmation(self, category: Dict[str, Any]) -> str:
        """獲取分類確認訊息"""
        try:
            return self.prompt_manager.get_category_confirmation(category)
        except Exception as e:
            raise PromptServiceError(f"獲取分類確認訊息失敗: {e}")
    
    def get_prompt_template(self, category_key: str) -> str:
        """獲取指定分類的Prompt模板"""
        try:
            template = self.prompt_manager.get_prompt_template(category_key)
            if not template:
                raise CategoryNotFoundError(f"找不到分類 '{category_key}' 的Prompt模板")
            return template
        except CategoryNotFoundError:
            raise
        except Exception as e:
            raise PromptServiceError(f"獲取Prompt模板失敗: {e}")
    
    def get_category_from_db(self, category_key: str) -> Optional[PromptCategory]:
        """從資料庫獲取問題分類"""
        try:
            return self.prompt_manager.get_category_from_db(category_key)
        except Exception as e:
            raise DatabaseError(f"從資料庫獲取分類失敗: {e}")
    
    def get_all_categories_from_db(self) -> List[PromptCategory]:
        """從資料庫獲取所有啟用的問題分類"""
        try:
            return self.prompt_manager.get_all_categories_from_db()
        except Exception as e:
            raise DatabaseError(f"從資料庫獲取所有分類失敗: {e}")
    
    def sync_categories_to_db(self) -> bool:
        """將分類定義同步到資料庫"""
        try:
            return self.prompt_manager.sync_categories_to_db()
        except Exception as e:
            raise DatabaseError(f"同步分類到資料庫失敗: {e}")
    
    def is_reset_keyword(self, text: str) -> bool:
        """檢查是否為重置關鍵詞"""
        try:
            return self.prompt_manager.is_reset_keyword(text)
        except Exception as e:
            raise PromptServiceError(f"重置關鍵詞檢查失敗: {e}")
    
    def is_confirm_keyword(self, text: str) -> Optional[str]:
        """檢查是否為確認關鍵詞"""
        try:
            return self.prompt_manager.is_confirm_keyword(text)
        except Exception as e:
            raise PromptServiceError(f"確認關鍵詞檢查失敗: {e}")
    
    def format_conversation_start(self, category_key: str) -> str:
        """格式化對話開始訊息"""
        try:
            return self.prompt_manager.format_conversation_start(category_key)
        except Exception as e:
            raise PromptServiceError(f"格式化對話開始訊息失敗: {e}")
    
    def get_reset_message(self) -> str:
        """獲取重置訊息"""
        try:
            return self.prompt_manager.get_reset_message()
        except Exception as e:
            raise PromptServiceError(f"獲取重置訊息失敗: {e}")
    
    def get_invalid_selection_message(self) -> str:
        """獲取無效選擇訊息"""
        try:
            return self.prompt_manager.get_invalid_selection_message()
        except Exception as e:
            raise PromptServiceError(f"獲取無效選擇訊息失敗: {e}")
    
    def get_invalid_confirmation_message(self) -> str:
        """獲取無效確認訊息"""
        try:
            return self.prompt_manager.get_invalid_confirmation_message()
        except Exception as e:
            raise PromptServiceError(f"獲取無效確認訊息失敗: {e}")
    
    def get_category_summary(self, category_key: str) -> Optional[Dict[str, str]]:
        """獲取分類摘要資訊"""
        try:
            return self.prompt_manager.get_category_summary(category_key)
        except Exception as e:
            raise PromptServiceError(f"獲取分類摘要失敗: {e}")
    
    def create_conversation_with_category(
        self, 
        user_id: str, 
        category_key: str,
        ai_model: str = "chatgpt"
    ) -> Conversation:
        """創建帶有分類的對話"""
        try:
            # 驗證分類是否存在
            category = self.get_category_from_db(category_key)
            if not category:
                raise CategoryNotFoundError(f"找不到分類 '{category_key}'")
            
            # 創建新對話
            conversation = Conversation(
                user_id=user_id,
                category_key=category_key,
                ai_model=ai_model,
                status="active",
                state="conversation"
            )
            
            self.db_session.add(conversation)
            self.db_session.commit()
            
            return conversation
            
        except CategoryNotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"創建對話失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise PromptServiceError(f"創建對話失敗: {e}")
    
    def get_conversation_category(self, conversation_id: str) -> Optional[PromptCategory]:
        """獲取對話的分類資訊"""
        try:
            conversation = self.db_session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation or not conversation.category_key:
                return None
            
            return self.get_category_from_db(conversation.category_key)
            
        except Exception as e:
            raise DatabaseError(f"獲取對話分類失敗: {e}")
    
    def update_conversation_category(
        self, 
        conversation_id: str, 
        category_key: str
    ) -> bool:
        """更新對話的分類"""
        try:
            conversation = self.db_session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return False
            
            # 驗證新分類是否存在
            category = self.get_category_from_db(category_key)
            if not category:
                raise CategoryNotFoundError(f"找不到分類 '{category_key}'")
            
            conversation.category_key = category_key
            conversation.state = "conversation"
            self.db_session.commit()
            
            return True
            
        except CategoryNotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise DatabaseError(f"更新對話分類失敗: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise PromptServiceError(f"更新對話分類失敗: {e}")
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """獲取分類使用統計"""
        try:
            # 獲取各分類的對話數量
            category_stats = self.db_session.query(
                Conversation.category_key,
                Conversation.ai_model,
                Conversation.status
            ).all()
            
            stats = {
                "total_conversations": len(category_stats),
                "by_category": {},
                "by_model": {},
                "by_status": {}
            }
            
            for category_key, ai_model, status in category_stats:
                # 按分類統計
                if category_key:
                    if category_key not in stats["by_category"]:
                        stats["by_category"][category_key] = 0
                    stats["by_category"][category_key] += 1
                
                # 按模型統計
                if ai_model not in stats["by_model"]:
                    stats["by_model"][ai_model] = 0
                stats["by_model"][ai_model] += 1
                
                # 按狀態統計
                if status not in stats["by_status"]:
                    stats["by_status"][status] = 0
                stats["by_status"][status] += 1
            
            return stats
            
        except Exception as e:
            raise DatabaseError(f"獲取分類統計失敗: {e}")
    
    def validate_conversation_flow(
        self, 
        user_input: str, 
        current_state: str
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """驗證對話流程並返回下一步狀態"""
        try:
            # 檢查重置關鍵詞
            if self.is_reset_keyword(user_input):
                return "initial", None, self.get_reset_message()
            
            # 根據當前狀態處理
            if current_state == "initial":
                # 初始狀態，等待分類選擇
                category = self.validate_category_selection(user_input)
                if category:
                    return "category_confirmation", category["key"], self.get_category_confirmation(category)
                else:
                    return "initial", None, self.get_invalid_selection_message()
            
            elif current_state == "category_confirmation":
                # 分類確認狀態
                confirm_result = self.is_confirm_keyword(user_input)
                if confirm_result == "yes":
                    return "conversation", None, self.format_conversation_start("current_category")
                elif confirm_result == "no":
                    return "initial", None, self.get_reset_message()
                else:
                    return "category_confirmation", None, self.get_invalid_confirmation_message()
            
            elif current_state == "conversation":
                # 對話狀態，檢查是否要重置
                if self.is_reset_keyword(user_input):
                    return "initial", None, self.get_reset_message()
                else:
                    return "conversation", None, None  # 繼續對話
            
            else:
                # 未知狀態，重置到初始狀態
                return "initial", None, self.get_reset_message()
                
        except Exception as e:
            raise PromptServiceError(f"驗證對話流程失敗: {e}")
    
    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """獲取對話上下文資訊"""
        try:
            conversation = self.db_session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return {}
            
            context = {
                "conversation_id": conversation.id,
                "user_id": conversation.user_id,
                "category_key": conversation.category_key,
                "ai_model": conversation.ai_model,
                "status": conversation.status,
                "state": conversation.state,
                "message_count": conversation.message_count,
                "total_tokens": conversation.total_tokens,
                "last_activity_at": conversation.last_activity_at,
                "created_at": conversation.created_at
            }
            
            # 添加分類資訊
            if conversation.category_key:
                category = self.get_category_from_db(conversation.category_key)
                if category:
                    context["category"] = {
                        "name": category.name,
                        "description": category.description,
                        "example": category.example
                    }
            
            return context
            
        except Exception as e:
            raise DatabaseError(f"獲取對話上下文失敗: {e}")
