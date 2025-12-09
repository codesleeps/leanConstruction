"""
LeanConstruction AI - Machine Learning Package

Phase 2 Core AI Development:
- Computer Vision for site progress monitoring (ResNet-based CNN)
- Waste Detection using DOWNTIME framework
- Predictive Models for schedule and cost forecasting (LSTM + Ensemble)
- Automated Reporting System

Phase 3 Advanced Features:
- Advanced Lean Tools (VSM, 5S, Kaizen, Kanban, A3)
- NLP Analysis for documents and communications
- Resource Optimization (OR-Tools based)
- Real-time Alerting System

Phase 4 Optimization and Scale:
- Model Fine-tuning with feedback collection and A/B testing
- Advanced Analytics and Business Intelligence
- Industry-specific Customizations
"""

# Computer Vision Models
from .computer_vision import (
    ProgressMonitoringModel,
    ProgressMonitoringPipeline,
    SafetyComplianceDetector,
    EquipmentTracker,
    WorkplaceOrganizationAnalyzer,
    ModelTrainer,
    ConstructionStage
)

# Waste Detection (DOWNTIME Framework)
from .waste_detection import (
    WasteDetectionEngine,
    WasteType,
    DefectsDetector,
    OverproductionDetector,
    WaitingDetector,
    NonUtilizedTalentDetector,
    TransportationDetector,
    InventoryDetector,
    MotionDetector,
    ExtraProcessingDetector
)

# Predictive Models
from .predictive_models import (
    IntegratedForecastingSystem,
    ScheduleForecastingModel,
    ScheduleForecastingLSTM,
    CostPredictionEnsemble,
    ResourceOptimizer as PredictiveResourceOptimizer,
    RiskLevel
)

# Automated Reporting
from .reporting import (
    AutomatedReportingSystem,
    ReportType,
    ReportFormat,
    ReportSection,
    ReportMetadata,
    ProgressReportGenerator,
    WasteReportGenerator,
    ForecastReportGenerator,
    SafetyReportGenerator,
    WorkplaceOrganizationReportGenerator,
    generate_project_report
)

# Phase 3 - Lean Tools
from .lean_tools import (
    LeanToolsIntegration,
    lean_tools,
    ValueStreamMapper,
    ValueStreamMetrics,
    ProcessStep,
    ProcessType,
    S5AnalysisSystem,
    S5Category,
    S5Score,
    KaizenManager,
    KaizenEvent,
    KaizenType,
    KanbanBoard,
    KanbanCard,
    KanbanStatus,
    A3ProblemSolver
)

# Phase 3 - NLP Analysis
from .nlp_analysis import (
    ConstructionNLPSystem,
    nlp_system,
    DocumentClassifier,
    DocumentType,
    ConstructionNER,
    EntityType,
    CommunicationAnalyzer,
    SentimentLevel,
    UrgencyLevel,
    DocumentSummarizer,
    RiskIssueExtractor,
    ContractAnalyzer
)

# Phase 3 - Resource Optimization
from .resource_optimizer import (
    ResourceOptimizationSystem,
    resource_optimizer,
    CrewSchedulingOptimizer,
    EquipmentOptimizer,
    DeliveryOptimizer,
    ResourceLeveler,
    CostOptimizer,
    ResourceType,
    SkillType,
    EquipmentType,
    OptimizationObjective
)

# Phase 3 - Alerting System
from .alerting import (
    AlertingSystem,
    alerting_system,
    AlertManager,
    AlertRule,
    AlertRuleBuilder,
    Alert,
    AlertSeverity,
    AlertCategory,
    AlertStatus,
    NotificationChannel,
    ConstructionAlertRules
)

# Phase 4 - Model Fine-tuning
from .model_finetuning import (
    ModelFineTuningSystem,
    finetuning_system,
    FeedbackCollector,
    FeedbackType,
    FeedbackEntry,
    PerformanceMonitor,
    ModelVersionManager,
    ModelVersion,
    ModelStatus,
    TrainingPipeline,
    TrainingConfig,
    ABTestManager,
    ABTest,
    ABTestStatus,
    RetrainingTrigger,
    TriggerCondition
)

# Phase 4 - Analytics and Business Intelligence
from .analytics_bi import (
    AnalyticsBISystem,
    analytics_bi_system,
    KPIEngine,
    KPIDefinition,
    KPICategory,
    KPIValue,
    TrendAnalysisEngine,
    TrendPeriod,
    TrendResult,
    BenchmarkingEngine,
    BenchmarkType,
    BenchmarkResult,
    DashboardManager,
    Dashboard,
    DashboardWidget,
    WidgetType,
    ExecutiveDecisionSupport
)

# Phase 4 - Industry Customizations
from .industry_customizations import (
    IndustryCustomizationSystem,
    industry_customization_system,
    IndustryProfileManager,
    IndustryProfile,
    IndustrySector,
    IndustryKPIConfiguration,
    IndustryWorkflow,
    WorkflowStep,
    IndustryTemplateManager,
    ProjectTemplate,
    ReportTemplate,
    IndustryComplianceManager,
    ComplianceFramework,
    ComplianceRequirement,
    IndustryBenchmarks
)

__all__ = [
    # Computer Vision
    'ProgressMonitoringModel',
    'ProgressMonitoringPipeline',
    'SafetyComplianceDetector',
    'EquipmentTracker',
    'WorkplaceOrganizationAnalyzer',
    'ModelTrainer',
    'ConstructionStage',
    
    # Waste Detection
    'WasteDetectionEngine',
    'WasteType',
    'DefectsDetector',
    'OverproductionDetector',
    'WaitingDetector',
    'NonUtilizedTalentDetector',
    'TransportationDetector',
    'InventoryDetector',
    'MotionDetector',
    'ExtraProcessingDetector',
    
    # Predictive Models
    'IntegratedForecastingSystem',
    'ScheduleForecastingModel',
    'ScheduleForecastingLSTM',
    'CostPredictionEnsemble',
    'PredictiveResourceOptimizer',
    'RiskLevel',
    
    # Reporting
    'AutomatedReportingSystem',
    'ReportType',
    'ReportFormat',
    'ReportSection',
    'ReportMetadata',
    'ProgressReportGenerator',
    'WasteReportGenerator',
    'ForecastReportGenerator',
    'SafetyReportGenerator',
    'WorkplaceOrganizationReportGenerator',
    'generate_project_report',
    
    # Phase 3 - Lean Tools
    'LeanToolsIntegration',
    'lean_tools',
    'ValueStreamMapper',
    'ValueStreamMetrics',
    'ProcessStep',
    'ProcessType',
    'S5AnalysisSystem',
    'S5Category',
    'S5Score',
    'KaizenManager',
    'KaizenEvent',
    'KaizenType',
    'KanbanBoard',
    'KanbanCard',
    'KanbanStatus',
    'A3ProblemSolver',
    
    # Phase 3 - NLP Analysis
    'ConstructionNLPSystem',
    'nlp_system',
    'DocumentClassifier',
    'DocumentType',
    'ConstructionNER',
    'EntityType',
    'CommunicationAnalyzer',
    'SentimentLevel',
    'UrgencyLevel',
    'DocumentSummarizer',
    'RiskIssueExtractor',
    'ContractAnalyzer',
    
    # Phase 3 - Resource Optimization
    'ResourceOptimizationSystem',
    'resource_optimizer',
    'CrewSchedulingOptimizer',
    'EquipmentOptimizer',
    'DeliveryOptimizer',
    'ResourceLeveler',
    'CostOptimizer',
    'ResourceType',
    'SkillType',
    'EquipmentType',
    'OptimizationObjective',
    
    # Phase 3 - Alerting
    'AlertingSystem',
    'alerting_system',
    'AlertManager',
    'AlertRule',
    'AlertRuleBuilder',
    'Alert',
    'AlertSeverity',
    'AlertCategory',
    'AlertStatus',
    'NotificationChannel',
    'ConstructionAlertRules',
    
    # Phase 4 - Model Fine-tuning
    'ModelFineTuningSystem',
    'finetuning_system',
    'FeedbackCollector',
    'FeedbackType',
    'FeedbackEntry',
    'PerformanceMonitor',
    'ModelVersionManager',
    'ModelVersion',
    'ModelStatus',
    'TrainingPipeline',
    'TrainingConfig',
    'ABTestManager',
    'ABTest',
    'ABTestStatus',
    'RetrainingTrigger',
    'TriggerCondition',
    
    # Phase 4 - Analytics and BI
    'AnalyticsBISystem',
    'analytics_bi_system',
    'KPIEngine',
    'KPIDefinition',
    'KPICategory',
    'KPIValue',
    'TrendAnalysisEngine',
    'TrendPeriod',
    'TrendResult',
    'BenchmarkingEngine',
    'BenchmarkType',
    'BenchmarkResult',
    'DashboardManager',
    'Dashboard',
    'DashboardWidget',
    'WidgetType',
    'ExecutiveDecisionSupport',
    
    # Phase 4 - Industry Customizations
    'IndustryCustomizationSystem',
    'industry_customization_system',
    'IndustryProfileManager',
    'IndustryProfile',
    'IndustrySector',
    'IndustryKPIConfiguration',
    'IndustryWorkflow',
    'WorkflowStep',
    'IndustryTemplateManager',
    'ProjectTemplate',
    'ReportTemplate',
    'IndustryComplianceManager',
    'ComplianceFramework',
    'ComplianceRequirement',
    'IndustryBenchmarks'
]

__version__ = '4.0.0'
