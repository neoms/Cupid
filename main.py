from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import close_db, connect_db
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接数据库，关闭时断开"""
    await connect_db()
    yield
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
