"""
文件/URL 上传处理路由
POST /api/upload
支持：PDF、TXT、Markdown 文件上传，或 URL 抓取
"""
import uuid
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader, WebBaseLoader
from services.embedder import embed_texts
from services.vectorstore import insert_chunks
from auth import get_current_user
from database import User
from config import settings

router = APIRouter()

# 文本分割器
splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)


def _load_file(path: str, filename: str) -> list:
    """根据文件扩展名选择对应 Loader"""
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        loader = PyPDFLoader(path)
    elif ext in ("md", "markdown"):
        loader = UnstructuredMarkdownLoader(path)
    else:
        loader = TextLoader(path, encoding="utf-8")
    return loader.load()


@router.post("/upload")
async def upload(
    file: UploadFile = File(None),
    url: str = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    上传文件或 URL，处理后存入 Milvus。
    - file: 上传的文件（PDF/TXT/MD）
    - url: 网页地址
    """
    if not file and not url:
        raise HTTPException(400, "需要提供 file 或 url 参数")

    if file:
        # 保存到临时文件
        suffix = "." + file.filename.rsplit(".", 1)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            docs = _load_file(tmp_path, file.filename)
            source = file.filename
        finally:
            os.unlink(tmp_path)
    else:
        # 抓取网页
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            source = url
        except Exception as e:
            raise HTTPException(400, f"URL 抓取失败: {e}")

    # 文本分割
    chunks = splitter.split_documents(docs)
    if not chunks:
        raise HTTPException(400, "未能提取到有效文本内容")

    # 向量化
    texts = [c.page_content for c in chunks]
    vectors = embed_texts(texts)

    # 构造插入数据
    records = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        records.append({
            "id": str(uuid.uuid4()).replace("-", "")[:32],
            "source": source,
            "chunk_index": i,
            "text": chunk.page_content,
            "vector": vector,
        })

    insert_chunks(records, user_id=current_user.id)
    return {"message": f"成功导入 {len(records)} 个文本块", "source": source}
