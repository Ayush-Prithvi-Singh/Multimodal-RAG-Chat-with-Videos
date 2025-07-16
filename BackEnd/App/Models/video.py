from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class VideoInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    frame_count: Optional[int] = None
    transcript: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VideoFrame(BaseModel):
    id: str
    video_id: str
    timestamp: float
    frame_number: int
    image_path: str
    description: Optional[str] = None
    objects: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    scene_description: Optional[str] = None

class ChatMessage(BaseModel):
    id: str
    video_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    context_frames: List[str] = Field(default_factory=list)  # Frame IDs used for context
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    video_id: str
    message: str
    use_vision: bool = True
    max_context_frames: int = 5

class ChatResponse(BaseModel):
    message_id: str
    response: str
    context_frames: List[VideoFrame] = Field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0

class VideoUploadResponse(BaseModel):
    video_id: str
    status: VideoStatus
    message: str 