#!/usr/bin/env python3
"""
Database Setup Script
Creates database, tables, views, and loads sample data
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import DatabaseHandler
from src.utils.logger import setup_logger

def load_config():
    """Load configuration from file"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        # Try example config
        example_config_path = config_path.with_suffix('.yaml.example')
        if example_config_path.exists():
            with open(example_config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

def read_sql_file(file_path: Path) -> str:
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"SQL file not found: {file_path}")
        return ""

def execute_sql_script(db_handler: DatabaseHandler, sql_content: str, script_name: str) -> bool:
    """Execute SQL script with error handling"""
    if not sql_content.strip():
        logging.warning(f"Empty SQL content for {script_name}")
        return True
    
    try:
        # Split by GO statements (SQL Server batch separator)
        batches = [batch.strip() for batch in sql_content.split('GO') if batch.strip()]
        
        for i, batch in enumerate(batches):
            if batch:
                logging.info(f"Executing batch {i+1}/{len(batches)} of {script_name}")
                db_handler.execute_non_query(batch)
        
        logging.info(f"Successfully executed {script_name}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to execute {script_name}: {e}")
        return False

def setup_database():
    """Main database setup function"""
    logger = setup_logger('database_setup', level='INFO')
    logger.info("Starting database setup...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize database handler
        db_handler = DatabaseHandler(config=config['database'])
        logger.info("Database connection established")
        
        # SQL files directory
        sql_dir = Path(__file__).parent.parent / 'sql'
        
        # Execute SQL scripts in order
        sql_scripts = [
            ('schema.sql', 'Database Schema'),
            ('views.sql', 'Database Views'),
            ('indexes.sql', 'Database Indexes'),
            ('sample_data.sql', 'Sample Data')
        ]
        
        success_count = 0
        for script_file, description in sql_scripts:
            script_path = sql_dir / script_file
            
            if script_path.exists():
                logger.info(f"Executing {description}...")
                sql_content = read_sql_file(script_path)
                
                if execute_sql_script(db_handler, sql_content, description):
                    success_count += 1
                    logger.info(f"✓ {description} completed successfully")
                else:
                    logger.error(f"✗ {description} failed")
            else:
                logger.warning(f"SQL script not found: {script_path}")
        
        # Verify database setup
        logger.info("Verifying database setup...")
        health_check = db_handler.health_check()
        
        if health_check['connection'] and health_check['tables_exist']:
            logger.info("✓ Database setup completed successfully!")
            logger.info(f"✓ Executed {success_count}/{len(sql_scripts)} scripts")
            
            # Print summary
            print("\n" + "="*50)
            print("DATABASE SETUP COMPLETE")
            print("="*50)
            print(f"✓ Database: {config['database']['database']}")
            print(f"✓ Server: {config['database']['server']}")
            print(f"✓ Scripts executed: {success_count}/{len(sql_scripts)}")
            print("✓ Tables and views created successfully")
            print("\nNext steps:")
            print("1. Run 'python scripts/run_analysis.py' to process feedback")
            print("2. Connect Power BI to your database")
            print("3. Import dashboard template from powerbi/")
            print("="*50)
            
            return True
        else:
            logger.error("✗ Database setup verification failed")
            logger.error(f"Health check results: {health_check}")
            return False
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def create_sample_data():
    """Create sample feedback data for testing"""
    logger = setup_logger('sample_data', level='INFO')
    
    try:
        import pandas as pd
        import random
        from datetime import datetime, timedelta
        
        logger.info("Generating sample feedback data...")
        
        # Sample feedback texts
        sample_feedback = [
            "Great product! Love the new features and excellent customer service.",
            "Poor quality, very disappointed. The product broke after one week.",
            "Average experience, nothing special but does the job okay.",
            "Excellent delivery speed and packaging was perfect!",
            "Customer support was unhelpful and took too long to respond.",
            "Amazing value for money, will definitely buy again.",
            "Product description was misleading, not what I expected.",
            "Fast shipping and great communication throughout the process.",
            "The return process was complicated and frustrating.",
            "Outstanding quality and design, highly recommend to others!",
            "Website is difficult to navigate and checkout was confusing.",
            "Product arrived damaged but replacement was sent quickly.",
            "Love the user-friendly interface and intuitive design.",
            "Overpriced for the quality provided, not worth the money.",
            "Fantastic customer experience from start to finish."
        ]
        
        # Generate sample data
        sample_data = []
        for i in range(1000):
            sample_data.append({
                'customer_id': f'CUST_{i//10:04d}',
                'feedback_text': random.choice(sample_feedback),
                'source': random.choice(['email', 'survey', 'social_media', 'website', 'phone']),
                'product_category': random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports']),
                'rating': random.randint(1, 5),
                'timestamp': datetime.now() - timedelta(days=random.randint(0, 90))
            })
        
        # Create DataFrame
        df = pd.DataFrame(sample_data)
        
        # Load config and save to database
        config = load_config()
        db_handler = DatabaseHandler(config=config['database'])
        
        success = db_handler.insert_dataframe(df, 'feedback', if_exists='append')
        
        if success:
            logger.info(f"✓ Successfully created {len(df)} sample feedback records")
            return True
        else:
            logger.error("✗ Failed to create sample data")
            return False
            
    except Exception as e:
        logger.error(f"Sample data creation failed: {e}")
        return False

def main():
    """Main function with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup database for Feedback Analysis Platform')
    parser.add_argument('--sample-data', action='store_true', 
                       help='Create sample feedback data for testing')
    parser.add_argument('--skip-schema', action='store_true',
                       help='Skip schema creation (useful for updates)')
    
    args = parser.parse_args()
    
    print("Smart Feedback Analysis Platform - Database Setup")
    print("="*50)
    
    # Setup database schema
    if not args.skip_schema:
        if not setup_database():
            print("Database setup failed!")
            sys.exit(1)
    
    # Create sample data if requested
    if args.sample_data:
        if not create_sample_data():
            print("Sample data creation failed!")
            sys.exit(1)
    
    print("\nDatabase setup completed successfully! 🎉")

if __name__ == "__main__":
    main()