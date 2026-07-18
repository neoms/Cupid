"""阿里云百炼 Embedding 服务 —— 将文本转为向量"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from langfuse import observe

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

_client: Optional[httpx.AsyncClient] = None


def _build_profile_text(profile: dict) -> str:
    """将用户资料各字段拼接成一段自然语言描述，用于向量化"""
    parts = []

    # 基本信息
    parts.append(f"昵称{profile.get('nickname', '')}")
    parts.append(f"性别{profile.get('gender', '')}")
    birth = profile.get("birth_date")
    if birth:
        birth_str = birth.strftime("%Y年%m月%d日") if hasattr(birth, "strftime") else str(birth)[:10]
        parts.append(f"出生日期{birth_str}")
    parts.append(f"身高{profile.get('height', '')}厘米")
    if profile.get("weight"):
        parts.append(f"体重{profile['weight']}公斤")

    # 所在地
    parts.append(f"所在地{profile.get('province', '')}{profile.get('city', '')}")

    # 学历 & 职业
    parts.append(f"学历{profile.get('education', '')}")
    if profile.get("school"):
        parts.append(f"毕业院校{profile['school']}")
    parts.append(f"职业{profile.get('occupation', '')}")
    if profile.get("industry"):
        parts.append(f"行业{profile['industry']}")
    if profile.get("income_range"):
        parts.append(f"年收入{profile['income_range']}")

    # 外貌
    if profile.get("body_type"):
        parts.append(f"体型{profile['body_type']}")

    # 婚恋
    parts.append(f"婚姻状况{profile.get('marriage_status', '')}")
    if profile.get("has_children"):
        parts.append("有子女")
    if profile.get("want_children") is True:
        parts.append("想要孩子")
    elif profile.get("want_children") is False:
        parts.append("不想要孩子")

    # 生活习惯
    if profile.get("smoking") is True:
        parts.append("吸烟")
    elif profile.get("smoking") is False:
        parts.append("不吸烟")
    if profile.get("drinking") is True:
        parts.append("饮酒")
    elif profile.get("drinking") is False:
        parts.append("不饮酒")

    # 自我介绍 & 兴趣爱好
    interests = profile.get("interests", [])
    if interests:
        parts.append(f"兴趣爱好{'、'.join(interests)}")
    if profile.get("self_intro"):
        parts.append(f"自我介绍{profile['self_intro']}")

    # 择偶偏好
    pref = profile.get("preference")
    if pref:
        pref_parts = ["择偶偏好"]
        if pref.get("gender"):
            pref_parts.append(f"希望对方性别{pref['gender']}")
        pref_parts.append(f"年龄{pref.get('age_min', '')}到{pref.get('age_max', '')}岁")
        if pref.get("height_min") or pref.get("height_max"):
            h = f"身高{pref.get('height_min', '不限')}到{pref.get('height_max', '不限')}厘米"
            pref_parts.append(h)
        if pref.get("education"):
            pref_parts.append(f"学历{pref['education']}")
        if pref.get("province") or pref.get("city"):
            pref_parts.append(f"希望对方在{pref.get('province', '')}{pref.get('city', '')}")
        parts.append("，".join(pref_parts))

    return "。".join(parts) + "。"


@observe(name="embed_text")
async def embed_text(text: str, text_type: str = "document") -> list[float]:
    """调用百炼 Embedding API 将文本转为向量"""
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-api-key-here":
        raise RuntimeError("请在 .env 中配置 DASHSCOPE_API_KEY")

    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10.0)

    resp = await _client.post(
        DASHSCOPE_URL,
        headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
        json={
            "model": EMBEDDING_MODEL,
            "input": {"texts": [text]},
            "parameters": {"text_type": text_type},
        },
    )
    resp.raise_for_status()
    data = resp.json()

    if "output" not in data or "embeddings" not in data["output"]:
        code = data.get("code", "unknown")
        msg = data.get("message", "未知错误")
        raise RuntimeError(f"百炼 Embedding 失败: {code} - {msg}")

    return data["output"]["embeddings"][0]["embedding"]


async def embed_profile(profile: dict) -> list[float]:
    """将用户资料拼成描述文本，再转为向量"""
    text = _build_profile_text(profile)
    return await embed_text(text, text_type="document")


async def embed_query(query: str) -> list[float]:
    """将搜索语句转为向量"""
    return await embed_text(query, text_type="query")


async def close_embedding_client():
    """关闭 HTTP 客户端"""
    global _client
    if _client:
        await _client.aclose()
        _client = None
