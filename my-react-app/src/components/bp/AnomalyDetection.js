import * as React from 'react';
import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { toast } from 'react-toastify';
import bpService from '../../services/bpService';

const AnomalyDetection = ({ readings }) => {
  const [loading, setLoading] = useState(false);
  const [anomalies, setAnomalies] = useState([]);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    if (readings && readings.length > 0) {
      detectAnomalies();
    }
  }, [readings]);

  const detectAnomalies = async () => {
    if (!readings || readings.length < 5) {
      setAnomalies([]);
      return;
    }

    setLoading(true);
    try {
      const result = await bpService.detectAnomalies();
      setAnomalies(result.anomalies || []);
    } catch (error) {
      console.error("Error detecting anomalies:", error);
      toast.error("Failed to detect anomalies. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id) => {
    setExpanded(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Anomaly Detection</h2>
        <div className="flex justify-center items-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Analyzing your blood pressure data...</span>
        </div>
      </div>
    );
  }

  if (!readings || readings.length < 5) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Anomaly Detection</h2>
        <div className="text-center py-4 text-gray-500">
          Not enough data for anomaly detection. Please add at least 5 readings.
        </div>
      </div>
    );
  }

  if (anomalies.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Anomaly Detection</h2>
        <div className="bg-green-50 rounded-lg p-4 flex items-start">
          <div className="text-green-500 mr-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <div>
            <p className="font-medium text-green-800">No anomalies detected</p>
            <p className="text-sm text-green-700 mt-1">
              Our system has analyzed your blood pressure readings and hasn't found any unusual patterns. Keep up the good work!
            </p>
          </div>
        </div>
        <div className="mt-4 text-right">
          <button 
            onClick={detectAnomalies}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Run analysis again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Anomaly Detection</h2>
        <button 
          onClick={detectAnomalies}
          className="text-sm px-3 py-1 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100"
        >
          Refresh
        </button>
      </div>
      
      <div className="space-y-4">
        {anomalies.map((anomaly, index) => (
          <div key={index} className="border rounded-lg overflow-hidden">
            <div 
              className={`flex justify-between items-center p-4 cursor-pointer ${
                anomaly.severity === 'high' ? 'bg-red-50' : 
                anomaly.severity === 'medium' ? 'bg-orange-50' : 'bg-yellow-50'
              }`}
              onClick={() => toggleExpand(anomaly.id)}
            >
              <div className="flex items-center">
                <div className={`rounded-full p-2 mr-3 ${
                  anomaly.severity === 'high' ? 'bg-red-100 text-red-500' : 
                  anomaly.severity === 'medium' ? 'bg-orange-100 text-orange-500' : 'bg-yellow-100 text-yellow-500'
                }`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium">{anomaly.type}</h3>
                  <p className="text-sm text-gray-600">
                    {format(new Date(anomaly.date), 'MMM dd, yyyy')}
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                <span className={`text-sm font-medium ${
                  anomaly.severity === 'high' ? 'text-red-700' : 
                  anomaly.severity === 'medium' ? 'text-orange-700' : 'text-yellow-700'
                }`}>
                  {anomaly.severity.charAt(0).toUpperCase() + anomaly.severity.slice(1)} Severity
                </span>
                <svg 
                  className={`w-5 h-5 ml-2 transform transition-transform ${expanded[anomaly.id] ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24" 
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            
            {expanded[anomaly.id] && (
              <div className="p-4 bg-white">
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Description</h4>
                  <p className="text-gray-600">{anomaly.description}</p>
                </div>
                
                {anomaly.readings && anomaly.readings.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Related Readings</h4>
                    <div className="bg-gray-50 rounded-lg overflow-hidden">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-100">
                          <tr>
                            <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Systolic</th>
                            <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Diastolic</th>
                            {anomaly.readings.some(r => r.pulse) && (
                              <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Pulse</th>
                            )}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {anomaly.readings.map((reading, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                {format(new Date(reading.measurement_date), 'MMM dd, HH:mm')}
                              </td>
                              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                {reading.systolic} mmHg
                              </td>
                              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                {reading.diastolic} mmHg
                              </td>
                              {anomaly.readings.some(r => r.pulse) && (
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                  {reading.pulse ? `${reading.pulse} bpm` : '-'}
                                </td>
                              )}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {anomaly.recommendation && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-700 mb-2">Recommendation</h4>
                    <div className="bg-blue-50 rounded-lg p-3 text-blue-800 text-sm">
                      {anomaly.recommendation}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnomalyDetection; 