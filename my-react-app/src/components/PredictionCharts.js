import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area, ScatterChart, Scatter, ZAxis, ReferenceArea
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

// Function to format date
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const PredictionCharts = ({ predictionData }) => {
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [riskFactorFrequency, setRiskFactorFrequency] = useState([]);
  const [trendAnalysis, setTrendAnalysis] = useState(null);
  
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
      date: formatDate(item.prediction_date),
      fullDate: new Date(item.prediction_date).toLocaleDateString() + ' ' + new Date(item.prediction_date).toLocaleTimeString(),
      score: item.prediction_score,
      riskLevel: item.risk_level,
      riskColor: riskLevelColors[item.risk_level] || colors.primary
    }));
    setTimeSeriesData(timeData);
    
    // Calculate trend analysis
    if (timeData.length >= 2) {
      const firstScore = timeData[0].score;
      const lastScore = timeData[timeData.length - 1].score;
      const scoreDiff = lastScore - firstScore;
      const percentChange = ((scoreDiff) / firstScore * 100).toFixed(1);
      
      setTrendAnalysis({
        firstDate: timeData[0].date,
        lastDate: timeData[timeData.length - 1].date,
        firstScore,
        lastScore,
        scoreDiff,
        percentChange,
        improving: scoreDiff < 0,
        worsening: scoreDiff > 0,
        stable: scoreDiff === 0
      });
    }
    
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
    
    // Collate risk factors from all predictions
    const factorCounts = {};
    sortedData.forEach(prediction => {
      if (prediction.risk_factors && Array.isArray(prediction.risk_factors)) {
        prediction.risk_factors.forEach(factor => {
          factorCounts[factor] = (factorCounts[factor] || 0) + 1;
        });
      }
    });
    
    // Convert to array and sort by frequency
    const factorFrequency = Object.entries(factorCounts)
      .map(([factor, count]) => ({ 
        factor, 
        count,
        percentage: (count / sortedData.length * 100).toFixed(0)
      }))
      .sort((a, b) => b.count - a.count);
    
    setRiskFactorFrequency(factorFrequency);
    
    // Prepare feature importance data if available
    const latestPrediction = sortedData[sortedData.length - 1];
    if (latestPrediction.feature_importances && typeof latestPrediction.feature_importances === 'object' && latestPrediction.feature_importances !== null) {
      try {
        const importanceData = Object.entries(latestPrediction.feature_importances)
          .map(([name, value]) => ({
            name: name.replace(/([A-Z])/g, ' $1').trim(), // Add spaces before capital letters
            value: parseFloat(value),
          }))
          .filter(item => !isNaN(item.value)) // Filter out non-numeric values
          .sort((a, b) => b.value - a.value) // Sort by importance
          .slice(0, 10); // Take top 10
        
        setFeatureImportance(importanceData);
      } catch (error) {
        console.error('Error processing feature importances:', error);
        setFeatureImportance([]);
      }
    } else {
      // If feature importances not available, set empty array
      setFeatureImportance([]);
    }
  };
  
  if (!predictionData || predictionData.length === 0) {
    return <div className="text-center py-6 text-gray-500">No prediction data available</div>;
  }
  
  return (
    <div className="space-y-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Prediction Analytics</h2>
      
      {/* Trend Summary */}
      {trendAnalysis && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Trend Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className={`p-4 rounded-lg ${trendAnalysis.improving ? 'bg-green-50' : trendAnalysis.worsening ? 'bg-red-50' : 'bg-gray-50'}`}>
              <h4 className="text-sm font-medium text-gray-500">Change in Risk Score</h4>
              <p className={`text-2xl font-bold ${trendAnalysis.improving ? 'text-green-600' : trendAnalysis.worsening ? 'text-red-600' : 'text-gray-600'}`}>
                {trendAnalysis.scoreDiff > 0 ? '+' : ''}{trendAnalysis.scoreDiff}%
              </p>
              <p className="text-sm text-gray-500">From {trendAnalysis.firstDate} to {trendAnalysis.lastDate}</p>
            </div>
            
            <div className="p-4 rounded-lg bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">Current Risk Score</h4>
              <p className="text-2xl font-bold text-indigo-600">{trendAnalysis.lastScore}%</p>
              <p className="text-sm text-gray-500">As of {trendAnalysis.lastDate}</p>
            </div>
            
            <div className="p-4 rounded-lg bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">Total Predictions</h4>
              <p className="text-2xl font-bold text-indigo-600">{predictionData.length}</p>
              <p className="text-sm text-gray-500">Over {trendAnalysis ? Math.ceil((new Date(predictionData[predictionData.length-1].prediction_date) - new Date(predictionData[0].prediction_date)) / (1000 * 60 * 60 * 24)) : 0} days</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Risk Score Timeline */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Score Timeline</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
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
              <defs>
                <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.primary} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={colors.primary} stopOpacity={0.2}/>
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="score"
                name="Risk Score"
                stroke={colors.primary}
                fillOpacity={1}
                fill="url(#colorScore)"
                activeDot={{ r: 8 }}
                strokeWidth={2}
              />
              {/* Add reference areas for risk levels */}
              <ReferenceArea y1={0} y2={20} fillOpacity={0.1} fill={colors.lowRisk} />
              <ReferenceArea y1={20} y2={50} fillOpacity={0.1} fill={colors.moderateRisk} />
              <ReferenceArea y1={50} y2={80} fillOpacity={0.1} fill={colors.highRisk} />
              <ReferenceArea y1={80} y2={100} fillOpacity={0.1} fill={colors.veryHighRisk} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Risk Distribution & Common Risk Factors */}
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
        
        {/* Common Risk Factors */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Common Risk Factors</h3>
          {riskFactorFrequency.length > 0 ? (
            <div className="h-72 overflow-auto">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={riskFactorFrequency.slice(0, 8)}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, predictionData.length]} />
                  <YAxis 
                    type="category" 
                    dataKey="factor" 
                    width={80}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    formatter={(value, name, props) => [
                      `${value} (${props.payload.percentage}%)`, 
                      'Frequency'
                    ]} 
                  />
                  <Bar dataKey="count" fill={colors.tertiary}>
                    {riskFactorFrequency.slice(0, 8).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors.chartColors[index % colors.chartColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              Risk factor data not available
            </div>
          )}
        </div>
      </div>
      
      {/* Additional visualizations based on data availability */}
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
      
      {/* Risk transition visualization */}
      {timeSeriesData.length >= 2 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Risk Level Transitions</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 20, right: 20, bottom: 10, left: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" name="Date" />
                <YAxis dataKey="score" name="Score" domain={[0, 100]} />
                <ZAxis range={[100, 100]} />
                <Tooltip 
                  formatter={(value, name, props) => name === 'Score' ? [`${value}%`, name] : [value, name]}
                  labelFormatter={(label) => timeSeriesData.find(d => d.date === label)?.fullDate || label}
                />
                <Scatter
                  name="Risk Scores"
                  data={timeSeriesData}
                  fill="#8884d8"
                >
                  {timeSeriesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.riskColor} />
                  ))}
                </Scatter>
                {/* Add reference lines for risk thresholds */}
                <ReferenceArea y1={0} y2={20} fillOpacity={0.1} fill={colors.lowRisk} />
                <ReferenceArea y1={20} y2={50} fillOpacity={0.1} fill={colors.moderateRisk} />
                <ReferenceArea y1={50} y2={80} fillOpacity={0.1} fill={colors.highRisk} />
                <ReferenceArea y1={80} y2={100} fillOpacity={0.1} fill={colors.veryHighRisk} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center mt-2 text-sm">
            <div className="flex items-center mr-4">
              <span className="inline-block w-3 h-3 mr-1 rounded-full" style={{backgroundColor: colors.lowRisk}}></span>
              <span>Low Risk (0-20%)</span>
            </div>
            <div className="flex items-center mr-4">
              <span className="inline-block w-3 h-3 mr-1 rounded-full" style={{backgroundColor: colors.moderateRisk}}></span>
              <span>Moderate Risk (20-50%)</span>
            </div>
            <div className="flex items-center mr-4">
              <span className="inline-block w-3 h-3 mr-1 rounded-full" style={{backgroundColor: colors.highRisk}}></span>
              <span>High Risk (50-80%)</span>
            </div>
            <div className="flex items-center">
              <span className="inline-block w-3 h-3 mr-1 rounded-full" style={{backgroundColor: colors.veryHighRisk}}></span>
              <span>Very High Risk (80-100%)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionCharts; 