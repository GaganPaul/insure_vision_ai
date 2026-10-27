"""
Virtual Assistant API Routes for InsureVisionAI.
Rule-based conversational assistance for safety, claims, emergency protocols,
and roadside service guidance.
"""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Virtual Assistant"])


@router.post("", response_model=ChatResponse)
def chat_assistant(payload: ChatRequest):
    """
    Interact with the InsureVisionAI safety and roadside virtual assistant.
    Provides immediate action items for accidents, insurance guidance,
    emergency helplines, and towing services.
    """
    response_data = chat_service.answer(payload.message)
    return ChatResponse(**response_data)

