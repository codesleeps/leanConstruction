"""
Sample data fixtures for beta testing Phase 2 and Phase 3 ML modules

This module provides realistic construction project data for testing:
- Computer vision progress monitoring
- Waste detection (DOWNTIME framework)
- Schedule and cost forecasting
- Automated reporting
- Lean tools (VSM, 5S, Kaizen, Kanban)
- NLP analysis (document classification, NER)
- Resource optimization (crew scheduling, equipment)
- Alerting and notifications
- ERP integrations
- IoT sensors
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


def generate_sample_project_data(
    project_id: str = "PROJ-001",
    project_name: str = "City Center Tower",
    days_in_progress: int = 90,
    planned_duration: int = 365,
    budget: float = 25_000_000.0,
    current_stage: str = "structural"
) -> Dict[str, Any]:
    """
    Generate comprehensive sample project data for testing
    
    Args:
        project_id: Unique project identifier
        project_name: Human-readable project name
        days_in_progress: Days since project start
        planned_duration: Total planned duration in days
        budget: Total project budget
        current_stage: Current construction stage
    
    Returns:
        Complete project data dictionary
    """
    start_date = datetime.utcnow() - timedelta(days=days_in_progress)
    end_date = start_date + timedelta(days=planned_duration)
    
    # Calculate progress
    planned_progress = (days_in_progress / planned_duration) * 100
    # Add some variance
    actual_progress = planned_progress * random.uniform(0.85, 1.15)
    actual_progress = min(max(actual_progress, 0), 100)
    
    return {
        'project_id': project_id,
        'project_name': project_name,
        'budget': budget,
        'start_date': start_date.isoformat(),
        'planned_end_date': end_date.isoformat(),
        'days_in_progress': days_in_progress,
        'planned_duration': planned_duration,
        'period_start': (datetime.utcnow() - timedelta(days=7)).isoformat(),
        'period_end': datetime.utcnow().isoformat(),
        
        # Progress data
        'progress': generate_progress_data(
            current_stage=current_stage,
            actual_progress=actual_progress,
            planned_progress=planned_progress,
            days_in_progress=days_in_progress
        ),
        
        # Waste analysis data
        'waste_analysis': generate_waste_data(),
        
        # Forecast data
        'forecast': generate_forecast_data(
            budget=budget,
            planned_duration=planned_duration,
            days_in_progress=days_in_progress
        ),
        
        # Safety data
        'safety': generate_safety_data(),
        
        # Workplace organization data
        'workplace_organization': generate_workplace_organization_data(),
        
        # Historical data for ML models
        'historical_data': generate_historical_data(days=days_in_progress)
    }


def generate_progress_data(
    current_stage: str,
    actual_progress: float,
    planned_progress: float,
    days_in_progress: int
) -> Dict[str, Any]:
    """Generate progress monitoring data"""
    
    stages = [
        'site_preparation', 'foundation', 'structural',
        'mep_rough_in', 'enclosure', 'interior_rough_in',
        'interior_finishes', 'commissioning'
    ]
    
    # Generate stage history
    stage_history = []
    for i in range(min(days_in_progress, 30)):
        date = datetime.utcnow() - timedelta(days=30-i)
        progress = actual_progress * (i / 30) if days_in_progress > 30 else actual_progress * (i / days_in_progress)
        stage_history.append({
            'date': date.isoformat(),
            'progress': progress,
            'stage': stages[min(int(progress / 12.5), len(stages) - 1)]
        })
    
    # Generate milestones
    milestones = [
        {
            'name': 'Site Preparation Complete',
            'planned_date': (datetime.utcnow() - timedelta(days=60)).isoformat(),
            'actual_date': (datetime.utcnow() - timedelta(days=58)).isoformat(),
            'status': 'completed'
        },
        {
            'name': 'Foundation Complete',
            'planned_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
            'actual_date': (datetime.utcnow() - timedelta(days=28)).isoformat(),
            'status': 'completed'
        },
        {
            'name': 'Structural Complete',
            'planned_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'actual_date': None,
            'status': 'in_progress'
        },
        {
            'name': 'Weather Tight',
            'planned_date': (datetime.utcnow() + timedelta(days=90)).isoformat(),
            'actual_date': None,
            'status': 'pending'
        }
    ]
    
    return {
        'current_stage': current_stage,
        'completion_percentage': actual_progress,
        'planned_percentage': planned_progress,
        'stage_history': stage_history,
        'milestones': milestones,
        'stall_count': random.randint(0, 3),
        'detected_activities': [
            'concrete_pouring', 'steel_erection', 'formwork_installation'
        ]
    }


def generate_waste_data() -> Dict[str, Any]:
    """Generate waste detection data following DOWNTIME framework"""
    
    waste_types = {
        'defects': {
            'detected': random.random() > 0.3,
            'severity_score': random.uniform(0.1, 0.6),
            'estimated_cost_impact': random.uniform(5000, 50000),
            'estimated_time_impact': random.uniform(2, 24),
            'indicators': ['rework_needed', 'quality_inspections_failed']
        },
        'overproduction': {
            'detected': random.random() > 0.5,
            'severity_score': random.uniform(0.05, 0.4),
            'estimated_cost_impact': random.uniform(2000, 20000),
            'estimated_time_impact': random.uniform(1, 8),
            'indicators': ['excess_materials', 'unused_prefab_elements']
        },
        'waiting': {
            'detected': random.random() > 0.4,
            'severity_score': random.uniform(0.1, 0.5),
            'estimated_cost_impact': random.uniform(3000, 30000),
            'estimated_time_impact': random.uniform(4, 40),
            'indicators': ['idle_workers', 'equipment_waiting', 'material_delays']
        },
        'non_utilized_talent': {
            'detected': random.random() > 0.6,
            'severity_score': random.uniform(0.05, 0.3),
            'estimated_cost_impact': random.uniform(1000, 15000),
            'estimated_time_impact': random.uniform(2, 16),
            'indicators': ['skill_mismatch', 'underutilized_expertise']
        },
        'transportation': {
            'detected': random.random() > 0.5,
            'severity_score': random.uniform(0.1, 0.4),
            'estimated_cost_impact': random.uniform(2000, 25000),
            'estimated_time_impact': random.uniform(3, 20),
            'indicators': ['excessive_material_movement', 'inefficient_routing']
        },
        'inventory': {
            'detected': random.random() > 0.4,
            'severity_score': random.uniform(0.1, 0.5),
            'estimated_cost_impact': random.uniform(5000, 40000),
            'estimated_time_impact': random.uniform(1, 10),
            'indicators': ['excess_stock', 'material_deterioration']
        },
        'motion': {
            'detected': random.random() > 0.5,
            'severity_score': random.uniform(0.05, 0.35),
            'estimated_cost_impact': random.uniform(1000, 12000),
            'estimated_time_impact': random.uniform(2, 15),
            'indicators': ['unnecessary_worker_movement', 'poor_site_layout']
        },
        'extra_processing': {
            'detected': random.random() > 0.6,
            'severity_score': random.uniform(0.05, 0.3),
            'estimated_cost_impact': random.uniform(2000, 18000),
            'estimated_time_impact': random.uniform(2, 12),
            'indicators': ['over_specification', 'redundant_approvals']
        }
    }
    
    # Calculate overall score
    detected_wastes = {k: v for k, v in waste_types.items() if v['detected']}
    if detected_wastes:
        overall_score = sum(v['severity_score'] for v in detected_wastes.values()) / len(detected_wastes)
    else:
        overall_score = 0.1
    
    # Calculate total impacts
    total_cost_impact = sum(v['estimated_cost_impact'] for v in detected_wastes.values())
    total_time_impact = sum(v['estimated_time_impact'] for v in detected_wastes.values())
    
    # Determine health status
    if overall_score > 0.6:
        health_status = 'critical'
    elif overall_score > 0.4:
        health_status = 'poor'
    elif overall_score > 0.2:
        health_status = 'moderate'
    else:
        health_status = 'healthy'
    
    # Generate priority actions
    priority_actions = []
    for waste_type, data in sorted(waste_types.items(), key=lambda x: x[1]['severity_score'], reverse=True)[:3]:
        if data['detected']:
            priority_actions.append({
                'waste_type': waste_type,
                'action': f"Address {waste_type.replace('_', ' ')} waste - estimated savings: ${data['estimated_cost_impact']:,.0f}",
                'priority': 'high' if data['severity_score'] > 0.4 else 'medium'
            })
    
    return {
        'detected_wastes': waste_types,
        'overall_waste_score': overall_score,
        'health_status': health_status,
        'total_cost_impact': total_cost_impact,
        'total_time_impact': total_time_impact,
        'priority_actions': priority_actions
    }


def generate_forecast_data(
    budget: float,
    planned_duration: int,
    days_in_progress: int
) -> Dict[str, Any]:
    """Generate schedule and cost forecast data"""
    
    # Schedule forecast
    schedule_variance = random.randint(-20, 15)
    predicted_completion = datetime.utcnow() + timedelta(days=planned_duration - days_in_progress + schedule_variance)
    
    # Cost forecast
    budget_variance_pct = random.uniform(-5, 15)
    predicted_cost = budget * (1 + budget_variance_pct / 100)
    current_spend = budget * (days_in_progress / planned_duration) * random.uniform(0.9, 1.1)
    
    # Risk assessment
    if abs(schedule_variance) > 15 or budget_variance_pct > 10:
        risk_level = 'high'
    elif abs(schedule_variance) > 7 or budget_variance_pct > 5:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    return {
        'schedule_forecast': {
            'predicted_completion_date': predicted_completion.isoformat(),
            'schedule_variance_days': schedule_variance,
            'confidence_level': 0.85,
            'schedule_performance_index': random.uniform(0.85, 1.15),
            'critical_path_delay': max(0, schedule_variance)
        },
        'cost_forecast': {
            'predicted_final_cost': predicted_cost,
            'budget_variance_percentage': budget_variance_pct,
            'current_spend': current_spend,
            'cost_performance_index': budget / predicted_cost,
            'contingency_remaining': budget * 0.1 - max(0, predicted_cost - budget)
        },
        'combined_risk_level': risk_level,
        'executive_summary': f"Project is forecasted to complete {'on time' if schedule_variance <= 0 else f'{schedule_variance} days late'} "
                           f"with a budget variance of {budget_variance_pct:+.1f}%. Risk level: {risk_level}.",
        'integrated_recommendations': [
            "Continue monitoring critical path activities",
            "Review resource allocation for optimal efficiency",
            "Update risk register with latest assessments",
            "Consider schedule compression if behind schedule",
            "Review change orders for cost impact"
        ][:3 if risk_level == 'low' else 5]
    }


def generate_safety_data() -> Dict[str, Any]:
    """Generate safety compliance data"""
    
    compliance_score = random.uniform(0.7, 0.98)
    
    # Generate violations if score is low
    violations = []
    if compliance_score < 0.9:
        violation_types = [
            ('Missing hard hat', 'medium', 'Issue hard hat and retrain worker'),
            ('Missing safety vest', 'low', 'Provide safety vest'),
            ('Improper scaffolding', 'high', 'Stop work and reinforce scaffolding'),
            ('Missing fall protection', 'critical', 'Immediate work stoppage, install fall protection'),
            ('Blocked emergency exit', 'high', 'Clear exit immediately'),
            ('Missing safety glasses', 'low', 'Issue safety glasses')
        ]
        
        num_violations = int((1 - compliance_score) * 15)
        selected_violations = random.sample(violation_types, min(num_violations, len(violation_types)))
        
        for label, severity, action in selected_violations:
            violations.append({
                'label': label,
                'severity': severity,
                'confidence': random.uniform(0.8, 0.99),
                'action': action,
                'location': f"Zone {random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1, 5)}",
                'detected_at': (datetime.utcnow() - timedelta(hours=random.randint(0, 48))).isoformat()
            })
    
    # Determine risk level
    critical_violations = sum(1 for v in violations if v['severity'] == 'critical')
    high_violations = sum(1 for v in violations if v['severity'] == 'high')
    
    if critical_violations > 0:
        risk_level = 'critical'
    elif high_violations > 1:
        risk_level = 'high'
    elif len(violations) > 3:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    # PPE compliance breakdown
    ppe_compliance = {
        'hard_hat': random.uniform(0.85, 1.0),
        'safety_vest': random.uniform(0.80, 1.0),
        'safety_glasses': random.uniform(0.75, 1.0),
        'gloves': random.uniform(0.70, 1.0),
        'safety_boots': random.uniform(0.90, 1.0)
    }
    
    return {
        'compliance_score': compliance_score,
        'violations': violations,
        'risk_level': risk_level,
        'ppe_compliance': ppe_compliance,
        'site_safety_items': [
            {'item': 'First Aid Station', 'status': 'compliant'},
            {'item': 'Fire Extinguishers', 'status': 'compliant'},
            {'item': 'Emergency Assembly Point', 'status': 'compliant'},
            {'item': 'Safety Signage', 'status': 'partial' if random.random() > 0.7 else 'compliant'}
        ],
        'recommendations': [
            "Conduct daily safety briefings",
            "Reinforce PPE requirements",
            "Schedule safety training refresher",
            "Review fall protection procedures",
            "Update safety signage in active zones"
        ][:len(violations) + 2]
    }


def generate_workplace_organization_data() -> Dict[str, Any]:
    """Generate 5S workplace organization data"""
    
    scores = {
        'sort': random.uniform(0.6, 0.95),
        'set_in_order': random.uniform(0.55, 0.90),
        'shine': random.uniform(0.5, 0.85),
        'standardize': random.uniform(0.6, 0.90),
        'sustain': random.uniform(0.55, 0.85)
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    # Determine grade
    if overall_score >= 0.9:
        grade = 'A'
    elif overall_score >= 0.8:
        grade = 'B'
    elif overall_score >= 0.7:
        grade = 'C'
    elif overall_score >= 0.6:
        grade = 'D'
    else:
        grade = 'F'
    
    # Certification status
    if overall_score >= 0.85:
        cert_level = 'gold'
    elif overall_score >= 0.75:
        cert_level = 'silver'
    elif overall_score >= 0.65:
        cert_level = 'bronze'
    else:
        cert_level = 'none'
    
    return {
        'overall_score': overall_score,
        'grade': grade,
        'scores': scores,
        'certification_status': {
            'level': cert_level,
            'valid_until': (datetime.utcnow() + timedelta(days=90)).isoformat() if cert_level != 'none' else None
        },
        'trend': {
            'direction': random.choice(['improving', 'stable', 'declining']),
            'change': random.uniform(-0.05, 0.08)
        },
        'recommendations': [
            "Improve tool organization in storage areas",
            "Establish daily cleaning routines",
            "Create visual management standards",
            "Implement checklist for daily 5S audits",
            "Train new workers on 5S principles"
        ][:5 if overall_score < 0.7 else 3]
    }


def generate_historical_data(days: int = 90) -> Dict[str, Any]:
    """Generate historical time series data for ML model training"""
    
    dates = [(datetime.utcnow() - timedelta(days=days-i)).isoformat()[:10] for i in range(days)]
    
    # Progress time series
    base_progress = np.linspace(0, days / 365 * 100, days)
    progress_series = base_progress + np.random.normal(0, 2, days)
    progress_series = np.clip(progress_series, 0, 100).tolist()
    
    # Cost time series
    daily_spend = np.random.normal(50000, 15000, days)
    cumulative_cost = np.cumsum(np.abs(daily_spend)).tolist()
    
    # Worker count time series
    base_workers = 50 + np.sin(np.linspace(0, 4*np.pi, days)) * 20
    worker_counts = (base_workers + np.random.normal(0, 5, days)).astype(int).tolist()
    worker_counts = [max(10, w) for w in worker_counts]
    
    # Weather conditions
    weather_conditions = [
        random.choice(['clear', 'cloudy', 'rainy', 'windy', 'hot', 'cold'])
        for _ in range(days)
    ]
    
    # Incidents
    incidents = []
    for i in range(random.randint(2, 8)):
        incidents.append({
            'date': random.choice(dates),
            'type': random.choice(['safety', 'quality', 'delay', 'equipment']),
            'severity': random.choice(['low', 'medium', 'high']),
            'resolution_days': random.randint(1, 5)
        })
    
    return {
        'dates': dates,
        'progress': progress_series,
        'cumulative_cost': cumulative_cost,
        'daily_worker_count': worker_counts,
        'weather': weather_conditions,
        'incidents': incidents,
        'deliveries': random.randint(days // 7, days // 3),
        'change_orders': random.randint(2, 15)
    }


def generate_batch_project_data(num_projects: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple sample projects for batch testing"""
    
    project_templates = [
        {"name": "City Center Tower", "budget": 25000000, "duration": 365},
        {"name": "Residential Complex Alpha", "budget": 15000000, "duration": 270},
        {"name": "Highway Bridge Extension", "budget": 35000000, "duration": 450},
        {"name": "Hospital Wing Addition", "budget": 45000000, "duration": 540},
        {"name": "School Building Renovation", "budget": 8000000, "duration": 180},
        {"name": "Industrial Warehouse", "budget": 12000000, "duration": 210},
        {"name": "Office Park Development", "budget": 30000000, "duration": 400},
        {"name": "Shopping Mall Phase 2", "budget": 50000000, "duration": 600}
    ]
    
    stages = ['site_preparation', 'foundation', 'structural', 'mep_rough_in', 
              'enclosure', 'interior_rough_in', 'interior_finishes']
    
    projects = []
    for i in range(min(num_projects, len(project_templates))):
        template = project_templates[i]
        days_progress = random.randint(30, template['duration'] - 60)
        current_stage = stages[min(int(days_progress / template['duration'] * len(stages)), len(stages) - 1)]
        
        projects.append(generate_sample_project_data(
            project_id=f"PROJ-{i+1:03d}",
            project_name=template['name'],
            days_in_progress=days_progress,
            planned_duration=template['duration'],
            budget=template['budget'],
            current_stage=current_stage
        ))
    
    return projects


# ============================================
# Phase 3 Fixtures
# ============================================

def generate_lean_tools_data() -> Dict[str, Any]:
    """Generate Lean Tools test data"""
    
    # Process steps for Value Stream Mapping
    process_steps = [
        {
            'id': f'PROC-{i:03d}',
            'name': step_name,
            'type': step_type,
            'cycle_time': random.randint(60, 3600),
            'wait_time': random.randint(30, 7200),
            'setup_time': random.randint(10, 1800),
            'defect_rate': random.uniform(0, 15),
            'value_ratio': random.uniform(0.3, 0.9)
        }
        for i, (step_name, step_type) in enumerate([
            ('Material Delivery', 'transport'),
            ('Inspection', 'inspection'),
            ('Concrete Preparation', 'value_adding'),
            ('Formwork Setup', 'necessary_non_value'),
            ('Concrete Pouring', 'value_adding'),
            ('Curing Wait', 'waiting'),
            ('Quality Check', 'inspection'),
            ('Formwork Removal', 'necessary_non_value')
        ])
    ]
    
    # 5S Assessment scores
    s5_scores = {
        'unnecessary_items': random.randint(60, 100),
        'red_tag_system': random.randint(50, 100),
        'clear_boundaries': random.randint(55, 95),
        'tool_audit': random.randint(45, 90),
        'disposal_process': random.randint(60, 95),
        'designated_locations': random.randint(70, 100),
        'visual_controls': random.randint(55, 90),
        'labeling': random.randint(50, 85),
        'ergonomic_placement': random.randint(60, 95),
        'shadow_boards': random.randint(40, 85),
        'cleaning_routine': random.randint(50, 90),
        'inspection_checklist': random.randint(55, 95),
        'spill_prevention': random.randint(60, 100),
        'tool_maintenance': random.randint(50, 90),
        'waste_segregation': random.randint(55, 85),
        'documented_procedures': random.randint(60, 95),
        'training_records': random.randint(50, 90),
        'responsibility_matrix': random.randint(55, 85),
        'standard_work_instructions': random.randint(45, 80),
        'cross_training': random.randint(40, 75),
        'regular_audits': random.randint(50, 85),
        'continuous_improvement': random.randint(55, 90),
        'management_commitment': random.randint(60, 95),
        'employee_engagement': random.randint(50, 85),
        'recognition_program': random.randint(40, 80)
    }
    
    # Kaizen events
    kaizen_events = [
        {
            'id': f'KAI-{i:03d}',
            'title': title,
            'type': ktype,
            'status': status,
            'target_improvement': random.randint(10, 50),
            'actual_improvement': random.randint(5, 60) if status == 'completed' else None,
            'team_size': random.randint(3, 8),
            'duration_days': random.randint(3, 10)
        }
        for i, (title, ktype, status) in enumerate([
            ('Reduce Setup Time', 'point', 'completed'),
            ('Improve Material Flow', 'line', 'in_progress'),
            ('Enhance Safety Procedures', 'system', 'planned'),
            ('Optimize Workspace Layout', 'plane', 'completed')
        ])
    ]
    
    # Kanban board data
    kanban_cards = [
        {
            'id': f'CARD-{i:03d}',
            'title': title,
            'status': status,
            'priority': priority,
            'assignee': f'Worker-{random.randint(1, 10)}',
            'due_date': (datetime.utcnow() + timedelta(days=random.randint(-5, 20))).isoformat()
        }
        for i, (title, status, priority) in enumerate([
            ('Pour Foundation Section A', 'done', 1),
            ('Install Steel Beams Floor 3', 'in_progress', 1),
            ('Electrical Rough-in Zone B', 'in_progress', 2),
            ('HVAC Ductwork Installation', 'ready', 2),
            ('Plumbing Rough-in Floor 2', 'blocked', 1),
            ('Drywall Installation Zone A', 'backlog', 3),
            ('Exterior Cladding North', 'review', 2),
            ('Fire Suppression System', 'backlog', 2)
        ])
    ]
    
    return {
        'process_steps': process_steps,
        's5_scores': s5_scores,
        'kaizen_events': kaizen_events,
        'kanban_cards': kanban_cards
    }


def generate_nlp_sample_documents() -> List[Dict[str, Any]]:
    """Generate sample construction documents for NLP testing"""
    
    documents = [
        {
            'id': 'DOC-001',
            'type': 'rfi',
            'title': 'RFI #42 - Concrete Specification Clarification',
            'content': """
REQUEST FOR INFORMATION

Project: Downtown Office Tower
Date: January 15, 2024
RFI Number: 42

Subject: Concrete Mix Design Clarification

We are requesting clarification on the following items:

1. The specification calls for 5000 PSI concrete for the foundation, but the drawings
   show 4000 PSI. Please clarify which is correct.

2. What is the required slump for the concrete mix?

3. Are there specific admixture requirements for cold weather placement?

Please respond by January 18, 2024 as this is affecting our schedule.

Submitted by: John Smith, Project Manager
ABC Construction Company
            """,
            'metadata': {
                'project': 'Downtown Office Tower',
                'submitted_by': 'John Smith',
                'urgency': 'high'
            }
        },
        {
            'id': 'DOC-002',
            'type': 'change_order',
            'title': 'Change Order #15 - Foundation Reinforcement',
            'content': """
CHANGE ORDER

Project: City Center Mall
Change Order Number: 15
Date: February 1, 2024

Description of Change:
Additional foundation reinforcement required due to soil conditions discovered during
excavation. The geotechnical report indicated presence of expansive clay not shown in
original borings.

Scope of Work:
- Additional #6 rebar at 12" O.C. both ways
- Increase footing depth from 4' to 6'
- Add 6" gravel drainage layer

Cost Impact: $45,000.00
Schedule Impact: 5 working days delay

Authorization Required: Owner approval within 48 hours to maintain schedule.

Prepared by: Project Manager
Approved by: ________________
            """,
            'metadata': {
                'cost_impact': 45000,
                'schedule_impact': 5,
                'status': 'pending_approval'
            }
        },
        {
            'id': 'DOC-003',
            'type': 'safety_report',
            'title': 'Daily Safety Report - January 20, 2024',
            'content': """
DAILY SAFETY REPORT

Date: January 20, 2024
Project: Highway Bridge Extension
Weather: Clear, 45°F

Safety Observations:
- All workers wearing proper PPE
- Scaffolding inspected and tagged
- Fall protection in place for elevated work
- Housekeeping satisfactory in most areas

Incidents:
- Near miss reported: Tool dropped from elevation, no injuries
- First aid case: Minor cut treated on site

Action Items:
1. Reinforce tool tethering requirements
2. Schedule toolbox talk on fall protection
3. Install additional debris netting on scaffold

Safety Score: 92/100

Report Submitted by: Safety Manager
            """,
            'metadata': {
                'safety_score': 92,
                'incidents': 2,
                'weather': 'clear'
            }
        },
        {
            'id': 'DOC-004',
            'type': 'meeting_minutes',
            'title': 'Weekly Progress Meeting - Week 5',
            'content': """
MEETING MINUTES

Project: Hospital Wing Addition
Date: January 22, 2024
Attendees: Owner Rep, Architect, GC PM, Structural Engineer, MEP Coordinator

Agenda Items Discussed:

1. Schedule Update
   - Currently 3 days ahead of schedule
   - Foundation complete
   - Structural steel delivery next week
   Action: GC to confirm crane schedule

2. Budget Status
   - 5% under budget to date
   - Change order #12 approved
   - Pending CO #13 decision needed by Friday
   Action: Owner to review and approve CO #13

3. Quality Issues
   - Concrete test results all passing
   - Minor rebar placement issue corrected
   Action: QC to document resolution

4. Safety
   - Zero recordable incidents this month
   - Safety audit scheduled for next week
   Action: All to prepare for audit

Next Meeting: January 29, 2024 at 10:00 AM

Minutes Prepared by: Project Administrator
            """,
            'metadata': {
                'project': 'Hospital Wing Addition',
                'schedule_status': 'ahead',
                'budget_status': 'under'
            }
        },
        {
            'id': 'DOC-005',
            'type': 'contract',
            'title': 'Subcontract Agreement - Electrical',
            'content': """
SUBCONTRACT AGREEMENT

This Agreement is entered into between General Contractor ("GC") and
Electrical Subcontractor ("Subcontractor").

SCOPE OF WORK:
Complete electrical installation per plans and specifications for the
Commercial Building Project including:
- Electrical rough-in
- Panel installation
- Lighting fixtures
- Fire alarm system

CONTRACT PRICE: $850,000.00

PAYMENT TERMS:
Progress payments monthly based on percentage complete.
Retainage: 10% until substantial completion.
Final payment within 30 days of completion.

SCHEDULE:
Start Date: February 1, 2024
Completion Date: August 15, 2024

WARRANTY:
Subcontractor warrants all work for a period of one year from substantial completion.

INSURANCE REQUIREMENTS:
- General Liability: $2,000,000
- Workers Compensation: As required by law
- Automotive: $1,000,000

INDEMNIFICATION:
Subcontractor shall indemnify and hold harmless the GC from all claims arising
from Subcontractor's work.

CHANGE ORDERS:
All changes must be approved in writing before work proceeds.
            """,
            'metadata': {
                'contract_value': 850000,
                'trade': 'electrical',
                'duration_months': 6
            }
        }
    ]
    
    return documents


def generate_resource_optimization_data() -> Dict[str, Any]:
    """Generate resource optimization test data"""
    
    # Workers/crew data
    workers = [
        {
            'id': f'W-{i:03d}',
            'name': f'Worker {i}',
            'skills': skills,
            'hourly_rate': rate,
            'availability': random.uniform(0.8, 1.0),
            'efficiency_rating': random.uniform(0.7, 1.0)
        }
        for i, (skills, rate) in enumerate([
            (['carpenter', 'framing'], 45.00),
            (['carpenter', 'finish'], 50.00),
            (['electrician'], 55.00),
            (['electrician', 'low_voltage'], 52.00),
            (['plumber'], 55.00),
            (['plumber', 'hvac'], 58.00),
            (['mason', 'concrete'], 48.00),
            (['mason', 'brick'], 46.00),
            (['ironworker', 'structural'], 60.00),
            (['laborer'], 35.00)
        ])
    ]
    
    # Tasks to be scheduled
    tasks = [
        {
            'id': f'T-{i:03d}',
            'name': name,
            'duration_hours': duration,
            'required_skills': skills,
            'required_workers': workers_needed,
            'predecessors': preds,
            'priority': priority
        }
        for i, (name, duration, skills, workers_needed, preds, priority) in enumerate([
            ('Foundation Layout', 8, ['laborer'], 2, [], 1),
            ('Excavation', 16, ['laborer'], 3, ['T-000'], 1),
            ('Rebar Installation', 12, ['ironworker'], 2, ['T-001'], 1),
            ('Concrete Pour', 6, ['mason', 'laborer'], 4, ['T-002'], 1),
            ('Framing Floor 1', 24, ['carpenter'], 3, ['T-003'], 2),
            ('Electrical Rough-in', 20, ['electrician'], 2, ['T-004'], 2),
            ('Plumbing Rough-in', 18, ['plumber'], 2, ['T-004'], 2),
            ('HVAC Installation', 16, ['hvac'], 2, ['T-004'], 3),
            ('Drywall', 20, ['carpenter'], 3, ['T-005', 'T-006', 'T-007'], 3),
            ('Electrical Finish', 12, ['electrician'], 2, ['T-008'], 4)
        ])
    ]
    
    # Equipment data
    equipment = [
        {
            'id': f'E-{i:03d}',
            'name': name,
            'type': etype,
            'daily_rate': rate,
            'capacity': capacity,
            'availability': avail
        }
        for i, (name, etype, rate, capacity, avail) in enumerate([
            ('Tower Crane #1', 'crane', 1500, 20, 'available'),
            ('Tower Crane #2', 'crane', 1500, 20, 'in_use'),
            ('Excavator Cat 320', 'excavator', 800, 1, 'available'),
            ('Concrete Pump', 'pump', 600, 1, 'available'),
            ('Boom Lift 60ft', 'lift', 350, 2, 'available'),
            ('Scissor Lift', 'lift', 200, 4, 'available'),
            ('Forklift 8000lb', 'forklift', 250, 2, 'available'),
            ('Generator 100kW', 'generator', 300, 3, 'in_use')
        ])
    ]
    
    # Material deliveries
    deliveries = [
        {
            'id': f'D-{i:03d}',
            'material': material,
            'quantity': qty,
            'unit': unit,
            'supplier': supplier,
            'delivery_date': (datetime.utcnow() + timedelta(days=days)).isoformat(),
            'priority': priority
        }
        for i, (material, qty, unit, supplier, days, priority) in enumerate([
            ('Concrete - 5000 PSI', 150, 'yards', 'Ready Mix Co', 2, 1),
            ('Rebar #5', 10000, 'lbs', 'Steel Supply', 1, 1),
            ('Lumber 2x4', 500, 'bf', 'Building Materials', 3, 2),
            ('Electrical Wire', 5000, 'ft', 'Electric Wholesale', 4, 2),
            ('PVC Pipe 4"', 200, 'ft', 'Plumbing Supply', 4, 2),
            ('Drywall 4x8', 200, 'sheets', 'Building Materials', 7, 3),
            ('Steel Beams W12', 25, 'ea', 'Steel Supply', 5, 1),
            ('HVAC Ductwork', 100, 'ft', 'HVAC Distributors', 6, 2)
        ])
    ]
    
    return {
        'workers': workers,
        'tasks': tasks,
        'equipment': equipment,
        'deliveries': deliveries
    }


def generate_alerting_data() -> Dict[str, Any]:
    """Generate alerting system test data"""
    
    # Metrics that might trigger alerts
    metrics = {
        'safety.incidents': random.randint(0, 2),
        'safety.near_misses': random.randint(0, 5),
        'safety.compliance_score': random.uniform(0.75, 1.0),
        'schedule.variance_days': random.randint(-5, 20),
        'schedule.critical_path_delay': random.randint(0, 10),
        'schedule.milestone_at_risk': random.randint(0, 3),
        'cost.variance_percentage': random.uniform(-5, 15),
        'cost.burn_rate_deviation': random.uniform(-10, 20),
        'quality.defect_rate': random.uniform(0, 10),
        'quality.rework_percentage': random.uniform(0, 8),
        'resource.utilization': random.uniform(0.6, 1.0),
        'resource.overtime_hours': random.randint(0, 50),
        'equipment.downtime_hours': random.randint(0, 20),
        'equipment.maintenance_overdue': random.randint(0, 5),
        'weather.temperature': random.uniform(20, 100),
        'weather.wind_speed': random.uniform(0, 40),
        'weather.precipitation': random.uniform(0, 2),
        'environmental.dust_level': random.uniform(0, 200),
        'environmental.noise_level': random.uniform(50, 100)
    }
    
    # Sample alerts
    alerts = [
        {
            'id': f'ALERT-{i:03d}',
            'title': title,
            'category': category,
            'severity': severity,
            'status': status,
            'message': message,
            'created_at': (datetime.utcnow() - timedelta(hours=random.randint(0, 72))).isoformat()
        }
        for i, (title, category, severity, status, message) in enumerate([
            ('Schedule Delay Alert', 'schedule', 'high', 'active',
             'Critical path delay of 5 days detected'),
            ('Cost Overrun Warning', 'cost', 'medium', 'acknowledged',
             'Budget variance exceeded 10%'),
            ('Safety Incident', 'safety', 'critical', 'in_progress',
             'Near-miss incident reported on Level 3'),
            ('Equipment Maintenance Due', 'equipment', 'low', 'active',
             'Crane #1 maintenance overdue by 2 days'),
            ('Weather Advisory', 'weather', 'medium', 'active',
             'High winds expected tomorrow'),
            ('Quality Issue', 'quality', 'high', 'resolved',
             'Concrete test failed specifications'),
            ('Resource Shortage', 'resource', 'medium', 'active',
             'Electrical crew understaffed for scheduled work')
        ])
    ]
    
    # Notification preferences
    notification_settings = {
        'email_enabled': True,
        'sms_enabled': True,
        'push_enabled': True,
        'escalation_enabled': True,
        'quiet_hours': {
            'enabled': False,
            'start': '22:00',
            'end': '07:00'
        },
        'channels_by_severity': {
            'critical': ['email', 'sms', 'push'],
            'high': ['email', 'push'],
            'medium': ['email'],
            'low': ['email'],
            'info': []
        }
    }
    
    return {
        'metrics': metrics,
        'alerts': alerts,
        'notification_settings': notification_settings
    }


def generate_erp_integration_data() -> Dict[str, Any]:
    """Generate ERP integration test data"""
    
    # Projects from ERP
    erp_projects = [
        {
            'erp_id': f'SAP-PRJ-{i:04d}',
            'name': name,
            'code': code,
            'status': status,
            'budget': budget,
            'start_date': (datetime.utcnow() - timedelta(days=random.randint(30, 180))).isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=random.randint(60, 365))).isoformat()
        }
        for i, (name, code, status, budget) in enumerate([
            ('Downtown Tower', 'DT-2024-001', 'active', 25000000),
            ('Highway Extension', 'HW-2024-002', 'active', 35000000),
            ('Hospital Addition', 'HA-2024-003', 'active', 45000000),
            ('School Renovation', 'SR-2024-004', 'planning', 8000000)
        ])
    ]
    
    # Cost codes
    cost_codes = [
        {
            'code': code,
            'description': desc,
            'category': cat,
            'budget': random.randint(50000, 500000)
        }
        for code, desc, cat in [
            ('01-001', 'General Requirements', 'general'),
            ('02-001', 'Site Work', 'sitework'),
            ('03-001', 'Concrete', 'concrete'),
            ('04-001', 'Masonry', 'masonry'),
            ('05-001', 'Metals', 'metals'),
            ('06-001', 'Wood and Plastics', 'carpentry'),
            ('07-001', 'Thermal and Moisture', 'envelope'),
            ('09-001', 'Finishes', 'finishes'),
            ('15-001', 'Mechanical', 'mep'),
            ('16-001', 'Electrical', 'mep')
        ]
    ]
    
    # Job costs
    job_costs = [
        {
            'transaction_id': f'JC-{i:06d}',
            'project_code': random.choice(['DT-2024-001', 'HW-2024-002']),
            'cost_code': random.choice([c['code'] for c in cost_codes]),
            'amount': random.uniform(1000, 50000),
            'type': random.choice(['labor', 'material', 'equipment', 'subcontract']),
            'date': (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
            'description': f'Cost transaction {i}'
        }
        for i in range(20)
    ]
    
    # Purchase orders
    purchase_orders = [
        {
            'po_number': f'PO-{i:05d}',
            'vendor': vendor,
            'project_code': 'DT-2024-001',
            'amount': amount,
            'status': status,
            'items': items
        }
        for i, (vendor, amount, status, items) in enumerate([
            ('Ready Mix Concrete', 75000, 'approved', 3),
            ('Steel Fabricators', 125000, 'approved', 5),
            ('Electrical Wholesale', 45000, 'pending', 12),
            ('Plumbing Supply', 35000, 'approved', 8),
            ('HVAC Equipment', 85000, 'draft', 4)
        ])
    ]
    
    return {
        'projects': erp_projects,
        'cost_codes': cost_codes,
        'job_costs': job_costs,
        'purchase_orders': purchase_orders
    }


def generate_iot_sensor_data() -> Dict[str, Any]:
    """Generate IoT sensor test data"""
    
    # Sensor configurations
    sensors = [
        {
            'sensor_id': f'SENS-{i:03d}',
            'device_id': f'DEV-{i // 3:02d}',
            'type': stype,
            'name': name,
            'location': location,
            'unit': unit,
            'thresholds': thresholds
        }
        for i, (stype, name, location, unit, thresholds) in enumerate([
            ('temperature', 'Ambient Temp', 'Site Office', '°C',
             {'warning_low': 5, 'warning_high': 35, 'critical_low': 0, 'critical_high': 40}),
            ('humidity', 'Humidity', 'Site Office', '%',
             {'warning_low': 20, 'warning_high': 80, 'critical_low': 10, 'critical_high': 90}),
            ('dust', 'Dust Level', 'Work Area A', 'µg/m³',
             {'warning_high': 100, 'critical_high': 150}),
            ('noise', 'Noise Level', 'Work Area A', 'dB',
             {'warning_high': 85, 'critical_high': 100}),
            ('vibration', 'Vibration', 'Foundation', 'mm/s',
             {'warning_high': 15, 'critical_high': 25}),
            ('temperature', 'Concrete Temp', 'Pour Zone', '°C',
             {'warning_low': 10, 'warning_high': 30, 'critical_low': 5, 'critical_high': 35}),
            ('strain', 'Structural Strain', 'Column A1', 'µε',
             {'warning_high': 1500, 'critical_high': 2000}),
            ('tilt', 'Tilt Sensor', 'Tower Crane', '°',
             {'warning_high': 3, 'critical_high': 5}),
            ('gas', 'CO Level', 'Basement', 'ppm',
             {'warning_high': 35, 'critical_high': 100}),
            ('wind', 'Wind Speed', 'Roof Level', 'm/s',
             {'warning_high': 15, 'critical_high': 25})
        ])
    ]
    
    # Historical readings (last 24 hours)
    readings = []
    for sensor in sensors:
        base_value = {
            'temperature': 22, 'humidity': 55, 'dust': 45, 'noise': 72,
            'vibration': 5, 'strain': 800, 'tilt': 0.5, 'gas': 5, 'wind': 8
        }.get(sensor['type'], 50)
        
        for h in range(24):
            readings.append({
                'sensor_id': sensor['sensor_id'],
                'timestamp': (datetime.utcnow() - timedelta(hours=24-h)).isoformat(),
                'value': base_value + random.uniform(-10, 10),
                'quality': 'good' if random.random() > 0.05 else 'suspect'
            })
    
    # Device status
    devices = [
        {
            'device_id': f'DEV-{i:02d}',
            'name': name,
            'type': dtype,
            'status': status,
            'battery_level': random.randint(20, 100) if status == 'online' else None,
            'last_seen': (datetime.utcnow() - timedelta(minutes=random.randint(0, 120))).isoformat()
        }
        for i, (name, dtype, status) in enumerate([
            ('Weather Station', 'weather_station', 'online'),
            ('Dust Monitor A', 'air_quality', 'online'),
            ('Structural Monitor', 'structural', 'online'),
            ('Safety Monitor', 'safety', 'offline'),
            ('Crane Sensor', 'equipment', 'online')
        ])
    ]
    
    # Alert events from sensors
    sensor_alerts = [
        {
            'alert_id': f'IOT-ALERT-{i:03d}',
            'sensor_id': sensors[random.randint(0, len(sensors)-1)]['sensor_id'],
            'level': level,
            'message': message,
            'timestamp': (datetime.utcnow() - timedelta(hours=random.randint(0, 48))).isoformat(),
            'acknowledged': random.choice([True, False])
        }
        for i, (level, message) in enumerate([
            ('warning', 'Temperature exceeded warning threshold'),
            ('critical', 'Dust level critical - stop work required'),
            ('warning', 'High wind speed detected'),
            ('info', 'Device battery low'),
            ('warning', 'Noise level elevated')
        ])
    ]
    
    return {
        'sensors': sensors,
        'readings': readings,
        'devices': devices,
        'alerts': sensor_alerts
    }


# Pre-generated sample data for quick access
SAMPLE_PROJECT = generate_sample_project_data()
SAMPLE_PROJECTS = generate_batch_project_data(5)

# Phase 3 sample data
SAMPLE_LEAN_TOOLS_DATA = generate_lean_tools_data()
SAMPLE_NLP_DOCUMENTS = generate_nlp_sample_documents()
SAMPLE_RESOURCE_DATA = generate_resource_optimization_data()
SAMPLE_ALERTING_DATA = generate_alerting_data()
SAMPLE_ERP_DATA = generate_erp_integration_data()
SAMPLE_IOT_DATA = generate_iot_sensor_data()


if __name__ == "__main__":
    # Test data generation
    import json
    
    project = generate_sample_project_data()
    print("Sample Project Data Generated:")
    print(json.dumps({
        'project_id': project['project_id'],
        'project_name': project['project_name'],
        'progress': project['progress']['completion_percentage'],
        'waste_score': project['waste_analysis']['overall_waste_score'],
        'safety_score': project['safety']['compliance_score']
    }, indent=2))
    
    # Phase 3 data summary
    print("\nPhase 3 Sample Data Generated:")
    print(f"  - Lean Tools: {len(SAMPLE_LEAN_TOOLS_DATA['process_steps'])} process steps, "
          f"{len(SAMPLE_LEAN_TOOLS_DATA['kaizen_events'])} kaizen events")
    print(f"  - NLP Documents: {len(SAMPLE_NLP_DOCUMENTS)} sample documents")
    print(f"  - Resource Data: {len(SAMPLE_RESOURCE_DATA['workers'])} workers, "
          f"{len(SAMPLE_RESOURCE_DATA['tasks'])} tasks")
    print(f"  - Alerting Data: {len(SAMPLE_ALERTING_DATA['alerts'])} sample alerts")
    print(f"  - ERP Data: {len(SAMPLE_ERP_DATA['projects'])} projects, "
          f"{len(SAMPLE_ERP_DATA['job_costs'])} transactions")
    print(f"  - IoT Data: {len(SAMPLE_IOT_DATA['sensors'])} sensors, "
          f"{len(SAMPLE_IOT_DATA['readings'])} readings")