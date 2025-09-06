"""
自定義異常處理
"""
from fastapi import HTTPException


class ChatbotException(Exception):
    """思考機器人基礎異常"""
    pass


class DatabaseException(ChatbotException):
    """資料庫相關異常"""
    pass


class RedisException(ChatbotException):
    """Redis相關異常"""
    pass


class AIServiceException(ChatbotException):
    """AI服務相關異常"""
    pass


class ConversationException(ChatbotException):
    """會話管理相關異常"""
    pass


class PromptException(ChatbotException):
    """Prompt管理相關異常"""
    pass


class UserException(ChatbotException):
    """用戶管理相關異常"""
    pass


class ValidationException(ChatbotException):
    """資料驗證相關異常"""
    pass


# 服務層異常
class PromptServiceError(PromptException):
    """Prompt服務異常"""
    pass


class CategoryNotFoundError(PromptException):
    """分類未找到異常"""
    pass


class InvalidCategorySelectionError(ValidationException):
    """無效分類選擇異常"""
    pass


class ConversationServiceError(ConversationException):
    """對話服務異常"""
    pass


class ConversationNotFoundError(ConversationException):
    """對話未找到異常"""
    pass


class UserNotFoundError(UserException):
    """用戶未找到異常"""
    pass


class DatabaseError(DatabaseException):
    """資料庫錯誤異常"""
    pass
