#!/usr/bin/env python3
"""
Run Analysis Script
Main entry point for running the feedback analysis pipeline
"""

import os
import sys
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.automation.pipeline import FeedbackAnalysisPipeline
from src.utils.logger import setup_logger
from src.utils.helpers import load_environment_variables, merge_configs

def load_config(config_path: str = None) -> dict:
    """Load configuration with environment variable overrides"""
    # Default config path
    if not config_path:
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    
    # Load base configuration
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        # Try example config
        example_config_path = Path(config_path).with_suffix('.yaml.example')
        if example_config_path.exists():
            with open(example_config_path, 'r') as file:
                config = yaml.safe_load(file)
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load environment variable overrides
    env_overrides = load_environment_variables()
    
    # Merge configurations (environment variables take precedence)
    if env_overrides:
        config = merge_configs(config, env_overrides)
    
    return config

def run_pipeline(args):
    """Run the main analysis pipeline"""
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Setup logging
        logger = setup_logger(
            name='pipeline_runner',
            level=config.get('logging', {}).get('level', 'INFO'),
            log_file=config.get('logging', {}).get('file', 'logs/pipeline.log')
        )
        
        logger.info("="*50)
        logger.info("STARTING FEEDBACK ANALYSIS PIPELINE")
        logger.info("="*50)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Config file: {args.config or 'config/config.yaml'}")
        logger.info(f"Batch size: {config.get('processing', {}).get('batch_size', 1000)}")
        
        # Initialize pipeline
        pipeline = FeedbackAnalysisPipeline(config_dict=config)
        
        # Run full pipeline
        result = pipeline.run_full_pipeline()
        
        # Print results
        print("\n" + "="*50)
        print("PIPELINE EXECUTION RESULTS")
        print("="*50)
        
        if result['success']:
            print("✅ Status: SUCCESS")
        else:
            print("❌ Status: FAILED")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        # Print statistics
        if 'statistics' in result:
            stats = result['statistics']
            print(f"📊 Feedback Processed: {stats.get('feedback_processed', 0):,}")
            print(f"🔍 Sentiment Analyzed: {stats.get('sentiment_analyzed', 0):,}")
            print(f"🏷️  Topics Extracted: {stats.get('topics_extracted', 0):,}")
            print(f"⚠️  Errors: {stats.get('errors', 0):,}")
            print(f"📈 Success Rate: {stats.get('success_rate', 0):.1f}%")
        
        # Print recent metrics
        if 'recent_metrics' in result:
            metrics = result['recent_metrics']
            print(f"\n📅 Recent Performance (30 days):")
            print(f"   Total Feedback: {metrics.get('total_feedback_30d', 0):,}")
            print(f"   Average Sentiment: {metrics.get('avg_sentiment_30d', 0):.3f}")
            
            if 'top_topics' in metrics and metrics['top_topics']:
                print(f"   Top Topics:")
                for i, topic in enumerate(metrics['top_topics'][:3], 1):
                    print(f"   {i}. {topic.get('topic', 'Unknown')} ({topic.get('mention_count', 0)} mentions)")
        
        # Print duration
        if result.get('duration_seconds'):
            duration = result['duration_seconds']
            print(f"⏱️  Duration: {duration:.2f} seconds")
        
        print("="*50)
        
        # Return exit code
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {e}")
        logging.error(f"Pipeline execution failed: {e}", exc_info=True)
        return 1

def run_maintenance(args):
    """Run maintenance tasks"""
    try:
        # Load configuration
        config = load_config(args.config)
        
        logger = setup_logger('maintenance', level='INFO')
        logger.info("Starting maintenance tasks...")
        
        # Initialize pipeline for maintenance
        pipeline = FeedbackAnalysisPipeline(config_dict=config)
        
        # Run maintenance
        success = pipeline.run_maintenance()
        
        if success:
            print("✅ Maintenance tasks completed successfully")
            return 0
        else:
            print("❌ Maintenance tasks failed")
            return 1
            
    except Exception as e:
        print(f"❌ Maintenance failed: {e}")
        return 1

def show_status(args):
    """Show pipeline status"""
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize pipeline
        pipeline = FeedbackAnalysisPipeline(config_dict=config)
        pipeline.initialize_components()
        
        # Get status
        status = pipeline.get_pipeline_status()
        
        print("\n" + "="*50)
        print("PIPELINE STATUS")
        print("="*50)
        
        # Pipeline status
        print(f"✅ Pipeline Initialized: {status['pipeline_initialized']}")
        print(f"✅ Config Loaded: {status['config_loaded']}")
        
        # Database health
        if 'database_health' in status:
            db_health = status['database_health']
            print(f"✅ Database Connection: {db_health.get('connection', False)}")
            print(f"✅ Tables Exist: {db_health.get('tables_exist', False)}")
            print(f"✅ Recent Data: {db_health.get('recent_data', False)}")
            
            if db_health.get('errors'):
                print(f"⚠️  Database Errors: {', '.join(db_health['errors'])}")
        
        # Last run statistics
        if 'last_run_stats' in status:
            stats = status['last_run_stats']
            if stats.get('feedback_processed', 0) > 0:
                print(f"\n📊 Last Run Statistics:")
                print(f"   Feedback Processed: {stats.get('feedback_processed', 0):,}")
                print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
                print(f"   Errors: {stats.get('errors', 0)}")
        
        print("="*50)
        return 0
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return 1

def generate_sample_data(args):
    """Generate sample data for testing"""
    try:
        import pandas as pd
        import random
        from datetime import datetime, timedelta
        
        # Load configuration
        config = load_config(args.config)
        
        from src.database.connection import DatabaseHandler
        
        print("Generating sample feedback data...")
        
        # Enhanced sample feedback texts
        positive_feedback = [
            "Excellent product quality! Exceeded my expectations completely.",
            "Outstanding customer service, resolved my issue immediately.",
            "Fast delivery and perfect packaging, very impressed!",
            "Great value for money, will definitely purchase again.",
            "User-friendly interface and intuitive design, love it!",
            "Amazing product features, exactly what I was looking for.",
            "Fantastic experience from start to finish, highly recommend!"
        ]
        
        negative_feedback = [
            "Poor quality product, broke after just one week of use.",
            "Terrible customer support, took days to get a response.",
            "Product arrived damaged and return process was complicated.",
            "Overpriced for the quality provided, not worth the money.",
            "Website is confusing and checkout process was frustrating.",
            "Product description was misleading, not as advertised.",
            "Long delivery time and poor communication throughout."
        ]
        
        neutral_feedback = [
            "Average product, does the job but nothing special.",
            "Standard delivery time, product as expected.",
            "Okay experience overall, neither great nor terrible.",
            "Product works fine, basic functionality as described.",
            "Normal customer service, no complaints but not impressed.",
            "Fair pricing for what you get, acceptable quality.",
            "Decent product but room for improvement in some areas."
        ]
        
        # Generate sample data
        sample_data = []
        for i in range(args.count):
            # Choose sentiment and corresponding feedback
            sentiment_choice = random.choices(
                ['positive', 'negative', 'neutral'],
                weights=[0.6, 0.25, 0.15],  # 60% positive, 25% negative, 15% neutral
                k=1
            )[0]
            
            if sentiment_choice == 'positive':
                feedback_text = random.choice(positive_feedback)
                rating = random.choices([4, 5], weights=[0.3, 0.7], k=1)[0]
            elif sentiment_choice == 'negative':
                feedback_text = random.choice(negative_feedback)
                rating = random.choices([1, 2], weights=[0.6, 0.4], k=1)[0]
            else:
                feedback_text = random.choice(neutral_feedback)
                rating = 3
            
            sample_data.append({
                'customer_id': f'CUST_{i//5:04d}',  # Multiple feedback per customer
                'feedback_text': feedback_text,
                'source': random.choice(['email', 'survey', 'social_media', 'website', 'phone', 'chat']),
                'product_category': random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']),
                'rating': rating,
                'timestamp': datetime.now() - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            })
        
        # Create DataFrame and save to database
        df = pd.DataFrame(sample_data)
        
        db_handler = DatabaseHandler(config=config['database'])
        success = db_handler.insert_dataframe(df, 'feedback', if_exists='append')
        
        if success:
            print(f"✅ Successfully generated {len(df):,} sample feedback records")
            print(f"   Positive: {len([d for d in sample_data if d['rating'] >= 4]):,}")
            print(f"   Negative: {len([d for d in sample_data if d['rating'] <= 2]):,}")
            print(f"   Neutral: {len([d for d in sample_data if d['rating'] == 3]):,}")
            return 0
        else:
            print("❌ Failed to generate sample data")
            return 1
            
    except Exception as e:
        print(f"❌ Sample data generation failed: {e}")
        return 1

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Smart Feedback Analysis Platform - Pipeline Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_analysis.py run                    # Run full pipeline
  python scripts/run_analysis.py run --config custom.yaml  # Use custom config
  python scripts/run_analysis.py maintenance            # Run maintenance tasks
  python scripts/run_analysis.py status                 # Check pipeline status
  python scripts/run_analysis.py sample --count 1000    # Generate 1000 sample records
        """
    )
    
    # Global arguments
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run pipeline command
    run_parser = subparsers.add_parser('run', help='Run the analysis pipeline')
    run_parser.set_defaults(func=run_pipeline)
    
    # Maintenance command
    maintenance_parser = subparsers.add_parser('maintenance', help='Run maintenance tasks')
    maintenance_parser.set_defaults(func=run_maintenance)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show pipeline status')
    status_parser.set_defaults(func=show_status)
    
    # Sample data command
    sample_parser = subparsers.add_parser('sample', help='Generate sample data')
    sample_parser.add_argument('--count', type=int, default=1000, help='Number of sample records')
    sample_parser.set_defaults(func=generate_sample_data)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 1
    
    # Set verbose logging if requested
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    # Run the specified command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)