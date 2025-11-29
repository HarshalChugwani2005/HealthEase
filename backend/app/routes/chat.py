from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.services.ai_service import ai_service
from app.middleware.auth import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send message to AI Health Assistant
    """
    try:
        response = await ai_service.get_health_assistant_response(
            request.message,
            [msg.dict() for msg in request.history]
        )
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
