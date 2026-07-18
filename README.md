# Cupid

晓夕成家用户资料查询后台微服务demo，基于 FastAPI + MongoDB Atlas Local 构建，支持字段筛选搜索与 AI 语义搜索（查询优化 → 向量召回 → 百炼重排）。

## 技术栈

- **Web 框架**：FastAPI
- **数据库**：MongoDB（mongodb/mongodb-atlas-local）
- **异步驱动**：Motor
- **向量化**：阿里云百炼 text-embedding-v3（1024 维）
- **语义重排**：阿里云百炼 qwen3-vl-rerank
- **查询优化**：阿里云百炼 qwen-plus（可选，LLM 扩写简短查询）
- **追踪 & 评估**：LangFuse Cloud（tracing + evaluation）
- **包管理**：UV / Python 3.12+

## 快速开始

### 前置要求

- Python >= 3.12（推荐使用 [uv](https://docs.astral.sh/uv/)）
- Docker（用于运行 MongoDB）
- 阿里云百炼 API Key（[控制台获取](https://bailian.console.aliyun.com/)）
- （可选）[LangFuse Cloud](https://cloud.langfuse.com) 账号，用于 AI 调用追踪

### 1. 拉取代码

```bash
git clone <your-repo-url>
cd Cupid
```

### 2. 配置环境变量

项目根目录 `.env` 文件控制全部配置，参考以下模板创建：

```env
# ── MongoDB ──
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your-password
MONGO_DATABASE=cupid

# ── 阿里云百炼（必填） ──
DASHSCOPE_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_DIM=1024
RERANK_MODEL=qwen3-vl-rerank
LLM_MODEL=qwen-plus

# ── LangFuse Cloud（可选，不配置则不上报追踪） ──
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

> `.env` 中的 MongoDB 凭证会被 `docker-compose.yml` 读取，因此需要先配置好再启动 Docker。

### 3. 启动 MongoDB

使用项目根目录的 `docker-compose.yml` 一键启动：

```bash
docker compose up -d
```

等待 MongoDB 就绪（healthcheck passing）：

```bash
docker ps --filter name=cupid-mongodb
# STATUS 列应显示 "(healthy)"
```

### 4. 安装依赖

```bash
uv sync
```

### 5. 启动服务

```bash
uv run uvicorn app.main:app --reload --port 8000
```

看到以下日志表示启动成功：

```
✓ MongoDB 已连接 (cupid)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问 http://localhost:8000/docs 查看 Swagger 接口文档（含完整字段说明和示例数据）。

### 6. 导入测试数据（可选）

```bash
uv run python test/generate_users.py   # 生成 200 条随机用户，输出到 user_data.json
uv run python test/import_users.py     # 批量导入到服务（自动向量化）
```

### 7. 验证全链路

一切就绪后，发一个完整的语义搜索请求验证所有环节：

```bash
curl -X POST http://localhost:8000/api/profiles/search/natural \
  -H "Content-Type: application/json" \
  -d '{
    "query": "30岁左右的程序员，喜欢运动",
    "use_query_optimization": true,
    "use_rerank": true,
    "page": 1,
    "page_size": 5
  }'
```

如果配置了 LangFuse，登录 [cloud.langfuse.com](https://cloud.langfuse.com) 即可看到这次请求的完整追踪链路：

```
natural_search (总耗时)
├── optimize_query (LLM 查询优化)
├── embed_text      (查询向量化)
└── rerank_documents (AI 精排)
```

### 常见问题

| 现象 | 排查 |
|------|------|
| 服务启动报 MongoDB 连接失败 | 确认 `docker compose up -d` 已执行且容器 healthy |
| 自然语言搜索返回空 | 检查 `DASHSCOPE_API_KEY` 是否正确，是否有导入数据 |
| LangFuse 控制台无数据 | 确认 `.env` 中三个 `LANGFUSE_*` 均正确配置 |
| Docker 端口冲突 | 修改 `.env` 中 `MONGO_PORT` 为其他端口 |

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
│   ├── observability/
│   │   ├── __init__.py          # 可观测性统一入口
│   │   └── langfuse/
│   │       └── client.py        # LangFuse 客户端 & flush 管理
│   └── services/
│       ├── __init__.py
│       ├── database.py          # MongoDB 连接 & 索引初始化
│       ├── embeddings.py        # 百炼向量化服务（含 @observe）
│       ├── query_optimizer.py   # 百炼 LLM 查询优化（含 @observe）
│       └── reranker.py          # 百炼重排序服务（含 @observe）
├── docker/
│   ├── mongodb-docker-compose.yml
│   └── langfuse-docker-compose.yml  # LangFuse 本地部署（可选）
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
    "query": "找个程序员",
    "min_score": 0.5,
    "use_query_optimization": true,
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
用户描述 → [可选: LLM 查询优化] → Embedding → 余弦相似度粗召回 top-K
                                                    ↓
                                          百炼 qwen3-vl-rerank 精排
                                                    ↓
                                         按 relevance_score 降序分页返回
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 自然语言描述（1-500字），越详细越精准 | 必填 |
| `use_query_optimization` | 是否用 LLM 扩写简短查询（如"找个程序员"→展开为丰富描述） | false |
| `min_score` | 余弦相似度阈值(0~1)，低于此值的候选丢弃 | 0.5 |
| `use_rerank` | 是否启用百炼 AI 重排序，关闭则仅用向量相似度 | true |
| `rerank_top_k` | 粗召回数量送入精排，上限100 | 50 |
| `gender/age_min/age_max/province/city` | 可选的结构化预筛选 | - |
| `page/page_size` | 分页 | 1 / 20 |

> **查询优化**：当用户输入很短（如"找个程序员"）时，开启 `use_query_optimization` 会让百炼 qwen-plus 将简短描述扩写为包含职业特征、生活场景等维度的丰富语义文本，显著提升匹配精度。优化后的文本会通过 `optimized_query` 字段返回。

返回结果中 `score` 越接近 1 越匹配。启用重排时为百炼 `relevance_score`，未启用时为余弦相似度。重排失败时自动回退到余弦相似度，不影响服务可用性。

## 可观测性 & AI 调用追踪

项目集成了 [LangFuse Cloud](https://cloud.langfuse.com) 用于 AI 链路追踪和评估。

- 在 `.env` 中配置 `LANGFUSE_*` 后，每次语义搜索自动上报 trace
- 追踪结构：`natural_search → embed_text / optimize_query / rerank_documents`
- `@observe()` 装饰器嵌入业务代码（services 层），客户端管理逻辑统一放在 `app/observability/`
- 服务关闭时自动 flush 确保数据不丢失

```text
app/observability/
├── __init__.py              # 统一导出
└── langfuse/
    └── client.py            # LangFuse 客户端初始化 & flush
```

未来评估相关逻辑（deepeval 等）也将放在 `observability/` 目录下。

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
