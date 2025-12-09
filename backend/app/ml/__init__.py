"""
LeanConstruction AI - Machine Learning Package

Phase 2 Core AI Development:
- Computer Vision for site progress monitoring (ResNet-based CNN)
- Waste Detection using DOWNTIME framework
- Predictive Models for schedule and cost forecasting (LSTM + Ensemble)
- Automated Reporting System
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
    ResourceOptimizer,
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
    'ResourceOptimizer',
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
    'generate_project_report'
]

__version__ = '2.0.0'
