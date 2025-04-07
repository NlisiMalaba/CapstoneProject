import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Prediction = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    age: 0,
    gender: "",
    current_smoker: false,
    cigs_per_day: 0,
    bp_meds: false,
    diabetes: false,
    total_chol: 0,
    sys_bp: 0,
    dia_bp: 0,
    bmi: 0,
    heart_rate: 0,
    glucose: 0,
    diet_description: "",
    medical_history: "",
    physical_activity_level: "",
    kidney_disease: false,
    heart_disease: false,
    family_history_htn: true,
    alcohol_consumption: "",
    salt_intake: "",
    stress_level: "",
    sleep_hours: 0
  });
  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // First save the patient data - remove predictionDate field
      const saveResponse = await fetch('http://localhost:5000/api/prediction/patient-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData) // Send only the form data without additional fields
      });

      if (!saveResponse.ok) {
        const errorData = await saveResponse.json();
        throw new Error(errorData.message || 'Failed to save patient data');
      }

      // Then call the prediction API endpoint
      const response = await fetch('http://localhost:5000/api/prediction/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to get prediction');
      }

      const result = await response.json();
      setPredictionResult(result);

      // The update-prediction endpoint is no longer needed as the backend handles this
      // Remove the third fetch call

    } catch (err) {
      setError(err.message);
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

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
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Hypertension Risk Prediction</h1>
        </div>

        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <p className="text-gray-700 mb-4">
            Fill out the form below to get an assessment of your hypertension risk based on our machine learning model.
            The prediction will provide a risk score from 0-100 and recommendations based on your profile.
          </p>

          {error && (
            <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
              {error}
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
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
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
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

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
                  required
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
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

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
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="glucose" className="block text-sm font-medium text-gray-700">
                  Glucose Level (mg/dL)
                </label>
                <input
                  type="number"
                  id="glucose"
                  name="glucose"
                  value={formData.glucose}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="bmi" className="block text-sm font-medium text-gray-700">
                  BMI
                </label>
                <input
                  type="number"
                  id="bmi"
                  name="bmi"
                  value={formData.bmi}
                  onChange={handleInputChange}
                  required
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
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="sleep_hours" className="block text-sm font-medium text-gray-700">
                  Sleep Hours
                </label>
                <input
                  type="number"
                  id="sleep_hours"
                  name="sleep_hours"
                  value={formData.sleep_hours}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="text-sm font-medium text-gray-700 mb-2">Medical Information</div>

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

            <div>
              <label htmlFor="diet_description" className="block text-sm font-medium text-gray-700">
                Diet Description
              </label>
              <textarea
                id="diet_description"
                name="diet_description"
                rows={2}
                value={formData.diet_description}
                onChange={handleInputChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="medical_history" className="block text-sm font-medium text-gray-700">
                Medical History
              </label>
              <textarea
                id="medical_history"
                name="medical_history"
                rows={2}
                value={formData.medical_history}
                onChange={handleInputChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

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
                <option value="">Select Activity Level</option>
                <option value="sedentary">Sedentary</option>
                <option value="light">Light</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
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
                <option value="">Select Consumption Level</option>
                <option value="none">None</option>
                <option value="light">Light</option>
                <option value="moderate">Moderate</option>
                <option value="heavy">Heavy</option>
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
                <option value="">Select Salt Intake Level</option>
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
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
                <option value="">Select Stress Level</option>
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 flex items-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </>
                ) : 'Get Prediction'}
              </button>
            </div>
          </form>
        </div>

        {predictionResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white shadow rounded-lg p-6"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Prediction Result</h2>

            <div className="mb-6">
              <div className="text-center mb-2">
                <span className="text-4xl font-bold">{predictionResult.prediction.prediction_score}%</span>
                <p className="text-sm text-gray-500">Hypertension Risk</p>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                <div
                  className={`h-4 rounded-full ${predictionResult.prediction.prediction_score < 30 ? 'bg-green-500' :
                      predictionResult.prediction.prediction_score < 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                  style={{ width: `${predictionResult.prediction.prediction_score}%` }}
                ></div>
              </div>

              <div className="text-sm text-gray-700">
                <div className="flex justify-between">
                  <span>Low Risk</span>
                  <span>Moderate Risk</span>
                  <span>High Risk</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Risk Level: {predictionResult.prediction.risk_level}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Prediction Date: {new Date(predictionResult.prediction.prediction_date).toLocaleDateString('en-GB', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                  , {new Date(predictionResult.prediction.prediction_date).toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true,
                  })}
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">Key Risk Factors</h3>
                <ul className="mt-2 list-disc list-inside text-gray-700">
                  {predictionResult.prediction.key_factors?.map((factor, index) => (
                    <li key={index}>{factor}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
                <ul className="mt-2 list-disc list-inside text-gray-700">
                  {predictionResult.prediction.recommendations?.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>

              {predictionResult.prediction.prediction_score > 50 && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Important Notice</h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p>
                          Your risk score is above 50%. It is recommended that you consult with a healthcare professional as soon as possible.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setPredictionResult(null)}
                  className="px-4 py-2 text-sm font-medium text-indigo-700 bg-indigo-100 border border-transparent rounded-md hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Make Another Prediction
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default Prediction; 