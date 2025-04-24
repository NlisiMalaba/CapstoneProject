import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from 'recharts';

// Color palette for consistent styling
const colors = {
  primary: '#4F46E5',  // Indigo
  secondary: '#10B981', // Emerald
  tertiary: '#F59E0B',  // Amber
  danger: '#EF4444',    // Red
  lowRisk: '#10B981',   // Green
  moderateRisk: '#F59E0B', // Amber
  highRisk: '#F97316',  // Orange
  veryHighRisk: '#EF4444', // Red
  chartColors: ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']
};

// Risk level colors mapping
const riskLevelColors = {
  'Low': colors.lowRisk,
  'Moderate': colors.moderateRisk,
  'High': colors.highRisk,
  'Very High': colors.veryHighRisk
};

const PredictionCharts = ({ predictionData }) => {
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
  
  useEffect(() => {
    if (predictionData && predictionData.length > 0) {
      prepareChartData(predictionData);
    }
  }, [predictionData]);
  
  const prepareChartData = (data) => {
    // Sort data by date
    const sortedData = [...data].sort((a, b) => 
      new Date(a.prediction_date) - new Date(b.prediction_date)
    );
    
    // Prepare time series data
    const timeData = sortedData.map(item => ({
      date: new Date(item.prediction_date).toLocaleDateString(),
      score: item.prediction_score,
      riskLevel: item.risk_level
    }));
    setTimeSeriesData(timeData);
    
    // Prepare risk distribution data
    const riskCounts = {};
    sortedData.forEach(item => {
      riskCounts[item.risk_level] = (riskCounts[item.risk_level] || 0) + 1;
    });
    
    const riskData = Object.keys(riskCounts).map(risk => ({
      name: risk,
      value: riskCounts[risk],
      color: riskLevelColors[risk] || colors.primary
    }));
    setRiskDistribution(riskData);
    
    // Prepare feature importance data
    const latestPrediction = sortedData[sortedData.length - 1];
    if (latestPrediction.feature_importances) {
      const importanceData = Object.entries(latestPrediction.feature_importances)
        .map(([name, value]) => ({
          name: name.replace(/([A-Z])/g, ' $1').trim(), // Add spaces before capital letters
          value: parseFloat(value),
        }))
        .sort((a, b) => b.value - a.value) // Sort by importance
        .slice(0, 10); // Take top 10
      
      setFeatureImportance(importanceData);
    }
  };
  
  if (!predictionData || predictionData.length === 0) {
    return <div className="text-center py-6 text-gray-500">No prediction data available</div>;
  }
  
  return (
    <div className="space-y-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Prediction Analytics</h2>
      
      {/* Risk Score Timeline */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Score Timeline</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={timeSeriesData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip
                formatter={(value, name) => [`${value}%`, 'Risk Score']}
                labelFormatter={(label) => `Date: ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="score"
                name="Risk Score"
                stroke={colors.primary}
                activeDot={{ r: 8 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Risk Distribution & Feature Importance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Level Distribution */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Level Distribution</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} prediction(s)`, 'Count']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Feature Importance */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Feature Importance</h3>
          {featureImportance.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={featureImportance}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 'dataMax']} />
                  <YAxis 
                    type="category" 
                    dataKey="name" 
                    width={80}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Importance']} />
                  <Bar dataKey="value" fill={colors.secondary}>
                    {featureImportance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors.chartColors[index % colors.chartColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              Feature importance data not available
            </div>
          )}
        </div>
      </div>
      
      {/* Key Risk Factors Radar Chart */}
      {featureImportance.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Factor Analysis</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={featureImportance.slice(0, 8)}>
                <PolarGrid />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis angle={30} domain={[0, 'auto']} />
                <Radar
                  name="Risk Factors"
                  dataKey="value"
                  stroke={colors.primary}
                  fill={colors.primary}
                  fillOpacity={0.6}
                />
                <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Importance']} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionCharts; 