# Cupid

婚恋交友用户资料后台服务，基于 FastAPI + MongoDB Atlas Local 构建。

## 技术栈

- **Web 框架**：FastAPI
- **数据库**：MongoDB（mongodb/mongodb-atlas-local）
- **异步驱动**：Motor
- **包管理**：UV / Python 3.12

## 快速开始

### 1. 启动 MongoDB

```bash
docker compose up -d
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 启动服务

```bash
uv run uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger 接口文档。

## 项目结构

```
Cupid/
├── main.py              # FastAPI 入口，生命周期管理
├── database.py          # MongoDB 连接 & 索引初始化
├── models.py            # Pydantic 数据模型
├── routes.py            # API 路由
├── docker-compose.yml   # MongoDB 容器编排
├── .env                 # 环境变量（不入库）
└── pyproject.toml
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/profiles` | 创建/更新用户资料 |
| `POST` | `/api/profiles/search` | 好友搜索（多条件筛选 + 分页） |
| `GET` | `/health` | 健康检查 |

### 创建/更新资料

```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "小明",
    "gender": "male",
    "birth_date": "1995-06-15",
    "height": 178,
    "province": "广东",
    "city": "深圳",
    "education": "bachelor",
    "occupation": "软件工程师",
    "interests": ["篮球", "旅行", "摄影"],
    "self_intro": "认真找对象"
  }'
```

- 传 `user_id` 则更新已有资料，不传则自动生成新 ID 并创建。

### 好友搜索

```bash
curl -X POST http://localhost:8000/api/profiles/search \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "female",
    "age_min": 25,
    "age_max": 35,
    "city": "深圳",
    "page": 1,
    "page_size": 20
  }'
```

支持的筛选条件：性别、年龄范围、身高范围、省份、城市、学历、婚姻状态、职业（模糊匹配）、兴趣标签。

## 用户资料字段

| 分类 | 字段 | 类型 |
|------|------|------|
| 标识 | `user_id`, `nickname` | string |
| 基本信息 | `gender`, `birth_date`, `height`, `weight` | enum/date/int |
| 所在地 | `province`, `city` | string |
| 学历职业 | `education`, `school`, `occupation`, `industry`, `income_range` | enum/string |
| 外貌 | `body_type` | enum |
| 婚恋 | `marriage_status`, `has_children`, `want_children` | enum/bool |
| 习惯 | `smoking`, `drinking` | bool |
| 介绍 | `self_intro`, `interests`, `avatar_url` | string/list |
| 择偶偏好 | `preference` (性别/年龄/身高/学历/地区) | object |

## 数据库索引

| 索引 | 用途 |
|------|------|
| `user_id` (unique) | 主键查询 |
| `created_at` (desc) | 默认排序 |
| `(province, city)` | 同城搜索 |
| `(gender, birth_date)` | 性别 + 年龄筛选 |
