import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://biaslabprototype-production.up.railway.app/';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Narratives
  async getNarratives() {
    const response = await api.get('/narratives');
    return response.data;
  },

  async getNarrativeDetail(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}`);
    return response.data;
  },

  async getNarrativeTimeline(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}/timeline`);
    return response.data;
  },

  async getNarrativeArticles(narrativeId) {
    const response = await api.get(`/narratives/${narrativeId}/articles`);
    return response.data;
  },

  // Articles
  async getArticles(params = {}) {
    const response = await api.get('/articles', { params });
    return response.data;
  },

  async getArticleDetail(articleId) {
    const response = await api.get(`/articles/${articleId}`);
    return response.data;
  },

  // Statistics
  async getStats() {
    const response = await api.get('/stats');
    return response.data;
  },
};

// Error handling wrapper
export const withErrorHandling = async (apiCall) => {
  try {
    return await apiCall();
  } catch (error) {
    console.error('API Error:', error);
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.data.detail || error.response.statusText}`);
    } else if (error.request) {
      // Network error
      throw new Error('Network Error: Unable to connect to the server');
    } else {
      // Other error
      throw new Error(`Error: ${error.message}`);
    }
  }
};

export default api;