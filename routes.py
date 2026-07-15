import math
import uuid
from datetime import date, datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from database import get_db
from models import (
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


# ────────────── 接口 1：创建/更新用户资料 ──────────────

@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate):
    """
    创建或更新用户资料。

    - 如果传入 user_id 且已存在，则更新该用户资料。
    - 如果未传 user_id，则自动生成一个新 user_id 并创建资料。
    """
    db = get_db()
    now = datetime.utcnow()

    doc = profile.model_dump()
    doc["birth_date"] = datetime.combine(profile.birth_date, datetime.min.time())
    doc["updated_at"] = now

    if profile.user_id:
        # 传了 user_id：存在则更新，不存在则创建
        doc["created_at"] = now  # 新建时设置，更新时用 $setOnInsert
        result = await db[PROFILES_COLLECTION].find_one_and_update(
            {"user_id": profile.user_id},
            {"$set": doc, "$setOnInsert": {"created_at": now}},
            upsert=True,
            return_document=True,
        )
    else:
        # 未传 user_id：自动生成并创建
        doc["user_id"] = uuid.uuid4().hex[:16]
        doc["created_at"] = now
        result = await db[PROFILES_COLLECTION].find_one_and_update(
            {"user_id": doc["user_id"]},
            {"$setOnInsert": doc},
            upsert=True,
            return_document=True,
        )

    return _serialize(result)


# ────────────── 接口 2：好友搜索 ──────────────

@router.post("/profiles/search", response_model=SearchResponse)
async def search_profiles(params: SearchParams):
    """
    搜索匹配的好友资料。

    支持按性别、年龄、身高、地区、学历、婚姻状态、职业等条件筛选，
    支持分页和排序。
    """
    db = get_db()
    filters: dict = {}

    if params.gender:
        filters["gender"] = params.gender.value

    if params.age_min is not None or params.age_max is not None:
        today = date.today()
        birth_conditions: dict = {}
        if params.age_max is not None:
            birth_conditions["$gte"] = datetime(today.year - params.age_max, 1, 1)
        if params.age_min is not None:
            birth_conditions["$lte"] = datetime(today.year - params.age_min, 12, 31)
        if birth_conditions:
            filters["birth_date"] = birth_conditions

    if params.height_min is not None:
        filters.setdefault("height", {})["$gte"] = params.height_min
    if params.height_max is not None:
        filters.setdefault("height", {})["$lte"] = params.height_max

    if params.province:
        filters["province"] = params.province
    if params.city:
        filters["city"] = params.city
    if params.education:
        filters["education"] = params.education.value
    if params.marriage_status:
        filters["marriage_status"] = params.marriage_status.value
    if params.occupation:
        filters["occupation"] = {"$regex": params.occupation, "$options": "i"}

    if params.interests:
        filters["interests"] = {"$in": params.interests}

    # 确定排序
    sort_field = params.sort_by or "created_at"
    sort_direction = -1  # 默认降序

    # 统计总数
    total = await db[PROFILES_COLLECTION].count_documents(filters)

    # 分页查询
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
