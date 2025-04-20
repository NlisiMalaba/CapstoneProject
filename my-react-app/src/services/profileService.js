import axios from 'axios';

const API_URL = '/api/user-profile';

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

const profileService = {
  // Get user profile
  getProfile: async () => {
    try {
      const response = await axiosInstance.get('');
      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        // Profile not found, return null instead of throwing
        return null;
      }
      throw error;
    }
  },

  // Create user profile
  createProfile: async (profileData) => {
    try {
      const response = await axiosInstance.post('', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update user profile
  updateProfile: async (profileData) => {
    try {
      const response = await axiosInstance.put('', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete user profile
  deleteProfile: async () => {
    try {
      const response = await axiosInstance.delete('');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Calculate BMI based on height and weight
  calculateBMI: (height, weight) => {
    if (!height || !weight || height <= 0 || weight <= 0) {
      return null;
    }
    // Convert height from cm to meters
    const heightInMeters = height / 100;
    // Calculate BMI: weight (kg) / height² (m)
    const bmi = weight / (heightInMeters * heightInMeters);
    return parseFloat(bmi.toFixed(2));
  }
};

export default profileService; 