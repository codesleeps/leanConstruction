"""
ML API Routes - Phase 2 Core AI Features

Provides REST API endpoints for:
- Computer Vision Progress Monitoring
- Waste Detection (DOWNTIME Framework)
- Predictive Analytics (Schedule & Cost)
- Automated Reporting
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import io
import json

# ML module imports
from ..ml import (
    # Computer Vision
    ProgressMonitoringPipeline,
    SafetyComplianceDetector,
    EquipmentTracker,
    WorkplaceOrganizationAnalyzer,
    
    # Waste Detection
    WasteDetectionEngine,
    WasteType,
    
    # Predictive Models
    IntegratedForecastingSystem,
    
    # Reporting
    AutomatedReportingSystem,
    ReportType,
    ReportFormat,
    generate_project_report
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Initialize ML components (lazy loading in production)
_progress_pipeline = None
_safety_detector = None
_equipment_tracker = None
_workplace_analyzer = None
_waste_engine = None
_forecast_system = None
_reporting_system = None


def get_progress_pipeline():
    """Lazy load progress monitoring pipeline"""
    global _progress_pipeline
    if _progress_pipeline is None:
        _progress_pipeline = ProgressMonitoringPipeline()
    return _progress_pipeline


def get_safety_detector():
    """Lazy load safety detector"""
    global _safety_detector
    if _safety_detector is None:
        _safety_detector = SafetyComplianceDetector()
    return _safety_detector


def get_waste_engine():
    """Lazy load waste detection engine"""
    global _waste_engine
    if _waste_engine is None:
        _waste_engine = WasteDetectionEngine()
    return _waste_engine


def get_forecast_system():
    """Lazy load forecasting system"""
    global _forecast_system
    if _forecast_system is None:
        _forecast_system = IntegratedForecastingSystem()
    return _forecast_system


def get_reporting_system():
    """Lazy load reporting system"""
    global _reporting_system
    if _reporting_system is None:
        _reporting_system = AutomatedReportingSystem()
    return _reporting_system


# ============================================
# Request/Response Models
# ============================================

class ProgressAnalysisRequest(BaseModel):
    """Request model for progress analysis"""
    project_id: str = Field(..., description="Project identifier")
    include_activities: bool = Field(True, description="Include activity detection")
    include_safety: bool = Field(False, description="Include safety analysis")


class ProgressAnalysisResponse(BaseModel):
    """Response model for progress analysis"""
    status: str
    project_id: str
    analysis: Dict[str, Any]
    timestamp: str


class WasteAnalysisRequest(BaseModel):
    """Request model for waste analysis"""
    project_id: str = Field(..., description="Project identifier")
    data: Dict[str, Any] = Field(..., description="Project data for analysis")
    include_recommendations: bool = Field(True, description="Include action recommendations")


class WasteAnalysisResponse(BaseModel):
    """Response model for waste analysis"""
    status: str
    project_id: str
    analysis: Dict[str, Any]
    timestamp: str


class ForecastRequest(BaseModel):
    """Request model for forecasting"""
    project_id: str = Field(..., description="Project identifier")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical time series data")
    project_info: Dict[str, Any] = Field(..., description="Project information")


class ForecastResponse(BaseModel):
    """Response model for forecasting"""
    status: str
    project_id: str
    forecast: Dict[str, Any]
    timestamp: str


class ReportTypeEnum(str, Enum):
    """Report type enumeration"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    executive = "executive"
    comprehensive = "comprehensive"
    waste_analysis = "waste_analysis"
    progress = "progress"
    safety = "safety"
    forecast = "forecast"


class ReportFormatEnum(str, Enum):
    """Report format enumeration"""
    json = "json"
    html = "html"
    markdown = "markdown"


class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    project_id: str = Field(..., description="Project identifier")
    project_data: Dict[str, Any] = Field(..., description="Project data for report")
    report_type: ReportTypeEnum = Field(ReportTypeEnum.daily, description="Type of report")
    output_format: ReportFormatEnum = Field(ReportFormatEnum.json, description="Output format")


class ReportScheduleRequest(BaseModel):
    """Request model for report scheduling"""
    project_id: str = Field(..., description="Project identifier")
    report_type: ReportTypeEnum = Field(..., description="Type of report")
    schedule: str = Field("daily", description="Schedule: daily, weekly, monthly")
    recipients: List[str] = Field(default_factory=list, description="Email recipients")


# ============================================
# Computer Vision Endpoints
# ============================================

@router.post("/analyze-progress", response_model=ProgressAnalysisResponse)
async def analyze_progress(
    file: UploadFile = File(...),
    project_id: str = "default",
    include_activities: bool = True,
    include_safety: bool = False
):
    """
    Analyze construction progress from site image
    
    - **file**: Site image (JPEG, PNG)
    - **project_id**: Project identifier for tracking
    - **include_activities**: Include activity detection
    - **include_safety**: Include safety compliance check
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # Get pipeline
        pipeline = get_progress_pipeline()
        
        # Analyze image
        result = pipeline.analyze_image(image_data)
        
        # Add safety analysis if requested
        if include_safety:
            safety_detector = get_safety_detector()
            safety_result = safety_detector.analyze(image_data)
            result['safety_analysis'] = safety_result
        
        return ProgressAnalysisResponse(
            status="success",
            project_id=project_id,
            analysis=result,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Progress analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-safety")
async def analyze_safety(
    file: UploadFile = File(...),
    project_id: str = "default"
):
    """
    Analyze safety compliance from site image
    
    - **file**: Site image (JPEG, PNG)
    - **project_id**: Project identifier
    """
    try:
        image_data = await file.read()
        
        detector = get_safety_detector()
        result = detector.analyze(image_data)
        
        return {
            "status": "success",
            "project_id": project_id,
            "safety_analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Safety analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-5s")
async def analyze_workplace_organization(
    file: UploadFile = File(...),
    project_id: str = "default"
):
    """
    Analyze 5S workplace organization from site image
    
    - **file**: Site image (JPEG, PNG)
    - **project_id**: Project identifier
    """
    try:
        image_data = await file.read()
        
        global _workplace_analyzer
        if _workplace_analyzer is None:
            _workplace_analyzer = WorkplaceOrganizationAnalyzer()
        
        result = _workplace_analyzer.analyze_5s(image_data)
        
        return {
            "status": "success",
            "project_id": project_id,
            "workplace_analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"5S analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Waste Detection Endpoints
# ============================================

@router.post("/analyze-waste", response_model=WasteAnalysisResponse)
async def analyze_waste(request: WasteAnalysisRequest):
    """
    Analyze project for lean wastes (DOWNTIME framework)
    
    Detects 8 types of waste:
    - Defects
    - Overproduction
    - Waiting
    - Non-utilized Talent
    - Transportation
    - Inventory
    - Motion
    - Extra Processing
    """
    try:
        engine = get_waste_engine()
        
        result = engine.analyze(request.data)
        
        # Remove recommendations if not requested
        if not request.include_recommendations:
            result.pop('priority_actions', None)
        
        return WasteAnalysisResponse(
            status="success",
            project_id=request.project_id,
            analysis=result,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Waste analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/waste-types")
async def get_waste_types():
    """
    Get information about DOWNTIME waste types
    """
    waste_info = {
        "framework": "DOWNTIME",
        "description": "8 types of lean construction waste",
        "wastes": [
            {
                "code": "D",
                "name": "Defects",
                "description": "Quality issues requiring rework or repair"
            },
            {
                "code": "O",
                "name": "Overproduction",
                "description": "Producing more than needed or before needed"
            },
            {
                "code": "W",
                "name": "Waiting",
                "description": "Idle time waiting for materials, information, or equipment"
            },
            {
                "code": "N",
                "name": "Non-utilized Talent",
                "description": "Underutilizing worker skills and knowledge"
            },
            {
                "code": "T",
                "name": "Transportation",
                "description": "Unnecessary movement of materials or equipment"
            },
            {
                "code": "I",
                "name": "Inventory",
                "description": "Excess materials or supplies on site"
            },
            {
                "code": "M",
                "name": "Motion",
                "description": "Unnecessary movement of workers"
            },
            {
                "code": "E",
                "name": "Extra Processing",
                "description": "Over-engineering or redundant work"
            }
        ]
    }
    
    return waste_info


# ============================================
# Forecasting Endpoints
# ============================================

@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Generate schedule and cost forecasts
    
    Uses LSTM for schedule forecasting and ensemble methods for cost prediction.
    """
    try:
        system = get_forecast_system()
        
        # Prepare project data
        project_data = {
            **request.project_info,
            'project_id': request.project_id
        }
        
        if request.historical_data:
            project_data['historical_data'] = request.historical_data
        
        result = system.generate_forecast(project_data)
        
        return ForecastResponse(
            status="success",
            project_id=request.project_id,
            forecast=result,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/schedule")
async def forecast_schedule(request: ForecastRequest):
    """
    Generate schedule forecast only
    """
    try:
        system = get_forecast_system()
        
        project_data = {
            **request.project_info,
            'project_id': request.project_id
        }
        
        if request.historical_data:
            project_data['historical_data'] = request.historical_data
        
        result = system.schedule_model.predict(project_data)
        
        return {
            "status": "success",
            "project_id": request.project_id,
            "schedule_forecast": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Schedule forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/cost")
async def forecast_cost(request: ForecastRequest):
    """
    Generate cost forecast only
    """
    try:
        system = get_forecast_system()
        
        project_data = {
            **request.project_info,
            'project_id': request.project_id
        }
        
        if request.historical_data:
            project_data['historical_data'] = request.historical_data
        
        result = system.cost_model.predict(project_data)
        
        return {
            "status": "success",
            "project_id": request.project_id,
            "cost_forecast": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Cost forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Reporting Endpoints
# ============================================

@router.post("/reports/generate")
async def generate_report(request: ReportGenerationRequest):
    """
    Generate a construction analytics report
    
    Report types: daily, weekly, monthly, executive, comprehensive
    Output formats: json, html, markdown
    """
    try:
        system = get_reporting_system()
        
        # Map enum values
        report_type_map = {
            "daily": ReportType.DAILY,
            "weekly": ReportType.WEEKLY,
            "monthly": ReportType.MONTHLY,
            "executive": ReportType.EXECUTIVE,
            "comprehensive": ReportType.COMPREHENSIVE,
            "waste_analysis": ReportType.WASTE_ANALYSIS,
            "progress": ReportType.PROGRESS,
            "safety": ReportType.SAFETY,
            "forecast": ReportType.FORECAST
        }
        
        format_map = {
            "json": ReportFormat.JSON,
            "html": ReportFormat.HTML,
            "markdown": ReportFormat.MARKDOWN
        }
        
        # Add project_id to data
        project_data = {
            **request.project_data,
            'project_id': request.project_id
        }
        
        report = system.generate_report(
            project_data,
            report_type=report_type_map[request.report_type],
            output_format=format_map[request.output_format]
        )
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate/html", response_class=HTMLResponse)
async def generate_html_report(request: ReportGenerationRequest):
    """
    Generate HTML report and return as renderable HTML
    """
    try:
        system = get_reporting_system()
        
        report_type_map = {
            "daily": ReportType.DAILY,
            "weekly": ReportType.WEEKLY,
            "monthly": ReportType.MONTHLY,
            "executive": ReportType.EXECUTIVE,
            "comprehensive": ReportType.COMPREHENSIVE,
            "waste_analysis": ReportType.WASTE_ANALYSIS,
            "progress": ReportType.PROGRESS,
            "safety": ReportType.SAFETY,
            "forecast": ReportType.FORECAST
        }
        
        project_data = {
            **request.project_data,
            'project_id': request.project_id
        }
        
        report = system.generate_report(
            project_data,
            report_type=report_type_map[request.report_type],
            output_format=ReportFormat.HTML
        )
        
        return report.get('html_content', '<html><body>Report generation error</body></html>')
    
    except Exception as e:
        logger.error(f"HTML report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/schedule")
async def schedule_report(request: ReportScheduleRequest):
    """
    Schedule automated report generation
    """
    try:
        system = get_reporting_system()
        
        report_type_map = {
            "daily": ReportType.DAILY,
            "weekly": ReportType.WEEKLY,
            "monthly": ReportType.MONTHLY,
            "executive": ReportType.EXECUTIVE,
            "comprehensive": ReportType.COMPREHENSIVE,
            "waste_analysis": ReportType.WASTE_ANALYSIS,
            "progress": ReportType.PROGRESS,
            "safety": ReportType.SAFETY,
            "forecast": ReportType.FORECAST
        }
        
        schedule_config = system.schedule_report(
            project_id=request.project_id,
            report_type=report_type_map[request.report_type],
            schedule=request.schedule,
            recipients=request.recipients
        )
        
        return {
            "status": "success",
            "schedule": schedule_config,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Report scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/history")
async def get_report_history(
    project_id: Optional[str] = None,
    report_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get report generation history
    """
    try:
        system = get_reporting_system()
        
        rt = None
        if report_type:
            report_type_map = {
                "daily": ReportType.DAILY,
                "weekly": ReportType.WEEKLY,
                "monthly": ReportType.MONTHLY,
                "executive": ReportType.EXECUTIVE,
                "comprehensive": ReportType.COMPREHENSIVE
            }
            rt = report_type_map.get(report_type)
        
        history = system.get_report_history(
            project_id=project_id,
            report_type=rt,
            limit=limit
        )
        
        return {
            "status": "success",
            "history": history,
            "count": len(history)
        }
    
    except Exception as e:
        logger.error(f"Report history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/types")
async def get_report_types():
    """
    Get available report types and their descriptions
    """
    return {
        "report_types": [
            {
                "type": "daily",
                "name": "Daily Report",
                "description": "Daily progress and safety summary",
                "sections": ["progress", "safety"]
            },
            {
                "type": "weekly",
                "name": "Weekly Report",
                "description": "Weekly comprehensive review",
                "sections": ["progress", "waste", "safety", "workplace"]
            },
            {
                "type": "monthly",
                "name": "Monthly Report",
                "description": "Monthly full analysis with forecasting",
                "sections": ["progress", "waste", "forecast", "safety", "workplace"]
            },
            {
                "type": "executive",
                "name": "Executive Report",
                "description": "High-level summary for management",
                "sections": ["progress", "forecast"]
            },
            {
                "type": "comprehensive",
                "name": "Comprehensive Report",
                "description": "Full analysis including all sections",
                "sections": ["progress", "waste", "forecast", "safety", "workplace"]
            }
        ],
        "output_formats": ["json", "html", "markdown"]
    }


# ============================================
# Health Check & Status
# ============================================

@router.get("/health")
async def ml_health_check():
    """
    Check ML module health status
    """
    status = {
        "status": "healthy",
        "modules": {
            "computer_vision": "available",
            "waste_detection": "available",
            "forecasting": "available",
            "reporting": "available"
        },
        "version": "2.0.0",
        "phase": "Phase 2 - Beta",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return status


@router.get("/models/info")
async def get_model_info():
    """
    Get information about ML models
    """
    return {
        "models": {
            "progress_monitoring": {
                "architecture": "ResNet-50 with CBAM attention",
                "input": "224x224 RGB images",
                "output": "13 construction stages + confidence",
                "status": "ready"
            },
            "waste_detection": {
                "framework": "DOWNTIME",
                "methods": ["IsolationForest", "Statistical analysis", "Rule-based"],
                "waste_types": 8,
                "status": "ready"
            },
            "schedule_forecasting": {
                "architecture": "Bidirectional LSTM with attention",
                "features": "Time series + project features",
                "output": "Completion date + confidence interval",
                "status": "ready"
            },
            "cost_forecasting": {
                "architecture": "Stacking ensemble",
                "base_models": ["Random Forest", "Gradient Boosting", "Ridge", "ElasticNet"],
                "output": "Cost prediction + variance",
                "status": "ready"
            }
        },
        "phase": "Phase 2 Core AI Development",
        "version": "2.0.0-beta"
    }