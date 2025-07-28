"""
FastAPI Endpoints for Smart Feedback Analysis Platform
Provides REST API access to feedback analysis functionality
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Query, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.automation.pipeline import FeedbackAnalysisPipeline
from src.database.connection import DatabaseHandler
from src.data_processing.sentiment_analyzer import SentimentAnalyzer
from src.data_processing.topic_extractor import TopicExtractor
from src.utils.helpers import calculate_business_metrics, generate_summary_report

# Pydantic Models for API
class FeedbackCreate(BaseModel):
    customer_id: str = Field(..., description="Customer identifier")
    feedback_text: str = Field(..., description="Feedback text content")
    source: str = Field(..., description="Feedback source (email, survey, etc.)")
    product_category: Optional[str] = Field(None, description="Product category")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5)")

class FeedbackResponse(BaseModel):
    feedback_id: int
    customer_id: str
    feedback_text: str
    source: str
    timestamp: datetime
    product_category: Optional[str]
    rating: Optional[int]

class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    vader_weight: Optional[float] = Field(0.6, ge=0, le=1, description="VADER weight")
    textblob_weight: Optional[float] = Field(0.4, ge=0, le=1, description="TextBlob weight")

class SentimentAnalysisResponse(BaseModel):
    score: float
    label: str
    confidence: float
    vader_compound: float
    textblob_polarity: float
    subjectivity: float

class BatchSentimentRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze")
    batch_size: Optional[int] = Field(1000, description="Batch processing size")

class TopicExtractionRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts for topic extraction")
    n_topics: Optional[int] = Field(10, description="Number of topics to extract")

class PipelineRunRequest(BaseModel):
    batch_size: Optional[int] = Field(1000, description="Processing batch size")
    force_reprocess: Optional[bool] = Field(False, description="Force reprocessing of existing data")

class DashboardMetrics(BaseModel):
    total_feedback: int
    unique_customers: int
    avg_sentiment: float
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    top_topics: List[Dict[str, Any]]
    recent_trends: List[Dict[str, Any]]

# Initialize FastAPI app
app = FastAPI(
    title="Smart Feedback Analysis Platform API",
    description="RESTful API for customer feedback sentiment analysis and topic extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration and handlers
config = {}
db_handler = None
sentiment_analyzer = None
topic_extractor = None
pipeline = None

def load_config():
    """Load configuration from file"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}

def get_db_handler():
    """Dependency to get database handler"""
    global db_handler, config
    if not db_handler:
        if not config:
            config = load_config()
        db_handler = DatabaseHandler(config=config.get('database', {}))
    return db_handler

def get_sentiment_analyzer():
    """Dependency to get sentiment analyzer"""
    global sentiment_analyzer
    if not sentiment_analyzer:
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer

def get_topic_extractor():
    """Dependency to get topic extractor"""
    global topic_extractor
    if not topic_extractor:
        topic_extractor = TopicExtractor()
    return topic_extractor

def get_pipeline():
    """Dependency to get pipeline"""
    global pipeline, config
    if not pipeline:
        if not config:
            config = load_config()
        pipeline = FeedbackAnalysisPipeline(config_dict=config)
    return pipeline

# Health Check Endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db: DatabaseHandler = Depends(get_db_handler)):
    """Detailed health check including database connectivity"""
    try:
        # Check database health
        db_health = db.health_check()
        
        # Check system resources
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            "status": "healthy" if db_health.get("connection", False) else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_health,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Feedback Management Endpoints
@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def create_feedback(
    feedback: FeedbackCreate,
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Create new feedback entry"""
    try:
        # Create DataFrame for database insertion
        df = pd.DataFrame([{
            'customer_id': feedback.customer_id,
            'feedback_text': feedback.feedback_text,
            'source': feedback.source,
            'product_category': feedback.product_category,
            'rating': feedback.rating,
            'timestamp': datetime.now()
        }])
        
        # Insert into database
        success = db.insert_dataframe(df, 'feedback')
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create feedback")
        
        # Get the created feedback (simplified - in production, get actual ID)
        return FeedbackResponse(
            feedback_id=1,  # This should be the actual generated ID
            customer_id=feedback.customer_id,
            feedback_text=feedback.feedback_text,
            source=feedback.source,
            timestamp=datetime.now(),
            product_category=feedback.product_category,
            rating=feedback.rating
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create feedback: {str(e)}")

@app.get("/feedback", tags=["Feedback"])
async def get_feedback(
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    source: Optional[str] = Query(None, description="Filter by source"),
    sentiment_label: Optional[str] = Query(None, description="Filter by sentiment label"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Get feedback with optional filtering"""
    try:
        # Build query with filters
        query = """
        SELECT f.*, sa.sentiment_score, sa.sentiment_label, sa.confidence_score
        FROM feedback f
        LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE 1=1
        """
        params = {}
        
        if source:
            query += " AND f.source = :source"
            params['source'] = source
            
        if sentiment_label:
            query += " AND sa.sentiment_label = :sentiment_label"
            params['sentiment_label'] = sentiment_label
        
        query += " ORDER BY f.timestamp DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
        params['offset'] = offset
        params['limit'] = limit
        
        result = db.execute_query(query, params)
        
        return {
            "total": len(result),
            "data": result.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")

# Sentiment Analysis Endpoints
@app.post("/analyze/sentiment", response_model=SentimentAnalysisResponse, tags=["Analysis"])
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
):
    """Analyze sentiment of a single text"""
    try:
        result = analyzer.analyze_sentiment(
            request.text,
            vader_weight=request.vader_weight,
            textblob_weight=request.textblob_weight
        )
        
        return SentimentAnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@app.post("/analyze/sentiment/batch", tags=["Analysis"])
async def analyze_sentiment_batch(
    request: BatchSentimentRequest,
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
):
    """Analyze sentiment for multiple texts"""
    try:
        if len(request.texts) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 texts per batch")
        
        results_df = analyzer.analyze_batch(request.texts, batch_size=request.batch_size)
        
        return {
            "total_processed": len(results_df),
            "results": results_df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch sentiment analysis failed: {str(e)}")

# Topic Analysis Endpoints
@app.post("/analyze/topics", tags=["Analysis"])
async def extract_topics(
    request: TopicExtractionRequest,
    extractor: TopicExtractor = Depends(get_topic_extractor)
):
    """Extract topics from multiple texts"""
    try:
        if len(request.texts) > 10000:
            raise HTTPException(status_code=400, detail="Maximum 10000 texts for topic extraction")
        
        # Extract topics
        topics = extractor.extract_topics_kmeans(request.texts, n_topics=request.n_topics)
        
        # Assign topics to documents
        document_topics = extractor.assign_topics_to_documents(request.texts, topics)
        
        # Generate summary
        summary = extractor.generate_topic_summary(topics, document_topics)
        
        return {
            "topics": topics,
            "document_assignments": document_topics,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic extraction failed: {str(e)}")

# Pipeline Management Endpoints
@app.post("/pipeline/run", tags=["Pipeline"])
async def run_pipeline(
    background_tasks: BackgroundTasks,
    request: PipelineRunRequest = Body(...),
    pipeline_instance: FeedbackAnalysisPipeline = Depends(get_pipeline)
):
    """Run the feedback analysis pipeline"""
    try:
        # Run pipeline in background
        def run_pipeline_task():
            return pipeline_instance.run_full_pipeline()
        
        background_tasks.add_task(run_pipeline_task)
        
        return {
            "message": "Pipeline started",
            "timestamp": datetime.now().isoformat(),
            "batch_size": request.batch_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")

@app.get("/pipeline/status", tags=["Pipeline"])
async def get_pipeline_status(
    pipeline_instance: FeedbackAnalysisPipeline = Depends(get_pipeline)
):
    """Get pipeline status and last run statistics"""
    try:
        status = pipeline_instance.get_pipeline_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")

# Dashboard and Metrics Endpoints
@app.get("/dashboard/metrics", response_model=DashboardMetrics, tags=["Dashboard"])
async def get_dashboard_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Get dashboard metrics for specified time period"""
    try:
        # Get dashboard data
        dashboard_data = db.get_dashboard_data()
        
        if 'error' in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data['error'])
        
        # Extract metrics
        overall_metrics = dashboard_data.get('overall_metrics', {})
        topic_summary = dashboard_data.get('topic_summary', pd.DataFrame())
        sentiment_trends = dashboard_data.get('sentiment_trends', pd.DataFrame())
        
        return DashboardMetrics(
            total_feedback=overall_metrics.get('total_feedback', 0),
            unique_customers=overall_metrics.get('unique_customers', 0) if 'unique_customers' in overall_metrics else 0,
            avg_sentiment=round(overall_metrics.get('avg_sentiment', 0), 3),
            positive_percentage=round(overall_metrics.get('positive_count', 0) / max(overall_metrics.get('total_feedback', 1), 1) * 100, 1),
            negative_percentage=round(overall_metrics.get('negative_count', 0) / max(overall_metrics.get('total_feedback', 1), 1) * 100, 1),
            neutral_percentage=round(overall_metrics.get('neutral_count', 0) / max(overall_metrics.get('total_feedback', 1), 1) * 100, 1),
            top_topics=topic_summary.head(5).to_dict('records') if not topic_summary.empty else [],
            recent_trends=sentiment_trends.tail(7).to_dict('records') if not sentiment_trends.empty else []
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")

@app.get("/dashboard/trends", tags=["Dashboard"])
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Get sentiment trends over time"""
    try:
        trends = db.get_sentiment_trends(days=days)
        return {
            "period_days": days,
            "data": trends.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment trends: {str(e)}")

@app.get("/dashboard/topics", tags=["Dashboard"])
async def get_topic_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    min_mentions: int = Query(3, ge=1, description="Minimum mentions to include topic"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Get topic analysis summary"""
    try:
        topics = db.get_topic_summary(days=days)
        
        # Filter by minimum mentions
        filtered_topics = topics[topics['mention_count'] >= min_mentions]
        
        return {
            "period_days": days,
            "total_topics": len(filtered_topics),
            "data": filtered_topics.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topic summary: {str(e)}")

# Export Endpoints
@app.get("/export/feedback", tags=["Export"])
async def export_feedback(
    format: str = Query("csv", regex="^(csv|json|excel)$", description="Export format"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Export feedback data in specified format"""
    try:
        # Get feedback data
        query = """
        SELECT f.*, sa.sentiment_score, sa.sentiment_label, sa.confidence_score
        FROM feedback f
        LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE f.timestamp >= DATEADD(day, -:days, GETDATE())
        ORDER BY f.timestamp DESC
        """
        
        data = db.execute_query(query, {'days': days})
        
        if format == "csv":
            return JSONResponse({
                "format": "csv",
                "data": data.to_csv(index=False),
                "total_records": len(data)
            })
        elif format == "json":
            return JSONResponse({
                "format": "json", 
                "data": data.to_dict('records'),
                "total_records": len(data)
            })
        elif format == "excel":
            # For Excel, you'd typically return a file download
            return JSONResponse({
                "format": "excel",
                "message": "Excel export would be implemented as file download",
                "total_records": len(data)
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Statistics Endpoints
@app.get("/stats/summary", tags=["Statistics"])
async def get_summary_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: DatabaseHandler = Depends(get_db_handler)
):
    """Get summary statistics"""
    try:
        # Get recent data
        query = """
        SELECT f.*, sa.sentiment_score, sa.sentiment_label, sa.confidence_score
        FROM feedback f
        LEFT JOIN sentiment_analysis sa ON f.feedback_id = sa.feedback_id
        WHERE f.timestamp >= DATEADD(day, -:days, GETDATE())
        """
        
        data = db.execute_query(query, {'days': days})
        
        if data.empty:
            return {"message": "No data found for the specified period"}
        
        # Calculate business metrics
        metrics = calculate_business_metrics(data)
        
        return {
            "period_days": days,
            "summary": metrics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary stats: {str(e)}")

# Configuration Endpoints
@app.get("/config", tags=["Configuration"])
async def get_config():
    """Get current configuration (sensitive values masked)"""
    try:
        if not config:
            config_data = load_config()
        else:
            config_data = config
        
        # Mask sensitive values
        masked_config = {}
        for key, value in config_data.items():
            if isinstance(value, dict):
                masked_config[key] = {}
                for sub_key, sub_value in value.items():
                    if any(sensitive in sub_key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                        masked_config[key][sub_key] = "***MASKED***"
                    else:
                        masked_config[key][sub_key] = sub_value
            else:
                masked_config[key] = value
        
        return masked_config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

# Initialize configuration on startup
@app.on_event("startup")
async def startup_event():
    """Initialize configuration and connections on startup"""
    global config
    config = load_config()
    
    # Verify critical components
    try:
        get_db_handler()
        get_sentiment_analyzer()
        get_topic_extractor()
        print("✅ API initialized successfully")
    except Exception as e:
        print(f"⚠️ API initialization warning: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Load configuration for development
    config = load_config()
    api_config = config.get('api', {})
    
    uvicorn.run(
        "endpoints:app",
        host=api_config.get('host', '0.0.0.0'),
        port=api_config.get('port', 8000),
        reload=api_config.get('debug', False)
    )