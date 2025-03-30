import axios from 'axios';

// Adjust this URL to match your backend API
const API_URL = 'http://localhost:5000/api/auth/';

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add interceptor to add bearer token to requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication service
const authService = {
  // Register a new user
  register: async (username, email, password) => {
    try {
      const response = await axiosInstance.post('register', {
        username,
        email,
        password
      });
      if (response.data.token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Login user
  login: async (username, password) => {
    try {
      const response = await axiosInstance.post('login', {
        username,
        password
      });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        
        // Create and store user object with available data
        const userData = {
          id: response.data.user_id,
          username: response.data.username,
          role: response.data.role
        };
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        console.warn('No access token received in login response');
      }
      return response.data;
    } catch (error) {
      console.error('Login request failed:', error);
      throw error;
    }
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  // Get current user info
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        console.error('Error parsing user data:', e);
        return null;
      }
    }
    return null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return localStorage.getItem('token') !== null;
  }
};

export default authService; 