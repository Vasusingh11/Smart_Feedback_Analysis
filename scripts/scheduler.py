#!/usr/bin/env python3
"""
Automated Scheduler Script
Manages scheduled execution of the feedback analysis pipeline
"""

import os
import sys
import yaml
import time
import schedule
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.automation.pipeline import FeedbackAnalysisPipeline
from src.utils.logger import setup_logger

class PipelineScheduler:
    """
    Manages scheduled execution of feedback analysis tasks
    """
    
    def __init__(self, config_path: str = None):
        """Initialize scheduler with configuration"""
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'config.yaml'
        self.config = self._load_config()
        self.running = False
        self.logger = setup_logger(
            name='scheduler',
            level=self.config.get('logging', {}).get('level', 'INFO'),
            log_file=self.config.get('logging', {}).get('file', 'logs/scheduler.log')
        )
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Try example config
            example_config_path = Path(self.config_path).with_suffix('.yaml.example')
            if example_config_path.exists():
                with open(example_config_path, 'r') as file:
                    return yaml.safe_load(file)
            else:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_main_pipeline(self):
        """Execute the main analysis pipeline"""
        job_name = "Main Pipeline"
        self.logger.info(f"Starting scheduled job: {job_name}")
        
        try:
            pipeline = FeedbackAnalysisPipeline(config_dict=self.config)
            result = pipeline.run_full_pipeline()
            
            if result['success']:
                self.logger.info(f"✅ {job_name} completed successfully")
                if 'statistics' in result:
                    stats = result['statistics']
                    self.logger.info(
                        f"Processed {stats.get('feedback_processed', 0)} feedback items, "
                        f"{stats.get('sentiment_analyzed', 0)} sentiment analyses, "
                        f"{stats.get('topics_extracted', 0)} topic extractions"
                    )
            else:
                self.logger.error(f"❌ {job_name} failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"❌ {job_name} failed with exception: {e}", exc_info=True)
    
    def run_daily_report(self):
        """Generate and send daily report"""
        job_name = "Daily Report"
        self.logger.info(f"Starting scheduled job: {job_name}")
        
        try:
            pipeline = FeedbackAnalysisPipeline(config_dict=self.config)
            pipeline.initialize_components()
            
            # Get dashboard data for report
            dashboard_data = pipeline.db_handler.get_dashboard_data()
            
            if 'error' not in dashboard_data:
                # Generate report summary
                from src.utils.helpers import calculate_business_metrics, generate_summary_report
                
                # Create a summary report
                metrics = dashboard_data.get('overall_metrics', {})
                topics = dashboard_data.get('topic_summary', pd.DataFrame()).head(5).to_dict('records')
                
                report = generate_summary_report(metrics, topics)
                
                # Send notification if enabled
                if self.config.get('notifications', {}).get('enabled', False):
                    from src.utils.helpers import send_notification
                    send_notification(
                        message=f"📊 Daily Feedback Analysis Report\n\n{report}",
                        config=self.config.get('notifications', {}),
                        logger=self.logger
                    )
                
                self.logger.info(f"✅ {job_name} completed successfully")
            else:
                self.logger.error(f"❌ {job_name} failed: {dashboard_data['error']}")
                
        except Exception as e:
            self.logger.error(f"❌ {job_name} failed with exception: {e}", exc_info=True)
    
    def run_weekly_cleanup(self):
        """Run weekly maintenance and cleanup"""
        job_name = "Weekly Cleanup"
        self.logger.info(f"Starting scheduled job: {job_name}")
        
        try:
            pipeline = FeedbackAnalysisPipeline(config_dict=self.config)
            success = pipeline.run_maintenance()
            
            if success:
                self.logger.info(f"✅ {job_name} completed successfully")
            else:
                self.logger.error(f"❌ {job_name} failed")
                
        except Exception as e:
            self.logger.error(f"❌ {job_name} failed with exception: {e}", exc_info=True)
    
    def run_monthly_maintenance(self):
        """Run monthly comprehensive maintenance"""
        job_name = "Monthly Maintenance"
        self.logger.info(f"Starting scheduled job: {job_name}")
        
        try:
            pipeline = FeedbackAnalysisPipeline(config_dict=self.config)
            pipeline.initialize_components()
            
            # Run maintenance
            success = pipeline.run_maintenance()
            
            # Export monthly data if configured
            if self.config.get('data_export', {}).get('enabled', False):
                self._export_monthly_data(pipeline)
            
            # Update performance statistics
            self._update_performance_stats(pipeline)
            
            if success:
                self.logger.info(f"✅ {job_name} completed successfully")
            else:
                self.logger.error(f"❌ {job_name} failed")
                
        except Exception as e:
            self.logger.error(f"❌ {job_name} failed with exception: {e}", exc_info=True)
    
    def _export_monthly_data(self, pipeline):
        """Export monthly data for archival"""
        try:
            from src.utils.helpers import export_data_to_formats
            
            # Get last month's data
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            month_str = last_month.strftime("%Y_%m")
            
            # Export feedback data
            query = """
            SELECT f.*, sa.sentiment_score, sa.sentiment_label, sa.confidence_score
            FROM feedback f
            LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
            WHERE YEAR(f.timestamp) = ? AND MONTH(f.timestamp) = ?
            ORDER BY f.timestamp
            """
            
            df = pipeline.db_handler.execute_query(
                query, 
                {'year': last_month.year, 'month': last_month.month}
            )
            
            if not df.empty:
                export_config = self.config.get('data_export', {})
                formats = export_config.get('formats', ['csv'])
                output_dir = export_config.get('output_directory', 'exports/')
                
                export_data_to_formats(
                    df, 
                    f"feedback_export_{month_str}", 
                    formats, 
                    output_dir
                )
                
                self.logger.info(f"Exported {len(df)} records for {month_str}")
            
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
    
    def _update_performance_stats(self, pipeline):
        """Update system performance statistics"""
        try:
            # Get system health metrics
            health_check = pipeline.db_handler.health_check()
            
            # Log performance metrics
            if health_check.get('connection'):
                # Get processing performance
                query = """
                SELECT 
                    COUNT(*) as total_processed,
                    AVG(CAST(confidence_score AS FLOAT)) as avg_confidence,
                    COUNT(DISTINCT f.customer_id) as unique_customers
                FROM sentiment_analysis sa
                JOIN feedback f ON sa.feedback_id = f.feedback_id
                WHERE sa.processed_date >= DATEADD(month, -1, GETDATE())
                """
                
                stats = pipeline.db_handler.execute_query(query)
                
                if not stats.empty:
                    record = stats.iloc[0]
                    self.logger.info(
                        f"Monthly Performance: {record['total_processed']} processed, "
                        f"avg confidence {record['avg_confidence']:.3f}, "
                        f"{record['unique_customers']} unique customers"
                    )
            
        except Exception as e:
            self.logger.error(f"Performance stats update failed: {e}")
    
    def setup_schedules(self):
        """Setup all scheduled jobs based on configuration"""
        automation_config = self.config.get('automation', {})
        
        if not automation_config.get('enabled', True):
            self.logger.info("Automation is disabled in configuration")
            return
        
        schedules = automation_config.get('schedule', {})
        
        # Main pipeline schedule (default: every 4 hours)
        main_schedule = schedules.get('main_pipeline', '0 */4 * * *')
        if main_schedule:
            # Convert cron to schedule format (simplified)
            if '*/4' in main_schedule:
                schedule.every(4).hours.do(self.run_main_pipeline)
                self.logger.info("Scheduled main pipeline every 4 hours")
            elif '*/2' in main_schedule:
                schedule.every(2).hours.do(self.run_main_pipeline)
                self.logger.info("Scheduled main pipeline every 2 hours")
            else:
                # Default fallback
                schedule.every(4).hours.do(self.run_main_pipeline)
                self.logger.info("Scheduled main pipeline every 4 hours (default)")
        
        # Daily report schedule
        daily_schedule = schedules.get('daily_report', '0 9 * * *')
        if daily_schedule:
            schedule.every().day.at("09:00").do(self.run_daily_report)
            self.logger.info("Scheduled daily report at 09:00")
        
        # Weekly cleanup schedule
        weekly_schedule = schedules.get('weekly_cleanup', '0 2 * * 0')
        if weekly_schedule:
            schedule.every().sunday.at("02:00").do(self.run_weekly_cleanup)
            self.logger.info("Scheduled weekly cleanup on Sunday at 02:00")
        
        # Monthly maintenance schedule
        monthly_schedule = schedules.get('monthly_maintenance', '0 1 1 * *')
        if monthly_schedule:
            schedule.every().month.do(self.run_monthly_maintenance)
            self.logger.info("Scheduled monthly maintenance")
        
        self.logger.info(f"Setup {len(schedule.jobs)} scheduled jobs")
    
    def run_scheduler(self):
        """Main scheduler loop"""
        self.logger.info("="*50)
        self.logger.info("STARTING FEEDBACK ANALYSIS SCHEDULER")
        self.logger.info("="*50)
        self.logger.info(f"Config file: {self.config_path}")
        self.logger.info(f"Start time: {datetime.now().isoformat()}")
        
        # Setup schedules
        self.setup_schedules()
        
        # Print schedule summary
        self.logger.info("\nScheduled Jobs:")
        for job in schedule.jobs:
            self.logger.info(f"  - {job}")
        
        self.running = True
        
        try:
            # Run initial pipeline if configured
            if self.config.get('automation', {}).get('run_on_startup', False):
                self.logger.info("Running initial pipeline on startup...")
                self.run_main_pipeline()
            
            # Main scheduler loop
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Log heartbeat every hour
                if datetime.now().minute == 0:
                    self.logger.info(f"Scheduler heartbeat: {datetime.now().isoformat()}")
        
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
        except Exception as e:
            self.logger.error(f"Scheduler failed: {e}", exc_info=True)
        finally:
            self.logger.info("Scheduler shutting down...")
            self.running = False
    
    def list_jobs(self):
        """List all scheduled jobs"""
        print("\n" + "="*50)
        print("SCHEDULED JOBS")
        print("="*50)
        
        if not schedule.jobs:
            print("No jobs scheduled")
            return
        
        for i, job in enumerate(schedule.jobs, 1):
            next_run = job.next_run
            print(f"{i}. {job.job_func.__name__}")
            print(f"   Schedule: {job}")
            print(f"   Next run: {next_run}")
            print()

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart Feedback Analysis Platform - Scheduler',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--list-jobs', action='store_true', help='List scheduled jobs and exit')
    parser.add_argument('--run-once', choices=['pipeline', 'report', 'cleanup', 'maintenance'],
                       help='Run a specific job once and exit')
    
    args = parser.parse_args()
    
    try:
        scheduler = PipelineScheduler(config_path=args.config)
        
        if args.list_jobs:
            scheduler.setup_schedules()
            scheduler.list_jobs()
            return 0
        
        if args.run_once:
            if args.run_once == 'pipeline':
                scheduler.run_main_pipeline()
            elif args.run_once == 'report':
                scheduler.run_daily_report()
            elif args.run_once == 'cleanup':
                scheduler.run_weekly_cleanup()
            elif args.run_once == 'maintenance':
                scheduler.run_monthly_maintenance()
            return 0
        
        # Run continuous scheduler
        scheduler.run_scheduler()
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Scheduler stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Scheduler failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)