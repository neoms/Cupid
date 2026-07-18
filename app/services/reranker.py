"""阿里云百炼 Rerank 服务 —— 对向量搜索候选集精排"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from langfuse import observe

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
RERANK_URL = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
RERANK_MODEL = os.getenv("RERANK_MODEL", "qwen3-vl-rerank")

_client: Optional[httpx.AsyncClient] = None


@observe(name="rerank_documents")
async def rerank_documents(
    query: str,
    documents: list[str],
    top_n: int | None = None,
) -> list[dict]:
    """
    调用百炼 Rerank API 对候选文档重新排序。

    Args:
        query: 用户查询文本
        documents: 候选文档文本列表（最多 100 条）
        top_n: 返回前 top_n 条，默认返回全部

    Returns:
        按 relevance_score 降序排列的结果列表:
        [{"index": int, "relevance_score": float}, ...]
    """
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-api-key-here":
        raise RuntimeError("请在 .env 中配置 DASHSCOPE_API_KEY")

    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)

    if len(documents) > 100:
        raise ValueError(f"单次重排文档数量不能超过 100 条，当前 {len(documents)} 条")

    payload: dict = {
        "model": RERANK_MODEL,
        "input": {
            "query": query,
            "documents": [{"text": doc} for doc in documents],
        },
        "parameters": {"return_documents": False},
    }
    if top_n is not None:
        payload["parameters"]["top_n"] = min(top_n, len(documents))

    resp = await _client.post(
        RERANK_URL,
        headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()

    if "output" not in data or "results" not in data["output"]:
        code = data.get("code", "unknown")
        msg = data.get("message", "未知错误")
        raise RuntimeError(f"百炼 Rerank 失败: {code} - {msg}")

    return data["output"]["results"]


async def close_rerank_client():
    """关闭 HTTP 客户端"""
    global _client
    if _client:
        await _client.aclose()
        _client = None
