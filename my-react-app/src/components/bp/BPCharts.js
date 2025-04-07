import React, { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { format, subDays } from 'date-fns';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const BPCharts = ({ readings = [], analytics = null }) => {
  const [timeRange, setTimeRange] = useState('month'); // week, month, year, all
  
  // Ensure readings is always an array
  const safeReadings = Array.isArray(readings) ? readings : [];
  
  if (safeReadings.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Blood Pressure Analytics</h2>
        <div className="text-center py-4 text-gray-500">
          No data available for analysis. Add readings to see charts.
        </div>
      </div>
    );
  }
  
  // Filter readings based on time range
  const getFilteredReadings = () => {
    const now = new Date();
    let since;
    
    switch (timeRange) {
      case 'week':
        since = subDays(now, 7);
        break;
      case 'month':
        since = subDays(now, 30);
        break;
      case 'year':
        since = subDays(now, 365);
        break;
      default: // 'all'
        return safeReadings;
    }
    
    return safeReadings.filter(reading => 
      reading && reading.measurement_date && new Date(reading.measurement_date) >= since
    );
  };
  
  const filteredReadings = getFilteredReadings();
  
  // Sort readings by date
  const sortedReadings = [...filteredReadings].sort(
    (a, b) => new Date(a.measurement_date) - new Date(b.measurement_date)
  );
  
  // Prepare data for line chart
  const prepareLineChartData = () => {
    const labels = sortedReadings.map(reading => 
      format(new Date(reading.measurement_date), 'MMM dd')
    );
    
    return {
      labels,
      datasets: [
        {
          label: 'Systolic',
          data: sortedReadings.map(reading => reading.systolic),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.1,
          fill: false
        },
        {
          label: 'Diastolic',
          data: sortedReadings.map(reading => reading.diastolic),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.1,
          fill: false
        }
      ]
    };
  };
  
  // Prepare data for category distribution chart
  const prepareCategoryData = () => {
    const categories = {};
    
    filteredReadings.forEach(reading => {
      const category = reading.category || 'Unknown';
      categories[category] = (categories[category] || 0) + 1;
    });
    
    const categoryColors = {
      'Normal': 'rgba(75, 192, 92, 0.7)',
      'Elevated': 'rgba(255, 206, 86, 0.7)',
      'Hypertension Stage 1': 'rgba(255, 159, 64, 0.7)',
      'Hypertension Stage 2': 'rgba(255, 99, 132, 0.7)',
      'Hypertensive Crisis': 'rgba(220, 53, 69, 0.7)',
      'Unknown': 'rgba(201, 203, 207, 0.7)'
    };
    
    return {
      labels: Object.keys(categories),
      datasets: [
        {
          label: 'Reading Count',
          data: Object.values(categories),
          backgroundColor: Object.keys(categories).map(cat => categoryColors[cat] || 'rgba(201, 203, 207, 0.7)')
        }
      ]
    };
  };
  
  // Options for charts
  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: false,
        min: Math.max(0, Math.min(...sortedReadings.map(r => r.diastolic)) - 10),
        title: {
          display: true,
          text: 'Blood Pressure (mmHg)'
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context) {
            const index = context.dataIndex;
            const reading = sortedReadings[index];
            return `${context.dataset.label}: ${context.parsed.y} mmHg (${reading.category})`;
          }
        }
      },
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Blood Pressure Trends'
      }
    }
  };
  
  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Blood Pressure Categories'
      }
    }
  };
  
  // Calculate averages and stats
  const calculateStats = () => {
    const systolicValues = filteredReadings.map(r => r.systolic);
    const diastolicValues = filteredReadings.map(r => r.diastolic);
    const pulseValues = filteredReadings.filter(r => r.pulse).map(r => r.pulse);
    
    return {
      avgSystolic: systolicValues.length > 0 ? 
        (systolicValues.reduce((a, b) => a + b, 0) / systolicValues.length).toFixed(1) : 'N/A',
      avgDiastolic: diastolicValues.length > 0 ? 
        (diastolicValues.reduce((a, b) => a + b, 0) / diastolicValues.length).toFixed(1) : 'N/A',
      avgPulse: pulseValues.length > 0 ? 
        (pulseValues.reduce((a, b) => a + b, 0) / pulseValues.length).toFixed(1) : 'N/A',
      maxSystolic: systolicValues.length > 0 ? Math.max(...systolicValues) : 'N/A',
      minSystolic: systolicValues.length > 0 ? Math.min(...systolicValues) : 'N/A',
      maxDiastolic: diastolicValues.length > 0 ? Math.max(...diastolicValues) : 'N/A',
      minDiastolic: diastolicValues.length > 0 ? Math.min(...diastolicValues) : 'N/A',
      abnormalCount: filteredReadings.filter(r => r.is_abnormal).length,
      readingCount: filteredReadings.length,
      pulseValues
    };
  };
  
  const stats = calculateStats();
  const pulseValues = filteredReadings.filter(r => r.pulse).map(r => r.pulse);
  
  // Find trend info from analytics (if available)
  const trendInfo = analytics?.trend_direction 
    ? {
        direction: analytics.trend_direction,
        details: analytics.trend_details
      }
    : null;
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Blood Pressure Analytics</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeRange('week')}
            className={`px-3 py-1 rounded-md text-sm ${
              timeRange === 'week' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setTimeRange('month')}
            className={`px-3 py-1 rounded-md text-sm ${
              timeRange === 'month' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Month
          </button>
          <button
            onClick={() => setTimeRange('year')}
            className={`px-3 py-1 rounded-md text-sm ${
              timeRange === 'year' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Year
          </button>
          <button
            onClick={() => setTimeRange('all')}
            className={`px-3 py-1 rounded-md text-sm ${
              timeRange === 'all' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Time
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg shadow-sm">
            <div className="text-blue-500 text-sm font-medium">Avg. Systolic</div>
            <div className="mt-1 text-2xl font-semibold">{stats.avgSystolic}</div>
            <div className="text-xs text-gray-500">mmHg</div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg shadow-sm">
            <div className="text-blue-500 text-sm font-medium">Avg. Diastolic</div>
            <div className="mt-1 text-2xl font-semibold">{stats.avgDiastolic}</div>
            <div className="text-xs text-gray-500">mmHg</div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg shadow-sm">
            <div className="text-blue-500 text-sm font-medium">Readings</div>
            <div className="mt-1 text-2xl font-semibold">{stats.readingCount}</div>
            <div className="text-xs text-gray-500">total</div>
          </div>
          
          <div className={`p-4 rounded-lg shadow-sm ${stats.abnormalCount > 0 ? 'bg-red-50' : 'bg-green-50'}`}>
            <div className={`text-sm font-medium ${stats.abnormalCount > 0 ? 'text-red-500' : 'text-green-500'}`}>
              Abnormal
            </div>
            <div className="mt-1 text-2xl font-semibold">{stats.abnormalCount}</div>
            <div className="text-xs text-gray-500">readings</div>
          </div>
        </div>
        
        {/* Trend Information */}
        {trendInfo && (
          <div className={`p-4 rounded-lg shadow-sm border ${
            trendInfo.direction === 'improving' ? 'border-green-200 bg-green-50' : 
            trendInfo.direction === 'worsening' ? 'border-red-200 bg-red-50' :
            trendInfo.direction === 'stable' ? 'border-blue-200 bg-blue-50' :
            'border-gray-200 bg-gray-50'
          }`}>
            <div className="flex items-center">
              <div className="mr-2">
                {trendInfo.direction === 'improving' ? '↓' : 
                 trendInfo.direction === 'worsening' ? '↑' : 
                 trendInfo.direction === 'stable' ? '→' : 'ℹ️'}
              </div>
              <div className="text-sm font-medium">
                {trendInfo.direction === 'improving' ? 'Improving Trend' : 
                 trendInfo.direction === 'worsening' ? 'Worsening Trend' : 
                 trendInfo.direction === 'stable' ? 'Stable Trend' : 
                 'Trend Analysis'}
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-600">{trendInfo.details}</div>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Line Chart */}
        <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
          <div className="h-64">
            <Line data={prepareLineChartData()} options={lineOptions} />
          </div>
        </div>
        
        {/* Bar Chart */}
        <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
          <div className="h-64">
            <Bar data={prepareCategoryData()} options={barOptions} />
          </div>
        </div>
      </div>
      
      {/* Min/Max Table */}
      <div className="mt-6">
        <h3 className="font-medium text-gray-700 mb-2">Blood Pressure Ranges</h3>
        <div className="bg-gray-50 overflow-hidden rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-100">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Measurement
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lowest
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Average
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Highest
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Systolic</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.minSystolic} mmHg</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.avgSystolic} mmHg</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.maxSystolic} mmHg</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Diastolic</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.minDiastolic} mmHg</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.avgDiastolic} mmHg</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.maxDiastolic} mmHg</td>
              </tr>
              {pulseValues.length > 0 && (
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Pulse</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.min(...pulseValues)} bpm
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats.avgPulse} bpm</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.max(...pulseValues)} bpm
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default BPCharts; 