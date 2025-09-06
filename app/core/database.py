"""
資料庫連接管理
"""
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from .config import settings

# 設定日誌
logger = logging.getLogger(__name__)

# SQLAlchemy 基礎類別
Base = declarative_base()

# 資料庫引擎
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug,  # 開發時顯示SQL
    echo_pool=settings.debug,
)

# 會話工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Redis連接
try:
    redis_client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    # 測試連接
    redis_client.ping()
    logger.info("Redis連接成功")
except Exception as e:
    logger.error(f"Redis連接失敗: {e}")
    redis_client = None


def get_db() -> Generator[Session, None, None]:
    """
    獲取資料庫會話
    用於FastAPI的依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"資料庫會話錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_database_connection() -> bool:
    """
    測試資料庫連接
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("資料庫連接測試成功")
        return True
    except Exception as e:
        logger.error(f"資料庫連接測試失敗: {e}")
        return False


def test_redis_connection() -> bool:
    """
    測試Redis連接
    """
    if redis_client is None:
        logger.error("Redis客戶端未初始化")
        return False
    
    try:
        redis_client.ping()
        logger.info("Redis連接測試成功")
        return True
    except Exception as e:
        logger.error(f"Redis連接測試失敗: {e}")
        return False


def get_redis() -> redis.Redis:
    """
    獲取Redis客戶端
    """
    if redis_client is None:
        raise RuntimeError("Redis客戶端未初始化")
    return redis_client


# 初始化時測試連接
if __name__ == "__main__":
    # 測試資料庫連接
    db_ok = test_database_connection()
    redis_ok = test_redis_connection()
    
    if db_ok and redis_ok:
        print("✅ 所有資料庫連接正常")
    else:
        print("❌ 資料庫連接有問題")
        if not db_ok:
            print("  - PostgreSQL連接失敗")
        if not redis_ok:
            print("  - Redis連接失敗")
