from fastapi import APIRouter
from pydantic import BaseModel

from assistant_service import StudentAIAssistant


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
)


# ------------------------------------------------------------
# AI Assistant instance
# ------------------------------------------------------------

assistant = StudentAIAssistant()


# ------------------------------------------------------------
# Request model
# ------------------------------------------------------------

class AIRequest(BaseModel):
    message: str


# ------------------------------------------------------------
# Chat endpoint
# ------------------------------------------------------------

@router.post("/chat")
async def ai_chat(request: AIRequest):

    response = await assistant.chat(
        request.message
    )

    return {
        "response": response
    }


# ------------------------------------------------------------
# Reset conversation
# ------------------------------------------------------------

@router.post("/reset")
async def reset_ai_conversation():

    assistant.reset_conversation()

    return {
        "message": "AI conversation reset successfully"
    }