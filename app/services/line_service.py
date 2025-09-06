"""
LINE服務整合器
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.adapters.line_adapter import LineAdapter
from app.services.ai_manager import AIManager
from app.services.conversation_service import ConversationService
from app.core.exceptions import AIServiceException, DatabaseError


class LineService:
    """LINE服務整合器"""
    
    def __init__(self, db_session: Session, line_config: Dict[str, Any], ai_manager: AIManager):
        self.db_session = db_session
        self.line_adapter = LineAdapter(line_config)
        self.ai_manager = ai_manager
        self.conversation_service = ConversationService(db_session)
    
    async def handle_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理LINE webhook請求"""
        try:
            events = request_data.get("events", [])
            responses = []
            
            for event in events:
                event_type = event.get("type")
                user_id = event.get("source", {}).get("userId")
                
                if event_type == "follow" and user_id:
                    # 處理加好友事件 - 發送歡迎訊息
                    response = await self._process_follow_event(user_id, event)
                    responses.append(response)
                elif event_type == "message" and event.get("message", {}).get("type") == "text":
                    # 處理文字訊息
                    message_text = event.get("message", {}).get("text", "")
                    
                    if user_id and message_text:
                        response = await self._process_message(user_id, message_text, event)
                        responses.append(response)
            
            return self.line_adapter.create_success_response(f"處理了 {len(responses)} 個事件")
            
        except Exception as e:
            print(f"處理LINE webhook失敗: {e}")
            return self.line_adapter.create_error_response(str(e))
    
    async def _process_follow_event(self, user_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理加好友事件"""
        try:
            # 獲取或創建用戶
            user = await self._get_or_create_user(user_id, event_data)
            if not user:
                await self.line_adapter.send_error_message(user_id, "無法創建用戶，請稍後再試。")
                return {"status": "error", "message": "無法創建用戶"}
            
            # 發送歡迎訊息
            success = await self.line_adapter.send_category_menu(user_id)
            
            if success:
                return {
                    "user_id": user_id,
                    "status": "success",
                    "message": "歡迎訊息已發送",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "user_id": user_id,
                    "status": "error",
                    "message": "發送歡迎訊息失敗",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            print(f"處理加好友事件失敗: {e}")
            await self.line_adapter.send_error_message(user_id, "歡迎訊息發送失敗，請稍後再試。")
            return {"status": "error", "message": str(e)}
    
    async def _process_message(self, user_id: str, message_text: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理用戶訊息"""
        try:
            # 獲取或創建用戶
            user = await self._get_or_create_user(user_id, event_data)
            if not user:
                await self.line_adapter.send_error_message(user_id, "無法創建用戶，請稍後再試。")
                return {"status": "error", "message": "無法創建用戶"}
            
            # 處理訊息
            ai_response, conversation_id, usage_info = self.ai_manager.process_user_message(
                user_id=str(user.id),
                user_message=message_text
            )
            
            # 發送AI回應
            success = await self.line_adapter.send_message(user_id, ai_response)
            
            if success:
                return {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "status": "success",
                    "usage_info": usage_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "user_id": user_id,
                    "status": "error",
                    "message": "發送回應失敗",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except AIServiceException as e:
            print(f"AI服務錯誤: {e}")
            await self.line_adapter.send_error_message(user_id, "AI服務暫時無法使用，請稍後再試。")
            return {"status": "error", "message": str(e)}
        except DatabaseError as e:
            print(f"資料庫錯誤: {e}")
            await self.line_adapter.send_error_message(user_id, "系統暫時無法使用，請稍後再試。")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"處理訊息失敗: {e}")
            await self.line_adapter.send_error_message(user_id)
            return {"status": "error", "message": str(e)}
    
    async def _get_or_create_user(self, line_user_id: str, event_data: Dict[str, Any]) -> Optional[Any]:
        """獲取或創建用戶"""
        try:
            # 檢查用戶是否已存在
            user = self.conversation_service.get_user_by_line_id(line_user_id)
            if user:
                return user
            
            # 獲取用戶資料
            try:
                profile = await self.line_adapter.get_user_profile(line_user_id)
                display_name = profile.get("display_name", "LINE用戶")
            except Exception:
                display_name = "LINE用戶"
            
            # 創建新用戶
            user = self.conversation_service.create_user(line_user_id, display_name)
            return user
            
        except Exception as e:
            print(f"獲取或創建用戶失敗: {e}")
            return None
    
    async def send_welcome_message(self, user_id: str) -> bool:
        """發送歡迎訊息"""
        try:
            return await self.line_adapter.send_category_menu(user_id)
        except Exception as e:
            print(f"發送歡迎訊息失敗: {e}")
            return False
    
    async def send_category_menu(self, user_id: str) -> bool:
        """發送問題分類選單"""
        try:
            return await self.line_adapter.send_category_menu(user_id)
        except Exception as e:
            print(f"發送分類選單失敗: {e}")
            return False
    
    async def send_reset_message(self, user_id: str) -> bool:
        """發送重置訊息"""
        try:
            return await self.line_adapter.send_reset_message(user_id)
        except Exception as e:
            print(f"發送重置訊息失敗: {e}")
            return False
    
    async def send_error_message(self, user_id: str, error_message: str = None) -> bool:
        """發送錯誤訊息"""
        try:
            return await self.line_adapter.send_error_message(user_id, error_message)
        except Exception as e:
            print(f"發送錯誤訊息失敗: {e}")
            return False
    
    async def verify_signature(self, signature: str, body: str) -> bool:
        """驗證LINE請求簽名"""
        try:
            return await self.line_adapter.verify_signature(signature, body)
        except Exception as e:
            print(f"驗證簽名失敗: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            line_health = await self.line_adapter.health_check()
            ai_health = self.ai_manager.check_ai_service_health()
            
            return {
                "line_adapter": line_health,
                "ai_service": ai_health,
                "overall_status": "healthy" if line_health["status"] == "healthy" else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_user_statistics(self, line_user_id: str) -> Dict[str, Any]:
        """獲取用戶統計"""
        try:
            user = self.conversation_service.get_user_by_line_id(line_user_id)
            if not user:
                return {"error": "用戶不存在"}
            
            stats = self.ai_manager.get_usage_statistics(str(user.id))
            return stats
            
        except Exception as e:
            print(f"獲取用戶統計失敗: {e}")
            return {"error": str(e)}
    
    async def send_user_statistics(self, line_user_id: str) -> bool:
        """發送用戶統計給用戶"""
        try:
            stats = await self.get_user_statistics(line_user_id)
            
            if "error" in stats:
                await self.line_adapter.send_error_message(line_user_id, "無法獲取統計資料")
                return False
            
            # 格式化統計訊息
            stats_message = f"""📊 你的使用統計：

💬 總對話數：{stats.get('total_conversations', 0)}
📝 總訊息數：{stats.get('total_messages', 0)}
🎯 總Token數：{stats.get('total_tokens', 0)}
💰 估算成本：${stats.get('estimated_total_cost_usd', 0):.4f}

📈 活躍對話：{stats.get('active_conversations', 0)}
⏰ 已過期對話：{stats.get('expired_conversations', 0)}
🔄 已重置對話：{stats.get('reset_conversations', 0)}"""
            
            return await self.line_adapter.send_message(line_user_id, stats_message)
            
        except Exception as e:
            print(f"發送用戶統計失敗: {e}")
            return False
    
    async def send_conversation_summary(self, line_user_id: str) -> bool:
        """發送對話總結"""
        try:
            user = self.conversation_service.get_user_by_line_id(line_user_id)
            if not user:
                await self.line_adapter.send_error_message(line_user_id, "用戶不存在")
                return False
            
            # 獲取活躍對話
            conversation = self.conversation_service.get_active_conversation(str(user.id))
            if not conversation:
                await self.line_adapter.send_message(line_user_id, "目前沒有活躍的對話")
                return True
            
            # 生成對話總結
            summary, usage_info = self.ai_manager.get_conversation_summary(str(conversation.id))
            
            # 發送總結
            summary_message = f"📋 對話總結：\n\n{summary}"
            return await self.line_adapter.send_message(line_user_id, summary_message)
            
        except Exception as e:
            print(f"發送對話總結失敗: {e}")
            return False
