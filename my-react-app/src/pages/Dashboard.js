import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';

const Dashboard = () => {
  const { currentUser, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsLoading(true);
        // Make an actual API call to fetch user data
        const response = await fetch('/auth/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setUserData(data);
        } else {
          console.error('Failed to fetch user data');
        }
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching user data:', error);
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [currentUser]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { id: 1, name: 'Hypertension Risk Prediction', icon: '🩺', path: '/prediction' },
    { id: 2, name: 'Blood Pressure Tracker', icon: '📊', path: '/bp-tracker' },
    { id: 3, name: 'Medication Reminder', icon: '💊', path: '/medication' },
    { id: 4, name: 'History & Reports', icon: '📝', path: '/history' },
    { id: 5, name: 'User Profile', icon: '👤', path: '/profile' },
  ];

  const cardItems = [
    { id: 1, title: 'Hypertension Risk', value: userData?.risk || 'N/A', unit: '%', color: 'bg-red-100 text-red-800' },
    { id: 2, title: 'Last BP Reading', value: userData?.lastBP || 'N/A', unit: 'mmHg', color: 'bg-blue-100 text-blue-800' },
    { id: 3, title: 'Medication Adherence', value: userData?.adherence || 'N/A', unit: '%', color: 'bg-green-100 text-green-800' },
    { id: 4, title: 'Next Reminder', value: userData?.nextReminder || 'N/A', unit: '', color: 'bg-purple-100 text-purple-800' },
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <motion.div 
        initial={{ x: -250 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.5 }}
        className="w-64 bg-white shadow-lg"
      >
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800">HyperTrack</h2>
          <p className="text-sm text-gray-600">Hypertension Management</p>
        </div>
        <nav className="mt-2">
          <ul>
            {menuItems.map((item, index) => (
              <motion.li 
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.5 }}
              >
                <Link
                  to={item.path}
                  className="flex items-center px-6 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors duration-200"
                >
                  <span className="mr-3">{item.icon}</span>
                  {item.name}
                </Link>
              </motion.li>
            ))}
          </ul>
        </nav>
        <div className="mt-auto p-6">
          <button
            onClick={handleLogout}
            className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
          >
            Logout
          </button>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto">
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <motion.h1 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="text-lg font-semibold text-gray-900"
            >
              Dashboard
            </motion.h1>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex items-center"
            >
              <span className="text-sm text-gray-600 mr-2">Welcome, {userData?.username || 'User'}</span>
              <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium">
                {userData?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
            </motion.div>
          </div>
        </header>

        <main className="py-6 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {cardItems.map((card, index) => (
              <motion.div
                key={card.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.5 }}
                className={`rounded-lg shadow-sm p-6 ${card.color}`}
              >
                <h3 className="text-sm font-medium">{card.title}</h3>
                <p className="text-3xl font-bold mt-2">{card.value} {card.unit}</p>
              </motion.div>
            ))}
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Health Activity</h2>
            <div className="space-y-4">
              {[
                { icon: '📊', title: 'Blood Pressure Recorded', time: '10 minutes ago', value: '120/80 mmHg' },
                { icon: '💊', title: 'Medication Taken', time: '4 hours ago', value: 'Amlodipine 5mg' },
                { icon: '🩺', title: 'Risk Assessment Completed', time: 'Yesterday', value: 'Risk: 35%' },
                { icon: '📝', title: 'Doctor Appointment', time: '3 days ago', value: 'Dr. Smith - Notes Available' },
                { icon: '💬', title: 'SMS Reminder Sent', time: '3 days ago', value: 'Medication reminder' }
              ].map((activity, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + (0.1 * index), duration: 0.5 }}
                  className="flex items-start p-4 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 mr-4">
                    {activity.icon}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.title}
                    </p>
                    <div className="flex justify-between">
                      <p className="text-sm text-gray-500 mt-1">
                        {activity.time}
                      </p>
                      <p className="text-sm font-semibold text-indigo-600">
                        {activity.value}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard; 