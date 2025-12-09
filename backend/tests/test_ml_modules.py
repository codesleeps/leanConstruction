"""
Unit tests for Phase 2 ML modules

Tests cover:
- Computer Vision (Progress Monitoring, Safety Detection)
- Waste Detection (DOWNTIME Framework)
- Predictive Models (Schedule, Cost Forecasting)
- Automated Reporting System
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import torch

# Import fixtures
from .fixtures.sample_data import (
    generate_sample_project_data,
    generate_progress_data,
    generate_waste_data,
    generate_forecast_data,
    generate_safety_data,
    generate_workplace_organization_data,
    generate_historical_data,
    SAMPLE_PROJECT,
    SAMPLE_PROJECTS
)


class TestComputerVisionModule:
    """Tests for computer vision progress monitoring"""
    
    def test_construction_stage_enum(self):
        """Test construction stage enumeration"""
        from backend.app.ml.computer_vision import ConstructionStage
        
        # Verify all stages exist
        stages = [
            'SITE_PREPARATION', 'FOUNDATION', 'STRUCTURAL',
            'MEP_ROUGH_IN', 'ENCLOSURE', 'INTERIOR_ROUGH_IN',
            'INTERIOR_FINISHES', 'COMMISSIONING', 'UNKNOWN'
        ]
        
        for stage in stages:
            assert hasattr(ConstructionStage, stage)
    
    def test_progress_monitoring_model_initialization(self):
        """Test model initialization without pretrained weights"""
        from backend.app.ml.computer_vision import ProgressMonitoringModel
        
        # Test with mock path (no actual model file)
        model = ProgressMonitoringModel(model_path=None)
        
        assert model is not None
        assert hasattr(model, 'num_classes')
    
    def test_progress_monitoring_pipeline_initialization(self):
        """Test pipeline initialization"""
        from backend.app.ml.computer_vision import ProgressMonitoringPipeline
        
        pipeline = ProgressMonitoringPipeline(model_path=None)
        
        assert pipeline is not None
        assert hasattr(pipeline, 'analyze_image')
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_model_device_handling(self):
        """Test model can handle different devices"""
        from backend.app.ml.computer_vision import ProgressMonitoringModel
        
        model = ProgressMonitoringModel(model_path=None)
        
        # Model should be on appropriate device
        assert model.device is not None
    
    def test_safety_compliance_detector_initialization(self):
        """Test safety detector initialization"""
        from backend.app.ml.computer_vision import SafetyComplianceDetector
        
        detector = SafetyComplianceDetector()
        
        assert detector is not None
        assert hasattr(detector, 'ppe_classes')
    
    def test_equipment_tracker_initialization(self):
        """Test equipment tracker initialization"""
        from backend.app.ml.computer_vision import EquipmentTracker
        
        tracker = EquipmentTracker()
        
        assert tracker is not None
        assert hasattr(tracker, 'equipment_classes')
    
    def test_workplace_organization_analyzer(self):
        """Test 5S workplace analyzer initialization"""
        from backend.app.ml.computer_vision import WorkplaceOrganizationAnalyzer
        
        analyzer = WorkplaceOrganizationAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_5s')


class TestWasteDetectionModule:
    """Tests for DOWNTIME waste detection framework"""
    
    def test_waste_type_enum(self):
        """Test waste type enumeration"""
        from backend.app.ml.waste_detection import WasteType
        
        # Verify all 8 DOWNTIME wastes
        wastes = [
            'DEFECTS', 'OVERPRODUCTION', 'WAITING',
            'NON_UTILIZED_TALENT', 'TRANSPORTATION',
            'INVENTORY', 'MOTION', 'EXTRA_PROCESSING'
        ]
        
        for waste in wastes:
            assert hasattr(WasteType, waste)
    
    def test_waste_detection_engine_initialization(self):
        """Test waste detection engine initialization"""
        from backend.app.ml.waste_detection import WasteDetectionEngine
        
        engine = WasteDetectionEngine()
        
        assert engine is not None
        assert hasattr(engine, 'detectors')
        assert len(engine.detectors) == 8  # 8 DOWNTIME wastes
    
    def test_waste_detection_engine_analyze(self):
        """Test waste analysis with sample data"""
        from backend.app.ml.waste_detection import WasteDetectionEngine
        
        engine = WasteDetectionEngine()
        
        # Use generated sample data
        project_data = SAMPLE_PROJECT
        
        result = engine.analyze(project_data)
        
        assert 'detected_wastes' in result
        assert 'overall_waste_score' in result
        assert 'health_status' in result
        assert 'priority_actions' in result
    
    def test_individual_waste_detectors(self):
        """Test individual waste detector classes"""
        from backend.app.ml.waste_detection import (
            DefectsDetector,
            OverproductionDetector,
            WaitingDetector,
            NonUtilizedTalentDetector,
            TransportationDetector,
            InventoryDetector,
            MotionDetector,
            ExtraProcessingDetector
        )
        
        detectors = [
            DefectsDetector(),
            OverproductionDetector(),
            WaitingDetector(),
            NonUtilizedTalentDetector(),
            TransportationDetector(),
            InventoryDetector(),
            MotionDetector(),
            ExtraProcessingDetector()
        ]
        
        for detector in detectors:
            assert hasattr(detector, 'detect')
            assert hasattr(detector, 'calculate_impact')
    
    def test_waste_severity_calculation(self):
        """Test waste severity score calculation"""
        from backend.app.ml.waste_detection import WasteDetectionEngine
        
        engine = WasteDetectionEngine()
        
        # Test with varying data
        for _ in range(5):
            project_data = generate_sample_project_data()
            result = engine.analyze(project_data)
            
            score = result['overall_waste_score']
            assert 0 <= score <= 1, f"Score {score} out of range"
    
    def test_waste_health_status_mapping(self):
        """Test health status determination"""
        from backend.app.ml.waste_detection import WasteDetectionEngine
        
        engine = WasteDetectionEngine()
        
        valid_statuses = ['healthy', 'moderate', 'poor', 'critical']
        
        for _ in range(10):
            project_data = generate_sample_project_data()
            result = engine.analyze(project_data)
            
            assert result['health_status'] in valid_statuses


class TestPredictiveModelsModule:
    """Tests for schedule and cost forecasting models"""
    
    def test_integrated_forecasting_system_initialization(self):
        """Test integrated forecasting system initialization"""
        from backend.app.ml.predictive_models import IntegratedForecastingSystem
        
        system = IntegratedForecastingSystem()
        
        assert system is not None
        assert hasattr(system, 'schedule_model')
        assert hasattr(system, 'cost_model')
    
    def test_schedule_forecasting_model(self):
        """Test schedule forecasting model"""
        from backend.app.ml.predictive_models import ScheduleForecastingModel
        
        model = ScheduleForecastingModel()
        
        assert model is not None
        assert hasattr(model, 'predict')
    
    def test_cost_prediction_ensemble(self):
        """Test cost prediction ensemble model"""
        from backend.app.ml.predictive_models import CostPredictionEnsemble
        
        ensemble = CostPredictionEnsemble()
        
        assert ensemble is not None
        assert hasattr(ensemble, 'predict')
    
    def test_integrated_forecast_generation(self):
        """Test integrated forecast generation"""
        from backend.app.ml.predictive_models import IntegratedForecastingSystem
        
        system = IntegratedForecastingSystem()
        project_data = SAMPLE_PROJECT
        
        result = system.generate_forecast(project_data)
        
        assert 'schedule_forecast' in result
        assert 'cost_forecast' in result
        assert 'combined_risk_level' in result
        assert 'executive_summary' in result
    
    def test_schedule_forecast_fields(self):
        """Test schedule forecast contains required fields"""
        from backend.app.ml.predictive_models import IntegratedForecastingSystem
        
        system = IntegratedForecastingSystem()
        project_data = SAMPLE_PROJECT
        
        result = system.generate_forecast(project_data)
        schedule = result['schedule_forecast']
        
        required_fields = [
            'predicted_completion_date',
            'schedule_variance_days',
            'confidence_level'
        ]
        
        for field in required_fields:
            assert field in schedule, f"Missing field: {field}"
    
    def test_cost_forecast_fields(self):
        """Test cost forecast contains required fields"""
        from backend.app.ml.predictive_models import IntegratedForecastingSystem
        
        system = IntegratedForecastingSystem()
        project_data = SAMPLE_PROJECT
        
        result = system.generate_forecast(project_data)
        cost = result['cost_forecast']
        
        required_fields = [
            'predicted_final_cost',
            'budget_variance_percentage'
        ]
        
        for field in required_fields:
            assert field in cost, f"Missing field: {field}"
    
    def test_risk_level_enum(self):
        """Test risk level enumeration"""
        from backend.app.ml.predictive_models import RiskLevel
        
        levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        for level in levels:
            assert hasattr(RiskLevel, level)
    
    def test_resource_optimizer(self):
        """Test resource optimizer"""
        from backend.app.ml.predictive_models import ResourceOptimizer
        
        optimizer = ResourceOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize')


class TestReportingModule:
    """Tests for automated reporting system"""
    
    def test_report_type_enum(self):
        """Test report type enumeration"""
        from backend.app.ml.reporting import ReportType
        
        types = [
            'DAILY', 'WEEKLY', 'MONTHLY', 'EXECUTIVE',
            'WASTE_ANALYSIS', 'PROGRESS', 'SAFETY',
            'FORECAST', 'COMPREHENSIVE', 'CUSTOM'
        ]
        
        for report_type in types:
            assert hasattr(ReportType, report_type)
    
    def test_report_format_enum(self):
        """Test report format enumeration"""
        from backend.app.ml.reporting import ReportFormat
        
        formats = ['JSON', 'HTML', 'MARKDOWN', 'PDF']
        
        for fmt in formats:
            assert hasattr(ReportFormat, fmt)
    
    def test_automated_reporting_system_initialization(self):
        """Test reporting system initialization"""
        from backend.app.ml.reporting import AutomatedReportingSystem
        
        system = AutomatedReportingSystem()
        
        assert system is not None
        assert hasattr(system, 'generators')
        assert hasattr(system, 'templates')
    
    def test_report_generators_available(self):
        """Test all report generators are available"""
        from backend.app.ml.reporting import AutomatedReportingSystem
        
        system = AutomatedReportingSystem()
        
        required_generators = ['progress', 'waste', 'forecast', 'safety', 'workplace']
        
        for gen in required_generators:
            assert gen in system.generators, f"Missing generator: {gen}"
    
    def test_daily_report_generation(self):
        """Test daily report generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.DAILY)
        
        assert 'metadata' in report
        assert 'executive_summary' in report
        assert 'sections' in report
    
    def test_weekly_report_generation(self):
        """Test weekly report generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.WEEKLY)
        
        assert len(report['sections']) >= 3  # Progress, waste, safety at minimum
    
    def test_comprehensive_report_generation(self):
        """Test comprehensive report generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.COMPREHENSIVE)
        
        assert len(report['sections']) == 5  # All sections
    
    def test_html_output_format(self):
        """Test HTML output format"""
        from backend.app.ml.reporting import (
            AutomatedReportingSystem, ReportType, ReportFormat
        )
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(
            project_data,
            ReportType.DAILY,
            output_format=ReportFormat.HTML
        )
        
        assert 'html_content' in report
        assert '<!DOCTYPE html>' in report['html_content']
    
    def test_markdown_output_format(self):
        """Test Markdown output format"""
        from backend.app.ml.reporting import (
            AutomatedReportingSystem, ReportType, ReportFormat
        )
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(
            project_data,
            ReportType.DAILY,
            output_format=ReportFormat.MARKDOWN
        )
        
        assert 'markdown_content' in report
        assert '#' in report['markdown_content']  # Markdown headers
    
    def test_report_metadata(self):
        """Test report metadata generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.DAILY)
        metadata = report['metadata']
        
        required_fields = [
            'report_id', 'report_type', 'project_id',
            'project_name', 'generated_at'
        ]
        
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"
    
    def test_executive_summary_generation(self):
        """Test executive summary generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.DAILY)
        summary = report['executive_summary']
        
        assert 'overall_status' in summary
        assert 'status_indicator' in summary
        assert 'narrative' in summary
    
    def test_key_metrics_extraction(self):
        """Test key metrics extraction from sections"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.COMPREHENSIVE)
        
        assert 'key_metrics' in report
    
    def test_action_items_consolidation(self):
        """Test action items consolidation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.COMPREHENSIVE)
        
        assert 'action_items' in report
        
        if report['action_items']:
            item = report['action_items'][0]
            assert 'id' in item
            assert 'category' in item
            assert 'action' in item
            assert 'priority' in item
    
    def test_alerts_generation(self):
        """Test alerts generation"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        report = system.generate_report(project_data, ReportType.COMPREHENSIVE)
        
        assert 'alerts' in report
    
    def test_report_scheduling(self):
        """Test report scheduling"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        
        schedule = system.schedule_report(
            project_id='PROJ-001',
            report_type=ReportType.DAILY,
            schedule='daily',
            recipients=['test@example.com']
        )
        
        assert 'project_id' in schedule
        assert 'next_run' in schedule
        assert schedule['active'] is True
    
    def test_report_history(self):
        """Test report history tracking"""
        from backend.app.ml.reporting import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        project_data = SAMPLE_PROJECT
        
        # Generate a few reports
        for _ in range(3):
            system.generate_report(project_data, ReportType.DAILY)
        
        history = system.get_report_history()
        
        assert len(history) == 3
    
    def test_generate_project_report_convenience_function(self):
        """Test convenience function for report generation"""
        from backend.app.ml.reporting import generate_project_report
        
        report = generate_project_report(
            SAMPLE_PROJECT,
            report_type='daily',
            output_format='json'
        )
        
        assert 'metadata' in report
        assert 'sections' in report


class TestProgressReportGenerator:
    """Tests for progress report generator specifically"""
    
    def test_progress_report_generation(self):
        """Test progress report section generation"""
        from backend.app.ml.reporting import ProgressReportGenerator
        
        generator = ProgressReportGenerator()
        project_data = SAMPLE_PROJECT
        
        section = generator.generate(project_data)
        
        assert section.title == 'Construction Progress'
        assert 'current_stage' in section.content
        assert 'completion_percentage' in section.content
    
    def test_progress_recommendations(self):
        """Test progress recommendations generation"""
        from backend.app.ml.reporting import ProgressReportGenerator
        
        generator = ProgressReportGenerator()
        
        # Test with behind schedule project
        project_data = generate_sample_project_data()
        project_data['progress']['completion_percentage'] = 20
        project_data['progress']['planned_percentage'] = 40  # 20% behind
        
        section = generator.generate(project_data)
        
        assert len(section.recommendations) > 0


class TestWasteReportGenerator:
    """Tests for waste report generator specifically"""
    
    def test_waste_report_generation(self):
        """Test waste report section generation"""
        from backend.app.ml.reporting import WasteReportGenerator
        
        generator = WasteReportGenerator()
        project_data = SAMPLE_PROJECT
        
        section = generator.generate(project_data)
        
        assert section.title == 'Lean Waste Analysis (DOWNTIME)'
        assert 'waste_breakdown' in section.content
    
    def test_waste_chart_data(self):
        """Test waste chart data generation"""
        from backend.app.ml.reporting import WasteReportGenerator
        
        generator = WasteReportGenerator()
        project_data = SAMPLE_PROJECT
        
        section = generator.generate(project_data)
        
        assert len(section.charts) >= 1
        assert section.charts[0]['type'] == 'radar_chart'


class TestForecastReportGenerator:
    """Tests for forecast report generator specifically"""
    
    def test_forecast_report_generation(self):
        """Test forecast report section generation"""
        from backend.app.ml.reporting import ForecastReportGenerator
        
        generator = ForecastReportGenerator()
        project_data = SAMPLE_PROJECT
        
        section = generator.generate(project_data)
        
        assert section.title == 'Project Forecast'
        assert 'schedule_variance_days' in section.content
        assert 'budget_variance_percentage' in section.content


class TestSafetyReportGenerator:
    """Tests for safety report generator specifically"""
    
    def test_safety_report_generation(self):
        """Test safety report section generation"""
        from backend.app.ml.reporting import SafetyReportGenerator
        
        generator = SafetyReportGenerator()
        project_data = SAMPLE_PROJECT
        
        section = generator.generate(project_data)
        
        assert section.title == 'Safety Compliance'
        assert 'compliance_score' in section.content
        assert 'is_compliant' in section.content


class TestIntegration:
    """Integration tests across modules"""
    
    def test_full_pipeline_integration(self):
        """Test full ML pipeline integration"""
        from backend.app.ml import (
            WasteDetectionEngine,
            IntegratedForecastingSystem,
            AutomatedReportingSystem,
            ReportType
        )
        
        project_data = SAMPLE_PROJECT
        
        # Run waste detection
        waste_engine = WasteDetectionEngine()
        waste_result = waste_engine.analyze(project_data)
        project_data['waste_analysis'] = waste_result
        
        # Run forecasting
        forecast_system = IntegratedForecastingSystem()
        forecast_result = forecast_system.generate_forecast(project_data)
        project_data['forecast'] = forecast_result
        
        # Generate comprehensive report
        reporting_system = AutomatedReportingSystem()
        report = reporting_system.generate_report(
            project_data,
            ReportType.COMPREHENSIVE
        )
        
        assert report is not None
        assert len(report['sections']) == 5
    
    def test_batch_processing(self):
        """Test batch processing multiple projects"""
        from backend.app.ml import AutomatedReportingSystem, ReportType
        
        system = AutomatedReportingSystem()
        
        reports = []
        for project_data in SAMPLE_PROJECTS:
            report = system.generate_report(project_data, ReportType.DAILY)
            reports.append(report)
        
        assert len(reports) == len(SAMPLE_PROJECTS)
        
        for report in reports:
            assert 'metadata' in report
            assert 'sections' in report


# Fixtures for pytest

@pytest.fixture
def sample_project():
    """Provide sample project data"""
    return generate_sample_project_data()


@pytest.fixture
def sample_projects():
    """Provide multiple sample projects"""
    return SAMPLE_PROJECTS


@pytest.fixture
def waste_engine():
    """Provide waste detection engine"""
    from backend.app.ml import WasteDetectionEngine
    return WasteDetectionEngine()


@pytest.fixture
def forecast_system():
    """Provide forecasting system"""
    from backend.app.ml import IntegratedForecastingSystem
    return IntegratedForecastingSystem()


@pytest.fixture
def reporting_system():
    """Provide reporting system"""
    from backend.app.ml import AutomatedReportingSystem
    return AutomatedReportingSystem()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])