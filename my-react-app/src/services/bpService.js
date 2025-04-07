import axios from 'axios';

const API_URL = 'http://localhost:5000/api/bp/';

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

// Blood Pressure service
const bpService = {
  // Get blood pressure readings with optional date filters
  getReadings: async (startDate = null, endDate = null, limit = 100) => {
    try {
      let url = 'readings';
      const params = {};
      
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (limit) params.limit = limit;
      
      const response = await axiosInstance.get(url, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching BP readings:', error);
      throw error;
    }
  },
  
  // Add a new blood pressure reading
  addReading: async (bpData) => {
    try {
      const response = await axiosInstance.post('readings', bpData);
      return response.data;
    } catch (error) {
      console.error('Error adding BP reading:', error);
      throw error;
    }
  },
  
  // Delete a blood pressure reading
  deleteReading: async (readingId) => {
    try {
      const response = await axiosInstance.delete(`readings/${readingId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting BP reading:', error);
      throw error;
    }
  },
  
  // Upload BP readings from CSV file
  uploadCSV: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_URL}upload/csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error uploading CSV:', error);
      throw error;
    }
  },
  
  // Upload image for OCR processing
  uploadImage: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_URL}upload/image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  },
  
  // Get BP analytics
  getAnalytics: async (days = 30) => {
    try {
      const response = await axiosInstance.get('analytics', { params: { days } });
      return response.data;
    } catch (error) {
      console.error('Error fetching BP analytics:', error);
      throw error;
    }
  },
  
  // Detect anomalies using ML
  detectAnomalies: async () => {
    try {
      const response = await axiosInstance.get('anomalies');
      return response.data;
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      throw error;
    }
  },
  
  // Generate report (PDF or Excel)
  generateReport: async (startDate = null, endDate = null, type = 'pdf') => {
    try {
      const params = { type };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await axiosInstance.get('report', { params });
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  },
  
  // Download report
  downloadReport: async (reportPath) => {
    try {
      const response = await axiosInstance.get('report/download', {
        params: { path: reportPath },
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from path
      const filename = reportPath.split('/').pop();
      link.setAttribute('download', filename);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return true;
    } catch (error) {
      console.error('Error downloading report:', error);
      throw error;
    }
  }
};

export default bpService; 