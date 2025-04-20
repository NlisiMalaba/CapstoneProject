import axios from 'axios';

const API_URL = '/api/prediction';

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

const predictionService = {
  // Save patient data
  savePatientData: async (patientData) => {
    try {
      const response = await axiosInstance.post('/patient-data', patientData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get patient data
  getPatientData: async () => {
    try {
      const response = await axiosInstance.get('/patient-data');
      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        // Patient data not found, return null instead of throwing
        return null;
      }
      throw error;
    }
  },
  
  // Get prediction for the current user
  getPrediction: async () => {
    try {
      const response = await axiosInstance.post('/predict');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get prediction history
  getPredictionHistory: async () => {
    try {
      const response = await axiosInstance.get('/history');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default predictionService; 