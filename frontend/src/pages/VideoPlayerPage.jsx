import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { videoAPI, interactionAPI } from "../services/api";

function VideoPlayerPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();

  const [video, setVideo] = useState(null);
  const [currentSnippet, setCurrentSnippet] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSymbol, setShowSymbol] = useState(false);
  const [keyPresses, setKeyPresses] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingState, setRecordingState] = useState("idle"); // idle, recording, stopped
  const [interactionId, setInteractionId] = useState(null);
  const [participantId] = useState(1);

  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const symbolIntervalRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  useEffect(() => {
    loadVideo();
    return () => {
      if (symbolIntervalRef.current) {
        clearInterval(symbolIntervalRef.current);
      }
    };
  }, [videoId]);

  const loadVideo = async () => {
    try {
      const response = await videoAPI.get(videoId);
      setVideo(response.data);
    } catch (error) {
      console.error("Error loading video:", error);
      alert("Failed to load video");
    }
  };

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.code === "Space" && isPlaying && videoRef.current) {
        e.preventDefault();
        const timestamp = Date.now();
        const videoTime = videoRef.current.currentTime;

        setKeyPresses((prev) => [
          ...prev,
          {
            key: "Space",
            timestamp,
            video_time: videoTime,
            symbol_visible: showSymbol,
          },
        ]);
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [isPlaying, showSymbol]);

  const startSnippet = async () => {
    if (!video || !video.snippets[currentSnippet]) return;

    const snippet = video.snippets[currentSnippet];

    try {
      const response = await interactionAPI.create({
        participant_id: participantId,
        video_id: video.id,
        snippet_index: snippet.snippet_index,
        keystroke_data: [],
      });
      setInteractionId(response.data.id);
    } catch (error) {
      console.error("Error creating interaction:", error);
    }

    setKeyPresses([]);

    if (videoRef.current && audioRef.current) {
      videoRef.current.src = `/videos/${video.video_id}/${snippet.video_filename}`;
      audioRef.current.src = `/videos/${video.video_id}/${snippet.audio_filename}`;

      if (video.audio_type === "full_replacement") {
        videoRef.current.muted = true;
        audioRef.current.volume = 1.0;
      } else if (video.audio_type === "balanced_simultaneous") {
        videoRef.current.volume = 0.7;
        audioRef.current.volume = 1.0;
      } else if (video.audio_type === "muffled_simultaneous") {
        videoRef.current.volume = 0.3;
        audioRef.current.volume = 1.0;
      }

      await videoRef.current.play();
      setTimeout(() => audioRef.current.play(), 200);

      setIsPlaying(true);
      startSymbolDisplay();
    }
  };

  const startSymbolDisplay = () => {
    symbolIntervalRef.current = setInterval(() => {
      if (Math.random() > 0.5) {
        setShowSymbol(true);
        setTimeout(() => setShowSymbol(false), 800);
      }
    }, Math.random() * 4000 + 3000);
  };

  const handleVideoEnd = async () => {
    setIsPlaying(false);
    if (symbolIntervalRef.current) {
      clearInterval(symbolIntervalRef.current);
    }

    if (interactionId) {
      try {
        await interactionAPI.create({
          participant_id: participantId,
          video_id: video.id,
          snippet_index: video.snippets[currentSnippet].snippet_index,
          keystroke_data: keyPresses,
        });
      } catch (error) {
        console.error("Error saving interaction:", error);
      }
    }

    setIsRecording(true);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      recordedChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, {
          type: "audio/webm",
        });
        console.log("Recording completed", blob);
        setRecordingState("stopped");
      };

      mediaRecorderRef.current.start();
      setRecordingState("recording");
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Could not access microphone");
    }
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream
        .getTracks()
        .forEach((track) => track.stop());
    }
  };

  const continueToNext = () => {
    if (currentSnippet < video.snippets.length - 1) {
      setCurrentSnippet((prev) => prev + 1);
      setIsRecording(false);
      setRecordingState("idle");
    } else {
      alert("Video completed! Thank you for participating.");
      navigate("/");
    }
  };

  if (!video) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <p className="text-white mt-4 text-lg">Loading video...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate("/")}
            className="flex items-center text-gray-400 hover:text-white transition"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Home
          </button>
        </div>

        {/* Video Player */}
        <div className="max-w-5xl mx-auto">
          <div className="relative bg-black rounded-2xl overflow-hidden shadow-2xl mb-6">
            <video
              ref={videoRef}
              className="w-full aspect-video"
              onEnded={handleVideoEnd}
            />

            {showSymbol && isPlaying && (
              <div className="absolute top-8 right-8 text-7xl animate-pulse-symbol">
                ⚡
              </div>
            )}

            <audio ref={audioRef} className="hidden" />
          </div>

          {/* Video Info Card */}
          <div className="bg-gray-800 rounded-xl p-6 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">{video.title}</h2>
                <p className="text-gray-400">{video.description}</p>
              </div>
              <div className="bg-indigo-600 px-4 py-2 rounded-lg text-sm font-semibold">
                {currentSnippet + 1} / {video.snippets.length}
              </div>
            </div>

            {video.snippets[currentSnippet] && (
              <div className="border-t border-gray-700 pt-4 space-y-3">
                <div>
                  <span className="text-gray-400 text-sm font-medium">
                    Original (Spanish):
                  </span>
                  <p className="text-lg mt-1">
                    {video.snippets[currentSnippet].transcript_original}
                  </p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm font-medium">
                    Translation (English):
                  </span>
                  <p className="text-lg mt-1">
                    {video.snippets[currentSnippet].transcript_translated}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          {!isPlaying && !isRecording && (
            <div className="text-center">
              <button
                onClick={startSnippet}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-12 rounded-xl text-lg transition duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                {currentSnippet === 0 ? "▶ Start Video" : "▶ Continue"}
              </button>
            </div>
          )}

          {/* Recording Interface */}
          {isRecording && (
            <div className="bg-gray-800 rounded-xl p-8 text-center">
              <div className="mb-6">
                <div className="w-20 h-20 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                  <svg
                    className="w-10 h-10 text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-2">
                  Record Your Response
                </h3>
                <p className="text-gray-400">
                  Respond naturally to what you just heard
                </p>
              </div>

              <div className="flex gap-4 justify-center mb-6">
                {recordingState === "idle" && (
                  <button
                    onClick={startRecording}
                    className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 flex items-center gap-2"
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

                {recordingState === "recording" && (
                  <button
                    onClick={stopRecording}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 flex items-center gap-2"
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

                {recordingState === "stopped" && (
                  <button
                    onClick={continueToNext}
                    className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 flex items-center gap-2"
                  >
                    Continue
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </button>
                )}

                <button
                  onClick={continueToNext}
                  className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-200"
                >
                  Skip
                </button>
              </div>
            </div>
          )}

          {/* Instructions */}
          {isPlaying && (
            <div className="bg-indigo-900 bg-opacity-50 rounded-xl p-4 text-center backdrop-blur-sm">
              <p className="text-lg">
                Press{" "}
                <kbd className="px-3 py-1 bg-white text-gray-900 rounded font-mono text-sm font-bold">
                  SPACE
                </kbd>{" "}
                when you see the ⚡ symbol
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default VideoPlayerPage;
