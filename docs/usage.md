# Smart Feedback Analysis Platform - Usage Guide

This comprehensive guide covers all aspects of using the Smart Feedback Analysis Platform, from basic setup to advanced features.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data Input Methods](#data-input-methods)
3. [Running Analysis](#running-analysis)
4. [Understanding Results](#understanding-results)
5. [Power BI Dashboards](#power-bi-dashboards)
6. [API Usage](#api-usage)
7. [Automation & Scheduling](#automation--scheduling)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Features](#advanced-features)

## Quick Start

### 1. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-feedback-analysis.git
cd smart-feedback-analysis

# Run the installer
python scripts/install.py

# Setup database
python scripts/setup_database.py --sample-data

# Run first analysis
python scripts/run_analysis.py run
```

### 2. Basic Configuration

Edit `config/config.yaml` with your database credentials:

```yaml
database:
  server: "your-server.database.windows.net"
  database: "feedback_analysis"
  username: "your-username"
  password: "your-password"
```

### 3. Generate Sample Data (Optional)

```bash
python scripts/run_analysis.py sample --count 1000
```

## Data Input Methods

### Method 1: Direct Database Insert

```python
import pandas as pd
from src.database.connection import DatabaseHandler

# Create feedback data
feedback_data = [{
    'customer_id': 'CUST_001',
    'feedback_text': 'Great product! Excellent customer service.',
    'source': 'email',
    'rating': 5,
    'product_category': 'Electronics'
}]

# Insert into database
df = pd.DataFrame(feedback_data)
db_handler = DatabaseHandler(config=your_config)
db_handler.insert_dataframe(df, 'feedback')
```

### Method 2: CSV Import

```python
# Import from CSV file
feedback_df = pd.read_csv('your_feedback_data.csv')

# Required columns: customer_id, feedback_text, source
# Optional columns: rating, product_category, timestamp

# Insert to database
db_handler.insert_dataframe(feedback_df, 'feedback')
```

### Method 3: API Endpoint

```bash
# Using curl
curl -X POST "http://localhost:8000/feedback" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": "CUST_001",
       "feedback_text": "Great product!",
       "source": "api",
       "rating": 5
     }'
```

### Method 4: Automated Integration

```python
# Example: Integrate with survey platform
def sync_survey_data():
    # Fetch from external API
    survey_responses = fetch_from_survey_platform()
    
    # Transform to required format
    feedback_data = transform_survey_data(survey_responses)
    
    # Insert to database
    db_handler.insert_dataframe(feedback_data, 'feedback')
```

## Running Analysis

### Command Line Interface

#### Basic Analysis Run
```bash
# Run complete pipeline
python scripts/run_analysis.py run

# Run with custom batch size
python scripts/run_analysis.py run --config custom_config.yaml

# Check pipeline status
python scripts/run_analysis.py status

# Run maintenance tasks
python scripts/run_analysis.py maintenance
```

#### Generate Reports
```bash
# Export recent data
python scripts/run_analysis.py export --format csv --days 30

# Generate summary report
python scripts/run_analysis.py report --days 7
```

### Programmatic Usage

```python
from src.automation.pipeline import FeedbackAnalysisPipeline

# Initialize pipeline
pipeline = FeedbackAnalysisPipeline(config_path='config/config.yaml')

# Run analysis
result = pipeline.run_full_pipeline()

print(f"Processed {result['statistics']['feedback_processed']} items")
print(f"Success rate: {result['statistics']['success_rate']}%")
```

### Individual Component Usage

#### Sentiment Analysis Only
```python
from src.data_processing.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Single text analysis
result = analyzer.analyze_sentiment("This product is amazing!")
print(f"Sentiment: {result['label']} (score: {result['score']})")

# Batch analysis
texts = ["Great service!", "Poor quality", "Average experience"]
results_df = analyzer.analyze_batch(texts)
print(results_df[['label', 'score', 'confidence']])
```

#### Topic Extraction Only
```python
from src.data_processing.topic_extractor import TopicExtractor

extractor = TopicExtractor(n_topics=5)

# Extract topics
texts = [
    "Customer service was excellent",
    "Delivery was fast and secure", 
    "Product quality could be better",
    "Website is easy to navigate"
]

topics = extractor.extract_topics_kmeans(texts, n_topics=3)

for topic in topics:
    print(f"Topic: {topic['topic_name']}")
    print(f"Keywords: {', '.join(topic['keywords'][:5])}")
```

## Understanding Results

### Sentiment Analysis Results

```python
{
    'score': 0.7234,           # -1 (negative) to 1 (positive)
    'label': 'Positive',       # Positive, Negative, or Neutral
    'confidence': 0.8567,      # 0 to 1 (higher = more confident)
    'vader_compound': 0.6982,  # VADER-specific score
    'textblob_polarity': 0.75, # TextBlob-specific score
    'subjectivity': 0.4        # 0 (objective) to 1 (subjective)
}
```

**Interpretation:**
- **Score > 0.05**: Positive sentiment
- **Score < -0.05**: Negative sentiment  
- **-0.05 ≤ Score ≤ 0.05**: Neutral sentiment
- **Confidence > 0.8**: High confidence
- **Confidence < 0.3**: Low confidence (manual review recommended)

### Topic Analysis Results

```python
{
    'topic_id': 0,
    'topic_name': 'customer service support',
    'keywords': ['customer', 'service', 'support', 'help', 'team'],
    'document_count': 45,
    'coherence_score': 0.834,
    'relevance_score': 0.67
}
```

**Interpretation:**
- **Document Count**: Number of feedback items mentioning this topic
- **Coherence Score**: How well the keywords relate (higher = better)
- **Relevance Score**: How relevant this topic is to the specific document

### Database Views

Query pre-built views for insights:

```sql
-- Daily sentiment trends
SELECT * FROM daily_sentiment_trend 
WHERE date >= DATEADD(day, -30, GETDATE())
ORDER BY date;

-- Top topics by sentiment
SELECT * FROM topic_sentiment_summary 
ORDER BY mention_count DESC;

-- Source performance
SELECT * FROM source_performance 
ORDER BY avg_sentiment DESC;
```

## Power BI Dashboards

### Setup Connection

1. **Open Power BI Desktop**
2. **Get Data** → **SQL Server**
3. **Enter server details:**
   - Server: your-server.database.windows.net
   - Database: feedback_analysis
4. **Select tables and views:**
   - daily_sentiment_trend
   - topic_sentiment_summary  
   - source_performance
   - customer_journey_analysis

### Import DAX Measures

Copy measures from `powerbi/dax_measures.txt`:

```dax
Total Feedback = COUNTROWS(feedback)

Average Sentiment = AVERAGE(sentiment_analysis[sentiment_score])

Positive Percentage = 
DIVIDE([Positive Count], [Total Feedback]) * 100
```

### Dashboard Layout

#### Page 1: Executive Summary
- **KPI Cards**: Total Feedback, Avg Sentiment, Positive %, Growth %
- **Line Chart**: Sentiment trend over time
- **Donut Chart**: Sentiment distribution
- **Bar Chart**: Top sources by volume

#### Page 2: Detailed Analysis  
- **Table**: Recent feedback with sentiment scores
- **Scatter Plot**: Rating vs Sentiment correlation
- **Heat Map**: Activity by hour/day
- **Tree Map**: Topics by mention count

#### Page 3: Customer Insights
- **Customer Journey**: Sentiment evolution over time
- **Retention Analysis**: New vs returning customers
- **Segment Performance**: Customer lifecycle stages

### Refresh Schedule

Set up automatic refresh:
1. **Publish to Power BI Service**
2. **Dataset Settings** → **Scheduled Refresh**
3. **Configure frequency**: Every 2 hours
4. **Set credentials**: Database connection

## API Usage

### Start API Server

```bash
# Development
python src/api/endpoints.py

# Production
uvicorn src.api.endpoints:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Analyze Sentiment
```bash
curl -X POST "http://localhost:8000/analyze/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text": "Great product, highly recommended!"}'
```

#### Extract Topics
```bash
curl -X POST "http://localhost:8000/analyze/topics" \
     -H "Content-Type: application/json" \
     -d '{
       "texts": [
         "Customer service was excellent",
         "Fast delivery and good packaging",
         "Product quality could be better"
       ],
       "n_topics": 3
     }'
```

#### Get Dashboard Metrics
```bash
curl "http://localhost:8000/dashboard/metrics?days=30"
```

#### Run Pipeline
```bash
curl -X POST "http://localhost:8000/pipeline/run" \
     -H "Content-Type: application/json" \
     -d '{"batch_size": 1000}'
```

### Python API Client

```python
import requests

class FeedbackAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_sentiment(self, text):
        response = requests.post(
            f"{self.base_url}/analyze/sentiment",
            json={"text": text}
        )
        return response.json()
    
    def get_metrics(self, days=30):
        response = requests.get(
            f"{self.base_url}/dashboard/metrics",
            params={"days": days}
        )
        return response.json()

# Usage
api = FeedbackAPI()
result = api.analyze_sentiment("This is amazing!")
print(f"Sentiment: {result['label']}")
```

## Automation & Scheduling

### Built-in Scheduler

```bash
# Start scheduler daemon
python scripts/scheduler.py

# List scheduled jobs
python scripts/scheduler.py --list-jobs

# Run specific job once
python scripts/scheduler.py --run-once pipeline
```

### Custom Scheduling

#### Using Cron (Linux/macOS)
```bash
# Edit crontab
crontab -e

# Add entries
0 */4 * * * cd /path/to/project && python scripts/run_analysis.py run
0 9 * * * cd /path/to/project && python scripts/run_analysis.py report --email
```

#### Using Windows Task Scheduler
1. **Open Task Scheduler**
2. **Create Basic Task**
3. **Set trigger**: Every 4 hours
4. **Set action**: Start program
   - Program: python
   - Arguments: scripts/run_analysis.py run
   - Start in: C:\path\to\project

### Docker Scheduling

```yaml
# docker-compose.yml
services:
  scheduler:
    build: .
    command: python scripts/scheduler.py
    environment:
      - SCHEDULE_ENABLED=true
    volumes:
      - ./logs:/app/logs
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Test connection
python scripts/health_check.py --check database

# Common solutions:
# - Check server/database names
# - Verify credentials
# - Ensure firewall allows connection
# - Install ODBC driver
```

#### 2. NLTK Data Missing
```bash
# Download NLTK data
python -c "import nltk; nltk.download('all')"

# Or specific datasets
python -c "import nltk; nltk.download('vader_lexicon')"
```

#### 3. Memory Issues with Large Datasets
```python
# Reduce batch size
config['processing']['batch_size'] = 500

# Enable incremental processing
config['processing']['incremental'] = True
```

#### 4. Low Sentiment Accuracy
```python
# Adjust model weights
config['sentiment_analysis']['vader_weight'] = 0.7
config['sentiment_analysis']['textblob_weight'] = 0.3

# Increase confidence threshold
config['sentiment_analysis']['confidence_threshold'] = 0.5
```

### Health Monitoring

```bash
# Complete health check
python scripts/health_check.py

# Specific component checks
python scripts/health_check.py --check system
python scripts/health_check.py --check database
python scripts/health_check.py --check dependencies

# JSON output for monitoring
python scripts/health_check.py --json
```

### Log Analysis

```bash
# View recent logs
tail -f logs/pipeline.log

# Search for errors
grep "ERROR" logs/pipeline.log

# View specific component logs
grep "sentiment_analyzer" logs/pipeline.log
```

## Advanced Features

### Custom Sentiment Models

```python
# Implement custom sentiment analyzer
class CustomSentimentAnalyzer(SentimentAnalyzer):
    def analyze_sentiment(self, text):
        # Your custom logic here
        custom_score = self.custom_model.predict(text)
        
        # Return standard format
        return {
            'score': custom_score,
            'label': self.score_to_label(custom_score),
            'confidence': self.calculate_confidence(custom_score)
        }

# Use in pipeline
pipeline.sentiment_analyzer = CustomSentimentAnalyzer()
```

### Advanced Topic Modeling

```python
# Use advanced topic modeling
from sklearn.decomposition import LatentDirichletAllocation

class AdvancedTopicExtractor(TopicExtractor):
    def extract_topics_advanced(self, texts, n_topics=10):
        # Implement LDA with custom parameters
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=20,
            learning_method='online',
            random_state=42
        )
        
        # Your advanced implementation
        return self.process_lda_results(lda, texts)
```

### Real-time Processing

```python
# Stream processing setup
from kafka import KafkaConsumer

def process_feedback_stream():
    consumer = KafkaConsumer('feedback-topic')
    
    for message in consumer:
        feedback_data = json.loads(message.value)
        
        # Process immediately
        result = pipeline.process_single_feedback(feedback_data)
        
        # Update dashboard in real-time
        update_realtime_dashboard(result)
```

### Multi-language Support

```python
# Configure for multiple languages
config['sentiment_analysis']['languages'] = ['en', 'es', 'fr']

# Use language-specific models
from textblob import TextBlob

def detect_language(text):
    try:
        return TextBlob(text).detect_language()
    except:
        return 'en'  # Default to English

def analyze_multilingual_sentiment(text):
    lang = detect_language(text)
    
    if lang == 'es':
        return analyze_spanish_sentiment(text)
    elif lang == 'fr':
        return analyze_french_sentiment(text)
    else:
        return analyze_english_sentiment(text)
```

### Custom Notifications

```python
# Implement custom notification channels
class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_alert(self, message, severity='info'):
        color = {'error': 'danger', 'warning': 'warning', 'info': 'good'}[severity]
        
        payload = {
            'attachments': [{
                'color': color,
                'text': message,
                'ts': time.time()
            }]
        }
        
        requests.post(self.webhook_url, json=payload)

# Register custom notifier
pipeline.add_notifier('slack', SlackNotifier(webhook_url))
```

### Performance Optimization

```python
# Enable caching for repeated queries
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_sentiment_analysis(text_hash):
    return analyzer.analyze_sentiment(text)

# Use database connection pooling
config['database']['pool_size'] = 20
config['database']['max_overflow'] = 30

# Enable parallel processing
config['processing']['parallel'] = True
config['processing']['max_workers'] = 8
```

This usage guide covers the most common scenarios and advanced features. For specific implementation details, refer to the code documentation and examples in the `examples/` directory.