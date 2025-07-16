import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, Video, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const VideoUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    if (!file.type.startsWith('video/')) {
      toast.error('Please select a valid video file');
      return;
    }

    // Validate file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
      toast.error('File size must be less than 100MB');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/videos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        },
      });

      const { video_id } = response.data;
      toast.success('Video uploaded successfully! Processing in background...');
      
      // Navigate to chat page
      navigate(`/chat/${video_id}`);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload video. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    },
    multiple: false,
    disabled: uploading
  });

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your Video
        </h2>
        <p className="text-lg text-gray-600">
          Upload a video file to start chatting with it using AI
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="space-y-4">
            <Loader2 className="mx-auto h-12 w-12 text-primary-500 animate-spin" />
            <div>
              <p className="text-lg font-medium text-gray-900">Uploading...</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-500 mt-1">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {isDragActive ? (
              <Video className="mx-auto h-12 w-12 text-primary-500" />
            ) : (
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
            )}
            
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Drop the video here' : 'Drag & drop a video file here'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or click to select a file
              </p>
            </div>
            
            <div className="text-xs text-gray-400">
              Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
              <br />
              Maximum size: 100MB
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-4">How it works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-primary-600 font-bold">1</span>
            </div>
            <h4 className="font-medium text-gray-900">Upload Video</h4>
            <p className="text-sm text-gray-600 mt-1">
              Upload any video file up to 100MB
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-primary-600 font-bold">2</span>
            </div>
            <h4 className="font-medium text-gray-900">AI Processing</h4>
            <p className="text-sm text-gray-600 mt-1">
              Our AI extracts frames and transcribes audio
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-primary-600 font-bold">3</span>
            </div>
            <h4 className="font-medium text-gray-900">Chat & Explore</h4>
            <p className="text-sm text-gray-600 mt-1">
              Ask questions about your video content
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoUpload; 