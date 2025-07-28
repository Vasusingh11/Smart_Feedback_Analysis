"""
Main Processing Pipeline
Orchestrates the complete feedback analysis workflow
"""

import pandas as pd
import numpy as np
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yaml
import traceback

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_processing.sentiment_analyzer import SentimentAnalyzer
from src.data_processing.topic_extractor import TopicExtractor
from src.database.connection import DatabaseHandler
from src.utils.logger import setup_logger
from src.utils.helpers import validate_config, send_notification

class FeedbackAnalysisPipeline:
    """
    Main pipeline for processing customer feedback
    Coordinates sentiment analysis, topic extraction, and database operations
    """
    
    def __init__(self, config_path: str = None, config_dict: Dict[str, Any] = None):
        """
        Initialize the feedback analysis pipeline
        
        Args:
            config_path (str): Path to configuration file
            config_dict (dict): Configuration dictionary
        """
        # Load configuration
        if config_path:
            self.config = self._load_config(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("Either config_path or config_dict must be provided")
        
        # Validate configuration
        validate_config(self.config)
        
        # Setup logging
        self.logger = setup_logger(
            name='feedback_pipeline',
            level=self.config.get('logging', {}).get('level', 'INFO'),
            log_file=self.config.get('logging', {}).get('file', 'pipeline.log')
        )
        
        # Initialize components
        self.db_handler = None
        self.sentiment_analyzer = None
        self.topic_extractor = None
        
        # Pipeline statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'feedback_processed': 0,
            'sentiment_analyzed': 0,
            'topics_extracted': 0,
            'errors': 0,
            'success_rate': 0.0
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            self.logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # Initialize database handler
            self.logger.info("Initializing database connection...")
            self.db_handler = DatabaseHandler(config=self.config['database'])
            
            # Initialize sentiment analyzer
            self.logger.info("Initializing sentiment analyzer...")
            self.sentiment_analyzer = SentimentAnalyzer()
            
            # Initialize topic extractor
            self.logger.info("Initializing topic extractor...")
            topic_config = self.config.get('topic_extraction', {})
            self.topic_extractor = TopicExtractor(
                max_features=topic_config.get('max_features', 100),
                min_df=topic_config.get('min_df', 2),
                ngram_range=tuple(topic_config.get('ngram_range', [1, 2]))
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            raise
    
    def run_sentiment_analysis(self, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """
        Run sentiment analysis on feedback data
        
        Args:
            feedback_df (pd.DataFrame): Feedback data to analyze
            
        Returns:
            pd.DataFrame: Sentiment analysis results
        """
        if feedback_df.empty:
            self.logger.info("No feedback data to analyze")
            return pd.DataFrame()
        
        try:
            self.logger.info(f"Starting sentiment analysis for {len(feedback_df)} feedback items")
            
            # Extract text data
            texts = feedback_df['feedback_text'].fillna('').tolist()
            
            # Run batch sentiment analysis
            sentiment_config = self.config.get('sentiment_analysis', {})
            batch_size = sentiment_config.get('batch_size', 1000)
            
            sentiment_results = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_feedback_ids = feedback_df.iloc[i:i + batch_size]['feedback_id'].tolist()
                
                self.logger.info(f"Processing sentiment batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
                for j, text in enumerate(batch_texts):
                    try:
                        sentiment = self.sentiment_analyzer.analyze_sentiment(
                            text,
                            vader_weight=sentiment_config.get('vader_weight', 0.6),
                            textblob_weight=sentiment_config.get('textblob_weight', 0.4)
                        )
                        
                        sentiment_results.append({
                            'feedback_id': batch_feedback_ids[j],
                            'sentiment_score': sentiment['score'],
                            'sentiment_label': sentiment['label'],
                            'confidence_score': sentiment['confidence'],
                            'vader_compound': sentiment['vader_compound'],
                            'textblob_polarity': sentiment['textblob_polarity'],
                            'subjectivity': sentiment['subjectivity'],
                            'processed_date': datetime.now()
                        })
                        
                    except Exception as e:
                        self.logger.error(f"Sentiment analysis failed for feedback {batch_feedback_ids[j]}: {e}")
                        self.stats['errors'] += 1
            
            results_df = pd.DataFrame(sentiment_results)
            self.stats['sentiment_analyzed'] = len(results_df)
            
            self.logger.info(f"Sentiment analysis completed for {len(results_df)} items")
            return results_df
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis batch failed: {e}")
            self.stats['errors'] += 1
            return pd.DataFrame()
    
    def run_topic_extraction(self, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """
        Run topic extraction on feedback data
        
        Args:
            feedback_df (pd.DataFrame): Feedback data to analyze
            
        Returns:
            pd.DataFrame: Topic analysis results
        """
        if feedback_df.empty:
            self.logger.info("No feedback data for topic extraction")
            return pd.DataFrame()
        
        try:
            self.logger.info(f"Starting topic extraction for {len(feedback_df)} feedback items")
            
            # Extract text data
            texts = feedback_df['feedback_text'].fillna('').tolist()
            
            # Get topic extraction configuration
            topic_config = self.config.get('topic_extraction', {})
            n_topics = topic_config.get('n_topics', 10)
            
            # Extract topics using K-means
            topics = self.topic_extractor.extract_topics_kmeans(texts, n_topics=n_topics)
            
            if not topics:
                self.logger.warning("No topics extracted")
                return pd.DataFrame()
            
            # Assign topics to documents
            document_topics = self.topic_extractor.assign_topics_to_documents(texts, topics)
            
            # Create results DataFrame
            topic_results = []
            for doc_topic in document_topics:
                feedback_id = feedback_df.iloc[doc_topic['document_id']]['feedback_id']
                
                topic_results.append({
                    'feedback_id': feedback_id,
                    'topic': doc_topic['topic_name'],
                    'relevance_score': doc_topic['relevance_score'],
                    'keyword_list': ', '.join(doc_topic['keywords_found'])
                })
            
            results_df = pd.DataFrame(topic_results)
            self.stats['topics_extracted'] = len(results_df)
            
            self.logger.info(f"Topic extraction completed, {len(topics)} topics found, "
                           f"{len(results_df)} topic assignments created")
            
            return results_df
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            self.stats['errors'] += 1
            return pd.DataFrame()
    
    def process_new_feedback(self) -> bool:
        """
        Process new feedback through the complete pipeline
        
        Returns:
            bool: Success status
        """
        try:
            self.stats['start_time'] = datetime.now()
            
            # Get unprocessed feedback
            batch_size = self.config.get('processing', {}).get('batch_size', 1000)
            feedback_df = self.db_handler.get_unprocessed_feedback(limit=batch_size)
            
            if feedback_df.empty:
                self.logger.info("No new feedback to process")
                return True
            
            self.logger.info(f"Processing {len(feedback_df)} new feedback items")
            self.stats['feedback_processed'] = len(feedback_df)
            
            # Run sentiment analysis
            sentiment_results = self.run_sentiment_analysis(feedback_df)
            
            # Save sentiment results
            if not sentiment_results.empty:
                success = self.db_handler.save_sentiment_results(sentiment_results)
                if not success:
                    self.logger.error("Failed to save sentiment results")
                    return False
            
            # Run topic extraction
            topic_results = self.run_topic_extraction(feedback_df)
            
            # Save topic results
            if not topic_results.empty:
                success = self.db_handler.save_topic_results(topic_results)
                if not success:
                    self.logger.error("Failed to save topic results")
                    return False
            
            # Update satisfaction metrics
            self.db_handler.update_satisfaction_metrics()
            
            self.stats['end_time'] = datetime.now()
            self.stats['success_rate'] = ((self.stats['sentiment_analyzed'] + self.stats['topics_extracted']) / 
                                        (2 * self.stats['feedback_processed'])) * 100 if self.stats['feedback_processed'] > 0 else 0
            
            self.logger.info("Pipeline processing completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline processing failed: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.stats['errors'] += 1
            return False
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete feedback analysis pipeline
        
        Returns:
            Dict[str, Any]: Pipeline execution results
        """
        try:
            self.logger.info("Starting feedback analysis pipeline")
            
            # Initialize components
            self.initialize_components()
            
            # Process new feedback
            success = self.process_new_feedback()
            
            # Generate pipeline report
            report = self.generate_pipeline_report(success)
            
            # Send notifications if configured
            if self.config.get('notifications', {}).get('enabled', False):
                self.send_pipeline_notification(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def generate_pipeline_report(self, success: bool) -> Dict[str, Any]:
        """
        Generate comprehensive pipeline execution report
        
        Args:
            success (bool): Pipeline success status
            
        Returns:
            Dict[str, Any]: Pipeline report
        """
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        report = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'statistics': {
                'feedback_processed': self.stats['feedback_processed'],
                'sentiment_analyzed': self.stats['sentiment_analyzed'],
                'topics_extracted': self.stats['topics_extracted'],
                'errors': self.stats['errors'],
                'success_rate': round(self.stats['success_rate'], 2)
            }
        }
        
        # Add database health check
        if self.db_handler:
            report['database_health'] = self.db_handler.health_check()
        
        # Add recent performance metrics
        if self.db_handler and success:
            try:
                dashboard_data = self.db_handler.get_dashboard_data()
                report['recent_metrics'] = {
                    'total_feedback_30d': dashboard_data.get('overall_metrics', {}).get('total_feedback', 0),
                    'avg_sentiment_30d': round(dashboard_data.get('overall_metrics', {}).get('avg_sentiment', 0), 3),
                    'top_topics': dashboard_data.get('topic_summary', pd.DataFrame()).head(5).to_dict('records')
                }
            except Exception as e:
                self.logger.warning(f"Failed to add recent metrics to report: {e}")
        
        return report
    
    def send_pipeline_notification(self, report: Dict[str, Any]):
        """Send pipeline execution notification"""
        try:
            notification_config = self.config.get('notifications', {})
            
            if not notification_config.get('enabled', False):
                return
            
            message = self._format_notification_message(report)
            
            # Send notification (implement based on your needs)
            send_notification(
                message=message,
                config=notification_config,
                logger=self.logger
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def _format_notification_message(self, report: Dict[str, Any]) -> str:
        """Format notification message"""
        status_emoji = "✅" if report['success'] else "❌"
        
        message = f"""
{status_emoji} Feedback Analysis Pipeline Report

📊 Processing Statistics:
• Feedback Processed: {report['statistics']['feedback_processed']}
• Sentiment Analyzed: {report['statistics']['sentiment_analyzed']}
• Topics Extracted: {report['statistics']['topics_extracted']}
• Success Rate: {report['statistics']['success_rate']}%
• Errors: {report['statistics']['errors']}
• Duration: {report['duration_seconds']:.2f} seconds

🔍 Recent Metrics (30 days):
• Total Feedback: {report.get('recent_metrics', {}).get('total_feedback_30d', 'N/A')}
• Average Sentiment: {report.get('recent_metrics', {}).get('avg_sentiment_30d', 'N/A')}

⏰ Timestamp: {report['timestamp']}
        """
        
        return message.strip()
    
    def run_maintenance(self) -> bool:
        """
        Run maintenance tasks
        
        Returns:
            bool: Success status
        """
        try:
            self.logger.info("Starting maintenance tasks")
            
            if not self.db_handler:
                self.initialize_components()
            
            # Clean up old data
            cleanup_config = self.config.get('maintenance', {})
            days_to_keep = cleanup_config.get('days_to_keep', 365)
            
            success = self.db_handler.cleanup_old_data(days_to_keep)
            
            if success:
                self.logger.info("Maintenance tasks completed successfully")
            else:
                self.logger.error("Maintenance tasks failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Maintenance tasks failed: {e}")
            return False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status
        
        Returns:
            Dict[str, Any]: Pipeline status information
        """
        status = {
            'pipeline_initialized': all([
                self.db_handler is not None,
                self.sentiment_analyzer is not None,
                self.topic_extractor is not None
            ]),
            'last_run_stats': self.stats,
            'config_loaded': self.config is not None
        }
        
        if self.db_handler:
            status['database_health'] = self.db_handler.health_check()
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        'database': {
            'server': 'localhost',
            'database': 'feedback_analysis',
            'username': 'sa',
            'password': 'password',
            'driver': 'ODBC Driver 17 for SQL Server'
        },
        'processing': {
            'batch_size': 1000
        },
        'sentiment_analysis': {
            'vader_weight': 0.6,
            'textblob_weight': 0.4,
            'batch_size': 1000
        },
        'topic_extraction': {
            'max_features': 100,
            'min_df': 2,
            'ngram_range': [1, 2],
            'n_topics': 10
        },
        'logging': {
            'level': 'INFO',
            'file': 'pipeline.log'
        },
        'notifications': {
            'enabled': False
        },
        'maintenance': {
            'days_to_keep': 365
        }
    }
    
    try:
        # Initialize pipeline
        pipeline = FeedbackAnalysisPipeline(config_dict=config)
        
        # Run full pipeline
        result = pipeline.run_full_pipeline()
        
        print("Pipeline Execution Report:")
        print("-" * 30)
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")