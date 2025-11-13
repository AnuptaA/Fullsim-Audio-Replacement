import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

function SystemCalibrationPage() {
  const R2_BASE_URL = import.meta.env.VITE_R2_BASE_URL;
  const navigate = useNavigate();
  const videoRef = useRef(null);
  
  const [participantId, setParticipantId] = useState("");
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showError, setShowError] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const CALIBRATION_VIDEO = `${R2_BASE_URL}/audiocalibration_muffled.mp4`;
  const MCQ_QUESTION = "What is the second sentence in the video?";
  const MCQ_OPTIONS = [
    "Prunes are dried plums",
    "Wine is made from grapes",
    "Figs grow on trees",
    "Pomegranates are red"
  ];
  const CORRECT_ANSWER = 0; // "Prunes are dried plums"

  useEffect(() => {
    const storedId = localStorage.getItem("participantId");
    const calibrated = localStorage.getItem("systemAudioCalibrated");
    
    if (!storedId) {
      alert("Please enter your participant ID first");
      navigate("/");
      return;
    }
    
    setParticipantId(storedId);
    
    // if already calibrated, redirect to home
    if (calibrated === "true") {
      navigate("/");
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("participantId");
    localStorage.removeItem("participantToken");
    localStorage.removeItem("systemAudioCalibrated");
    navigate("/");
  };

  const handleSubmit = () => {
    if (selectedAnswer === null) {
      alert("Please select an answer before continuing.");
      return;
    }

    if (selectedAnswer !== CORRECT_ANSWER) {
      setShowError(true);
      return;
    }

    // correct answer, show confirmation modal
    setShowError(false);
    setShowConfirmModal(true);
  };

  const handleConfirmCalibration = () => {
    localStorage.setItem("systemAudioCalibrated", "true");
    navigate("/");
  };

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-8">
        <div className="max-w-3xl w-full bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
          {/* Header with Logout */}
          <div className="flex justify-between items-start mb-8">
            <div className="text-center flex-1">
              <div className="w-20 h-20 bg-blue-500 bg-opacity-30 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-10 h-10 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                  />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-white mb-2">
                System Audio Calibration
              </h1>
              <p className="text-gray-300">
                Before we begin, let's set up your audio!
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="text-white hover:text-gray-300 flex items-center text-sm"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>

          {/* Instructions */}
          <div className="bg-blue-900 bg-opacity-30 border border-blue-400 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-3">
              Instructions:
            </h2>
            <ol className="space-y-3 text-gray-200">
              <li className="flex items-start">
                <span className="font-bold text-blue-300 mr-3">1.</span>
                <span>
                  Watch the video below and <strong>adjust your device's system volume</strong> so you can clearly hear the audio.
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-300 mr-3">2.</span>
                <span>
                  You can pause, rewind, or replay the video as needed.
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-300 mr-3">3.</span>
                <span>
                  Answer the comprehension question below to confirm you can hear clearly.
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-300 mr-3">4.</span>
                <span>
                  <strong className="text-yellow-300">Important:</strong> Once you continue, please <strong>do not change your system volume</strong> for the rest of the study.
                </span>
              </li>
            </ol>
          </div>

          {/* Video Player */}
          <div className="bg-white bg-opacity-10 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold text-white mb-4">
              Calibration Video
            </h3>
            <div className="bg-black rounded-lg overflow-hidden mb-4">
              <video
                ref={videoRef}
                className="w-full"
                controls
                src={CALIBRATION_VIDEO}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>

          {/* MCQ Section */}
          <div className="bg-white bg-opacity-10 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold text-white mb-4">
              Comprehension Check
            </h3>
            <p className="text-gray-300 mb-4 font-medium">
              {MCQ_QUESTION}
            </p>

            <div className="space-y-3">
              {MCQ_OPTIONS.map((option, index) => (
                <label
                  key={index}
                  className={`flex items-center p-4 rounded-lg cursor-pointer transition ${
                    selectedAnswer === index
                      ? 'bg-blue-600 bg-opacity-50 border-2 border-blue-400'
                      : 'bg-white bg-opacity-5 hover:bg-opacity-10 border-2 border-transparent'
                  }`}
                >
                  <input
                    type="radio"
                    name="answer"
                    value={index}
                    checked={selectedAnswer === index}
                    onChange={() => {
                      setSelectedAnswer(index);
                      setShowError(false);
                    }}
                    className="w-5 h-5 mr-3"
                  />
                  <span className="text-white">{option}</span>
                </label>
              ))}
            </div>

            {showError && (
              <div className="mt-4 bg-red-900 bg-opacity-30 border border-red-500 rounded-lg p-3">
                <p className="text-red-300 text-sm flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  Incorrect answer. Please adjust your volume and try again. Make sure you can clearly hear the audio.
                </p>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={selectedAnswer === null}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:cursor-not-allowed text-white font-bold py-4 rounded-lg transition duration-200 text-lg"
          >
            {selectedAnswer === null ? "Select an Answer" : "Submit & Continue"}
          </button>

          {/* Warning */}
          <div className="mt-6 bg-yellow-900 bg-opacity-30 border border-yellow-500 rounded-lg p-4">
            <div className="flex items-center justify-center align-center">
              <svg className="w-6 h-6 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-yellow-200 text-sm">
                After continuing, please keep your system volume at this level throughout the entire study. Changing it may affect the research data.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                Correct! Audio Calibrated
              </h3>
              <p className="text-gray-600 mb-4">
                Great! You answered correctly, which means you can hear the audio clearly.
              </p>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleConfirmCalibration}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg transition"
              >
                Continue to Study
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default SystemCalibrationPage;