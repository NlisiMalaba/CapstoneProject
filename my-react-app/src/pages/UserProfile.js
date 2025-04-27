import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import profileService from '../services/profileService';
import authService from '../services/authService';

const UserProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [profileExists, setProfileExists] = useState(false);
  
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    contact_email: '',
    emergency_contact: ''
  });
  
  const [bmi, setBmi] = useState(null);
  
  // Load profile data on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const profile = await profileService.getProfile();
        
        if (profile) {
          setProfileExists(true);
          setFormData({
            age: profile.age || '',
            gender: profile.gender || '',
            height: profile.height || '',
            weight: profile.weight || '',
            contact_email: profile.contact_email || '',
            emergency_contact: profile.emergency_contact || ''
          });
          setBmi(profile.bmi || null);
        }
      } catch (err) {
        console.error('Error fetching profile:', err);
        if (err.response && err.response.status === 404) {
          setProfileExists(false);
        } else {
          setError('Failed to load profile. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };
    
    if (authService.isAuthenticated()) {
      fetchProfile();
    } else {
      navigate('/login');
    }
  }, [navigate]);
  
  // Calculate BMI when height or weight changes
  useEffect(() => {
    if (formData.height && formData.weight) {
      const calculatedBmi = profileService.calculateBMI(
        parseFloat(formData.height),
        parseFloat(formData.weight)
      );
      setBmi(calculatedBmi);
    } else {
      setBmi(null);
    }
  }, [formData.height, formData.weight]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      const data = {
        ...formData,
        age: formData.age ? parseInt(formData.age) : null,
        height: formData.height ? parseFloat(formData.height) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null
      };
      
      let response;
      if (profileExists) {
        response = await profileService.updateProfile(data);
        setSuccessMessage('Profile updated successfully!');
      } else {
        response = await profileService.createProfile(data);
        setProfileExists(true);
        setSuccessMessage('Profile created successfully!');
      }
      
      // Update BMI from response if available
      if (response && response.bmi) {
        setBmi(response.bmi);
      }
    } catch (err) {
      console.error('Error saving profile:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to save profile. Please try again.');
      }
    } finally {
      setSaving(false);
      
      // Clear success message after 3 seconds
      if (successMessage) {
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      }
    }
  };
  
  const handleBack = () => {
    navigate('/dashboard');
  };
  
  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-3xl mx-auto"
      >
        <div className="flex items-center mb-6">
          <button
            onClick={handleBack}
            className="mr-4 p-2 rounded-full hover:bg-gray-200 transition-colors"
            aria-label="Go back"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            {profileExists ? 'Edit Your Profile' : 'Create Your Profile'}
          </h1>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="mb-6 p-4 bg-blue-50 rounded-md text-gray-700">
            <h3 className="font-semibold text-blue-800 mb-2">
              {profileExists ? 'Update Your Information' : 'Set Up Your Profile'}
            </h3>
            <p>
              Your profile information is used to automatically populate fields in the hypertension prediction tool.
              Keeping this information up to date ensures more accurate predictions.
            </p>
            {!profileExists && (
              <p className="mt-2 text-sm text-blue-800 font-medium">
                This is your first time here. Please create your profile to continue.
              </p>
            )}
          </div>
          
          {error && (
            <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}
          
          {successMessage && (
            <div className="mb-6 p-4 bg-green-100 text-green-700 rounded-md">
              {successMessage}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="age" className="block text-sm font-medium text-gray-700">
                  Age
                </label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Enter your age"
                  min="0"
                  max="120"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700">
                  Gender
                </label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="height" className="block text-sm font-medium text-gray-700">
                  Height (cm)
                </label>
                <input
                  type="number"
                  id="height"
                  name="height"
                  value={formData.height}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Height in centimeters"
                  min="0"
                  step="0.1"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="weight" className="block text-sm font-medium text-gray-700">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  id="weight"
                  name="weight"
                  value={formData.weight}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Weight in kilograms"
                  min="0"
                  step="0.1"
                  required
                />
              </div>
              
              {bmi !== null && (
                <div className="md:col-span-2">
                  <div className="p-4 bg-blue-50 rounded-md">
                    <p className="font-medium text-blue-900">
                      Calculated BMI: <span className="font-bold">{bmi.toFixed(1)}</span>
                      {' '}
                      <span className="text-sm">
                        ({bmi < 18.5 ? 'Underweight' : 
                          bmi < 25 ? 'Normal' : 
                          bmi < 30 ? 'Overweight' : 'Obese'})
                      </span>
                    </p>
                  </div>
                </div>
              )}
              
              <div className="md:col-span-2">
                <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">
                  Contact Email
                </label>
                <input
                  type="email"
                  id="contact_email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Your contact email"
                  required
                />
              </div>
              
              <div className="md:col-span-2">
                <label htmlFor="emergency_contact" className="block text-sm font-medium text-gray-700">
                  Emergency Contact
                </label>
                <input
                  type="text"
                  id="emergency_contact"
                  name="emergency_contact"
                  value={formData.emergency_contact}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Name and phone number of emergency contact"
                />
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className={`px-6 py-2 rounded-md text-white ${
                  saving ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors`}
              >
                {saving ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⟳</span>
                    Saving...
                  </>
                ) : profileExists ? (
                  'Update Profile'
                ) : (
                  'Create Profile'
                )}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default UserProfile; 