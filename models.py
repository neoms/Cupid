from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ────────────── 枚举 ──────────────

class Gender(str, Enum):
    male = "男"
    female = "女"


class EducationLevel(str, Enum):
    high_school = "高中"
    associate = "大专"
    bachelor = "本科"
    master = "硕士"
    doctor = "博士"


class IncomeRange(str, Enum):
    low = "10万以下"
    mid_low = "10-20万"
    mid = "20-50万"
    mid_high = "50-100万"
    high = "100万以上"


class MarriageStatus(str, Enum):
    never_married = "未婚"
    divorced = "离异"
    widowed = "丧偶"


class BodyType(str, Enum):
    slim = "偏瘦"
    average = "匀称"
    athletic = "运动型"
    plump = "丰满"


# ────────────── 择偶偏好 ──────────────

class PartnerPreference(BaseModel):
    gender: Gender | None = None
    age_min: int = Field(default=20, ge=18, le=100, description="期望对方最小年龄")
    age_max: int = Field(default=40, ge=18, le=100, description="期望对方最大年龄")
    height_min: int | None = Field(default=None, ge=140, le=220, description="期望对方最低身高(cm)")
    height_max: int | None = Field(default=None, ge=140, le=220, description="期望对方最高身高(cm)")
    education: EducationLevel | None = None
    province: str | None = None
    city: str | None = None
    marriage_status: MarriageStatus | None = None

    @model_validator(mode="after")
    def check_age_range(self):
        if self.age_min > self.age_max:
            raise ValueError("age_min 不能大于 age_max")
        if self.height_min and self.height_max and self.height_min > self.height_max:
            raise ValueError("height_min 不能大于 height_max")
        return self


# ────────────── 用户资料（请求） ──────────────

class ProfileCreate(BaseModel):
    """创建/更新用户资料的请求体"""
    user_id: str | None = Field(default=None, description="用户唯一ID，不传则自动生成")
    # 基本信息
    nickname: str = Field(min_length=1, max_length=30, description="昵称")
    gender: Gender
    birth_date: date = Field(description="出生日期")
    height: int = Field(ge=140, le=220, description="身高(cm)")
    weight: int | None = Field(default=None, ge=30, le=200, description="体重(kg)")

    # 所在地
    province: str = Field(min_length=1, max_length=20, description="省份")
    city: str = Field(min_length=1, max_length=20, description="城市")

    # 学历 & 职业
    education: EducationLevel
    school: str | None = Field(default=None, max_length=50)
    occupation: str = Field(min_length=1, max_length=50, description="职业")
    industry: str | None = Field(default=None, max_length=30, description="行业")
    income_range: IncomeRange | None = None

    # 外貌
    body_type: BodyType | None = None

    # 婚恋状态
    marriage_status: MarriageStatus = Field(default=MarriageStatus.never_married)
    has_children: bool = False
    want_children: bool | None = None

    # 生活习惯
    smoking: bool | None = None
    drinking: bool | None = None

    # 自我介绍
    self_intro: str | None = Field(default=None, max_length=500, description="自我介绍")
    interests: list[str] = Field(default_factory=list, description="兴趣爱好标签")
    avatar_url: str | None = None

    # 择偶偏好
    preference: PartnerPreference | None = None


# ────────────── 用户资料（响应） ──────────────

class ProfileResponse(BaseModel):
    """返回给前端的用户资料"""
    id: str = Field(alias="_id")
    user_id: str
    nickname: str
    gender: Gender
    birth_date: date
    age: int = Field(description="年龄（实时计算）")
    height: int
    weight: int | None = None
    province: str
    city: str
    education: EducationLevel
    school: str | None = None
    occupation: str
    industry: str | None = None
    income_range: IncomeRange | None = None
    body_type: BodyType | None = None
    marriage_status: MarriageStatus
    has_children: bool = False
    want_children: bool | None = None
    smoking: bool | None = None
    drinking: bool | None = None
    self_intro: str | None = None
    interests: list[str] = []
    avatar_url: str | None = None
    preference: PartnerPreference | None = None
    created_at: datetime

    model_config = {"populate_by_name": True}


# ────────────── 搜索参数 ──────────────

class SearchParams(BaseModel):
    """好友搜索过滤参数"""
    gender: Gender | None = None
    age_min: int | None = Field(default=None, ge=18, le=100)
    age_max: int | None = Field(default=None, ge=18, le=100)
    height_min: int | None = Field(default=None, ge=140, le=220)
    height_max: int | None = Field(default=None, ge=140, le=220)
    province: str | None = None
    city: str | None = None
    education: EducationLevel | None = None
    marriage_status: MarriageStatus | None = None
    occupation: str | None = None
    interests: list[str] | None = None

    # 分页
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    # 排序（可选按注册时间、身高）
    sort_by: str | None = Field(default="created_at", pattern=r"^(created_at|height|birth_date)$")


class SearchResponse(BaseModel):
    """搜索接口响应"""
    total: int
    page: int
    page_size: int
    results: list[ProfileResponse]


# ────────────── 自然语言搜索 ──────────────

class NaturalSearchParams(BaseModel):
    """自然语言搜索参数"""
    query: str = Field(min_length=1, max_length=500, description="自然语言描述，如'30岁左右的程序员，喜欢运动'")
    min_score: float = Field(default=0.5, ge=0, le=1.0, description="最低相似度阈值")

    # 可选的结构化预筛选
    gender: Gender | None = None
    age_min: int | None = Field(default=None, ge=18, le=100)
    age_max: int | None = Field(default=None, ge=18, le=100)
    province: str | None = None
    city: str | None = None

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class NaturalSearchResult(BaseModel):
    """自然语言搜索结果"""
    profile: ProfileResponse
    score: float = Field(description="语义相似度分数 (0~1)")


class NaturalSearchResponse(BaseModel):
    """自然语言搜索响应"""
    total: int
    page: int
    page_size: int
    results: list[NaturalSearchResult]
