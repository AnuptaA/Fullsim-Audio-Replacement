import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:3000/api' 
  : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const participantAPI = {
  create: (data) => api.post('/participants/', data),
  get: (id) => api.get(`/participants/${id}`),
  list: () => api.get('/participants/'),
};

export const videoAPI = {
  list: () => api.get('/videos/'),
  get: (id) => api.get(`/videos/${id}`),
  getSnippets: (videoId) => api.get(`/videos/${videoId}/snippets`),
};

export const interactionAPI = {
  create: (data) => api.post('/interactions/', data),
  complete: (id) => api.put(`/interactions/${id}/complete`),
  getByParticipant: (participantId) => 
    api.get(`/interactions/participant/${participantId}`),
};

export const healthCheck = () => api.get('/health');

export default api;