import * as React from 'react';
import { useState } from 'react';
import { toast } from 'react-toastify';
import { format, subDays, subMonths } from 'date-fns';
import bpService from '../../services/bpService';

const ReportGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [reportType, setReportType] = useState('pdf');
  const [dateRange, setDateRange] = useState('week');
  const [customRange, setCustomRange] = useState({
    startDate: format(subDays(new Date(), 7), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd')
  });

  const handleDateRangeChange = (e) => {
    const value = e.target.value;
    setDateRange(value);
    
    // Set default dates based on selection
    const now = new Date();
    let startDate;
    
    switch (value) {
      case 'week':
        startDate = subDays(now, 7);
        break;
      case 'month':
        startDate = subDays(now, 30);
        break;
      case '3months':
        startDate = subMonths(now, 3);
        break;
      case '6months':
        startDate = subMonths(now, 6);
        break;
      case 'year':
        startDate = subMonths(now, 12);
        break;
      default:
        // Keep current custom range for 'custom'
        return;
    }
    
    setCustomRange({
      startDate: format(startDate, 'yyyy-MM-dd'),
      endDate: format(now, 'yyyy-MM-dd')
    });
  };

  const handleCustomRangeChange = (e) => {
    const { name, value } = e.target;
    setCustomRange(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const startDate = customRange.startDate;
      const endDate = customRange.endDate;
      
      if (new Date(startDate) > new Date(endDate)) {
        toast.error("Start date cannot be after end date");
        setLoading(false);
        return;
      }
      
      const response = await bpService.generateReport(startDate, endDate, reportType);
      
      if (response.reportPath) {
        toast.success(`Report generated successfully!`);
        await bpService.downloadReport(response.reportPath);
      } else {
        toast.error("No data available for the selected date range");
      }
    } catch (error) {
      console.error("Error generating report:", error);
      toast.error("Failed to generate report. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-6">Generate BP Report</h2>
      
      <div className="space-y-6">
        {/* Report Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Report Format
          </label>
          <div className="flex flex-wrap gap-3">
            <label className={`flex items-center p-3 rounded-lg border cursor-pointer ${
              reportType === 'pdf' ? 'bg-blue-50 border-blue-300' : 'bg-white hover:bg-gray-50'
            }`}>
              <input
                type="radio"
                value="pdf"
                checked={reportType === 'pdf'}
                onChange={() => setReportType('pdf')}
                className="hidden"
              />
              <svg className="w-6 h-6 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
              </svg>
              <span>PDF Document</span>
            </label>
            
            <label className={`flex items-center p-3 rounded-lg border cursor-pointer ${
              reportType === 'excel' ? 'bg-blue-50 border-blue-300' : 'bg-white hover:bg-gray-50'
            }`}>
              <input
                type="radio"
                value="excel"
                checked={reportType === 'excel'}
                onChange={() => setReportType('excel')}
                className="hidden"
              />
              <svg className="w-6 h-6 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>Excel Spreadsheet</span>
            </label>
          </div>
        </div>
        
        {/* Date Range Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date Range
          </label>
          <select
            value={dateRange}
            onChange={handleDateRangeChange}
            className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="week">Last 7 days</option>
            <option value="month">Last 30 days</option>
            <option value="3months">Last 3 months</option>
            <option value="6months">Last 6 months</option>
            <option value="year">Last 12 months</option>
            <option value="custom">Custom range</option>
          </select>
        </div>
        
        {/* Custom Date Range Inputs */}
        {dateRange === 'custom' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                name="startDate"
                value={customRange.startDate}
                onChange={handleCustomRangeChange}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                name="endDate"
                value={customRange.endDate}
                onChange={handleCustomRangeChange}
                max={format(new Date(), 'yyyy-MM-dd')}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
        )}
        
        {/* Report Content Preview */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="font-medium text-gray-700 mb-3">Report Will Include:</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              All BP readings within the selected date range
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Statistical analysis (averages, min/max values)
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Trend visualization charts
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              BP category distribution
            </li>
            {reportType === 'pdf' && (
              <li className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Medical-friendly format (shareable with healthcare providers)
              </li>
            )}
          </ul>
        </div>
        
        {/* Generate Button */}
        <div className="flex justify-end">
          <button
            onClick={generateReport}
            disabled={loading}
            className={`px-4 py-2 rounded-md text-white font-medium flex items-center ${
              loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Generate & Download
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator; 