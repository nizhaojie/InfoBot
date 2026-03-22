"""
Milvus 向量数据库工具类
负责：Collection 初始化、向量插入、相似度检索、按条件删除
每个用户使用独立的 Collection（命名：{base}_{user_id}）
"""
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from config import settings

VECTOR_DIM = 1536


def get_connection():
    host = settings.milvus_host or "localhost"
    port = settings.milvus_port or 19530
    uri = f"{host}:{port}"
    kwargs = {"alias": "default", "uri": uri}
    if settings.milvus_user:
        kwargs["user"] = settings.milvus_user
        kwargs["password"] = settings.milvus_password
    connections.connect(**kwargs)


def _collection_name(user_id: int) -> str:
    return f"{settings.milvus_collection}_{user_id}"


def init_collection(user_id: int) -> Collection:
    get_connection()
    col_name = _collection_name(user_id)
    if not utility.has_collection(col_name):
        fields = [
            FieldSchema("id", DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema("source", DataType.VARCHAR, max_length=512),
            FieldSchema("chunk_index", DataType.INT64),
            FieldSchema("text", DataType.VARCHAR, max_length=2000),
            FieldSchema("vector", DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
        ]
        col = Collection(col_name, CollectionSchema(fields))
        col.create_index("vector", {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}})
    else:
        col = Collection(col_name)
    col.load()
    return col


def insert_chunks(chunks: list[dict], user_id: int) -> list[str]:
    col = init_collection(user_id)
    ids = [c["id"] for c in chunks]
    col.insert([
        ids,
        [c["source"] for c in chunks],
        [c["chunk_index"] for c in chunks],
        [c["text"][:2000] for c in chunks],
        [c["vector"] for c in chunks],
    ])
    col.flush()
    return ids


def search_similar(vector: list[float], user_id: int, top_k: int = 5) -> list[dict]:
    col = init_collection(user_id)
    results = col.search(
        data=[vector],
        anns_field="vector",
        param={"metric_type": "IP", "params": {"nprobe": 16}},
        limit=top_k,
        output_fields=["id", "source", "chunk_index", "text"],
    )
    return [{
        "id": h.entity.get("id"),
        "source": h.entity.get("source"),
        "chunk_index": h.entity.get("chunk_index"),
        "text": h.entity.get("text"),
        "score": h.score,
    } for h in results[0]]


def list_documents(user_id: int, page: int = 1, page_size: int = 20) -> dict:
    col = init_collection(user_id)
    all_rows = col.query(expr="chunk_index >= 0", output_fields=["source"])
    counts: dict[str, int] = {}
    for row in all_rows:
        s = row["source"]
        counts[s] = counts.get(s, 0) + 1
    sources = sorted(counts.keys())
    paged = sources[(page - 1) * page_size: page * page_size]
    return {"total": len(sources), "page": page, "page_size": page_size,
            "items": [{"source": s, "chunk_count": counts[s]} for s in paged]}


def delete_by_source(source: str, user_id: int):
    col = init_collection(user_id)
    col.delete(f'source == "{source}"')
    col.flush()
