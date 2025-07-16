import cv2
import os
import uuid
import whisper
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from app.models.video import VideoInfo, VideoFrame, VideoStatus
from app.core.config import settings

class VideoProcessor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        
    async def process_video(self, video_path: str, video_id: str) -> VideoInfo:
        """Process uploaded video: extract frames, transcribe audio, analyze content"""
        try:
            # Get video metadata
            video_info = await self._extract_video_metadata(video_path, video_id)
            
            # Extract frames
            frames = await self._extract_frames(video_path, video_id)
            video_info.frame_count = len(frames)
            
            # Transcribe audio
            transcript = await self._transcribe_audio(video_path)
            video_info.transcript = transcript
            
            # Analyze frames
            await self._analyze_frames(frames)
            
            # Update status
            video_info.status = VideoStatus.READY
            video_info.processed_at = datetime.now()
            
            return video_info
            
        except Exception as e:
            # Update status to error
            video_info = VideoInfo(
                id=video_id,
                filename=os.path.basename(video_path),
                original_filename=os.path.basename(video_path),
                file_size=os.path.getsize(video_path),
                status=VideoStatus.ERROR,
                uploaded_at=datetime.now(),
                metadata={"error": str(e)}
            )
            return video_info
    
    async def _extract_video_metadata(self, video_path: str, video_id: str) -> VideoInfo:
        """Extract basic video metadata"""
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resolution = f"{width}x{height}"
        
        cap.release()
        
        return VideoInfo(
            id=video_id,
            filename=os.path.basename(video_path),
            original_filename=os.path.basename(video_path),
            file_size=os.path.getsize(video_path),
            duration=duration,
            fps=fps,
            resolution=resolution,
            status=VideoStatus.PROCESSING,
            uploaded_at=datetime.now()
        )
    
    async def _extract_frames(self, video_path: str, video_id: str) -> List[VideoFrame]:
        """Extract frames from video at specified intervals"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * settings.FRAME_EXTRACTION_RATE)
        frame_count = 0
        extracted_count = 0
        
        # Create frames directory for this video
        video_frames_dir = os.path.join(settings.FRAMES_DIR, video_id)
        os.makedirs(video_frames_dir, exist_ok=True)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0 and extracted_count < settings.MAX_FRAMES_PER_VIDEO:
                # Save frame
                frame_filename = f"frame_{extracted_count:04d}.jpg"
                frame_path = os.path.join(video_frames_dir, frame_filename)
                cv2.imwrite(frame_path, frame)
                
                # Create frame object
                timestamp = frame_count / fps
                frame_obj = VideoFrame(
                    id=str(uuid.uuid4()),
                    video_id=video_id,
                    timestamp=timestamp,
                    frame_number=extracted_count,
                    image_path=f"/static/frames/{video_id}/{frame_filename}"
                )
                frames.append(frame_obj)
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        return frames
    
    async def _transcribe_audio(self, video_path: str) -> str:
        """Transcribe audio from video using Whisper"""
        try:
            result = self.whisper_model.transcribe(video_path)
            return result["text"]
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    async def _analyze_frames(self, frames: List[VideoFrame]):
        """Analyze frames for objects, actions, and scene descriptions"""
        # This would integrate with vision models like GPT-4 Vision or CLIP
        # For now, we'll add placeholder analysis
        for frame in frames:
            # Placeholder analysis - in real implementation, this would call vision APIs
            frame.objects = ["object1", "object2"]  # Placeholder
            frame.actions = ["action1"]  # Placeholder
            frame.scene_description = "A scene with various objects and activities"  # Placeholder
    
    async def get_video_frames(self, video_id: str) -> List[VideoFrame]:
        """Get all frames for a video"""
        # In a real implementation, this would load from database
        # For now, return empty list
        return []
    
    async def get_video_info(self, video_id: str) -> Optional[VideoInfo]:
        """Get video information"""
        # In a real implementation, this would load from database
        # For now, return None
        return None 