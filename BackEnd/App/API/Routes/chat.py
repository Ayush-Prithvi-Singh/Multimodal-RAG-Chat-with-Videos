from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime
from typing import List

from app.models.video import ChatRequest, ChatResponse, ChatMessage, VideoFrame
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.core.config import settings

router = APIRouter()
rag_service = RAGService()
llm_service = LLMService()

# In-memory storage for chat messages (in production, use a proper database)
chat_messages_db = {}

@router.post("/", response_model=ChatResponse)
async def chat_with_video(request: ChatRequest):
    """Chat with a video using RAG-powered responses"""
    
    # Get relevant context from RAG system
    context = await rag_service.get_context_for_chat(
        request.message, 
        request.video_id, 
        request.max_context_frames
    )
    
    # Generate response using LLM
    response = await llm_service.generate_response(
        request.message,
        context,
        use_vision=request.use_vision
    )
    
    # Create chat message
    message_id = str(uuid.uuid4())
    chat_message = ChatMessage(
        id=message_id,
        video_id=request.video_id,
        role="user",
        content=request.message,
        timestamp=datetime.now(),
        context_frames=[frame["frame_id"] for frame in context["frames"]]
    )
    
    # Store user message
    if request.video_id not in chat_messages_db:
        chat_messages_db[request.video_id] = []
    chat_messages_db[request.video_id].append(chat_message)
    
    # Add to RAG system for future context
    await rag_service.add_chat_message(chat_message)
    
    # Create assistant message
    assistant_message = ChatMessage(
        id=str(uuid.uuid4()),
        video_id=request.video_id,
        role="assistant",
        content=response["content"],
        timestamp=datetime.now(),
        context_frames=[frame["frame_id"] for frame in context["frames"]]
    )
    
    # Store assistant message
    chat_messages_db[request.video_id].append(assistant_message)
    
    # Convert context frames to VideoFrame objects for response
    context_frames = []
    for frame_data in context["frames"]:
        frame = VideoFrame(
            id=frame_data["frame_id"],
            video_id=request.video_id,
            timestamp=frame_data["timestamp"],
            frame_number=0,  # This would be loaded from database
            image_path=frame_data["image_path"],
            description=frame_data["description"]
        )
        context_frames.append(frame)
    
    return ChatResponse(
        message_id=assistant_message.id,
        response=response["content"],
        context_frames=context_frames,
        confidence=response.get("confidence", 0.0),
        processing_time=response.get("processing_time", 0.0)
    )

@router.get("/{video_id}/history")
async def get_chat_history(video_id: str):
    """Get chat history for a video"""
    if video_id not in chat_messages_db:
        return {"messages": []}
    
    return {"messages": chat_messages_db[video_id]}

@router.delete("/{video_id}/history")
async def clear_chat_history(video_id: str):
    """Clear chat history for a video"""
    if video_id in chat_messages_db:
        chat_messages_db[video_id] = []
    
    return {"message": "Chat history cleared"} 