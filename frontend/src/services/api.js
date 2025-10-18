import axios from "axios";

// in prod, use relative URLs; in dev, use full URL
const API_BASE_URL = import.meta.env.DEV ? "http://localhost:3000/api" : "/api";

// // API Client Secret - should be in .env for production
// const API_CLIENT_SECRET =
//   import.meta.env.VITE_API_CLIENT_SECRET || "dev-secret-key";

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

export const uploadRecording = async (
  audioBlob,
  participantId,
  videoId,
  snippetIndex
) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("participant_id", participantId);
  formData.append("video_id", videoId);
  formData.append("snippet_index", snippetIndex);

  // use relative URL in prod, full URL in dev
  const uploadUrl = import.meta.env.DEV
    ? "http://localhost:3000/api/upload-recording"
    : "/api/upload-recording";

  const participantToken = localStorage.getItem("participantToken");

  return axios.post(uploadUrl, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
      ...(participantToken && { Authorization: `Bearer ${participantToken}` }), 
    },
  });
};

export const healthCheck = () => api.get("/health");

export default api;
