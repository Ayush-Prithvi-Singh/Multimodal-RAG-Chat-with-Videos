# Multimodal RAG: Chat with Videos

A powerful multimodal retrieval-augmented generation (RAG) system that allows you to chat with videos by extracting, processing, and understanding video content through AI.

## 🎯 Project Overview

This project enables users to upload videos and have intelligent conversations about the content. The system processes videos by extracting frames, transcribing audio, and using AI to understand and respond to questions about the video content.

### Key Features
- **Video Upload & Processing**: Support for multiple video formats with automatic frame extraction
- **Audio Transcription**: Automatic speech-to-text conversion using Whisper
- **Multimodal Understanding**: Combines visual, audio, and text analysis
- **RAG-Powered Chat**: Vector-based retrieval for context-aware responses
- **Real-time Processing**: Stream and process videos on-the-fly
- **Modern Web Interface**: Beautiful, responsive UI for seamless interaction

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (OpenAI/Claude)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Vector Database│
                       │   (ChromaDB)    │
                       └─────────────────┘
```

## 🔧 Tech Stack & Components

### Backend (Python/FastAPI)

#### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
  - **Why**: High performance, automatic API documentation, type safety with Pydantic
  - **Role**: Handles HTTP requests, file uploads, and coordinates all services

#### Video Processing
- **OpenCV (cv2)**: Computer vision library for video frame extraction
  - **Why**: Industry-standard for video/image processing, efficient frame extraction
  - **Role**: Extracts frames at specified intervals from uploaded videos

- **FFmpeg**: Video processing toolkit
  - **Why**: Robust video format support, efficient video manipulation
  - **Role**: Video format conversion and metadata extraction

- **MoviePy**: Python library for video editing
  - **Why**: High-level video processing, easy integration with Python
  - **Role**: Video duration, FPS, and resolution extraction

#### Audio Processing
- **OpenAI Whisper**: Speech recognition model
  - **Why**: State-of-the-art speech-to-text, supports multiple languages
  - **Role**: Transcribes audio from videos to text

- **Librosa**: Audio analysis library
  - **Why**: Advanced audio processing capabilities
  - **Role**: Audio feature extraction and analysis

#### AI & Machine Learning
- **OpenAI GPT-4 Vision**: Multimodal language model
  - **Why**: Advanced vision-language understanding, can analyze images and text
  - **Role**: Generates responses based on video frames and context

- **Anthropic Claude**: Alternative AI model
  - **Why**: High-quality responses, good at reasoning
  - **Role**: Backup AI service for text generation

- **Sentence Transformers**: Text embedding model
  - **Why**: Efficient text-to-vector conversion, good semantic understanding
  - **Role**: Creates embeddings for RAG retrieval

#### Vector Database
- **ChromaDB**: Vector database for similarity search
  - **Why**: Lightweight, easy to use, good performance for embeddings
  - **Role**: Stores and retrieves video frame and transcript embeddings

#### Data Processing
- **NumPy**: Numerical computing
  - **Why**: Efficient array operations, mathematical computations
  - **Role**: Data manipulation for video frames and embeddings

- **Pandas**: Data analysis library
  - **Why**: Powerful data manipulation and analysis
  - **Role**: Processing video metadata and structured data

### Frontend (React/TypeScript)

#### Core Framework
- **React 18**: JavaScript library for building user interfaces
  - **Why**: Component-based architecture, large ecosystem, excellent performance
  - **Role**: Creates interactive, responsive web interface

- **TypeScript**: Typed JavaScript
  - **Why**: Type safety, better developer experience, fewer runtime errors
  - **Role**: Ensures code quality and maintainability

#### Build Tools
- **Vite**: Build tool and development server
  - **Why**: Extremely fast development server, optimized builds
  - **Role**: Bundles and serves the React application

#### UI Framework
- **Tailwind CSS**: Utility-first CSS framework
  - **Why**: Rapid UI development, consistent design system
  - **Role**: Styling and responsive design

#### UI Components
- **Lucide React**: Icon library
  - **Why**: Beautiful, consistent icons
  - **Role**: Visual elements throughout the interface

- **React Dropzone**: File upload component
  - **Why**: Drag-and-drop file uploads, excellent UX
  - **Role**: Video file upload interface

#### State Management & HTTP
- **Axios**: HTTP client
  - **Why**: Promise-based, easy to use, good error handling
  - **Role**: API communication with backend

#### Notifications
- **React Hot Toast**: Toast notifications
  - **Why**: Lightweight, customizable notifications
  - **Role**: User feedback for actions and errors

#### Routing
- **React Router DOM**: Client-side routing
  - **Why**: Single-page application navigation
  - **Role**: Navigation between upload and chat pages

## 🧠 AI Techniques & Methodologies

### 1. Retrieval-Augmented Generation (RAG)
**What it is**: A technique that combines information retrieval with text generation
**Why used**: Provides contextually relevant responses by retrieving relevant information before generating answers
**How implemented**: 
- Store video frames and transcripts as vector embeddings
- Retrieve similar content when user asks questions
- Use retrieved context to generate informed responses

### 2. Vector Embeddings
**What it is**: Converting text, images, or other data into numerical vectors that capture semantic meaning
**Why used**: Enables similarity search and semantic understanding
**Techniques used**:
- **Sentence Transformers**: For text embeddings (transcripts)
- **Vision Models**: For image embeddings (video frames)
- **Cosine Similarity**: For measuring similarity between vectors

### 3. Multimodal AI Processing
**What it is**: AI systems that can process and understand multiple types of data (text, images, audio)
**Why used**: Videos contain visual, audio, and textual information that need to be understood together
**Techniques used**:
- **Frame Extraction**: Sampling video frames at regular intervals
- **Audio Transcription**: Converting speech to text using Whisper
- **Vision-Language Models**: GPT-4 Vision for understanding visual content
- **Context Fusion**: Combining visual and textual information

### 4. Semantic Search
**What it is**: Finding content based on meaning rather than exact keyword matches
**Why used**: Users ask questions in natural language, not exact transcript quotes
**Implementation**:
- Convert user queries to embeddings
- Find similar embeddings in the vector database
- Return most relevant video segments and transcript chunks

### 5. Chunking Strategy
**What it is**: Breaking down large documents or transcripts into smaller, manageable pieces
**Why used**: Improves retrieval accuracy and allows for more precise context matching
**Techniques**:
- **Sliding Window**: Overlapping chunks for better context preservation
- **Semantic Chunking**: Breaking at natural sentence boundaries
- **Fixed-size Chunks**: For consistent embedding sizes

### 6. Context Window Management
**What it is**: Managing how much context is provided to the AI model
**Why used**: AI models have token limits, so we need to be selective about what context to include
**Strategy**:
- Retrieve top-k most relevant chunks
- Prioritize by relevance score
- Include both visual and textual context

### 7. Fallback Mechanisms
**What it is**: Having backup systems when primary AI services fail
**Why used**: Ensures system reliability and availability
**Implementation**:
- Multiple AI providers (OpenAI, Anthropic)
- Graceful degradation when services are unavailable
- Cached responses for common queries

### 8. Real-time Processing Pipeline
**What it is**: Processing videos as they're uploaded without blocking the user
**Why used**: Provides immediate feedback and better user experience
**Techniques**:
- **Asynchronous Processing**: Non-blocking video analysis
- **Progress Tracking**: Real-time status updates
- **Streaming**: Process video in chunks rather than all at once

## 🔄 Component Interaction Flow

### 1. Video Upload Process
```
User Uploads Video
       ↓
Frontend (VideoUpload.tsx)
       ↓
Backend API (/api/videos/upload)
       ↓
VideoProcessor Service
├── Extract metadata (duration, FPS, resolution)
├── Extract frames using OpenCV
├── Transcribe audio using Whisper
└── Analyze frames (placeholder for vision AI)
       ↓
RAGService
├── Create embeddings for frames
├── Create embeddings for transcript
└── Store in ChromaDB
       ↓
Return video_id to frontend
       ↓
Navigate to chat interface
```

### 2. Chat Process
```
User Sends Message
       ↓
Frontend (VideoChat.tsx)
       ↓
Backend API (/api/chat)
       ↓
RAGService
├── Create query embedding
├── Search similar frames and transcript chunks
└── Return relevant context
       ↓
LLMService
├── Combine user message with context
├── Generate response using GPT-4 Vision/Claude
└── Return AI response
       ↓
Store chat history
       ↓
Return response to frontend
       ↓
Display in chat interface
```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── routes/
│   │   │       ├── videos.py    # Video upload/management
│   │   │       └── chat.py      # Chat functionality
│   │   ├── core/           # Configuration
│   │   │   └── config.py   # Environment settings
│   │   ├── models/         # Data models
│   │   │   └── video.py    # Pydantic models
│   │   ├── services/       # Business logic
│   │   │   ├── video_processor.py  # Video processing
│   │   │   ├── rag_service.py      # Vector search
│   │   │   └── llm_service.py      # AI integration
│   │   └── utils/          # Utilities
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # FastAPI app entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── VideoUpload.tsx  # Upload interface
│   │   │   └── VideoChat.tsx    # Chat interface
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx         # Main app component
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── data/                   # Data storage
│   ├── videos/             # Uploaded videos
│   ├── frames/             # Extracted frames
│   └── vectors/            # Vector database
└── README.md              # This file
```

## 🚀 Key Components Explained

### VideoProcessor Service
- **Purpose**: Handles all video-related processing
- **Responsibilities**:
  - Extract video metadata (duration, FPS, resolution)
  - Extract frames at specified intervals
  - Transcribe audio using Whisper
  - Prepare data for AI analysis

### RAGService
- **Purpose**: Manages vector storage and retrieval
- **Responsibilities**:
  - Create embeddings for video frames and transcripts
  - Store embeddings in ChromaDB
  - Perform similarity search for relevant content
  - Provide context for AI responses

### LLMService
- **Purpose**: Interfaces with AI models
- **Responsibilities**:
  - Generate responses using GPT-4 Vision or Claude
  - Handle multimodal input (text + images)
  - Manage API keys and fallback options
  - Format responses for frontend

### VideoUpload Component
- **Purpose**: Handles video file uploads
- **Features**:
  - Drag-and-drop interface
  - File validation (type, size)
  - Upload progress tracking
  - Error handling and user feedback

### VideoChat Component
- **Purpose**: Chat interface for video conversations
- **Features**:
  - Real-time messaging
  - Message history
  - Loading states
  - Responsive design

## 🔑 Environment Variables

### Backend (.env)
```bash
OPENAI_API_KEY=your_openai_key          # For GPT-4 Vision
ANTHROPIC_API_KEY=your_anthropic_key    # For Claude
CHROMA_DB_PATH=./data/vectors           # Vector database location
UPLOAD_DIR=./data/videos                # Video storage location
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000      # Backend API URL
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- FFmpeg installed on your system

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Use Cases

1. **Content Analysis**: Analyze educational videos, presentations, or tutorials
2. **Video Search**: Find specific moments or content within videos
3. **Accessibility**: Generate descriptions for video content
4. **Research**: Extract insights from video datasets
5. **Documentation**: Create summaries and transcripts of video content

## 🔮 Future Enhancements

- **Real-time Video Processing**: Stream processing for live videos
- **Advanced Vision Models**: Integration with specialized computer vision models
- **Multi-language Support**: Enhanced language detection and translation
- **Video Editing**: AI-powered video editing suggestions
- **Collaborative Features**: Shared video analysis and annotations
- **Mobile App**: Native mobile application
- **Cloud Deployment**: Scalable cloud infrastructure

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with ❤️ using modern AI and web technologies** 