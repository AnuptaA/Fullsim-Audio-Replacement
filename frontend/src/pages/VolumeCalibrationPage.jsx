import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { videoAPI, calibrationAPI, sessionAPI } from "../services/api";

function VolumeCalibrationPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  
  const [video, setVideo] = useState(null);
  const [calibrationSnippet, setCalibrationSnippet] = useState(null);
  const [volume, setVolume] = useState(0.5);
  const [participantId, setParticipantId] = useState("");
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [calibrationExists, setCalibrationExists] = useState(false);
  
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
            setCalibrationSnippet(lastSnippet);
            
        } catch (error) {
            console.error("Error loading video:", error);
        }
    };

    useEffect(() => {
        if (participantId && videoId) {
            loadExistingCalibration();
        }
    }, [participantId, videoId]);

    const loadExistingCalibration = async () => {
        try {
            const response = await calibrationAPI.get(videoId);
            if (response.data.optimal_volume !== null) {
                setVolume(response.data.optimal_volume);
                setCalibrationExists(true);
                console.log("Loaded existing calibration:", response.data.optimal_volume);
            }
        } catch (error) {
            console.error("Error loading calibration:", error);
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
            
            try {
                await sessionAPI.end(videoId);
                console.log("Video session ended");
            } catch (sessionError) {
                console.error("Error ending session:", sessionError);
            }
            
            setCalibrationExists(true);
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

  const translatedVideoFile = calibrationSnippet.video_filename_full;
  const originalAudioFile = calibrationSnippet.video_filename_muffled;

    return (
        <div className="min-h-screen bg-blue-900 p-6">
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h1 className="text-2xl font-bold mb-4">Volume Calibration</h1>
                    <p className="text-gray-600 mb-6 text-lg">
                    Adjust the volume of the original audio to your preferred level using the slider below.
                    </p>

                    {calibrationExists && (
                        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                            <p className="font-medium">Volume calibration already submitted.</p>
                            <p className="text-sm">Your preferred volume: {Math.round(volume * 100)}%</p>
                        </div>
                    )}

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
                            src={translatedVideoFile}
                        >
                        Your browser does not support the video tag.
                        </video>
                    </div>

                    {/* Original Audio - volume controlled by slider, overlaid */}
                    <video
                        ref={originalAudioRef}
                        loop
                        autoPlay
                        style={{ display: 'none' }}
                        playsInline
                        src={originalAudioFile}
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
                            disabled={calibrationExists}
                            className={`w-full h-2 bg-gray-200 rounded-lg appearance-none ${
                                calibrationExists ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
                            }`}
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
                            {calibrationExists ? "Continue" : "Submit and Continue"}
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
    )};

export default VolumeCalibrationPage;