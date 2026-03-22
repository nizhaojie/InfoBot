"""Pydantic 请求/响应模型"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"


class DocumentDeleteRequest(BaseModel):
    sources: list[str]  # 按文件名/URL 列表删除


class DocumentItem(BaseModel):
    source: str    # 文件名或 URL
    chunk_count: int  # 该来源的向量块数量


class DocumentListResponse(BaseModel):
    total: int   # 来源总数
    page: int
    page_size: int
    items: list[DocumentItem]
