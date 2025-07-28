-- Smart Feedback Analysis Platform - Additional Views
-- Advanced views for reporting and analytics

USE feedback_analysis;
GO

-- Advanced sentiment analysis view with rolling averages
CREATE VIEW sentiment_trends_advanced AS
WITH DailySentiment AS (
    SELECT 
        CAST(f.timestamp AS DATE) as date,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as daily_sentiment,
        COUNT(*) as daily_count,
        AVG(CAST(sa.confidence_score AS FLOAT)) as daily_confidence
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    GROUP BY CAST(f.timestamp AS DATE)
)
SELECT 
    date,
    daily_sentiment,
    daily_count,
    daily_confidence,
    -- 7-day rolling average
    AVG(daily_sentiment) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as sentiment_7day_avg,
    -- 30-day rolling average
    AVG(daily_sentiment) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as sentiment_30day_avg,
    -- Day-over-day change
    daily_sentiment - LAG(daily_sentiment) OVER (ORDER BY date) as sentiment_change,
    -- Volume trend
    daily_count - LAG(daily_count) OVER (ORDER BY date) as volume_change
FROM DailySentiment;
GO

-- Customer journey and lifecycle view
CREATE VIEW customer_journey AS
WITH CustomerMetrics AS (
    SELECT 
        f.customer_id,
        COUNT(*) as total_feedback,
        MIN(f.timestamp) as first_feedback_date,
        MAX(f.timestamp) as last_feedback_date,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
        AVG(CAST(f.rating AS FLOAT)) as avg_rating,
        COUNT(DISTINCT f.source) as sources_used,
        COUNT(DISTINCT f.product_category) as categories_engaged,
        DATEDIFF(day, MIN(f.timestamp), MAX(f.timestamp)) as engagement_days
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    GROUP BY f.customer_id
)
SELECT 
    customer_id,
    total_feedback,
    first_feedback_date,
    last_feedback_date,
    avg_sentiment,
    avg_rating,
    sources_used,
    categories_engaged,
    engagement_days,
    -- Customer lifecycle stage
    CASE 
        WHEN total_feedback = 1 THEN 'New Customer'
        WHEN total_feedback BETWEEN 2 AND 5 THEN 'Engaged Customer'
        WHEN total_feedback > 5 THEN 'Loyal Customer'
    END as lifecycle_stage,
    -- Customer sentiment category
    CASE 
        WHEN avg_sentiment > 0.3 THEN 'Advocate'
        WHEN avg_sentiment BETWEEN -0.1 AND 0.3 THEN 'Neutral'
        WHEN avg_sentiment < -0.1 THEN 'Detractor'
    END as sentiment_category,
    -- Recency (days since last feedback)
    DATEDIFF(day, last_feedback_date, GETDATE()) as days_since_last_feedback,
    -- Customer value score (simple)
    (total_feedback * 0.4) + (avg_sentiment * 50) + (avg_rating * 10) as customer_value_score
FROM CustomerMetrics;
GO

-- Topic evolution and trending view
CREATE VIEW topic_evolution AS
WITH TopicsByMonth AS (
    SELECT 
        ta.topic,
        YEAR(f.timestamp) as year,
        MONTH(f.timestamp) as month,
        COUNT(*) as monthly_mentions,
        AVG(CAST(ta.relevance_score AS FLOAT)) as avg_relevance,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment
    FROM topic_analysis ta
    INNER JOIN feedback f ON ta.feedback_id = f.feedback_id
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    GROUP BY ta.topic, YEAR(f.timestamp), MONTH(f.timestamp)
)
SELECT 
    topic,
    year,
    month,
    CONCAT(year, '-', FORMAT(month, '00')) as year_month,
    monthly_mentions,
    avg_relevance,
    avg_sentiment,
    -- Month-over-month change
    monthly_mentions - LAG(monthly_mentions) OVER (
        PARTITION BY topic 
        ORDER BY year, month
    ) as mentions_change,
    -- Sentiment trend
    avg_sentiment - LAG(avg_sentiment) OVER (
        PARTITION BY topic 
        ORDER BY year, month
    ) as sentiment_change,
    -- Topic trending score
    CASE 
        WHEN monthly_mentions > LAG(monthly_mentions) OVER (
            PARTITION BY topic ORDER BY year, month
        ) THEN 'Trending Up'
        WHEN monthly_mentions < LAG(monthly_mentions) OVER (
            PARTITION BY topic ORDER BY year, month
        ) THEN 'Trending Down'
        ELSE 'Stable'
    END as trend_direction
FROM TopicsByMonth;
GO

-- Comprehensive feedback dashboard view
CREATE VIEW feedback_dashboard AS
WITH RecentMetrics AS (
    SELECT 
        COUNT(*) as total_feedback,
        COUNT(DISTINCT f.customer_id) as unique_customers,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
        SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
        SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
        SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
        AVG(CAST(f.rating AS FLOAT)) as avg_rating,
        AVG(CAST(sa.confidence_score AS FLOAT)) as avg_confidence
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(day, -30, GETDATE())
),
PreviousMetrics AS (
    SELECT 
        COUNT(*) as prev_total_feedback,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as prev_avg_sentiment,
        AVG(CAST(f.rating AS FLOAT)) as prev_avg_rating
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(day, -60, GETDATE()) 
    AND f.timestamp < DATEADD(day, -30, GETDATE())
),
TopTopics AS (
    SELECT TOP 5
        ta.topic,
        COUNT(*) as mention_count,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as topic_sentiment
    FROM topic_analysis ta
    INNER JOIN feedback f ON ta.feedback_id = f.feedback_id
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(day, -30, GETDATE())
    GROUP BY ta.topic
    ORDER BY COUNT(*) DESC
)
SELECT 
    -- Current metrics
    rm.total_feedback,
    rm.unique_customers,
    rm.avg_sentiment,
    rm.positive_count,
    rm.negative_count,
    rm.neutral_count,
    rm.avg_rating,
    rm.avg_confidence,
    
    -- Percentage distributions
    ROUND((CAST(rm.positive_count AS FLOAT) / rm.total_feedback) * 100, 2) as positive_percentage,
    ROUND((CAST(rm.negative_count AS FLOAT) / rm.total_feedback) * 100, 2) as negative_percentage,
    ROUND((CAST(rm.neutral_count AS FLOAT) / rm.total_feedback) * 100, 2) as neutral_percentage,
    
    -- Period-over-period changes
    rm.total_feedback - pm.prev_total_feedback as feedback_change,
    rm.avg_sentiment - pm.prev_avg_sentiment as sentiment_change,
    rm.avg_rating - pm.prev_avg_rating as rating_change,
    
    -- Growth rates
    CASE 
        WHEN pm.prev_total_feedback > 0 
        THEN ROUND(((CAST(rm.total_feedback AS FLOAT) - pm.prev_total_feedback) / pm.prev_total_feedback) * 100, 2)
        ELSE NULL 
    END as feedback_growth_rate,
    
    -- Top topics (concatenated)
    STRING_AGG(CONCAT(tt.topic, ' (', tt.mention_count, ')'), ', ') as top_topics,
    
    -- Data freshness
    (SELECT MAX(timestamp) FROM feedback) as latest_feedback_time,
    (SELECT MAX(processed_date) FROM sentiment_analysis) as latest_processing_time,
    
    -- Quality indicators
    ROUND((CAST(rm.total_feedback AS FLOAT) / (SELECT COUNT(*) FROM feedback WHERE timestamp >= DATEADD(day, -30, GETDATE()))) * 100, 2) as processing_completeness
    
FROM RecentMetrics rm
CROSS JOIN PreviousMetrics pm
CROSS JOIN TopTopics tt
GROUP BY 
    rm.total_feedback, rm.unique_customers, rm.avg_sentiment,
    rm.positive_count, rm.negative_count, rm.neutral_count,
    rm.avg_rating, rm.avg_confidence,
    pm.prev_total_feedback, pm.prev_avg_sentiment, pm.prev_avg_rating;
GO

-- Alert conditions view
CREATE VIEW feedback_alerts AS
WITH AlertConditions AS (
    SELECT 
        'Sentiment Alert' as alert_type,
        CASE 
            WHEN AVG(CAST(sa.sentiment_score AS FLOAT)) < -0.3 THEN 'CRITICAL'
            WHEN AVG(CAST(sa.sentiment_score AS FLOAT)) < -0.1 THEN 'WARNING'
            ELSE 'NORMAL'
        END as alert_level,
        CONCAT('Average sentiment: ', ROUND(AVG(CAST(sa.sentiment_score AS FLOAT)), 3)) as alert_message,
        COUNT(*) as affected_items
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(day, -1, GETDATE())
    
    UNION ALL
    
    SELECT 
        'Volume Alert' as alert_type,
        CASE 
            WHEN COUNT(*) > (
                SELECT AVG(daily_count) * 2 
                FROM (
                    SELECT COUNT(*) as daily_count
                    FROM feedback 
                    WHERE timestamp >= DATEADD(day, -7, GETDATE())
                    GROUP BY CAST(timestamp AS DATE)
                ) prev_days
            ) THEN 'WARNING'
            WHEN COUNT(*) < (
                SELECT AVG(daily_count) * 0.5 
                FROM (
                    SELECT COUNT(*) as daily_count
                    FROM feedback 
                    WHERE timestamp >= DATEADD(day, -7, GETDATE())
                    GROUP BY CAST(timestamp AS DATE)
                ) prev_days
            ) THEN 'WARNING'
            ELSE 'NORMAL'
        END as alert_level,
        CONCAT('Daily volume: ', COUNT(*), ' items') as alert_message,
        COUNT(*) as affected_items
    FROM feedback f
    WHERE f.timestamp >= DATEADD(day, -1, GETDATE())
    
    UNION ALL
    
    SELECT 
        'Processing Delay Alert' as alert_type,
        CASE 
            WHEN COUNT(f.feedback_id) > 0 THEN 'WARNING'
            ELSE 'NORMAL'
        END as alert_level,
        CONCAT(COUNT(f.feedback_id), ' unprocessed feedback items') as alert_message,
        COUNT(f.feedback_id) as affected_items
    FROM feedback f
    LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(hour, -6, GETDATE())
    AND sa.feedback_id IS NULL
    
    UNION ALL
    
    SELECT 
        'Negative Feedback Spike' as alert_type,
        CASE 
            WHEN negative_pct > 40 THEN 'CRITICAL'
            WHEN negative_pct > 25 THEN 'WARNING'
            ELSE 'NORMAL'
        END as alert_level,
        CONCAT('Negative feedback: ', negative_pct, '%') as alert_message,
        total_feedback as affected_items
    FROM (
        SELECT 
            COUNT(*) as total_feedback,
            ROUND((SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 1) as negative_pct
        FROM feedback f
        INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE f.timestamp >= DATEADD(day, -1, GETDATE())
    ) sub
)
SELECT 
    alert_type,
    alert_level,
    alert_message,
    affected_items,
    GETDATE() as check_time
FROM AlertConditions
WHERE alert_level != 'NORMAL';
GO

-- Performance monitoring view
CREATE VIEW system_performance AS
SELECT 
    'Database Performance' as metric_category,
    'Total Records' as metric_name,
    CAST(COUNT(*) AS VARCHAR(50)) as metric_value,
    'records' as metric_unit,
    GETDATE() as measurement_time
FROM feedback

UNION ALL

SELECT 
    'Processing Performance' as metric_category,
    'Processing Rate' as metric_name,
    CAST(ROUND(
        (CAST(COUNT(sa.feedback_id) AS FLOAT) / COUNT(f.feedback_id)) * 100, 2
    ) AS VARCHAR(50)) as metric_value,
    'percentage' as metric_unit,
    GETDATE() as measurement_time
FROM feedback f
LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
WHERE f.timestamp >= DATEADD(day, -7, GETDATE())

UNION ALL

SELECT 
    'Data Quality' as metric_category,
    'Average Confidence' as metric_name,
    CAST(ROUND(AVG(CAST(confidence_score AS FLOAT)), 3) AS VARCHAR(50)) as metric_value,
    'score' as metric_unit,
    GETDATE() as measurement_time
FROM sentiment_analysis
WHERE processed_date >= DATEADD(day, -7, GETDATE())

UNION ALL

SELECT 
    'Business Impact' as metric_category,
    'Customer Satisfaction' as metric_name,
    CAST(ROUND(AVG(CAST(sentiment_score AS FLOAT)), 3) AS VARCHAR(50)) as metric_value,
    'sentiment_score' as metric_unit,
    GETDATE() as measurement_time
FROM sentiment_analysis sa
INNER JOIN feedback f ON sa.feedback_id = f.feedback_id
WHERE f.timestamp >= DATEADD(day, -30, GETDATE());
GO

-- Export-ready summary view for Power BI
CREATE VIEW powerbi_export_summary AS
SELECT 
    -- Date dimension
    CAST(f.timestamp AS DATE) as feedback_date,
    YEAR(f.timestamp) as feedback_year,
    MONTH(f.timestamp) as feedback_month,
    DATEPART(week, f.timestamp) as feedback_week,
    DATEPART(weekday, f.timestamp) as feedback_weekday,
    
    -- Feedback details
    f.feedback_id,
    f.customer_id,
    f.source,
    f.product_category,
    f.rating,
    
    -- Sentiment analysis
    sa.sentiment_score,
    sa.sentiment_label,
    sa.confidence_score,
    
    -- Topic analysis (primary topic only)
    (SELECT TOP 1 ta.topic 
     FROM topic_analysis ta 
     WHERE ta.feedback_id = f.feedback_id 
     ORDER BY ta.relevance_score DESC) as primary_topic,
    (SELECT TOP 1 ta.relevance_score 
     FROM topic_analysis ta 
     WHERE ta.feedback_id = f.feedback_id 
     ORDER BY ta.relevance_score DESC) as primary_topic_relevance,
    
    -- Calculated fields
    CASE 
        WHEN sa.sentiment_score > 0.1 THEN 1 ELSE 0 
    END as is_positive,
    CASE 
        WHEN sa.sentiment_score < -0.1 THEN 1 ELSE 0 
    END as is_negative,
    CASE 
        WHEN f.rating >= 4 THEN 1 ELSE 0 
    END as is_high_rating,
    CASE 
        WHEN f.rating <= 2 THEN 1 ELSE 0 
    END as is_low_rating,
    
    -- Customer segments
    CASE 
        WHEN (SELECT COUNT(*) FROM feedback f2 WHERE f2.customer_id = f.customer_id) = 1 
        THEN 'New Customer'
        WHEN (SELECT COUNT(*) FROM feedback f2 WHERE f2.customer_id = f.customer_id) BETWEEN 2 AND 5 
        THEN 'Regular Customer'
        ELSE 'Loyal Customer'
    END as customer_segment
    
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
WHERE f.timestamp >= DATEADD(year, -2, GETDATE()); -- Last 2 years for performance
GO

PRINT 'Advanced views created successfully!';
PRINT 'Views created: sentiment_trends_advanced, customer_journey, topic_evolution, feedback_dashboard, feedback_alerts, system_performance, powerbi_export_summary';