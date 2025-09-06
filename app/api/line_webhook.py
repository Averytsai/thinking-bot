"""
LINE Webhook API路由
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json

from app.core.database import get_db
from app.core.config import Settings
from app.services import AIManager, LineService

router = APIRouter(prefix="/api/line", tags=["LINE Bot"])

# 全域變數（在實際應用中應該使用依賴注入）
_line_service: LineService = None


def get_line_service() -> LineService:
    """獲取LINE服務實例"""
    global _line_service
    if _line_service is None:
        settings = Settings()
        db_session = next(get_db())
        ai_manager = AIManager(db_session, settings)
        
        line_config = {
            "channel_access_token": settings.line_channel_access_token,
            "channel_secret": settings.line_channel_secret
        }
        
        _line_service = LineService(db_session, line_config, ai_manager)
    
    return _line_service


@router.post("/webhook")
async def line_webhook(request: Request):
    """LINE Bot webhook端點"""
    try:
        # 獲取請求資料
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")
        
        # 獲取LINE服務
        line_service = get_line_service()
        
        # 驗證簽名
        if not await line_service.verify_signature(signature, body.decode('utf-8')):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析請求資料
        request_data = json.loads(body.decode('utf-8'))
        
        # 處理webhook
        response = await line_service.handle_webhook(request_data)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"LINE webhook處理失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


@router.get("/health")
async def line_health():
    """LINE服務健康檢查"""
    try:
        line_service = get_line_service()
        health_info = await line_service.health_check()
        
        return JSONResponse(content=health_info)
        
    except Exception as e:
        print(f"LINE健康檢查失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Health check failed"}
        )


@router.post("/send-message")
async def send_message(
    user_id: str,
    message: str,
    line_service: LineService = Depends(get_line_service)
):
    """發送訊息給指定用戶"""
    try:
        success = await line_service.line_adapter.send_message(user_id, message)
        
        return JSONResponse(content={
            "success": success,
            "user_id": user_id,
            "message": message
        })
        
    except Exception as e:
        print(f"發送訊息失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to send message"}
        )


@router.get("/user/{line_user_id}/stats")
async def get_user_stats(
    line_user_id: str,
    line_service: LineService = Depends(get_line_service)
):
    """獲取用戶統計"""
    try:
        stats = await line_service.get_user_statistics(line_user_id)
        return JSONResponse(content=stats)
        
    except Exception as e:
        print(f"獲取用戶統計失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get user statistics"}
        )


@router.post("/user/{line_user_id}/stats")
async def send_user_stats(
    line_user_id: str,
    line_service: LineService = Depends(get_line_service)
):
    """發送用戶統計給用戶"""
    try:
        success = await line_service.send_user_statistics(line_user_id)
        
        return JSONResponse(content={
            "success": success,
            "user_id": line_user_id
        })
        
    except Exception as e:
        print(f"發送用戶統計失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to send user statistics"}
        )


@router.post("/user/{line_user_id}/summary")
async def send_conversation_summary(
    line_user_id: str,
    line_service: LineService = Depends(get_line_service)
):
    """發送對話總結給用戶"""
    try:
        success = await line_service.send_conversation_summary(line_user_id)
        
        return JSONResponse(content={
            "success": success,
            "user_id": line_user_id
        })
        
    except Exception as e:
        print(f"發送對話總結失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to send conversation summary"}
        )


@router.post("/user/{line_user_id}/welcome")
async def send_welcome_message(
    line_user_id: str,
    line_service: LineService = Depends(get_line_service)
):
    """發送歡迎訊息給用戶"""
    try:
        success = await line_service.send_welcome_message(line_user_id)
        
        return JSONResponse(content={
            "success": success,
            "user_id": line_user_id
        })
        
    except Exception as e:
        print(f"發送歡迎訊息失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to send welcome message"}
        )
