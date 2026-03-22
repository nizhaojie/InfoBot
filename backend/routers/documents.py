from fastapi import APIRouter, Query, Depends
from models import DocumentDeleteRequest, DocumentListResponse, DocumentItem
from services.vectorstore import list_documents, delete_by_source
from auth import get_current_user
from database import User

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    result = list_documents(user_id=current_user.id, page=page, page_size=page_size)
    items = [DocumentItem(source=i["source"], chunk_count=i["chunk_count"]) for i in result["items"]]
    return DocumentListResponse(total=result["total"], page=result["page"], page_size=result["page_size"], items=items)


@router.delete("/documents")
def delete_documents(req: DocumentDeleteRequest, current_user: User = Depends(get_current_user)):
    for source in req.sources:
        delete_by_source(source, user_id=current_user.id)
    return {"message": "删除成功"}
