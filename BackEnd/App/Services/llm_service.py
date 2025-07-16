import openai
import anthropic
import time
import base64
from typing import Dict, Any, List, Optional
import os

from app.core.config import settings

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Only initialize clients if API keys are provided and not placeholder values
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_key":
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        
        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_anthropic_key":
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Anthropic client: {e}")
    
    async def generate_response(self, message: str, context: Dict[str, Any], 
                              use_vision: bool = True) -> Dict[str, Any]:
        """Generate response using LLM with multimodal context"""
        start_time = time.time()
        
        try:
            if use_vision and context.get("frames"):
                # Use vision-capable model
                if self.openai_client and "gpt-4" in settings.LLM_MODEL:
                    response = await self._generate_openai_vision_response(message, context)
                elif self.anthropic_client:
                    response = await self._generate_anthropic_vision_response(message, context)
                else:
                    response = await self._generate_text_only_response(message, context)
            else:
                # Use text-only model
                response = await self._generate_text_only_response(message, context)
            
            processing_time = time.time() - start_time
            response["processing_time"] = processing_time
            
            return response
            
        except Exception as e:
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "confidence": 0.0,
                "processing_time": time.time() - start_time
            }
    
    async def _generate_openai_vision_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using OpenAI GPT-4 Vision"""
        if not self.openai_client:
            raise Exception("OpenAI client not configured")
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that can analyze videos and answer questions about them. 
                You have access to video frames and transcript information. 
                Provide detailed, accurate responses based on the visual and audio content you can see."""
            }
        ]
        
        # Add context information
        if context.get("transcript"):
            messages.append({
                "role": "user",
                "content": f"Video transcript: {context['transcript']}"
            })
        
        # Add visual content
        content_parts = [message]
        for frame in context.get("frames", []):
            try:
                # Read and encode image
                image_path = frame["image_path"].replace("/static/", "./data/")
                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}",
                            "detail": "high"
                        }
                    })
            except Exception as e:
                print(f"Error processing image {frame['image_path']}: {e}")
        
        messages.append({
            "role": "user",
            "content": content_parts
        })
        
        # Generate response
        response = self.openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return {
            "content": response.choices[0].message.content,
            "confidence": 0.9
        }
    
    async def _generate_anthropic_vision_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using Anthropic Claude Vision"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not configured")
        
        # Prepare content
        content = [
            {
                "type": "text",
                "text": f"""You are a helpful assistant that can analyze videos and answer questions about them.
                
                Video transcript: {context.get('transcript', 'No transcript available')}
                
                User question: {message}
                
                Please analyze the video frames and provide a detailed response."""
            }
        ]
        
        # Add visual content
        for frame in context.get("frames", []):
            try:
                image_path = frame["image_path"].replace("/static/", "./data/")
                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                    
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.b64encode(image_data).decode('utf-8')
                        }
                    })
            except Exception as e:
                print(f"Error processing image {frame['image_path']}: {e}")
        
        # Generate response
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": content
            }]
        )
        
        return {
            "content": response.content[0].text,
            "confidence": 0.9
        }
    
    async def _generate_text_only_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text-only response using available LLM"""
        if self.openai_client:
            return await self._generate_openai_text_response(message, context)
        elif self.anthropic_client:
            return await self._generate_anthropic_text_response(message, context)
        else:
            return {
                "content": "I apologize, but no LLM service is configured. Please set up OpenAI or Anthropic API keys in your .env file.",
                "confidence": 0.0
            }
    
    async def _generate_openai_text_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text-only response using OpenAI"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can analyze videos and answer questions about them."
            },
            {
                "role": "user",
                "content": f"""Video transcript: {context.get('transcript', 'No transcript available')}
                
                Frame descriptions: {[frame.get('description', '') for frame in context.get('frames', [])]}
                
                User question: {message}"""
            }
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return {
            "content": response.choices[0].message.content,
            "confidence": 0.8
        }
    
    async def _generate_anthropic_text_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text-only response using Anthropic"""
        content = f"""Video transcript: {context.get('transcript', 'No transcript available')}

Frame descriptions: {[frame.get('description', '') for frame in context.get('frames', [])]}

User question: {message}"""
        
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": content
            }]
        )
        
        return {
            "content": response.content[0].text,
            "confidence": 0.8
        } 