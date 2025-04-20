import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import predictionService from '../services/predictionService';
import profileService from '../services/profileService';

// Risk level colors for the UI
const riskLevelColors = {
  'Low': 'green',
  'Moderate': 'yellow',
  'High': 'orange',
  'Very High': 'red'
};

const Prediction = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    current_smoker: false,
    cigs_per_day: 0,
    bp_meds: false,
    diabetes: false,
    total_chol: '',
    sys_bp: '',
    dia_bp: '',
    heart_rate: '',
    glucose: '',
    diet_description: '',
    medical_history: '',
    physical_activity_level: '',
    kidney_disease: false,
    heart_disease: false,
    family_history_htn: false,
    alcohol_consumption: '',
    salt_intake: '',
    stress_level: '',
    sleep_hours: ''
  });
  
  // Profile data that will automatically be used
  const [profileData, setProfileData] = useState(null);
  const [profileComplete, setProfileComplete] = useState(true);
  const [missingFields, setMissingFields] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [error, setError] = useState(null);
  const [showProfileAlert, setShowProfileAlert] = useState(false);

  // Load profile and patient data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch user profile
        const profile = await profileService.getProfile();
        setProfileData(profile);
        
        // Check if profile has required fields
        if (!profile || 
            !profile.age || 
            !profile.gender || 
            (!profile.bmi && (!profile.height || !profile.weight))) {
          setProfileComplete(false);
          
          // Determine which fields are missing
          const missing = [];
          if (!profile || !profile.age) missing.push('age');
          if (!profile || !profile.gender) missing.push('gender');
          if (!profile || (!profile.bmi && (!profile.height || !profile.weight))) {
            missing.push('height and weight');
          }
          setMissingFields(missing);
          setShowProfileAlert(true);
        }
        
        // Fetch existing patient data if available
        const patientData = await predictionService.getPatientData();
        if (patientData) {
          // Only update fields that exist in our formData
          const updatedFormData = { ...formData };
          Object.keys(formData).forEach(key => {
            if (patientData[key] !== undefined && patientData[key] !== null) {
              updatedFormData[key] = patientData[key];
            }
          });
          setFormData(updatedFormData);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load your data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if profile is complete
    if (!profileComplete) {
      setShowProfileAlert(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    setSubmitting(true);
    setError(null);
    setPredictionResult(null);

    try {
      // Save patient data
      await predictionService.savePatientData(formData);
      
      // Get prediction
      const result = await predictionService.getPrediction();
      setPredictionResult(result);
      
      // Scroll to the results
      setTimeout(() => {
        const resultElement = document.getElementById('prediction-result');
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: 'smooth' });
        }
      }, 500);
      
    } catch (err) {
      console.error('Prediction error:', err);
      
      // Handle missing profile data error
      if (err.response && err.response.data && err.response.data.missing_fields) {
        setProfileComplete(false);
        setMissingFields(err.response.data.missing_fields);
        setShowProfileAlert(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        setError(err.response?.data?.error || err.message || 'Failed to get prediction');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };
  
  const navigateToProfile = () => {
    navigate('/profile');
  };

  // Display loading spinner while data is being fetched
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your data...</p>
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
        className="max-w-4xl mx-auto"
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
          <h1 className="text-2xl font-bold text-gray-900">Hypertension Risk Prediction</h1>
        </div>

        {showProfileAlert && !profileComplete && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-yellow-100 border border-yellow-400 rounded-md"
          >
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Profile information required</h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    To get an accurate prediction, please complete your profile with the following information:
                    {missingFields.map((field, index) => (
                      <span key={field}>
                        {index > 0 && index < missingFields.length - 1 ? ', ' : index > 0 ? ' and ' : ' '}
                        <strong>{field}</strong>
                      </span>
                    ))}
                  </p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={navigateToProfile}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                  >
                    Complete your profile
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">Your Health Information</h2>
            <p className="mt-2 text-gray-600">
              Fill out the form below to get an assessment of your hypertension risk.
              {profileData && (
                <span className="block mt-1 text-sm font-medium">
                  We'll automatically use your profile data: Age ({profileData.age}), 
                  Gender ({profileData.gender}){profileData.bmi ? `, BMI (${profileData.bmi})` : ''}
                </span>
              )}
            </p>
          </div>

          {error && (
            <div className="p-4 mx-6 my-4 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Blood Pressure Section */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Blood Pressure</h3>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="sys_bp" className="block text-sm font-medium text-gray-700">
                      Systolic Blood Pressure (mmHg)
                    </label>
                    <input
                      type="number"
                      id="sys_bp"
                      name="sys_bp"
                      value={formData.sys_bp}
                      onChange={handleInputChange}
                      placeholder="e.g., 120"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="dia_bp" className="block text-sm font-medium text-gray-700">
                      Diastolic Blood Pressure (mmHg)
                    </label>
                    <input
                      type="number"
                      id="dia_bp"
                      name="dia_bp"
                      value={formData.dia_bp}
                      onChange={handleInputChange}
                      placeholder="e.g., 80"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              </div>

              {/* Health Metrics Section */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Health Metrics</h3>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="total_chol" className="block text-sm font-medium text-gray-700">
                      Total Cholesterol (mg/dL)
                    </label>
                    <input
                      type="number"
                      id="total_chol"
                      name="total_chol"
                      value={formData.total_chol}
                      onChange={handleInputChange}
                      placeholder="e.g., 200"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="heart_rate" className="block text-sm font-medium text-gray-700">
                      Heart Rate (bpm)
                    </label>
                    <input
                      type="number"
                      id="heart_rate"
                      name="heart_rate"
                      value={formData.heart_rate}
                      onChange={handleInputChange}
                      placeholder="e.g., 72"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="glucose" className="block text-sm font-medium text-gray-700">
                      Blood Glucose (mg/dL)
                    </label>
                    <input
                      type="number"
                      id="glucose"
                      name="glucose"
                      value={formData.glucose}
                      onChange={handleInputChange}
                      placeholder="e.g., 100"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="sleep_hours" className="block text-sm font-medium text-gray-700">
                      Average Sleep Hours
                    </label>
                    <input
                      type="number"
                      id="sleep_hours"
                      name="sleep_hours"
                      value={formData.sleep_hours}
                      onChange={handleInputChange}
                      step="0.5"
                      placeholder="e.g., 7.5"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              </div>

              {/* Medical Conditions Section */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Medical Conditions</h3>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="current_smoker"
                      name="current_smoker"
                      checked={formData.current_smoker}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="current_smoker" className="ml-2 block text-sm text-gray-700">
                      Current Smoker
                    </label>
                  </div>

                  {formData.current_smoker && (
                    <div>
                      <label htmlFor="cigs_per_day" className="block text-sm font-medium text-gray-700">
                        Cigarettes Per Day
                      </label>
                      <input
                        type="number"
                        id="cigs_per_day"
                        name="cigs_per_day"
                        value={formData.cigs_per_day}
                        onChange={handleInputChange}
                        placeholder="e.g., 10"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                    </div>
                  )}

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="bp_meds"
                      name="bp_meds"
                      checked={formData.bp_meds}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="bp_meds" className="ml-2 block text-sm text-gray-700">
                      Taking Blood Pressure Medication
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="diabetes"
                      name="diabetes"
                      checked={formData.diabetes}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="diabetes" className="ml-2 block text-sm text-gray-700">
                      Diabetes
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="kidney_disease"
                      name="kidney_disease"
                      checked={formData.kidney_disease}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="kidney_disease" className="ml-2 block text-sm text-gray-700">
                      Kidney Disease
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="heart_disease"
                      name="heart_disease"
                      checked={formData.heart_disease}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="heart_disease" className="ml-2 block text-sm text-gray-700">
                      Heart Disease
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="family_history_htn"
                      name="family_history_htn"
                      checked={formData.family_history_htn}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="family_history_htn" className="ml-2 block text-sm text-gray-700">
                      Family History of Hypertension
                    </label>
                  </div>
                </div>
              </div>

              {/* Lifestyle Section */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Lifestyle Factors</h3>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="physical_activity_level" className="block text-sm font-medium text-gray-700">
                      Physical Activity Level
                    </label>
                    <select
                      id="physical_activity_level"
                      name="physical_activity_level"
                      value={formData.physical_activity_level}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value="">Select one</option>
                      <option value="Low">Low (Rarely exercise)</option>
                      <option value="Moderate">Moderate (1-3 days/week)</option>
                      <option value="High">High (4+ days/week)</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="alcohol_consumption" className="block text-sm font-medium text-gray-700">
                      Alcohol Consumption
                    </label>
                    <select
                      id="alcohol_consumption"
                      name="alcohol_consumption"
                      value={formData.alcohol_consumption}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value="">Select one</option>
                      <option value="None">None</option>
                      <option value="Light">Light (1-2 drinks/week)</option>
                      <option value="Moderate">Moderate (3-7 drinks/week)</option>
                      <option value="Heavy">Heavy (8+ drinks/week)</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="salt_intake" className="block text-sm font-medium text-gray-700">
                      Salt Intake
                    </label>
                    <select
                      id="salt_intake"
                      name="salt_intake"
                      value={formData.salt_intake}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value="">Select one</option>
                      <option value="Low">Low (Rarely add salt)</option>
                      <option value="Moderate">Moderate (Occasionally add salt)</option>
                      <option value="High">High (Frequently add salt)</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="stress_level" className="block text-sm font-medium text-gray-700">
                      Stress Level
                    </label>
                    <select
                      id="stress_level"
                      name="stress_level"
                      value={formData.stress_level}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value="">Select one</option>
                      <option value="Low">Low (Rarely feel stressed)</option>
                      <option value="Moderate">Moderate (Occasionally stressed)</option>
                      <option value="High">High (Frequently stressed)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Additional Information Section */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Additional Information</h3>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-1 gap-4">
                  <div>
                    <label htmlFor="medical_history" className="block text-sm font-medium text-gray-700">
                      Medical History
                    </label>
                    <textarea
                      id="medical_history"
                      name="medical_history"
                      value={formData.medical_history}
                      onChange={handleInputChange}
                      rows="3"
                      placeholder="Describe any other relevant medical conditions or history..."
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    ></textarea>
                  </div>

                  <div>
                    <label htmlFor="diet_description" className="block text-sm font-medium text-gray-700">
                      Diet Description
                    </label>
                    <textarea
                      id="diet_description"
                      name="diet_description"
                      value={formData.diet_description}
                      onChange={handleInputChange}
                      rows="3"
                      placeholder="Describe your typical diet..."
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className={`px-6 py-3 rounded-md text-white text-lg font-medium ${
                  submitting ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors`}
              >
                {submitting ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⟳</span>
                    Calculating...
                  </>
                ) : (
                  'Calculate Hypertension Risk'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Prediction Results */}
        {predictionResult && (
          <motion.div
            id="prediction-result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white shadow rounded-lg overflow-hidden mb-6"
          >
            <div className="p-6 border-b border-gray-200 bg-indigo-50">
              <h2 className="text-xl font-semibold text-gray-800">Your Hypertension Risk Assessment</h2>
              <p className="mt-1 text-gray-600">
                Based on the information provided and your profile data
              </p>
            </div>

            <div className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:space-x-8 mb-6">
                <div className="mb-4 md:mb-0">
                  <div className="text-gray-700 mb-1">Risk Score</div>
                  <div className="text-4xl font-bold text-indigo-700">
                    {predictionResult.prediction_score}
                    <span className="text-xl text-gray-500 ml-1">/ 100</span>
                  </div>
                </div>

                <div className="flex-1 mb-4 md:mb-0">
                  <div className="text-gray-700 mb-1">Risk Level</div>
                  <div className="inline-block px-4 py-2 rounded-full text-lg font-semibold" 
                       style={{ 
                         backgroundColor: `${riskLevelColors[predictionResult.risk_level]}25`, 
                         color: riskLevelColors[predictionResult.risk_level]
                       }}>
                    {predictionResult.risk_level}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="text-gray-700 mb-1">Prediction Date</div>
                  <div className="text-lg">
                    {new Date(predictionResult.prediction_date).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Key Risk Factors</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {predictionResult.key_factors.map((factor, index) => (
                      <li key={index} className="text-gray-700">{factor}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Recommendations</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {predictionResult.recommendations.map((recommendation, index) => (
                      <li key={index} className="text-gray-700">{recommendation}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <p className="text-sm text-gray-500">
                  This prediction is based on the information you provided and statistical models.
                  It is intended for informational purposes only and should not replace professional medical advice.
                  Always consult with a healthcare provider for diagnosis and treatment.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default Prediction; 