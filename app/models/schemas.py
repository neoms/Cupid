from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ────────────── 枚举 ──────────────

class Gender(str, Enum):
    """性别"""
    male = "男"
    female = "女"


class EducationLevel(str, Enum):
    """学历"""
    high_school = "高中"
    associate = "大专"
    bachelor = "本科"
    master = "硕士"
    doctor = "博士"


class IncomeRange(str, Enum):
    """年收入区间"""
    low = "10万以下"
    mid_low = "10-20万"
    mid = "20-50万"
    mid_high = "50-100万"
    high = "100万以上"


class MarriageStatus(str, Enum):
    """婚姻状况"""
    never_married = "未婚"
    divorced = "离异"
    widowed = "丧偶"


class BodyType(str, Enum):
    """体型"""
    slim = "偏瘦"
    average = "匀称"
    athletic = "运动型"
    plump = "丰满"


# ────────────── 择偶偏好 ──────────────

class PartnerPreference(BaseModel):
    """择偶偏好 —— 描述用户期望的理想伴侣条件"""
    gender: Gender | None = Field(default=None, description="期望对方性别（男/女），不填则不限制")
    age_min: int = Field(default=20, ge=18, le=100, description="期望对方最小年龄（周岁），默认20")
    age_max: int = Field(default=40, ge=18, le=100, description="期望对方最大年龄（周岁），默认40")
    height_min: int | None = Field(default=None, ge=140, le=220, description="期望对方最低身高(cm)，不填则不限制")
    height_max: int | None = Field(default=None, ge=140, le=220, description="期望对方最高身高(cm)，不填则不限制")
    education: EducationLevel | None = Field(default=None, description="期望对方学历（高中/大专/本科/硕士/博士），不填则不限制")
    province: str | None = Field(default=None, max_length=20, description="期望对方所在省份，如'广东'，不填则不限制")
    city: str | None = Field(default=None, max_length=20, description="期望对方所在城市，如'深圳'，不填则不限制")
    marriage_status: MarriageStatus | None = Field(default=None, description="期望对方婚姻状况（未婚/离异/丧偶），不填则不限制")

    @model_validator(mode="after")
    def check_age_range(self):
        if self.age_min > self.age_max:
            raise ValueError("age_min 不能大于 age_max")
        if self.height_min and self.height_max and self.height_min > self.height_max:
            raise ValueError("height_min 不能大于 height_max")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "gender": "女",
                    "age_min": 25,
                    "age_max": 35,
                    "height_min": 160,
                    "height_max": 175,
                    "education": "本科",
                    "province": "广东",
                    "city": "深圳",
                    "marriage_status": "未婚",
                }
            ]
        }
    }


# ────────────── 用户资料（请求） ──────────────

class ProfileCreate(BaseModel):
    """创建/更新用户资料

    传入 user_id 且已存在 → 更新资料；不传 user_id → 自动生成新用户并创建。
    创建/更新时自动提取所有字段生成文本描述并向量化，用于自然语言搜索。
    """
    user_id: str | None = Field(default=None, description="用户唯一ID。传入且存在则更新资料，不传则自动生成")

    # ── 基本信息 ──
    nickname: str = Field(min_length=1, max_length=30, description="昵称/称呼，1-30字，展示用")
    gender: Gender = Field(description="性别：男/女")
    birth_date: date = Field(description="出生日期，格式 YYYY-MM-DD，用于计算周岁年龄")
    height: int = Field(ge=140, le=220, description="身高(cm)，范围 140~220")
    weight: int | None = Field(default=None, ge=30, le=200, description="体重(kg)，选填，范围 30~200")

    # ── 所在地 ──
    province: str = Field(min_length=1, max_length=20, description="省份，如'广东'、'北京'")
    city: str = Field(min_length=1, max_length=20, description="城市，如'深圳'、'朝阳'")

    # ── 学历 & 职业 ──
    education: EducationLevel = Field(description="学历：高中/大专/本科/硕士/博士")
    school: str | None = Field(default=None, max_length=50, description="毕业院校，选填")
    occupation: str = Field(min_length=1, max_length=50, description="职业，如'程序员'、'教师'、'设计师'")
    industry: str | None = Field(default=None, max_length=30, description="行业，如'互联网'、'金融'、'教育'，选填")
    income_range: IncomeRange | None = Field(default=None, description="年收入：10万以下 / 10-20万 / 20-50万 / 50-100万 / 100万以上")

    # ── 外貌 ──
    body_type: BodyType | None = Field(default=None, description="体型：偏瘦/匀称/运动型/丰满，选填")

    # ── 婚恋状态 ──
    marriage_status: MarriageStatus = Field(default=MarriageStatus.never_married, description="婚姻状况：未婚/离异/丧偶，默认未婚")
    has_children: bool = Field(default=False, description="是否有子女，默认否")
    want_children: bool | None = Field(default=None, description="是否想要孩子：true=想 / false=不想 / null=未表态")

    # ── 生活习惯 ──
    smoking: bool | None = Field(default=None, description="是否吸烟：true=吸 / false=不吸 / null=未知")
    drinking: bool | None = Field(default=None, description="是否饮酒：true=喝 / false=不喝 / null=未知")

    # ── 自我介绍 ──
    self_intro: str | None = Field(default=None, max_length=500, description="自我介绍/内心独白，最多500字。会在自然语言搜索中被匹配")
    interests: list[str] = Field(default_factory=list, description="兴趣爱好标签列表，如 ['跑步','电影','旅行']")
    avatar_url: str | None = Field(default=None, description="头像图片URL地址")

    # ── 择偶偏好 ──
    preference: PartnerPreference | None = Field(default=None, description="择偶偏好，选填")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nickname": "小明",
                    "gender": "男",
                    "birth_date": "1994-08-20",
                    "height": 178,
                    "weight": 72,
                    "province": "广东",
                    "city": "深圳",
                    "education": "本科",
                    "school": "中山大学",
                    "occupation": "程序员",
                    "industry": "互联网",
                    "income_range": "20-50万",
                    "body_type": "匀称",
                    "marriage_status": "未婚",
                    "has_children": False,
                    "want_children": True,
                    "smoking": False,
                    "drinking": False,
                    "self_intro": "热爱生活，喜欢运动旅行，期待遇见有趣的你",
                    "interests": ["跑步", "电影", "旅行"],
                    "avatar_url": "https://example.com/avatar.jpg",
                    "preference": {
                        "gender": "女",
                        "age_min": 24,
                        "age_max": 32,
                        "height_min": 160,
                        "height_max": 172,
                    },
                }
            ]
        }
    }


# ────────────── 用户资料（响应） ──────────────

class ProfileResponse(BaseModel):
    """用户资料响应 —— 返回给前端的完整用户数据，age 为实时计算"""
    id: str = Field(alias="_id", description="MongoDB 文档 ID（系统内部使用）")
    user_id: str = Field(description="用户业务 ID（16位），创建时自动生成")
    nickname: str = Field(description="昵称")
    gender: Gender = Field(description="性别：男/女")
    birth_date: date = Field(description="出生日期，YYYY-MM-DD")
    age: int = Field(description="周岁年龄（根据 birth_date 实时计算）")
    height: int = Field(description="身高(cm)")
    weight: int | None = Field(default=None, description="体重(kg)，未填则为 null")
    province: str = Field(description="省份")
    city: str = Field(description="城市")
    education: EducationLevel = Field(description="学历")
    school: str | None = Field(default=None, description="毕业院校")
    occupation: str = Field(description="职业")
    industry: str | None = Field(default=None, description="行业")
    income_range: IncomeRange | None = Field(default=None, description="年收入区间")
    body_type: BodyType | None = Field(default=None, description="体型")
    marriage_status: MarriageStatus = Field(description="婚姻状况")
    has_children: bool = Field(default=False, description="是否有子女")
    want_children: bool | None = Field(default=None, description="是否想要孩子，null=未表态")
    smoking: bool | None = Field(default=None, description="是否吸烟，null=未知")
    drinking: bool | None = Field(default=None, description="是否饮酒，null=未知")
    self_intro: str | None = Field(default=None, description="自我介绍")
    interests: list[str] = Field(default_factory=list, description="兴趣爱好标签列表")
    avatar_url: str | None = Field(default=None, description="头像图片URL")
    preference: PartnerPreference | None = Field(default=None, description="择偶偏好")
    created_at: datetime = Field(description="资料创建时间（UTC）")

    model_config = {"populate_by_name": True}


# ────────────── 结构化搜索 ──────────────

class SearchParams(BaseModel):
    """结构化字段筛选搜索 —— 按固定条件精确过滤

    所有筛选条件均为可选，不传则不限制。多个条件之间为 AND 关系（同时满足）。
    """
    gender: Gender | None = Field(default=None, description="按性别筛选：男/女，不填则不限制")
    age_min: int | None = Field(default=None, ge=18, le=100, description="最小年龄（周岁），不填则不限制下限")
    age_max: int | None = Field(default=None, ge=18, le=100, description="最大年龄（周岁），不填则不限制上限")
    height_min: int | None = Field(default=None, ge=140, le=220, description="最低身高(cm)，不填则不限制")
    height_max: int | None = Field(default=None, ge=140, le=220, description="最高身高(cm)，不填则不限制")
    province: str | None = Field(default=None, description="所在省份，精确匹配，如'广东'")
    city: str | None = Field(default=None, description="所在城市，精确匹配，如'深圳'")
    education: EducationLevel | None = Field(default=None, description="学历筛选：高中/大专/本科/硕士/博士")
    marriage_status: MarriageStatus | None = Field(default=None, description="婚姻状况筛选：未婚/离异/丧偶")
    occupation: str | None = Field(default=None, description="职业，模糊匹配。如输入'程序'可匹配到'程序员'")
    interests: list[str] | None = Field(default=None, description="兴趣爱好筛选，包含任一标签即匹配。如 ['跑步','游泳']")

    # ── 分页 ──
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页返回条数，最大100")

    # ── 排序 ──
    sort_by: str | None = Field(
        default="created_at",
        pattern=r"^(created_at|height|birth_date)$",
        description="排序字段：created_at=注册时间 / height=身高 / birth_date=出生日期。默认按注册时间降序",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "gender": "女",
                    "age_min": 25,
                    "age_max": 35,
                    "height_min": 160,
                    "province": "广东",
                    "city": "深圳",
                    "education": "本科",
                    "marriage_status": "未婚",
                    "page": 1,
                    "page_size": 20,
                    "sort_by": "created_at",
                }
            ]
        }
    }


class SearchResponse(BaseModel):
    """结构化搜索响应"""
    total: int = Field(description="符合条件的总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    results: list[ProfileResponse] = Field(description="当前页的用户资料列表")


# ────────────── 自然语言搜索 ──────────────

class NaturalSearchParams(BaseModel):
    """自然语言搜索 —— 用一句话描述理想对象，AI 理解语义并匹配

    搜索流程：
    1. 用户描述 → Embedding 向量化
    2. 余弦相似度粗召回 top-N 条候选
    3. 百炼 Reranker 精排（确保准确性）
    4. 按匹配度降序分页返回

    可叠加性别/年龄/地区预筛选缩小候选范围，提升速度。
    """
    query: str = Field(
        min_length=1,
        max_length=500,
        description="自然语言描述（1-500字）。如'30岁左右的程序员，喜欢运动，性格开朗'。越详细结果越精准",
    )
    min_score: float = Field(default=0.5, ge=0, le=1.0, description="最低余弦相似度阈值(0~1)，低于此分数的候选直接丢弃。默认0.5")

    # ── 查询优化 ──
    use_query_optimization: bool = Field(
        default=False,
        description="是否用百炼 LLM 优化用户查询。简短输入如'找个程序员'会被扩写为丰富的语义描述，提升匹配精度。默认关闭",
    )

    # ── 重排控制 ──
    use_rerank: bool = Field(
        default=True,
        description="是否启用百炼 AI 重排序。默认开启，大幅提升准确率。关闭后仅用向量相似度排序",
    )
    rerank_top_k: int = Field(
        default=50, ge=1, le=100,
        description="粗召回候选数量，送入 AI 精排模型。默认50，上限100。越大覆盖越广但需更多时间",
    )

    # ── 可选的结构化预筛选 ──
    gender: Gender | None = Field(default=None, description="按性别预筛选：男/女，不填则不限制")
    education: EducationLevel | None = Field(default=None, description="按学历预筛选：高中/大专/本科/硕士/博士")
    marriage_status: MarriageStatus | None = Field(default=None, description="按婚姻状况预筛选：未婚/离异/丧偶")
    age_min: int | None = Field(default=None, ge=18, le=100, description="按最小年龄预筛选（周岁），不填则不限制")
    age_max: int | None = Field(default=None, ge=18, le=100, description="按最大年龄预筛选（周岁），不填则不限制")
    height_min: int | None = Field(default=None, ge=140, le=220, description="按最低身高预筛选(cm)")
    height_max: int | None = Field(default=None, ge=140, le=220, description="按最高身高预筛选(cm)")
    province: str | None = Field(default=None, description="按省份预筛选，精确匹配。如'广东'")
    city: str | None = Field(default=None, description="按城市预筛选，精确匹配。如'深圳'")
    occupation: str | None = Field(default=None, description="按职业预筛选，模糊匹配。如'程序'可匹配'程序员'")

    # ── 分页 ──
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页返回条数，最大100")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "30岁左右的程序员，喜欢运动和旅行，性格开朗大方",
                    "min_score": 0.5,
                    "use_query_optimization": False,
                    "use_rerank": True,
                    "rerank_top_k": 50,
                    "gender": "女",
                    "age_min": 25,
                    "age_max": 35,
                    "province": "广东",
                    "city": "深圳",
                    "page": 1,
                    "page_size": 20,
                },
                {
                    "query": "找个程序员",
                    "min_score": 0.5,
                    "use_query_optimization": True,
                    "use_rerank": True,
                    "rerank_top_k": 50,
                    "gender": "女",
                    "page": 1,
                    "page_size": 20,
                },
            ]
        }
    }


class NaturalSearchResult(BaseModel):
    """自然语言搜索单条结果"""
    profile: ProfileResponse = Field(description="匹配到的用户完整资料")
    score: float = Field(
        description="匹配度分数(0~1)，越接近1越匹配。启用重排时为百炼AI的relevance_score，未启用时为向量余弦相似度",
    )


class NaturalSearchResponse(BaseModel):
    """自然语言搜索响应"""
    total: int = Field(description="符合条件的总记录数。重排模式下上限为 rerank_top_k，超出部分未经过精排")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页返回条数")
    results: list[NaturalSearchResult] = Field(description="当前页搜索结果，按匹配度从高到低排列")
    optimized_query: str | None = Field(default=None, description="开启查询优化后，LLM 扩写后的查询文本，可用于调试和效果验证")
