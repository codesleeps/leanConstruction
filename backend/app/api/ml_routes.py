"""
ML API Routes - Phase 2, 3 & 4 AI Features

Provides REST API endpoints for:
- Computer Vision Progress Monitoring
- Waste Detection (DOWNTIME Framework)
- Predictive Analytics (Schedule & Cost)
- Automated Reporting
- Lean Tools (VSM, 5S, Kaizen, Kanban, A3)
- NLP Document Analysis
- Resource Optimization
- Real-time Alerting
- ERP Integrations
- IoT Sensor Data
- Model Fine-tuning & A/B Testing (Phase 4)
- Analytics & Business Intelligence (Phase 4)
- Industry Customizations (Phase 4)
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
    generate_project_report,
    
    # Phase 3 - Lean Tools
    lean_tools,
    ValueStreamMapper,
    S5AnalysisSystem,
    KaizenManager,
    KaizenType,
    KanbanStatus,
    
    # Phase 3 - NLP
    nlp_system,
    DocumentType,
    
    # Phase 3 - Resource Optimization
    resource_optimizer,
    
    # Phase 3 - Alerting
    alerting_system,
    AlertSeverity,
    AlertCategory,
    AlertStatus,
    
    # Phase 4 - Model Fine-tuning
    finetuning_system,
    FeedbackType,
    ModelStatus,
    ABTestStatus,
    
    # Phase 4 - Analytics & BI
    analytics_bi_system,
    KPICategory,
    TrendPeriod,
    BenchmarkType,
    WidgetType,
    
    # Phase 4 - Industry Customizations
    industry_customization_system,
    IndustrySector
)

# Integration imports
from ..integrations import (
    erp_manager,
    ERPSystem,
    DataEntity,
    iot_system,
    SensorType,
    ConstructionSensorPresets
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
            "reporting": "available",
            "lean_tools": "available",
            "nlp_analysis": "available",
            "resource_optimization": "available",
            "alerting": "available",
            "model_finetuning": "available",
            "analytics_bi": "available",
            "industry_customizations": "available"
        },
        "version": "4.0.0",
        "phase": "Phase 4 - Production Ready",
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
        "phase": "Phase 4 Production Ready",
        "version": "4.0.0"
    }
    
    
    # ============================================
    # Phase 3 - Lean Tools Endpoints
    # ============================================
    
    @router.post("/lean/vsm/analyze")
    async def analyze_value_stream(
        process_data: List[Dict[str, Any]],
        customer_demand_rate: float = 0
    ):
        """
        Analyze value stream and identify wastes
        
        - **process_data**: List of process steps with times and types
        - **customer_demand_rate**: Customer demand rate (units per day)
        """
        try:
            vsm = lean_tools.vsm
            vsm.customer_demand_rate = customer_demand_rate
            vsm.create_from_data(process_data)
            
            metrics = vsm.analyze_current_state()
            future_state = vsm.generate_future_state()
            
            return {
                "status": "success",
                "current_state": vsm.current_state_map,
                "future_state": future_state,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"VSM analysis error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/lean/5s/assessment")
    async def conduct_5s_assessment(
        area_id: str,
        area_name: str,
        scores: Dict[str, float],
        assessor: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Conduct 5S workplace assessment
        
        - **area_id**: Unique area identifier
        - **area_name**: Name of work area
        - **scores**: Dictionary of criterion_id -> score (0-100)
        """
        try:
            result = lean_tools.s5_system.conduct_assessment(
                area_id=area_id,
                area_name=area_name,
                scores=scores,
                assessor=assessor,
                notes=notes
            )
            
            return {
                "status": "success",
                "assessment": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"5S assessment error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/lean/5s/improvement-plan/{assessment_id}")
    async def get_5s_improvement_plan(assessment_id: str):
        """Get detailed improvement plan from 5S assessment"""
        try:
            plan = lean_tools.s5_system.get_improvement_plan(assessment_id)
            return {"status": "success", "improvement_plan": plan}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/lean/kaizen/create")
    async def create_kaizen_event(
        title: str,
        kaizen_type: str,
        target_area: str,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        team_members: List[str],
        duration_days: int = 5
    ):
        """Create a Kaizen improvement event"""
        try:
            kaizen_types = {
                "point": KaizenType.POINT,
                "system": KaizenType.SYSTEM,
                "line": KaizenType.LINE,
                "plane": KaizenType.PLANE,
                "cube": KaizenType.CUBE
            }
            
            event = lean_tools.kaizen_manager.create_event(
                title=title,
                kaizen_type=kaizen_types.get(kaizen_type, KaizenType.POINT),
                target_area=target_area,
                current_state=current_state,
                target_state=target_state,
                team_members=team_members,
                duration_days=duration_days
            )
            
            return {
                "status": "success",
                "event_id": event.id,
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "expected_savings": event.expected_savings,
                    "start_date": event.start_date.isoformat(),
                    "end_date": event.end_date.isoformat()
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/lean/kaizen/dashboard")
    async def get_kaizen_dashboard():
        """Get Kaizen events dashboard"""
        try:
            dashboard = lean_tools.kaizen_manager.get_event_dashboard()
            return {"status": "success", "dashboard": dashboard}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/lean/kanban/board/create")
    async def create_kanban_board(
        board_id: str,
        name: str,
        wip_limits: Optional[Dict[str, int]] = None
    ):
        """Create a Kanban board"""
        try:
            board = lean_tools.create_kanban_board(board_id, name, wip_limits)
            return {
                "status": "success",
                "board_id": board.board_id,
                "name": board.name,
                "wip_limits": board.wip_limits
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/lean/kanban/{board_id}/card")
    async def create_kanban_card(
        board_id: str,
        title: str,
        description: str,
        priority: int = 3,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """Create a Kanban card"""
        try:
            board = lean_tools.kanban_boards.get(board_id)
            if not board:
                raise HTTPException(status_code=404, detail="Board not found")
            
            card = board.create_card(
                title=title,
                description=description,
                priority=priority,
                assignee=assignee,
                tags=tags or []
            )
            
            return {
                "status": "success",
                "card_id": card.id,
                "card": {
                    "id": card.id,
                    "title": card.title,
                    "status": card.status.value
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/lean/kanban/{board_id}")
    async def get_kanban_board(board_id: str):
        """Get Kanban board state"""
        try:
            board = lean_tools.kanban_boards.get(board_id)
            if not board:
                raise HTTPException(status_code=404, detail="Board not found")
            
            return {"status": "success", "board": board.get_board_state()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/lean/metrics")
    async def get_lean_metrics():
        """Get summary of all Lean metrics"""
        try:
            metrics = lean_tools.get_lean_metrics_summary()
            return {"status": "success", "metrics": metrics}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================
    # Phase 3 - NLP Endpoints
    # ============================================
    
    @router.post("/nlp/analyze-document")
    async def analyze_document(
        text: str,
        include_entities: bool = True,
        include_sentiment: bool = True,
        include_summary: bool = True
    ):
        """
        Comprehensive NLP analysis of construction document
        
        - **text**: Document text content
        - **include_entities**: Include named entity extraction
        - **include_sentiment**: Include sentiment analysis
        - **include_summary**: Include document summary
        """
        try:
            result = nlp_system.analyze_document(text)
            
            # Filter based on parameters
            if not include_entities:
                result.pop('entities', None)
            if not include_sentiment:
                result.pop('sentiment', None)
            if not include_summary:
                result.pop('summary', None)
                result.pop('key_points', None)
            
            return {"status": "success", "analysis": result}
        except Exception as e:
            logger.error(f"NLP analysis error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/nlp/classify")
    async def classify_document(text: str):
        """
        Classify construction document type
        
        Returns document type (RFI, submittal, change order, etc.)
        """
        try:
            classification = nlp_system.classifier.classify(text)
            return {
                "status": "success",
                "classification": {
                    "document_type": classification.document_type.value,
                    "confidence": classification.confidence,
                    "secondary_type": classification.secondary_type.value if classification.secondary_type else None,
                    "keywords": classification.keywords
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/nlp/extract-entities")
    async def extract_entities(text: str):
        """Extract named entities from text"""
        try:
            entities = nlp_system.ner.extract_entities(text)
            return {
                "status": "success",
                "entities": [
                    {
                        "text": e.text,
                        "type": e.entity_type.value,
                        "confidence": e.confidence
                    }
                    for e in entities
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/nlp/analyze-sentiment")
    async def analyze_sentiment(text: str):
        """Analyze communication sentiment and urgency"""
        try:
            sentiment = nlp_system.sentiment_analyzer.analyze_sentiment(text)
            urgency = nlp_system.sentiment_analyzer.analyze_urgency(text)
            
            return {
                "status": "success",
                "sentiment": {
                    "level": sentiment.sentiment.value,
                    "score": sentiment.score,
                    "positive_indicators": sentiment.positive_indicators,
                    "negative_indicators": sentiment.negative_indicators
                },
                "urgency": urgency.value
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/nlp/extract-risks")
    async def extract_risks(text: str):
        """Extract risks and action items from document"""
        try:
            risks = nlp_system.risk_extractor.extract_risks(text)
            actions = nlp_system.risk_extractor.extract_action_items(text)
            
            return {
                "status": "success",
                "risks": [
                    {
                        "description": r.description,
                        "category": r.category,
                        "severity": r.severity,
                        "confidence": r.confidence
                    }
                    for r in risks
                ],
                "action_items": [
                    {
                        "description": a.description,
                        "assignee": a.assignee,
                        "due_date": a.due_date,
                        "priority": a.priority
                    }
                    for a in actions
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/nlp/analyze-contract")
    async def analyze_contract(text: str):
        """Analyze contract document for key clauses and risks"""
        try:
            analysis = nlp_system.contract_analyzer.analyze_contract(text)
            return {"status": "success", "analysis": analysis}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================
    # Phase 3 - Resource Optimization Endpoints
    # ============================================
    
    @router.post("/optimization/optimize-resources")
    async def optimize_resources(project_data: Dict[str, Any]):
        """
        Comprehensive resource optimization
        
        - **project_data**: Project data including workers, tasks, equipment, deliveries
        """
        try:
            result = resource_optimizer.optimize_project_resources(project_data)
            return {"status": "success", "optimization": result}
        except Exception as e:
            logger.error(f"Resource optimization error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/optimization/schedule-crew")
    async def schedule_crew(
        workers: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        objective: str = "minimize_cost"
    ):
        """
        Optimize crew scheduling
        
        - **workers**: List of workers with skills and rates
        - **tasks**: List of tasks with requirements
        - **objective**: minimize_cost, minimize_duration, balance_workload
        """
        try:
            optimizer = resource_optimizer.crew_optimizer
            
            # Add workers and tasks
            from ..ml.resource_optimizer import Resource, Task, ResourceType, SkillType, OptimizationObjective
            
            for w in workers:
                optimizer.add_worker(Resource(
                    id=w['id'],
                    name=w['name'],
                    resource_type=ResourceType.LABOR,
                    capacity=1,
                    cost_per_unit=w.get('hourly_rate', 50),
                    skills=[SkillType(s) for s in w.get('skills', [])]
                ))
            
            for t in tasks:
                optimizer.add_task(Task(
                    id=t['id'],
                    name=t['name'],
                    duration=t['duration'],
                    required_resources=t.get('resources', {'labor': 1}),
                    required_skills=[SkillType(s) for s in t.get('skills', [])],
                    predecessors=t.get('predecessors', []),
                    priority=t.get('priority', 1)
                ))
            
            obj_map = {
                "minimize_cost": OptimizationObjective.MINIMIZE_COST,
                "minimize_duration": OptimizationObjective.MINIMIZE_DURATION,
                "balance_workload": OptimizationObjective.BALANCE_WORKLOAD
            }
            
            schedule = optimizer.optimize(obj_map.get(objective, OptimizationObjective.MINIMIZE_COST))
            
            return {
                "status": "success",
                "schedule": {
                    "total_cost": schedule.total_cost,
                    "total_duration": schedule.total_duration,
                    "makespan": schedule.makespan,
                    "utilization": schedule.utilization,
                    "critical_path": schedule.critical_path,
                    "assignments_count": len(schedule.assignments)
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/optimization/delivery-routes")
    async def optimize_delivery_routes(
        deliveries: List[Dict[str, Any]],
        vehicles: List[Dict[str, Any]],
        warehouse: Dict[str, float]
    ):
        """
        Optimize material delivery routes
        
        - **deliveries**: List of delivery requests
        - **vehicles**: Fleet of delivery vehicles
        - **warehouse**: Warehouse location {lat, lon}
        """
        try:
            optimizer = resource_optimizer.delivery_optimizer
            optimizer.set_warehouse(warehouse['lat'], warehouse['lon'])
            
            from ..ml.resource_optimizer import DeliveryRequest
            
            for d in deliveries:
                optimizer.add_delivery(DeliveryRequest(
                    id=d['id'],
                    material_type=d['type'],
                    quantity=d['quantity'],
                    destination=d['destination'],
                    earliest_delivery=datetime.fromisoformat(d['earliest']),
                    latest_delivery=datetime.fromisoformat(d['latest']),
                    priority=d.get('priority', 1)
                ))
            
            for v in vehicles:
                optimizer.add_vehicle(
                    v['id'],
                    v['capacity'],
                    v.get('cost_per_mile', 2.0)
                )
            
            routes = optimizer.optimize_routes()
            
            return {
                "status": "success",
                "routes": [
                    {
                        "vehicle_id": r.vehicle_id,
                        "stops": r.stops,
                        "total_distance": r.total_distance,
                        "total_time": r.total_time,
                        "deliveries": r.deliveries
                    }
                    for r in routes
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================
    # Phase 3 - Alerting Endpoints
    # ============================================
    
    @router.post("/alerts/evaluate-metrics")
    async def evaluate_metrics(
        project_id: str,
        metrics: Dict[str, float]
    ):
        """
        Evaluate project metrics and trigger alerts
        
        - **project_id**: Project identifier
        - **metrics**: Dictionary of metric values to evaluate
        """
        try:
            alerting_system.process_project_metrics(project_id, metrics)
            active_alerts = alerting_system.get_alerts(project_id=project_id)
            
            return {
                "status": "success",
                "metrics_processed": len(metrics),
                "active_alerts": len(active_alerts),
                "alerts": active_alerts[:10]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/alerts/create")
    async def create_alert(
        title: str,
        message: str,
        category: str,
        severity: str,
        source: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Create a custom alert"""
        try:
            category_map = {c.value: c for c in AlertCategory}
            severity_map = {s.value: s for s in AlertSeverity}
            
            alert = alerting_system.create_custom_alert(
                title=title,
                message=message,
                category=category_map.get(category, AlertCategory.SYSTEM),
                severity=severity_map.get(severity, AlertSeverity.MEDIUM),
                source=source,
                context=context
            )
            
            return {
                "status": "success",
                "alert_id": alert.id if alert else None,
                "created": alert is not None
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/alerts")
    async def get_alerts(
        category: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """Get active alerts with optional filtering"""
        try:
            category_map = {c.value: c for c in AlertCategory}
            severity_map = {s.value: s for s in AlertSeverity}
            status_map = {s.value: s for s in AlertStatus}
            
            alerts = alerting_system.get_alerts(
                status=status_map.get(status) if status else None,
                category=category_map.get(category) if category else None,
                severity=severity_map.get(severity) if severity else None,
                project_id=project_id
            )
            
            return {"status": "success", "alerts": alerts, "count": len(alerts)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/alerts/{alert_id}/acknowledge")
    async def acknowledge_alert(
        alert_id: str,
        user_id: str,
        note: Optional[str] = None
    ):
        """Acknowledge an alert"""
        try:
            success = alerting_system.acknowledge(alert_id, user_id, note)
            return {"status": "success" if success else "failed", "alert_id": alert_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/alerts/{alert_id}/resolve")
    async def resolve_alert(
        alert_id: str,
        user_id: str,
        resolution: Optional[str] = None
    ):
        """Resolve an alert"""
        try:
            success = alerting_system.resolve(alert_id, user_id, resolution)
            return {"status": "success" if success else "failed", "alert_id": alert_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/alerts/dashboard")
    async def get_alerts_dashboard():
        """Get alerting dashboard"""
        try:
            dashboard = alerting_system.get_dashboard()
            return {"status": "success", "dashboard": dashboard}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/alerts/statistics")
    async def get_alerts_statistics():
        """Get alert statistics"""
        try:
            stats = alerting_system.get_statistics()
            return {"status": "success", "statistics": stats}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================
    # Phase 3 - ERP Integration Endpoints
    # ============================================
    
    @router.post("/integrations/erp/connect")
    async def connect_erp(
        connection_id: str,
        system: str,
        host: str,
        port: int,
        username: str,
        password: str,
        database: Optional[str] = None,
        company_id: Optional[str] = None
    ):
        """
        Connect to an ERP system
        
        Supported systems: sap, oracle, sage, viewpoint, foundation, cmic, generic
        """
        try:
            from ..integrations import ERPConnection
            
            system_map = {s.value: s for s in ERPSystem}
            
            connection = ERPConnection(
                system=system_map.get(system, ERPSystem.GENERIC),
                host=host,
                port=port,
                username=username,
                password=password,
                database=database,
                company_id=company_id
            )
            
            success = erp_manager.register_connection(connection_id, connection)
            
            return {
                "status": "success" if success else "failed",
                "connection_id": connection_id,
                "system": system
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/integrations/erp/{connection_id}/sync/{entity}")
    async def sync_erp_entity(
        connection_id: str,
        entity: str
    ):
        """Sync specific entity from ERP"""
        try:
            entity_map = {e.value: e for e in DataEntity}
            
            result = erp_manager.sync_entity(
                connection_id,
                entity_map.get(entity, DataEntity.PROJECT)
            )
            
            return {
                "status": result.status,
                "entity": entity,
                "records_processed": result.records_processed,
                "records_created": result.records_created,
                "records_failed": result.records_failed,
                "errors": result.errors
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/erp/{connection_id}/projects")
    async def get_erp_projects(connection_id: str):
        """Get projects from ERP"""
        try:
            client = erp_manager.clients.get(connection_id)
            if not client:
                raise HTTPException(status_code=404, detail="Connection not found")
            
            projects = client.get_projects()
            return {"status": "success", "projects": projects}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/erp/{connection_id}/budget/{project_id}")
    async def get_erp_budget(connection_id: str, project_id: str):
        """Get project budget from ERP"""
        try:
            client = erp_manager.clients.get(connection_id)
            if not client:
                raise HTTPException(status_code=404, detail="Connection not found")
            
            budget = client.get_budget(project_id)
            return {"status": "success", "budget": budget}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/erp/status")
    async def get_erp_status():
        """Get ERP integration status"""
        try:
            status = erp_manager.get_sync_status()
            return {"status": "success", "erp_status": status}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================
    # Phase 3 - IoT Sensor Endpoints
    # ============================================
    
    @router.post("/integrations/iot/ingest")
    async def ingest_sensor_data(readings: List[Dict[str, Any]]):
        """
        Ingest sensor readings
        
        - **readings**: List of sensor readings with sensor_id, type, value, timestamp
        """
        try:
            iot_system.ingest_batch(readings)
            active_alerts = iot_system.get_active_alerts()
            
            return {
                "status": "success",
                "readings_processed": len(readings),
                "active_alerts": len(active_alerts)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/iot/sensor/{sensor_id}")
    async def get_sensor_data(sensor_id: str, window_minutes: int = 60):
        """Get sensor data and statistics"""
        try:
            data = iot_system.get_sensor_data(sensor_id, window_minutes)
            return {"status": "success", "sensor_data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/iot/device/{device_id}")
    async def get_device_status(device_id: str):
        """Get IoT device status and sensor readings"""
        try:
            status = iot_system.get_device_status(device_id)
            return {"status": "success", "device": status}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/iot/overview")
    async def get_iot_overview():
        """Get overview of all IoT data"""
        try:
            overview = iot_system.get_site_overview()
            return {"status": "success", "overview": overview}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get("/integrations/iot/alerts")
    async def get_iot_alerts():
        """Get active sensor threshold alerts"""
        try:
            alerts = iot_system.get_active_alerts()
            return {"status": "success", "alerts": alerts}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/integrations/iot/configure-presets/{preset_type}")
    async def configure_iot_presets(preset_type: str):
        """
        Configure sensors from presets
        
        Types: environmental, structural, safety, equipment, concrete, weather
        """
        try:
            count = iot_system.configure_presets(preset_type)
            return {
                "status": "success",
                "preset_type": preset_type,
                "sensors_configured": count
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Phase 4 - Model Fine-tuning Endpoints
# ============================================

@router.post("/finetuning/feedback")
async def submit_feedback(
    model_id: str,
    feedback_type: str,
    original_input: Dict[str, Any],
    model_output: Dict[str, Any],
    corrected_output: Optional[Dict[str, Any]] = None,
    rating: Optional[int] = None,
    comment: Optional[str] = None
):
    """
    Submit feedback for model improvement
    
    - **model_id**: ID of the model that produced the output
    - **feedback_type**: Type of feedback (correction, rating, approval, rejection, suggestion)
    - **original_input**: Input that was sent to the model
    - **model_output**: Output produced by the model
    - **corrected_output**: Corrected output (for corrections)
    - **rating**: Rating 1-5 (for ratings)
    """
    try:
        from ..ml import FeedbackType, FeedbackEntry
        
        feedback_type_map = {f.value: f for f in FeedbackType}
        
        entry = FeedbackEntry(
            id=str(uuid.uuid4()),
            model_id=model_id,
            feedback_type=feedback_type_map.get(feedback_type, FeedbackType.RATING),
            original_input=original_input,
            model_output=model_output,
            corrected_output=corrected_output,
            rating=rating,
            timestamp=datetime.utcnow(),
            user_id="api_user",
            metadata={'comment': comment} if comment else {}
        )
        
        result = finetuning_system.collect_feedback(entry)
        
        return {
            "status": "success",
            "feedback_id": entry.id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finetuning/models")
async def get_models():
    """Get all model versions"""
    try:
        versions = finetuning_system.get_model_versions()
        return {"status": "success", "models": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finetuning/models/{model_id}/performance")
async def get_model_performance(model_id: str, days: int = 30):
    """Get model performance metrics"""
    try:
        performance = finetuning_system.get_model_performance(model_id, days)
        return {"status": "success", "performance": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finetuning/ab-test")
async def create_ab_test(
    name: str,
    control_model_id: str,
    treatment_model_id: str,
    traffic_split: float = 0.5,
    duration_days: int = 14,
    success_metrics: List[str] = None
):
    """
    Create an A/B test between two model versions
    
    - **control_model_id**: Current production model
    - **treatment_model_id**: New model to test
    - **traffic_split**: Percentage of traffic for treatment (0-1)
    """
    try:
        test = finetuning_system.create_ab_test(
            name=name,
            control_model_id=control_model_id,
            treatment_model_id=treatment_model_id,
            traffic_split=traffic_split,
            duration_days=duration_days,
            success_metrics=success_metrics or ['accuracy', 'latency']
        )
        
        return {
            "status": "success",
            "test_id": test.id,
            "test": {
                "name": test.name,
                "status": test.status.value,
                "start_date": test.start_date.isoformat(),
                "end_date": test.end_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finetuning/ab-tests")
async def get_ab_tests(status: Optional[str] = None):
    """Get all A/B tests"""
    try:
        status_filter = None
        if status:
            status_map = {s.value: s for s in ABTestStatus}
            status_filter = status_map.get(status)
        
        tests = finetuning_system.get_ab_tests(status_filter)
        return {"status": "success", "tests": tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finetuning/ab-tests/{test_id}/results")
async def get_ab_test_results(test_id: str):
    """Get A/B test results"""
    try:
        results = finetuning_system.get_ab_test_results(test_id)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finetuning/trigger-retraining")
async def trigger_model_retraining(
    model_id: str,
    reason: Optional[str] = None
):
    """Trigger model retraining"""
    try:
        result = finetuning_system.trigger_retraining(model_id, reason)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finetuning/retraining-status")
async def get_retraining_status():
    """Get status of retraining triggers and jobs"""
    try:
        status = finetuning_system.get_retraining_status()
        return {"status": "success", "retraining": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Phase 4 - Analytics & BI Endpoints
# ============================================

@router.get("/analytics/kpis/{project_id}")
async def get_project_kpis(
    project_id: str,
    categories: Optional[List[str]] = None
):
    """
    Get KPIs for a project
    
    - **categories**: Filter by categories (schedule, cost, quality, safety, productivity, sustainability)
    """
    try:
        category_filter = None
        if categories:
            category_map = {c.value: c for c in KPICategory}
            category_filter = [category_map.get(c) for c in categories if c in category_map]
        
        kpis = analytics_bi_system.get_project_kpis(project_id, category_filter)
        return {"status": "success", "kpis": kpis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/kpis/calculate")
async def calculate_kpis(
    project_data: Dict[str, Any],
    kpi_ids: Optional[List[str]] = None
):
    """Calculate KPIs from project data"""
    try:
        results = analytics_bi_system.calculate_kpis(project_data, kpi_ids)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trends/{project_id}")
async def analyze_trends(
    project_id: str,
    kpi_id: str,
    period: str = "monthly"
):
    """
    Analyze trends for a KPI
    
    - **period**: daily, weekly, monthly, quarterly
    """
    try:
        period_map = {p.value: p for p in TrendPeriod}
        trend_period = period_map.get(period, TrendPeriod.MONTHLY)
        
        trends = analytics_bi_system.analyze_trends(project_id, kpi_id, trend_period)
        return {"status": "success", "trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/benchmarks/{project_id}")
async def get_benchmarks(
    project_id: str,
    benchmark_type: str = "industry"
):
    """
    Get benchmarking data
    
    - **benchmark_type**: industry, regional, historical, peer_group
    """
    try:
        type_map = {t.value: t for t in BenchmarkType}
        b_type = type_map.get(benchmark_type, BenchmarkType.INDUSTRY)
        
        benchmarks = analytics_bi_system.get_benchmarks(project_id, b_type)
        return {"status": "success", "benchmarks": benchmarks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/dashboard")
async def create_dashboard(
    name: str,
    widgets: List[Dict[str, Any]],
    owner_id: str,
    is_public: bool = False
):
    """Create a custom dashboard"""
    try:
        dashboard = analytics_bi_system.create_dashboard(
            name=name,
            widgets=widgets,
            owner_id=owner_id,
            is_public=is_public
        )
        return {"status": "success", "dashboard": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboards")
async def get_dashboards(owner_id: Optional[str] = None):
    """Get available dashboards"""
    try:
        dashboards = analytics_bi_system.get_dashboards(owner_id)
        return {"status": "success", "dashboards": dashboards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard with data"""
    try:
        dashboard = analytics_bi_system.get_dashboard_with_data(dashboard_id)
        return {"status": "success", "dashboard": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/executive-summary/{project_id}")
async def get_executive_summary(project_id: str):
    """Get executive decision support summary"""
    try:
        summary = analytics_bi_system.get_executive_summary(project_id)
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/insights")
async def generate_insights(project_data: Dict[str, Any]):
    """Generate AI-powered insights from project data"""
    try:
        insights = analytics_bi_system.generate_insights(project_data)
        return {"status": "success", "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Phase 4 - Industry Customizations Endpoints
# ============================================

@router.get("/industry/sectors")
async def get_industry_sectors():
    """Get available industry sectors"""
    try:
        sectors = [
            {
                "id": s.value,
                "name": s.value.replace("_", " ").title()
            }
            for s in IndustrySector
        ]
        return {"status": "success", "sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/profile/{sector}")
async def get_industry_profile(sector: str):
    """Get industry profile with configurations"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        profile = industry_customization_system.get_profile(industry_sector)
        return {"status": "success", "profile": profile}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/kpis/{sector}")
async def get_industry_kpis(sector: str):
    """Get industry-specific KPIs"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        kpis = industry_customization_system.get_industry_kpis(industry_sector)
        return {"status": "success", "kpis": kpis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/workflows/{sector}")
async def get_industry_workflows(sector: str):
    """Get industry-specific workflows"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        workflows = industry_customization_system.get_workflows(industry_sector)
        return {"status": "success", "workflows": workflows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/templates/{sector}")
async def get_industry_templates(sector: str, template_type: Optional[str] = None):
    """Get industry-specific templates"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        templates = industry_customization_system.get_templates(industry_sector, template_type)
        return {"status": "success", "templates": templates}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/compliance/{sector}")
async def get_industry_compliance(sector: str):
    """Get industry compliance requirements"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        compliance = industry_customization_system.get_compliance_requirements(industry_sector)
        return {"status": "success", "compliance": compliance}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry/benchmarks/{sector}")
async def get_industry_benchmarks(sector: str):
    """Get industry benchmarks"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        benchmarks = industry_customization_system.get_benchmarks(industry_sector)
        return {"status": "success", "benchmarks": benchmarks}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/industry/configure-project")
async def configure_project_for_industry(
    project_id: str,
    sector: str,
    subsector: Optional[str] = None,
    custom_settings: Optional[Dict[str, Any]] = None
):
    """Configure a project for a specific industry"""
    try:
        sector_map = {s.value: s for s in IndustrySector}
        industry_sector = sector_map.get(sector)
        
        if not industry_sector:
            raise HTTPException(status_code=404, detail="Industry sector not found")
        
        config = industry_customization_system.configure_project(
            project_id=project_id,
            sector=industry_sector,
            subsector=subsector,
            custom_settings=custom_settings or {}
        )
        return {"status": "success", "configuration": config}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Phase 4 - Infrastructure & Commercial Routes
# ============================================

@router.get("/infrastructure/status")
async def get_infrastructure_status():
    """Get infrastructure status"""
    try:
        from ..core import infrastructure_manager
        status = infrastructure_manager.get_infrastructure_status()
        return {"status": "success", "infrastructure": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/infrastructure/scale/{service_id}")
async def scale_infrastructure_service(
    service_id: str,
    instances: int
):
    """Scale an infrastructure service"""
    try:
        from ..core import infrastructure_manager
        result = infrastructure_manager.scale_service(service_id, instances)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infrastructure/k8s-configs")
async def get_kubernetes_configs():
    """Get Kubernetes configurations"""
    try:
        from ..core import infrastructure_manager
        configs = infrastructure_manager.generate_all_k8s_configs()
        return {"status": "success", "configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infrastructure/capacity")
async def get_capacity_report():
    """Get capacity planning report"""
    try:
        from ..core import infrastructure_manager
        report = infrastructure_manager.get_capacity_report()
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commercial/tiers")
async def get_subscription_tiers():
    """Get available subscription tiers"""
    try:
        from ..core import commercial_system
        tiers = commercial_system.get_subscription_tiers()
        return {"status": "success", "tiers": tiers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/commercial/provision")
async def provision_customer(
    tenant_name: str,
    tier: str,
    admin_email: str,
    company_name: Optional[str] = None,
    industry: Optional[str] = None
):
    """Provision a new customer"""
    try:
        from ..core import commercial_system
        result = commercial_system.provision_new_customer(
            tenant_name=tenant_name,
            tier=tier,
            admin_email=admin_email,
            company_name=company_name,
            industry=industry
        )
        return {"status": "success", "provisioning": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commercial/tenant/{tenant_id}")
async def get_tenant_info(tenant_id: str):
    """Get tenant information"""
    try:
        from ..core import commercial_system
        info = commercial_system.get_tenant_info(tenant_id)
        return {"status": "success", "tenant": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commercial/tenant/{tenant_id}/usage")
async def get_tenant_usage(tenant_id: str):
    """Get tenant usage metrics"""
    try:
        from ..core import commercial_system
        usage = commercial_system.get_tenant_usage(tenant_id)
        return {"status": "success", "usage": usage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/commercial/license/validate")
async def validate_license(license_key: str):
    """Validate a license key"""
    try:
        from ..core import commercial_system
        result = commercial_system.validate_license(license_key)
        return {"status": "success", "validation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commercial/sla/{tenant_id}")
async def get_sla_status(tenant_id: str):
    """Get SLA status for a tenant"""
    try:
        from ..core import commercial_system
        sla = commercial_system.get_sla_status(tenant_id)
        return {"status": "success", "sla": sla}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))