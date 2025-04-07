import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Prediction from './pages/Prediction';
import BPTracker from './pages/BPTracker';
import Medication from './pages/Medication';
import History from './pages/History';
import PrivateRoute from './components/PrivateRoute';
import './App.css';

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route 
            path="/dashboard" 
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            } 
          />
          
          <Route 
            path="/prediction" 
            element={
              <PrivateRoute>
                <Prediction />
              </PrivateRoute>
            } 
          />
          
          <Route 
            path="/bp-tracker" 
            element={
              <PrivateRoute>
                <BPTracker />
              </PrivateRoute>
            } 
          />
          
          <Route 
            path="/medication" 
            element={
              <PrivateRoute>
                <Medication />
              </PrivateRoute>
            } 
          />
          
          <Route 
            path="/history" 
            element={
              <PrivateRoute>
                <History />
              </PrivateRoute>
            } 
          />
          
          {/* Redirect to dashboard if trying to access root */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Catch all route - redirect to login */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}
