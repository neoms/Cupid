import traceback
import uuid
from datetime import date, datetime

from fastapi import APIRouter, HTTPException, status

from app.services.database import get_db
from app.services.embeddings import _build_profile_text, embed_profile, embed_query
from app.services.reranker import rerank_documents
from app.models.schemas import (
    NaturalSearchParams,
    NaturalSearchResponse,
    NaturalSearchResult,
    ProfileCreate,
    ProfileResponse,
    SearchParams,
    SearchResponse,
)

router = APIRouter()

PROFILES_COLLECTION = "profiles"


def _calc_age(birth_date: date | datetime) -> int:
    """根据出生日期计算周岁年龄"""
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _serialize(doc: dict) -> ProfileResponse:
    """将 MongoDB 文档转为响应模型"""
    doc["_id"] = str(doc["_id"])
    doc["age"] = _calc_age(doc["birth_date"])
    return ProfileResponse(**doc)


def _build_filters(params) -> dict:
    """构建结构化筛选条件（共用逻辑）"""
    filters: dict = {}

    if params.gender:
        filters["gender"] = params.gender.value

    if getattr(params, "age_min", None) is not None or getattr(params, "age_max", None) is not None:
        today = date.today()
        birth_conditions: dict = {}
        if params.age_max is not None:
            birth_conditions["$gte"] = datetime(today.year - params.age_max, 1, 1)
        if params.age_min is not None:
            birth_conditions["$lte"] = datetime(today.year - params.age_min, 12, 31)
        if birth_conditions:
            filters["birth_date"] = birth_conditions

    if getattr(params, "height_min", None) is not None:
        filters.setdefault("height", {})["$gte"] = params.height_min
    if getattr(params, "height_max", None) is not None:
        filters.setdefault("height", {})["$lte"] = params.height_max

    if getattr(params, "province", None):
        filters["province"] = params.province
    if getattr(params, "city", None):
        filters["city"] = params.city
    if getattr(params, "education", None):
        filters["education"] = params.education.value
    if getattr(params, "marriage_status", None):
        filters["marriage_status"] = params.marriage_status.value
    if getattr(params, "occupation", None):
        filters["occupation"] = {"$regex": params.occupation, "$options": "i"}
    if getattr(params, "interests", None):
        filters["interests"] = {"$in": params.interests}

    return filters


# ────────────── 接口 1：创建/更新用户资料 ──────────────

@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate):
    """
    创建或更新用户资料。

    传入 user_id 且存在 → 更新资料；不传 user_id → 自动生成新用户。
    创建/更新时自动提取所有字段生成文本描述并向量化，用于后续自然语言搜索。

    字段说明（详见下方 Schema）：
    - **nickname**: 昵称，1-30字
    - **gender**: 性别，男/女
    - **birth_date**: 出生日期，YYYY-MM-DD，用于计算年龄
    - **height**: 身高(cm)，140-220
    - **weight**: 体重(kg)，选填，30-200
    - **province / city**: 所在地，如 广东 / 深圳
    - **education**: 学历，高中/大专/本科/硕士/博士
    - **occupation**: 职业，如"程序员"
    - **industry**: 行业，如"互联网"，选填
    - **income_range**: 年收入区间，选填
    - **body_type**: 体型，偏瘦/匀称/运动型/丰满，选填
    - **marriage_status**: 婚姻状况，默认未婚
    - **has_children**: 是否有子女
    - **want_children**: 是否想要孩子，true/false/null
    - **smoking / drinking**: 是否吸烟/饮酒，true/false/null
    - **self_intro**: 自我介绍，最多500字，会在语义搜索中被匹配
    - **interests**: 兴趣爱好标签列表，如["跑步","电影"]
    - **preference**: 择偶偏好对象，选填
    """
    db = get_db()
    now = datetime.utcnow()

    doc = profile.model_dump(mode="json")  # mode=json 将枚举转为字符串值
    doc["birth_date"] = datetime.combine(profile.birth_date, datetime.min.time())
    doc["updated_at"] = now

    # 生成向量嵌入（失败不影响资料创建）
    doc["embedding_text"] = _build_profile_text(doc)
    try:
        doc["embedding"] = await embed_profile(doc)
    except Exception:
        print(f"[WARN] 向量生成失败，将跳过 embedding 字段\n{traceback.format_exc()}")

    if profile.user_id:
        result = await db[PROFILES_COLLECTION].find_one_and_update(
            {"user_id": profile.user_id},
            {"$set": doc, "$setOnInsert": {"created_at": now}},
            upsert=True,
            return_document=True,
        )
    else:
        doc["user_id"] = uuid.uuid4().hex[:16]
        doc["created_at"] = now
        result = await db[PROFILES_COLLECTION].find_one_and_update(
            {"user_id": doc["user_id"]},
            {"$setOnInsert": doc},
            upsert=True,
            return_document=True,
        )

    return _serialize(result)


# ────────────── 接口 2：字段筛选搜索 ──────────────

@router.post("/profiles/search", response_model=SearchResponse)
async def search_profiles(params: SearchParams):
    """
    按结构化字段精确筛选好友资料。

    所有筛选条件可选，不传则不限制。多条件之间为 AND（同时满足）关系。

    字段说明（详见下方 Schema）：
    - **gender**: 性别筛选，男/女
    - **age_min / age_max**: 年龄范围（周岁），如 25-35
    - **height_min / height_max**: 身高范围(cm)，如 160-175
    - **province / city**: 所在地，精确匹配
    - **education**: 学历筛选
    - **marriage_status**: 婚姻状况筛选
    - **occupation**: 职业，模糊匹配（如"程序"可匹配"程序员"）
    - **interests**: 兴趣爱好，包含任一标签即匹配
    - **page / page_size**: 分页，默认第1页每页20条
    - **sort_by**: 排序，created_at/height/birth_date，默认按注册时间降序

    返回 total（总数）、当前页 results 列表。
    """
    db = get_db()
    filters = _build_filters(params)

    sort_field = params.sort_by or "created_at"
    sort_direction = -1

    total = await db[PROFILES_COLLECTION].count_documents(filters)

    skip = (params.page - 1) * params.page_size
    cursor = (
        db[PROFILES_COLLECTION]
        .find(filters)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(params.page_size)
    )
    results = [_serialize(doc) async for doc in cursor]

    return SearchResponse(
        total=total,
        page=params.page,
        page_size=params.page_size,
        results=results,
    )


# ────────────── 接口 3：自然语言搜索 ──────────────

@router.post("/profiles/search/natural", response_model=NaturalSearchResponse)
async def natural_search(params: NaturalSearchParams):
    """
    用自然语言描述搜索好友资料（AI 语义搜索 + 重排）。

    搜索流程：
    1. 用户描述 → Embedding 向量化
    2. 余弦相似度粗召回候选
    3. 百炼 Reranker AI 精排
    4. 按匹配度降序分页返回

    字段说明（详见下方 Schema）：
    - **query**: 自然语言描述（必填）。如"30岁左右的程序员，喜欢运动，性格开朗"。越详细越精准
    - **min_score**: 最低余弦相似度阈值(0~1)，低于此值的直接丢弃。默认0.5
    - **use_rerank**: 是否启用AI重排序。默认开启，大幅提升准确率；关闭则仅用向量相似度
    - **rerank_top_k**: 粗召回数量，送入AI精排。默认50，上限100。越大覆盖越广
    - **gender**: 可选，按性别预筛选
    - **age_min / age_max**: 可选，按年龄范围预筛选（周岁）
    - **province / city**: 可选，按地区预筛选
    - **page / page_size**: 分页，默认第1页每页20条

    返回结果中 score 越接近1越匹配。启用重排时 score 为百炼AI给出的 relevance_score。
    """
    db = get_db()

    # 1. 将查询文本转为向量
    try:
        query_embedding = await embed_query(params.query)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"向量化查询失败: {e}")

    # 2. 构建预筛选条件（可选）
    pre_filters = _build_filters(params)
    # 只搜索有 embedding 的资料
    pre_filters["embedding"] = {"$exists": True}

    # 3. 聚合管线：dot product 计算余弦相似度
    pipeline = [
        {"$match": pre_filters},
        {
            "$addFields": {
                "score": {
                    "$sum": {
                        "$map": {
                            "input": {"$zip": {"inputs": ["$embedding", query_embedding]}},
                            "as": "pair",
                            "in": {"$multiply": [{"$arrayElemAt": ["$$pair", 0]}, {"$arrayElemAt": ["$$pair", 1]}]},
                        }
                    }
                }
            }
        },
        {"$match": {"score": {"$gte": params.min_score}}},
    ]

    # 4. 统计总数
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = [doc async for doc in db[PROFILES_COLLECTION].aggregate(count_pipeline)]
    total = count_result[0]["total"] if count_result else 0

    if total == 0:
        return NaturalSearchResponse(total=0, page=params.page, page_size=params.page_size, results=[])

    # 5. 获取候选集
    if params.use_rerank:
        # 粗召回：取 top-N 送入重排
        candidates_pipeline = pipeline + [
            {"$sort": {"score": -1}},
            {"$limit": params.rerank_top_k},
        ]
    else:
        # 不走重排，直接分页
        skip = (params.page - 1) * params.page_size
        candidates_pipeline = pipeline + [
            {"$sort": {"score": -1}},
            {"$skip": skip},
            {"$limit": params.page_size},
        ]

    docs: list[dict] = []
    scores: list[float] = []
    async for doc in db[PROFILES_COLLECTION].aggregate(candidates_pipeline):
        scores.append(doc.pop("score", 0.0))
        docs.append(doc)

    # 6. 重排
    if params.use_rerank and docs:
        try:
            # 提取每个候选资料的文本表示
            doc_texts = [d.get("embedding_text", "") for d in docs]
            rerank_results = await rerank_documents(params.query, doc_texts)

            # 建立 index → relevance_score 映射
            score_map = {r["index"]: r["relevance_score"] for r in rerank_results}
            ranked = [(docs[i], score_map.get(i, 0.0)) for i in range(len(docs))]
            ranked.sort(key=lambda x: x[1], reverse=True)

            # 分页
            page_start = (params.page - 1) * params.page_size
            page_end = page_start + params.page_size
            page_items = ranked[page_start:page_end]

            # 重排后的总量以实际粗召回数为准
            total = min(total, params.rerank_top_k)
        except Exception:
            import traceback
            print(f"[WARN] 重排失败，回退到余弦相似度排序\n{traceback.format_exc()}")
            # 回退：使用余弦相似度分数，同时需要自行分页
            ranked = list(zip(docs, scores))
            ranked.sort(key=lambda x: x[1], reverse=True)
            total = min(total, params.rerank_top_k)
            page_start = (params.page - 1) * params.page_size
            page_end = page_start + params.page_size
            page_items = ranked[page_start:page_end]
    else:
        # 非重排模式：聚合管线已分页，直接组装
        page_items = list(zip(docs, scores))

    # 7. 构建响应
    results = [
        NaturalSearchResult(profile=_serialize(doc), score=round(score, 4))
        for doc, score in page_items
    ]

    return NaturalSearchResponse(
        total=total,
        page=params.page,
        page_size=params.page_size,
        results=results,
    )
