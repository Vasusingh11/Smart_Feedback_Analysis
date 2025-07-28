-- Smart Feedback Analysis Platform - Performance Indexes
-- Optimized indexes for faster query performance

USE feedback_analysis;
GO

-- Drop existing indexes if they exist (for clean setup)
-- Note: Primary key indexes are automatically created and managed by SQL Server

-- Feedback table indexes
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_feedback_timestamp_source' AND object_id = OBJECT_ID('feedback'))
    DROP INDEX IX_feedback_timestamp_source ON feedback;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_feedback_customer_timestamp' AND object_id = OBJECT_ID('feedback'))
    DROP INDEX IX_feedback_customer_timestamp ON feedback;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_feedback_category_rating' AND object_id = OBJECT_ID('feedback'))
    DROP INDEX IX_feedback_category_rating ON feedback;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_feedback_source_timestamp' AND object_id = OBJECT_ID('feedback'))
    DROP INDEX IX_feedback_source_timestamp ON feedback;

-- Sentiment analysis table indexes
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sentiment_label_score' AND object_id = OBJECT_ID('sentiment_analysis'))
    DROP INDEX IX_sentiment_label_score ON sentiment_analysis;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sentiment_processed_date' AND object_id = OBJECT_ID('sentiment_analysis'))
    DROP INDEX IX_sentiment_processed_date ON sentiment_analysis;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sentiment_confidence_label' AND object_id = OBJECT_ID('sentiment_analysis'))
    DROP INDEX IX_sentiment_confidence_label ON sentiment_analysis;

-- Topic analysis table indexes
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_topic_topic_relevance' AND object_id = OBJECT_ID('topic_analysis'))
    DROP INDEX IX_topic_topic_relevance ON topic_analysis;

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_topic_feedback_relevance' AND object_id = OBJECT_ID('topic_analysis'))
    DROP INDEX IX_topic_feedback_relevance ON topic_analysis;

PRINT 'Dropped existing custom indexes (if any)';

-- ===== FEEDBACK TABLE INDEXES =====

-- Composite index for time-based queries with source filtering
CREATE NONCLUSTERED INDEX IX_feedback_timestamp_source
ON feedback (timestamp DESC, source)
INCLUDE (feedback_id, customer_id, product_category, rating);

-- Customer-focused index for customer journey analysis
CREATE NONCLUSTERED INDEX IX_feedback_customer_timestamp
ON feedback (customer_id, timestamp DESC)
INCLUDE (source, product_category, rating, feedback_text);

-- Product category analysis with rating
CREATE NONCLUSTERED INDEX IX_feedback_category_rating
ON feedback (product_category, rating, timestamp DESC)
INCLUDE (customer_id, source);

-- Source performance analysis
CREATE NONCLUSTERED INDEX IX_feedback_source_timestamp
ON feedback (source, timestamp DESC)
INCLUDE (product_category, rating, customer_id);

-- Full-text search index for feedback text (if full-text search is needed)
-- CREATE FULLTEXT CATALOG feedback_catalog;
-- CREATE FULLTEXT INDEX ON feedback (feedback_text) KEY INDEX PK_feedback_id ON feedback_catalog;

PRINT 'Created feedback table indexes';

-- ===== SENTIMENT ANALYSIS TABLE INDEXES =====

-- Sentiment distribution and filtering
CREATE NONCLUSTERED INDEX IX_sentiment_label_score
ON sentiment_analysis (sentiment_label, sentiment_score DESC)
INCLUDE (feedback_id, confidence_score, processed_date);

-- Processing monitoring and recent analysis
CREATE NONCLUSTERED INDEX IX_sentiment_processed_date
ON sentiment_analysis (processed_date DESC)
INCLUDE (sentiment_label, sentiment_score, confidence_score);

-- Confidence-based analysis
CREATE NONCLUSTERED INDEX IX_sentiment_confidence_label
ON sentiment_analysis (confidence_score DESC, sentiment_label)
INCLUDE (sentiment_score, feedback_id);

-- Composite index for dashboard queries
CREATE NONCLUSTERED INDEX IX_sentiment_score_processed
ON sentiment_analysis (sentiment_score, processed_date DESC)
INCLUDE (sentiment_label, confidence_score, feedback_id);

PRINT 'Created sentiment analysis table indexes';

-- ===== TOPIC ANALYSIS TABLE INDEXES =====

-- Topic popularity and relevance
CREATE NONCLUSTERED INDEX IX_topic_topic_relevance
ON topic_analysis (topic, relevance_score DESC)
INCLUDE (feedback_id, keyword_list, created_date);

-- Feedback-topic relationship optimization
CREATE NONCLUSTERED INDEX IX_topic_feedback_relevance
ON topic_analysis (feedback_id, relevance_score DESC)
INCLUDE (topic, keyword_list);

-- Topic trending analysis
CREATE NONCLUSTERED INDEX IX_topic_created_topic
ON topic_analysis (created_date DESC, topic)
INCLUDE (relevance_score, feedback_id);

PRINT 'Created topic analysis table indexes';

-- ===== SATISFACTION METRICS TABLE INDEXES =====

-- Time series analysis for satisfaction metrics
CREATE NONCLUSTERED INDEX IX_satisfaction_date_sentiment
ON satisfaction_metrics (date_period DESC)
INCLUDE (avg_sentiment, total_feedback_count, positive_count, negative_count);

PRINT 'Created satisfaction metrics table indexes';

-- ===== COMPOSITE CROSS-TABLE INDEXES =====

-- Note: These are handled by foreign key relationships and joins
-- The existing indexes on feedback_id columns will be used efficiently

-- ===== COLUMNSTORE INDEXES FOR ANALYTICS (Optional) =====
-- For large datasets and analytical workloads
-- Uncomment if you have SQL Server Enterprise Edition and large data volumes

/*
-- Columnstore index for feedback analytics
CREATE NONCLUSTERED COLUMNSTORE INDEX IX_feedback_analytics
ON feedback (customer_id, source, product_category, rating, timestamp);

-- Columnstore index for sentiment analytics  
CREATE NONCLUSTERED COLUMNSTORE INDEX IX_sentiment_analytics
ON sentiment_analysis (sentiment_score, sentiment_label, confidence_score, processed_date);

-- Columnstore index for topic analytics
CREATE NONCLUSTERED COLUMNSTORE INDEX IX_topic_analytics  
ON topic_analysis (topic, relevance_score, created_date);

PRINT 'Created columnstore indexes for analytics';
*/

-- ===== INDEX USAGE MONITORING =====

-- Create a view to monitor index usage
CREATE VIEW index_usage_stats AS
SELECT 
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    i.type_desc AS index_type,
    us.user_seeks,
    us.user_scans,
    us.user_lookups,
    us.user_updates,
    us.last_user_seek,
    us.last_user_scan,
    us.last_user_lookup,
    us.last_user_update,
    -- Calculate usage ratio
    CASE 
        WHEN (us.user_seeks + us.user_scans + us.user_lookups) > 0 
        THEN ROUND(
            (us.user_seeks + us.user_scans + us.user_lookups) * 100.0 / 
            (us.user_seeks + us.user_scans + us.user_lookups + us.user_updates), 2
        )
        ELSE 0 
    END AS read_write_ratio
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats us ON i.object_id = us.object_id AND i.index_id = us.index_id
WHERE OBJECT_NAME(i.object_id) IN ('feedback', 'sentiment_analysis', 'topic_analysis', 'satisfaction_metrics')
AND i.type > 0; -- Exclude heaps
GO

PRINT 'Created index usage monitoring view';

-- ===== MAINTENANCE PROCEDURES =====

-- Procedure to rebuild fragmented indexes
CREATE PROCEDURE sp_RebuildFragmentedIndexes
    @FragmentationThreshold FLOAT = 30.0,
    @RebuildThreshold FLOAT = 50.0
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @TableName SYSNAME;
    DECLARE @IndexName SYSNAME;
    DECLARE @FragmentationPercent FLOAT;
    
    -- Cursor to iterate through fragmented indexes
    DECLARE fragmented_indexes CURSOR FOR
    SELECT 
        OBJECT_NAME(ips.object_id) AS table_name,
        i.name AS index_name,
        ips.avg_fragmentation_in_percent
    FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
    INNER JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
    WHERE ips.avg_fragmentation_in_percent > @FragmentationThreshold
    AND i.name IS NOT NULL
    AND OBJECT_NAME(ips.object_id) IN ('feedback', 'sentiment_analysis', 'topic_analysis', 'satisfaction_metrics');
    
    OPEN fragmented_indexes;
    FETCH NEXT FROM fragmented_indexes INTO @TableName, @IndexName, @FragmentationPercent;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        IF @FragmentationPercent > @RebuildThreshold
        BEGIN
            -- Rebuild heavily fragmented indexes
            SET @SQL = 'ALTER INDEX ' + QUOTENAME(@IndexName) + ' ON ' + QUOTENAME(@TableName) + ' REBUILD WITH (ONLINE = OFF, FILLFACTOR = 90)';
            PRINT 'Rebuilding index: ' + @IndexName + ' on ' + @TableName + ' (Fragmentation: ' + CAST(@FragmentationPercent AS VARCHAR(10)) + '%)';
        END
        ELSE
        BEGIN
            -- Reorganize moderately fragmented indexes
            SET @SQL = 'ALTER INDEX ' + QUOTENAME(@IndexName) + ' ON ' + QUOTENAME(@TableName) + ' REORGANIZE';
            PRINT 'Reorganizing index: ' + @IndexName + ' on ' + @TableName + ' (Fragmentation: ' + CAST(@FragmentationPercent AS VARCHAR(10)) + '%)';
        END
        
        EXEC sp_executesql @SQL;
        
        FETCH NEXT FROM fragmented_indexes INTO @TableName, @IndexName, @FragmentationPercent;
    END
    
    CLOSE fragmented_indexes;
    DEALLOCATE fragmented_indexes;
    
    -- Update statistics after index maintenance
    EXEC sp_updatestats;
    
    PRINT 'Index maintenance completed successfully';
END;
GO

-- Procedure to analyze index usage and suggest optimizations
CREATE PROCEDURE sp_AnalyzeIndexUsage
AS
BEGIN
    SET NOCOUNT ON;
    
    PRINT 'INDEX USAGE ANALYSIS REPORT';
    PRINT '=' + REPLICATE('=', 50);
    
    -- Unused indexes
    PRINT '';
    PRINT 'UNUSED INDEXES (Consider dropping):';
    PRINT '-' + REPLICATE('-', 40);
    
    SELECT 
        table_name,
        index_name,
        index_type
    FROM index_usage_stats
    WHERE (user_seeks + user_scans + user_lookups) = 0
    AND user_updates > 0
    ORDER BY table_name, index_name;
    
    -- Most used indexes
    PRINT '';
    PRINT 'MOST USED INDEXES:';
    PRINT '-' + REPLICATE('-', 20);
    
    SELECT TOP 10
        table_name,
        index_name,
        (user_seeks + user_scans + user_lookups) AS total_reads,
        user_updates,
        read_write_ratio
    FROM index_usage_stats
    WHERE (user_seeks + user_scans + user_lookups) > 0
    ORDER BY (user_seeks + user_scans + user_lookups) DESC;
    
    -- Indexes with poor read/write ratio
    PRINT '';
    PRINT 'INDEXES WITH HIGH UPDATE OVERHEAD:';
    PRINT '-' + REPLICATE('-', 35);
    
    SELECT 
        table_name,
        index_name,
        user_updates,
        (user_seeks + user_scans + user_lookups) AS total_reads,
        read_write_ratio
    FROM index_usage_stats
    WHERE user_updates > (user_seeks + user_scans + user_lookups) * 2
    AND user_updates > 100
    ORDER BY user_updates DESC;
END;
GO

-- ===== PERFORMANCE MONITORING QUERIES =====

-- Create a view for index fragmentation monitoring
CREATE VIEW index_fragmentation_stats AS
SELECT 
    OBJECT_NAME(ips.object_id) AS table_name,
    i.name AS index_name,
    i.type_desc AS index_type,
    ips.index_depth,
    ips.avg_fragmentation_in_percent,
    ips.page_count,
    CASE 
        WHEN ips.avg_fragmentation_in_percent > 50 THEN 'Critical - Rebuild Required'
        WHEN ips.avg_fragmentation_in_percent > 30 THEN 'High - Consider Rebuild'
        WHEN ips.avg_fragmentation_in_percent > 10 THEN 'Moderate - Monitor'
        ELSE 'Good'
    END AS fragmentation_status
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
INNER JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
WHERE i.name IS NOT NULL
AND OBJECT_NAME(ips.object_id) IN ('feedback', 'sentiment_analysis', 'topic_analysis', 'satisfaction_metrics');
GO

PRINT 'Created index fragmentation monitoring view';

-- ===== SUMMARY =====

PRINT '';
PRINT '=' + REPLICATE('=', 60);
PRINT 'INDEX CREATION COMPLETED SUCCESSFULLY';
PRINT '=' + REPLICATE('=', 60);
PRINT 'Created indexes:';
PRINT '✓ Feedback table: 4 performance indexes';
PRINT '✓ Sentiment analysis: 4 performance indexes';  
PRINT '✓ Topic analysis: 3 performance indexes';
PRINT '✓ Satisfaction metrics: 1 performance index';
PRINT '';
PRINT 'Created maintenance objects:';
PRINT '✓ Index usage monitoring view';
PRINT '✓ Index fragmentation monitoring view';
PRINT '✓ sp_RebuildFragmentedIndexes procedure';
PRINT '✓ sp_AnalyzeIndexUsage procedure';
PRINT '';
PRINT 'Usage recommendations:';
PRINT '• Run sp_AnalyzeIndexUsage monthly to monitor performance';
PRINT '• Run sp_RebuildFragmentedIndexes weekly during maintenance';
PRINT '• Monitor index_usage_stats for optimization opportunities';
PRINT '• Check index_fragmentation_stats for maintenance needs';
PRINT '';
PRINT 'Next steps:';
PRINT '1. Load sample data: python scripts/setup_database.py --sample-data';
PRINT '2. Run analysis: python scripts/run_analysis.py run';
PRINT '3. Monitor performance: SELECT * FROM index_usage_stats;';
PRINT '=' + REPLICATE('=', 60);