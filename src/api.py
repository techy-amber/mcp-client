from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from assistant_service import StudentAIAssistant


# ============================================================
# Our AI Assistant
# ============================================================

assistant = StudentAIAssistant()


# ============================================================
# Start/stop assistant together with FastAPI
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # FastAPI start hote hi MCP servers bhi start honge
    await assistant.start()

    yield

    # FastAPI band hote hi MCP connections safely close honge
    await assistant.stop()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Student AI Analytics API",
    description="AI-powered student analytics using Qwen, MCP and MySQL",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Request structure
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# Basic health endpoint
# ============================================================

@app.get("/")
async def home():

    return {
        "status": "running",
        "message": "Student AI Analytics API is running"
    }


# ============================================================
# AI Chat endpoint
# ============================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):

    response = await assistant.chat(request.message)

    return {
        "response": response
    }


# ============================================================
# Reset conversation
# ============================================================

@app.post("/api/reset")
async def reset():

    assistant.reset_conversation()

    return {
        "message": "Conversation reset successfully"
    }