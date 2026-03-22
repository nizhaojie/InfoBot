"""
Embedding 服务
使用 OpenAI 兼容接口调用千问 text-embedding-v3 模型
"""
from openai import OpenAI
from config import settings

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_api_base,
        )
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量文本转向量，返回向量列表"""
    client = get_client()
    # OpenAI 接口单次最多 2048 条，分批处理
    batch_size = 25
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        resp = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        all_vectors.extend([item.embedding for item in resp.data])
    return all_vectors


def embed_query(text: str) -> list[float]:
    """单条查询文本转向量"""
    return embed_texts([text])[0]
