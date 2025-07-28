-- Smart Feedback Analysis Platform Database Schema
-- SQL Server Implementation

-- Create database (run separately if needed)
-- CREATE DATABASE feedback_analysis;
-- GO

USE feedback_analysis;
GO

-- Drop existing tables if they exist (for clean setup)
IF OBJECT_ID('topic_analysis', 'U') IS NOT NULL DROP TABLE topic_analysis;
IF OBJECT_ID('sentiment_analysis', 'U') IS NOT NULL DROP TABLE sentiment_analysis;
IF OBJECT_ID('satisfaction_metrics', 'U') IS NOT NULL DROP TABLE satisfaction_metrics;
IF OBJECT_ID('feedback', 'U') IS NOT NULL DROP TABLE feedback;
GO

-- Main feedback table
CREATE TABLE feedback (
    feedback_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    feedback_text NVARCHAR(MAX) NOT NULL,
    source VARCHAR(50) NOT NULL, -- email, survey, social_media, website, etc.
    timestamp DATETIME2 NOT NULL DEFAULT GETDATE(),
    product_category VARCHAR(100),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Indexes for performance
    INDEX IX_feedback_timestamp (timestamp),
    INDEX IX_feedback_source (source),
    INDEX IX_feedback_customer_id (customer_id),
    INDEX IX_feedback_created_date (created_date)
);
GO

-- Sentiment analysis results table
CREATE TABLE sentiment_analysis (
    analysis_id INT IDENTITY(1,1) PRIMARY KEY,
    feedback_id INT NOT NULL,
    sentiment_score FLOAT NOT NULL, -- -1 to 1 (negative to positive)
    sentiment_label VARCHAR(20) NOT NULL CHECK (sentiment_label IN ('Positive', 'Negative', 'Neutral')),
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    vader_compound FLOAT, -- VADER specific score
    textblob_polarity FLOAT, -- TextBlob specific score
    subjectivity FLOAT, -- TextBlob subjectivity score
    processed_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Foreign key constraint
    CONSTRAINT FK_sentiment_feedback FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX IX_sentiment_feedback_id (feedback_id),
    INDEX IX_sentiment_label (sentiment_label),
    INDEX IX_sentiment_score (sentiment_score),
    INDEX IX_sentiment_processed_date (processed_date)
);
GO

-- Topic analysis results table
CREATE TABLE topic_analysis (
    topic_id INT IDENTITY(1,1) PRIMARY KEY,
    feedback_id INT NOT NULL,
    topic VARCHAR(200) NOT NULL,
    relevance_score FLOAT NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
    keyword_list VARCHAR(1000),
    created_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Foreign key constraint
    CONSTRAINT FK_topic_feedback FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX IX_topic_feedback_id (feedback_id),
    INDEX IX_topic_name (topic),
    INDEX IX_topic_relevance (relevance_score),
    INDEX IX_topic_created_date (created_date)
);
GO

-- Daily satisfaction metrics table
CREATE TABLE satisfaction_metrics (
    metric_id INT IDENTITY(1,1) PRIMARY KEY,
    date_period DATE NOT NULL,
    avg_sentiment FLOAT NOT NULL,
    total_feedback_count INT NOT NULL,
    positive_count INT NOT NULL,
    negative_count INT NOT NULL,
    neutral_count INT NOT NULL,
    top_topics VARCHAR(1000),
    created_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Unique constraint on date
    CONSTRAINT UK_satisfaction_date UNIQUE (date_period),
    
    -- Indexes
    INDEX IX_satisfaction_date (date_period),
    INDEX IX_satisfaction_sentiment (avg_sentiment)
);
GO

-- Create views for Power BI and reporting
-- Daily sentiment trend view
CREATE VIEW daily_sentiment_trend AS
SELECT 
    CAST(f.timestamp AS DATE) as date,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    COUNT(*) as feedback_count,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    ROUND(AVG(CAST(sa.confidence_score AS FLOAT)) * 100, 2) as avg_confidence_pct,
    COUNT(DISTINCT f.customer_id) as unique_customers
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY CAST(f.timestamp AS DATE);
GO

-- Topic sentiment summary view
CREATE VIEW topic_sentiment_summary AS
SELECT 
    ta.topic,
    COUNT(*) as mention_count,
    AVG(CAST(ta.relevance_score AS FLOAT)) as avg_relevance,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_mentions,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_mentions,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_mentions,
    AVG(CAST(f.rating AS FLOAT)) as avg_rating,
    COUNT(DISTINCT f.customer_id) as unique_customers,
    MIN(f.timestamp) as first_mention,
    MAX(f.timestamp) as last_mention
FROM topic_analysis ta
INNER JOIN sentiment_analysis sa ON ta.feedback_id = sa.feedback_id
INNER JOIN feedback f ON ta.feedback_id = f.feedback_id
GROUP BY ta.topic
HAVING COUNT(*) >= 3; -- Only topics mentioned at least 3 times
GO

-- Source performance view
CREATE VIEW source_performance AS
SELECT 
    f.source,
    COUNT(*) as total_feedback,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    ROUND(
        CAST(SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 
        2
    ) as positive_percentage,
    AVG(CAST(f.rating AS FLOAT)) as avg_rating,
    COUNT(DISTINCT f.customer_id) as unique_customers
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY f.source;
GO

-- Monthly trends view
CREATE VIEW monthly_sentiment_trends AS
SELECT 
    YEAR(f.timestamp) as year,
    MONTH(f.timestamp) as month,
    CONCAT(YEAR(f.timestamp), '-', FORMAT(MONTH(f.timestamp), '00')) as year_month,
    COUNT(*) as feedback_count,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    AVG(CAST(f.rating AS FLOAT)) as avg_rating,
    COUNT(DISTINCT f.customer_id) as unique_customers
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY YEAR(f.timestamp), MONTH(f.timestamp);
GO

-- Customer sentiment profile view
CREATE VIEW customer_sentiment_profile AS
SELECT 
    f.customer_id,
    COUNT(*) as total_feedback,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    AVG(CAST(f.rating AS FLOAT)) as avg_rating,
    MIN(f.timestamp) as first_feedback,
    MAX(f.timestamp) as last_feedback,
    DATEDIFF(day, MIN(f.timestamp), MAX(f.timestamp)) as engagement_days
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY f.customer_id
HAVING COUNT(*) >= 2; -- Customers with at least 2 feedback items
GO

-- Product category analysis view
CREATE VIEW product_category_analysis AS
SELECT 
    ISNULL(f.product_category, 'Uncategorized') as product_category,
    COUNT(*) as feedback_count,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    AVG(CAST(f.rating AS FLOAT)) as avg_rating,
    COUNT(DISTINCT f.customer_id) as unique_customers
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
GROUP BY f.product_category;
GO

-- Recent activity summary view (last 7 days)
CREATE VIEW recent_activity_summary AS
SELECT 
    'Overall' as metric_type,
    COUNT(*) as feedback_count,
    AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
    SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count
FROM feedback f
INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
WHERE f.timestamp >= DATEADD(day, -7, GETDATE());
GO

-- Create stored procedures for common operations

-- Procedure to get unprocessed feedback
CREATE PROCEDURE sp_GetUnprocessedFeedback
    @BatchSize INT = 1000
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TOP (@BatchSize)
        f.feedback_id,
        f.customer_id,
        f.feedback_text,
        f.source,
        f.timestamp,
        f.product_category,
        f.rating,
        f.created_date
    FROM feedback f
    LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE sa.feedback_id IS NULL
    ORDER BY f.created_date ASC;
END;
GO

-- Procedure to update satisfaction metrics
CREATE PROCEDURE sp_UpdateSatisfactionMetrics
    @DatePeriod DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @DatePeriod IS NULL
        SET @DatePeriod = CAST(GETDATE() AS DATE);
    
    MERGE satisfaction_metrics AS target
    USING (
        SELECT 
            @DatePeriod as date_period,
            AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
            COUNT(*) as total_feedback_count,
            SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
            STRING_AGG(ta.topic, ', ') as top_topics
        FROM sentiment_analysis sa
        INNER JOIN feedback f ON sa.feedback_id = f.feedback_id
        LEFT JOIN topic_analysis ta ON f.feedback_id = ta.feedback_id
        WHERE CAST(f.timestamp AS DATE) = @DatePeriod
    ) AS source
    ON target.date_period = source.date_period
    WHEN MATCHED THEN
        UPDATE SET 
            avg_sentiment = source.avg_sentiment,
            total_feedback_count = source.total_feedback_count,
            positive_count = source.positive_count,
            negative_count = source.negative_count,
            neutral_count = source.neutral_count,
            top_topics = source.top_topics
    WHEN NOT MATCHED THEN
        INSERT (date_period, avg_sentiment, total_feedback_count, 
               positive_count, negative_count, neutral_count, top_topics)
        VALUES (source.date_period, source.avg_sentiment, source.total_feedback_count,
               source.positive_count, source.negative_count, source.neutral_count, source.top_topics);
END;
GO

-- Procedure to clean up old data
CREATE PROCEDURE sp_CleanupOldData
    @DaysToKeep INT = 365,
    @RowsDeleted INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CutoffDate DATETIME2 = DATEADD(day, -@DaysToKeep, GETDATE());
    SET @RowsDeleted = 0;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Delete old topic analysis records
        DELETE FROM topic_analysis 
        WHERE feedback_id IN (
            SELECT feedback_id FROM feedback 
            WHERE timestamp < @CutoffDate
        );
        SET @RowsDeleted = @RowsDeleted + @@ROWCOUNT;
        
        -- Delete old sentiment analysis records
        DELETE FROM sentiment_analysis 
        WHERE feedback_id IN (
            SELECT feedback_id FROM feedback 
            WHERE timestamp < @CutoffDate
        );
        SET @RowsDeleted = @RowsDeleted + @@ROWCOUNT;
        
        -- Delete old feedback records
        DELETE FROM feedback 
        WHERE timestamp < @CutoffDate;
        SET @RowsDeleted = @RowsDeleted + @@ROWCOUNT;
        
        -- Delete old satisfaction metrics (keep more history for metrics)
        DELETE FROM satisfaction_metrics 
        WHERE date_period < DATEADD(day, -(@DaysToKeep * 2), GETDATE());
        SET @RowsDeleted = @RowsDeleted + @@ROWCOUNT;
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Create function to calculate sentiment trend
CREATE FUNCTION fn_GetSentimentTrend(@Days INT = 7)
RETURNS TABLE
AS
RETURN
(
    SELECT 
        CAST(f.timestamp AS DATE) as date,
        AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
        COUNT(*) as feedback_count,
        LAG(AVG(CAST(sa.sentiment_score AS FLOAT))) OVER (ORDER BY CAST(f.timestamp AS DATE)) as prev_sentiment,
        AVG(CAST(sa.sentiment_score AS FLOAT)) - 
        LAG(AVG(CAST(sa.sentiment_score AS FLOAT))) OVER (ORDER BY CAST(f.timestamp AS DATE)) as sentiment_change
    FROM feedback f
    INNER JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
    WHERE f.timestamp >= DATEADD(day, -@Days, GETDATE())
    GROUP BY CAST(f.timestamp AS DATE)
);
GO

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON feedback TO [feedback_app_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sentiment_analysis TO [feedback_app_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON topic_analysis TO [feedback_app_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON satisfaction_metrics TO [feedback_app_user];
-- GRANT SELECT ON daily_sentiment_trend TO [feedback_app_user];
-- GRANT SELECT ON topic_sentiment_summary TO [feedback_app_user];
-- GRANT EXECUTE ON sp_GetUnprocessedFeedback TO [feedback_app_user];
-- GRANT EXECUTE ON sp_UpdateSatisfactionMetrics TO [feedback_app_user];

PRINT 'Database schema created successfully!';
PRINT 'Tables created: feedback, sentiment_analysis, topic_analysis, satisfaction_metrics';
PRINT 'Views created: daily_sentiment_trend, topic_sentiment_summary, source_performance, monthly_sentiment_trends, customer_sentiment_profile, product_category_analysis, recent_activity_summary';
PRINT 'Procedures created: sp_GetUnprocessedFeedback, sp_UpdateSatisfactionMetrics, sp_CleanupOldData';
PRINT 'Functions created: fn_GetSentimentTrend';