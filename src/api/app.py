from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.student_routes import router as student_router
from api.calculator_routes import router as calculator_router
from api.ai_routes import router as ai_router


app = FastAPI(
    title="Student AI Backend",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://mcp-client-1-ew4q.onrender.com"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(student_router)

app.include_router(calculator_router)

app.include_router(ai_router)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Student AI Backend Running"
    }