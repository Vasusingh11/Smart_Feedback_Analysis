"""
Logging Utility Module
Provides centralized logging configuration for the feedback analysis platform
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: str, level: str = 'INFO', log_file: Optional[str] = None, 
                max_file_size: str = '10MB', backup_count: int = 5) -> logging.Logger:
    """
    Setup centralized logger with file and console handlers
    
    Args:
        name (str): Logger name
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Log file path (optional)
        max_file_size (str): Maximum log file size
        backup_count (int): Number of backup files to keep
        
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Convert size string to bytes
        max_bytes = _convert_size_to_bytes(max_file_size)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def _convert_size_to_bytes(size_str: str) -> int:
    """Convert size string (e.g., '10MB') to bytes"""
    size_str = size_str.upper()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes if no unit specified
        return int(size_str)

class PerformanceLogger:
    """Context manager for performance logging"""
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.2f} seconds")
        else:
            self.logger.error(f"Failed {self.operation_name} after {duration:.2f} seconds: {exc_val}")

class StructuredLogger:
    """Structured logging with consistent format"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_pipeline_start(self, pipeline_name: str, batch_size: int):
        """Log pipeline start"""
        self.logger.info(f"PIPELINE_START: {pipeline_name} | batch_size={batch_size}")
    
    def log_pipeline_end(self, pipeline_name: str, success: bool, duration: float, 
                        records_processed: int, errors: int):
        """Log pipeline completion"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"PIPELINE_END: {pipeline_name} | status={status} | "
            f"duration={duration:.2f}s | records={records_processed} | errors={errors}"
        )
    
    def log_database_operation(self, operation: str, table: str, records: int, success: bool):
        """Log database operations"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"DB_OPERATION: {operation} | table={table} | records={records} | status={status}")
    
    def log_analysis_results(self, analysis_type: str, input_count: int, 
                           output_count: int, avg_confidence: float):
        """Log analysis results"""
        self.logger.info(
            f"ANALYSIS: {analysis_type} | input={input_count} | "
            f"output={output_count} | avg_confidence={avg_confidence:.3f}"
        )
    
    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context"""
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        self.logger.error(f"ERROR: {str(error)} | {context_str}", exc_info=True)

# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = setup_logger(
        name='test_logger',
        level='DEBUG',
        log_file='logs/test.log'
    )
    
    # Test basic logging
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test performance logging
    with PerformanceLogger(logger, "test_operation"):
        import time
        time.sleep(1)  # Simulate work
    
    # Test structured logging
    structured = StructuredLogger(logger)
    structured.log_pipeline_start("test_pipeline", 1000)
    structured.log_analysis_results("sentiment", 100, 95, 0.87)
    structured.log_pipeline_end("test_pipeline", True, 10.5, 1000, 0)