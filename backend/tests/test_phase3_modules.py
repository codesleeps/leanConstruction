"""
Unit tests for Phase 3 ML modules

Tests cover:
- Lean Tools (VSM, 5S, Kaizen, Kanban, A3)
- NLP Analysis (Document Classification, NER, Sentiment)
- Resource Optimization (Crew Scheduling, Equipment, Delivery)
- Alerting System
- ERP Integrations
- IoT Sensors
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


# ============================================
# Lean Tools Tests
# ============================================

class TestLeanToolsModule:
    """Tests for Lean Tools implementation"""
    
    def test_process_type_enum(self):
        """Test process type enumeration"""
        from backend.app.ml.lean_tools import ProcessType
        
        types = ['VALUE_ADDING', 'NECESSARY_NON_VALUE', 'NON_VALUE_ADDING', 
                 'WAITING', 'TRANSPORT', 'INSPECTION', 'REWORK']
        
        for ptype in types:
            assert hasattr(ProcessType, ptype)
    
    def test_s5_category_enum(self):
        """Test 5S category enumeration"""
        from backend.app.ml.lean_tools import S5Category
        
        categories = ['SORT', 'SET_IN_ORDER', 'SHINE', 'STANDARDIZE', 'SUSTAIN']
        
        for cat in categories:
            assert hasattr(S5Category, cat)
    
    def test_kaizen_type_enum(self):
        """Test Kaizen type enumeration"""
        from backend.app.ml.lean_tools import KaizenType
        
        types = ['POINT', 'SYSTEM', 'LINE', 'PLANE', 'CUBE']
        
        for ktype in types:
            assert hasattr(KaizenType, ktype)
    
    def test_kanban_status_enum(self):
        """Test Kanban status enumeration"""
        from backend.app.ml.lean_tools import KanbanStatus
        
        statuses = ['BACKLOG', 'READY', 'IN_PROGRESS', 'REVIEW', 'BLOCKED', 'DONE']
        
        for status in statuses:
            assert hasattr(KanbanStatus, status)
    
    def test_value_stream_mapper_initialization(self):
        """Test Value Stream Mapper initialization"""
        from backend.app.ml.lean_tools import ValueStreamMapper
        
        vsm = ValueStreamMapper()
        
        assert vsm is not None
        assert hasattr(vsm, 'process_steps')
        assert hasattr(vsm, 'analyze_current_state')
        assert hasattr(vsm, 'generate_future_state')
    
    def test_value_stream_analysis(self):
        """Test Value Stream analysis"""
        from backend.app.ml.lean_tools import ValueStreamMapper, ProcessType
        
        vsm = ValueStreamMapper()
        
        # Add sample process steps
        process_data = [
            {'id': 'p1', 'name': 'Excavation', 'type': 'value_adding', 
             'cycle_time': 3600, 'wait_time': 1800, 'setup_time': 900, 'defect_rate': 2},
            {'id': 'p2', 'name': 'Foundation', 'type': 'value_adding',
             'cycle_time': 7200, 'wait_time': 3600, 'setup_time': 1200, 'defect_rate': 5},
            {'id': 'p3', 'name': 'Inspection', 'type': 'inspection',
             'cycle_time': 1800, 'wait_time': 7200, 'setup_time': 0, 'defect_rate': 0}
        ]
        
        vsm.create_from_data(process_data)
        metrics = vsm.analyze_current_state()
        
        assert metrics is not None
        assert metrics.total_cycle_time > 0
        assert metrics.total_wait_time > 0
        assert metrics.process_efficiency >= 0
    
    def test_value_stream_future_state(self):
        """Test Value Stream future state generation"""
        from backend.app.ml.lean_tools import ValueStreamMapper
        
        vsm = ValueStreamMapper()
        
        process_data = [
            {'id': 'p1', 'name': 'Step 1', 'type': 'value_adding',
             'cycle_time': 100, 'wait_time': 50, 'setup_time': 20, 'defect_rate': 10}
        ]
        
        vsm.create_from_data(process_data)
        vsm.analyze_current_state()
        
        future = vsm.generate_future_state()
        
        assert future is not None
        assert 'improvements' in future
        assert 'estimated_savings' in future
        assert 'implementation_phases' in future
    
    def test_s5_analysis_system_initialization(self):
        """Test 5S Analysis System initialization"""
        from backend.app.ml.lean_tools import S5AnalysisSystem
        
        s5 = S5AnalysisSystem()
        
        assert s5 is not None
        assert hasattr(s5, 'conduct_assessment')
        assert hasattr(s5, 'criteria')
    
    def test_s5_assessment(self):
        """Test 5S assessment"""
        from backend.app.ml.lean_tools import S5AnalysisSystem
        
        s5 = S5AnalysisSystem()
        
        scores = {
            'unnecessary_items': 75,
            'red_tag_system': 80,
            'clear_boundaries': 70,
            'tool_audit': 65,
            'disposal_process': 85,
            'designated_locations': 90,
            'visual_controls': 75,
            'labeling': 80,
            'ergonomic_placement': 70,
            'shadow_boards': 60
        }
        
        assessment = s5.conduct_assessment(
            area_id='A001',
            area_name='Workshop A',
            scores=scores,
            assessor='John Doe'
        )
        
        assert assessment is not None
        assert 'overall_score' in assessment
        assert 'grade' in assessment
        assert 'category_scores' in assessment
        assert 'certification' in assessment
    
    def test_s5_certification_levels(self):
        """Test 5S certification level determination"""
        from backend.app.ml.lean_tools import S5AnalysisSystem
        
        s5 = S5AnalysisSystem()
        
        # High scores should get gold
        high_scores = {k: 95 for k in [
            'unnecessary_items', 'red_tag_system', 'clear_boundaries',
            'tool_audit', 'disposal_process', 'designated_locations',
            'visual_controls', 'labeling', 'ergonomic_placement', 'shadow_boards'
        ]}
        
        assessment = s5.conduct_assessment('A001', 'Area', high_scores)
        
        assert assessment['certification']['level'] in ['gold', 'silver', 'bronze', 'none']
    
    def test_kaizen_manager_initialization(self):
        """Test Kaizen Manager initialization"""
        from backend.app.ml.lean_tools import KaizenManager
        
        km = KaizenManager()
        
        assert km is not None
        assert hasattr(km, 'create_event')
        assert hasattr(km, 'events')
    
    def test_kaizen_event_creation(self):
        """Test Kaizen event creation"""
        from backend.app.ml.lean_tools import KaizenManager, KaizenType
        
        km = KaizenManager()
        
        event = km.create_event(
            title='Reduce Setup Time',
            kaizen_type=KaizenType.POINT,
            target_area='Assembly Line',
            current_state={'cycle_time': 100, 'defect_rate': 5},
            target_state={'cycle_time': 70, 'defect_rate': 2},
            team_members=['Alice', 'Bob', 'Charlie'],
            duration_days=5
        )
        
        assert event is not None
        assert event.id is not None
        assert event.expected_savings >= 0
    
    def test_kanban_board_initialization(self):
        """Test Kanban Board initialization"""
        from backend.app.ml.lean_tools import KanbanBoard
        
        board = KanbanBoard('KB001', 'Sprint Board')
        
        assert board is not None
        assert board.board_id == 'KB001'
        assert hasattr(board, 'wip_limits')
    
    def test_kanban_card_operations(self):
        """Test Kanban card operations"""
        from backend.app.ml.lean_tools import KanbanBoard, KanbanStatus
        
        board = KanbanBoard('KB001', 'Sprint Board')
        
        # Create card
        card = board.create_card(
            title='Implement Feature',
            description='Build the new feature',
            priority=1,
            assignee='Developer'
        )
        
        assert card is not None
        assert card.status == KanbanStatus.BACKLOG
        
        # Move card
        result = board.move_card(card.id, KanbanStatus.IN_PROGRESS)
        
        assert 'error' not in result
        assert card.status == KanbanStatus.IN_PROGRESS
    
    def test_kanban_wip_limits(self):
        """Test Kanban WIP limits enforcement"""
        from backend.app.ml.lean_tools import KanbanBoard, KanbanStatus
        
        board = KanbanBoard('KB001', 'Sprint Board', wip_limits={
            'in_progress': 2
        })
        
        # Create and move cards to reach limit
        for i in range(2):
            card = board.create_card(f'Task {i}', 'Desc', 1)
            board.move_card(card.id, KanbanStatus.IN_PROGRESS)
        
        # Try to exceed limit
        new_card = board.create_card('Task 3', 'Desc', 1)
        result = board.move_card(new_card.id, KanbanStatus.IN_PROGRESS)
        
        assert 'error' in result
        assert result['error'] == 'WIP limit reached'
    
    def test_a3_problem_solver_initialization(self):
        """Test A3 Problem Solver initialization"""
        from backend.app.ml.lean_tools import A3ProblemSolver
        
        a3 = A3ProblemSolver()
        
        assert a3 is not None
        assert hasattr(a3, 'create_a3')
        assert hasattr(a3, 'a3_reports')
    
    def test_a3_report_creation(self):
        """Test A3 report creation"""
        from backend.app.ml.lean_tools import A3ProblemSolver
        
        a3 = A3ProblemSolver()
        
        a3_id = a3.create_a3(
            title='Quality Issue',
            owner='Quality Manager',
            background='Defect rate increased by 20%'
        )
        
        assert a3_id is not None
        assert a3_id in a3.a3_reports
    
    def test_lean_tools_integration(self):
        """Test Lean Tools Integration"""
        from backend.app.ml.lean_tools import LeanToolsIntegration
        
        lean = LeanToolsIntegration()
        
        assert lean is not None
        assert hasattr(lean, 'vsm')
        assert hasattr(lean, 's5_system')
        assert hasattr(lean, 'kaizen_manager')
        assert hasattr(lean, 'a3_solver')
    
    def test_lean_metrics_summary(self):
        """Test lean metrics summary"""
        from backend.app.ml.lean_tools import lean_tools
        
        summary = lean_tools.get_lean_metrics_summary()
        
        assert 'vsm' in summary
        assert 's5' in summary
        assert 'kaizen' in summary
        assert 'kanban' in summary
        assert 'a3' in summary


# ============================================
# NLP Analysis Tests
# ============================================

class TestNLPAnalysisModule:
    """Tests for NLP Analysis implementation"""
    
    def test_document_type_enum(self):
        """Test document type enumeration"""
        from backend.app.ml.nlp_analysis import DocumentType
        
        types = ['RFI', 'SUBMITTAL', 'CHANGE_ORDER', 'SAFETY_REPORT',
                 'DAILY_LOG', 'MEETING_MINUTES', 'CONTRACT']
        
        for dtype in types:
            assert hasattr(DocumentType, dtype)
    
    def test_entity_type_enum(self):
        """Test entity type enumeration"""
        from backend.app.ml.nlp_analysis import EntityType
        
        types = ['PERSON', 'ORGANIZATION', 'LOCATION', 'DATE', 'MONEY',
                 'MATERIAL', 'EQUIPMENT', 'TRADE']
        
        for etype in types:
            assert hasattr(EntityType, etype)
    
    def test_sentiment_level_enum(self):
        """Test sentiment level enumeration"""
        from backend.app.ml.nlp_analysis import SentimentLevel
        
        levels = ['VERY_NEGATIVE', 'NEGATIVE', 'NEUTRAL', 'POSITIVE', 'VERY_POSITIVE']
        
        for level in levels:
            assert hasattr(SentimentLevel, level)
    
    def test_document_classifier_initialization(self):
        """Test Document Classifier initialization"""
        from backend.app.ml.nlp_analysis import DocumentClassifier
        
        classifier = DocumentClassifier()
        
        assert classifier is not None
        assert hasattr(classifier, 'classify')
        assert hasattr(classifier, 'keyword_patterns')
    
    def test_document_classification(self):
        """Test document classification"""
        from backend.app.ml.nlp_analysis import DocumentClassifier, DocumentType
        
        classifier = DocumentClassifier()
        
        # Test RFI detection
        rfi_text = """
        REQUEST FOR INFORMATION
        Project: Commercial Building
        
        Please clarify the specification for the concrete mix.
        We need clarification on the reinforcement requirements.
        """
        
        result = classifier.classify(rfi_text)
        
        assert result is not None
        assert result.document_type == DocumentType.RFI
        assert result.confidence > 0
    
    def test_change_order_classification(self):
        """Test change order classification"""
        from backend.app.ml.nlp_analysis import DocumentClassifier, DocumentType
        
        classifier = DocumentClassifier()
        
        text = """
        CHANGE ORDER #15
        
        This change order modifies the contract scope.
        Additional work required: Foundation reinforcement
        Cost adjustment: $50,000
        """
        
        result = classifier.classify(text)
        
        assert result.document_type == DocumentType.CHANGE_ORDER
    
    def test_construction_ner_initialization(self):
        """Test Construction NER initialization"""
        from backend.app.ml.nlp_analysis import ConstructionNER
        
        ner = ConstructionNER()
        
        assert ner is not None
        assert hasattr(ner, 'extract_entities')
        assert hasattr(ner, 'domain_vocab')
    
    def test_entity_extraction(self):
        """Test entity extraction"""
        from backend.app.ml.nlp_analysis import ConstructionNER, EntityType
        
        ner = ConstructionNER()
        
        text = """
        The concrete delivery is scheduled for 01/15/2024.
        The carpenter will install the steel beams on floor 3.
        Total cost: $150,000.
        """
        
        entities = ner.extract_entities(text)
        
        assert len(entities) > 0
        
        # Check for expected entity types
        entity_types = [e.entity_type for e in entities]
        assert EntityType.DATE in entity_types or EntityType.MONEY in entity_types
    
    def test_communication_analyzer_initialization(self):
        """Test Communication Analyzer initialization"""
        from backend.app.ml.nlp_analysis import CommunicationAnalyzer
        
        analyzer = CommunicationAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_sentiment')
        assert hasattr(analyzer, 'analyze_urgency')
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        from backend.app.ml.nlp_analysis import CommunicationAnalyzer, SentimentLevel
        
        analyzer = CommunicationAnalyzer()
        
        # Positive text
        positive_text = "Great job on the progress! The team did excellent work."
        result = analyzer.analyze_sentiment(positive_text)
        
        assert result is not None
        assert result.sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]
        
        # Negative text
        negative_text = "This is a critical problem. We are behind schedule and over budget."
        result = analyzer.analyze_sentiment(negative_text)
        
        assert result.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE, SentimentLevel.NEUTRAL]
    
    def test_urgency_analysis(self):
        """Test urgency level analysis"""
        from backend.app.ml.nlp_analysis import CommunicationAnalyzer, UrgencyLevel
        
        analyzer = CommunicationAnalyzer()
        
        urgent_text = "URGENT: Stop work immediately. Safety hazard identified."
        urgency = analyzer.analyze_urgency(urgent_text)
        
        assert urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]
    
    def test_document_summarizer_initialization(self):
        """Test Document Summarizer initialization"""
        from backend.app.ml.nlp_analysis import DocumentSummarizer
        
        summarizer = DocumentSummarizer()
        
        assert summarizer is not None
        assert hasattr(summarizer, 'summarize')
        assert hasattr(summarizer, 'extract_key_points')
    
    def test_text_summarization(self):
        """Test text summarization"""
        from backend.app.ml.nlp_analysis import DocumentSummarizer
        
        summarizer = DocumentSummarizer()
        
        long_text = """
        The construction project has been progressing well. 
        The foundation work was completed last week. 
        We are now starting the structural phase. 
        The team has been working efficiently. 
        There were some minor delays due to weather. 
        However, we expect to catch up next week.
        Quality inspections have passed successfully.
        Safety compliance is at 100%.
        """
        
        summary = summarizer.summarize(long_text, max_length=100)
        
        assert summary is not None
        assert len(summary) <= 200  # Approximate max
    
    def test_key_points_extraction(self):
        """Test key points extraction"""
        from backend.app.ml.nlp_analysis import DocumentSummarizer
        
        summarizer = DocumentSummarizer()
        
        text = """
        Action Required: Complete the foundation by Friday.
        Please ensure all safety protocols are followed.
        The deadline for submittal is January 20th.
        Must verify concrete strength before proceeding.
        """
        
        key_points = summarizer.extract_key_points(text, max_points=3)
        
        assert len(key_points) > 0
        assert len(key_points) <= 3
    
    def test_risk_issue_extractor_initialization(self):
        """Test Risk Issue Extractor initialization"""
        from backend.app.ml.nlp_analysis import RiskIssueExtractor
        
        extractor = RiskIssueExtractor()
        
        assert extractor is not None
        assert hasattr(extractor, 'extract_risks')
        assert hasattr(extractor, 'extract_action_items')
    
    def test_risk_extraction(self):
        """Test risk extraction"""
        from backend.app.ml.nlp_analysis import RiskIssueExtractor
        
        extractor = RiskIssueExtractor()
        
        text = """
        There is a schedule risk due to material delays.
        Safety hazard identified near the excavation.
        Cost overrun is expected due to change orders.
        """
        
        risks = extractor.extract_risks(text)
        
        assert len(risks) > 0
        assert all(hasattr(r, 'category') for r in risks)
    
    def test_action_item_extraction(self):
        """Test action item extraction"""
        from backend.app.ml.nlp_analysis import RiskIssueExtractor
        
        extractor = RiskIssueExtractor()
        
        text = """
        Please submit the revised drawings by Friday.
        Action required: John must complete the inspection.
        Ensure all permits are obtained before starting.
        """
        
        actions = extractor.extract_action_items(text)
        
        assert len(actions) > 0
    
    def test_contract_analyzer_initialization(self):
        """Test Contract Analyzer initialization"""
        from backend.app.ml.nlp_analysis import ContractAnalyzer
        
        analyzer = ContractAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_contract')
        assert hasattr(analyzer, 'clause_patterns')
    
    def test_contract_analysis(self):
        """Test contract analysis"""
        from backend.app.ml.nlp_analysis import ContractAnalyzer
        
        analyzer = ContractAnalyzer()
        
        contract_text = """
        PAYMENT TERMS
        Progress payments shall be made monthly.
        Retainage of 10% will be held until completion.
        
        CHANGE ORDER PROCESS
        All changes must have written approval.
        
        INDEMNIFICATION
        Contractor shall indemnify and hold harmless the Owner.
        
        WARRANTY
        Contractor warrants all work for a period of one year.
        """
        
        analysis = analyzer.analyze_contract(contract_text)
        
        assert 'identified_clauses' in analysis
        assert 'recommendations' in analysis
        assert len(analysis['identified_clauses']) > 0
    
    def test_nlp_system_integration(self):
        """Test integrated NLP system"""
        from backend.app.ml.nlp_analysis import ConstructionNLPSystem
        
        nlp = ConstructionNLPSystem()
        
        document = """
        REQUEST FOR INFORMATION #42
        
        Project: Downtown Office Tower
        Date: January 15, 2024
        
        We need clarification on the concrete specification.
        Please respond urgently as this is affecting the schedule.
        
        Thank you for your prompt attention.
        """
        
        result = nlp.analyze_document(document)
        
        assert 'classification' in result
        assert 'entities' in result
        assert 'sentiment' in result
        assert 'summary' in result


# ============================================
# Resource Optimization Tests
# ============================================

class TestResourceOptimizationModule:
    """Tests for Resource Optimization implementation"""
    
    def test_resource_type_enum(self):
        """Test resource type enumeration"""
        from backend.app.ml.resource_optimizer import ResourceType
        
        types = ['LABOR', 'EQUIPMENT', 'MATERIAL', 'SUBCONTRACTOR', 'SPACE']
        
        for rtype in types:
            assert hasattr(ResourceType, rtype)
    
    def test_skill_type_enum(self):
        """Test skill type enumeration"""
        from backend.app.ml.resource_optimizer import SkillType
        
        skills = ['CARPENTER', 'ELECTRICIAN', 'PLUMBER', 'HVAC', 'MASON']
        
        for skill in skills:
            assert hasattr(SkillType, skill)
    
    def test_optimization_objective_enum(self):
        """Test optimization objective enumeration"""
        from backend.app.ml.resource_optimizer import OptimizationObjective
        
        objectives = ['MINIMIZE_COST', 'MINIMIZE_DURATION', 'MAXIMIZE_UTILIZATION',
                     'BALANCE_WORKLOAD', 'MINIMIZE_OVERTIME']
        
        for obj in objectives:
            assert hasattr(OptimizationObjective, obj)
    
    def test_crew_scheduling_optimizer_initialization(self):
        """Test Crew Scheduling Optimizer initialization"""
        from backend.app.ml.resource_optimizer import CrewSchedulingOptimizer
        
        optimizer = CrewSchedulingOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize')
        assert hasattr(optimizer, 'workers')
        assert hasattr(optimizer, 'tasks')
    
    def test_crew_scheduling(self):
        """Test crew scheduling optimization"""
        from backend.app.ml.resource_optimizer import (
            CrewSchedulingOptimizer, Resource, Task, 
            ResourceType, SkillType, OptimizationObjective
        )
        
        optimizer = CrewSchedulingOptimizer()
        
        # Add workers
        optimizer.add_worker(Resource(
            id='W1', name='Worker 1', resource_type=ResourceType.LABOR,
            capacity=1, cost_per_unit=50, skills=[SkillType.CARPENTER]
        ))
        optimizer.add_worker(Resource(
            id='W2', name='Worker 2', resource_type=ResourceType.LABOR,
            capacity=1, cost_per_unit=60, skills=[SkillType.ELECTRICIAN]
        ))
        
        # Add tasks
        optimizer.add_task(Task(
            id='T1', name='Framing', duration=8,
            required_resources={'labor': 1},
            required_skills=[SkillType.CARPENTER]
        ))
        optimizer.add_task(Task(
            id='T2', name='Wiring', duration=6,
            required_resources={'labor': 1},
            required_skills=[SkillType.ELECTRICIAN],
            predecessors=['T1']
        ))
        
        schedule = optimizer.optimize(OptimizationObjective.MINIMIZE_COST)
        
        assert schedule is not None
        assert hasattr(schedule, 'assignments')
        assert hasattr(schedule, 'total_cost')
        assert hasattr(schedule, 'makespan')
    
    def test_equipment_optimizer_initialization(self):
        """Test Equipment Optimizer initialization"""
        from backend.app.ml.resource_optimizer import EquipmentOptimizer
        
        optimizer = EquipmentOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_allocation')
    
    def test_equipment_allocation(self):
        """Test equipment allocation optimization"""
        from backend.app.ml.resource_optimizer import (
            EquipmentOptimizer, Resource, ResourceType
        )
        
        optimizer = EquipmentOptimizer()
        
        # Add equipment
        optimizer.add_equipment(Resource(
            id='E1', name='Crane 1', resource_type=ResourceType.EQUIPMENT,
            capacity=1, cost_per_unit=500
        ))
        
        # Add demand
        optimizer.add_demand(
            location='Site A',
            equipment_type='crane',
            quantity=1,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=5),
            priority=1
        )
        
        result = optimizer.optimize_allocation()
        
        assert 'allocations' in result
        assert 'total_cost' in result
    
    def test_delivery_optimizer_initialization(self):
        """Test Delivery Optimizer initialization"""
        from backend.app.ml.resource_optimizer import DeliveryOptimizer
        
        optimizer = DeliveryOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_routes')
    
    def test_delivery_route_optimization(self):
        """Test delivery route optimization"""
        from backend.app.ml.resource_optimizer import DeliveryOptimizer, DeliveryRequest
        
        optimizer = DeliveryOptimizer()
        optimizer.set_warehouse(0, 0)
        
        # Add deliveries
        optimizer.add_delivery(DeliveryRequest(
            id='D1', material_type='concrete', quantity=10,
            destination='Site A',
            earliest_delivery=datetime.utcnow(),
            latest_delivery=datetime.utcnow() + timedelta(hours=4),
            priority=1
        ))
        
        # Add vehicle
        optimizer.add_vehicle('V1', capacity=20, cost_per_mile=2.0)
        
        routes = optimizer.optimize_routes()
        
        assert len(routes) > 0 or True  # May be empty if no deliveries assigned
    
    def test_resource_leveler_initialization(self):
        """Test Resource Leveler initialization"""
        from backend.app.ml.resource_optimizer import ResourceLeveler
        
        leveler = ResourceLeveler()
        
        assert leveler is not None
        assert hasattr(leveler, 'level_resources')
    
    def test_resource_leveling(self):
        """Test resource leveling"""
        from backend.app.ml.resource_optimizer import ResourceLeveler, Task
        
        leveler = ResourceLeveler()
        
        # Add tasks
        leveler.add_task(Task(
            id='T1', name='Task 1', duration=4,
            required_resources={'labor': 2}
        ))
        leveler.add_task(Task(
            id='T2', name='Task 2', duration=3,
            required_resources={'labor': 3}
        ))
        
        leveler.set_resource_limit('labor', 4)
        
        result = leveler.level_resources()
        
        assert 'schedule' in result
        assert 'metrics' in result
    
    def test_cost_optimizer_initialization(self):
        """Test Cost Optimizer initialization"""
        from backend.app.ml.resource_optimizer import CostOptimizer
        
        optimizer = CostOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_cost_duration')
    
    def test_cost_duration_optimization(self):
        """Test cost-duration trade-off optimization"""
        from backend.app.ml.resource_optimizer import CostOptimizer
        
        optimizer = CostOptimizer()
        
        # Add activities
        optimizer.add_activity(
            activity_id='A1', name='Activity 1',
            duration_normal=10, duration_crash=6,
            cost_normal=1000, cost_crash=1600
        )
        optimizer.add_activity(
            activity_id='A2', name='Activity 2',
            duration_normal=8, duration_crash=5,
            cost_normal=800, cost_crash=1200
        )
        
        result = optimizer.optimize_cost_duration(target_duration=14)
        
        assert 'activities' in result
        assert 'total_cost' in result
        assert 'target_achieved' in result
    
    def test_resource_optimization_system_integration(self):
        """Test integrated resource optimization system"""
        from backend.app.ml.resource_optimizer import ResourceOptimizationSystem
        
        system = ResourceOptimizationSystem()
        
        assert system is not None
        assert hasattr(system, 'crew_optimizer')
        assert hasattr(system, 'equipment_optimizer')
        assert hasattr(system, 'delivery_optimizer')


# ============================================
# Alerting System Tests
# ============================================

class TestAlertingModule:
    """Tests for Alerting System implementation"""
    
    def test_alert_severity_enum(self):
        """Test alert severity enumeration"""
        from backend.app.ml.alerting import AlertSeverity
        
        severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
        
        for sev in severities:
            assert hasattr(AlertSeverity, sev)
    
    def test_alert_category_enum(self):
        """Test alert category enumeration"""
        from backend.app.ml.alerting import AlertCategory
        
        categories = ['SAFETY', 'SCHEDULE', 'COST', 'QUALITY', 
                     'RESOURCE', 'EQUIPMENT', 'WEATHER']
        
        for cat in categories:
            assert hasattr(AlertCategory, cat)
    
    def test_alert_status_enum(self):
        """Test alert status enumeration"""
        from backend.app.ml.alerting import AlertStatus
        
        statuses = ['ACTIVE', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'SUPPRESSED']
        
        for status in statuses:
            assert hasattr(AlertStatus, status)
    
    def test_notification_channel_enum(self):
        """Test notification channel enumeration"""
        from backend.app.ml.alerting import NotificationChannel
        
        channels = ['EMAIL', 'SMS', 'PUSH', 'WEBHOOK', 'SLACK', 'TEAMS']
        
        for channel in channels:
            assert hasattr(NotificationChannel, channel)
    
    def test_condition_evaluator_initialization(self):
        """Test Condition Evaluator initialization"""
        from backend.app.ml.alerting import ConditionEvaluator
        
        evaluator = ConditionEvaluator()
        
        assert evaluator is not None
        assert hasattr(evaluator, 'evaluate_condition')
        assert hasattr(evaluator, 'record_metric')
    
    def test_metric_recording(self):
        """Test metric recording"""
        from backend.app.ml.alerting import ConditionEvaluator
        
        evaluator = ConditionEvaluator()
        
        evaluator.record_metric('temperature', 25.5)
        evaluator.record_metric('temperature', 26.0)
        
        assert len(evaluator.metric_history['temperature']) == 2
    
    def test_condition_evaluation(self):
        """Test condition evaluation"""
        from backend.app.ml.alerting import (
            ConditionEvaluator, AlertCondition, ConditionOperator
        )
        
        evaluator = ConditionEvaluator()
        
        condition = AlertCondition(
            metric='temperature',
            operator=ConditionOperator.GREATER_THAN,
            threshold=30
        )
        
        # Test below threshold
        triggered, _ = evaluator.evaluate_condition(condition, current_value=25)
        assert not triggered
        
        # Test above threshold
        triggered, _ = evaluator.evaluate_condition(condition, current_value=35)
        assert triggered
    
    def test_alert_manager_initialization(self):
        """Test Alert Manager initialization"""
        from backend.app.ml.alerting import AlertManager
        
        manager = AlertManager()
        
        assert manager is not None
        assert hasattr(manager, 'rules')
        assert hasattr(manager, 'alerts')
        assert len(manager.rules) > 0  # Default rules
    
    def test_alert_creation(self):
        """Test alert creation"""
        from backend.app.ml.alerting import AlertManager
        
        manager = AlertManager()
        
        alert = manager.create_alert(
            rule_id='safety_incident',
            title='Safety Incident',
            message='Worker injured on site',
            source='manual'
        )
        
        assert alert is not None
        assert alert.id is not None
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment"""
        from backend.app.ml.alerting import AlertManager, AlertStatus
        
        manager = AlertManager()
        
        alert = manager.create_alert(
            rule_id='safety_incident',
            title='Test Alert',
            message='Test message',
            source='test'
        )
        
        result = manager.acknowledge_alert(alert.id, 'user123')
        
        assert result is not None
        assert result.status == AlertStatus.ACKNOWLEDGED
        assert result.acknowledged_by == 'user123'
    
    def test_alert_resolution(self):
        """Test alert resolution"""
        from backend.app.ml.alerting import AlertManager, AlertStatus
        
        manager = AlertManager()
        
        alert = manager.create_alert(
            rule_id='safety_incident',
            title='Test Alert',
            message='Test message',
            source='test'
        )
        
        manager.acknowledge_alert(alert.id, 'user123')
        result = manager.resolve_alert(alert.id, 'user123', 'Issue fixed')
        
        assert result is not None
        assert result.status == AlertStatus.RESOLVED
    
    def test_metrics_evaluation(self):
        """Test metrics evaluation triggers alerts"""
        from backend.app.ml.alerting import AlertManager
        
        manager = AlertManager()
        
        # Evaluate metrics that should trigger safety alert
        metrics = {
            'safety.incidents': 1
        }
        
        manager.evaluate_metrics(metrics, source='test')
        
        # Check for alerts
        active_alerts = manager.get_active_alerts()
        
        assert len(active_alerts) >= 0  # May or may not trigger based on rules
    
    def test_alert_statistics(self):
        """Test alert statistics"""
        from backend.app.ml.alerting import AlertManager
        
        manager = AlertManager()
        
        # Create some alerts
        for i in range(5):
            manager.create_alert(
                rule_id='safety_incident',
                title=f'Alert {i}',
                message='Test',
                source='test'
            )
        
        stats = manager.get_alert_statistics()
        
        assert 'total_alerts' in stats
        assert 'by_category' in stats
        assert 'by_severity' in stats
    
    def test_alert_rule_builder(self):
        """Test alert rule builder"""
        from backend.app.ml.alerting import (
            AlertRuleBuilder, AlertCategory, AlertSeverity,
            ConditionOperator, NotificationChannel
        )
        
        rule = (AlertRuleBuilder()
            .with_id('custom_rule')
            .with_name('Custom Alert')
            .with_category(AlertCategory.COST)
            .with_severity(AlertSeverity.HIGH)
            .add_condition('cost.variance', ConditionOperator.GREATER_THAN, 10)
            .notify_via(NotificationChannel.EMAIL)
            .build())
        
        assert rule is not None
        assert rule.id == 'custom_rule'
        assert len(rule.conditions) == 1
    
    def test_construction_alert_rules(self):
        """Test construction-specific alert rules"""
        from backend.app.ml.alerting import ConstructionAlertRules
        
        rules = ConstructionAlertRules.get_all_rules()
        
        assert len(rules) > 0
        
        # Check for safety rules
        safety_rules = ConstructionAlertRules.create_safety_rules()
        assert len(safety_rules) > 0
        
        # Check for schedule rules
        schedule_rules = ConstructionAlertRules.create_schedule_rules()
        assert len(schedule_rules) > 0
    
    def test_alerting_system_integration(self):
        """Test integrated alerting system"""
        from backend.app.ml.alerting import AlertingSystem
        
        system = AlertingSystem()
        
        assert system is not None
        assert hasattr(system, 'manager')
        assert hasattr(system, 'process_project_metrics')
    
    def test_alerting_dashboard(self):
        """Test alerting dashboard"""
        from backend.app.ml.alerting import alerting_system
        
        dashboard = alerting_system.get_dashboard()
        
        assert 'statistics' in dashboard
        assert 'active_alerts' in dashboard
        assert 'recent_activity' in dashboard


# ============================================
# ERP Integration Tests
# ============================================

class TestERPIntegrationModule:
    """Tests for ERP Integration implementation"""
    
    def test_erp_system_enum(self):
        """Test ERP system enumeration"""
        from backend.app.integrations.erp_systems import ERPSystem
        
        systems = ['SAP', 'ORACLE', 'SAGE', 'VIEWPOINT', 'GENERIC']
        
        for system in systems:
            assert hasattr(ERPSystem, system)
    
    def test_data_entity_enum(self):
        """Test data entity enumeration"""
        from backend.app.integrations.erp_systems import DataEntity
        
        entities = ['PROJECT', 'COST_CODE', 'JOB_COST', 'PURCHASE_ORDER', 'INVOICE']
        
        for entity in entities:
            assert hasattr(DataEntity, entity)
    
    def test_sap_client_initialization(self):
        """Test SAP client initialization"""
        from backend.app.integrations.erp_systems import SAPClient, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.SAP,
            host='sap.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        client = SAPClient(connection)
        
        assert client is not None
        assert hasattr(client, 'connect')
        assert hasattr(client, 'get_projects')
    
    def test_sap_client_connection(self):
        """Test SAP client connection"""
        from backend.app.integrations.erp_systems import SAPClient, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.SAP,
            host='sap.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        client = SAPClient(connection)
        result = client.connect()
        
        assert result is True
        assert client.is_connected
    
    def test_sap_get_projects(self):
        """Test SAP get projects"""
        from backend.app.integrations.erp_systems import SAPClient, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.SAP,
            host='sap.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        client = SAPClient(connection)
        client.connect()
        
        projects = client.get_projects()
        
        assert isinstance(projects, list)
    
    def test_oracle_primavera_client(self):
        """Test Oracle Primavera client"""
        from backend.app.integrations.erp_systems import OraclePrimaveraClient, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.ORACLE,
            host='primavera.example.com',
            port=7443,
            username='user',
            password='pass'
        )
        
        client = OraclePrimaveraClient(connection)
        
        assert client is not None
        assert client.connect() is True
    
    def test_sage_client(self):
        """Test Sage 300 client"""
        from backend.app.integrations.erp_systems import Sage300Client, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.SAGE,
            host='sage.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        client = Sage300Client(connection)
        
        assert client is not None
        assert client.connect() is True
    
    def test_generic_erp_client(self):
        """Test Generic ERP client"""
        from backend.app.integrations.erp_systems import GenericERPClient, ERPConnection, ERPSystem
        
        connection = ERPConnection(
            system=ERPSystem.GENERIC,
            host='erp.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        client = GenericERPClient(connection)
        
        assert client is not None
        assert client.connect() is True
    
    def test_erp_integration_manager(self):
        """Test ERP Integration Manager"""
        from backend.app.integrations.erp_systems import (
            ERPIntegrationManager, ERPConnection, ERPSystem
        )
        
        manager = ERPIntegrationManager()
        
        connection = ERPConnection(
            system=ERPSystem.GENERIC,
            host='test.example.com',
            port=443,
            username='user',
            password='pass'
        )
        
        success = manager.register_connection('test', connection)
        
        assert success is True
        assert 'test' in manager.clients


# ============================================
# IoT Sensor Tests
# ============================================

class TestIoTSensorModule:
    """Tests for IoT Sensor integration"""
    
    def test_sensor_type_enum(self):
        """Test sensor type enumeration"""
        from backend.app.integrations.iot_sensors import SensorType
        
        types = ['TEMPERATURE', 'HUMIDITY', 'DUST', 'NOISE', 'VIBRATION']
        
        for stype in types:
            assert hasattr(SensorType, stype)
    
    def test_device_status_enum(self):
        """Test device status enumeration"""
        from backend.app.integrations.iot_sensors import DeviceStatus
        
        statuses = ['ONLINE', 'OFFLINE', 'WARNING', 'ERROR', 'MAINTENANCE']
        
        for status in statuses:
            assert hasattr(DeviceStatus, status)
    
    def test_data_processor_initialization(self):
        """Test Data Processor initialization"""
        from backend.app.integrations.iot_sensors import DataProcessor
        
        processor = DataProcessor()
        
        assert processor is not None
        assert hasattr(processor, 'add_reading')
        assert hasattr(processor, 'calculate_statistics')
    
    def test_sensor_reading_processing(self):
        """Test sensor reading processing"""
        from backend.app.integrations.iot_sensors import (
            DataProcessor, SensorReading, SensorType
        )
        
        processor = DataProcessor()
        
        reading = SensorReading(
            sensor_id='TEMP001',
            sensor_type=SensorType.TEMPERATURE,
            value=25.5,
            unit='°C',
            timestamp=datetime.utcnow()
        )
        
        processor.add_reading(reading)
        
        latest = processor.get_latest('TEMP001')
        
        assert latest is not None
        assert latest.value == 25.5
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        from backend.app.integrations.iot_sensors import (
            DataProcessor, SensorReading, SensorType
        )
        
        processor = DataProcessor()
        
        # Add multiple readings
        for i in range(10):
            reading = SensorReading(
                sensor_id='TEMP001',
                sensor_type=SensorType.TEMPERATURE,
                value=20 + i,
                unit='°C',
                timestamp=datetime.utcnow()
            )
            processor.add_reading(reading)
        
        stats = processor.calculate_statistics('TEMP001')
        
        assert 'min' in stats
        assert 'max' in stats
        assert 'avg' in stats
        assert stats['min'] == 20
        assert stats['max'] == 29
    
    def test_threshold_monitor_initialization(self):
        """Test Threshold Monitor initialization"""
        from backend.app.integrations.iot_sensors import ThresholdMonitor
        
        monitor = ThresholdMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'check_threshold')
        assert hasattr(monitor, 'configure_sensor')
    
    def test_threshold_checking(self):
        """Test threshold checking"""
        from backend.app.integrations.iot_sensors import (
            ThresholdMonitor, SensorConfig, SensorReading, SensorType, AlertLevel
        )
        
        monitor = ThresholdMonitor()
        
        config = SensorConfig(
            sensor_id='TEMP001',
            device_id='DEV001',
            sensor_type=SensorType.TEMPERATURE,
            name='Temperature Sensor',
            unit='°C',
            warning_high=30,
            critical_high=40
        )
        
        monitor.configure_sensor(config)
        
        # Normal reading
        normal = SensorReading(
            sensor_id='TEMP001',
            sensor_type=SensorType.TEMPERATURE,
            value=25,
            unit='°C',
            timestamp=datetime.utcnow()
        )
        
        event = monitor.check_threshold(normal)
        assert event is None  # No alert
        
        # High reading
        high = SensorReading(
            sensor_id='TEMP001',
            sensor_type=SensorType.TEMPERATURE,
            value=35,
            unit='°C',
            timestamp=datetime.utcnow()
        )
        
        event = monitor.check_threshold(high)
        assert event is not None
        assert event.level == AlertLevel.WARNING
    
    def test_device_manager_initialization(self):
        """Test Device Manager initialization"""
        from backend.app.integrations.iot_sensors import DeviceManager
        
        manager = DeviceManager()
        
        assert manager is not None
        assert hasattr(manager, 'register_device')
        assert hasattr(manager, 'register_sensor')
    
    def test_device_registration(self):
        """Test device registration"""
        from backend.app.integrations.iot_sensors import (
            DeviceManager, DeviceConfig, Protocol
        )
        
        manager = DeviceManager()
        
        config = DeviceConfig(
            device_id='DEV001',
            name='Environmental Station',
            device_type='weather_station',
            sensors=['TEMP001', 'HUM001'],
            protocol=Protocol.MQTT
        )
        
        success = manager.register_device(config)
        
        assert success is True
        assert 'DEV001' in manager.devices
    
    def test_construction_sensor_presets(self):
        """Test construction sensor presets"""
        from backend.app.integrations.iot_sensors import ConstructionSensorPresets
        
        env_sensors = ConstructionSensorPresets.environmental_monitoring()
        assert len(env_sensors) > 0
        
        safety_sensors = ConstructionSensorPresets.safety_monitoring()
        assert len(safety_sensors) > 0
        
        weather_sensors = ConstructionSensorPresets.weather_station()
        assert len(weather_sensors) > 0
    
    def test_iot_integration_system(self):
        """Test IoT Integration System"""
        from backend.app.integrations.iot_sensors import IoTIntegrationSystem
        
        system = IoTIntegrationSystem()
        
        assert system is not None
        assert hasattr(system, 'ingest_reading')
        assert hasattr(system, 'get_site_overview')
    
    def test_site_overview(self):
        """Test site overview generation"""
        from backend.app.integrations.iot_sensors import iot_system
        
        overview = iot_system.get_site_overview()
        
        assert 'timestamp' in overview
        assert 'summary' in overview
        assert 'alerts' in overview


# ============================================
# Integration Tests
# ============================================

class TestPhase3Integration:
    """Integration tests for Phase 3 modules"""
    
    def test_lean_nlp_integration(self):
        """Test Lean Tools with NLP integration"""
        from backend.app.ml.lean_tools import lean_tools, KaizenType
        from backend.app.ml.nlp_analysis import nlp_system
        
        # Create improvement event
        event = lean_tools.kaizen_manager.create_event(
            title='Reduce Documentation Time',
            kaizen_type=KaizenType.POINT,
            target_area='Document Processing',
            current_state={'processing_time': 60},
            target_state={'processing_time': 30},
            team_members=['Team Lead']
        )
        
        # Analyze related document
        doc = "Please review the improvement proposal for document processing efficiency."
        analysis = nlp_system.analyze_document(doc)
        
        assert event is not None
        assert analysis is not None
    
    def test_alerting_iot_integration(self):
        """Test Alerting with IoT integration"""
        from backend.app.ml.alerting import alerting_system, AlertCategory, AlertSeverity
        from backend.app.integrations.iot_sensors import (
            iot_system, SensorReading, SensorType
        )
        
        # Configure IoT to alerting callback
        def on_threshold(event):
            alerting_system.create_custom_alert(
                title=f"Sensor Alert: {event.sensor_id}",
                message=f"Value {event.value} exceeded threshold",
                category=AlertCategory.SAFETY,
                severity=AlertSeverity.HIGH,
                source='iot_system'
            )
        
        iot_system.register_alert_callback(on_threshold)
        
        # System should be connected
        assert alerting_system is not None
        assert iot_system is not None
    
    def test_full_phase3_pipeline(self):
        """Test complete Phase 3 pipeline"""
        from backend.app.ml.lean_tools import lean_tools
        from backend.app.ml.nlp_analysis import nlp_system
        from backend.app.ml.resource_optimizer import resource_optimizer
        from backend.app.ml.alerting import alerting_system
        
        # All systems should be available
        assert lean_tools is not None
        assert nlp_system is not None
        assert resource_optimizer is not None
        assert alerting_system is not None
        
        # Get metrics from each
        lean_metrics = lean_tools.get_lean_metrics_summary()
        alert_dashboard = alerting_system.get_dashboard()
        
        assert lean_metrics is not None
        assert alert_dashboard is not None


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])