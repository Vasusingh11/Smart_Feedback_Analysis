#!/usr/bin/env python3
"""
Health Check Script
Monitors system health and provides status information
"""

import os
import sys
import yaml
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import DatabaseHandler
from src.utils.helpers import health_check_external_services

class HealthChecker:
    """
    Comprehensive health checking for the feedback analysis platform
    """
    
    def __init__(self, config_path: str = None):
        """Initialize health checker"""
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'config.yaml'
        self.config = self._load_config()
        self.db_handler = None
        
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
                return {}
    
    def check_system_resources(self) -> dict:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # System load (Unix/Linux only)
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                load_avg = None
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'memory_available_gb': round(memory_available_gb, 2),
                'disk_percent': round(disk_percent, 2),
                'disk_free_gb': round(disk_free_gb, 2),
                'load_average': load_avg,
                'status': 'healthy' if cpu_percent < 90 and memory_percent < 90 and disk_percent < 90 else 'warning'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def check_database_health(self) -> dict:
        """Check database connectivity and performance"""
        try:
            if not self.db_handler:
                self.db_handler = DatabaseHandler(config=self.config.get('database', {}))
            
            # Basic health check
            health_status = self.db_handler.health_check()
            
            # Additional performance checks
            if health_status.get('connection', False):
                # Check recent processing activity
                query = """
                SELECT 
                    COUNT(*) as total_feedback,
                    COUNT(DISTINCT f.timestamp::date) as active_days,
                    MAX(f.timestamp) as latest_feedback,
                    COUNT(sa.feedback_id) as processed_count
                FROM feedback f
                LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
                WHERE f.timestamp >= CURRENT_DATE - INTERVAL '7 days'
                """
                
                try:
                    # Adjust query for SQL Server
                    sql_server_query = """
                    SELECT 
                        COUNT(*) as total_feedback,
                        COUNT(DISTINCT CAST(f.timestamp AS DATE)) as active_days,
                        MAX(f.timestamp) as latest_feedback,
                        COUNT(sa.feedback_id) as processed_count
                    FROM feedback f
                    LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
                    WHERE f.timestamp >= DATEADD(day, -7, GETDATE())
                    """
                    
                    result = self.db_handler.execute_query(sql_server_query)
                    
                    if not result.empty:
                        row = result.iloc[0]
                        health_status.update({
                            'total_feedback_7d': int(row['total_feedback']),
                            'active_days_7d': int(row['active_days']),
                            'latest_feedback': row['latest_feedback'],
                            'processed_count_7d': int(row['processed_count']),
                            'processing_rate': round(int(row['processed_count']) / max(int(row['total_feedback']), 1) * 100, 2)
                        })
                    
                except Exception as e:
                    health_status['query_error'] = str(e)
            
            return health_status
            
        except Exception as e:
            return {
                'connection': False,
                'error': str(e),
                'status': 'error'
            }
    
    def check_log_files(self) -> dict:
        """Check log file status and recent activity"""
        try:
            log_dir = Path('logs')
            log_status = {
                'log_directory_exists': log_dir.exists(),
                'log_files': [],
                'recent_activity': False,
                'total_size_mb': 0,
                'status': 'healthy'
            }
            
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    try:
                        stat = log_file.stat()
                        size_mb = stat.st_size / (1024 * 1024)
                        modified = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Check if modified in last 24 hours
                        is_recent = modified > (datetime.now() - timedelta(hours=24))
                        
                        log_status['log_files'].append({
                            'name': log_file.name,
                            'size_mb': round(size_mb, 2),
                            'modified': modified.isoformat(),
                            'recent_activity': is_recent
                        })
                        
                        log_status['total_size_mb'] += size_mb
                        
                        if is_recent:
                            log_status['recent_activity'] = True
                            
                    except Exception as e:
                        log_status['log_files'].append({
                            'name': log_file.name,
                            'error': str(e)
                        })
                
                log_status['total_size_mb'] = round(log_status['total_size_mb'], 2)
                
                # Status based on activity and size
                if log_status['total_size_mb'] > 100:  # Over 100MB
                    log_status['status'] = 'warning'
                elif not log_status['recent_activity']:
                    log_status['status'] = 'warning'
            else:
                log_status['status'] = 'warning'
            
            return log_status
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def check_data_directories(self) -> dict:
        """Check data directory status"""
        try:
            directories = ['data', 'exports', 'logs']
            dir_status = {
                'directories': {},
                'status': 'healthy'
            }
            
            for directory in directories:
                dir_path = Path(directory)
                
                if dir_path.exists():
                    # Get directory size and file count
                    total_size = 0
                    file_count = 0
                    
                    try:
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                total_size += file_path.stat().st_size
                                file_count += 1
                        
                        dir_status['directories'][directory] = {
                            'exists': True,
                            'size_mb': round(total_size / (1024 * 1024), 2),
                            'file_count': file_count,
                            'writable': os.access(dir_path, os.W_OK)
                        }
                        
                    except Exception as e:
                        dir_status['directories'][directory] = {
                            'exists': True,
                            'error': str(e)
                        }
                else:
                    dir_status['directories'][directory] = {
                        'exists': False,
                        'status': 'missing'
                    }
                    dir_status['status'] = 'warning'
            
            return dir_status
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def check_dependencies(self) -> dict:
        """Check Python dependencies and NLTK data"""
        try:
            import pkg_resources
            
            dep_status = {
                'python_version': sys.version,
                'packages': {},
                'nltk_data': {},
                'status': 'healthy'
            }
            
            # Check key packages
            key_packages = [
                'pandas', 'numpy', 'nltk', 'textblob', 'scikit-learn',
                'sqlalchemy', 'pyodbc', 'pyyaml', 'schedule'
            ]
            
            for package in key_packages:
                try:
                    dist = pkg_resources.get_distribution(package)
                    dep_status['packages'][package] = {
                        'version': dist.version,
                        'available': True
                    }
                except pkg_resources.DistributionNotFound:
                    dep_status['packages'][package] = {
                        'available': False
                    }
                    dep_status['status'] = 'error'
            
            # Check NLTK data
            try:
                import nltk
                
                nltk_datasets = ['punkt', 'stopwords', 'vader_lexicon', 'wordnet']
                
                for dataset in nltk_datasets:
                    try:
                        if dataset == 'punkt':
                            nltk.data.find('tokenizers/punkt')
                        elif dataset == 'vader_lexicon':
                            nltk.data.find('vader_lexicon')
                        else:
                            nltk.data.find(f'corpora/{dataset}')
                        
                        dep_status['nltk_data'][dataset] = True
                        
                    except LookupError:
                        dep_status['nltk_data'][dataset] = False
                        if dep_status['status'] == 'healthy':
                            dep_status['status'] = 'warning'
                            
            except ImportError:
                dep_status['nltk_data'] = {'error': 'NLTK not available'}
                dep_status['status'] = 'error'
            
            return dep_status
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def run_comprehensive_health_check(self) -> dict:
        """Run all health checks and return comprehensive status"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Run all health checks
        checks = [
            ('system_resources', self.check_system_resources),
            ('database', self.check_database_health),
            ('log_files', self.check_log_files),
            ('data_directories', self.check_data_directories),
            ('dependencies', self.check_dependencies),
            ('external_services', health_check_external_services)
        ]
        
        error_count = 0
        warning_count = 0
        
        for check_name, check_function in checks:
            try:
                result = check_function()
                health_report['checks'][check_name] = result
                
                status = result.get('status', 'unknown')
                if status == 'error':
                    error_count += 1
                elif status == 'warning':
                    warning_count += 1
                    
            except Exception as e:
                health_report['checks'][check_name] = {
                    'error': str(e),
                    'status': 'error'
                }
                error_count += 1
        
        # Determine overall status
        if error_count > 0:
            health_report['overall_status'] = 'error'
        elif warning_count > 0:
            health_report['overall_status'] = 'warning'
        
        health_report['summary'] = {
            'total_checks': len(checks),
            'healthy_checks': len(checks) - error_count - warning_count,
            'warning_checks': warning_count,
            'error_checks': error_count
        }
        
        return health_report
    
    def print_health_report(self, health_report: dict):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("SMART FEEDBACK ANALYSIS - HEALTH CHECK REPORT")
        print("="*60)
        print(f"Timestamp: {health_report['timestamp']}")
        print(f"Overall Status: {self._get_status_emoji(health_report['overall_status'])} {health_report['overall_status'].upper()}")
        
        summary = health_report['summary']
        print(f"Summary: {summary['healthy_checks']}/{summary['total_checks']} checks healthy, "
              f"{summary['warning_checks']} warnings, {summary['error_checks']} errors")
        
        print("\n" + "-"*60)
        
        for check_name, check_result in health_report['checks'].items():
            status = check_result.get('status', 'unknown')
            emoji = self._get_status_emoji(status)
            
            print(f"\n{emoji} {check_name.replace('_', ' ').title()}: {status.upper()}")
            
            # Print key metrics for each check
            if check_name == 'system_resources' and 'cpu_percent' in check_result:
                print(f"  CPU: {check_result['cpu_percent']}%")
                print(f"  Memory: {check_result['memory_percent']}% ({check_result['memory_available_gb']:.1f}GB free)")
                print(f"  Disk: {check_result['disk_percent']}% ({check_result['disk_free_gb']:.1f}GB free)")
                
            elif check_name == 'database' and 'connection' in check_result:
                print(f"  Connection: {'✓' if check_result['connection'] else '✗'}")
                print(f"  Tables: {'✓' if check_result.get('tables_exist') else '✗'}")
                if 'total_feedback_7d' in check_result:
                    print(f"  Recent Activity: {check_result['total_feedback_7d']} feedback (7 days)")
                    print(f"  Processing Rate: {check_result.get('processing_rate', 0)}%")
                    
            elif check_name == 'log_files' and 'log_files' in check_result:
                print(f"  Log Files: {len(check_result['log_files'])}")
                print(f"  Total Size: {check_result['total_size_mb']}MB")
                print(f"  Recent Activity: {'✓' if check_result['recent_activity'] else '✗'}")
                
            elif check_name == 'dependencies' and 'packages' in check_result:
                available_packages = sum(1 for p in check_result['packages'].values() if p.get('available', False))
                total_packages = len(check_result['packages'])
                print(f"  Packages: {available_packages}/{total_packages} available")
                
                if 'nltk_data' in check_result:
                    available_nltk = sum(1 for v in check_result['nltk_data'].values() if v is True)
                    total_nltk = len([v for v in check_result['nltk_data'].values() if isinstance(v, bool)])
                    print(f"  NLTK Data: {available_nltk}/{total_nltk} datasets")
            
            # Print errors if any
            if 'error' in check_result:
                print(f"  Error: {check_result['error']}")
        
        print("\n" + "="*60)
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        emoji_map = {
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌',
            'unknown': '❓'
        }
        return emoji_map.get(status, '❓')

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart Feedback Analysis Platform - Health Check',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--check', choices=['system', 'database', 'logs', 'directories', 'dependencies'],
                       help='Run specific check only')
    parser.add_argument('--exit-code', action='store_true', 
                       help='Exit with non-zero code if any errors found')
    
    args = parser.parse_args()
    
    try:
        checker = HealthChecker(config_path=args.config)
        
        if args.check:
            # Run specific check
            check_methods = {
                'system': checker.check_system_resources,
                'database': checker.check_database_health,
                'logs': checker.check_log_files,
                'directories': checker.check_data_directories,
                'dependencies': checker.check_dependencies
            }
            
            result = check_methods[args.check]()
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{args.check.title()} Check: {result.get('status', 'unknown')}")
                if result.get('error'):
                    print(f"Error: {result['error']}")
        else:
            # Run comprehensive health check
            health_report = checker.run_comprehensive_health_check()
            
            if args.json:
                print(json.dumps(health_report, indent=2))
            else:
                checker.print_health_report(health_report)
            
            # Exit with appropriate code
            if args.exit_code:
                if health_report['overall_status'] == 'error':
                    return 2
                elif health_report['overall_status'] == 'warning':
                    return 1
        
        return 0
        
    except Exception as e:
        if args.json:
            print(json.dumps({'error': str(e), 'status': 'error'}))
        else:
            print(f"❌ Health check failed: {e}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)