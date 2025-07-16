from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Multimodal RAG: Chat with Videos"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # File Storage
    UPLOAD_DIR: str = "./data/videos"
    FRAMES_DIR: str = "./data/frames"
    VECTORS_DIR: str = "./data/vectors"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Vector Database
    CHROMA_DB_PATH: str = "./data/vectors"
    
    # Video Processing
    FRAME_EXTRACTION_RATE: int = 1  # Extract 1 frame per second
    MAX_FRAMES_PER_VIDEO: int = 300  # Maximum frames to extract
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-4-vision-preview"  # or "claude-3-sonnet-20240229"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 