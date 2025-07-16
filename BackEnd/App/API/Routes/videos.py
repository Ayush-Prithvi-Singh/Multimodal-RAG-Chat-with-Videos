from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import uuid
import aiofiles
from typing import List

from app.models.video import VideoInfo, VideoUploadResponse, VideoStatus
from app.services.video_processor import VideoProcessor
from app.services.rag_service import RAGService
from app.core.config import settings

router = APIRouter()
video_processor = VideoProcessor()
rag_service = RAGService()

# In-memory storage for demo (in production, use a proper database)
videos_db = {}
frames_db = {}

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a video file"""
    
    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Save video file
    video_filename = f"{video_id}_{file.filename}"
    video_path = os.path.join(settings.UPLOAD_DIR, video_filename)
    
    async with aiofiles.open(video_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create initial video info
    video_info = VideoInfo(
        id=video_id,
        filename=video_filename,
        original_filename=file.filename or "unknown",
        file_size=file.size,
        status=VideoStatus.UPLOADING,
        uploaded_at=uuid.uuid4().time  # This should be datetime.now()
    )
    
    # Store in memory (in production, save to database)
    videos_db[video_id] = video_info
    
    # Process video in background
    background_tasks.add_task(process_video_background, video_id, video_path)
    
    return VideoUploadResponse(
        video_id=video_id,
        status=VideoStatus.UPLOADING,
        message="Video uploaded successfully. Processing in background."
    )

@router.get("/{video_id}", response_model=VideoInfo)
async def get_video_info(video_id: str):
    """Get video information"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return videos_db[video_id]

@router.get("/{video_id}/frames")
async def get_video_frames(video_id: str):
    """Get video frames"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # In a real implementation, this would load from database
    # For now, return empty list
    return {"frames": []}

@router.get("/{video_id}/transcript")
async def get_video_transcript(video_id: str):
    """Get video transcript"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_info = videos_db[video_id]
    return {"transcript": video_info.transcript}

@router.get("/{video_id}/stream")
async def stream_video(video_id: str):
    """Stream video file"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_info = videos_db[video_id]
    video_path = os.path.join(settings.UPLOAD_DIR, video_info.filename)
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=video_info.original_filename
    )

async def process_video_background(video_id: str, video_path: str):
    """Background task to process video"""
    try:
        # Update status to processing
        if video_id in videos_db:
            videos_db[video_id].status = VideoStatus.PROCESSING
        
        # Process video
        video_info = await video_processor.process_video(video_path, video_id)
        
        # Update stored video info
        videos_db[video_id] = video_info
        
        # Add to RAG system
        frames = await video_processor.get_video_frames(video_id)
        await rag_service.add_video_content(video_info, frames)
        
    except Exception as e:
        # Update status to error
        if video_id in videos_db:
            videos_db[video_id].status = VideoStatus.ERROR
            videos_db[video_id].metadata["error"] = str(e) 