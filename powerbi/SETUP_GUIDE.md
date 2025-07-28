# Power BI Dashboard Setup Guide

This guide walks you through setting up comprehensive dashboards for the Smart Feedback Analysis Platform using Power BI Desktop and Power BI Service.

## Prerequisites

- Power BI Desktop (latest version)
- SQL Server database with feedback analysis data
- Power BI Pro license (for sharing and collaboration)
- Database credentials with read access

## Step 1: Database Connection Setup

### 1.1 Open Power BI Desktop

1. Launch Power BI Desktop
2. Click **Get Data** or use **Home** → **Get Data**
3. Select **SQL Server** from the database section

### 1.2 Configure Connection

**Server Details:**
```
Server: your-server.database.windows.net
Database: feedback_analysis
```

**Authentication:**
- Choose **Database** for SQL Server authentication
- Enter username and password
- Or choose **Windows** for Windows authentication

**Advanced Options:**
```sql
-- Optional: Add custom SQL statement for specific data
SELECT f.*, sa.sentiment_score, sa.sentiment_label, sa.confidence_score
FROM feedback f
LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
WHERE f.timestamp >= DATEADD(month, -6, GETDATE())
```

### 1.3 Select Tables and Views

**Required Tables:**
- ✅ feedback
- ✅ sentiment_analysis  
- ✅ topic_analysis
- ✅ satisfaction_metrics

**Recommended Views:**
- ✅ daily_sentiment_trend
- ✅ topic_sentiment_summary
- ✅ source_performance
- ✅ customer_journey_analysis
- ✅ hourly_activity_patterns

Click **Load** or **Transform Data** for data preprocessing.

## Step 2: Data Model Configuration

### 2.1 Relationships

Power BI should auto-detect relationships, but verify these connections:

```
feedback (feedback_id) → sentiment_analysis (feedback_id) [1:1]
feedback (feedback_id) → topic_analysis (feedback_id) [1:*]
feedback (customer_id) → customer_journey_analysis (customer_id) [*:1]
```

### 2.2 Data Types

Ensure correct data types:
- **feedback_id**: Whole Number
- **timestamp**: Date/Time
- **sentiment_score**: Decimal Number
- **rating**: Whole Number
- **confidence_score**: Decimal Number

### 2.3 Hierarchies

Create date hierarchy:
1. Right-click **timestamp** field
2. Select **New Hierarchy**
3. Name it **Date Hierarchy**
4. Add levels: Year → Quarter → Month → Day

## Step 3: Import DAX Measures

### 3.1 Core Metrics

Copy measures from `dax_measures.txt` and create them in Power BI:

**Navigation:** Modeling → New Measure

```dax
Total Feedback = COUNTROWS(feedback)

Average Sentiment = AVERAGE(sentiment_analysis[sentiment_score])

Positive Percentage = 
DIVIDE([Positive Count], [Total Feedback]) * 100

Negative Percentage = 
DIVIDE([Negative Count], [Total Feedback]) * 100

Sentiment Trend = 
VAR CurrentMonth = [Average Sentiment This Month]
VAR LastMonth = [Average Sentiment Last Month]
RETURN
IF(ISBLANK(LastMonth), BLANK(), CurrentMonth - LastMonth)
```

### 3.2 Advanced Measures

```dax
Net Promoter Score = 
VAR Promoters = CALCULATE(COUNTROWS(feedback), feedback[rating] >= 4)
VAR Detractors = CALCULATE(COUNTROWS(feedback), feedback[rating] <= 2)
VAR Total = COUNTROWS(feedback)
RETURN
IF(Total > 0, ((Promoters - Detractors) / Total) * 100, BLANK())

Customer Satisfaction Index = 
VAR PositiveWeight = [Positive Count] * 1
VAR NeutralWeight = [Neutral Count] * 0.5
VAR NegativeWeight = [Negative Count] * 0
RETURN
DIVIDE(PositiveWeight + NeutralWeight + NegativeWeight, [Total Feedback]) * 100
```

## Step 4: Dashboard Design

### 4.1 Executive Dashboard (Page 1)

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  KPI Cards Row                                              │
│  [Total] [Avg Sentiment] [Positive %] [Monthly Growth]      │
├─────────────────────────────────────────────────────────────┤
│  Main Charts Row                                            │
│  [Sentiment Trend Line Chart] [Distribution Donut Chart]    │
├─────────────────────────────────────────────────────────────┤
│  Analysis Row                                               │
│  [Source Performance Bar] [Top Topics Table]               │
└─────────────────────────────────────────────────────────────┘
```

#### KPI Cards Configuration

**Card 1: Total Feedback**
- Visual: Card
- Field: Total Feedback measure
- Format: Add data labels, conditional formatting

**Card 2: Average Sentiment**
- Visual: Gauge
- Value: Average Sentiment measure
- Min: -1, Max: 1, Target: 0.5
- Color coding: Red (-1 to -0.1), Yellow (-0.1 to 0.1), Green (0.1 to 1)

**Card 3: Positive Percentage**
- Visual: Card
- Field: Positive Percentage measure
- Format: Percentage, conditional formatting

**Card 4: Monthly Growth**
- Visual: Card
- Field: Monthly Growth measure
- Format: Percentage with trend arrow

#### Line Chart: Sentiment Trend
- **Visual**: Line Chart
- **Axis**: timestamp (Date Hierarchy → Month)
- **Values**: Average Sentiment
- **Secondary Values**: Total Feedback (show as columns)
- **Formatting**: 
  - X-axis: Month names
  - Y-axis: Sentiment scale (-1 to 1)
  - Data colors: Blue for sentiment, Gray for volume
  - Add average line

#### Donut Chart: Sentiment Distribution
- **Visual**: Donut Chart
- **Legend**: sentiment_label
- **Values**: Count of feedback
- **Colors**: Green (Positive), Red (Negative), Gray (Neutral)
- **Data Labels**: Show percentages

#### Bar Chart: Source Performance
- **Visual**: Clustered Bar Chart
- **Axis**: source
- **Values**: Total Feedback, Average Sentiment
- **Sort**: By Total Feedback (descending)

#### Table: Top Topics
- **Visual**: Table
- **Columns**:
  - topic (from topic_sentiment_summary)
  - mention_count
  - avg_sentiment (formatted as sentiment icon)
  - avg_relevance (formatted as percentage)

### 4.2 Detailed Analysis (Page 2)

#### Scatter Plot: Rating vs Sentiment
- **Visual**: Scatter Chart
- **X-axis**: rating
- **Y-axis**: sentiment_score
- **Size**: confidence_score
- **Color**: sentiment_label
- **Play Axis**: timestamp (for time-based animation)

#### Heat Map: Activity Patterns
- **Visual**: Matrix
- **Rows**: Hour of day
- **Columns**: Day of week
- **Values**: Count of feedback
- **Conditional Formatting**: Color scale (white to blue)

#### Tree Map: Topics by Volume
- **Visual**: Treemap
- **Group**: topic
- **Values**: Count of mentions
- **Color Saturation**: Average sentiment
- **Tooltips**: Add avg_relevance, sample keywords

#### Timeline: Customer Journey
- **Visual**: Line Chart
- **Axis**: timestamp
- **Values**: Cumulative customer count
- **Legend**: Customer lifecycle stage
- **Filters**: Allow customer_id selection

### 4.3 Real-time Monitoring (Page 3)

#### Alert Cards
```dax
Sentiment Alert = 
IF([Average Sentiment] < -0.2, "🔴 Low Sentiment Alert",
   IF([Average Sentiment] > 0.3, "🟢 High Satisfaction", "🟡 Normal"))
```

#### Recent Activity Feed
- **Visual**: Table
- **Columns**: timestamp, customer_id, feedback_text (truncated), sentiment_label, confidence_score
- **Filters**: Last 24 hours
- **Sort**: timestamp (descending)
- **Conditional Formatting**: Row colors by sentiment

## Step 5: Formatting and Styling

### 5.1 Theme Configuration

**Custom Theme JSON:**
```json
{
  "name": "Feedback Analysis Theme",
  "dataColors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
  "background": "#FFFFFF",
  "foreground": "#333333",
  "tableAccent": "#118DFF"
}
```

### 5.2 Consistent Formatting

**Color Scheme:**
- Positive Sentiment: #2ca02c (Green)
- Negative Sentiment: #d62728 (Red)  
- Neutral Sentiment: #7f7f7f (Gray)
- Primary Brand: #1f77b4 (Blue)
- Secondary: #ff7f0e (Orange)

**Typography:**
- Headers: Segoe UI Bold, 14pt
- Body: Segoe UI Regular, 10pt
- KPIs: Segoe UI Bold, 24pt

### 5.3 Interactive Features

**Slicers Configuration:**
- Date Range Slicer: Between style, relative date filtering
- Source Filter: Dropdown style, multi-select enabled
- Rating Filter: Numeric range slider
- Customer Segment: List style with search

**Cross-filtering:**
- Enable cross-filtering between all visuals
- Set bi-directional relationships where appropriate
- Configure drillthrough pages for detailed analysis

## Step 6: Performance Optimization

### 6.1 Data Model Optimization

**DirectQuery vs Import:**
- Use **Import** for better performance (< 1GB data)
- Use **DirectQuery** for real-time requirements (> 1GB data)
- Consider **Composite models** for hybrid approach

**Aggregations:**
```sql
-- Create aggregation tables in SQL Server
CREATE VIEW monthly_aggregations AS
SELECT 
    YEAR(timestamp) as Year,
    MONTH(timestamp) as Month,
    source,
    COUNT(*) as FeedbackCount,
    AVG(CAST(sentiment_score AS FLOAT)) as AvgSentiment
FROM feedback f
JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY YEAR(timestamp), MONTH(timestamp), source;
```

### 6.2 Query Optimization

**Reduce Data Volume:**
- Filter to last 2 years of data
- Remove unused columns
- Use calculated columns instead of measures where appropriate

**Optimize DAX:**
```dax
-- Efficient measure
Optimized Positive Count = 
COUNTROWS(
    FILTER(
        sentiment_analysis,
        sentiment_analysis[sentiment_label] = "Positive"
    )
)

-- Less efficient alternative
Slow Positive Count = 
SUMX(
    sentiment_analysis,
    IF(sentiment_analysis[sentiment_label] = "Positive", 1, 0)
)
```

## Step 7: Publishing and Sharing

### 7.1 Publish to Power BI Service

1. **File** → **Publish** → **Publish to Power BI**
2. Select workspace (or create new)
3. Choose **Replace** if updating existing report

### 7.2 Configure Scheduled Refresh

**In Power BI Service:**
1. Go to **Datasets** tab
2. Find your dataset → **Settings**
3. Expand **Scheduled refresh**
4. Configure data source credentials
5. Set refresh frequency: **Every 2 hours** (recommended)
6. Add notification emails for refresh failures

**Gateway Setup (if on-premises):**
1. Install Power BI Gateway on server with database access
2. Configure data source in gateway settings
3. Map dataset to gateway data source

### 7.3 Security and Access

**Row-Level Security (RLS):**
```dax
-- Create role: "Regional Manager"
[customer_region] = USERNAME()

-- Create role: "Department Head" 
[department] = USERPRINCIPALNAME()
```

**Sharing Options:**
- **App**: Create app for end-user consumption
- **Workspace**: Add users to workspace for collaboration
- **Direct Share**: Share specific reports with individuals
- **Embed**: Embed in internal applications using Power BI Embedded

## Step 8: Mobile Optimization

### 8.1 Mobile Layout

1. Switch to **Mobile Layout** view
2. Resize and rearrange visuals for phone screens
3. Prioritize key metrics (KPI cards first)
4. Use mobile-friendly chart types

### 8.2 Mobile-Specific Features

- **Phone Report**: Create simplified version
- **Touch Interactions**: Enable touch-friendly navigation
- **Offline Viewing**: Configure for offline access

## Step 9: Advanced Features

### 9.1 AI-Powered Insights

**Key Influencers Visual:**
- Analyze what influences positive/negative sentiment
- Identify key factors driving customer satisfaction

**Decomposition Tree:**
- Break down sentiment by multiple dimensions
- Interactive exploration of data hierarchies

### 9.2 Custom Visuals

**Recommended Custom Visuals:**
- **Word Cloud**: For topic visualization
- **Sankey Diagram**: For customer journey flows  
- **Calendar Heatmap**: For temporal pattern analysis
- **Advanced Card**: For enhanced KPI displays

### 9.3 Integration with Other Tools

**Power Automate Integration:**
- Trigger alerts based on sentiment thresholds
- Automate report distribution
- Update external systems based on insights

**Teams Integration:**
- Embed dashboards in Teams channels
- Set up automated report sharing
- Enable collaborative analysis

## Troubleshooting Common Issues

### Connection Issues
```
Error: Unable to connect to data source
Solution: 
1. Verify server name and database name
2. Check firewall settings
3. Confirm ODBC driver installation
4. Test connection with SQL Server Management Studio
```

### Performance Issues
```
Problem: Dashboard loads slowly
Solutions:
1. Reduce data volume with filters
2. Use aggregations instead of detailed data
3. Optimize DAX measures
4. Consider DirectQuery for large datasets
```

### Refresh Failures
```
Error: Scheduled refresh failed
Solutions:
1. Update data source credentials
2. Check gateway connectivity
3. Verify SQL Server permissions
4. Review error logs in Power BI Service
```

## Maintenance and Updates

### Monthly Tasks
- Review dashboard performance metrics
- Update color themes and formatting
- Add new measures based on user feedback
- Optimize slow-running queries

### Quarterly Tasks  
- Assess data model efficiency
- Update security roles and permissions
- Review and update calculated columns
- Plan new dashboard features

This comprehensive setup will give you professional-grade dashboards that provide actionable insights from your customer feedback analysis platform.