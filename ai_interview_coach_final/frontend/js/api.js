/**
 * Unified API Client for AI Interview Coaching System
 */
const API_BASE = '/api';

const API = {
  getAuthToken() {
    return localStorage.getItem('access_token');
  },

  setAuthToken(token) {
    localStorage.setItem('access_token', token);
  },

  clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
  },

  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json'
    };
    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = this.getHeaders(options.auth !== false);
    
    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401 && options.auth !== false) {
          this.clearAuth();
          if (!window.location.pathname.includes('login.html')) {
            window.location.href = 'login.html';
          }
        }
        throw new Error(data.detail || 'API request failed');
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth
  register(userData) {
    return this.request('/auth/register', { method: 'POST', body: JSON.stringify(userData), auth: false });
  },

  login(credentials) {
    return this.request('/auth/login', { method: 'POST', body: JSON.stringify(credentials), auth: false });
  },

  getMe() {
    return this.request('/auth/me');
  },

  // Profile
  getProfile() {
    return this.request('/profile');
  },

  updateProfile(profileData) {
    return this.request('/profile', { method: 'PUT', body: JSON.stringify(profileData) });
  },

  getSkillGap() {
    return this.request('/profile/skill-gap');
  },

  // Interviews
  createInterview(config) {
    return this.request('/interviews', { method: 'POST', body: JSON.stringify(config) });
  },

  listInterviews() {
    return this.request('/interviews');
  },

  getInterview(id) {
    return this.request(`/interviews/${id}`);
  },

  startInterview(id) {
    return this.request(`/interviews/${id}/start`, { method: 'POST' });
  },

  getCurrentQuestion(id) {
    return this.request(`/interviews/${id}/questions/current`);
  },

  submitAnswer(id, questionId, answerText) {
    return this.request(`/interviews/${id}/answer?question_id=${questionId}`, {
      method: 'POST',
      body: JSON.stringify({ answer_text: answerText })
    });
  },

  completeInterview(id) {
    return this.request(`/interviews/${id}/complete`, { method: 'POST' });
  },

  getInterviewFeedback(id) {
    return this.request(`/interviews/${id}/feedback`);
  },

  getDetailedReport(id) {
    return this.request(`/reports/${id}`);
  },

  // Dashboard
  getDashboard() {
    return this.request('/dashboard');
  },

  // Seed
  seedDemoData() {
    return this.request('/seed/demo-data', { method: 'POST', auth: false });
  }
};
