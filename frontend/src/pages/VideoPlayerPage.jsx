import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { videoAPI, responseAPI, sessionAPI } from "../services/api";

function VideoPlayerPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();

  const [video, setVideo] = useState(null);
  const [currentSnippetIndex, setCurrentSnippetIndex] = useState(0);
  const [participantId, setParticipantId] = useState("");
  const [existingResponses, setExistingResponses] = useState({});
  const [currentAudioType, setCurrentAudioType] = useState(null);
  const [audioAssignments, setAudioAssignments] = useState({});

  const [hasPlayedVideo, setHasPlayedVideo] = useState(false);
  const [hasVideoEnded, setHasVideoEnded] = useState(false);
  const [lastVideoTime, setLastVideoTime] = useState(0);
  
  const [recording, setRecording] = useState(null);
  const [recordingUrl, setRecordingUrl] = useState(null);
  const [recordingBase64, setRecordingBase64] = useState(null);
  const [recordingMimeType, setRecordingMimeType] = useState(null);
  const [savedRecordingPath, setSavedRecordingPath] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mcqAnswers, setMcqAnswers] = useState([]);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [showCustomControls, setShowCustomControls] = useState(true);
  const videoRef = useRef(null);

  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

    // Helper function to format time
    const formatTime = (seconds) => {
        if (!seconds || isNaN(seconds)) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Update your video event handlers
    const handleVideoPlay = () => {
        setHasPlayedVideo(true);
        setIsPlaying(true);
    };

    const handleVideoEnd = () => {
        setHasVideoEnded(true);
        setIsPlaying(false);
    };

    const handleVideoTimeUpdate = (e) => {
        const video = e.target;
        const currentTimeValue = video.currentTime;

        if (currentTimeValue > lastVideoTime + 0.5) {
            video.currentTime = lastVideoTime;
        } else {
            setLastVideoTime(currentTimeValue);
            setCurrentTime(currentTimeValue);
        }
    };

    // Add these new handlers
    const handleVideoPause = () => {
        setIsPlaying(false);
    };

    const handleVideoLoadedMetadata = (e) => {
        setDuration(e.target.duration);
    };

    const togglePlayPause = () => {
        if (videoRef.current) {
            if (videoRef.current.paused) {
            videoRef.current.play();
            } else {
            videoRef.current.pause();
            }
        }
    };

    const handleVolumeChange = (e) => {
        const newVolume = parseFloat(e.target.value);
        setVolume(newVolume);
        if (videoRef.current) {
            videoRef.current.volume = newVolume;
            setIsMuted(newVolume === 0);
        }
    };

    const toggleMute = () => {
        if (videoRef.current) {
            if (isMuted) {
                videoRef.current.volume = volume || 0.5;
                setIsMuted(false);
            } else {
                videoRef.current.volume = 0;
                setIsMuted(true);
            }
        }
    };

  useEffect(() => {
    const storedId = localStorage.getItem("participantId");
    if (!storedId) {
      alert("Please enter your participant ID first");
      navigate("/");
      return;
    }
    setParticipantId(storedId);
    loadVideo();
    loadAudioAssignments();
    startVideoSession();
  }, [videoId, navigate]);

    const loadVideo = async () => {
        try {
            const response = await videoAPI.get(videoId);

            if (!response.data.snippets || !Array.isArray(response.data.snippets)) {
                console.error("Video data missing snippets array:", response.data);
                alert("Error: Video data is incomplete");
                return;
            }

            setVideo(response.data);
        } catch (error) {
            console.error("Error loading video:", error);
            alert("Failed to load video");
            navigate("/");
        }
    };

    const loadAudioAssignments = async () => {
    try {
        const response = await videoAPI.getAudioAssignments(videoId);
        setAudioAssignments(response.data);
    } catch (error) {
        console.error("Error loading audio assignments:", error);
    }
    };

    const startVideoSession = async () => {
        try {
            await sessionAPI.start(videoId);
            console.log("Video session started");
        } catch (error) {
            console.error("Error starting session:", error);
        }
    };

  const loadExistingResponses = async (pId) => {
    if (!pId || !videoId) return;

    try {
      const response = await responseAPI.getParticipantVideoResponses(
        pId,
        videoId
      );
      //   console.log("Existing responses:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("Expected array of responses, got:", response.data);
        return;
      }

      const responsesMap = {};
      response.data.forEach((resp) => {
        responsesMap[resp.snippet_id] = resp;
      });
      setExistingResponses(responsesMap);
    } catch (error) {
      console.error("Error loading existing responses:", error);
    }
  };

  const currentSnippet = video?.snippets?.[currentSnippetIndex];
  const currentSnippetId = currentSnippet?.id;
  const existingResponse = currentSnippetId
    ? existingResponses[currentSnippetId]
    : null;

  useEffect(() => {
    if (participantId && video) {
      loadExistingResponses(participantId);
    }
  }, [participantId, video]);

  useEffect(() => {
    const interval = setInterval(() => {
      const videoElement = document.querySelector('video');
      if (videoElement && videoElement.playbackRate !== 1.0) {
        console.warn('Playback rate changed, resetting to 1.0x');
        videoElement.playbackRate = 1.0;
      }
    }, 500);

    return () => clearInterval(interval);
  }, []);

useEffect(() => {
    setHasPlayedVideo(false);
    setHasVideoEnded(false);
    setLastVideoTime(0);

    if (existingResponse) {
        console.log("Loading existing response for snippet:", currentSnippetIndex);
        
        if (existingResponse.audio_recording_base64) {
            const base64String = existingResponse.audio_recording_base64;
            const mimeType = existingResponse.audio_mime_type || 'audio/webm';
            
            // convert base64 to blob URL for playback
            const byteCharacters = atob(base64String);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: mimeType });
            const url = URL.createObjectURL(blob);
            
            setRecordingUrl(url);
            setRecordingBase64(base64String);
            setRecordingMimeType(mimeType);
            console.log("Loaded audio from base64, size:", blob.size);
        }
        
        setSavedRecordingPath(existingResponse.audio_recording_path || null);
        setMcqAnswers(existingResponse.mcq_answers || []);
        setHasSubmitted(!!existingResponse.submitted_at);
    } else {
        setSavedRecordingPath(null);
        setMcqAnswers([]);
        setHasSubmitted(false);
        setRecordingBase64(null);
        setRecordingMimeType(null);
    }
    setRecording(null);
    
    if (recordingUrl && !existingResponse) {
        URL.revokeObjectURL(recordingUrl);
        setRecordingUrl(null);
    }

    if (currentSnippetId && audioAssignments[currentSnippetId]) {
        setCurrentAudioType(audioAssignments[currentSnippetId]);
    }
}, [currentSnippetIndex, existingResponse]);

  useEffect(() => {
    return () => {
      if (recordingUrl) {
        URL.revokeObjectURL(recordingUrl);
      }
    };
  }, [recordingUrl]);

  const handleKeyDown = (e) => {
    const blockedKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' ', 'Home', 'End'];

    if (blockedKeys.includes(e.key)) {
        e.preventDefault();
        e.stopPropagation();
    }

    if (e.key >= '0' && e.key <= '9') {
        e.preventDefault();
        e.stopPropagation();
    }
  };

  const startRecording = async () => {
    try {
      //   console.log("=== Starting Recording ===");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      //   console.log("Got media stream:", stream);

      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
      ];

      let selectedMimeType = null;
      for (const mimeType of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType;
          //   console.log("Selected MIME type:", mimeType);
          break;
        }
      }

      if (!selectedMimeType) {
        console.error("No supported MIME types found!");
        alert("Your browser doesn't support audio recording");
        return;
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: selectedMimeType,
      });
      mediaRecorderRef.current = mediaRecorder;
      recordedChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        console.log("Data available, size:", event.data.size);
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

    mediaRecorder.onstop = () => {
        console.log("=== Recording Stopped ===");
        console.log("Total chunks:", recordedChunksRef.current.length);

        if (recordedChunksRef.current.length === 0) {
            console.error("No audio data recorded!");
            alert("Recording failed - no audio data captured");
            return;
        }

        const blob = new Blob(recordedChunksRef.current, {
            type: selectedMimeType,
        });

        console.log("Created blob:");
        console.log("  - Size:", blob.size, "bytes");
        console.log("  - Type:", blob.type);

        if (blob.size === 0) {
            console.error("Blob is empty!");
            alert("Recording failed - empty audio file");
            return;
        }

        setRecording(blob);
        setRecordingMimeType(blob.type);
        const url = URL.createObjectURL(blob);
        console.log("Created blob URL:", url);
        setRecordingUrl(url);

        stream.getTracks().forEach((track) => {
            track.stop();
        });
    };


      mediaRecorder.onerror = (e) => {
        console.error("MediaRecorder error:", e);
        alert("Recording error: " + e.error);
      };

      mediaRecorder.start(100);
      console.log("MediaRecorder started");
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    // console.log("=== Stopping Recording ===");
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    ) {
      //   console.log("Stopping MediaRecorder, chunks:", recordedChunksRef.current.length);
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleMcqChange = (questionIndex, optionIndex) => {
    const newAnswers = [...mcqAnswers];
    newAnswers[questionIndex] = optionIndex;
    setMcqAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    console.log("=== Starting Submit ===");
    console.log("Recording:", recording);
    console.log("Saved base64:", recordingBase64 ? "exists" : "none");
    console.log("MCQ answers:", mcqAnswers);

    if (!recording && !recordingBase64) {
        alert("Please record your audio response first!");
        return;
    }

    if (mcqAnswers.length !== currentSnippet.mcq_questions.length) {
        alert(
            `Please answer all ${currentSnippet.mcq_questions.length} questions! You've answered ${mcqAnswers.length}.`
        );
        return;
    }

    setShowSubmitConfirm(false);
    setIsUploading(true);

    try {
        let audioBase64 = recordingBase64;
        let audioMimeType = recordingMimeType;

        if (recording && !recordingBase64) {
            console.log("=== Converting Recording to Base64 ===");
            console.log("Blob size:", recording.size);
            console.log("Blob type:", recording.type);

            try {
                // convert blob to base64
                const reader = new FileReader();
                const base64Promise = new Promise((resolve, reject) => {
                    reader.onloadend = () => {
                        const base64String = reader.result.split(',')[1]; // remove data:audio/webm;base64, prefix
                        resolve(base64String);
                    };
                    reader.onerror = reject;
                });
                
                reader.readAsDataURL(recording);
                audioBase64 = await base64Promise;
                audioMimeType = recording.type;
                
                console.log("Base64 conversion complete, length:", audioBase64.length);
                setRecordingBase64(audioBase64);  // save for potential re-submission
            } catch (encodeError) {
                console.error("Encoding error:", encodeError);
                throw new Error(`Failed to encode recording: ${encodeError.message}`);
            }
        }

        const responseData = {
            participant_id: participantId,
            snippet_id: currentSnippetId,
            audio_recording_base64: audioBase64,
            audio_mime_type: audioMimeType,
            audio_recording_path: `base64_${participantId}_${currentSnippetId}`, // reference only
            audio_duration: 5.0,
            mcq_answers: mcqAnswers,
            submit: true,
        };

        console.log("=== Submitting Response ===");
        console.log("Response data (base64 length):", audioBase64.length);

        try {
            const submitResponse = await responseAPI.create(responseData);
            console.log("Submit response:", submitResponse.data);
        } catch (submitError) {
            console.error("Submit error:", submitError);
            console.error("Submit error response:", submitError.response?.data);
            throw new Error(
                `Failed to save response: ${
                    submitError.response?.data?.error || submitError.message
                }`
            );
        }

        setHasSubmitted(true);
        await loadExistingResponses(participantId);
        alert("Response submitted successfully!");

    } catch (error) {
        console.error("=== Submit Failed ===");
        console.error("Error:", error);
        alert(`Failed to submit: ${error.message}`);
    } finally {
        setIsUploading(false);
        console.log("=== Submit Complete ===");
    }
};

const handleNext = () => {
  if (!video?.snippets) return;

  if (recordingUrl) {
    URL.revokeObjectURL(recordingUrl);
  }

  const nextIndex = currentSnippetIndex + 1;
  
  if (nextIndex < video.snippets.length) {
    const isLastSnippet = (nextIndex === video.snippets.length - 1);
    
    if (isLastSnippet) {
      navigate(`/calibration/${videoId}`);
    } else {
      console.log("Moving to next regular snippet");
      setCurrentSnippetIndex(nextIndex);
    }
  }
};

  if (!video || !participantId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  if (!video.snippets || video.snippets.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-2xl">
          No snippets available for this video
        </div>
      </div>
    );
  }

  if (!currentSnippet) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-2xl">Error loading snippet</div>
      </div>
    );
  }

  // show response section if: video has ended, OR already submitted
  const showResponseSection = hasVideoEnded || hasSubmitted;

  return (
    <>
        <style>{`
        /* Hide default webkit controls */
        video::-webkit-media-controls-skip-forward-button,
        video::-webkit-media-controls-skip-backward-button,
        video::-webkit-media-controls-playback-speed-button {
            display: none !important;
        }
        
        /* Style the volume slider */
        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 12px;
            height: 12px;
            background: white;
            cursor: pointer;
            border-radius: 50%;
            border: none;
        }
        
        .slider::-moz-range-thumb {
            width: 12px;
            height: 12px;
            background: white;
            cursor: pointer;
            border-radius: 50%;
            border: none;
        }
        
        .slider:focus {
            outline: none;
        }
        `}</style>
      
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-8">
        <div className="max-w-4xl mx-auto">
            <div className="mb-6 flex justify-between items-center">
                <button
                    onClick={() => navigate("/")}
                    className="text-white hover:text-gray-300 flex items-center"
                >
                    Back to Home
                </button>
                <div className="flex items-center gap-4">
                    {currentAudioType && (
                        <div className={`px-4 py-2 rounded-full font-semibold text-white`}>
                            Audiotype: {currentAudioType.charAt(0).toUpperCase() + currentAudioType.slice(1)}
                        </div>
                    )}
                    
                    <div className="text-white">
                        Snippet {currentSnippetIndex + 1} of {video.snippets.length}
                    </div>
                </div>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8 mb-6">
            <h2 className="text-3xl font-bold text-white mb-4">{video.title}</h2>
            <p className="text-gray-300">{video.description}</p>
            {currentAudioType && (
                <p className="text-gray-300 mb-6">
                    *The audio type is <span className="font-semibold">{currentAudioType.charAt(0).toUpperCase() + currentAudioType.slice(1)}</span>. 
                    Please remember this for future reference.
                </p>
            )}


            {/* Instruction text */}
            {!hasPlayedVideo && !hasSubmitted && (
                <div className="mb-4 p-4 bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg">
                    <p className="text-blue-200 text-center font-semibold">
                        Press play below to start the snippet
                    </p>
                </div>
            )}

            {/* Video Player */}
            <div className="relative bg-black rounded-lg overflow-hidden">
            <video
                ref={videoRef}
                className="w-full cursor-pointer"
                controls={!showCustomControls}
                controlsList="nodownload noplaybackrate nofullscreen noremoteplayback"
                disablePictureInPicture
                disableRemotePlayback
                onPlay={handleVideoPlay}
                onPause={handleVideoPause}
                onEnded={handleVideoEnd}
                onTimeUpdate={handleVideoTimeUpdate}
                onLoadedMetadata={handleVideoLoadedMetadata}
                onClick={togglePlayPause} // Click anywhere on video to play/pause
                onSeeking={(e) => { 
                e.preventDefault();
                e.target.currentTime = lastVideoTime; 
                }}
                onRateChange={(e) => { 
                e.preventDefault();
                e.target.playbackRate = 1.0; 
                }}
                onKeyDown={handleKeyDown}
                onContextMenu={(e) => e.preventDefault()}
                onDoubleClick={(e) => e.preventDefault()}
                src={
                audioAssignments[currentSnippet.id] 
                    ? currentSnippet[`video_filename_${audioAssignments[currentSnippet.id]}`]
                    : currentSnippet.video_filename_balanced
                }
            >
                Your browser does not support the video tag.
            </video>
            
            {showCustomControls && (
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent pt-8 pb-2 px-3">
                {/* Progress Bar */}
                    <div 
                        className="relative h-1 bg-gray-600/50 rounded-full mb-3"
                        style={{ cursor: 'not-allowed' }}
                        title="Seeking is disabled for this video"
                    >
                    <div 
                    className="h-full bg-white rounded-full relative"
                    style={{
                        width: `${duration ? (currentTime / duration) * 100 : 0}%`
                    }}
                    >
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 hover:opacity-100 transition-opacity" />
                    </div>
                </div>

                {/* Controls Row */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                    {/* Play/Pause Button */}
                    <button
                        onClick={togglePlayPause}
                        className="text-white hover:text-gray-300 transition-colors p-1"
                        aria-label={isPlaying ? "Pause" : "Play"}
                    >
                        {isPlaying ? (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <rect x="6" y="5" width="4" height="14" rx="1" />
                            <rect x="14" y="5" width="4" height="14" rx="1" />
                        </svg>
                        ) : (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                        </svg>
                        )}
                    </button>

                    {/* Volume Controls */}
                    <div className="flex items-center gap-2">
                        <button
                        onClick={toggleMute}
                        className="text-white hover:text-gray-300 transition-colors"
                        aria-label={isMuted ? "Unmute" : "Mute"}
                        >
                        {isMuted || volume === 0 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                            </svg>
                        ) : volume > 0.5 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M7 9v6h4l5 5V4l-5 5H7z"/>
                            </svg>
                        )}
                        </button>
                        <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={isMuted ? 0 : volume}
                        onChange={handleVolumeChange}
                        className="w-20 h-1 bg-gray-600 rounded-full appearance-none cursor-pointer slider"
                        style={{
                            background: `linear-gradient(to right, white ${volume * 100}%, #4B5563 ${volume * 100}%)`
                        }}
                        />
                    </div>

                    {/* Time Display */}
                    <div className="text-white text-sm font-medium ml-2">
                        <span>{formatTime(currentTime)}</span>
                        <span className="text-gray-400 mx-1">/</span>
                        <span className="text-gray-400">{formatTime(duration)}</span>
                    </div>
                    </div>

                    {/* Right Side Controls (can add fullscreen button here if needed) */}
                    <div className="flex items-center gap-2">
                    {/* Placeholder for additional controls */}
                    </div>
                </div>
                </div>
            )}
            </div>

            {showResponseSection && (
                <div className="space-y-6">
                {/* Audio Recording Section */}
                <div className="bg-white bg-opacity-20 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-white mb-2">
                    Audio Response
                    </h3>
                    <p className="text-md font-semibold text-white mb-4">
                    Please record your spoken response to the snippet you just
                    watched.
                    </p>

                    {!hasSubmitted ? (
                    <div className="space-y-4">
                        {!recording && !isRecording && (
                        <button
                            onClick={startRecording}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg transition duration-200 flex items-center justify-center gap-2"
                        >
                            <svg
                            className="w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                            >
                            <circle cx="12" cy="12" r="10" />
                            </svg>
                            Start Recording
                        </button>
                        )}

                        {isRecording && (
                        <button
                            onClick={stopRecording}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition duration-200 flex items-center justify-center gap-2 animate-pulse"
                        >
                            <svg
                            className="w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                            >
                            <rect x="6" y="6" width="12" height="12" />
                            </svg>
                            Stop Recording
                        </button>
                        )}

                        {recording && !isRecording && (
                        <div className="space-y-3">
                            <div className="bg-green-900 bg-opacity-30 border border-green-500 rounded-lg p-4">
                            <p className="text-green-300 mb-2">
                                Recording complete - Listen to your recording:
                            </p>
                            <p className="text-gray-400 text-xs mb-2">
                                Please replay the recording at least once to ensure
                                it is correct before submitting. There may be a
                                playback issue due to recording delay on the first
                                playback.
                            </p>
                            <audio
                                controls
                                preload="auto"
                                src={recordingUrl}
                                className="w-full mb-3"
                                onLoadedMetadata={(e) => {
                                console.log(
                                    "Audio loaded, duration:",
                                    e.target.duration
                                );
                                }}
                                onError={(e) => {
                                console.error("Audio playback error:", e);
                                console.error(
                                    "Error code:",
                                    e.target.error?.code
                                );
                                console.error("Blob URL:", recordingUrl);
                                }}
                                onCanPlay={() => console.log("Audio can play")}
                            />
                            <button
                                onClick={() => {
                                if (recordingUrl) {
                                    URL.revokeObjectURL(recordingUrl);
                                }
                                setRecording(null);
                                setRecordingUrl(null);
                                startRecording();
                                }}
                                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200"
                            >
                                Re-record
                            </button>
                            </div>
                        </div>
                        )}
                    </div>
                    ) : (
                    <div className="bg-green-900 bg-opacity-30 border border-green-500 rounded-lg p-4">
                        <p className="text-green-300 text-sm mb-2">
                        Submitted recording:
                        </p>
                        <audio
                            controls
                            preload="auto"
                            src={recordingUrl}
                            className="w-full"
                            onError={(e) => {
                                console.error("Error loading saved recording:", e);
                            }}
                        />
                    </div>
                    )}
                </div>

                {/* MCQ Section */}
                <div className="bg-white bg-opacity-20 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-white mb-4">
                    Comprehension Questions
                    </h3>
                    <div className="space-y-6">
                    {currentSnippet.mcq_questions &&
                        currentSnippet.mcq_questions.map((q, qIndex) => (
                        <div
                            key={qIndex}
                            className="border-b border-gray-400 pb-4 last:border-0"
                        >
                            <p className="text-white font-semibold mb-3">
                            {qIndex + 1}. {q.question}
                            </p>
                            <div className="space-y-2">
                            {q.options.map((option, oIndex) => (
                                <label
                                key={oIndex}
                                className="flex items-center space-x-3 text-white cursor-pointer hover:bg-white hover:bg-opacity-10 p-2 rounded transition"
                                >
                                <input
                                    type="radio"
                                    name={`question-${qIndex}`}
                                    checked={mcqAnswers[qIndex] === oIndex}
                                    onChange={() => handleMcqChange(qIndex, oIndex)}
                                    disabled={hasSubmitted}
                                    className="form-radio h-5 w-5"
                                />
                                <span>{option}</span>
                                </label>
                            ))}
                            </div>
                        </div>
                        ))}
                    </div>

                    {hasSubmitted && (
                    <div className="mt-4 p-3 bg-green-900 bg-opacity-30 border border-green-500 rounded-lg">
                        <p className="text-green-300 text-sm">
                        Your answers have been submitted
                        </p>
                    </div>
                    )}
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4">
                    {!hasSubmitted ? (
                    <button
                        onClick={() => setShowSubmitConfirm(true)}
                        disabled={isUploading || !recording}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isUploading ? "Submitting..." : "Submit Response"}
                    </button>
                    ) : (
                    <button
                        onClick={handleNext}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg"
                    >
                        {currentSnippetIndex < video.snippets.length - 1
                        ? "Next Snippet"
                        : "Complete"}
                    </button>
                    )}
                </div>
                </div>
            )}
            </div>
        </div>

        {/* Submit Confirmation Modal */}
        {showSubmitConfirm && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
                <h3 className="text-xl font-bold mb-4">Confirm Submission</h3>
                <p className="mb-6">
                Are you sure you want to submit? You won't be able to change your
                response after submission.
                </p>
                <div className="flex space-x-4">
                <button
                    onClick={() => setShowSubmitConfirm(false)}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 rounded"
                >
                    Cancel
                </button>
                <button
                    onClick={handleSubmit}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded"
                >
                    Confirm
                </button>
                </div>
            </div>
            </div>
        )}
        </div>
    </>
  );
}

export default VideoPlayerPage;
