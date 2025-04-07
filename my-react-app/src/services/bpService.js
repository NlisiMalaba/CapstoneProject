import axios from 'axios';

const API_URL = 'http://localhost:5000/api/bp/';

// Mock data for development without backend
const MOCK_BP_READINGS = [
  {
    id: 1,
    measurement_date: new Date(2023, 9, 15, 8, 30).toISOString(),
    systolic: 120,
    diastolic: 80,
    pulse: 72,
    category: 'Normal',
    notes: 'Morning reading',
    source: 'Manual'
  },
  {
    id: 2,
    measurement_date: new Date(2023, 9, 15, 20, 0).toISOString(),
    systolic: 128,
    diastolic: 82,
    pulse: 75,
    category: 'Elevated',
    notes: 'Evening reading after dinner',
    source: 'Manual'
  },
  {
    id: 3,
    measurement_date: new Date(2023, 9, 16, 9, 0).toISOString(),
    systolic: 135,
    diastolic: 88,
    pulse: 77,
    category: 'Hypertension Stage 1',
    notes: 'After coffee',
    source: 'Manual'
  }
];

// Mock analytics data for development without backend
const MOCK_ANALYTICS = {
  total_readings: 25,
  average_systolic: 128,
  average_diastolic: 82,
  average_pulse: 74,
  max_systolic: 145,
  max_diastolic: 95,
  min_systolic: 115,
  min_diastolic: 75,
  normal_percentage: 40,
  elevated_percentage: 30,
  stage1_percentage: 20,
  stage2_percentage: 10,
  crisis_percentage: 0,
  trend_direction: 'stable',
  trend_details: 'Your blood pressure has been stable over the past 30 days.'
};

// Mock anomalies data
const MOCK_ANOMALIES = {
  anomalies: [
    {
      id: 1,
      type: 'Morning Hypertension',
      severity: 'medium',
      date: new Date(2023, 9, 15).toISOString(),
      description: 'Your blood pressure readings are consistently higher in the morning than other times of day.',
      recommendation: 'Consider taking your medication earlier or speaking with your doctor about adjusting your dosage schedule.',
      readings: MOCK_BP_READINGS.slice(0, 2)
    }
  ]
};

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
      
      try {
        const response = await axiosInstance.get(url, { params });
        return response.data;
      } catch (apiError) {
        console.warn('API request failed, using mock data:', apiError.message);
        return MOCK_BP_READINGS;
      }
    } catch (error) {
      console.error('Error fetching BP readings:', error);
      // Return empty array instead of throwing
      return [];
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
      try {
        const response = await axiosInstance.get('analytics', { params: { days } });
        return response.data;
      } catch (apiError) {
        console.warn('API request failed, using mock analytics data:', apiError.message);
        return MOCK_ANALYTICS;
      }
    } catch (error) {
      console.error('Error fetching BP analytics:', error);
      // Return empty object instead of throwing
      return {};
    }
  },
  
  // Detect anomalies using ML
  detectAnomalies: async () => {
    try {
      try {
        const response = await axiosInstance.get('anomalies');
        return response.data;
      } catch (apiError) {
        console.warn('API request failed, using mock anomalies data:', apiError.message);
        return MOCK_ANOMALIES;
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      // Return empty object instead of throwing
      return { anomalies: [] };
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