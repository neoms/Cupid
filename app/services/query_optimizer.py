"""百炼 LLM 查询优化 —— 将简短的用户搜索描述扩展为丰富的语义文本"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from langfuse import observe

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
LLM_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

SYSTEM_PROMPT = (
    "你是一个婚恋交友平台的搜索助手。用户会用简短的口语描述理想对象，"
    "你需要将其扩展为一段丰富的、包含多维信息的自然语言描述，用于语义搜索匹配。\n\n"
    "扩写规则：\n"
    "1. 保留用户原始意图，不要编造用户没提到的信息\n"
    "2. 如果用户提到了职业（如'程序员'），补充典型的职业特征（作息、性格倾向等）\n"
    "3. 如果用户提到了爱好，补充相关的生活场景描述\n"
    "4. 使用自然的叙述语句，不要用列表或标签格式\n"
    "5. 输出仅包含优化后的描述文本，不要加任何前缀、后缀或解释\n"
    "6. 字数控制在 50-200 字之间"
)

_client: Optional[httpx.AsyncClient] = None


@observe(name="optimize_query")
async def optimize_query(raw_query: str) -> str:
    """
    使用百炼 LLM 将用户简短的原始查询优化为丰富的语义描述。

    Args:
        raw_query: 用户输入的原始查询文本

    Returns:
        优化后的查询文本
    """
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-api-key-here":
        raise RuntimeError("请在 .env 中配置 DASHSCOPE_API_KEY")

    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=15.0)

    resp = await _client.post(
        LLM_URL,
        headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"用户想找：{raw_query}"},
            ],
            "temperature": 0.7,
            "max_tokens": 400,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    if "choices" not in data or not data["choices"]:
        code = data.get("code", "unknown")
        msg = data.get("message", "未知错误")
        raise RuntimeError(f"百炼 LLM 查询优化失败: {code} - {msg}")

    optimized = data["choices"][0]["message"]["content"].strip()
    return optimized


async def close_optimizer_client():
    """关闭 HTTP 客户端"""
    global _client
    if _client:
        await _client.aclose()
        _client = None
