import { useState, useEffect } from 'react';
import { participantAPI, videoAPI, healthCheck } from '../services/api';

function TestPage() {
  const [health, setHealth] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [videos, setVideos] = useState([]);
  const [newParticipant, setNewParticipant] = useState({
    participant_code: '',
    native_language: ''
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
        videoAPI.list()
      ]);
      
      setHealth(healthRes.data);
      setParticipants(participantsRes.data);
      setVideos(videosRes.data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading data:', err);
    }
  };

  const handleCreateParticipant = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await participantAPI.create(newParticipant);
      setNewParticipant({ participant_code: '', native_language: '' });
      await loadData();
      alert('Participant created successfully!');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Backend Test Page</h1>
      
      {/* health check */}
      <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
        <h2>Health Check</h2>
        {health ? (
          <pre>{JSON.stringify(health, null, 2)}</pre>
        ) : (
          <p>Loading...</p>
        )}
      </div>

      {/* test create participant form */}
      <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#e8f5e9', borderRadius: '5px' }}>
        <h2>Create Participant</h2>
        <form onSubmit={handleCreateParticipant}>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              Participant Code:
              <input
                type="text"
                value={newParticipant.participant_code}
                onChange={(e) => setNewParticipant({...newParticipant, participant_code: e.target.value})}
                required
                style={{ marginLeft: '10px', padding: '5px' }}
              />
            </label>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              Native Language:
              <input
                type="text"
                value={newParticipant.native_language}
                onChange={(e) => setNewParticipant({...newParticipant, native_language: e.target.value})}
                style={{ marginLeft: '10px', padding: '5px' }}
              />
            </label>
          </div>
          <button 
            type="submit" 
            disabled={loading}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            {loading ? 'Creating...' : 'Create Participant'}
          </button>
        </form>
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      </div>

      {/* list of participatns */}
      <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#fff3e0', borderRadius: '5px' }}>
        <h2>Participants ({participants.length})</h2>
        {participants.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '8px', textAlign: 'left' }}>ID</th>
                <th style={{ padding: '8px', textAlign: 'left' }}>Code</th>
                <th style={{ padding: '8px', textAlign: 'left' }}>Language</th>
                <th style={{ padding: '8px', textAlign: 'left' }}>Created</th>
              </tr>
            </thead>
            <tbody>
              {participants.map((p) => (
                <tr key={p.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '8px' }}>{p.id}</td>
                  <td style={{ padding: '8px' }}>{p.participant_code}</td>
                  <td style={{ padding: '8px' }}>{p.native_language || 'N/A'}</td>
                  <td style={{ padding: '8px' }}>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No participants yet</p>
        )}
      </div>

      {/* videos list */}
      <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '5px' }}>
        <h2>Videos ({videos.length})</h2>
        {videos.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
            {videos.map((v) => (
              <div key={v.id} style={{ padding: '15px', backgroundColor: 'white', borderRadius: '5px', border: '1px solid #ddd' }}>
                <h3 style={{ marginTop: 0 }}>{v.title}</h3>
                <p><strong>Video ID:</strong> {v.video_id}</p>
                <p><strong>Description:</strong> {v.description}</p>
                <p><strong>Snippets:</strong> {v.total_snippets}</p>
                <p><strong>Audio Type:</strong> {v.audio_type}</p>
                <p><strong>Created:</strong> {new Date(v.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        ) : (
          <p>No videos yet. Run seed_data.py to add sample videos.</p>
        )}
      </div>

      <button 
        onClick={loadData}
        style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
      >
        Refresh Data
      </button>
    </div>
  );
}

export default TestPage;