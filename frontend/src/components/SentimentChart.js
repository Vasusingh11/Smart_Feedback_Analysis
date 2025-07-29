import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { format, parseISO } from 'date-fns';

const SentimentChart = ({ data = [] }) => {
  // Process data for the chart
  const chartData = data.map(item => ({
    ...item,
    date: typeof item.date === 'string' ? item.date : format(new Date(item.date), 'MMM dd'),
    avg_sentiment: Number(item.avg_sentiment || 0),
    feedback_count: Number(item.feedback_count || 0)
  }));

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">{label}</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Sentiment:</span>
              <span className={`text-sm font-medium ${
                data.avg_sentiment > 0.1 
                  ? 'text-green-600 dark:text-green-400' 
                  : data.avg_sentiment < -0.1 
                    ? 'text-red-600 dark:text-red-400' 
                    : 'text-yellow-600 dark:text-yellow-400'
              }`}>
                {data.avg_sentiment.toFixed(3)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Feedback:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {data.feedback_count}
              </span>
            </div>
            {data.positive_count !== undefined && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-green-600 dark:text-green-400">Positive:</span>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    {data.positive_count}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-red-600 dark:text-red-400">Negative:</span>
                  <span className="text-sm font-medium text-red-600 dark:text-red-400">
                    {data.negative_count}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Neutral:</span>
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {data.neutral_count}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate dynamic Y-axis domain
  const sentimentValues = chartData.map(d => d.avg_sentiment);
  const minSentiment = Math.min(...sentimentValues);
  const maxSentiment = Math.max(...sentimentValues);
  const padding = Math.max(0.1, (maxSentiment - minSentiment) * 0.1);
  const yAxisDomain = [
    Math.max(-1, minSentiment - padding),
    Math.min(1, maxSentiment + padding)
  ];

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        <div className="text-center">
          <div className="text-lg mb-2">📊</div>
          <p>No sentiment trend data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#e5e7eb" 
            className="dark:stroke-gray-700" 
          />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            className="dark:stroke-gray-400"
          />
          <YAxis 
            domain={yAxisDomain}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            className="dark:stroke-gray-400"
            tickFormatter={(value) => value.toFixed(2)}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Reference line at y=0 */}
          <ReferenceLine 
            y={0} 
            stroke="#6b7280" 
            strokeDasharray="2 2"
            className="dark:stroke-gray-500"
          />
          
          {/* Positive sentiment reference line */}
          <ReferenceLine 
            y={0.1} 
            stroke="#10b981" 
            strokeDasharray="1 1" 
            opacity={0.5}
          />
          
          {/* Negative sentiment reference line */}
          <ReferenceLine 
            y={-0.1} 
            stroke="#ef4444" 
            strokeDasharray="1 1" 
            opacity={0.5}
          />
          
          <Line
            type="monotone"
            dataKey="avg_sentiment"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ 
              fill: '#3b82f6', 
              strokeWidth: 2, 
              r: 4,
              className: "hover:r-6 transition-all duration-200"
            }}
            activeDot={{ 
              r: 6, 
              stroke: '#3b82f6', 
              strokeWidth: 2, 
              fill: '#ffffff',
              className: "dark:fill-gray-800"
            }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center mt-4 space-x-6 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center">
          <div className="w-3 h-0.5 bg-green-500 mr-1"></div>
          <span>Positive (>0.1)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-0.5 bg-gray-500 mr-1"></div>
          <span>Neutral (-0.1 to 0.1)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-0.5 bg-red-500 mr-1"></div>
          <span>Negative (<-0.1)</span>
        </div>
      </div>
    </div>
  );
};

export default SentimentChart;