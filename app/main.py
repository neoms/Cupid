from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.database import close_db, connect_db
from app.observability import flush as flush_langfuse
from app.services.embeddings import close_embedding_client
from app.services.query_optimizer import close_optimizer_client
from app.services.reranker import close_rerank_client
from app.api.profiles import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接数据库，关闭时断开"""
    await connect_db()
    yield
    flush_langfuse()
    await close_rerank_client()
    await close_optimizer_client()
    await close_embedding_client()
    await close_db()


app = FastAPI(
    title="Cupid",
    description="婚恋交友用户资料后台服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
