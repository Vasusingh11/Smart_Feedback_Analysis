# Smart Feedback Analysis Platform - Environment Variables
# Copy this file to .env and update with your actual values

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_DATABASE_SERVER=localhost
FEEDBACK_ANALYSIS_DATABASE_DATABASE=feedback_analysis
FEEDBACK_ANALYSIS_DATABASE_USERNAME=sa
FEEDBACK_ANALYSIS_DATABASE_PASSWORD=YourPassword123
FEEDBACK_ANALYSIS_DATABASE_DRIVER=ODBC Driver 17 for SQL Server

# =============================================================================
# PROCESSING CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_PROCESSING_BATCH_SIZE=1000
FEEDBACK_ANALYSIS_PROCESSING_MAX_RETRIES=3
FEEDBACK_ANALYSIS_PROCESSING_RETRY_DELAY=30

# =============================================================================
# SENTIMENT ANALYSIS CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_SENTIMENT_ANALYSIS_VADER_WEIGHT=0.6
FEEDBACK_ANALYSIS_SENTIMENT_ANALYSIS_TEXTBLOB_WEIGHT=0.4
FEEDBACK_ANALYSIS_SENTIMENT_ANALYSIS_POSITIVE_THRESHOLD=0.05
FEEDBACK_ANALYSIS_SENTIMENT_ANALYSIS_NEGATIVE_THRESHOLD=-0.05
FEEDBACK_ANALYSIS_SENTIMENT_ANALYSIS_CONFIDENCE_THRESHOLD=0.3

# =============================================================================
# TOPIC EXTRACTION CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_TOPIC_EXTRACTION_MAX_FEATURES=100
FEEDBACK_ANALYSIS_TOPIC_EXTRACTION_MIN_DF=2
FEEDBACK_ANALYSIS_TOPIC_EXTRACTION_N_TOPICS=10
FEEDBACK_ANALYSIS_TOPIC_EXTRACTION_RELEVANCE_THRESHOLD=0.2

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_LOGGING_LEVEL=INFO
FEEDBACK_ANALYSIS_LOGGING_FILE=logs/pipeline.log
FEEDBACK_ANALYSIS_LOGGING_MAX_FILE_SIZE=10MB
FEEDBACK_ANALYSIS_LOGGING_BACKUP_COUNT=5

# =============================================================================
# AUTOMATION CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_AUTOMATION_ENABLED=true

# =============================================================================
# NOTIFICATION CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_NOTIFICATIONS_ENABLED=false

# Email Notifications
FEEDBACK_ANALYSIS_NOTIFICATIONS_EMAIL_ENABLED=false
FEEDBACK_ANALYSIS_NOTIFICATIONS_EMAIL_SMTP_SERVER=smtp.gmail.com
FEEDBACK_ANALYSIS_NOTIFICATIONS_EMAIL_SMTP_PORT=587
FEEDBACK_ANALYSIS_NOTIFICATIONS_EMAIL_USERNAME=your-email@gmail.com
FEEDBACK_ANALYSIS_NOTIFICATIONS_EMAIL_PASSWORD=your-app-password

# Slack Notifications
FEEDBACK_ANALYSIS_NOTIFICATIONS_SLACK_ENABLED=false
FEEDBACK_ANALYSIS_NOTIFICATIONS_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
FEEDBACK_ANALYSIS_NOTIFICATIONS_SLACK_CHANNEL=#data-alerts

# Microsoft Teams Notifications
FEEDBACK_ANALYSIS_NOTIFICATIONS_TEAMS_ENABLED=false
FEEDBACK_ANALYSIS_NOTIFICATIONS_TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK

# =============================================================================
# MAINTENANCE CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_MAINTENANCE_ENABLED=true
FEEDBACK_ANALYSIS_MAINTENANCE_DAYS_TO_KEEP=365
FEEDBACK_ANALYSIS_MAINTENANCE_CLEANUP_FREQUENCY=7

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_PERFORMANCE_CONNECTION_POOL_SIZE=10
FEEDBACK_ANALYSIS_PERFORMANCE_MAX_OVERFLOW=20
FEEDBACK_ANALYSIS_PERFORMANCE_QUERY_TIMEOUT=300
FEEDBACK_ANALYSIS_PERFORMANCE_MAX_WORKERS=4

# =============================================================================
# FEATURE FLAGS
# =============================================================================
FEEDBACK_ANALYSIS_FEATURES_ENABLE_TOPIC_EXTRACTION=true
FEEDBACK_ANALYSIS_FEATURES_ENABLE_SENTIMENT_ANALYSIS=true
FEEDBACK_ANALYSIS_FEATURES_ENABLE_REAL_TIME_PROCESSING=false
FEEDBACK_ANALYSIS_FEATURES_ENABLE_ADVANCED_ANALYTICS=true

# =============================================================================
# DATA EXPORT CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_DATA_EXPORT_ENABLED=true
FEEDBACK_ANALYSIS_DATA_EXPORT_OUTPUT_DIRECTORY=exports/
FEEDBACK_ANALYSIS_DATA_EXPORT_RETENTION_DAYS=30

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_SECURITY_ENCRYPT_SENSITIVE_DATA=true
FEEDBACK_ANALYSIS_SECURITY_MASK_CUSTOMER_DATA=false
FEEDBACK_ANALYSIS_SECURITY_AUDIT_LOGGING=true
FEEDBACK_ANALYSIS_SECURITY_SESSION_TIMEOUT=3600

# =============================================================================
# POWER BI INTEGRATION
# =============================================================================
FEEDBACK_ANALYSIS_POWERBI_ENABLED=true
FEEDBACK_ANALYSIS_POWERBI_DATASET_ID=your-powerbi-dataset-id
FEEDBACK_ANALYSIS_POWERBI_WORKSPACE_ID=your-powerbi-workspace-id

# Power BI Service Principal (for automated refresh)
FEEDBACK_ANALYSIS_POWERBI_SERVICE_PRINCIPAL_CLIENT_ID=your-client-id
FEEDBACK_ANALYSIS_POWERBI_SERVICE_PRINCIPAL_CLIENT_SECRET=your-client-secret
FEEDBACK_ANALYSIS_POWERBI_SERVICE_PRINCIPAL_TENANT_ID=your-tenant-id

# =============================================================================
# API CONFIGURATION (if enabled)
# =============================================================================
FEEDBACK_ANALYSIS_API_ENABLED=false
FEEDBACK_ANALYSIS_API_HOST=0.0.0.0
FEEDBACK_ANALYSIS_API_PORT=8000
FEEDBACK_ANALYSIS_API_DEBUG=false

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_MONITORING_ENABLED=true
FEEDBACK_ANALYSIS_MONITORING_HEALTH_CHECK_INTERVAL=300

# Alert Thresholds
FEEDBACK_ANALYSIS_MONITORING_ALERT_THRESHOLDS_ERROR_RATE=0.05
FEEDBACK_ANALYSIS_MONITORING_ALERT_THRESHOLDS_PROCESSING_DELAY=3600
FEEDBACK_ANALYSIS_MONITORING_ALERT_THRESHOLDS_DISK_USAGE=0.85
FEEDBACK_ANALYSIS_MONITORING_ALERT_THRESHOLDS_MEMORY_USAGE=0.90

# =============================================================================
# DEVELOPMENT/TESTING CONFIGURATION
# =============================================================================
FEEDBACK_ANALYSIS_DEVELOPMENT_DEBUG_MODE=false
FEEDBACK_ANALYSIS_DEVELOPMENT_VERBOSE_LOGGING=false
FEEDBACK_ANALYSIS_DEVELOPMENT_USE_SAMPLE_DATA=false

FEEDBACK_ANALYSIS_TESTING_ENABLED=false
FEEDBACK_ANALYSIS_TESTING_SAMPLE_DATA_SIZE=1000
FEEDBACK_ANALYSIS_TESTING_TEST_DATABASE=feedback_analysis_test

# =============================================================================
# DOCKER CONFIGURATION
# =============================================================================
# Database connection for Docker compose
DB_SERVER=sqlserver
DB_NAME=feedback_analysis
DB_USER=sa
DB_PASSWORD=YourPassword123

# Other Docker services
REDIS_HOST=redis
REDIS_PORT=6379

# Grafana (for monitoring)
GRAFANA_PASSWORD=admin123

# =============================================================================
# EXTERNAL INTEGRATIONS
# =============================================================================
# Azure/AWS configuration (if using cloud services)
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection-string
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# =============================================================================
# CUSTOM CONFIGURATION
# =============================================================================
# Add any custom environment variables here
COMPANY_NAME=Your Company Name
ENVIRONMENT=development
VERSION=1.0.0