import * as React from 'react';
import { useState } from 'react';
import { toast } from 'react-toastify';
import bpService from '../../services/bpService';

const AddBPReadingForm = ({ onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    systolic: '',
    diastolic: '',
    pulse: '',
    measurement_date: new Date().toISOString().slice(0, 16),
    measurement_time: 'Morning',
    notes: '',
    source: 'manual'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const validateForm = () => {
    if (!formData.systolic || !formData.diastolic) {
      toast.error('Systolic and diastolic values are required');
      return false;
    }

    const systolic = parseInt(formData.systolic);
    const diastolic = parseInt(formData.diastolic);

    if (isNaN(systolic) || isNaN(diastolic)) {
      toast.error('Blood pressure values must be numbers');
      return false;
    }

    if (systolic < 70 || systolic > 250) {
      toast.error('Systolic value must be between 70 and 250');
      return false;
    }

    if (diastolic < 40 || diastolic > 150) {
      toast.error('Diastolic value must be between 40 and 150');
      return false;
    }

    if (diastolic > systolic) {
      toast.error('Diastolic value cannot be higher than systolic');
      return false;
    }

    if (formData.pulse && (isNaN(parseInt(formData.pulse)) || parseInt(formData.pulse) < 30 || parseInt(formData.pulse) > 220)) {
      toast.error('Pulse must be a number between 30 and 220');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      setLoading(true);
      
      // Convert date and time to ISO format
      const bpData = {
        ...formData,
        systolic: parseInt(formData.systolic),
        diastolic: parseInt(formData.diastolic),
        pulse: formData.pulse ? parseInt(formData.pulse) : null
      };
      
      const response = await bpService.addReading(bpData);
      
      toast.success('Blood pressure reading added successfully');
      setFormData({
        systolic: '',
        diastolic: '',
        pulse: '',
        measurement_date: new Date().toISOString().slice(0, 16),
        measurement_time: 'Morning',
        notes: '',
        source: 'manual'
      });
      
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (error) {
      console.error('Error adding BP reading:', error);
      toast.error(error.response?.data?.message || 'Failed to add reading');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Add Blood Pressure Reading</h2>
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
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Systolic (mmHg) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="systolic"
              value={formData.systolic}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 120"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Diastolic (mmHg) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="diastolic"
              value={formData.diastolic}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 80"
              required
            />
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Pulse (bpm)
          </label>
          <input
            type="number"
            name="pulse"
            value={formData.pulse}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 75"
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date & Time <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              name="measurement_date"
              value={formData.measurement_date}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time of Day
            </label>
            <select
              name="measurement_time"
              value={formData.measurement_time}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Morning">Morning</option>
              <option value="Afternoon">Afternoon</option>
              <option value="Evening">Evening</option>
              <option value="Night">Night</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Additional information about this reading..."
            rows="3"
          />
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
            {loading ? 'Saving...' : 'Add Reading'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddBPReadingForm; 