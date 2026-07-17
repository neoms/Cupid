import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "cupid2024")
MONGO_DB = os.getenv("MONGO_DATABASE", "cupid")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?directConnection=true"

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db():
    """连接 MongoDB"""
    global _client, _db
    _client = AsyncIOMotorClient(MONGO_URI)
    _db = _client[MONGO_DB]
    # 验证连接
    await _client.admin.command("ping")
    print(f"✓ MongoDB 已连接 ({MONGO_DB})")

    # 创建索引
    await _db.profiles.create_index("user_id", unique=True)
    await _db.profiles.create_index([("created_at", -1)])
    await _db.profiles.create_index([("province", 1), ("city", 1)])
    await _db.profiles.create_index([("gender", 1), ("birth_date", -1)])


async def close_db():
    """断开 MongoDB 连接"""
    global _client
    if _client:
        _client.close()
        print("✗ MongoDB 已断开")


def get_db() -> AsyncIOMotorDatabase:
    """获取数据库实例"""
    assert _db is not None, "数据库未初始化，请先调用 connect_db()"
    return _db
