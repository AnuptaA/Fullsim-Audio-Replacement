import { useState, useEffect } from "react";
import { participantAPI, videoAPI, healthCheck } from "../services/api";

function TestPage() {
  const [health, setHealth] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [videos, setVideos] = useState([]);
  const [newParticipant, setNewParticipant] = useState({
    participant_code: "",
    native_language: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [healthRes, participantsRes, videosRes] = await Promise.all([
        healthCheck(),
        participantAPI.list(),
        videoAPI.list(),
      ]);

      setHealth(healthRes.data);
      setParticipants(participantsRes.data);
      setVideos(videosRes.data);
    } catch (err) {
      setError(err.message);
      console.error("Error loading data:", err);
    }
  };

  const handleCreateParticipant = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await participantAPI.create(newParticipant);
      setNewParticipant({ participant_code: "", native_language: "" });
      await loadData();
      alert("Participant created successfully!");
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">
          Backend Test Page
        </h1>

        {/* Health Check */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Health Check</h2>
          {health ? (
            <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
              {JSON.stringify(health, null, 2)}
            </pre>
          ) : (
            <p className="text-gray-500">Loading...</p>
          )}
        </div>

        {/* Create Participant */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Create Participant</h2>
          <form onSubmit={handleCreateParticipant} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Participant Code
              </label>
              <input
                type="text"
                value={newParticipant.participant_code}
                onChange={(e) =>
                  setNewParticipant({
                    ...newParticipant,
                    participant_code: e.target.value,
                  })
                }
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Native Language
              </label>
              <input
                type="text"
                value={newParticipant.native_language}
                onChange={(e) =>
                  setNewParticipant({
                    ...newParticipant,
                    native_language: e.target.value,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg disabled:opacity-50 transition"
            >
              {loading ? "Creating..." : "Create Participant"}
            </button>
          </form>
          {error && <p className="text-red-600 mt-4">{error}</p>}
        </div>

        {/* Participants List */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">
            Participants ({participants.length})
          </h2>
          {participants.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Language
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {participants.map((p) => (
                    <tr key={p.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {p.native_language || "N/A"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {new Date(p.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">No participants yet</p>
          )}
        </div>

        {/* Videos List */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">
            Videos ({videos.length})
          </h2>
          {videos.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {videos.map((v) => (
                <div
                  key={v.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-bold text-lg mb-2">{v.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{v.description}</p>
                  <div className="text-sm text-gray-500 space-y-1">
                    <p>
                      <strong>ID:</strong> {v.video_id}
                    </p>
                    <p>
                      <strong>Snippets:</strong> {v.total_snippets}
                    </p>
                    <p>
                      <strong>Audio:</strong> {v.audio_type}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">
              No videos yet. Run seed_data.py to add sample videos.
            </p>
          )}
        </div>

        <button
          onClick={loadData}
          className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
}

export default TestPage;
