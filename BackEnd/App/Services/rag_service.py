import chromadb
import uuid
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import json

from app.models.video import VideoFrame, VideoInfo, ChatMessage
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Create collections
        self.frames_collection = self.client.get_or_create_collection(
            name="video_frames",
            metadata={"hnsw:space": "cosine"}
        )
        self.transcripts_collection = self.client.get_or_create_collection(
            name="video_transcripts",
            metadata={"hnsw:space": "cosine"}
        )
        self.chat_collection = self.client.get_or_create_collection(
            name="chat_history",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_video_content(self, video_info: VideoInfo, frames: List[VideoFrame]):
        """Add video content to vector database"""
        # Add transcript
        if video_info.transcript:
            await self._add_transcript(video_info)
        
        # Add frames
        await self._add_frames(frames)
    
    async def _add_transcript(self, video_info: VideoInfo):
        """Add video transcript to vector database"""
        if not video_info.transcript:
            return
            
        transcript_chunks = self._chunk_transcript(video_info.transcript)
        
        for i, chunk in enumerate(transcript_chunks):
            chunk_id = f"{video_info.id}_transcript_{i}"
            embedding = self.embedding_model.encode(chunk).tolist()
            
            self.transcripts_collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "video_id": video_info.id,
                    "chunk_index": i,
                    "type": "transcript",
                    "timestamp": video_info.uploaded_at.isoformat()
                }],
                ids=[chunk_id]
            )
    
    async def _add_frames(self, frames: List[VideoFrame]):
        """Add video frames to vector database"""
        for frame in frames:
            # Create frame description
            frame_text = self._create_frame_description(frame)
            embedding = self.embedding_model.encode(frame_text).tolist()
            
            self.frames_collection.add(
                embeddings=[embedding],
                documents=[frame_text],
                metadatas=[{
                    "video_id": frame.video_id,
                    "frame_id": frame.id,
                    "timestamp": frame.timestamp,
                    "frame_number": frame.frame_number,
                    "image_path": frame.image_path,
                    "type": "frame",
                    "objects": json.dumps(frame.objects),
                    "actions": json.dumps(frame.actions),
                    "scene_description": frame.scene_description or ""
                }],
                ids=[frame.id]
            )
    
    def _chunk_transcript(self, transcript: str, chunk_size: int = 500) -> List[str]:
        """Split transcript into chunks"""
        words = transcript.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _create_frame_description(self, frame: VideoFrame) -> str:
        """Create text description of frame for embedding"""
        description_parts = []
        
        if frame.scene_description:
            description_parts.append(f"Scene: {frame.scene_description}")
        
        if frame.objects:
            description_parts.append(f"Objects: {', '.join(frame.objects)}")
        
        if frame.actions:
            description_parts.append(f"Actions: {', '.join(frame.actions)}")
        
        description_parts.append(f"Timestamp: {frame.timestamp:.2f} seconds")
        
        return " | ".join(description_parts)
    
    async def search_relevant_content(self, query: str, video_id: str, 
                                    max_results: int = 10) -> Dict[str, Any]:
        """Search for relevant content in video"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in frames
        frame_results = self.frames_collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            where={"video_id": video_id}
        )
        
        # Search in transcript
        transcript_results = self.transcripts_collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            where={"video_id": video_id}
        )
        
        return {
            "frames": frame_results,
            "transcript": transcript_results
        }
    
    async def get_context_for_chat(self, query: str, video_id: str, 
                                  max_frames: int = 5) -> Dict[str, Any]:
        """Get relevant context for chat response"""
        search_results = await self.search_relevant_content(query, video_id, max_frames * 2)
        
        # Process frame results
        relevant_frames = []
        if search_results["frames"]["ids"]:
            for i, frame_id in enumerate(search_results["frames"]["ids"][0]):
                metadata = search_results["frames"]["metadatas"][0][i]
                distance = search_results["frames"]["distances"][0][i]
                
                relevant_frames.append({
                    "frame_id": frame_id,
                    "image_path": metadata["image_path"],
                    "timestamp": metadata["timestamp"],
                    "description": search_results["frames"]["documents"][0][i],
                    "relevance_score": 1 - distance  # Convert distance to similarity
                })
        
        # Sort by relevance and take top frames
        relevant_frames.sort(key=lambda x: x["relevance_score"], reverse=True)
        relevant_frames = relevant_frames[:max_frames]
        
        # Process transcript results
        relevant_transcript = ""
        if search_results["transcript"]["documents"]:
            transcript_chunks = search_results["transcript"]["documents"][0]
            relevant_transcript = " ".join(transcript_chunks)
        
        return {
            "frames": relevant_frames,
            "transcript": relevant_transcript
        }
    
    async def add_chat_message(self, message: ChatMessage):
        """Add chat message to vector database for context"""
        embedding = self.embedding_model.encode(message.content).tolist()
        
        self.chat_collection.add(
            embeddings=[embedding],
            documents=[message.content],
            metadatas=[{
                "video_id": message.video_id,
                "message_id": message.id,
                "role": message.role,
                "timestamp": message.timestamp.isoformat(),
                "context_frames": json.dumps(message.context_frames)
            }],
            ids=[message.id]
        ) 