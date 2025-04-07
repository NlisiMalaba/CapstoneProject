import React, { useState, useRef } from 'react';
import { toast } from 'react-toastify';
import bpService from '../../services/bpService';

const FileUploadForm = ({ onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [uploadType, setUploadType] = useState('csv'); // 'csv' or 'image'
  const fileInputRef = useRef(null);

  const handleUploadTypeChange = (type) => {
    setUploadType(type);
    // Reset file input when changing type
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    const file = fileInputRef.current.files[0];
    
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }
    
    // Validate file type
    if (uploadType === 'csv' && !file.name.toLowerCase().endsWith('.csv')) {
      toast.error('Please select a CSV file');
      return;
    }
    
    if (uploadType === 'image') {
      const validImageTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
      if (!validImageTypes.includes(file.type)) {
        toast.error('Please select a valid image file (JPG, PNG, BMP, TIFF)');
        return;
      }
    }
    
    try {
      setLoading(true);
      
      let response;
      
      if (uploadType === 'csv') {
        response = await bpService.uploadCSV(file);
        toast.success(`CSV processed successfully. Added ${response.readings_added} readings.`);
      } else {
        response = await bpService.uploadImage(file);
        toast.success(`Image processed successfully. Added ${response.readings_added} readings.`);
      }
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (error) {
      console.error(`Error uploading ${uploadType}:`, error);
      toast.error(error.response?.data?.message || `Failed to upload ${uploadType}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Upload Blood Pressure Data</h2>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-500"
            aria-label="Close"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      
      <div className="flex mb-4 border-b">
        <button
          type="button"
          className={`py-2 px-4 mr-2 ${uploadType === 'csv' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
          onClick={() => handleUploadTypeChange('csv')}
        >
          CSV Upload
        </button>
        <button
          type="button"
          className={`py-2 px-4 ${uploadType === 'image' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
          onClick={() => handleUploadTypeChange('image')}
        >
          Image OCR
        </button>
      </div>
      
      <form onSubmit={handleFileUpload}>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {uploadType === 'csv' ? 'Select CSV File' : 'Select Image with BP Readings'}
          </label>
          
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                >
                  <span>Upload a file</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    ref={fileInputRef}
                    accept={uploadType === 'csv' ? '.csv' : 'image/*'}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">
                {uploadType === 'csv' ? 'CSV file with BP readings' : 'JPG, PNG, BMP, TIFF up to 10MB'}
              </p>
            </div>
          </div>
          
          <div className="mt-6 flex justify-end space-x-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="py-2 px-4 rounded font-medium bg-gray-200 hover:bg-gray-300 text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={loading}
              className={`py-2 px-4 rounded font-medium ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
            >
              {loading ? 'Processing...' : `Upload ${uploadType.toUpperCase()}`}
            </button>
          </div>
          
          {uploadType === 'csv' && (
            <div className="mt-4 text-sm text-gray-600">
              <p className="font-medium mb-1">CSV Format Requirements:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Column headers: systolic, diastolic, pulse, date, time, notes</li>
                <li>Systolic and diastolic are required for each row</li>
                <li>Date format should be YYYY-MM-DD</li>
                <li>Time is optional</li>
              </ul>
            </div>
          )}
          
          {uploadType === 'image' && (
            <div className="mt-4 text-sm text-gray-600">
              <p className="font-medium mb-1">Image Upload Requirements:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Image must contain visible BP readings (e.g., from a BP monitor display)</li>
                <li>Make sure the reading is clearly visible and the image is well-lit</li>
                <li>Standard format: 120/80 (Systolic/Diastolic)</li>
              </ul>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default FileUploadForm; 