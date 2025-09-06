"""
LINE Bot適配器
"""
import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction,
    TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, URIAction
)

from app.adapters.base_adapter import BaseAdapter
from app.core.exceptions import AIServiceException


class LineAdapter(BaseAdapter):
    """LINE Bot適配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # LINE Bot配置
        self.channel_access_token = config.get("channel_access_token")
        self.channel_secret = config.get("channel_secret")
        
        if not self.channel_access_token or not self.channel_secret:
            raise ValueError("LINE Bot需要channel_access_token和channel_secret")
        
        # 初始化LINE Bot API
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
    
    async def send_message(self, user_id: str, message: str, **kwargs) -> bool:
        """發送訊息給用戶"""
        try:
            return await self.send_text_message(user_id, message)
        except Exception as e:
            print(f"發送訊息失敗: {e}")
            return False
    
    async def send_text_message(self, user_id: str, text: str) -> bool:
        """發送文字訊息"""
        try:
            message = TextSendMessage(text=text)
            self.line_bot_api.push_message(user_id, message)
            return True
        except LineBotApiError as e:
            print(f"LINE Bot API錯誤: {e}")
            return False
        except Exception as e:
            print(f"發送文字訊息失敗: {e}")
            return False
    
    async def send_quick_reply(self, user_id: str, text: str, options: List[Dict[str, str]]) -> bool:
        """發送快速回覆選項"""
        try:
            # 創建快速回覆按鈕
            quick_reply_buttons = []
            for option in options:
                button = QuickReplyButton(
                    action=MessageAction(
                        label=option.get("label", option.get("text", "")),
                        text=option.get("text", option.get("label", ""))
                    )
                )
                quick_reply_buttons.append(button)
            
            # 創建快速回覆
            quick_reply = QuickReply(items=quick_reply_buttons)
            
            # 發送訊息
            message = TextSendMessage(text=text, quick_reply=quick_reply)
            self.line_bot_api.push_message(user_id, message)
            return True
            
        except LineBotApiError as e:
            print(f"LINE Bot API錯誤: {e}")
            return False
        except Exception as e:
            print(f"發送快速回覆失敗: {e}")
            return False
    
    async def send_template_message(self, user_id: str, template: Dict[str, Any]) -> bool:
        """發送模板訊息"""
        try:
            template_type = template.get("type", "carousel")
            
            if template_type == "carousel":
                return await self._send_carousel_template(user_id, template)
            else:
                # 預設發送文字訊息
                text = template.get("text", "模板訊息")
                return await self.send_text_message(user_id, text)
                
        except Exception as e:
            print(f"發送模板訊息失敗: {e}")
            return False
    
    async def _send_carousel_template(self, user_id: str, template: Dict[str, Any]) -> bool:
        """發送輪播模板"""
        try:
            columns = []
            for item in template.get("columns", []):
                column = CarouselColumn(
                    thumbnail_image_url=item.get("thumbnail_image_url"),
                    title=item.get("title", ""),
                    text=item.get("text", ""),
                    actions=[
                        PostbackAction(
                            label=action.get("label", ""),
                            data=action.get("data", "")
                        ) for action in item.get("actions", [])
                    ]
                )
                columns.append(column)
            
            carousel_template = CarouselTemplate(columns=columns)
            message = TemplateSendMessage(
                alt_text=template.get("alt_text", "輪播訊息"),
                template=carousel_template
            )
            
            self.line_bot_api.push_message(user_id, message)
            return True
            
        except Exception as e:
            print(f"發送輪播模板失敗: {e}")
            return False
    
    async def handle_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理webhook請求"""
        try:
            events = request_data.get("events", [])
            responses = []
            
            for event in events:
                if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
                    # 處理文字訊息
                    user_id = event.get("source", {}).get("userId")
                    message_text = event.get("message", {}).get("text", "")
                    
                    if user_id and message_text:
                        response = await self._process_text_message(user_id, message_text, event)
                        responses.append(response)
            
            return self.create_success_response(f"處理了 {len(responses)} 個事件")
            
        except Exception as e:
            print(f"處理webhook失敗: {e}")
            return self.create_error_response(str(e))
    
    async def _process_text_message(self, user_id: str, message_text: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理文字訊息"""
        try:
            # 這裡會與AI管理器整合
            # 暫時返回成功回應
            return {
                "user_id": user_id,
                "message": message_text,
                "status": "processed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"處理文字訊息失敗: {e}")
            return {
                "user_id": user_id,
                "message": message_text,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def verify_signature(self, signature: str, body: str) -> bool:
        """驗證請求簽名"""
        try:
            import base64
            
            # 手動實現LINE Bot的簽名驗證
            # 如果body是字符串，需要轉換為bytes
            if isinstance(body, str):
                body_bytes = body.encode('utf-8')
            else:
                body_bytes = body
            
            # 計算簽名
            hash_value = hmac.new(
                self.channel_secret.encode('utf-8'),
                body_bytes,
                hashlib.sha256
            ).digest()
            
            expected_signature = base64.b64encode(hash_value).decode('utf-8')
            
            # 比較簽名
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            # 調試信息
            print(f"收到的簽名: {signature}")
            print(f"計算的簽名: {expected_signature}")
            print(f"Body內容: {body[:100]}...")
            print(f"驗證結果: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            print(f"驗證簽名失敗: {e}")
            return False
    
    async def extract_user_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """從事件中提取用戶資訊"""
        try:
            user_info = {}
            
            # 提取用戶ID
            source = event_data.get("source", {})
            user_id = source.get("userId")
            if user_id:
                user_info["user_id"] = user_id
            
            # 提取群組ID（如果有的話）
            group_id = source.get("groupId")
            if group_id:
                user_info["group_id"] = group_id
            
            # 提取房間ID（如果有的話）
            room_id = source.get("roomId")
            if room_id:
                user_info["room_id"] = room_id
            
            # 提取用戶類型
            user_type = source.get("type", "user")
            user_info["user_type"] = user_type
            
            return user_info
            
        except Exception as e:
            print(f"提取用戶資訊失敗: {e}")
            return {}
    
    async def extract_message_content(self, event_data: Dict[str, Any]) -> str:
        """從事件中提取訊息內容"""
        try:
            message = event_data.get("message", {})
            message_type = message.get("type", "")
            
            if message_type == "text":
                return message.get("text", "")
            elif message_type == "sticker":
                return f"[貼圖: {message.get('packageId', '')}-{message.get('stickerId', '')}]"
            elif message_type == "image":
                return "[圖片]"
            elif message_type == "video":
                return "[影片]"
            elif message_type == "audio":
                return "[音訊]"
            elif message_type == "file":
                return "[檔案]"
            else:
                return f"[{message_type}訊息]"
                
        except Exception as e:
            print(f"提取訊息內容失敗: {e}")
            return ""
    
    async def get_user_profile(self, user_id: str) -> Dict[str, str]:
        """獲取用戶資料"""
        try:
            profile = self.line_bot_api.get_profile(user_id)
            return {
                "user_id": user_id,
                "display_name": profile.display_name,
                "picture_url": profile.picture_url,
                "status_message": profile.status_message
            }
        except LineBotApiError as e:
            print(f"獲取用戶資料失敗: {e}")
            return {"user_id": user_id}
        except Exception as e:
            print(f"獲取用戶資料失敗: {e}")
            return {"user_id": user_id}
    
    async def send_category_menu(self, user_id: str) -> bool:
        """發送問題分類選單"""
        try:
            menu_text = """🎯 我幫你把常見的工作場景整理成五種思考模式，你需要哪一個？

1️⃣ 任務拆解
   收到任務後該怎麼理清思路

2️⃣ 問題討論
   遇到難題，怎麼和主管有效溝通

3️⃣ 成果回報
   報告時怎麼安排順序更清楚

4️⃣ 觀點表達
   分享想法時如何更有說服力

5️⃣ 總結整理
   會議或專案後如何做出完整總結

💡 操作方式：
• 輸入數字 1–5 選擇場景
• 輸入「重置」回到選單"""
            
            return await self.send_text_message(user_id, menu_text)
            
        except Exception as e:
            print(f"發送分類選單失敗: {e}")
            return False
    
    async def send_category_confirmation(self, user_id: str, category_info: Dict[str, Any]) -> bool:
        """發送分類確認訊息"""
        try:
            confirmation_text = f"""✅ 你選擇了：{category_info['name']}

📝 這個分類可以幫助你：
{category_info['description']}

💡 例如：
{category_info['example']}

❓ 這是你想要的分類嗎？
請回覆「是」或「否」："""
            
            return await self.send_text_message(user_id, confirmation_text)
            
        except Exception as e:
            print(f"發送分類確認失敗: {e}")
            return False
    
    async def send_reset_message(self, user_id: str) -> bool:
        """發送重置訊息"""
        try:
            reset_text = "🔄 好的，讓我們重新開始！\n\n"
            menu_text = """🎯 你好！我是你的思考助手，請選擇你想要解決的問題類型：

1. 收到任務的時候，該如何思考任務
2. 遇到問題的時候，該怎麼跟團隊討論
3. 報告工作結果的時候順序該如何排
4. 我該如何有效的分享我的觀點？
5. 我該如何做會議或是專案總結

請輸入數字 (1-5) 來選擇："""
            
            return await self.send_text_message(user_id, reset_text + menu_text)
            
        except Exception as e:
            print(f"發送重置訊息失敗: {e}")
            return False
    
    async def send_error_message(self, user_id: str, error_message: str = "抱歉，發生了錯誤，請稍後再試。") -> bool:
        """發送錯誤訊息"""
        try:
            return await self.send_text_message(user_id, error_message)
        except Exception as e:
            print(f"發送錯誤訊息失敗: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 嘗試獲取LINE Bot資訊
            bot_info = self.line_bot_api.get_bot_info()
            return {
                "platform": "line",
                "status": "healthy",
                "bot_id": bot_info.user_id,
                "bot_name": bot_info.display_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "platform": "line",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
