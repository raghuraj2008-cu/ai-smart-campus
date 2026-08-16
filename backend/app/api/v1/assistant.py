from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.campus_rag import campus_rag

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def ask_assistant(req: QueryRequest):
    result = await campus_rag.query(req.query)
    return result