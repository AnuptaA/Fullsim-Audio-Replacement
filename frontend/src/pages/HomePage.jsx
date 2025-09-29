import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { videoAPI, participantAPI } from "../services/api";

function HomePage() {
  const [videos, setVideos] = useState([]);
  const [participantCode, setParticipantCode] = useState("");
  const [participantCreated, setParticipantCreated] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const response = await videoAPI.list();
      setVideos(response.data);
    } catch (error) {
      console.error("Error loading videos:", error);
    }
  };

  const handleCreateParticipant = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await participantAPI.create({
        participant_code: participantCode,
        native_language: "English",
      });
      setParticipantCreated(true);
    } catch (error) {
      console.error("Error creating participant:", error);
      alert("Error creating participant. Code may already exist.");
    } finally {
      setLoading(false);
    }
  };

  const startVideo = (videoId) => {
    if (!participantCreated) {
      alert("Please create a participant first!");
      return;
    }
    navigate(`/video/${videoId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Language Learning Study
          </h1>
          <p className="text-xl text-gray-600">
            Immersive Spanish Conversation Experience
          </p>
        </div>

        {!participantCreated ? (
          <div className="max-w-md mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="mb-6">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-8 h-8 text-indigo-600"
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
                <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
                  Welcome!
                </h2>
                <p className="text-center text-gray-600">
                  Enter your participant code to begin the study
                </p>
              </div>

              <form onSubmit={handleCreateParticipant} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Participant Code
                  </label>
                  <input
                    type="text"
                    value={participantCode}
                    onChange={(e) => setParticipantCode(e.target.value)}
                    placeholder="e.g., PART001"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Creating..." : "Start Study"}
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div>
            <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
              Select a Conversation
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
                  onClick={() => startVideo(video.id)}
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
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
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
                            d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                          />
                        </svg>
                        {video.audio_type.replace(/_/g, " ")}
                      </div>
                    </div>

                    <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200">
                      Begin Conversation
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {videos.length === 0 && (
              <div className="text-center text-gray-500 mt-12">
                <p className="text-lg">No videos available yet.</p>
                <p className="text-sm mt-2">joe mama</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default HomePage;
