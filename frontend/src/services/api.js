import axios from "axios";

// in prod, use relative URLs; in dev, use full URL
const API_BASE_URL = import.meta.env.DEV ? "http://localhost:3000/api" : "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  },
});

api.interceptors.request.use((config) => {
  // admin token takes precedence
  const adminToken = localStorage.getItem("adminToken");
  if (adminToken) {
    config.headers.Authorization = `Bearer ${adminToken}`;
    return config;
  }
  
  // use participant token if available
  const participantToken = localStorage.getItem("participantToken");
  if (participantToken) {
    config.headers.Authorization = `Bearer ${participantToken}`;
  }
  
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("adminToken");
      localStorage.removeItem("participantToken");
      if (window.location.pathname.startsWith("/admin")) {
        window.location.href = "/admin/login";
      }
    }
    if (error.response?.status === 403) {
      console.error("API authentication failed - invalid credentials");
    }
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const requestParticipantToken = async (participantId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/participant-token`, {
      participant_id: participantId
    });
    const token = response.data.token;
    localStorage.setItem('participantToken', token);
    return response.data;
  } catch (error) {
    console.error('Error getting participant token:', error);
    throw error;
  }
};

export const participantAPI = {
  validate: (participantId) => axios.post(`${API_BASE_URL}/participants/validate`, { participant_id: participantId }),
  get: (participantId) => api.get(`/participants/${participantId}`)
};

export const videoAPI = {
  list: () => api.get("/videos/"),
  get: (id) => api.get(`/videos/${id}`),
  getSnippets: (videoId) => api.get(`/videos/${videoId}/snippets`),
  getAudioAssignments: (videoId) => api.get(`/videos/${videoId}/audio-assignments`),
};

export const responseAPI = {
  create: (data) => api.post("/responses/", data),
  get: (responseId) => api.get(`/responses/${responseId}`),
  getParticipantVideoResponses: (participantId, videoId) =>
    api.get(`/responses/participant/${participantId}/video/${videoId}`),
};

export const adminAPI = {
  login: (password) => api.post("/admin/login", { password }),
  listParticipants: () => api.get("/admin/participants"),
  createParticipant: (data) => api.post("/admin/participants", data),
  deleteParticipant: (id) => api.delete(`/admin/participants/${id}`),
};

export const calibrationAPI = {
  submit: (videoId, optimalVolume) => 
    api.post('/calibration/', { video_id: videoId, optimal_volume: optimalVolume }),
  get: (videoId) => 
    api.get(`/calibration/video/${videoId}`),
};

export const sessionAPI = {
  start: (videoId) =>
    api.post("/sessions/start", {
      participant_id: localStorage.getItem('participantId'),
      video_id: parseInt(videoId),
    }),
  end: (videoId) =>
    api.post("/sessions/end", {
      participant_id: localStorage.getItem('participantId'),
      video_id: parseInt(videoId),
    }),
  get: (videoId) => api.get(`/sessions/participant/${localStorage.getItem('participantId')}/video/${videoId}`),
};

export const healthCheck = () => api.get("/health");

export default api;
