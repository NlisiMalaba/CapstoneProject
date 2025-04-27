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
      return response.data.patient_data;
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
      if (response.data && response.data.success) {
        return response.data.prediction;
      } else {
        throw new Error(response.data.message || 'Failed to get prediction');
      }
    } catch (error) {
      // Extract structured error data from response if available
      if (error.response && error.response.data) {
        const errorData = error.response.data;
        const customError = new Error(errorData.message || 'Failed to get prediction');
        
        // Attach additional error data for structured handling
        if (errorData.missing_fields) {
          customError.missing_fields = errorData.missing_fields;
        }
        
        throw customError;
      }
      throw error;
    }
  },
  
  // Get prediction history - returns array of predictions
  getPredictionHistory: async () => {
    try {
      const response = await axiosInstance.get('/history');
      if (response.data && response.data.success) {
        return response.data.prediction_history || [];
      }
      console.warn('Unexpected response format from prediction history endpoint:', response.data);
      return [];
    } catch (error) {
      console.error('Error fetching prediction history:', error);
      
      // Check if the error is due to the API returning a specific error message
      if (error.response && error.response.data) {
        console.error('Server error details:', error.response.data);
        
        // If there's a message in the error, throw it with more context
        if (error.response.data.message) {
          throw new Error(`Server error: ${error.response.data.message}`);
        }
      }
      
      // For other errors or if status is 404, return empty array instead of throwing
      return [];
    }
  },
  
  // Get the latest prediction
  getLatestPrediction: async () => {
    try {
      const history = await predictionService.getPredictionHistory();
      return history.length > 0 ? history[0] : null;
    } catch (error) {
      throw error;
    }
  }
};

export default predictionService; 