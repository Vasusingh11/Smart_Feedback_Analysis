"""
Database Connection and Operations Module
Handles all database interactions for the feedback analysis platform
"""

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pyodbc
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from contextlib import contextmanager

class DatabaseHandler:
    """
    Handles database connections and operations for feedback analysis
    Supports SQL Server with connection pooling and error handling
    """
    
    def __init__(self, connection_string: str = None, config: Dict[str, Any] = None):
        """
        Initialize database handler
        
        Args:
            connection_string (str): Direct connection string
            config (dict): Database configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        
        if connection_string:
            self.connection_string = connection_string
        elif config:
            self.connection_string = self._build_connection_string(config)
        else:
            raise ValueError("Either connection_string or config must be provided")
        
        self.engine = None
        self._connect()
    
    def _build_connection_string(self, config: Dict[str, Any]) -> str:
        """Build connection string from config dictionary"""
        driver = config.get('driver', 'ODBC Driver 17 for SQL Server')
        server = config['server']
        database = config['database']
        username = config.get('username')
        password = config.get('password')
        
        if username and password:
            # SQL Server authentication
            conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"
        else:
            # Windows authentication
            conn_str = f"mssql+pyodbc://@{server}/{database}?driver={driver.replace(' ', '+')}&trusted_connection=yes"
        
        return conn_str
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Execute SELECT query and return results as DataFrame
        
        Args:
            query (str): SQL query to execute
            params (dict): Query parameters
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            with self.get_connection() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
                
                self.logger.info(f"Query executed successfully, returned {len(result)} rows")
                return result
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_non_query(self, query: str, params: Dict[str, Any] = None) -> int:
        """
        Execute INSERT, UPDATE, DELETE query
        
        Args:
            query (str): SQL query to execute
            params (dict): Query parameters
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                conn.commit()
                affected_rows = result.rowcount
                
                self.logger.info(f"Non-query executed successfully, {affected_rows} rows affected")
                return affected_rows
                
        except Exception as e:
            self.logger.error(f"Non-query execution failed: {e}")
            raise
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, 
                        if_exists: str = 'append', chunk_size: int = 1000) -> bool:
        """
        Insert DataFrame into database table
        
        Args:
            df (pd.DataFrame): Data to insert
            table_name (str): Target table name
            if_exists (str): What to do if table exists ('append', 'replace', 'fail')
            chunk_size (int): Number of rows to insert at once
            
        Returns:
            bool: Success status
        """
        try:
            # Clean column names (remove special characters)
            df_clean = df.copy()
            df_clean.columns = [col.replace(' ', '_').replace('-', '_').replace('.', '_') 
                               for col in df_clean.columns]
            
            # Insert data in chunks
            for i in range(0, len(df_clean), chunk_size):
                chunk = df_clean.iloc[i:i + chunk_size]
                chunk.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists=if_exists if i == 0 else 'append',
                    index=False,
                    method='multi'
                )
                
                self.logger.info(f"Inserted chunk {i//chunk_size + 1}/{(len(df_clean)-1)//chunk_size + 1} "
                               f"into {table_name}")
            
            self.logger.info(f"Successfully inserted {len(df_clean)} rows into {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"DataFrame insertion failed: {e}")
            return False
    
    # Feedback-specific database operations
    
    def get_unprocessed_feedback(self, limit: int = 1000) -> pd.DataFrame:
        """Get feedback that hasn't been processed for sentiment analysis"""
        query = """
        SELECT TOP (:limit) 
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
        ORDER BY f.created_date ASC
        """
        
        return self.execute_query(query, {'limit': limit})
    
    def save_sentiment_results(self, results_df: pd.DataFrame) -> bool:
        """Save sentiment analysis results to database"""
        if results_df.empty:
            self.logger.warning("No sentiment results to save")
            return True
        
        # Ensure required columns exist
        required_columns = ['feedback_id', 'sentiment_score', 'sentiment_label', 
                           'confidence_score', 'processed_date']
        
        missing_columns = [col for col in required_columns if col not in results_df.columns]
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        return self.insert_dataframe(results_df, 'sentiment_analysis')
    
    def save_topic_results(self, results_df: pd.DataFrame) -> bool:
        """Save topic analysis results to database"""
        if results_df.empty:
            self.logger.warning("No topic results to save")
            return True
        
        required_columns = ['feedback_id', 'topic', 'relevance_score', 'keyword_list']
        missing_columns = [col for col in required_columns if col not in results_df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        return self.insert_dataframe(results_df, 'topic_analysis')
    
    def update_satisfaction_metrics(self, date_period: datetime = None) -> bool:
        """Update daily satisfaction metrics"""
        if not date_period:
            date_period = datetime.now().date()
        
        query = """
        MERGE satisfaction_metrics AS target
        USING (
            SELECT 
                :date_period as date_period,
                AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
                COUNT(*) as total_feedback_count,
                SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
                STRING_AGG(ta.topic, ', ') as top_topics
            FROM sentiment_analysis sa
            JOIN feedback f ON sa.feedback_id = f.feedback_id
            LEFT JOIN topic_analysis ta ON f.feedback_id = ta.feedback_id
            WHERE CAST(f.timestamp AS DATE) = :date_period
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
        """
        
        try:
            affected_rows = self.execute_non_query(query, {'date_period': date_period})
            self.logger.info(f"Updated satisfaction metrics for {date_period}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update satisfaction metrics: {e}")
            return False
    
    def get_sentiment_trends(self, days: int = 30) -> pd.DataFrame:
        """Get sentiment trends for the last N days"""
        query = """
        SELECT 
            CAST(f.timestamp AS DATE) as date,
            AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
            COUNT(*) as feedback_count,
            SUM(CASE WHEN sa.sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN sa.sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN sa.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count
        FROM feedback f
        JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE f.timestamp >= DATEADD(day, -:days, GETDATE())
        GROUP BY CAST(f.timestamp AS DATE)
        ORDER BY date
        """
        
        return self.execute_query(query, {'days': days})
    
    def get_topic_summary(self, days: int = 30) -> pd.DataFrame:
        """Get topic analysis summary for the last N days"""
        query = """
        SELECT 
            ta.topic,
            COUNT(*) as mention_count,
            AVG(CAST(ta.relevance_score AS FLOAT)) as avg_relevance,
            AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment,
            COUNT(DISTINCT f.customer_id) as unique_customers
        FROM topic_analysis ta
        JOIN feedback f ON ta.feedback_id = f.feedback_id
        JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE f.timestamp >= DATEADD(day, -:days, GETDATE())
        GROUP BY ta.topic
        HAVING COUNT(*) >= 3  -- Only topics mentioned at least 3 times
        ORDER BY mention_count DESC
        """
        
        return self.execute_query(query, {'days': days})
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for dashboard"""
        dashboard_data = {}
        
        try:
            # Overall metrics
            overall_query = """
            SELECT 
                COUNT(*) as total_feedback,
                AVG(CAST(sentiment_score AS FLOAT)) as avg_sentiment,
                SUM(CASE WHEN sentiment_label = 'Positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment_label = 'Negative' THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN sentiment_label = 'Neutral' THEN 1 ELSE 0 END) as neutral_count
            FROM sentiment_analysis sa
            JOIN feedback f ON sa.feedback_id = f.feedback_id
            WHERE f.timestamp >= DATEADD(day, -30, GETDATE())
            """
            
            dashboard_data['overall_metrics'] = self.execute_query(overall_query).to_dict('records')[0]
            
            # Sentiment trends
            dashboard_data['sentiment_trends'] = self.get_sentiment_trends(30)
            
            # Topic summary
            dashboard_data['topic_summary'] = self.get_topic_summary(30)
            
            # Source breakdown
            source_query = """
            SELECT 
                f.source,
                COUNT(*) as feedback_count,
                AVG(CAST(sa.sentiment_score AS FLOAT)) as avg_sentiment
            FROM feedback f
            JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
            WHERE f.timestamp >= DATEADD(day, -30, GETDATE())
            GROUP BY f.source
            ORDER BY feedback_count DESC
            """
            
            dashboard_data['source_breakdown'] = self.execute_query(source_query)
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            dashboard_data = {'error': str(e)}
        
        return dashboard_data
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """Clean up old data to maintain performance"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        queries = [
            "DELETE FROM topic_analysis WHERE feedback_id IN (SELECT feedback_id FROM feedback WHERE timestamp < :cutoff_date)",
            "DELETE FROM sentiment_analysis WHERE feedback_id IN (SELECT feedback_id FROM feedback WHERE timestamp < :cutoff_date)",
            "DELETE FROM feedback WHERE timestamp < :cutoff_date"
        ]
        
        try:
            total_deleted = 0
            for query in queries:
                affected = self.execute_non_query(query, {'cutoff_date': cutoff_date})
                total_deleted += affected
            
            self.logger.info(f"Cleaned up {total_deleted} old records")
            return True
            
        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        health_status = {
            'connection': False,
            'tables_exist': False,
            'recent_data': False,
            'errors': []
        }
        
        try:
            # Test connection
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
            health_status['connection'] = True
            
            # Check if tables exist
            tables_query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('feedback', 'sentiment_analysis', 'topic_analysis', 'satisfaction_metrics')
            """
            tables = self.execute_query(tables_query)
            health_status['tables_exist'] = len(tables) == 4
            
            # Check for recent data
            recent_query = """
            SELECT COUNT(*) as recent_count
            FROM feedback 
            WHERE timestamp >= DATEADD(day, -7, GETDATE())
            """
            recent_data = self.execute_query(recent_query)
            health_status['recent_data'] = recent_data.iloc[0]['recent_count'] > 0
            
        except Exception as e:
            health_status['errors'].append(str(e))
        
        return health_status

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Example configuration
    config = {
        'server': 'localhost',
        'database': 'feedback_analysis',
        'username': 'sa',
        'password': 'your_password',
        'driver': 'ODBC Driver 17 for SQL Server'
    }
    
    try:
        # Initialize database handler
        db = DatabaseHandler(config=config)
        
        # Perform health check
        health = db.health_check()
        print("Database Health Check:")
        for key, value in health.items():
            print(f"  {key}: {value}")
        
        # Get unprocessed feedback
        unprocessed = db.get_unprocessed_feedback(limit=10)
        print(f"\nUnprocessed feedback count: {len(unprocessed)}")
        
        # Get sentiment trends
        trends = db.get_sentiment_trends(days=7)
        print(f"\nSentiment trends (last 7 days): {len(trends)} records")
        
    except Exception as e:
        print(f"Database test failed: {e}")