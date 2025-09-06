"""
AI服務整合
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI

from app.core.config import Settings
from app.core.exceptions import AIServiceException, DatabaseError
from app.models import Message, Conversation


class AIService:
    """AI服務類別"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.default_model = settings.openai_model
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成AI回應"""
        try:
            start_time = time.time()
            
            # 使用指定的模型或預設模型
            model_name = model or self.default_model
            
            # 準備API請求參數
            request_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # 調用OpenAI API
            response = self.client.chat.completions.create(**request_params)
            
            # 計算處理時間
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # 提取回應內容
            ai_response = response.choices[0].message.content
            
            # 提取使用統計
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": model_name,
                "processing_time_ms": processing_time_ms,
                "conversation_id": conversation_id
            }
            
            return ai_response, usage_info
            
        except openai.RateLimitError as e:
            raise AIServiceException(f"API速率限制: {e}")
        except openai.APITimeoutError as e:
            raise AIServiceException(f"API超時: {e}")
        except openai.APIConnectionError as e:
            raise AIServiceException(f"API連接錯誤: {e}")
        except openai.AuthenticationError as e:
            raise AIServiceException(f"API認證錯誤: {e}")
        except openai.PermissionError as e:
            raise AIServiceException(f"API權限錯誤: {e}")
        except Exception as e:
            raise AIServiceException(f"AI服務錯誤: {e}")
    
    def generate_conversation_response(
        self,
        user_message: str,
        conversation_history: List[Message],
        system_prompt: str,
        model: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成對話回應"""
        try:
            # 構建訊息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加對話歷史
            for msg in conversation_history:
                role = "user" if msg.message_type == "user" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.content
                })
            
            # 添加當前用戶訊息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 生成回應
            return self.generate_response(
                messages=messages,
                model=model,
                conversation_id=conversation_id
            )
            
        except Exception as e:
            raise AIServiceException(f"生成對話回應失敗: {e}")
    
    def generate_category_response(
        self,
        user_message: str,
        category_prompt: str,
        conversation_history: List[Message],
        model: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成分類專用回應"""
        try:
            # 直接使用分類的prompt模板作為系統提示
            system_prompt = category_prompt
            
            return self.generate_conversation_response(
                user_message=user_message,
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                model=model,
                conversation_id=conversation_id
            )
            
        except Exception as e:
            raise AIServiceException(f"生成分類回應失敗: {e}")
    
    def generate_initial_response(
        self,
        category_name: str,
        category_description: str,
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成初始回應"""
        try:
            system_prompt = f"""你是一個專業的{category_name}顧問。

{category_description}

請用友善、專業的語氣向用戶打招呼，並詢問他們遇到的具體問題。"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "你好，我想開始對話"}
            ]
            
            return self.generate_response(
                messages=messages,
                model=model
            )
            
        except Exception as e:
            raise AIServiceException(f"生成初始回應失敗: {e}")
    
    def generate_summary_response(
        self,
        conversation_history: List[Message],
        model: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成對話總結"""
        try:
            # 構建對話內容
            conversation_text = ""
            for msg in conversation_history:
                role = "用戶" if msg.message_type == "user" else "助手"
                conversation_text += f"{role}: {msg.content}\n"
            
            system_prompt = """你是一個對話總結專家。請根據對話內容，提供一個簡潔明了的總結，包括：

1. 主要討論的問題
2. 關鍵建議和解決方案
3. 後續行動建議

請用繁體中文回應，保持專業和友善的語氣。"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請總結以下對話：\n\n{conversation_text}"}
            ]
            
            return self.generate_response(
                messages=messages,
                model=model
            )
            
        except Exception as e:
            raise AIServiceException(f"生成對話總結失敗: {e}")
    
    def validate_model(self, model: str) -> bool:
        """驗證模型是否可用"""
        try:
            # 嘗試獲取模型列表
            models = self.client.models.list()
            available_models = [model.id for model in models.data]
            return model in available_models
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """獲取可用模型列表"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if model.id.startswith('gpt')]
        except Exception as e:
            raise AIServiceException(f"獲取模型列表失敗: {e}")
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本的token數量"""
        try:
            # 簡單的token估算（實際使用時可以更精確）
            # 一般來說，1個token約等於0.75個英文單詞或2-3個中文字符
            chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
            english_chars = len(text) - chinese_chars
            
            # 估算token數量
            estimated_tokens = int(chinese_chars / 2.5 + english_chars / 4)
            return max(estimated_tokens, 1)
        except Exception:
            return len(text) // 4  # 簡單估算
    
    def check_api_health(self) -> Dict[str, Any]:
        """檢查API健康狀態"""
        try:
            start_time = time.time()
            
            # 發送簡單的測試請求
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "healthy",
                "model": self.default_model,
                "response_time_ms": response_time_ms,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_usage_statistics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """獲取使用統計（需要OpenAI Pro帳戶）"""
        try:
            # 注意：這需要OpenAI Pro帳戶才能使用
            # 在實際應用中，我們會從自己的資料庫中統計使用情況
            
            return {
                "message": "使用統計功能需要OpenAI Pro帳戶",
                "suggestion": "建議從應用程式資料庫中統計使用情況"
            }
            
        except Exception as e:
            raise AIServiceException(f"獲取使用統計失敗: {e}")
    
    def create_conversation_context(
        self,
        conversation_history: List[Message],
        max_history: int = 10
    ) -> List[Dict[str, str]]:
        """創建對話上下文"""
        try:
            # 限制歷史訊息數量
            recent_messages = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
            
            context = []
            for msg in recent_messages:
                role = "user" if msg.message_type == "user" else "assistant"
                context.append({
                    "role": role,
                    "content": msg.content
                })
            
            return context
            
        except Exception as e:
            raise AIServiceException(f"創建對話上下文失敗: {e}")
    
    def format_error_response(self, error: Exception) -> str:
        """格式化錯誤回應"""
        if isinstance(error, openai.RateLimitError):
            return "抱歉，目前服務使用量較高，請稍後再試。"
        elif isinstance(error, openai.APITimeoutError):
            return "抱歉，服務回應時間過長，請稍後再試。"
        elif isinstance(error, openai.APIConnectionError):
            return "抱歉，網路連接出現問題，請檢查網路後再試。"
        elif isinstance(error, openai.AuthenticationError):
            return "抱歉，服務認證出現問題，請聯繫管理員。"
        else:
            return "抱歉，服務暫時無法使用，請稍後再試。"
