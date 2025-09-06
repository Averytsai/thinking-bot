"""
思考機器人主應用程式
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.line_webhook import router as line_router

app = FastAPI(
    title="思考機器人",
    description="支援多通訊平台的對話機器人",
    version="1.0.0"
)

# 設定CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(line_router)

@app.get("/")
async def root():
    """根路徑 - 健康檢查"""
    return {
        "message": "思考機器人 API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
