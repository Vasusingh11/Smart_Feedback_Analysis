"""
Helper Utilities Module
Provides common utility functions for the feedback analysis platform
"""

import os
import json
import yaml
import smtplib
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration dictionary
    
    Args:
        config (dict): Configuration to validate
        
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    required_sections = ['database', 'processing', 'sentiment_analysis', 'topic_extraction']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate database config
    db_config = config['database']
    required_db_fields = ['server', 'database']
    for field in required_db_fields:
        if field not in db_config:
            raise ValueError(f"Missing required database field: {field}")
    
    # Validate processing config
    processing_config = config['processing']
    if 'batch_size' in processing_config:
        if not isinstance(processing_config['batch_size'], int) or processing_config['batch_size'] <= 0:
            raise ValueError("batch_size must be a positive integer")
    
    # Validate sentiment analysis config
    sentiment_config = config['sentiment_analysis']
    if 'vader_weight' in sentiment_config and 'textblob_weight' in sentiment_config:
        total_weight = sentiment_config['vader_weight'] + sentiment_config['textblob_weight']
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError("vader_weight and textblob_weight must sum to 1.0")
    
    return True

def load_environment_variables():
    """Load environment variables with FEEDBACK_ANALYSIS_ prefix"""
    env_vars = {}
    prefix = "FEEDBACK_ANALYSIS_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to nested dict structure
            clean_key = key[len(prefix):].lower()
            sections = clean_key.split('_')
            
            # Navigate/create nested structure
            current = env_vars
            for section in sections[:-1]:
                if section not in current:
                    current[section] = {}
                current = current[section]
            
            # Set the value (try to convert to appropriate type)
            current[sections[-1]] = convert_env_value(value)
    
    return env_vars

def convert_env_value(value: str) -> Union[str, int, float, bool]:
    """Convert environment variable string to appropriate type"""
    # Boolean conversion
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Integer conversion
    try:
        return int(value)
    except ValueError:
        pass
    
    # Float conversion
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge configuration dictionaries
    
    Args:
        base_config (dict): Base configuration
        override_config (dict): Override configuration
        
    Returns:
        dict: Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged

def send_notification(message: str, config: Dict[str, Any], logger: logging.Logger):
    """
    Send notification via configured channels
    
    Args:
        message (str): Message to send
        config (dict): Notification configuration
        logger (logging.Logger): Logger instance
    """
    try:
        # Email notification
        if config.get('email', {}).get('enabled', False):
            send_email_notification(message, config['email'], logger)
        
        # Slack notification
        if config.get('slack', {}).get('enabled', False):
            send_slack_notification(message, config['slack'], logger)
        
        # Teams notification
        if config.get('teams', {}).get('enabled', False):
            send_teams_notification(message, config['teams'], logger)
            
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def send_email_notification(message: str, email_config: Dict[str, Any], logger: logging.Logger):
    """Send email notification"""
    try:
        msg = MimeMultipart()
        msg['From'] = email_config['username']
        msg['To'] = ', '.join(email_config['recipients'])
        msg['Subject'] = f"{email_config.get('subject_prefix', '')} Pipeline Report"
        
        msg.attach(MimeText(message, 'plain'))
        
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['username'], email_config['password'])
        text = msg.as_string()
        server.sendmail(email_config['username'], email_config['recipients'], text)
        server.quit()
        
        logger.info("Email notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")

def send_slack_notification(message: str, slack_config: Dict[str, Any], logger: logging.Logger):
    """Send Slack notification"""
    try:
        payload = {
            'text': message,
            'channel': slack_config.get('channel', '#general')
        }
        
        response = requests.post(
            slack_config['webhook_url'], 
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info("Slack notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")

def send_teams_notification(message: str, teams_config: Dict[str, Any], logger: logging.Logger):
    """Send Microsoft Teams notification"""
    try:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Feedback Analysis Pipeline Report",
            "sections": [{
                "activityTitle": "Feedback Analysis Pipeline",
                "activitySubtitle": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text": message,
                "markdown": True
            }]
        }
        
        response = requests.post(
            teams_config['webhook_url'],
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info("Teams notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send Teams notification: {e}")

def calculate_business_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate business metrics from feedback data
    
    Args:
        df (pd.DataFrame): Feedback data with sentiment analysis
        
    Returns:
        dict: Business metrics
    """
    if df.empty:
        return {}
    
    metrics = {}
    
    # Basic counts
    metrics['total_feedback'] = len(df)
    metrics['unique_customers'] = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
    
    # Sentiment distribution
    if 'sentiment_label' in df.columns:
        sentiment_counts = df['sentiment_label'].value_counts()
        total = len(df)
        
        metrics['positive_count'] = sentiment_counts.get('Positive', 0)
        metrics['negative_count'] = sentiment_counts.get('Negative', 0)
        metrics['neutral_count'] = sentiment_counts.get('Neutral', 0)
        
        metrics['positive_percentage'] = round((metrics['positive_count'] / total) * 100, 2)
        metrics['negative_percentage'] = round((metrics['negative_count'] / total) * 100, 2)
        metrics['neutral_percentage'] = round((metrics['neutral_count'] / total) * 100, 2)
    
    # Sentiment scores
    if 'sentiment_score' in df.columns:
        metrics['avg_sentiment'] = round(df['sentiment_score'].mean(), 4)
        metrics['sentiment_std'] = round(df['sentiment_score'].std(), 4)
        metrics['min_sentiment'] = round(df['sentiment_score'].min(), 4)
        metrics['max_sentiment'] = round(df['sentiment_score'].max(), 4)
    
    # Confidence metrics
    if 'confidence_score' in df.columns:
        metrics['avg_confidence'] = round(df['confidence_score'].mean(), 4)
        metrics['high_confidence_count'] = len(df[df['confidence_score'] > 0.8])
        metrics['low_confidence_count'] = len(df[df['confidence_score'] < 0.3])
    
    # Time-based metrics
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        metrics['date_range'] = {
            'start': df['timestamp'].min().isoformat(),
            'end': df['timestamp'].max().isoformat()
        }
        
        # Daily averages
        daily_stats = df.groupby(df['timestamp'].dt.date).agg({
            'sentiment_score': 'mean',
            'feedback_id': 'count'
        }).round(4)
        
        metrics['avg_daily_feedback'] = round(daily_stats['feedback_id'].mean(), 2)
        metrics['avg_daily_sentiment'] = round(daily_stats['sentiment_score'].mean(), 4)
    
    # Source breakdown
    if 'source' in df.columns:
        source_stats = df.groupby('source').agg({
            'feedback_id': 'count',
            'sentiment_score': 'mean'
        }).round(4)
        
        metrics['source_breakdown'] = source_stats.to_dict('index')
    
    return metrics

def generate_summary_report(metrics: Dict[str, Any], topics: List[Dict[str, Any]] = None) -> str:
    """
    Generate a human-readable summary report
    
    Args:
        metrics (dict): Business metrics
        topics (list): Top topics (optional)
        
    Returns:
        str: Formatted summary report
    """
    report_lines = [
        "=" * 50,
        "FEEDBACK ANALYSIS SUMMARY REPORT",
        "=" * 50,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📊 OVERVIEW",
        f"• Total Feedback: {metrics.get('total_feedback', 0):,}",
        f"• Unique Customers: {metrics.get('unique_customers', 0):,}",
        f"• Average Sentiment: {metrics.get('avg_sentiment', 0):.3f}",
        f"• Average Confidence: {metrics.get('avg_confidence', 0):.3f}",
        "",
        "😊 SENTIMENT DISTRIBUTION",
        f"• Positive: {metrics.get('positive_count', 0):,} ({metrics.get('positive_percentage', 0)}%)",
        f"• Negative: {metrics.get('negative_count', 0):,} ({metrics.get('negative_percentage', 0)}%)",
        f"• Neutral: {metrics.get('neutral_count', 0):,} ({metrics.get('neutral_percentage', 0)}%)",
        "",
    ]
    
    # Add time-based metrics if available
    if 'date_range' in metrics:
        report_lines.extend([
            "📅 TIME ANALYSIS",
            f"• Date Range: {metrics['date_range']['start']} to {metrics['date_range']['end']}",
            f"• Daily Average Feedback: {metrics.get('avg_daily_feedback', 0):.1f}",
            f"• Daily Average Sentiment: {metrics.get('avg_daily_sentiment', 0):.3f}",
            "",
        ])
    
    # Add source breakdown if available
    if 'source_breakdown' in metrics:
        report_lines.extend([
            "📱 SOURCE ANALYSIS",
        ])
        for source, stats in metrics['source_breakdown'].items():
            count = stats.get('feedback_id', 0)
            avg_sentiment = stats.get('sentiment_score', 0)
            report_lines.append(f"• {source}: {count:,} items (avg sentiment: {avg_sentiment:.3f})")
        report_lines.append("")
    
    # Add topics if provided
    if topics:
        report_lines.extend([
            "🏷️ TOP TOPICS",
        ])
        for i, topic in enumerate(topics[:5], 1):
            name = topic.get('topic_name', 'Unknown')
            doc_count = topic.get('document_count', 0)
            relevance = topic.get('coherence_score', 0)
            report_lines.append(f"• {i}. {name}: {doc_count} mentions (relevance: {relevance:.3f})")
        report_lines.append("")
    
    report_lines.extend([
        "=" * 50,
        "End of Report",
        "=" * 50
    ])
    
    return "\n".join(report_lines)

def export_data_to_formats(df: pd.DataFrame, base_filename: str, formats: List[str], 
                          output_dir: str = "exports/") -> List[str]:
    """
    Export DataFrame to multiple formats
    
    Args:
        df (pd.DataFrame): Data to export
        base_filename (str): Base filename without extension
        formats (list): List of formats ('csv', 'excel', 'json')
        output_dir (str): Output directory
        
    Returns:
        list: List of created file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    created_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for format_type in formats:
        try:
            filename = f"{base_filename}_{timestamp}.{format_type}"
            filepath = os.path.join(output_dir, filename)
            
            if format_type.lower() == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8')
            elif format_type.lower() in ['excel', 'xlsx']:
                df.to_excel(filepath, index=False, engine='openpyxl')
            elif format_type.lower() == 'json':
                df.to_json(filepath, orient='records', date_format='iso', indent=2)
            
            created_files.append(filepath)
            
        except Exception as e:
            logging.error(f"Failed to export to {format_type}: {e}")
    
    return created_files

def clean_old_exports(export_dir: str = "exports/", retention_days: int = 30):
    """Clean old export files"""
    if not os.path.exists(export_dir):
        return
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for filename in os.listdir(export_dir):
        filepath = os.path.join(export_dir, filename)
        
        try:
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_modified < cutoff_date:
                os.remove(filepath)
                logging.info(f"Removed old export file: {filename}")
        except Exception as e:
            logging.error(f"Failed to remove old export file {filename}: {e}")

def health_check_external_services() -> Dict[str, bool]:
    """Check health of external services"""
    health_status = {}
    
    # Check internet connectivity
    try:
        response = requests.get('https://httpbin.org/status/200', timeout=5)
        health_status['internet'] = response.status_code == 200
    except:
        health_status['internet'] = False
    
    # Add more service checks as needed
    # health_status['api_service'] = check_api_service()
    # health_status['file_storage'] = check_file_storage()
    
    return health_status

# Example usage
if __name__ == "__main__":
    # Test configuration validation
    test_config = {
        'database': {
            'server': 'localhost',
            'database': 'test'
        },
        'processing': {
            'batch_size': 1000
        },
        'sentiment_analysis': {
            'vader_weight': 0.6,
            'textblob_weight': 0.4
        },
        'topic_extraction': {
            'n_topics': 10
        }
    }
    
    try:
        validate_config(test_config)
        print("✓ Configuration validation passed")
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")
    
    # Test metrics calculation
    sample_data = pd.DataFrame({
        'feedback_id': range(100),
        'customer_id': [f'CUST_{i//10}' for i in range(100)],
        'sentiment_label': ['Positive'] * 60 + ['Negative'] * 25 + ['Neutral'] * 15,
        'sentiment_score': np.random.normal(0.1, 0.3, 100),
        'confidence_score': np.random.uniform(0.5, 1.0, 100),
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H')
    })
    
    metrics = calculate_business_metrics(sample_data)
    print("\n📊 Sample Metrics:")
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
    
    # Test summary report
    report = generate_summary_report(metrics)
    print("\n" + report)