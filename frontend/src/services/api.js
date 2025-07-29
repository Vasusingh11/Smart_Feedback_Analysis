import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens or other headers
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      // Redirect to login if needed
    }
    return Promise.reject(error);
  }
);

// Dashboard API calls
export const fetchDashboardData = async () => {
  try {
    const response = await api.get('/dashboard/metrics?days=30');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch dashboard data');
  }
};

export const fetchSentimentTrends = async (days = 30) => {
  try {
    const response = await api.get(`/dashboard/trends?days=${days}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch sentiment trends');
  }
};

export const fetchTopicSummary = async (days = 30, minMentions = 3) => {
  try {
    const response = await api.get(`/dashboard/topics?days=${days}&min_mentions=${minMentions}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch topic summary');
  }
};

// Feedback API calls
export const fetchFeedback = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams({
      limit: params.limit || 100,
      offset: params.offset || 0,
      ...params
    });
    const response = await api.get(`/feedback?${queryParams}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch feedback');
  }
};

export const createFeedback = async (feedbackData) => {
  try {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to create feedback');
  }
};

// Analysis API calls
export const analyzeSentiment = async (text, options = {}) => {
  try {
    const response = await api.post('/analyze/sentiment', {
      text,
      vader_weight: options.vaderWeight || 0.6,
      textblob_weight: options.textblobWeight || 0.4
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to analyze sentiment');
  }
};

export const analyzeSentimentBatch = async (texts, batchSize = 100) => {
  try {
    const response = await api.post('/analyze/sentiment/batch', {
      texts,
      batch_size: batchSize
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to analyze sentiment batch');
  }
};

export const extractTopics = async (texts, nTopics = 10) => {
  try {
    const response = await api.post('/analyze/topics', {
      texts,
      n_topics: nTopics
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to extract topics');
  }
};

// Pipeline API calls
export const runPipeline = async (options = {}) => {
  try {
    const response = await api.post('/pipeline/run', {
      batch_size: options.batchSize || 1000,
      force_reprocess: options.forceReprocess || false
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to run pipeline');
  }
};

export const getPipelineStatus = async () => {
  try {
    const response = await api.get('/pipeline/status');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get pipeline status');
  }
};

// Health check
export const getHealthStatus = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get health status');
  }
};

export const getDetailedHealthStatus = async () => {
  try {
    const response = await api.get('/health/detailed');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get detailed health status');
  }
};

// Export data
export const exportFeedback = async (format = 'csv', days = 30) => {
  try {
    const response = await api.get(`/export/feedback?format=${format}&days=${days}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to export feedback');
  }
};

// Statistics
export const getSummaryStats = async (days = 30) => {
  try {
    const response = await api.get(`/stats/summary?days=${days}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get summary stats');
  }
};

// Configuration
export const getConfiguration = async () => {
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get configuration');
  }
};

// Mock data fallback functions for development
export const getMockDashboardData = () => {
  return {
    overall_metrics: {
      total_feedback: 2547,
      unique_customers: 1834,
      avg_sentiment: 0.234,
      positive_count: 1523,
      negative_count: 512,
      neutral_count: 512
    },
    sentiment_trends: [
      { date: '2024-01-15', avg_sentiment: 0.12, feedback_count: 45, positive_count: 28, negative_count: 10, neutral_count: 7 },
      { date: '2024-01-16', avg_sentiment: 0.18, feedback_count: 52, positive_count: 32, negative_count: 12, neutral_count: 8 },
      { date: '2024-01-17', avg_sentiment: 0.25, feedback_count: 48, positive_count: 31, negative_count: 9, neutral_count: 8 },
      { date: '2024-01-18', avg_sentiment: 0.31, feedback_count: 56, positive_count: 38, negative_count: 10, neutral_count: 8 },
      { date: '2024-01-19', avg_sentiment: 0.28, feedback_count: 41, positive_count: 27, negative_count: 8, neutral_count: 6 },
      { date: '2024-01-20', avg_sentiment: 0.35, feedback_count: 39, positive_count: 28, negative_count: 6, neutral_count: 5 },
      { date: '2024-01-21', avg_sentiment: 0.42, feedback_count: 44, positive_count: 32, negative_count: 7, neutral_count: 5 }
    ],
    topic_summary: [
      { topic: 'customer service', mention_count: 234, avg_relevance: 0.85, avg_sentiment: 0.42 },
      { topic: 'product quality', mention_count: 198, avg_relevance: 0.78, avg_sentiment: 0.31 },
      { topic: 'delivery shipping', mention_count: 167, avg_relevance: 0.82, avg_sentiment: 0.28 },
      { topic: 'website experience', mention_count: 143, avg_relevance: 0.76, avg_sentiment: 0.15 },
      { topic: 'pricing value', mention_count: 134, avg_relevance: 0.71, avg_sentiment: 0.09 }
    ],
    source_breakdown: [
      { source: 'email', feedback_count: 892, avg_sentiment: 0.28 },
      { source: 'survey', feedback_count: 645, avg_sentiment: 0.31 },
      { source: 'website', feedback_count: 523, avg_sentiment: 0.19 },
      { source: 'social_media', feedback_count: 287, avg_sentiment: 0.15 },
      { source: 'phone', feedback_count: 200, avg_sentiment: 0.42 }
    ]
  };
};

export const getMockRecentFeedback = () => {
  return [
    {
      feedback_id: 1,
      customer_id: 'CUST_001',
      feedback_text: 'Absolutely love this product! The quality exceeded my expectations and the customer service was outstanding.',
      sentiment_label: 'Positive',
      sentiment_score: 0.87,
      confidence_score: 0.92,
      source: 'email',
      timestamp: '2024-01-21T14:30:00Z',
      rating: 5
    },
    {
      feedback_id: 2,
      customer_id: 'CUST_002',
      feedback_text: 'The delivery was slower than expected and the packaging was damaged when it arrived.',
      sentiment_label: 'Negative',
      sentiment_score: -0.45,
      confidence_score: 0.78,
      source: 'survey',
      timestamp: '2024-01-21T13:15:00Z',
      rating: 2
    },
    {
      feedback_id: 3,
      customer_id: 'CUST_003',
      feedback_text: 'Product works as described. Nothing exceptional but meets basic requirements.',
      sentiment_label: 'Neutral',
      sentiment_score: 0.02,
      confidence_score: 0.65,
      source: 'website',
      timestamp: '2024-01-21T12:45:00Z',
      rating: 3
    },
    {
      feedback_id: 4,
      customer_id: 'CUST_004',
      feedback_text: 'Great customer support team! They resolved my issue quickly and were very professional.',
      sentiment_label: 'Positive',
      sentiment_score: 0.72,
      confidence_score: 0.89,
      source: 'phone',
      timestamp: '2024-01-21T11:30:00Z',
      rating: 5
    },
    {
      feedback_id: 5,
      customer_id: 'CUST_005',
      feedback_text: 'Website navigation is confusing and the checkout process failed multiple times.',
      sentiment_label: 'Negative',
      sentiment_score: -0.62,
      confidence_score: 0.84,
      source: 'social_media',
      timestamp: '2024-01-21T10:20:00Z',
      rating: 1
    }
  ];
};

// Helper function to determine if we should use mock data
export const shouldUseMockData = () => {
  return process.env.REACT_APP_USE_MOCK_DATA === 'true' || process.env.NODE_ENV === 'development';
};

export default api;