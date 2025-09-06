"""
基礎通訊平台適配器
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseAdapter(ABC):
    """基礎通訊平台適配器抽象類別"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform_name = self.__class__.__name__.replace("Adapter", "").lower()
    
    @abstractmethod
    async def send_message(self, user_id: str, message: str, **kwargs) -> bool:
        """發送訊息給用戶"""
        pass
    
    @abstractmethod
    async def send_text_message(self, user_id: str, text: str) -> bool:
        """發送文字訊息"""
        pass
    
    @abstractmethod
    async def send_quick_reply(self, user_id: str, text: str, options: List[Dict[str, str]]) -> bool:
        """發送快速回覆選項"""
        pass
    
    @abstractmethod
    async def send_template_message(self, user_id: str, template: Dict[str, Any]) -> bool:
        """發送模板訊息"""
        pass
    
    @abstractmethod
    async def handle_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理webhook請求"""
        pass
    
    @abstractmethod
    async def verify_signature(self, signature: str, body: str) -> bool:
        """驗證請求簽名"""
        pass
    
    @abstractmethod
    async def extract_user_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """從事件中提取用戶資訊"""
        pass
    
    @abstractmethod
    async def extract_message_content(self, event_data: Dict[str, Any]) -> str:
        """從事件中提取訊息內容"""
        pass
    
    def get_platform_name(self) -> str:
        """獲取平台名稱"""
        return self.platform_name
    
    def get_config(self) -> Dict[str, Any]:
        """獲取配置資訊"""
        return self.config
    
    def format_message_for_logging(self, message: str, user_id: str) -> str:
        """格式化訊息用於日誌記錄"""
        return f"[{self.platform_name.upper()}] {user_id}: {message[:100]}{'...' if len(message) > 100 else ''}"
    
    def create_error_response(self, error_message: str) -> Dict[str, Any]:
        """創建錯誤回應"""
        return {
            "status": "error",
            "platform": self.platform_name,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_success_response(self, message: str = "success") -> Dict[str, Any]:
        """創建成功回應"""
        return {
            "status": "success",
            "platform": self.platform_name,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return {
            "platform": self.platform_name,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
