"""
对话路由 - SSE 流式输出
POST /api/chat
使用 LangChain RAG 链：检索 -> 构造 Prompt -> LLM 流式生成
"""
import json
import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from models import ChatRequest
from services.embedder import embed_query
from services.vectorstore import search_similar
from auth import get_current_user
from database import User
from config import settings

router = APIRouter()

# 会话历史存储（内存，生产环境可替换为 Redis）
_session_histories: dict[str, list] = {}

# LLM 实例（streaming=True 启用流式）
llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base,
    model=settings.openai_model,
    streaming=True,
    temperature=0.7,
)

# RAG Prompt 模板
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能问答助手。请根据以下检索到的上下文内容回答用户问题。
如果上下文中没有相关信息，请如实告知，不要编造答案。

上下文：
{context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])


async def _stream_rag(question: str, session_id: str, user_id: int):
    """
    RAG 流式生成器：
    1. 向量化问题
    2. 检索 Top-5 相关块
    3. 构造 Prompt
    4. LLM 流式输出，每个 token 以 SSE 格式发送
    """
    # 1. 检索
    q_vector = embed_query(question)
    hits = search_similar(q_vector, user_id=user_id, top_k=5)
    context = "\n\n".join([f"[{h['source']}] {h['text']}" for h in hits])

    # 2. 获取历史（key 含 user_id，确保不同用户完全隔离）
    key = f"{user_id}:{session_id}"
    history = _session_histories.get(key, [])

    # 3. 构造消息
    messages = RAG_PROMPT.format_messages(
        context=context,
        history=history,
        question=question,
    )

    # 4. 流式生成
    full_response = ""
    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            full_response += token
            # SSE 格式：data: {...}\n\n
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)  # 让出事件循环，确保实时推送

    # 5. 更新历史
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=full_response))
    # 保留最近 20 条消息（10 轮对话）
    _session_histories[key] = history[-20:]

    # 发送结束信号
    yield f"data: {json.dumps({'done': True})}\n\n"


@router.post("/chat")
async def chat(req: ChatRequest, current_user: User = Depends(get_current_user)):
    """流式对话接口，返回 SSE 响应"""
    return StreamingResponse(
        _stream_rag(req.question, req.session_id, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )
