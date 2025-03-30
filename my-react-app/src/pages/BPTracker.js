// import React, { useState, useEffect, useRef } from 'react';
// import { motion } from 'framer-motion';
// import { useNavigate } from 'react-router-dom';
// import { Line } from 'react-chartjs-2';
// import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
// import { jsPDF } from 'jspdf';
// import * as XLSX from 'xlsx';
// import moment from 'moment';

// // Register Chart.js components
// ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// const BPTracker = () => {
//   const navigate = useNavigate();
//   const [loading, setLoading] = useState(true);
//   const [bpData, setBpData] = useState([]);
//   const [newReading, setNewReading] = useState({
//     systolic: '',
//     diastolic: '',
//     pulse: '',
//     notes: '',
//     timestamp: new Date().toISOString(),
//   });
//   const [showForm, setShowForm] = useState(false);
//   const [uploadImage, setUploadImage] = useState(null);
//   const [recordingVoice, setRecordingVoice] = useState(false);
//   const [anomalyDetected, setAnomalyDetected] = useState(null);
//   const [timeRange, setTimeRange] = useState('week'); // week, month, year
//   const [exportLoading, setExportLoading] = useState(false);
//   const fileInputRef = useRef(null);
//   const mediaRecorderRef = useRef(null);
//   const audioChunksRef = useRef([]);

//   useEffect(() => {
//     fetchBPData();
//   }, [timeRange]);

//   const fetchBPData = async () => {
//     try {
//       setLoading(true);
//       // API call to get blood pressure data
//       const response = await fetch(`/prediction/patient-data?timeRange=${timeRange}`, {
//         method: 'GET',
//         headers: {
//           'Authorization': `Bearer ${localStorage.getItem('token')}`
//         }
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setBpData(data);
//       } else {
//         console.error('Failed to fetch BP data');
//       }
//     } catch (error) {
//       console.error('Error fetching BP data:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setNewReading({
//       ...newReading,
//       [name]: value
//     });
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       setLoading(true);
      
//       // API call to save the new BP reading
//       const response = await fetch('/prediction/patient-data', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${localStorage.getItem('token')}`
//         },
//         body: JSON.stringify({
//           ...newReading,
//           type: 'bp_reading'
//         })
//       });

//       if (response.ok) {
//         // Check for anomalies with the ML model
//         const anomalyResponse = await fetch('/prediction/predict', {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json',
//             'Authorization': `Bearer ${localStorage.getItem('token')}`
//           },
//           body: JSON.stringify({
//             systolicBP: newReading.systolic,
//             diastolicBP: newReading.diastolic,
//             checkBPAnomaly: true
//           })
//         });

//         if (anomalyResponse.ok) {
//           const anomalyResult = await anomalyResponse.json();
//           setAnomalyDetected(anomalyResult.isAnomaly ? anomalyResult : null);
//         }

//         // Reset form and refresh data
//         setNewReading({
//           systolic: '',
//           diastolic: '',
//           pulse: '',
//           notes: '',
//           timestamp: new Date().toISOString(),
//         });
//         setShowForm(false);
//         fetchBPData();
//       } else {
//         console.error('Failed to save BP reading');
//       }
//     } catch (error) {
//       console.error('Error saving BP reading:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleImageUpload = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       setUploadImage(file);
//       // In a real app, you would use OCR (Optical Character Recognition) 
//       // to extract BP values from the image
//       // For this demo, we'll simulate processing the image
//       simulateImageProcessing(file);
//     }
//   };

//   const simulateImageProcessing = (file) => {
//     setLoading(true);
//     // Simulate OCR processing delay
//     setTimeout(() => {
//       // Simulated values extracted from image
//       setNewReading({
//         ...newReading,
//         systolic: '128',
//         diastolic: '85',
//         pulse: '72',
//         notes: 'Extracted from image upload'
//       });
//       setLoading(false);
//       setUploadImage(null);
//       setShowForm(true);
//     }, 2000);
//   };

//   const startVoiceRecording = async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       mediaRecorderRef.current = new MediaRecorder(stream);
      
//       mediaRecorderRef.current.ondataavailable = (event) => {
//         if (event.data.size > 0) {
//           audioChunksRef.current.push(event.data);
//         }
//       };
      
//       mediaRecorderRef.current.onstop = () => {
//         const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
//         processVoiceRecording(audioBlob);
//         audioChunksRef.current = [];
//       };
      
//       mediaRecorderRef.current.start();
//       setRecordingVoice(true);
//     } catch (error) {
//       console.error('Error accessing microphone:', error);
//     }
//   };

//   const stopVoiceRecording = () => {
//     if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
//       mediaRecorderRef.current.stop();
//       setRecordingVoice(false);
//     }
//   };

//   const processVoiceRecording = (audioBlob) => {
//     setLoading(true);
//     // In a real app, you would use speech-to-text to extract BP values
//     // For this demo, we'll simulate processing the audio
//     setTimeout(() => {
//       // Simulated values extracted from voice
//       setNewReading({
//         ...newReading,
//         systolic: '132',
//         diastolic: '88',
//         pulse: '75',
//         notes: 'Recorded via voice'
//       });
//       setLoading(false);
//       setShowForm(true);
//     }, 2000);
//   };

//   const exportToPDF = () => {
//     setExportLoading(true);
    
//     const doc = new jsPDF();
//     doc.setFontSize(18);
//     doc.text('Blood Pressure Report', 14, 22);
    
//     doc.setFontSize(12);
//     doc.text(`Generated on ${new Date().toLocaleDateString()}`, 14, 30);
    
//     // Add table headers
//     const headers = ['Date', 'Systolic', 'Diastolic', 'Pulse', 'Notes'];
//     let y = 40;
    
//     doc.setFontSize(10);
//     doc.text(headers[0], 14, y);
//     doc.text(headers[1], 60, y);
//     doc.text(headers[2], 90, y);
//     doc.text(headers[3], 120, y);
//     doc.text(headers[4], 150, y);
    
//     y += 10;
    
//     // Add table rows
//     bpData.forEach((reading) => {
//       const date = new Date(reading.timestamp).toLocaleDateString();
//       doc.text(date, 14, y);
//       doc.text(reading.systolic.toString(), 60, y);
//       doc.text(reading.diastolic.toString(), 90, y);
//       doc.text(reading.pulse?.toString() || '-', 120, y);
      
//       // Truncate notes to avoid overflow
//       const notes = reading.notes?.substring(0, 30) || '-';
//       doc.text(notes, 150, y);
      
//       y += 10;
      
//       // Add new page if needed
//       if (y > 280) {
//         doc.addPage();
//         y = 20;
//       }
//     });
    
//     // Save the PDF
//     doc.save('blood-pressure-report.pdf');
//     setExportLoading(false);
//   };

//   const exportToExcel = () => {
//     setExportLoading(true);
    
//     // Format data for Excel
//     const excelData = bpData.map((reading) => ({
//       Date: new Date(reading.timestamp).toLocaleDateString(),
//       Time: new Date(reading.timestamp).toLocaleTimeString(),
//       Systolic: reading.systolic,
//       Diastolic: reading.diastolic,
//       Pulse: reading.pulse || '',
//       Notes: reading.notes || '',
//     }));
    
//     // Create worksheet and workbook
//     const worksheet = XLSX.utils.json_to_sheet(excelData);
//     const workbook = XLSX.utils.book_new();
//     XLSX.utils.book_append_sheet(workbook, worksheet, 'BP Readings');
    
//     // Save the Excel file
//     XLSX.writeFile(workbook, 'blood-pressure-data.xlsx');
//     setExportLoading(false);
//   };

//   // Prepare chart data
//   const chartData = {
//     labels: bpData.map(reading => moment(reading.timestamp).format('MM/DD')),
//     datasets: [
//       {
//         label: 'Systolic',
//         data: bpData.map(reading => reading.systolic),
//         borderColor: 'rgb(255, 99, 132)',
//         backgroundColor: 'rgba(255, 99, 132, 0.5)',
//         tension: 0.1,
//       },
//       {
//         label: 'Diastolic',
//         data: bpData.map(reading => reading.diastolic),
//         borderColor: 'rgb(53, 162, 235)',
//         backgroundColor: 'rgba(53, 162, 235, 0.5)',
//         tension: 0.1,
//       },
//       {
//         label: 'Pulse',
//         data: bpData.map(reading => reading.pulse),
//         borderColor: 'rgb(75, 192, 192)',
//         backgroundColor: 'rgba(75, 192, 192, 0.5)',
//         tension: 0.1,
//       },
//     ],
//   };

//   const chartOptions = {
//     responsive: true,
//     plugins: {
//       legend: {
//         position: 'top',
//       },
//       title: {
//         display: true,
//         text: 'Blood Pressure Trends',
//       },
//       tooltip: {
//         callbacks: {
//           label: function(context) {
//             const label = context.dataset.label || '';
//             const value = context.parsed.y;
//             if (label === 'Systolic' || label === 'Diastolic') {
//               return `${label}: ${value} mmHg`;
//             } else {
//               return `${label}: ${value} bpm`;
//             }
//           }
//         }
//       }
//     },
//     scales: {
//       y: {
//         title: {
//           display: true,
//           text: 'Value'
//         }
//       },
//       x: {
//         title: {
//           display: true,
//           text: 'Date'
//         }
//       }
//     }
//   };

//   const handleBack = () => {
//     navigate('/dashboard');
//   };

//   return (
//     <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
//       <motion.div
//         initial={{ opacity: 0, y: 20 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.5 }}
//         className="max-w-6xl mx-auto"
//       >
//         <div className="flex items-center justify-between mb-6">
//           <div className="flex items-center">
//             <button
//               onClick={handleBack}
//               className="mr-4 p-2 rounded-full hover:bg-gray-200 transition-colors"
//             >
//               <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
//                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
//               </svg>
//             </button>
//             <h1 className="text-2xl font-bold text-gray-900">Blood Pressure Tracker</h1>
//           </div>
//           <div className="flex space-x-3">
//             <button
//               onClick={() => setShowForm(true)}
//               className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
//             >
//               Add Reading
//             </button>
//             <div className="relative">
//               <button
//                 onClick={() => fileInputRef.current.click()}
//                 className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
//               >
//                 Upload Image
//               </button>
//               <input
//                 type="file"
//                 ref={fileInputRef}
//                 onChange={handleImageUpload}
//                 accept="image/*"
//                 className="hidden"
//               />
//             </div>
//             <button
//               onClick={recordingVoice ? stopVoiceRecording : startVoiceRecording}
//               className={`px-4 py-2 ${recordingVoice ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'} text-white rounded-md transition-colors`}
//             >
//               {recordingVoice ? 'Stop Recording' : 'Record Voice'}
//             </button>
//           </div>
//         </div>

//         {anomalyDetected && (
//           <motion.div
//             initial={{ opacity: 0, scale: 0.9 }}
//             animate={{ opacity: 1, scale: 1 }}
//             className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md"
//           >
//             <div className="flex">
//               <div className="flex-shrink-0">
//                 <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
//                   <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
//                 </svg>
//               </div>
//               <div className="ml-3">
//                 <h3 className="text-sm font-medium text-red-800">Anomaly Detected</h3>
//                 <div className="mt-2 text-sm text-red-700">
//                   <p>
//                     Your blood pressure reading is outside the normal range. 
//                     {anomalyDetected.isCritical ? 
//                       ' This is a critical reading. Please consult a healthcare professional immediately.' : 
//                       ' Consider consulting with a healthcare professional.'}
//                   </p>
//                   <ul className="list-disc list-inside mt-2">
//                     {anomalyDetected.reasons.map((reason, index) => (
//                       <li key={index}>{reason}</li>
//                     ))}
//                   </ul>
//                 </div>
//               </div>
//               <div className="ml-auto">
//                 <button
//                   onClick={() => setAnomalyDetected(null)}
//                   className="inline-flex text-gray-400 hover:text-gray-500"
//                 >
//                   <span className="sr-only">Dismiss</span>
//                   <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
//                     <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
//                   </svg>
//                 </button>
//               </div>
//             </div>
//           </motion.div>
//         )}

//         {showForm && (
//           <motion.div
//             initial={{ opacity: 0, y: -20 }}
//             animate={{ opacity: 1, y: 0 }}
//             className="bg-white shadow rounded-lg p-6 mb-6"
//           >
//             <div className="flex justify-between items-center mb-4">
//               <h2 className="text-lg font-medium text-gray-900">Add New BP Reading</h2>
//               <button
//                 onClick={() => setShowForm(false)}
//                 className="text-gray-400 hover:text-gray-500"
//               >
//                 <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
//                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
//                 </svg>
//               </button>
//             </div>
            
//             <form onSubmit={handleSubmit} className="space-y-4">
//               <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//                 <div>
//                   <label htmlFor="systolic" className="block text-sm font-medium text-gray-700">
//                     Systolic (mmHg)
//                   </label>
//                   <input
//                     type="number"
//                     id="systolic"
//                     name="systolic"
//                     value={newReading.systolic}
//                     onChange={handleInputChange}
//                     required
//                     className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
//                   />
//                 </div>
                
//                 <div>
//                   <label htmlFor="diastolic" className="block text-sm font-medium text-gray-700">
//                     Diastolic (mmHg)
//                   </label>
//                   <input
//                     type="number"
//                     id="diastolic"
//                     name="diastolic"
//                     value={newReading.diastolic}
//                     onChange={handleInputChange}
//                     required
//                     className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
//                   />
//                 </div>
                
//                 <div>
//                   <label htmlFor="pulse" className="block text-sm font-medium text-gray-700">
//                     Pulse (bpm)
//                   </label>
//                   <input
//                     type="number"
//                     id="pulse"
//                     name="pulse"
//                     value={newReading.pulse}
//                     onChange={handleInputChange}
//                     className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
//                   />
//                 </div>
//               </div>
              
//               <div>
//                 <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
//                   Notes
//                 </label>
//                 <textarea
//                   id="notes"
//                   name="notes"
//                   rows={2}
//                   value={newReading.notes}
//                   onChange={handleInputChange}
//                   className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
//                 ></textarea>
//               </div>
              
//               <div className="flex justify-end">
//                 <button
//                   type="submit"
//                   disabled={loading}
//                   className="px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 flex items-center"
//                 >
//                   {loading ? (
//                     <>
//                       <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                         <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
//                         <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
//                       </svg>
//                       Saving...
//                     </>
//                   ) : 'Save Reading'}
//                 </button>
//               </div>
//             </form>
//           </motion.div>
//         )}

//         <div className="bg-white shadow rounded-lg p-6 mb-6">
//           <div className="flex justify-between items-center mb-6">
//             <h2 className="text-lg font-medium text-gray-900">Blood Pressure Analytics</h2>
//             <div className="flex space-x-4">
//               <select
//                 value={timeRange}
//                 onChange={(e) => setTimeRange(e.target.value)}
//                 className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
//               >
//                 <option value="week">Last Week</option>
//                 <option value="month">Last Month</option>
//                 <option value="year">Last Year</option>
//               </select>
              
//               <div className="flex space-x-2">
//                 <button
//                   onClick={exportToPDF}
//                   disabled={exportLoading || bpData.length === 0}
//                   className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
//                 >
//                   {exportLoading ? (
//                     <svg className="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                       <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
//                       <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
//                     </svg>
//                   ) : (
//                     <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
//                       <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
//                     </svg>
//                   )}
//                   PDF
//                 </button>
                
//                 <button
//                   onClick={exportToExcel}
//                   disabled={exportLoading || bpData.length === 0}
//                   className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center"
//                 >
//                   {exportLoading ? (
//                     <svg className="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                       <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
//                       <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
//                     </svg>
//                   ) : (
//                     <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
//                       <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
//                     </svg>
//                   )}
//                   Excel
//                 </button>
//               </div>
//             </div>
//           </div>
          
//           {loading ? (
//             <div className="flex justify-center items-center h-64">
//               <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
//             </div>
//           ) : bpData.length === 0 ? (
//             <div className="flex flex-col items-center justify-center h-64 text-gray-500">
//               <svg className="h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
//                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
//               </svg>
//               <p>No blood pressure data available.</p>
//               <p className="mt-2">Add your first reading to start tracking.</p>
//             </div>
//           ) : (
//             <div>
//               <div className="h-80 mb-8">
//                 <Line data={chartData} options={chartOptions} />
//               </div>
              
//               <div className="flex justify-between mb-4">
//                 <h3 className="text-lg font-medium text-gray-900">BP Readings</h3>
//                 <p className="text-sm text-gray-500">{bpData.length} reading(s)</p>
//               </div>
              
//               <div className="overflow-x-auto">
//                 <table className="min-w-full divide-y divide-gray-200">
//                   <thead className="bg-gray-50">
//                     <tr>
//                       <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
//                         Date & Time
//                       </th>
//                       <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
//                         Systolic
//                       </th>
//                       <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
//                         Diastolic
//                       </th>
//                       <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
//                         Pulse