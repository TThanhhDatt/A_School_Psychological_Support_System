from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chatbot_router import chatbot_router

app = FastAPI(
    title="Therapy bot API",
    description="API for managing therapy bot for student in university",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc"  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS
    allow_headers=["Content-Type", "Action"],  # Allow custom Action header
)

app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot routers"])

@app.get("/")
async def root():
    return {"message": "Welcome to Therapy bot "}