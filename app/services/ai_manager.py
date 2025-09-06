"""
AI服務管理器
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import Settings
from app.core.exceptions import AIServiceException, DatabaseError
from app.services.ai_service import AIService
from app.services.conversation_service import ConversationService
from app.services.prompt_service import PromptService
from app.models import Message, Conversation


class AIManager:
    """AI服務管理器"""
    
    def __init__(self, db_session: Session, settings: Settings):
        self.db_session = db_session
        self.settings = settings
        self.ai_service = AIService(settings)
        self.conversation_service = ConversationService(db_session)
        self.prompt_service = PromptService(db_session)
    
    def process_user_message(
        self,
        user_id: str,
        user_message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """處理用戶訊息並生成回應"""
        try:
            # 獲取或創建對話
            if conversation_id:
                conversation = self.conversation_service.get_conversation_by_id(conversation_id)
                if not conversation:
                    raise AIServiceException(f"找不到對話 ID: {conversation_id}")
            else:
                conversation = self.conversation_service.get_active_conversation(user_id)
                if not conversation:
                    # 創建新對話
                    conversation = self.conversation_service.create_conversation(user_id)
            
            # 添加用戶訊息
            user_msg = self.conversation_service.add_message(
                conversation_id=conversation.id,
                message_type="user",
                content=user_message
            )
            
            # 獲取對話歷史
            conversation_history = self.conversation_service.get_conversation_messages(
                conversation.id, limit=20
            )
            
            # 生成AI回應
            ai_response, usage_info = self._generate_ai_response(
                conversation=conversation,
                user_message=user_message,
                conversation_history=conversation_history,
                model=model
            )
            
            # 添加AI回應
            ai_msg = self.conversation_service.add_message(
                conversation_id=conversation.id,
                message_type="assistant",
                content=ai_response,
                tokens_used=usage_info.get("total_tokens"),
                processing_time_ms=usage_info.get("processing_time_ms")
            )
            
            # 更新對話統計
            self._update_conversation_stats(conversation, usage_info)
            
            return ai_response, str(conversation.id), usage_info
            
        except Exception as e:
            raise AIServiceException(f"處理用戶訊息失敗: {e}")
    
    def _generate_ai_response(
        self,
        conversation: Conversation,
        user_message: str,
        conversation_history: List[Message],
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成AI回應"""
        try:
            # 檢查是否為重置關鍵詞
            if self.prompt_service.is_reset_keyword(user_message):
                self.conversation_service.reset_conversation(conversation.id)
                # 重新獲取對話以更新狀態
                conversation = self.conversation_service.get_conversation_by_id(conversation.id)
                return self.prompt_service.get_reset_message(), {}
            
            # 根據對話狀態處理
            if conversation.state == "initial":
                return self._handle_initial_state(conversation, user_message, model)
            elif conversation.state == "category_confirmation":
                return self._handle_category_confirmation(conversation, user_message, model)
            elif conversation.state == "conversation":
                return self._handle_conversation_state(
                    conversation, user_message, conversation_history, model
                )
            else:
                return self._handle_unknown_state(conversation, user_message, model)
                
        except Exception as e:
            raise AIServiceException(f"生成AI回應失敗: {e}")
    
    def _handle_initial_state(
        self,
        conversation: Conversation,
        user_message: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """處理初始狀態"""
        # 驗證分類選擇
        category = self.prompt_service.validate_category_selection(user_message)
        if category:
            # 更新對話狀態
            self.conversation_service.update_conversation_state(
                conversation.id, "category_confirmation"
            )
            conversation.category_key = category["key"]
            self.db_session.commit()
            
            return self.prompt_service.get_category_confirmation(category), {}
        else:
            return self.prompt_service.get_invalid_selection_message(), {}
    
    def _handle_category_confirmation(
        self,
        conversation: Conversation,
        user_message: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """處理分類確認狀態"""
        confirm_result = self.prompt_service.is_confirm_keyword(user_message)
        
        if confirm_result == "yes":
            # 確認分類，開始對話
            self.conversation_service.update_conversation_state(
                conversation.id, "conversation"
            )
            
            # 生成初始回應
            category = self.prompt_service.get_category_from_db(conversation.category_key)
            if category:
                return self.ai_service.generate_initial_response(
                    category_name=category.name,
                    category_description=category.description,
                    model=model
                )
            else:
                return "好的，讓我們開始對話吧！", {}
                
        elif confirm_result == "no":
            # 拒絕分類，回到初始狀態
            self.conversation_service.update_conversation_state(
                conversation.id, "initial"
            )
            conversation.category_key = None
            self.db_session.commit()
            
            return self.prompt_service.get_reset_message(), {}
        else:
            return self.prompt_service.get_invalid_confirmation_message(), {}
    
    def _handle_conversation_state(
        self,
        conversation: Conversation,
        user_message: str,
        conversation_history: List[Message],
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """處理對話狀態"""
        # 檢查是否為重置關鍵詞
        if self.prompt_service.is_reset_keyword(user_message):
            self.conversation_service.reset_conversation(conversation.id)
            return self.prompt_service.get_reset_message(), {}
        
        # 獲取分類的Prompt模板
        if conversation.category_key:
            category = self.prompt_service.get_category_from_db(conversation.category_key)
            if category:
                return self.ai_service.generate_category_response(
                    user_message=user_message,
                    category_prompt=category.prompt_template,
                    conversation_history=conversation_history,
                    model=model,
                    conversation_id=str(conversation.id)
                )
        
        # 如果沒有分類，使用通用回應
        return self.ai_service.generate_conversation_response(
            user_message=user_message,
            conversation_history=conversation_history,
            system_prompt="你是一個友善的AI助手，請根據用戶的問題提供有用的建議。",
            model=model,
            conversation_id=str(conversation.id)
        )
    
    def _handle_unknown_state(
        self,
        conversation: Conversation,
        user_message: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """處理未知狀態"""
        # 重置到初始狀態
        self.conversation_service.update_conversation_state(
            conversation.id, "initial"
        )
        return self.prompt_service.get_reset_message(), {}
    
    def _update_conversation_stats(
        self,
        conversation: Conversation,
        usage_info: Dict[str, Any]
    ):
        """更新對話統計"""
        try:
            if usage_info.get("total_tokens"):
                conversation.total_tokens += usage_info["total_tokens"]
            
            conversation.last_activity_at = datetime.utcnow()
            self.db_session.commit()
            
        except Exception as e:
            # 統計更新失敗不影響主要功能
            print(f"更新對話統計失敗: {e}")
    
    def get_conversation_summary(
        self,
        conversation_id: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """獲取對話總結"""
        try:
            conversation = self.conversation_service.get_conversation_by_id(conversation_id)
            if not conversation:
                raise AIServiceException(f"找不到對話 ID: {conversation_id}")
            
            # 獲取對話歷史
            conversation_history = self.conversation_service.get_conversation_messages(
                conversation_id, limit=50
            )
            
            # 生成總結
            summary, usage_info = self.ai_service.generate_summary_response(
                conversation_history=conversation_history,
                model=model
            )
            
            return summary, usage_info
            
        except Exception as e:
            raise AIServiceException(f"獲取對話總結失敗: {e}")
    
    def check_ai_service_health(self) -> Dict[str, Any]:
        """檢查AI服務健康狀態"""
        try:
            return self.ai_service.check_api_health()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_available_models(self) -> List[str]:
        """獲取可用模型列表"""
        try:
            return self.ai_service.get_available_models()
        except Exception as e:
            raise AIServiceException(f"獲取可用模型失敗: {e}")
    
    def validate_model(self, model: str) -> bool:
        """驗證模型是否可用"""
        try:
            return self.ai_service.validate_model(model)
        except Exception as e:
            raise AIServiceException(f"驗證模型失敗: {e}")
    
    def estimate_cost(
        self,
        conversation_history: List[Message],
        estimated_response_length: int = 200
    ) -> Dict[str, Any]:
        """估算對話成本"""
        try:
            # 估算輸入token
            input_tokens = 0
            for msg in conversation_history:
                input_tokens += self.ai_service.estimate_tokens(msg.content)
            
            # 估算輸出token
            output_tokens = self.ai_service.estimate_tokens("x" * estimated_response_length)
            
            # 簡單的成本估算（GPT-3.5-turbo的價格）
            input_cost = input_tokens * 0.0015 / 1000  # $0.0015 per 1K tokens
            output_cost = output_tokens * 0.002 / 1000  # $0.002 per 1K tokens
            
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "estimated_cost_usd": input_cost + output_cost,
                "model": self.settings.openai_model
            }
            
        except Exception as e:
            raise AIServiceException(f"估算成本失敗: {e}")
    
    def get_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶使用統計"""
        try:
            stats = self.conversation_service.get_conversation_statistics(user_id)
            
            # 計算總成本（簡單估算）
            total_cost = stats["total_tokens"] * 0.002 / 1000  # 假設平均價格
            
            return {
                **stats,
                "estimated_total_cost_usd": total_cost,
                "average_tokens_per_conversation": (
                    stats["total_tokens"] / stats["total_conversations"]
                    if stats["total_conversations"] > 0 else 0
                )
            }
            
        except Exception as e:
            raise AIServiceException(f"獲取使用統計失敗: {e}")
