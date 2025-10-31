import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { videoAPI, calibrationAPI } from "../services/api";

function VolumeCalibrationPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  
  const [video, setVideo] = useState(null);
  const [calibrationSnippet, setCalibrationSnippet] = useState(null);
  const [volume, setVolume] = useState(0.5);
  const [participantId, setParticipantId] = useState("");
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  
  const translatedVideoRef = useRef(null);
  const originalAudioRef = useRef(null);

    useEffect(() => {
    const storedId = localStorage.getItem("participantId");
    if (!storedId) {
        navigate("/");
        return;
    }
    setParticipantId(storedId);
    loadVideo();
    }, [videoId, navigate]);

    const loadVideo = async () => {
        try {
            const response = await videoAPI.get(videoId);
            const videoData = response.data;
            setVideo(videoData);
            
            const lastSnippet = videoData.snippets[videoData.snippets.length - 1];
            console.log("Last snippet (calibration):", lastSnippet);
            setCalibrationSnippet(lastSnippet);
            
        } catch (error) {
            console.error("Error loading video:", error);
        }
    };

    useEffect(() => {
        // sync original audio volume with slider
        if (originalAudioRef.current) {
            originalAudioRef.current.volume = volume;
        }
    }, [volume]);

    useEffect(() => {
        const video = translatedVideoRef.current;
        const audio = originalAudioRef.current;

        if (!video || !audio) return;

        const syncAudioToVideo = () => {
            // keep audio synced with video playback position
            if (Math.abs(audio.currentTime - video.currentTime) > 0.3) {
                audio.currentTime = video.currentTime;
            }
        };

        const handleVideoPlay = () => {
            audio.play().catch(e => console.error("Audio play error:", e));
        };

        const handleVideoPause = () => {
            audio.pause();
        };

        const handleVideoSeeked = () => {
            audio.currentTime = video.currentTime;
        };

        video.addEventListener('timeupdate', syncAudioToVideo);
        video.addEventListener('play', handleVideoPlay);
        video.addEventListener('pause', handleVideoPause);
        video.addEventListener('seeked', handleVideoSeeked);

        return () => {
            video.removeEventListener('timeupdate', syncAudioToVideo);
            video.removeEventListener('play', handleVideoPlay);
            video.removeEventListener('pause', handleVideoPause);
            video.removeEventListener('seeked', handleVideoSeeked);
        };
    }, [calibrationSnippet]);

    const handleSubmit = async () => {
    try {
        await calibrationAPI.submit(videoId, volume);
        setShowCompleteModal(true);
    } catch (error) {
        console.error("Error submitting calibration:", error);
        alert("Failed to submit volume calibration");
    }
    };

    const handleCompleteModalClose = () => {
        setShowCompleteModal(false);
        navigate("/");
    };

    if (!video || !calibrationSnippet) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-xl">Loading...</div>
            </div>
        );
    }

    // get the translated video filename (full quality version, has translated audio)
    const translatedVideoFile = calibrationSnippet.video_filename_full;

    // for calibration, always use the balanced version for original audio overlay
    const originalAudioFile = calibrationSnippet.video_filename_balanced;

    return (
        <div className="min-h-screen bg-blue-900 p-6">
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h1 className="text-2xl font-bold mb-4">Volume Calibration</h1>
                    <p className="text-gray-600 mb-6 text-lg">
                    Adjust the volume of the original audio to your preferred level using the slider below.
                    </p>

                    <div className="space-y-6">
                    {/* Video Container with Two Audio Tracks */}
                    <div className="relative">
                        {/* Translated Video - plays at system volume */}
                        <video
                        ref={translatedVideoRef}
                        className="w-full rounded-lg"
                        loop
                        autoPlay
                        disablePictureInPicture
                        disableRemotePlayback
                        controlsList="nodownload noplaybackrate"
                        onContextMenu={(e) => e.preventDefault()}
                        src={`/videos/${translatedVideoFile}`}
                        >
                        Your browser does not support the video tag.
                        </video>
                    </div>

                    {/* Original Audio - volume controlled by slider, overlaid */}
                    <audio
                        ref={originalAudioRef}
                        loop
                        autoPlay
                        src={`/videos/${originalAudioFile}`}
                    />

                    {/* Volume Slider */}
                    <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">
                        Original Audio Volume: {Math.round(volume * 100)}%
                        </label>
                        <p className="text-sm text-gray-600 mb-2">
                        Adjust this slider to control the level of the original audio. Your system volume controls both audio tracks together.
                        </p>
                        <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        />
                        <div className="flex justify-between text-xs text-gray-500">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        onClick={handleSubmit}
                        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                        Submit and Continue to Survey
                    </button>
                    </div>
                </div>
            </div>
                  {/* Complete Modal */}
            {showCompleteModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-lg p-6 max-w-md w-full">
                    <h3 className="text-2xl font-bold mb-4">Conversation Complete!</h3>
                    <p className="mb-6">
                    You've completed all snippets for this conversation. Thank you for your participation!
                    </p>
                    {video.google_form_url && (
                    <a
                        href={video.google_form_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded text-center mb-4"
                    >
                        Fill Out Survey
                    </a>
                    )}
                    <button
                    onClick={handleCompleteModalClose}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded"
                    >
                    Return to Home
                    </button>
                </div>
            </div>
            )}
        </div>
    );
}

export default VolumeCalibrationPage;