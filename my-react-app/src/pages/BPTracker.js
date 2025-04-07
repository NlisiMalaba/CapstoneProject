import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Import our components
import AddBPReadingForm from '../components/bp/AddBPReadingForm';
import FileUploadForm from '../components/bp/FileUploadForm';
import BPReadingsTable from '../components/bp/BPReadingsTable';
import BPCharts from '../components/bp/BPCharts';
import AnomalyDetection from '../components/bp/AnomalyDetection';
import ReportGenerator from '../components/bp/ReportGenerator';

// Import our BP service
import bpService from '../services/bpService';

const BPTracker = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [readings, setReadings] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showReportGenerator, setShowReportGenerator] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState('readings'); // readings, charts, anomalies

  // Fetch BP readings and analytics when component mounts
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch readings (default: last 30 days, limit 100)
      const readingsData = await bpService.getReadings(null, null, 100);
      setReadings(readingsData);

      // Fetch analytics for the last 30 days
      const analyticsData = await bpService.getAnalytics(30);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch your blood pressure data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReading = async (readingId) => {
    if (window.confirm('Are you sure you want to delete this reading?')) {
      try {
        // BP service would need a deleteReading method
        await bpService.deleteReading(readingId);
        toast.success('Reading deleted successfully');
        
        // Update local state to remove the deleted reading
        setReadings(readings.filter(reading => reading.id !== readingId));
      } catch (error) {
        console.error('Error deleting reading:', error);
        toast.error('Failed to delete reading');
      }
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <ToastContainer position="top-right" autoClose={5000} />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6">
          <div className="flex items-center mb-4 sm:mb-0">
            <button
              onClick={handleBack}
              className="mr-4 p-2 rounded-full hover:bg-gray-200 transition-colors"
              aria-label="Go back"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Blood Pressure Tracker</h1>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => {
                setShowAddForm(true);
                setShowFileUpload(false);
                setShowReportGenerator(false);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
              </svg>
              Add Reading
            </button>
            
            <button
              onClick={() => {
                setShowFileUpload(true);
                setShowAddForm(false);
                setShowReportGenerator(false);
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
              </svg>
              Upload
            </button>
            
            <button
              onClick={() => {
                setShowReportGenerator(true);
                setShowAddForm(false);
                setShowFileUpload(false);
              }}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              Generate Report
            </button>
            
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors flex items-center"
              aria-label="Refresh data"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
          </div>
        </div>

        {/* Forms */}
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <AddBPReadingForm 
              onSuccess={() => {
                setShowAddForm(false);
                fetchData();
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </motion.div>
        )}

        {showFileUpload && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <FileUploadForm 
              onSuccess={() => {
                setShowFileUpload(false);
                fetchData();
              }}
              onCancel={() => setShowFileUpload(false)}
            />
          </motion.div>
        )}

        {showReportGenerator && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <ReportGenerator />
          </motion.div>
        )}

        {/* Tabs Navigation */}
        <div className="bg-white shadow rounded-lg mb-6">
          <nav className="flex border-b">
            <button
              className={`px-6 py-4 text-sm font-medium flex items-center ${
                activeTab === 'readings'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('readings')}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
              Readings
            </button>
            
            <button
              className={`px-6 py-4 text-sm font-medium flex items-center ${
                activeTab === 'charts'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('charts')}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Analytics
            </button>
            
            <button
              className={`px-6 py-4 text-sm font-medium flex items-center ${
                activeTab === 'anomalies'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('anomalies')}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              Anomalies
            </button>
          </nav>
        </div>

        {/* Content based on active tab */}
        {loading ? (
          <div className="bg-white shadow rounded-lg p-8 flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-gray-600">Loading your data...</span>
          </div>
        ) : (
          <>
            {activeTab === 'readings' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <BPReadingsTable 
                  readings={readings} 
                  onDeleteReading={handleDeleteReading} 
                />
              </motion.div>
            )}
            
            {activeTab === 'charts' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <BPCharts 
                  readings={readings} 
                  analytics={analytics} 
                />
              </motion.div>
            )}
            
            {activeTab === 'anomalies' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <AnomalyDetection 
                  readings={readings} 
                />
              </motion.div>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
};

export default BPTracker;
