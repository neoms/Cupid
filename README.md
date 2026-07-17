# Cupid

婚恋交友用户资料后台服务，基于 FastAPI + MongoDB Atlas Local 构建，支持字段筛选搜索与 AI 语义搜索（向量召回 + 百炼重排）。

## 技术栈

- **Web 框架**：FastAPI
- **数据库**：MongoDB（mongodb/mongodb-atlas-local）
- **异步驱动**：Motor
- **向量化**：阿里云百炼 text-embedding-v3（1024 维）
- **语义重排**：阿里云百炼 qwen3-vl-rerank
- **包管理**：UV / Python 3.12+

## 快速开始

### 1. 启动 MongoDB

```bash
docker compose up -d
```

### 2. 配置环境变量

编辑 `.env`，填入百炼 API Key：

```env
DASHSCOPE_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_DIM=1024
RERANK_MODEL=qwen3-vl-rerank
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 启动服务

```bash
uv run uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger 接口文档（含完整字段说明和示例数据）。

### 5. 导入测试数据（可选）

```bash
uv run python test/generate_users.py
uv run python test/import_users.py
```

## 项目结构

```
Cupid/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口，生命周期管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── profiles.py          # API 路由（资料创建、搜索）
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic 数据模型（请求/响应）
│   └── services/
│       ├── __init__.py
│       ├── database.py          # MongoDB 连接 & 索引初始化
│       ├── embeddings.py        # 百炼向量化服务
│       └── reranker.py          # 百炼重排序服务
├── test/
│   ├── generate_users.py        # 生成测试用户数据
│   ├── import_users.py          # 批量导入到服务
│   └── user_data.json           # 测试数据
├── .env                         # 环境变量
├── docker-compose.yml           # MongoDB 容器编排
├── pyproject.toml
└── uv.lock
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/profiles` | 创建/更新用户资料（自动向量化） |
| `POST` | `/api/profiles/search` | 结构化字段筛选搜索 |
| `POST` | `/api/profiles/search/natural` | 自然语言 AI 语义搜索（向量+重排） |
| `GET` | `/health` | 健康检查 |

所有接口的字段说明、可选值、示例数据均可在 `/docs` 页面直接查看。

### 创建/更新资料

```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "小明",
    "gender": "男",
    "birth_date": "1995-06-15",
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
    "has_children": false,
    "smoking": false,
    "drinking": false,
    "self_intro": "热爱生活，喜欢运动旅行，期待遇见有趣的你",
    "interests": ["跑步", "电影", "旅行"],
    "preference": {
      "gender": "女",
      "age_min": 24,
      "age_max": 32,
      "height_min": 160,
      "height_max": 172
    }
  }'
```

- 传 `user_id` 则更新已有资料，不传则自动生成。
- 创建/更新时自动将所有字段拼接为文本描述并向量化，失败不影响资料写入。

### 结构化字段筛选搜索

```bash
curl -X POST http://localhost:8000/api/profiles/search \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "女",
    "age_min": 25,
    "age_max": 35,
    "city": "深圳",
    "page": 1,
    "page_size": 20,
    "sort_by": "created_at"
  }'
```

支持筛选：性别、年龄范围、身高范围、省份、城市、学历、婚姻状态、职业（模糊匹配）、兴趣标签。所有条件可选，多条件 AND 关系。

### 自然语言 AI 语义搜索

```bash
curl -X POST http://localhost:8000/api/profiles/search/natural \
  -H "Content-Type: application/json" \
  -d '{
    "query": "30岁左右的程序员，喜欢运动和旅行，性格开朗",
    "min_score": 0.5,
    "use_rerank": true,
    "rerank_top_k": 50,
    "gender": "女",
    "age_min": 25,
    "age_max": 35,
    "city": "深圳",
    "page": 1,
    "page_size": 20
  }'
```

**搜索流程**：

```
用户描述 → 百炼 Embedding 向量化 → MongoDB 余弦相似度粗召回 top-K
                                              ↓
                                    百炼 qwen3-vl-rerank 精排
                                              ↓
                                   按 relevance_score 降序分页返回
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 自然语言描述（1-500字），越详细越精准 | 必填 |
| `min_score` | 余弦相似度阈值(0~1)，低于此值的候选丢弃 | 0.5 |
| `use_rerank` | 是否启用百炼 AI 重排序，关闭则仅用向量相似度 | true |
| `rerank_top_k` | 粗召回数量送入精排，上限100 | 50 |
| `gender/age_min/age_max/province/city` | 可选的结构化预筛选 | - |
| `page/page_size` | 分页 | 1 / 20 |

返回结果中 `score` 越接近 1 越匹配。启用重排时为百炼 `relevance_score`，未启用时为余弦相似度。重排失败时自动回退到余弦相似度，不影响服务可用性。

## 用户资料字段

| 分类 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 标识 | `user_id`, `nickname` | string | 业务ID（16位） / 昵称 |
| 基本信息 | `gender`, `birth_date`, `height`, `weight` | enum/date/int/int | 性别 / 出生日期 / 身高(cm) / 体重(kg) |
| 所在地 | `province`, `city` | string | 省份 / 城市 |
| 学历职业 | `education`, `school`, `occupation`, `industry`, `income_range` | enum/string | 学历 / 院校 / 职业 / 行业 / 年收入 |
| 外貌 | `body_type` | enum | 偏瘦/匀称/运动型/丰满 |
| 婚恋 | `marriage_status`, `has_children`, `want_children` | enum/bool/bool | 婚姻状况 / 有无子女 / 生育意愿 |
| 习惯 | `smoking`, `drinking` | bool/null | 是否吸烟/饮酒，null=未知 |
| 介绍 | `self_intro`, `interests`, `avatar_url` | string/list/string | 自我介绍 / 兴趣标签 / 头像 |
| 择偶偏好 | `preference` | object | 期望对方的性别/年龄/身高/学历/地区/婚姻状态 |
| 系统 | `embedding`, `created_at` | float[]/datetime | 1024维向量 / 创建时间 |

## 数据库索引

| 索引 | 用途 |
|------|------|
| `user_id` (unique) | 主键查询 & upsert |
| `created_at` (desc) | 按注册时间排序 |
| `(province, city)` | 同城搜索 |
| `(gender, birth_date)` | 性别 + 年龄范围筛选 |
