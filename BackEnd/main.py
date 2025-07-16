from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.routes import videos, chat
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Multimodal RAG: Chat with Videos",
    description="A powerful multimodal RAG system for chatting with videos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FRAMES_DIR, exist_ok=True)
os.makedirs(settings.VECTORS_DIR, exist_ok=True)

# Mount static files for serving uploaded videos and frames
app.mount("/static", StaticFiles(directory="data"), name="static")

# Include routers
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "Multimodal RAG: Chat with Videos API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 