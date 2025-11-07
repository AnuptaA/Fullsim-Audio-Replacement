import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { videoAPI, participantAPI, requestParticipantToken } from "../services/api";

function HomePage() {
  const [videos, setVideos] = useState([]);
  const [participantId, setParticipantId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isValidated, setIsValidated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const storedId = localStorage.getItem("participantId");
    const storedToken = localStorage.getItem("participantToken");
    if (storedId && storedToken) {
      setParticipantId(storedId);
      setIsValidated(true);
      loadVideos();
    }
  }, []);

  const loadVideos = async () => {
    try {
      const response = await videoAPI.list();
      setVideos(response.data);
    } catch (error) {
      console.error("Error loading videos:", error);
    }
  };

  const validateParticipant = async (id) => {
    setLoading(true);
    setError("");
    try {
      // validate the ID
      const validateResponse = await participantAPI.validate(id);
      if (validateResponse.data.valid) {
        await requestParticipantToken(id);
        
        localStorage.setItem("participantId", id);
        setParticipantId(id);
        setIsValidated(true);

        const videoResponse = await videoAPI.list();
         setVideos(videoResponse.data);
      } else {
        setError("Invalid Participant ID");
        setIsValidated(false);
        localStorage.removeItem("participantId");
        localStorage.removeItem("participantToken");
      }
    } catch (err) {
      setError(
        "Invalid Participant ID: " +
          (err.response?.data?.error || "Unknown error")
      );
      setIsValidated(false);
      localStorage.removeItem("participantId");
      localStorage.removeItem("participantToken");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateParticipant(participantId.toUpperCase().trim());
  };

  const startVideo = (videoId) => {
    if (!isValidated) {
      alert("Please enter a valid participant ID first!");
      return;
    }
    navigate(`/video/${videoId}`);
  };

  if (!isValidated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-10 h-10 text-indigo-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome!</h1>
            <p className="text-gray-600">Language Learning Study</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Participant ID
              </label>
              <input
                type="text"
                value={participantId}
                onChange={(e) => setParticipantId(e.target.value.toUpperCase())}
                placeholder="Enter your ID (e.g., A1B2C3D4)"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-center font-mono text-lg"
              />
              <p className="text-sm text-gray-500 mt-2">
                Enter the ID provided to you by email
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:opacity-50"
            >
              {loading ? "Validating..." : "Continue"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a
              href="/admin/login"
              className="text-indigo-600 hover:text-indigo-700 text-sm"
            >
              Admin Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  Your Participant ID
                </h2>
                <p className="text-3xl font-mono font-bold text-indigo-600 mt-2">
                  {participantId}
                </p>
              </div>
              <button
                onClick={() => {
                  localStorage.removeItem("participantId");
                  setIsValidated(false);
                  setParticipantId("");
                }}
                className="text-gray-600 hover:text-gray-800 underline"
              >
                Use Different ID
              </button>
            </div>
          </div>

          <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
            Select a Conversation
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((video) => (
              <div
                key={video.id}
                className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
                onClick={() => startVideo(video.video_id)}
              >
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-32 flex items-center justify-center">
                  <svg
                    className="w-16 h-16 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </div>

                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    {video.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {video.description}
                  </p>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-500">
                      <svg
                        className="w-4 h-4 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
                        />
                      </svg>
                      {video.total_snippets} snippets
                    </div>
                  </div>

                  <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200">
                    Begin Conversation
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
