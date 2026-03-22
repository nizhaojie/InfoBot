"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat, documents
from routers import auth as auth_router
from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表，失败只打印警告不阻断服务
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[WARNING] 数据库建表失败，请检查 MYSQL_URL 配置: {e}")
    yield


app = FastAPI(title="RAG 智能问答系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
