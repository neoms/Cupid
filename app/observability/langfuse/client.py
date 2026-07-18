"""LangFuse 追踪客户端 —— 统一初始化与 flush 管理"""

from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

_client = None


def get_langfuse():
    """获取 LangFuse 客户端单例（延迟初始化，自动读取 LANGFUSE_* 环境变量）"""
    global _client
    if _client is None:
        _client = get_client()
    return _client


def flush():
    """同步 flush 所有未发送的追踪事件（关闭服务前调用）"""
    global _client
    if _client is not None:
        _client.flush()
