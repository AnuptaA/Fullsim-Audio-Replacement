import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { videoAPI, responseAPI, uploadRecording } from "../services/api";

function VideoPlayerPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();

  const [video, setVideo] = useState(null);
  const [currentSnippetIndex, setCurrentSnippetIndex] = useState(0);
  const [participantId, setParticipantId] = useState("");
  const [existingResponses, setExistingResponses] = useState({});

  const [hasPlayedVideo, setHasPlayedVideo] = useState(false);
  const [hasVideoEnded, setHasVideoEnded] = useState(false);
  const [recording, setRecording] = useState(null);
  const [recordingUrl, setRecordingUrl] = useState(null);
  const [savedRecordingPath, setSavedRecordingPath] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mcqAnswers, setMcqAnswers] = useState([]);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);

  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  useEffect(() => {
    const storedId = localStorage.getItem("participantId");
    if (!storedId) {
      alert("Please enter your participant ID first");
      navigate("/");
      return;
    }
    setParticipantId(storedId);
    loadVideo();
  }, [videoId, navigate]);

  const loadVideo = async () => {
    try {
      const response = await videoAPI.get(videoId);
      //   console.log("Video data:", response.data);

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
    setHasPlayedVideo(false);
    setHasVideoEnded(false);

    if (existingResponse) {
      //   console.log("Loading existing response for snippet:", currentSnippetIndex);
      setSavedRecordingPath(existingResponse.audio_recording_path || null);
      setMcqAnswers(existingResponse.mcq_answers || []);
      setHasSubmitted(!!existingResponse.submitted_at);
    } else {
      setSavedRecordingPath(null);
      setMcqAnswers([]);
      setHasSubmitted(false);
    }
    setRecording(null);
    setRecordingUrl(null);
  }, [currentSnippetIndex, existingResponse]);

  useEffect(() => {
    return () => {
      if (recordingUrl) {
        URL.revokeObjectURL(recordingUrl);
      }
    };
  }, [recordingUrl]);

  const handleVideoPlay = () => {
    setHasPlayedVideo(true);
  };

  const handleVideoEnd = () => {
    setHasVideoEnded(true);
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
        // console.log("=== Recording Stopped ===");
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
        const url = URL.createObjectURL(blob);
        // console.log("Created blob URL:", url);
        setRecordingUrl(url);

        stream.getTracks().forEach((track) => {
          //   console.log("Stopping track:", track.kind);
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
    // console.log("=== Starting Submit ===");
    // console.log("Recording:", recording);
    // console.log("Saved path:", savedRecordingPath);
    // console.log("MCQ answers:", mcqAnswers);
    // console.log("MCQ questions length:", currentSnippet.mcq_questions.length);

    if (!recording && !savedRecordingPath) {
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
      let audioPath = savedRecordingPath;

      if (recording && !savedRecordingPath) {
        // console.log("=== Uploading Recording ===");
        // console.log("Blob size:", recording.size);
        // console.log("Blob type:", recording.type);
        // console.log("Participant ID:", participantId);
        // console.log("Video ID:", videoId);
        // console.log("Snippet index:", currentSnippetIndex);

        try {
          const uploadResponse = await uploadRecording(
            recording,
            participantId,
            videoId,
            currentSnippetIndex
          );
          //   console.log("Upload response:", uploadResponse.data);
          audioPath = uploadResponse.data.path;
          //   console.log("Audio path:", audioPath);
          setSavedRecordingPath(audioPath);
        } catch (uploadError) {
          console.error("Upload error:", uploadError);
          console.error("Upload error response:", uploadError.response?.data);
          throw new Error(
            `Failed to upload recording: ${
              uploadError.response?.data?.error || uploadError.message
            }`
          );
        }
      }

      const responseData = {
        participant_id: participantId,
        snippet_id: currentSnippetId,
        audio_recording_path: audioPath,
        audio_duration: 5.0,
        mcq_answers: mcqAnswers,
        submit: true,
      };

      //   console.log("=== Submitting Response ===");
      //   console.log("Response data:", responseData);

      try {
        const submitResponse = await responseAPI.create(responseData);
        // console.log("Submit response:", submitResponse.data);
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

      const isLastSnippet =
        video?.snippets && currentSnippetIndex === video.snippets.length - 1;

      if (isLastSnippet) {
        setShowCompleteModal(true);
      }
    } catch (error) {
      console.error("=== Submit Failed ===");
      console.error("Error:", error);
      alert(`Failed to submit: ${error.message}`);
    } finally {
      setIsUploading(false);
      //   console.log("=== Submit Complete ===");
    }
  };

  const handleNext = () => {
    if (!video?.snippets) return;

    if (recordingUrl) {
      URL.revokeObjectURL(recordingUrl);
    }

    if (currentSnippetIndex < video.snippets.length - 1) {
      setCurrentSnippetIndex(currentSnippetIndex + 1);
    } else {
      setShowCompleteModal(true);
    }
  };

  const handleCompleteModalClose = () => {
    setShowCompleteModal(false);
    navigate("/");
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <button
            onClick={() => navigate("/")}
            className="text-white hover:text-gray-300 flex items-center"
          >
            ← Back to Home
          </button>
          <div className="text-white">
            Snippet {currentSnippetIndex + 1} of {video.snippets.length}
          </div>
        </div>

        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8 mb-6">
          <h2 className="text-3xl font-bold text-white mb-4">{video.title}</h2>
          <p className="text-gray-300 mb-6">{video.description}</p>

          {/* Instruction text */}
          {!hasPlayedVideo && !hasSubmitted && (
            <div className="mb-4 p-4 bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg">
              <p className="text-blue-200 text-center font-semibold">
                Press play below to start the snippet
              </p>
            </div>
          )}

          {/* Video Player */}
          <div className="space-y-4 mb-6">
            <video
              className="w-full rounded-lg"
              controls
              onPlay={handleVideoPlay}
              onEnded={handleVideoEnd}
              src={`/videos/${currentSnippet.video_filename}`}
            >
              Your browser does not support the video tag.
            </video>
            {/* <audio
              controls
              onPlay={handleVideoPlay}
              src={`/videos/${currentSnippet.audio_filename}`}
            >
              Your browser does not support the audio element.
            </audio> */}
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
                      src={`/${savedRecordingPath}`}
                      className="w-full"
                      onError={(e) => {
                        console.error("Error loading saved recording:", e);
                        console.error("Path:", savedRecordingPath);
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
                      ? "Next Snippet →"
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

      {/* Complete Modal */}
      {showCompleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-2xl font-bold mb-4">Conversation Complete!</h3>
            <p className="mb-6">
              You've completed all snippets for this conversation. Thank you for your
              participation!
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

export default VideoPlayerPage;
