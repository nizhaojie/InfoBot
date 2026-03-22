"""
数据库连接与 User 模型
使用 SQLAlchemy 同步引擎连接远程 MySQL
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from config import settings

engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,       # 自动检测断开的连接
    pool_recycle=3600,        # 每小时回收连接，防止 MySQL 8h 超时断开
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    """FastAPI 依赖注入：提供数据库 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
