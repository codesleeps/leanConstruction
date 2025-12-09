"""
Sample data fixtures for beta testing Phase 2 ML modules

This module provides realistic construction project data for testing:
- Computer vision progress monitoring
- Waste detection (DOWNTIME framework)
- Schedule and cost forecasting
- Automated reporting
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


# Pre-generated sample data for quick access
SAMPLE_PROJECT = generate_sample_project_data()
SAMPLE_PROJECTS = generate_batch_project_data(5)


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