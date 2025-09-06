"""
Prompt管理器
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models import PromptCategory
from app.prompts.categories import (
    PROBLEM_CATEGORIES, 
    get_category_by_number, 
    get_category_by_key,
    format_category_menu,
    format_category_confirmation,
    is_reset_keyword,
    is_confirm_keyword
)


class PromptManager:
    """Prompt管理器"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_category_menu(self) -> str:
        """獲取問題分類選單"""
        return format_category_menu()
    
    def get_category_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        """根據數字獲取問題分類"""
        return get_category_by_number(number)
    
    def get_category_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """根據鍵值獲取問題分類"""
        return get_category_by_key(key)
    
    def get_category_confirmation(self, category: Dict[str, Any]) -> str:
        """獲取分類確認訊息"""
        return format_category_confirmation(category)
    
    def is_reset_keyword(self, text: str) -> bool:
        """檢查是否為重置關鍵詞"""
        return is_reset_keyword(text)
    
    def is_confirm_keyword(self, text: str) -> Optional[str]:
        """檢查是否為確認關鍵詞"""
        return is_confirm_keyword(text)
    
    def get_prompt_template(self, category_key: str) -> Optional[str]:
        """獲取指定分類的Prompt模板"""
        category = self.get_category_by_key(category_key)
        if category:
            return category['prompt_template']
        return None
    
    def get_category_from_db(self, category_key: str) -> Optional[PromptCategory]:
        """從資料庫獲取問題分類"""
        return PromptCategory.get_by_key(self.db_session, category_key)
    
    def get_all_categories_from_db(self) -> List[PromptCategory]:
        """從資料庫獲取所有啟用的問題分類"""
        return PromptCategory.get_active_categories(self.db_session)
    
    def sync_categories_to_db(self) -> bool:
        """將分類定義同步到資料庫"""
        try:
            for number, category_data in PROBLEM_CATEGORIES.items():
                # 檢查分類是否已存在
                existing_category = self.get_category_from_db(category_data['key'])
                
                if existing_category:
                    # 更新現有分類
                    existing_category.name = category_data['name']
                    existing_category.description = category_data['description']
                    existing_category.example = category_data['example']
                    existing_category.prompt_template = category_data['prompt_template']
                    existing_category.is_active = True
                else:
                    # 創建新分類
                    new_category = PromptCategory(
                        category_key=category_data['key'],
                        name=category_data['name'],
                        description=category_data['description'],
                        example=category_data['example'],
                        prompt_template=category_data['prompt_template'],
                        is_active=True
                    )
                    self.db_session.add(new_category)
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            self.db_session.rollback()
            print(f"同步分類到資料庫失敗: {e}")
            return False
    
    def validate_category_selection(self, user_input: str) -> Optional[Dict[str, Any]]:
        """驗證用戶的分類選擇"""
        try:
            choice = int(user_input.strip())
            if 1 <= choice <= 5:
                return self.get_category_by_number(choice)
        except ValueError:
            pass
        return None
    
    def get_category_summary(self, category_key: str) -> Optional[Dict[str, str]]:
        """獲取分類摘要資訊"""
        category = self.get_category_by_key(category_key)
        if category:
            return {
                'name': category['name'],
                'description': category['description'],
                'example': category['example']
            }
        return None
    
    def format_conversation_start(self, category_key: str) -> str:
        """格式化對話開始訊息"""
        category = self.get_category_by_key(category_key)
        if category:
            return f"""✅ 好的！我現在是你的{category['name']}顧問。

{category['prompt_template']}

請告訴我你遇到的具體問題，我會根據你的情況提供專業的建議和指導。"""
        return "抱歉，無法找到指定的問題分類。"
    
    def get_reset_message(self) -> str:
        """獲取重置訊息"""
        return "🔄 好的，讓我們重新開始！\n\n" + self.get_category_menu()
    
    def get_invalid_selection_message(self) -> str:
        """獲取無效選擇訊息"""
        return "❌ 請輸入有效的數字 (1-5)："
    
    def get_invalid_confirmation_message(self) -> str:
        """獲取無效確認訊息"""
        return "❓ 請回覆「是」或「否」："
