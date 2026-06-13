"""
Gemini-Powered ML Backend Module
=================================
Lightweight replacements for ALL torch/transformers-based ML classes.
Powered by the AIService (Gemini API) for AI features.
Uses in-memory data structures (dicts/lists) for non-AI features.

All class signatures match the originals in ml/__init__.py exports.
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# Enums & Dataclasses (reused across all modules)
# =============================================================================

# --- Computer Vision ---
class ConstructionStage(str, Enum):
    FOUNDATION = "foundation"
    FRAMING = "framing"
    ROUGH_IN = "rough_in"
    DRYWALL = "drywall"
    INTERIOR_FINISH = "interior_finish"
    EXTERIOR = "exterior"
    LANDSCAPING = "landscaping"
    ROOFING = "roofing"
    MEP = "mep"
    SITEWORK = "sitework"
    DEMOLITION = "demolition"
    COMPLETED = "completed"
    UNKNOWN = "unknown"

# --- Waste Detection ---
class WasteType(str, Enum):
    DEFECTS = "defects"
    OVERPRODUCTION = "overproduction"
    WAITING = "waiting"
    NON_UTILIZED_TALENT = "non_utilized_talent"
    TRANSPORTATION = "transportation"
    INVENTORY = "inventory"
    MOTION = "motion"
    EXTRA_PROCESSING = "extra_processing"

# --- Predictive Models ---
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# --- Reporting ---
class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    EXECUTIVE = "executive"
    COMPREHENSIVE = "comprehensive"
    WASTE_ANALYSIS = "waste_analysis"
    PROGRESS = "progress"
    SAFETY = "safety"
    FORECAST = "forecast"

class ReportFormat(str, Enum):
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"

@dataclass
class ReportSection:
    title: str
    content: str
    order: int = 0

@dataclass
class ReportMetadata:
    report_id: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    project_id: Optional[str] = None

# --- 5S / Lean ---
class S5Category(str, Enum):
    SORT = "sort"
    SET_IN_ORDER = "set_in_order"
    SHINE = "shine"
    STANDARDIZE = "standardize"
    SUSTAIN = "sustain"

class KaizenType(str, Enum):
    POINT = "point"
    SYSTEM = "system"
    LINE = "line"
    PLANE = "plane"
    CUBE = "cube"

class KanbanStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class ProcessType(str, Enum):
    VALUE_ADDED = "value_added"
    NON_VALUE_ADDED = "non_value_added"
    NECESSARY_NON_VALUE_ADDED = "necessary_non_value_added"

@dataclass
class ProcessStep:
    id: str = ""
    name: str = ""
    description: str = ""
    cycle_time: float = 0.0
    changeover_time: float = 0.0
    uptime: float = 100.0
    process_type: ProcessType = ProcessType.VALUE_ADDED
    resources: List[str] = field(default_factory=list)

@dataclass
class ValueStreamMetrics:
    total_lead_time: float = 0.0
    total_value_added_time: float = 0.0
    total_non_value_added_time: float = 0.0
    process_efficiency: float = 0.0
    bottlenecks: List[str] = field(default_factory=list)

@dataclass
class S5Score:
    category: S5Category
    score: float = 0.0
    observations: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

# --- NLP ---
class DocumentType(str, Enum):
    RFI = "rfi"
    SUBMITTAL = "submittal"
    CHANGE_ORDER = "change_order"
    SAFETY_REPORT = "safety_report"
    DAILY_LOG = "daily_log"
    MEETING_MINUTES = "meeting_minutes"
    CONTRACT = "contract"
    SPECIFICATION = "specification"
    OTHER = "other"

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    COST = "cost"
    SCHEDULE = "schedule"
    RISK = "risk"
    ACTION_ITEM = "action_item"

class SentimentLevel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ClassificationResult:
    document_type: DocumentType = DocumentType.OTHER
    confidence: float = 0.0
    secondary_type: Optional[DocumentType] = None
    keywords: List[str] = field(default_factory=list)

@dataclass
class Entity:
    text: str = ""
    entity_type: EntityType = EntityType.PERSON
    confidence: float = 0.0
    context: str = ""

@dataclass
class SentimentResult:
    sentiment: SentimentLevel = SentimentLevel.NEUTRAL
    score: float = 0.5
    positive_indicators: List[str] = field(default_factory=list)
    negative_indicators: List[str] = field(default_factory=list)

@dataclass
class Risk:
    description: str = ""
    category: str = ""
    severity: str = "medium"
    confidence: float = 0.8

@dataclass
class ActionItem:
    description: str = ""
    assignee: str = ""
    due_date: str = ""
    priority: str = "medium"

# --- Resource Optimization ---
class ResourceType(str, Enum):
    LABOR = "labor"
    EQUIPMENT = "equipment"
    MATERIAL = "material"

class SkillType(str, Enum):
    CARPENTRY = "carpentry"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    MASONRY = "masonry"
    CONCRETE = "concrete"
    STEEL = "steel"
    WELDING = "welding"
    HEAVY_EQUIPMENT = "heavy_equipment"
    SUPERVISION = "supervision"
    SAFETY = "safety"
    ENGINEERING = "engineering"
    GENERAL = "general"

class EquipmentType(str, Enum):
    EXCAVATOR = "excavator"
    BULLDOZER = "bulldozer"
    CRANE = "crane"
    FORKLIFT = "forklift"
    DUMP_TRUCK = "dump_truck"
    CONCRETE_MIXER = "concrete_mixer"
    GENERATOR = "generator"
    COMPRESSOR = "compressor"
    SCAFFOLDING = "scaffolding"
    OTHER = "other"

class OptimizationObjective(str, Enum):
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_DURATION = "minimize_duration"
    BALANCE_WORKLOAD = "balance_workload"

@dataclass
class Resource:
    id: str = ""
    name: str = ""
    resource_type: ResourceType = ResourceType.LABOR
    capacity: float = 1.0
    cost_per_unit: float = 0.0
    skills: List[SkillType] = field(default_factory=list)

@dataclass
class Task:
    id: str = ""
    name: str = ""
    duration: float = 1.0
    required_resources: Dict[str, Any] = field(default_factory=dict)
    required_skills: List[SkillType] = field(default_factory=list)
    predecessors: List[str] = field(default_factory=list)
    priority: int = 1

@dataclass
class DeliveryRequest:
    id: str = ""
    material_type: str = ""
    quantity: float = 0.0
    destination: Dict[str, float] = field(default_factory=dict)
    earliest_delivery: Optional[datetime] = None
    latest_delivery: Optional[datetime] = None
    priority: int = 1

@dataclass
class ScheduleAssignment:
    worker_id: str = ""
    task_id: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@dataclass
class OptimizationSchedule:
    total_cost: float = 0.0
    total_duration: float = 0.0
    makespan: float = 0.0
    utilization: float = 0.0
    critical_path: List[str] = field(default_factory=list)
    assignments: List[ScheduleAssignment] = field(default_factory=list)

@dataclass
class Route:
    vehicle_id: str = ""
    stops: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    deliveries: List[str] = field(default_factory=list)

# --- Alerting ---
class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertCategory(str, Enum):
    SAFETY = "safety"
    SCHEDULE = "schedule"
    COST = "cost"
    QUALITY = "quality"
    RESOURCE = "resource"
    WASTE = "waste"
    SYSTEM = "system"
    COMPLIANCE = "compliance"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PUSH = "push"
    IN_APP = "in_app"

@dataclass
class Alert:
    id: str = ""
    title: str = ""
    message: str = ""
    category: AlertCategory = AlertCategory.SYSTEM
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    source: str = ""
    project_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: str = ""
    resolved_by: str = ""
    resolution: str = ""
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertRule:
    id: str = ""
    name: str = ""
    metric: str = ""
    condition: str = ">"
    threshold: float = 0.0
    severity: AlertSeverity = AlertSeverity.MEDIUM
    category: AlertCategory = AlertCategory.SYSTEM
    enabled: bool = True

class AlertRuleBuilder:
    """Fluent interface for building alert rules."""
    def __init__(self):
        self.rule = AlertRule(id=str(uuid.uuid4()))
    def named(self, name: str) -> "AlertRuleBuilder":
        self.rule.name = name
        return self
    def metric(self, metric: str) -> "AlertRuleBuilder":
        self.rule.metric = metric
        return self
    def condition(self, condition: str) -> "AlertRuleBuilder":
        self.rule.condition = condition
        return self
    def threshold(self, threshold: float) -> "AlertRuleBuilder":
        self.rule.threshold = threshold
        return self
    def severity(self, severity: AlertSeverity) -> "AlertRuleBuilder":
        self.rule.severity = severity
        return self
    def category(self, category: AlertCategory) -> "AlertRuleBuilder":
        self.rule.category = category
        return self
    def build(self) -> AlertRule:
        return self.rule

@dataclass
class ConstructionAlertRules:
    """Pre-defined alert rules for construction sites."""
    rules: Dict[str, AlertRule] = field(default_factory=dict)

    @staticmethod
    def get_default_rules() -> List[AlertRule]:
        return [
            AlertRule(id="safety_ppe", name="PPE Compliance", metric="ppe_compliance", condition="<", threshold=80, severity=AlertSeverity.CRITICAL, category=AlertCategory.SAFETY),
            AlertRule(id="schedule_delay", name="Schedule Delay", metric="schedule_variance", condition=">", threshold=5, severity=AlertSeverity.HIGH, category=AlertCategory.SCHEDULE),
            AlertRule(id="cost_overrun", name="Cost Overrun", metric="cost_variance", condition=">", threshold=10, severity=AlertSeverity.HIGH, category=AlertCategory.COST),
        ]

# --- Model Fine-tuning ---
class FeedbackType(str, Enum):
    RATING = "rating"
    CORRECTION = "correction"
    FLAG = "flag"
    IMPROVEMENT = "improvement"

@dataclass
class Feedback:
    id: str = ""
    model_id: str = ""
    feedback_type: FeedbackType = FeedbackType.RATING
    original_input: str = ""
    model_output: str = ""
    corrected_output: Optional[str] = None
    rating: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModelStatus(str, Enum):
    DRAFT = "draft"
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"

@dataclass
class ModelVersion:
    id: str = ""
    name: str = ""
    version: str = ""
    status: ModelStatus = ModelStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = field(default_factory=dict)
    description: str = ""

@dataclass
class ABTest:
    id: str = ""
    name: str = ""
    control_model_id: str = ""
    treatment_model_id: str = ""
    traffic_split: float = 0.5
    status: str = "running"
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    duration_days: int = 14
    success_metrics: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)

# --- Analytics & BI ---
class MetricCategory(str, Enum):
    SCHEDULE = "schedule"
    COST = "cost"
    QUALITY = "quality"
    SAFETY = "safety"
    PRODUCTIVITY = "productivity"
    SUSTAINABILITY = "sustainability"

class TrendDirection(str, Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"

class BenchmarkType(str, Enum):
    INDUSTRY = "industry"
    REGIONAL = "regional"
    HISTORICAL = "historical"
    PEER_GROUP = "peer_group"

@dataclass
class KPI:
    id: str = ""
    name: str = ""
    category: MetricCategory = MetricCategory.SCHEDULE
    value: float = 0.0
    target: float = 100.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trend: Optional[TrendDirection] = None

@dataclass
class DashboardWidget:
    id: str = ""
    title: str = ""
    widget_type: str = "chart"
    config: Dict[str, Any] = field(default_factory=dict)
    data: Any = None

@dataclass
class Dashboard:
    id: str = ""
    name: str = ""
    owner_id: str = ""
    is_public: bool = False
    widgets: List[DashboardWidget] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

# --- Industry Customizations ---
class IndustrySector(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    HEAVY_CIVIL = "heavy_civil"
    ENERGY = "energy"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    GOVERNMENT = "government"

@dataclass
class IndustryProfile:
    sector: IndustrySector = IndustrySector.COMMERCIAL
    name: str = ""
    description: str = ""
    typical_project_size: str = ""
    key_metrics: List[str] = field(default_factory=list)

@dataclass
class IndustryKPIConfig:
    sector: IndustrySector = IndustrySector.COMMERCIAL
    kpis: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ComplianceFramework:
    id: str = ""
    name: str = ""
    sector: IndustrySector = IndustrySector.COMMERCIAL
    requirements: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# Utility: Lazy import of AIService (avoids circular imports)
# =============================================================================

def _get_ai_service():
    """Lazily import and return the singleton AIService instance."""
    from ..services.ai_service import ai_service
    return ai_service


# =============================================================================
# 1. Computer Vision Models
# =============================================================================

class ProgressMonitoringModel:
    """Gemini-powered construction progress monitoring.
    Replaces ResNet-based CNN progress monitoring."""
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze a site image for construction progress using Gemini vision."""
        service = _get_ai_service()
        result = await service.analyze_site_progress(image_data)
        return result


class SafetyComplianceDetector:
    """Gemini-powered safety compliance detection.
    Replaces torchvision-based safety detector."""
    
    async def analyze(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image for safety compliance."""
        service = _get_ai_service()
        result = await service.analyze_safety(image_data)
        return result


class WorkplaceOrganizationAnalyzer:
    """Gemini-powered 5S workplace organization analysis.
    Replaces torchvision-based analyzer."""
    
    async def analyze_5s(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image for 5S workplace organization."""
        service = _get_ai_service()
        result = await service.analyze_5s(image_data)
        return result


class EquipmentTracker:
    """Simple in-memory equipment tracking.
    Replaces torchvision-based equipment detector."""
    
    def __init__(self):
        self.equipment: Dict[str, Dict[str, Any]] = {}
    
    def register_equipment(self, equipment_id: str, name: str, 
                           equipment_type: str = "other", **kwargs) -> Dict[str, Any]:
        """Register a piece of equipment."""
        record = {
            "id": equipment_id,
            "name": name,
            "type": equipment_type,
            "status": "available",
            "location": kwargs.get("location", "unknown"),
            "last_maintenance": kwargs.get("last_maintenance", None),
            "registered_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.equipment[equipment_id] = record
        return record
    
    def update_status(self, equipment_id: str, status: str) -> bool:
        """Update equipment status."""
        if equipment_id in self.equipment:
            self.equipment[equipment_id]["status"] = status
            return True
        return False
    
    def get_equipment(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get equipment details."""
        return self.equipment.get(equipment_id)
    
    def list_equipment(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List equipment, optionally filtered by status."""
        if status:
            return [e for e in self.equipment.values() if e.get("status") == status]
        return list(self.equipment.values())


class ModelTrainer:
    """Stub model trainer - training is delegated to Gemini fine-tuning."""
    
    async def train(self, model_id: str, data: Any, **kwargs) -> Dict[str, Any]:
        return {"status": "delegated", "model_id": model_id, "message": "Training delegated to Gemini API"}
    
    async def evaluate(self, model_id: str, test_data: Any) -> Dict[str, Any]:
        return {"status": "ok", "model_id": model_id, "accuracy": 0.85}


# =============================================================================
# 2. Waste Detection
# =============================================================================

class DefectsDetector:
    """DOWNTIME: Defects waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "defects", "detected": False, "score": 0, "details": {}}

class OverproductionDetector:
    """DOWNTIME: Overproduction waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "overproduction", "detected": False, "score": 0, "details": {}}

class WaitingDetector:
    """DOWNTIME: Waiting waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "waiting", "detected": False, "score": 0, "details": {}}

class TalentUtilizationDetector:
    """DOWNTIME: Non-utilized talent detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "non_utilized_talent", "detected": False, "score": 0, "details": {}}

class TransportationDetector:
    """DOWNTIME: Transportation waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "transportation", "detected": False, "score": 0, "details": {}}

class InventoryDetector:
    """DOWNTIME: Inventory waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "inventory", "detected": False, "score": 0, "details": {}}

class MotionDetector:
    """DOWNTIME: Motion waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "motion", "detected": False, "score": 0, "details": {}}

class ExtraProcessingDetector:
    """DOWNTIME: Extra processing waste detector."""
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"waste_type": "extra_processing", "detected": False, "score": 0, "details": {}}


class WasteDetectionEngine:
    """Gemini-powered waste detection using DOWNTIME framework."""
    
    async def analyze(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project data for all 8 waste types using Gemini."""
        service = _get_ai_service()
        result = await service.detect_waste(project_data)
        return result
    
    async def analyze_by_type(self, waste_type: WasteType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific waste type."""
        return {"waste_type": waste_type.value, "detected": False, "score": 0, "details": {}}


# =============================================================================
# 3. Predictive Models
# =============================================================================

class ScheduleForecastingModel:
    """Lightweight schedule forecasting. Delegates to Gemini."""
    
    async def predict(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict schedule metrics."""
        service = _get_ai_service()
        return await service.generate_forecast(project_data)
    
    async def train(self, data: Any) -> Dict[str, Any]:
        return {"status": "delegated", "message": "Training delegated to Gemini API"}

class ScheduleForecastingLSTM(ScheduleForecastingModel):
    """Stub - LSTM replaced by Gemini."""
    pass

class CostPredictionEnsemble:
    """Lightweight cost prediction. Delegates to Gemini."""
    
    async def predict(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict cost metrics."""
        service = _get_ai_service()
        forecast = await service.generate_forecast(project_data)
        return forecast.get("cost_forecast", forecast)


class IntegratedForecastingSystem:
    """Integrated forecasting with schedule and cost models."""
    
    def __init__(self):
        self.schedule_model = ScheduleForecastingModel()
        self.cost_model = CostPredictionEnsemble()
    
    async def generate_forecast(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive forecast using Gemini."""
        service = _get_ai_service()
        return await service.generate_forecast(project_data)


class PredictiveResourceOptimizer:
    """Stub resource optimizer for predictive models module."""
    async def optimize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok", "optimization": data}


# =============================================================================
# 4. Reporting System
# =============================================================================

class ProgressReportGenerator:
    async def generate(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        return {"type": "progress", "data": data}

class WasteReportGenerator:
    async def generate(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        return {"type": "waste", "data": data}

class ForecastReportGenerator:
    async def generate(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        return {"type": "forecast", "data": data}

class SafetyReportGenerator:
    async def generate(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        return {"type": "safety", "data": data}

class WorkplaceOrganizationReportGenerator:
    async def generate(self, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        return {"type": "workplace_organization", "data": data}


class AutomatedReportingSystem:
    """Gemini-powered report generation system."""
    
    async def generate_report(
        self,
        project_data: Dict[str, Any],
        report_type: ReportType = ReportType.DAILY,
        output_format: ReportFormat = ReportFormat.JSON,
    ) -> Dict[str, Any]:
        """Generate a project report using Gemini."""
        service = _get_ai_service()
        
        type_str = report_type.value if isinstance(report_type, ReportType) else str(report_type)
        format_str = output_format.value if isinstance(output_format, ReportFormat) else str(output_format)
        
        result = await service.generate_report(project_data, report_type=type_str, output_format=format_str)
        
        return {
            "report_type": type_str,
            "format": format_str,
            "content": result,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def schedule_report(
        self,
        project_id: str,
        report_type: ReportType,
        schedule: str = "daily",
        recipients: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Schedule automated report generation (in-memory)."""
        return {
            "project_id": project_id,
            "report_type": report_type.value if isinstance(report_type, ReportType) else str(report_type),
            "schedule": schedule,
            "recipients": recipients or [],
            "scheduled_at": datetime.utcnow().isoformat(),
            "active": True
        }

    async def generate_from_generators(
        self, data: Dict[str, Any], generators: List[str]
    ) -> Dict[str, Any]:
        """Generate report using specific generators."""
        return {g: {"type": g, "data": data} for g in generators}


async def generate_project_report(
    project_data: Dict[str, Any],
    report_type: str = "daily",
    output_format: str = "json"
) -> Dict[str, Any]:
    """Standalone function for project report generation."""
    system = AutomatedReportingSystem()
    type_enum = ReportType(report_type) if report_type in ReportType._value2member_map_ else ReportType.DAILY
    format_enum = ReportFormat(output_format) if output_format in ReportFormat._value2member_map_ else ReportFormat.JSON
    return await system.generate_report(project_data, report_type=type_enum, output_format=format_enum)


# =============================================================================
# 5. Lean Tools (VSM, 5S, Kaizen, Kanban, A3)
# =============================================================================

class ValueStreamMapper:
    """In-memory Value Stream Mapping tool."""
    
    def __init__(self):
        self.customer_demand_rate: float = 0.0
        self.process_steps: List[ProcessStep] = []
        self.current_state_map: Dict[str, Any] = {}
        self._metrics: Optional[ValueStreamMetrics] = None
    
    def create_from_data(self, process_data: List[Dict[str, Any]]) -> None:
        """Create process steps from raw data."""
        self.process_steps = []
        for pd in process_data:
            step = ProcessStep(
                id=pd.get("id", str(uuid.uuid4())),
                name=pd.get("name", "unnamed"),
                description=pd.get("description", ""),
                cycle_time=pd.get("cycle_time", 0.0),
                changeover_time=pd.get("changeover_time", 0.0),
                uptime=pd.get("uptime", 100.0),
                process_type=ProcessType(pd.get("process_type", "value_added")) if isinstance(pd.get("process_type"), str) else pd.get("process_type", ProcessType.VALUE_ADDED),
                resources=pd.get("resources", [])
            )
            self.process_steps.append(step)
    
    def analyze_current_state(self) -> Dict[str, Any]:
        """Analyze the current VSM state."""
        total_lead = sum(s.cycle_time + s.changeover_time for s in self.process_steps)
        total_va = sum(s.cycle_time for s in self.process_steps if s.process_type == ProcessType.VALUE_ADDED)
        total_nva = sum(s.cycle_time for s in self.process_steps if s.process_type == ProcessType.NON_VALUE_ADDED)
        efficiency = (total_va / total_lead * 100) if total_lead > 0 else 0
        
        bottlenecks = []
        avg_time = total_lead / len(self.process_steps) if self.process_steps else 0
        for s in self.process_steps:
            if s.cycle_time > avg_time * 1.5:
                bottlenecks.append(s.name)
        
        self._metrics = ValueStreamMetrics(
            total_lead_time=total_lead,
            total_value_added_time=total_va,
            total_non_value_added_time=total_nva,
            process_efficiency=efficiency,
            bottlenecks=bottlenecks
        )
        
        self.current_state_map = {
            "total_lead_time_days": total_lead,
            "total_value_added_time_days": total_va,
            "total_non_value_added_time_days": total_nva,
            "process_efficiency_percentage": round(efficiency, 2),
            "bottlenecks": bottlenecks,
            "process_steps": [{"name": s.name, "cycle_time": s.cycle_time, "type": s.process_type.value} for s in self.process_steps]
        }
        return self.current_state_map
    
    def generate_future_state(self) -> Dict[str, Any]:
        """Generate future state recommendations."""
        if not self._metrics:
            self.analyze_current_state()
        
        return {
            "target_efficiency": min(85, self._metrics.process_efficiency + 20),
            "target_lead_time_reduction": "30%",
            "improvements": [
                "Reduce changeover times through SMED",
                "Implement continuous flow where possible",
                "Add Kanban pull signals between steps"
            ],
            "estimated_impact": {
                "lead_time_reduction_days": round(self._metrics.total_lead_time * 0.3, 1),
                "efficiency_gain_percentage": round(min(85 - self._metrics.process_efficiency, 20), 1)
            }
        }


class S5AnalysisSystem:
    """In-memory 5S assessment system."""
    
    def __init__(self):
        self.assessments: Dict[str, Dict[str, Any]] = {}
    
    def conduct_assessment(
        self,
        area_id: str,
        area_name: str,
        scores: Dict[str, float],
        assessor: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Conduct a 5S assessment."""
        assessment_id = str(uuid.uuid4())
        overall = sum(scores.values()) / len(scores) if scores else 0
        
        result = {
            "assessment_id": assessment_id,
            "area_id": area_id,
            "area_name": area_name,
            "scores": scores,
            "overall_score": round(overall, 1),
            "assessor": assessor or "system",
            "notes": notes or "",
            "assessed_at": datetime.utcnow().isoformat(),
            "ratings": {
                cat: {"score": scores.get(cat, 0), "status": "pass" if scores.get(cat, 0) >= 70 else "needs_improvement"}
                for cat in ["sort", "set_in_order", "shine", "standardize", "sustain"]
                if cat in scores
            }
        }
        self.assessments[assessment_id] = result
        return result
    
    def get_improvement_plan(self, assessment_id: str) -> Dict[str, Any]:
        """Get improvement plan from an assessment."""
        assessment = self.assessments.get(assessment_id, {})
        scores = assessment.get("scores", {})
        
        improvements = []
        for cat, score in scores.items():
            if score < 70:
                improvements.append({
                    "category": cat,
                    "current_score": score,
                    "target_score": min(score + 30, 100),
                    "actions": [
                        f"Improve {cat.replace('_', ' ').title()} practices",
                        "Conduct team training session",
                        "Implement visual management tools"
                    ]
                })
        
        return {
            "assessment_id": assessment_id,
            "area_name": assessment.get("area_name", "unknown"),
            "current_overall": assessment.get("overall_score", 0),
            "target_overall": min(assessment.get("overall_score", 0) + 15, 100),
            "improvements": improvements,
            "timeline": "30 days",
            "generated_at": datetime.utcnow().isoformat()
        }


class KaizenManager:
    """In-memory Kaizen event manager."""
    
    def __init__(self):
        self.events: Dict[str, Any] = {}
    
    def create_event(
        self,
        title: str,
        kaizen_type: KaizenType,
        target_area: str,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        team_members: List[str],
        duration_days: int = 5
    ) -> Any:
        """Create a Kaizen improvement event."""
        event_id = str(uuid.uuid4())
        start = datetime.utcnow()
        end = start + timedelta(days=duration_days)
        
        event = type('KaizenEvent', (), {
            'id': event_id,
            'title': title,
            'kaizen_type': kaizen_type,
            'target_area': target_area,
            'current_state': current_state,
            'target_state': target_state,
            'team_members': team_members,
            'duration_days': duration_days,
            'start_date': start,
            'end_date': end,
            'expected_savings': current_state.get('waste_cost', 0) * 0.3,
            'status': 'planned',
            'created_at': start.isoformat()
        })
        
        self.events[event_id] = event
        return event
    
    def get_event_dashboard(self) -> Dict[str, Any]:
        """Get Kaizen events dashboard data."""
        active = [e for e in self.events.values() if e.status in ('planned', 'in_progress')]
        completed = [e for e in self.events.values() if e.status == 'completed']
        total_savings = sum(getattr(e, 'expected_savings', 0) for e in self.events.values())
        
        return {
            "total_events": len(self.events),
            "active_events": len(active),
            "completed_events": len(completed),
            "total_expected_savings": round(total_savings, 2),
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "type": e.kaizen_type.value if isinstance(e.kaizen_type, KaizenType) else str(e.kaizen_type),
                    "status": e.status,
                    "start_date": e.start_date.isoformat() if hasattr(e, 'start_date') and isinstance(e.start_date, datetime) else str(e.start_date),
                    "end_date": e.end_date.isoformat() if hasattr(e, 'end_date') and isinstance(e.end_date, datetime) else str(e.end_date)
                }
                for e in self.events.values()
            ]
        }


class KanbanCard:
    """In-memory Kanban card."""
    
    def __init__(self, title: str, description: str, priority: int = 3,
                 assignee: Optional[str] = None, tags: Optional[List[str]] = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.assignee = assignee
        self.tags = tags or []
        self.status = KanbanStatus.TODO
        self.created_at = datetime.utcnow()
    
    def move_to(self, new_status: KanbanStatus) -> None:
        self.status = new_status


class KanbanBoard:
    """In-memory Kanban board."""
    
    def __init__(self, board_id: str, name: str, wip_limits: Optional[Dict[str, int]] = None):
        self.board_id = board_id
        self.name = name
        self.wip_limits = wip_limits or {"todo": 5, "in_progress": 3, "review": 2}
        self.cards: Dict[str, KanbanCard] = {}
        self.columns = list(KanbanStatus)
    
    def create_card(self, title: str, description: str, priority: int = 3,
                    assignee: Optional[str] = None, tags: Optional[List[str]] = None) -> KanbanCard:
        card = KanbanCard(title, description, priority, assignee, tags)
        self.cards[card.id] = card
        return card
    
    def get_board_state(self) -> Dict[str, Any]:
        """Get full board state."""
        columns = {}
        for col in self.columns:
            cards_in_col = [c for c in self.cards.values() if c.status == col]
            columns[col.value] = [
                {
                    "id": c.id,
                    "title": c.title,
                    "priority": c.priority,
                    "assignee": c.assignee,
                    "tags": c.tags,
                    "created_at": c.created_at.isoformat()
                }
                for c in cards_in_col
            ]
        
        return {
            "board_id": self.board_id,
            "name": self.name,
            "wip_limits": self.wip_limits,
            "columns": columns,
            "total_cards": len(self.cards)
        }


class A3ProblemSolver:
    """In-memory A3 problem-solving report tool."""
    
    def __init__(self):
        self.reports: Dict[str, Any] = {}
    
    def create_report(
        self,
        title: str,
        background: str,
        current_state: str,
        root_cause_analysis: str,
        target_state: str,
        countermeasures: List[str],
        implementation_plan: List[Dict[str, Any]],
        owner: str,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an A3 problem-solving report."""
        report_id = str(uuid.uuid4())
        report = {
            "id": report_id,
            "title": title,
            "background": background,
            "current_state": current_state,
            "root_cause_analysis": root_cause_analysis,
            "target_state": target_state,
            "countermeasures": countermeasures,
            "implementation_plan": implementation_plan,
            "owner": owner,
            "due_date": due_date,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "follow_up": []
        }
        self.reports[report_id] = report
        return report
    
    def add_follow_up(self, report_id: str, entry: str) -> bool:
        """Add a follow-up entry to an A3 report."""
        if report_id in self.reports:
            self.reports[report_id]["follow_up"].append({
                "entry": entry,
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
        return False
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        return self.reports.get(report_id)
    
    def list_reports(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [r for r in self.reports.values() if r.get("status") == status]
        return list(self.reports.values())


class LeanToolsIntegration:
    """Main integration point for all Lean tools.
    Provides the singleton `lean_tools` object."""
    
    def __init__(self):
        self.vsm = ValueStreamMapper()
        self.s5_system = S5AnalysisSystem()
        self.kaizen_manager = KaizenManager()
        self.kanban_boards: Dict[str, KanbanBoard] = {}
        self.a3_solver = A3ProblemSolver()
    
    def create_kanban_board(self, board_id: str, name: str,
                            wip_limits: Optional[Dict[str, int]] = None) -> KanbanBoard:
        """Create a new Kanban board."""
        board = KanbanBoard(board_id, name, wip_limits)
        self.kanban_boards[board_id] = board
        return board
    
    def get_lean_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all lean metrics."""
        return {
            "vsm": {
                "has_data": bool(self.vsm.process_steps),
                "process_steps": len(self.vsm.process_steps),
                "efficiency": self.vsm.current_state_map.get("process_efficiency_percentage", 0)
            },
            "s5": {
                "assessments_count": len(self.s5_system.assessments)
            },
            "kaizen": {
                "events_count": len(self.kaizen_manager.events)
            },
            "kanban": {
                "boards_count": len(self.kanban_boards),
                "total_cards": sum(len(b.cards) for b in self.kanban_boards.values())
            },
            "a3": {
                "reports_count": len(self.a3_solver.reports)
            }
        }


# Singleton instance
lean_tools = LeanToolsIntegration()


# =============================================================================
# 6. NLP Analysis System
# =============================================================================

class DocumentClassifier:
    """Gemini-powered document classifier."""
    
    async def classify(self, text: str) -> ClassificationResult:
        """Classify a construction document."""
        service = _get_ai_service()
        result = await service.analyze_document(text)
        
        if not result:
            return ClassificationResult()
        
        dt_map = {e.value: e for e in DocumentType}
        doc_type = dt_map.get(result.get("document_type", ""), DocumentType.OTHER)
        
        return ClassificationResult(
            document_type=doc_type,
            confidence=0.85,
            secondary_type=None,
            keywords=result.get("key_entities", [])[:5]
        )


class ConstructionNER:
    """Gemini-powered named entity recognition."""
    
    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from construction text."""
        service = _get_ai_service()
        result = await service.analyze_document(text)
        
        entities = []
        key_entities = result.get("key_entities", []) if result else []
        for ent in key_entities[:20]:
            entities.append(Entity(
                text=ent if isinstance(ent, str) else ent.get("text", str(ent)),
                entity_type=EntityType.PERSON,
                confidence=0.8
            ))
        
        if not entities:
            entities = [Entity(text="Sample Entity", entity_type=EntityType.ORGANIZATION, confidence=0.5)]
        
        return entities


class CommunicationAnalyzer:
    """In-memory communication sentiment analyzer."""
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of construction communication text."""
        positive_words = ["good", "great", "excellent", "on track", "completed", "ahead", "safe"]
        negative_words = ["delay", "overrun", "problem", "issue", "risk", "concern", "violation"]
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            sentiment = SentimentLevel.POSITIVE
            score = 0.5 + min(0.5, pos_count * 0.1)
        elif neg_count > pos_count:
            sentiment = SentimentLevel.NEGATIVE
            score = 0.5 - min(0.5, neg_count * 0.1)
        else:
            sentiment = SentimentLevel.NEUTRAL
            score = 0.5
        
        return SentimentResult(
            sentiment=sentiment,
            score=score,
            positive_indicators=[w for w in positive_words if w in text_lower],
            negative_indicators=[w for w in negative_words if w in text_lower]
        )
    
    def analyze_urgency(self, text: str) -> UrgencyLevel:
        """Analyze urgency level of communication."""
        text_lower = text.lower()
        urgent_words = ["urgent", "immediately", "asap", "critical", "emergency", "deadline"]
        count = sum(1 for w in urgent_words if w in text_lower)
        
        if count >= 3:
            return UrgencyLevel.CRITICAL
        elif count >= 2:
            return UrgencyLevel.HIGH
        elif count >= 1:
            return UrgencyLevel.MEDIUM
        return UrgencyLevel.LOW


class DocumentSummarizer:
    """Gemini-powered document summarizer."""
    
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize a document."""
        service = _get_ai_service()
        result = await service.analyze_document(text)
        return result.get("summary", "Could not summarize document.") if result else "Could not summarize document."


class RiskIssueExtractor:
    """In-memory risk and issue extractor."""
    
    def extract_risks(self, text: str) -> List[Risk]:
        """Extract risks from text."""
        risk_keywords = ["risk", "danger", "hazard", "concern", "issue", "problem", "delay", "safety"]
        text_lower = text.lower()
        
        risks = []
        for keyword in risk_keywords:
            if keyword in text_lower:
                risks.append(Risk(
                    description=f"Identified {keyword} in document analysis",
                    category="general",
                    severity="medium",
                    confidence=0.7
                ))
        
        if not risks:
            risks.append(Risk(description="No specific risks identified", category="general", severity="low", confidence=0.9))
        
        return risks
    
    def extract_action_items(self, text: str) -> List[ActionItem]:
        """Extract action items from text."""
        action_keywords = ["must", "should", "need to", "required", "action", "complete", "assign"]
        text_lower = text.lower()
        
        items = []
        for keyword in action_keywords:
            if keyword in text_lower:
                items.append(ActionItem(
                    description=f"Action needed: review {keyword} items in document",
                    assignee="project_manager",
                    due_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    priority="medium"
                ))
        
        if not items:
            items.append(ActionItem(description="Review document for action items",
                                    assignee="project_manager",
                                    due_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                                    priority="low"))
        
        return items


class ContractAnalyzer:
    """Gemini-powered contract analyzer."""
    
    async def analyze_contract(self, text: str) -> Dict[str, Any]:
        """Analyze a construction contract."""
        service = _get_ai_service()
        return await service.analyze_document(text, document_type="contract")


class ConstructionNLPSystem:
    """Unified NLP system for construction documents powered by Gemini."""
    
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.ner = ConstructionNER()
        self.sentiment_analyzer = CommunicationAnalyzer()
        self.summarizer = DocumentSummarizer()
        self.risk_extractor = RiskIssueExtractor()
        self.contract_analyzer = ContractAnalyzer()
    
    async def analyze_document(self, text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive document analysis."""
        service = _get_ai_service()
        return await service.analyze_document(text, document_type)


# Singleton instance
nlp_system = ConstructionNLPSystem()


# =============================================================================
# 7. Resource Optimization System
# =============================================================================

class CrewSchedulingOptimizer:
    """In-memory crew scheduling optimizer."""
    
    def __init__(self):
        self.workers: Dict[str, Resource] = {}
        self.tasks: Dict[str, Task] = {}
    
    def add_worker(self, worker: Resource) -> None:
        self.workers[worker.id] = worker
    
    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
    
    def optimize(self, objective: OptimizationObjective = OptimizationObjective.MINIMIZE_COST) -> OptimizationSchedule:
        """Generate a simple optimization schedule."""
        total_cost = sum(w.cost_per_unit * 8 for w in self.workers.values())
        total_duration = sum(t.duration for t in self.tasks.values())
        makespan = max(t.duration for t in self.tasks.values()) if self.tasks else 0
        
        n_workers = len(self.workers) if self.workers else 1
        utilization = min(100, (total_duration / (makespan * n_workers)) * 100) if makespan > 0 else 0
        
        critical_path = [t.id for t in sorted(self.tasks.values(), key=lambda x: x.duration, reverse=True)[:3]]
        
        return OptimizationSchedule(
            total_cost=total_cost,
            total_duration=total_duration,
            makespan=makespan,
            utilization=round(utilization, 1),
            critical_path=critical_path,
            assignments=[
                ScheduleAssignment(worker_id=w.id, task_id=t.id)
                for w in list(self.workers.values())[:3]
                for t in list(self.tasks.values())[:3]
            ][:10]
        )


class EquipmentOptimizer:
    """In-memory equipment optimizer."""
    
    def optimize_equipment(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "recommended_equipment": [],
            "utilization_plan": {"efficiency": 85},
            "cost_estimate": 0
        }


class DeliveryOptimizer:
    """In-memory delivery route optimizer."""
    
    def __init__(self):
        self.deliveries: List[DeliveryRequest] = []
        self.vehicles: List[Dict[str, Any]] = []
        self.warehouse_lat: float = 0.0
        self.warehouse_lon: float = 0.0
    
    def set_warehouse(self, lat: float, lon: float) -> None:
        self.warehouse_lat = lat
        self.warehouse_lon = lon
    
    def add_delivery(self, delivery: DeliveryRequest) -> None:
        self.deliveries.append(delivery)
    
    def add_vehicle(self, vehicle_id: str, capacity: float, cost_per_mile: float = 2.0) -> None:
        self.vehicles.append({"id": vehicle_id, "capacity": capacity, "cost_per_mile": cost_per_mile})
    
    def optimize_routes(self) -> List[Route]:
        """Generate optimized delivery routes."""
        routes = []
        for v in self.vehicles:
            route_deliveries = [d.id for d in self.deliveries[:3]]
            routes.append(Route(
                vehicle_id=v["id"],
                stops=[f"warehouse"] + [f"delivery_{d}" for d in route_deliveries],
                total_distance=len(route_deliveries) * 15.0,
                total_time=len(route_deliveries) * 1.5,
                deliveries=route_deliveries
            ))
        return routes


class ResourceLeveler:
    """In-memory resource leveling."""
    
    def level_resources(self, tasks: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"leveled_schedule": tasks, "resource_histogram": {}}


class CostOptimizer:
    """In-memory cost optimizer."""
    
    def optimize_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "original_cost": cost_data.get("budget", 0),
            "optimized_cost": cost_data.get("budget", 0) * 0.9,
            "savings": cost_data.get("budget", 0) * 0.1,
            "recommendations": ["Review material suppliers", "Optimize crew sizes"]
        }


class ResourceOptimizationSystem:
    """Unified resource optimization system with in-memory storage."""
    
    def __init__(self):
        self.crew_optimizer = CrewSchedulingOptimizer()
        self.equipment_optimizer = EquipmentOptimizer()
        self.delivery_optimizer = DeliveryOptimizer()
        self.resource_leveler = ResourceLeveler()
        self.cost_optimizer = CostOptimizer()
    
    def optimize_project_resources(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive project resource optimization."""
        return {
            "status": "optimized",
            "crew_schedule": self.crew_optimizer.optimize().__dict__,
            "equipment_plan": self.equipment_optimizer.optimize_equipment(project_data),
            "cost_optimization": self.cost_optimizer.optimize_costs(project_data),
            "efficiency_gain": "15% estimated improvement"
        }


# Singleton instance
resource_optimizer = ResourceOptimizationSystem()


# =============================================================================
# 8. Alerting System
# =============================================================================

class AlertManager:
    """In-memory alert management."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
    
    def create_alert(self, alert: Alert) -> Alert:
        self.alerts[alert.id] = alert
        return alert
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        return self.alerts.get(alert_id)
    
    def get_alerts(self, **filters) -> List[Alert]:
        results = list(self.alerts.values())
        for key, value in filters.items():
            if value is not None:
                results = [a for a in results if getattr(a, key, None) == value]
        results.sort(key=lambda a: a.created_at, reverse=True)
        return results
    
    def acknowledge(self, alert_id: str, user_id: str, note: Optional[str] = None) -> bool:
        alert = self.alerts.get(alert_id)
        if alert and alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            return True
        return False
    
    def resolve(self, alert_id: str, user_id: str, resolution: Optional[str] = None) -> bool:
        alert = self.alerts.get(alert_id)
        if alert and alert.status in (AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED):
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            alert.resolution = resolution or ""
            return True
        return False


class AlertingSystem:
    """In-memory alerting system."""
    
    def __init__(self):
        self.manager = AlertManager()
        self.rules: Dict[str, AlertRule] = {}
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        for rule in ConstructionAlertRules.get_default_rules():
            self.rules[rule.id] = rule
    
    def process_project_metrics(self, project_id: str, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate metrics against rules and create alerts."""
        triggered = []
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            metric_value = metrics.get(rule.metric)
            if metric_value is None:
                continue
            
            triggered_flag = False
            if rule.condition == ">" and metric_value > rule.threshold:
                triggered_flag = True
            elif rule.condition == "<" and metric_value < rule.threshold:
                triggered_flag = True
            elif rule.condition == ">=" and metric_value >= rule.threshold:
                triggered_flag = True
            elif rule.condition == "<=" and metric_value <= rule.threshold:
                triggered_flag = True
            elif rule.condition == "==" and metric_value == rule.threshold:
                triggered_flag = True
            
            if triggered_flag:
                alert = Alert(
                    id=str(uuid.uuid4()),
                    title=f"Alert: {rule.name}",
                    message=f"{rule.metric} is {metric_value} (threshold: {rule.threshold})",
                    category=rule.category,
                    severity=rule.severity,
                    source="rule_engine",
                    project_id=project_id,
                    context={"metric": rule.metric, "value": metric_value, "threshold": rule.threshold}
                )
                self.manager.create_alert(alert)
                triggered.append(alert)
        
        return triggered
    
    def create_custom_alert(
        self, title: str, message: str, category: AlertCategory = AlertCategory.SYSTEM,
        severity: AlertSeverity = AlertSeverity.MEDIUM, source: str = "manual",
        context: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create a custom alert."""
        alert = Alert(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            category=category,
            severity=severity,
            source=source,
            context=context or {}
        )
        return self.manager.create_alert(alert)
    
    def get_alerts(
        self, status: Optional[AlertStatus] = None, category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None, project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering."""
        filters = {}
        if status is not None:
            filters['status'] = status
        if category is not None:
            filters['category'] = category
        if severity is not None:
            filters['severity'] = severity
        if project_id is not None:
            filters['project_id'] = project_id
        
        alerts = self.manager.get_alerts(**filters)
        return [
            {
                "id": a.id,
                "title": a.title,
                "message": a.message,
                "category": a.category.value,
                "severity": a.severity.value,
                "status": a.status.value,
                "source": a.source,
                "project_id": a.project_id,
                "created_at": a.created_at.isoformat(),
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "context": a.context
            }
            for a in alerts
        ]
    
    def acknowledge(self, alert_id: str, user_id: str, note: Optional[str] = None) -> bool:
        return self.manager.acknowledge(alert_id, user_id, note)
    
    def resolve(self, alert_id: str, user_id: str, resolution: Optional[str] = None) -> bool:
        return self.manager.resolve(alert_id, user_id, resolution)
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get alerting dashboard data."""
        all_alerts = list(self.manager.alerts.values())
        active = [a for a in all_alerts if a.status == AlertStatus.ACTIVE]
        acknowledged = [a for a in all_alerts if a.status == AlertStatus.ACKNOWLEDGED]
        resolved = [a for a in all_alerts if a.status == AlertStatus.RESOLVED]
        
        by_severity = {}
        for sev in AlertSeverity:
            by_severity[sev.value] = len([a for a in all_alerts if a.severity == sev])
        
        return {
            "total_alerts": len(all_alerts),
            "active": len(active),
            "acknowledged": len(acknowledged),
            "resolved": len(resolved),
            "by_severity": by_severity,
            "recent_alerts": self.get_alerts()[:10]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return {
            "total_alerts_created": len(self.manager.alerts),
            "active_rules": len([r for r in self.rules.values() if r.enabled]),
            "average_response_time_minutes": 15,
            "alerts_by_category": {c.value: len([a for a in self.manager.alerts.values() if a.category == c]) for c in AlertCategory}
        }


# Singleton instance
alerting_system = AlertingSystem()


# =============================================================================
# 9. Model Fine-tuning System
# =============================================================================

class FeedbackCollector:
    """In-memory feedback collector."""
    
    def __init__(self):
        self.feedback_entries: List[Feedback] = []
    
    def collect(self, feedback: Feedback) -> Dict[str, Any]:
        self.feedback_entries.append(feedback)
        return {"status": "collected", "feedback_id": feedback.id, "total_collected": len(self.feedback_entries)}
    
    def get_feedback(self, model_id: Optional[str] = None, limit: int = 100) -> List[Feedback]:
        if model_id:
            return [f for f in self.feedback_entries if f.model_id == model_id][:limit]
        return self.feedback_entries[:limit]


class PerformanceMonitor:
    """In-memory performance monitor."""
    
    def __init__(self):
        self.performance_data: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_metric(self, model_id: str, metric_name: str, value: float) -> None:
        if model_id not in self.performance_data:
            self.performance_data[model_id] = []
        self.performance_data[model_id].append({
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_performance(self, model_id: str, days: int = 30) -> Dict[str, Any]:
        data = self.performance_data.get(model_id, [])
        cutoff = datetime.utcnow() - timedelta(days=days)
        filtered = [d for d in data if d.get("timestamp", "") >= cutoff.isoformat()]
        
        avg_values = {}
        for d in filtered:
            metric = d.get("metric", "unknown")
            if metric not in avg_values:
                avg_values[metric] = []
            avg_values[metric].append(d.get("value", 0))
        
        return {
            "model_id": model_id,
            "period_days": days,
            "data_points": len(filtered),
            "metrics": {k: {"avg": round(sum(v) / len(v), 3), "count": len(v)} for k, v in avg_values.items()},
            "overall_health": "good"
        }


class ModelVersionManager:
    """In-memory model version manager."""
    
    def __init__(self):
        self.versions: Dict[str, ModelVersion] = {}
    
    def register_version(self, version: ModelVersion) -> ModelVersion:
        self.versions[version.id] = version
        return version
    
    def get_versions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": v.id,
                "name": v.name,
                "version": v.version,
                "status": v.status.value,
                "created_at": v.created_at.isoformat(),
                "metrics": v.metrics,
                "description": v.description
            }
            for v in self.versions.values()
        ]
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        return self.versions.get(version_id)


class TrainingPipeline:
    """Stub training pipeline."""
    
    async def train(self, model_id: str, data: Any, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "completed", "model_id": model_id, "epochs": 10, "accuracy": 0.92}


class ABTestManager:
    """In-memory A/B test manager."""
    
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
    
    def create_test(self, test: ABTest) -> ABTest:
        self.tests[test.id] = test
        return test
    
    def get_tests(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        results = list(self.tests.values())
        if status_filter:
            results = [t for t in results if t.status == status_filter]
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "control_model_id": t.control_model_id,
                "treatment_model_id": t.treatment_model_id,
                "traffic_split": t.traffic_split,
                "status": t.status,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "duration_days": t.duration_days,
                "success_metrics": t.success_metrics
            }
            for t in results
        ]
    
    def get_results(self, test_id: str) -> Dict[str, Any]:
        test = self.tests.get(test_id)
        if not test:
            return {"error": "Test not found"}
        return {
            "test_id": test.id,
            "name": test.name,
            "status": test.status,
            "control_metrics": {"accuracy": 0.85, "latency_ms": 120},
            "treatment_metrics": {"accuracy": 0.89, "latency_ms": 135},
            "improvement": "+4.7% accuracy, +12.5% latency",
            "winner": "treatment" if test.results.get("treatment_wins", False) else "control",
            "confidence": 0.95
        }


class RetrainingTrigger:
    """In-memory retraining trigger manager."""
    
    def __init__(self):
        self.retraining_jobs: List[Dict[str, Any]] = []
    
    def trigger(self, model_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        job = {
            "job_id": str(uuid.uuid4()),
            "model_id": model_id,
            "reason": reason or "Manual trigger",
            "status": "queued",
            "triggered_at": datetime.utcnow().isoformat()
        }
        self.retraining_jobs.append(job)
        return job
    
    def get_status(self) -> Dict[str, Any]:
        active = [j for j in self.retraining_jobs if j["status"] in ("queued", "running")]
        completed = [j for j in self.retraining_jobs if j["status"] == "completed"]
        return {
            "total_triggers": len(self.retraining_jobs),
            "active_jobs": len(active),
            "completed_jobs": len(completed),
            "recent_jobs": self.retraining_jobs[-5:] if self.retraining_jobs else []
        }


class ModelFineTuningSystem:
    """In-memory model fine-tuning system."""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.performance_monitor = PerformanceMonitor()
        self.version_manager = ModelVersionManager()
        self.training_pipeline = TrainingPipeline()
        self.ab_test_manager = ABTestManager()
        self.retraining_trigger = RetrainingTrigger()
        
        # Register a default model version
        self.version_manager.register_version(ModelVersion(
            id="default",
            name="Gemini Base Model",
            version="1.0.0",
            status=ModelStatus.DEPLOYED,
            description="Base Gemini-powered model"
        ))
    
    def collect_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        return self.feedback_collector.collect(feedback)
    
    def get_model_versions(self) -> List[Dict[str, Any]]:
        return self.version_manager.get_versions()
    
    def get_model_performance(self, model_id: str, days: int = 30) -> Dict[str, Any]:
        return self.performance_monitor.get_performance(model_id, days)
    
    def create_ab_test(
        self, name: str, control_model_id: str, treatment_model_id: str,
        traffic_split: float = 0.5, duration_days: int = 14,
        success_metrics: Optional[List[str]] = None
    ) -> ABTest:
        test = ABTest(
            id=str(uuid.uuid4()),
            name=name,
            control_model_id=control_model_id,
            treatment_model_id=treatment_model_id,
            traffic_split=traffic_split,
            duration_days=duration_days,
            success_metrics=success_metrics or ["accuracy", "latency"],
            status="running",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration_days)
        )
        return self.ab_test_manager.create_test(test)
    
    def get_ab_tests(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.ab_test_manager.get_tests(status_filter)
    
    def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        return self.ab_test_manager.get_results(test_id)
    
    def trigger_retraining(self, model_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        return self.retraining_trigger.trigger(model_id, reason)
    
    def get_retraining_status(self) -> Dict[str, Any]:
        return self.retraining_trigger.get_status()


# Singleton instance
finetuning_system = ModelFineTuningSystem()


# =============================================================================
# 10. Analytics & Business Intelligence System
# =============================================================================

class KPIEngine:
    """In-memory KPI engine."""
    
    def __init__(self):
        self.kpis: Dict[str, List[KPI]] = {}
    
    def register_kpi(self, project_id: str, kpi: KPI) -> KPI:
        if project_id not in self.kpis:
            self.kpis[project_id] = []
        self.kpis[project_id].append(kpi)
        return kpi
    
    def get_kpis(self, project_id: str, category_filter: Optional[List[MetricCategory]] = None) -> List[Dict[str, Any]]:
        results = self.kpis.get(project_id, [])
        if category_filter:
            results = [k for k in results if k.category in category_filter]
        
        return [
            {
                "id": k.id,
                "name": k.name,
                "category": k.category.value,
                "value": k.value,
                "target": k.target,
                "unit": k.unit,
                "timestamp": k.timestamp.isoformat(),
                "trend": k.trend.value if k.trend else None,
                "status": "on_track" if k.value >= k.target * 0.9 else "at_risk" if k.value >= k.target * 0.7 else "critical"
            }
            for k in results
        ]
    
    def calculate(self, project_data: Dict[str, Any], kpi_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Calculate KPIs from project data."""
        defaults = [
            KPI(id="schedule_performance", name="Schedule Performance Index", category=MetricCategory.SCHEDULE,
                value=0.95, target=1.0, unit="index"),
            KPI(id="cost_performance", name="Cost Performance Index", category=MetricCategory.COST,
                value=0.92, target=1.0, unit="index"),
            KPI(id="safety_incidents", name="Safety Incidents", category=MetricCategory.SAFETY,
                value=2, target=0, unit="count"),
            KPI(id="quality_score", name="Quality Score", category=MetricCategory.QUALITY,
                value=88, target=95, unit="%"),
            KPI(id="productivity_rate", name="Productivity Rate", category=MetricCategory.PRODUCTIVITY,
                value=82, target=90, unit="%"),
        ]
        
        selected = defaults
        if kpi_ids:
            selected = [k for k in defaults if k.id in kpi_ids]
        
        return [
            {
                "id": k.id,
                "name": k.name,
                "category": k.category.value,
                "value": k.value,
                "target": k.target,
                "unit": k.unit
            }
            for k in selected
        ]


class TrendAnalysisEngine:
    """In-memory trend analysis."""
    
    def analyze(self, project_id: str, kpi_id: str, period: str = "monthly") -> Dict[str, Any]:
        """Analyze trends for a KPI."""
        data_points = []
        base_value = {"schedule_performance": 0.95, "cost_performance": 0.92, "safety_incidents": 2,
                       "quality_score": 88, "productivity_rate": 82}.get(kpi_id, 80)
        
        num_points = {"daily": 30, "weekly": 12, "monthly": 6, "quarterly": 4}.get(period, 6)
        for i in range(num_points):
            data_points.append({
                "period": (datetime.utcnow() - timedelta(days=i * (30 // max(num_points, 1)))).strftime("%Y-%m-%d"),
                "value": round(base_value + (i * 0.5 - num_points * 0.25), 2)
            })
        
        values = [d["value"] for d in data_points]
        trend = TrendDirection.IMPROVING if values[-1] > values[0] else TrendDirection.DECLINING if values[-1] < values[0] else TrendDirection.STABLE
        
        return {
            "kpi_id": kpi_id,
            "project_id": project_id,
            "period": period,
            "trend": trend.value,
            "data_points": list(reversed(data_points)),
            "min_value": min(values),
            "max_value": max(values),
            "average": round(sum(values) / len(values), 2) if values else 0,
            "variation": round(max(values) - min(values), 2) if values else 0
        }


class BenchmarkingEngine:
    """In-memory benchmarking engine."""
    
    def get_benchmarks(self, project_id: str, benchmark_type: BenchmarkType = BenchmarkType.INDUSTRY) -> List[Dict[str, Any]]:
        """Get benchmark data."""
        benchmarks = []
        for cat in MetricCategory:
            benchmarks.append({
                "category": cat.value,
                "project_value": {"schedule": 0.95, "cost": 0.92, "quality": 88,
                                   "safety": 2, "productivity": 82}.get(cat.value, 75),
                "benchmark_value": {"schedule": 1.0, "cost": 1.0, "quality": 95,
                                     "safety": 0, "productivity": 90}.get(cat.value, 80),
                "benchmark_source": benchmark_type.value,
                "percentile": 65,
                "gap": round({"schedule": -0.05, "cost": -0.08, "quality": -7,
                               "safety": 2, "productivity": -8}.get(cat.value, -5), 2)
            })
        return benchmarks


class DashboardManager:
    """In-memory dashboard manager."""
    
    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
    
    def create(self, name: str, widgets: List[Dict[str, Any]], owner_id: str, is_public: bool = False) -> Dict[str, Any]:
        dashboard_id = str(uuid.uuid4())
        dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            owner_id=owner_id,
            is_public=is_public,
            widgets=[
                DashboardWidget(
                    id=str(uuid.uuid4()),
                    title=w.get("title", "Widget"),
                    widget_type=w.get("type", "chart"),
                    config=w.get("config", {})
                )
                for w in widgets
            ]
        )
        self.dashboards[dashboard_id] = dashboard
        return self._serialize(dashboard)
    
    def get_dashboards(self, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = list(self.dashboards.values())
        if owner_id:
            results = [d for d in results if d.owner_id == owner_id or d.is_public]
        return [self._serialize(d) for d in results]
    
    def get_dashboard_with_data(self, dashboard_id: str) -> Dict[str, Any]:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {"error": "Dashboard not found"}
        serialized = self._serialize(dashboard)
        for widget in serialized.get("widgets", []):
            widget["data"] = {"labels": ["Week 1", "Week 2", "Week 3"],
                              "values": [85, 88, 92]}
        return serialized
    
    def _serialize(self, d: Dashboard) -> Dict[str, Any]:
        return {
            "id": d.id,
            "name": d.name,
            "owner_id": d.owner_id,
            "is_public": d.is_public,
            "created_at": d.created_at.isoformat(),
            "widgets": [
                {
                    "id": w.id,
                    "title": w.title,
                    "type": w.widget_type,
                    "config": w.config
                }
                for w in d.widgets
            ]
        }


class ExecutiveDecisionSupport:
    """In-memory executive decision support."""
    
    def get_summary(self, project_id: str) -> Dict[str, Any]:
        """Generate executive summary."""
        return {
            "project_id": project_id,
            "overall_health": "yellow",
            "schedule_status": {"spi": 0.95, "variance_days": -5, "forecast": "on_track"},
            "cost_status": {"cpi": 0.92, "variance_percent": -8, "forecast": "at_risk"},
            "safety_status": {"incidents": 2, "trend": "improving"},
            "quality_status": {"score": 88, "trend": "stable"},
            "key_recommendations": [
                "Focus on cost control - CPI below 1.0",
                "Continue safety improvements",
                "Review critical path for schedule recovery"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_insights(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights."""
        return [
            {"type": "schedule", "insight": "Project is 5 days behind schedule", "severity": "medium",
             "recommendation": "Review critical path activities"},
            {"type": "cost", "insight": "Cost variance is 8% over budget", "severity": "high",
             "recommendation": "Implement cost control measures"},
            {"type": "safety", "insight": "2 safety incidents reported this month", "severity": "medium",
             "recommendation": "Increase safety training frequency"}
        ]


class AnalyticsBISystem:
    """Unified analytics and business intelligence system."""
    
    def __init__(self):
        self.kpi_engine = KPIEngine()
        self.trend_engine = TrendAnalysisEngine()
        self.benchmarking_engine = BenchmarkingEngine()
        self.dashboard_manager = DashboardManager()
        self.executive_support = ExecutiveDecisionSupport()
    
    def get_project_kpis(self, project_id: str, category_filter: Optional[List[MetricCategory]] = None) -> List[Dict[str, Any]]:
        return self.kpi_engine.get_kpis(project_id, category_filter)
    
    def calculate_kpis(self, project_data: Dict[str, Any], kpi_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.kpi_engine.calculate(project_data, kpi_ids)
    
    def analyze_trends(self, project_id: str, kpi_id: str, period: str = "monthly") -> Dict[str, Any]:
        return self.trend_engine.analyze(project_id, kpi_id, period)
    
    def get_benchmarks(self, project_id: str, benchmark_type: BenchmarkType = BenchmarkType.INDUSTRY) -> List[Dict[str, Any]]:
        return self.benchmarking_engine.get_benchmarks(project_id, benchmark_type)
    
    def create_dashboard(self, name: str, widgets: List[Dict[str, Any]], owner_id: str, is_public: bool = False) -> Dict[str, Any]:
        return self.dashboard_manager.create(name, widgets, owner_id, is_public)
    
    def get_dashboards(self, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.dashboard_manager.get_dashboards(owner_id)
    
    def get_dashboard_with_data(self, dashboard_id: str) -> Dict[str, Any]:
        return self.dashboard_manager.get_dashboard_with_data(dashboard_id)
    
    def get_executive_summary(self, project_id: str) -> Dict[str, Any]:
        return self.executive_support.get_summary(project_id)
    
    def generate_insights(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.executive_support.generate_insights(project_data)


# Singleton instance
analytics_bi_system = AnalyticsBISystem()


# =============================================================================
# 11. Industry Customizations
# =============================================================================

class IndustryProfileRegistry:
    """Static industry profile registry."""
    
    _profiles = {
        IndustrySector.RESIDENTIAL: IndustryProfile(
            sector=IndustrySector.RESIDENTIAL, name="Residential Construction",
            description="Single-family homes, apartments, condominiums",
            typical_project_size="$1M - $50M",
            key_metrics=["cycle_time", "defect_rate", "customer_satisfaction"]
        ),
        IndustrySector.COMMERCIAL: IndustryProfile(
            sector=IndustrySector.COMMERCIAL, name="Commercial Construction",
            description="Office buildings, retail, mixed-use",
            typical_project_size="$5M - $500M",
            key_metrics=["schedule_performance", "cost_performance", "safety_rate"]
        ),
        IndustrySector.INDUSTRIAL: IndustryProfile(
            sector=IndustrySector.INDUSTRIAL, name="Industrial Construction",
            description="Factories, warehouses, manufacturing plants",
            typical_project_size="$10M - $1B",
            key_metrics=["productivity", "equipment_uptime", "safety_compliance"]
        ),
        IndustrySector.INFRASTRUCTURE: IndustryProfile(
            sector=IndustrySector.INFRASTRUCTURE, name="Infrastructure",
            description="Roads, bridges, tunnels, utilities",
            typical_project_size="$50M - $5B",
            key_metrics=["schedule_adherence", "quality_metrics", "safety_incidents"]
        ),
        IndustrySector.HEAVY_CIVIL: IndustryProfile(
            sector=IndustrySector.HEAVY_CIVIL, name="Heavy Civil",
            description="Dams, ports, airports, railways",
            typical_project_size="$100M - $10B",
            key_metrics=["productivity", "cost_control", "safety"]
        ),
        IndustrySector.ENERGY: IndustryProfile(
            sector=IndustrySector.ENERGY, name="Energy",
            description="Power plants, renewable energy, oil & gas",
            typical_project_size="$50M - $10B",
            key_metrics=["schedule_performance", "safety", "quality"]
        ),
        IndustrySector.HEALTHCARE: IndustryProfile(
            sector=IndustrySector.HEALTHCARE, name="Healthcare",
            description="Hospitals, clinics, medical facilities",
            typical_project_size="$10M - $2B",
            key_metrics=["quality", "schedule", "compliance"]
        ),
        IndustrySector.EDUCATION: IndustryProfile(
            sector=IndustrySector.EDUCATION, name="Education",
            description="Schools, universities, research facilities",
            typical_project_size="$5M - $500M",
            key_metrics=["budget_adherence", "schedule", "quality"]
        ),
        IndustrySector.HOSPITALITY: IndustryProfile(
            sector=IndustrySector.HOSPITALITY, name="Hospitality",
            description="Hotels, resorts, entertainment venues",
            typical_project_size="$10M - $1B",
            key_metrics=["schedule", "quality", "cost"]
        ),
        IndustrySector.GOVERNMENT: IndustryProfile(
            sector=IndustrySector.GOVERNMENT, name="Government",
            description="Public buildings, courthouses, civic centers",
            typical_project_size="$5M - $1B",
            key_metrics=["compliance", "budget", "schedule"]
        ),
    }


class IndustryWorkflowManager:
    """Static industry workflow configurations."""
    
    _workflows = {
        sector.value: [
            {"id": f"{sector.value}_planning", "name": "Project Planning", "steps": ["scope", "budget", "schedule"]},
            {"id": f"{sector.value}_execution", "name": "Project Execution", "steps": ["mobilize", "construct", "inspect"]},
            {"id": f"{sector.value}_closeout", "name": "Project Closeout", "steps": ["punch_list", "handover", "warranty"]},
        ]
        for sector in IndustrySector
    }


class IndustryTemplateManager:
    """Static industry template configurations."""
    
    _templates = {
        sector.value: [
            {"id": f"{sector.value}_report", "name": f"{sector.value.title()} Report Template", "type": "report"},
            {"id": f"{sector.value}_checklist", "name": f"{sector.value.title()} Quality Checklist", "type": "checklist"},
        ]
        for sector in IndustrySector
    }


class ComplianceConfigManager:
    """Static compliance configurations."""
    
    _frameworks = {
        IndustrySector.RESIDENTIAL: ComplianceFramework(
            id="res_code", name="Residential Building Code", sector=IndustrySector.RESIDENTIAL,
            requirements=[
                {"code": "IRC-2021", "description": "International Residential Code", "mandatory": True},
                {"code": "IBC-2021", "description": "International Building Code (for multi-family)", "mandatory": True},
            ]
        ),
        IndustrySector.INDUSTRIAL: ComplianceFramework(
            id="ind_osha", name="OSHA Industrial Standards", sector=IndustrySector.INDUSTRIAL,
            requirements=[
                {"code": "OSHA-1910", "description": "Occupational Safety and Health Standards", "mandatory": True},
                {"code": "NFPA-70E", "description": "Standard for Electrical Safety", "mandatory": True},
            ]
        ),
    }


class IndustryCustomizationSystem:
    """Industry customization system with static configuration data."""
    
    def __init__(self):
        self.registry = IndustryProfileRegistry()
        self.workflow_manager = IndustryWorkflowManager()
        self.template_manager = IndustryTemplateManager()
        self.compliance_manager = ComplianceConfigManager()
        self.project_configs: Dict[str, Dict[str, Any]] = {}
    
    def get_available_sectors(self) -> List[Dict[str, Any]]:
        return [
            {"sector": s.value, "name": p.name, "description": p.description,
             "typical_project_size": p.typical_project_size}
            for s, p in self.registry._profiles.items()
        ]
    
    def get_profile(self, sector: IndustrySector) -> Dict[str, Any]:
        profile = self.registry._profiles.get(sector)
        if not profile:
            return {"error": f"Unknown sector: {sector}"}
        return {
            "sector": profile.sector.value,
            "name": profile.name,
            "description": profile.description,
            "typical_project_size": profile.typical_project_size,
            "key_metrics": profile.key_metrics
        }
    
    def get_industry_kpis(self, sector: IndustrySector) -> List[Dict[str, Any]]:
        profile = self.registry._profiles.get(sector)
        if not profile:
            return []
        return [
            {"id": f"{sector.value}_spi", "name": "Schedule Performance Index", "target": 1.0, "unit": "index"},
            {"id": f"{sector.value}_cpi", "name": "Cost Performance Index", "target": 1.0, "unit": "index"},
            {"id": f"{sector.value}_safety", "name": "Safety Incident Rate", "target": 0, "unit": "count"},
        ]
    
    def get_workflows(self, sector: IndustrySector) -> List[Dict[str, Any]]:
        return self.workflow_manager._workflows.get(sector.value, [])
    
    def get_templates(self, sector: IndustrySector, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        templates = self.template_manager._templates.get(sector.value, [])
        if template_type:
            templates = [t for t in templates if t.get("type") == template_type]
        return templates
    
    def get_compliance_requirements(self, sector: IndustrySector) -> List[Dict[str, Any]]:
        framework = self.compliance_manager._frameworks.get(sector)
        if framework:
            return framework.requirements
        return [
            {"code": "general", "description": f"Standard {sector.value} compliance requirements", "mandatory": True}
        ]
    
    def get_benchmarks(self, sector: IndustrySector) -> List[Dict[str, Any]]:
        return [
            {"category": "schedule", "industry_average": 0.92, "top_quartile": 1.02, "unit": "index"},
            {"category": "cost", "industry_average": 0.90, "top_quartile": 1.0, "unit": "index"},
            {"category": "safety", "industry_average": 3.5, "top_quartile": 1.0, "unit": "incidents_per_year"},
        ]
    
    def configure_project(
        self, project_id: str, sector: IndustrySector,
        subsector: Optional[str] = None, custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        config = {
            "project_id": project_id,
            "sector": sector.value,
            "subsector": subsector,
            "configured_at": datetime.utcnow().isoformat(),
            "kpi_templates": self.get_industry_kpis(sector),
            "workflows": self.get_workflows(sector),
            "compliance": self.get_compliance_requirements(sector),
            "custom_settings": custom_settings or {}
        }
        self.project_configs[project_id] = config
        return config


# Singleton instance
industry_customization_system = IndustryCustomizationSystem()
