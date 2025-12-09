"""
Automated Reporting System - Phase 2
Generates comprehensive construction analytics reports integrating:
- Computer vision progress monitoring
- Waste detection analysis (DOWNTIME)
- Schedule and cost forecasting
- Resource optimization recommendations
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
from abc import ABC, abstractmethod
import io
import base64

# Import ML components
from .computer_vision import (
    ProgressMonitoringModel,
    SafetyComplianceDetector,
    EquipmentTracker,
    WorkplaceOrganizationAnalyzer
)
from .waste_detection import WasteDetectionEngine, WasteType
from .predictive_models import (
    IntegratedForecastingSystem,
    ScheduleForecastingModel,
    CostPredictionEnsemble,
    RiskLevel
)

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports available"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    EXECUTIVE = "executive"
    WASTE_ANALYSIS = "waste_analysis"
    PROGRESS = "progress"
    SAFETY = "safety"
    FORECAST = "forecast"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Output formats for reports"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"


@dataclass
class ReportSection:
    """Individual section of a report"""
    title: str
    content: Dict[str, Any]
    summary: str
    charts: List[Dict] = field(default_factory=list)
    tables: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    priority: int = 1  # 1 = highest priority


@dataclass
class ReportMetadata:
    """Metadata for generated reports"""
    report_id: str
    report_type: ReportType
    project_id: str
    project_name: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    generated_by: str = "LeanConstruction AI"
    version: str = "2.0"


class ReportGenerator(ABC):
    """Abstract base class for report generators"""
    
    @abstractmethod
    def generate(self, data: Dict) -> Dict:
        """Generate report content"""
        pass
    
    @abstractmethod
    def get_summary(self, data: Dict) -> str:
        """Generate executive summary"""
        pass


class ProgressReportGenerator(ReportGenerator):
    """Generates progress monitoring reports"""
    
    def __init__(self):
        self.progress_model = ProgressMonitoringModel()
    
    def generate(self, data: Dict) -> ReportSection:
        """Generate progress report section"""
        progress_data = data.get('progress', {})
        
        # Calculate progress metrics
        current_stage = progress_data.get('current_stage', 'unknown')
        completion_pct = progress_data.get('completion_percentage', 0)
        planned_pct = progress_data.get('planned_percentage', 0)
        variance = completion_pct - planned_pct
        
        # Stage history
        stage_history = progress_data.get('stage_history', [])
        
        # Generate charts data
        charts = [
            {
                'type': 'progress_bar',
                'title': 'Overall Progress',
                'data': {
                    'actual': completion_pct,
                    'planned': planned_pct
                }
            },
            {
                'type': 'line_chart',
                'title': 'Progress Over Time',
                'data': stage_history
            }
        ]
        
        # Generate tables
        tables = [
            {
                'title': 'Progress Summary',
                'headers': ['Metric', 'Value', 'Status'],
                'rows': [
                    ['Current Stage', current_stage, self._get_status_indicator(variance)],
                    ['Completion %', f'{completion_pct:.1f}%', ''],
                    ['Planned %', f'{planned_pct:.1f}%', ''],
                    ['Variance', f'{variance:+.1f}%', self._get_variance_status(variance)]
                ]
            }
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(variance, progress_data)
        
        return ReportSection(
            title='Construction Progress',
            content={
                'current_stage': current_stage,
                'completion_percentage': completion_pct,
                'planned_percentage': planned_pct,
                'variance': variance,
                'is_on_track': variance >= -5,
                'stage_history': stage_history,
                'milestones': progress_data.get('milestones', [])
            },
            summary=self.get_summary(progress_data),
            charts=charts,
            tables=tables,
            recommendations=recommendations,
            priority=1 if variance < -10 else 2
        )
    
    def get_summary(self, data: Dict) -> str:
        """Generate progress summary"""
        completion = data.get('completion_percentage', 0)
        planned = data.get('planned_percentage', 0)
        variance = completion - planned
        
        if variance >= 5:
            status = "ahead of schedule"
        elif variance >= -5:
            status = "on track"
        elif variance >= -15:
            status = "slightly behind schedule"
        else:
            status = "significantly behind schedule"
        
        return (
            f"Project is currently {status} with {completion:.1f}% complete "
            f"({variance:+.1f}% vs plan). Current construction stage: "
            f"{data.get('current_stage', 'unknown')}."
        )
    
    def _get_status_indicator(self, variance: float) -> str:
        if variance >= 0:
            return "✅ On Track"
        elif variance >= -10:
            return "⚠️ Attention"
        else:
            return "🚨 Critical"
    
    def _get_variance_status(self, variance: float) -> str:
        if variance >= 5:
            return "Ahead"
        elif variance >= -5:
            return "On Track"
        elif variance >= -15:
            return "Behind"
        else:
            return "Critical"
    
    def _generate_recommendations(self, variance: float, data: Dict) -> List[str]:
        recommendations = []
        
        if variance < -15:
            recommendations.append(
                "URGENT: Schedule recovery meeting to address significant delays"
            )
            recommendations.append(
                "Consider fast-tracking critical path activities"
            )
        elif variance < -5:
            recommendations.append(
                "Review schedule and identify opportunities to accelerate"
            )
        
        if data.get('stall_count', 0) > 2:
            recommendations.append(
                "Multiple progress stalls detected - investigate root causes"
            )
        
        if not recommendations:
            recommendations.append("Continue current pace to maintain schedule")
        
        return recommendations


class WasteReportGenerator(ReportGenerator):
    """Generates waste analysis reports (DOWNTIME framework)"""
    
    def __init__(self):
        self.waste_engine = WasteDetectionEngine()
    
    def generate(self, data: Dict) -> ReportSection:
        """Generate waste analysis report section"""
        waste_data = data.get('waste_analysis', {})
        
        # Get waste detection results
        detected_wastes = waste_data.get('detected_wastes', {})
        overall_score = waste_data.get('overall_waste_score', 0)
        health_status = waste_data.get('health_status', 'unknown')
        
        # Build waste breakdown
        waste_breakdown = []
        for waste_type, waste_info in detected_wastes.items():
            waste_breakdown.append({
                'type': waste_type,
                'detected': waste_info.get('detected', False),
                'severity': waste_info.get('severity_score', 0),
                'cost_impact': waste_info.get('estimated_cost_impact', 0),
                'time_impact': waste_info.get('estimated_time_impact', 0)
            })
        
        # Sort by severity
        waste_breakdown.sort(key=lambda x: x['severity'], reverse=True)
        
        # Charts
        charts = [
            {
                'type': 'radar_chart',
                'title': 'Waste Profile (DOWNTIME)',
                'data': {
                    waste['type']: waste['severity'] 
                    for waste in waste_breakdown
                }
            },
            {
                'type': 'bar_chart',
                'title': 'Cost Impact by Waste Type',
                'data': {
                    waste['type']: waste['cost_impact'] 
                    for waste in waste_breakdown
                }
            }
        ]
        
        # Tables
        tables = [
            {
                'title': 'Waste Detection Summary',
                'headers': ['Waste Type', 'Detected', 'Severity', 'Cost Impact', 'Time Impact'],
                'rows': [
                    [
                        waste['type'].replace('_', ' ').title(),
                        '✓' if waste['detected'] else '✗',
                        f"{waste['severity']:.0%}",
                        f"${waste['cost_impact']:,.0f}",
                        f"{waste['time_impact']:.1f} hrs"
                    ]
                    for waste in waste_breakdown
                ]
            }
        ]
        
        # Recommendations from priority actions
        recommendations = [
            action.get('action', '')
            for action in waste_data.get('priority_actions', [])[:5]
        ]
        
        return ReportSection(
            title='Lean Waste Analysis (DOWNTIME)',
            content={
                'overall_score': overall_score,
                'health_status': health_status,
                'waste_breakdown': waste_breakdown,
                'total_cost_impact': sum(w['cost_impact'] for w in waste_breakdown),
                'total_time_impact': sum(w['time_impact'] for w in waste_breakdown),
                'critical_wastes': [
                    w['type'] for w in waste_breakdown if w['severity'] > 0.6
                ]
            },
            summary=self.get_summary(waste_data),
            charts=charts,
            tables=tables,
            recommendations=recommendations,
            priority=1 if overall_score > 0.5 else 2
        )
    
    def get_summary(self, data: Dict) -> str:
        """Generate waste analysis summary"""
        score = data.get('overall_waste_score', 0)
        health = data.get('health_status', 'unknown')
        detected_count = len([
            w for w in data.get('detected_wastes', {}).values()
            if w.get('detected', False)
        ])
        total_cost = data.get('total_cost_impact', 0)
        
        return (
            f"Waste analysis indicates {health} project health (score: {score:.0%}). "
            f"{detected_count} waste type(s) detected with estimated total cost impact "
            f"of ${total_cost:,.0f}."
        )


class ForecastReportGenerator(ReportGenerator):
    """Generates schedule and cost forecast reports"""
    
    def __init__(self):
        self.forecasting_system = IntegratedForecastingSystem()
    
    def generate(self, data: Dict) -> ReportSection:
        """Generate forecast report section"""
        forecast_data = data.get('forecast', {})
        
        schedule = forecast_data.get('schedule_forecast', {})
        cost = forecast_data.get('cost_forecast', {})
        
        # Schedule metrics
        schedule_variance = schedule.get('schedule_variance_days', 0)
        completion_date = schedule.get('predicted_completion_date', 'TBD')
        
        # Cost metrics
        budget_variance = cost.get('budget_variance_percentage', 0)
        predicted_cost = cost.get('predicted_final_cost', 0)
        budget = data.get('budget', predicted_cost)
        
        # Risk level
        combined_risk = forecast_data.get('combined_risk_level', 'medium')
        
        # Charts
        charts = [
            {
                'type': 'gauge',
                'title': 'Schedule Risk',
                'data': {
                    'value': abs(schedule_variance),
                    'max': 60,
                    'zones': [
                        {'min': 0, 'max': 7, 'color': 'green'},
                        {'min': 7, 'max': 14, 'color': 'yellow'},
                        {'min': 14, 'max': 30, 'color': 'orange'},
                        {'min': 30, 'max': 60, 'color': 'red'}
                    ]
                }
            },
            {
                'type': 'cost_comparison',
                'title': 'Budget vs Forecast',
                'data': {
                    'budget': budget,
                    'forecast': predicted_cost,
                    'variance': budget_variance
                }
            }
        ]
        
        # Tables
        tables = [
            {
                'title': 'Forecast Summary',
                'headers': ['Metric', 'Current', 'Forecast', 'Variance'],
                'rows': [
                    [
                        'Schedule',
                        'Today',
                        str(completion_date)[:10] if completion_date else 'TBD',
                        f"{schedule_variance:+d} days"
                    ],
                    [
                        'Cost',
                        f"${budget:,.0f}",
                        f"${predicted_cost:,.0f}",
                        f"{budget_variance:+.1f}%"
                    ]
                ]
            }
        ]
        
        # Get recommendations
        recommendations = forecast_data.get('integrated_recommendations', [])
        
        return ReportSection(
            title='Project Forecast',
            content={
                'schedule_variance_days': schedule_variance,
                'predicted_completion_date': completion_date,
                'budget_variance_percentage': budget_variance,
                'predicted_final_cost': predicted_cost,
                'combined_risk_level': combined_risk,
                'confidence_level': schedule.get('confidence_level', 0.95)
            },
            summary=self.get_summary(forecast_data),
            charts=charts,
            tables=tables,
            recommendations=recommendations[:5],
            priority=1 if combined_risk in ['critical', 'high'] else 2
        )
    
    def get_summary(self, data: Dict) -> str:
        """Generate forecast summary"""
        return data.get('executive_summary', 'Forecast data unavailable.')


class SafetyReportGenerator(ReportGenerator):
    """Generates safety compliance reports"""
    
    def __init__(self):
        self.safety_detector = SafetyComplianceDetector()
    
    def generate(self, data: Dict) -> ReportSection:
        """Generate safety report section"""
        safety_data = data.get('safety', {})
        
        compliance_score = safety_data.get('compliance_score', 0)
        violations = safety_data.get('violations', [])
        risk_level = safety_data.get('risk_level', 'unknown')
        
        # Charts
        charts = [
            {
                'type': 'gauge',
                'title': 'Safety Compliance Score',
                'data': {
                    'value': compliance_score * 100,
                    'max': 100,
                    'zones': [
                        {'min': 0, 'max': 60, 'color': 'red'},
                        {'min': 60, 'max': 80, 'color': 'yellow'},
                        {'min': 80, 'max': 100, 'color': 'green'}
                    ]
                }
            }
        ]
        
        # Tables
        if violations:
            tables = [
                {
                    'title': 'Safety Violations',
                    'headers': ['Violation', 'Severity', 'Required Action'],
                    'rows': [
                        [
                            v.get('label', 'Unknown'),
                            v.get('severity', 'medium'),
                            v.get('action', 'Review required')
                        ]
                        for v in violations[:10]
                    ]
                }
            ]
        else:
            tables = [
                {
                    'title': 'Safety Status',
                    'headers': ['Status', 'Details'],
                    'rows': [
                        ['Compliance Score', f"{compliance_score:.0%}"],
                        ['Risk Level', risk_level.title()],
                        ['Violations', 'None detected']
                    ]
                }
            ]
        
        recommendations = safety_data.get('recommendations', [])
        
        return ReportSection(
            title='Safety Compliance',
            content={
                'compliance_score': compliance_score,
                'is_compliant': compliance_score >= 0.8,
                'violation_count': len(violations),
                'risk_level': risk_level,
                'ppe_compliance': safety_data.get('ppe_compliance', {}),
                'site_safety_items': safety_data.get('site_safety_items', [])
            },
            summary=self.get_summary(safety_data),
            charts=charts,
            tables=tables,
            recommendations=recommendations[:5],
            priority=1 if risk_level in ['critical', 'high'] else 3
        )
    
    def get_summary(self, data: Dict) -> str:
        """Generate safety summary"""
        score = data.get('compliance_score', 0)
        violations = len(data.get('violations', []))
        risk = data.get('risk_level', 'unknown')
        
        status = "compliant" if score >= 0.8 else "non-compliant"
        
        return (
            f"Site safety is {status} with {score:.0%} compliance score. "
            f"{violations} violation(s) detected. Risk level: {risk}."
        )


class WorkplaceOrganizationReportGenerator(ReportGenerator):
    """Generates 5S workplace organization reports"""
    
    def __init__(self):
        self.analyzer = WorkplaceOrganizationAnalyzer()
    
    def generate(self, data: Dict) -> ReportSection:
        """Generate 5S report section"""
        org_data = data.get('workplace_organization', {})
        
        overall_score = org_data.get('overall_score', 0)
        grade = org_data.get('grade', 'N/A')
        scores = org_data.get('scores', {})
        
        # Charts
        charts = [
            {
                'type': 'radar_chart',
                'title': '5S Assessment',
                'data': scores
            }
        ]
        
        # Tables
        tables = [
            {
                'title': '5S Scores',
                'headers': ['Category', 'Score', 'Status'],
                'rows': [
                    [
                        cat.replace('_', ' ').title(),
                        f"{score:.0%}",
                        '✓ Pass' if score >= 0.7 else '✗ Improve'
                    ]
                    for cat, score in scores.items()
                ]
            }
        ]
        
        recommendations = org_data.get('recommendations', [])
        
        return ReportSection(
            title='5S Workplace Organization',
            content={
                'overall_score': overall_score,
                'grade': grade,
                'scores': scores,
                'certification_status': org_data.get('certification_status', {}),
                'trend': org_data.get('trend', {})
            },
            summary=self.get_summary(org_data),
            charts=charts,
            tables=tables,
            recommendations=recommendations[:5],
            priority=3
        )
    
    def get_summary(self, data: Dict) -> str:
        """Generate 5S summary"""
        score = data.get('overall_score', 0)
        grade = data.get('grade', 'N/A')
        cert = data.get('certification_status', {})
        
        cert_level = cert.get('level', 'none')
        
        return (
            f"Workplace organization score: {score:.0%} (Grade: {grade}). "
            f"5S certification level: {cert_level.title()}."
        )


class AutomatedReportingSystem:
    """
    Main automated reporting system that orchestrates all report generators
    """
    
    def __init__(self):
        self.generators = {
            'progress': ProgressReportGenerator(),
            'waste': WasteReportGenerator(),
            'forecast': ForecastReportGenerator(),
            'safety': SafetyReportGenerator(),
            'workplace': WorkplaceOrganizationReportGenerator()
        }
        
        self.report_history: List[Dict] = []
        self.templates: Dict[ReportType, List[str]] = {
            ReportType.DAILY: ['progress', 'safety'],
            ReportType.WEEKLY: ['progress', 'waste', 'safety', 'workplace'],
            ReportType.MONTHLY: ['progress', 'waste', 'forecast', 'safety', 'workplace'],
            ReportType.EXECUTIVE: ['progress', 'forecast'],
            ReportType.WASTE_ANALYSIS: ['waste'],
            ReportType.PROGRESS: ['progress'],
            ReportType.SAFETY: ['safety'],
            ReportType.FORECAST: ['forecast'],
            ReportType.COMPREHENSIVE: ['progress', 'waste', 'forecast', 'safety', 'workplace']
        }
    
    def generate_report(
        self,
        project_data: Dict,
        report_type: ReportType = ReportType.DAILY,
        custom_sections: Optional[List[str]] = None,
        output_format: ReportFormat = ReportFormat.JSON
    ) -> Dict:
        """
        Generate a complete report
        
        Args:
            project_data: Project data for report generation
            report_type: Type of report to generate
            custom_sections: Custom sections for CUSTOM report type
            output_format: Output format for the report
        
        Returns:
            Complete report dictionary
        """
        # Determine sections to include
        if report_type == ReportType.CUSTOM and custom_sections:
            sections_to_include = custom_sections
        else:
            sections_to_include = self.templates.get(report_type, ['progress'])
        
        # Generate metadata
        metadata = ReportMetadata(
            report_id=self._generate_report_id(),
            report_type=report_type,
            project_id=project_data.get('project_id', 'unknown'),
            project_name=project_data.get('project_name', 'Unknown Project'),
            generated_at=datetime.utcnow(),
            period_start=project_data.get('period_start', datetime.utcnow() - timedelta(days=1)),
            period_end=project_data.get('period_end', datetime.utcnow())
        )
        
        # Generate sections
        sections = []
        for section_name in sections_to_include:
            if section_name in self.generators:
                try:
                    section = self.generators[section_name].generate(project_data)
                    sections.append(section)
                except Exception as e:
                    logger.error(f"Error generating {section_name} section: {e}")
                    sections.append(ReportSection(
                        title=section_name.title(),
                        content={'error': str(e)},
                        summary=f"Error generating {section_name} report",
                        recommendations=[]
                    ))
        
        # Sort sections by priority
        sections.sort(key=lambda x: x.priority)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(sections, project_data)
        
        # Build report
        report = {
            'metadata': asdict(metadata) if hasattr(metadata, '__dataclass_fields__') else {
                'report_id': metadata.report_id,
                'report_type': metadata.report_type.value,
                'project_id': metadata.project_id,
                'project_name': metadata.project_name,
                'generated_at': metadata.generated_at.isoformat(),
                'period_start': metadata.period_start.isoformat() if isinstance(metadata.period_start, datetime) else str(metadata.period_start),
                'period_end': metadata.period_end.isoformat() if isinstance(metadata.period_end, datetime) else str(metadata.period_end),
                'generated_by': metadata.generated_by,
                'version': metadata.version
            },
            'executive_summary': executive_summary,
            'sections': [
                {
                    'title': s.title,
                    'content': s.content,
                    'summary': s.summary,
                    'charts': s.charts,
                    'tables': s.tables,
                    'recommendations': s.recommendations
                }
                for s in sections
            ],
            'key_metrics': self._extract_key_metrics(sections),
            'action_items': self._consolidate_action_items(sections),
            'alerts': self._generate_alerts(sections, project_data)
        }
        
        # Store in history
        self.report_history.append({
            'report_id': metadata.report_id,
            'report_type': report_type.value,
            'generated_at': metadata.generated_at.isoformat(),
            'project_id': metadata.project_id
        })
        
        # Format output
        if output_format == ReportFormat.HTML:
            return self._format_html(report)
        elif output_format == ReportFormat.MARKDOWN:
            return self._format_markdown(report)
        else:
            return report
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"RPT-{timestamp}-{len(self.report_history):04d}"
    
    def _generate_executive_summary(
        self,
        sections: List[ReportSection],
        project_data: Dict
    ) -> Dict:
        """Generate executive summary from all sections"""
        summaries = [s.summary for s in sections if s.summary]
        
        # Determine overall status
        overall_status = self._determine_overall_status(sections, project_data)
        
        # Key highlights
        highlights = []
        for section in sections:
            if section.priority == 1:
                highlights.append(f"{section.title}: Requires attention")
        
        return {
            'overall_status': overall_status,
            'status_indicator': self._get_status_indicator(overall_status),
            'narrative': ' '.join(summaries),
            'highlights': highlights,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _determine_overall_status(
        self,
        sections: List[ReportSection],
        project_data: Dict
    ) -> str:
        """Determine overall project status"""
        critical_count = sum(1 for s in sections if s.priority == 1)
        
        if critical_count >= 2:
            return 'critical'
        elif critical_count == 1:
            return 'warning'
        else:
            return 'good'
    
    def _get_status_indicator(self, status: str) -> str:
        """Get visual indicator for status"""
        indicators = {
            'critical': '🔴',
            'warning': '🟡',
            'good': '🟢'
        }
        return indicators.get(status, '⚪')
    
    def _extract_key_metrics(self, sections: List[ReportSection]) -> Dict:
        """Extract key metrics from all sections"""
        metrics = {}
        
        for section in sections:
            content = section.content
            
            if 'completion_percentage' in content:
                metrics['progress'] = {
                    'value': content['completion_percentage'],
                    'unit': '%',
                    'status': 'on_track' if content.get('is_on_track', True) else 'behind'
                }
            
            if 'overall_waste_score' in content:
                metrics['waste_score'] = {
                    'value': content['overall_waste_score'] * 100,
                    'unit': '%',
                    'status': content.get('health_status', 'unknown')
                }
            
            if 'budget_variance_percentage' in content:
                metrics['budget_variance'] = {
                    'value': content['budget_variance_percentage'],
                    'unit': '%',
                    'status': 'over' if content['budget_variance_percentage'] > 0 else 'under'
                }
            
            if 'compliance_score' in content:
                metrics['safety_compliance'] = {
                    'value': content['compliance_score'] * 100,
                    'unit': '%',
                    'status': 'compliant' if content.get('is_compliant', False) else 'non_compliant'
                }
        
        return metrics
    
    def _consolidate_action_items(self, sections: List[ReportSection]) -> List[Dict]:
        """Consolidate action items from all sections"""
        action_items = []
        
        for section in sections:
            for i, rec in enumerate(section.recommendations):
                action_items.append({
                    'id': f"{section.title[:3].upper()}-{i+1:02d}",
                    'category': section.title,
                    'action': rec,
                    'priority': 'high' if section.priority == 1 else 'medium',
                    'due': 'immediate' if 'URGENT' in rec else 'this_week'
                })
        
        # Sort by priority
        action_items.sort(key=lambda x: 0 if x['priority'] == 'high' else 1)
        
        return action_items[:15]  # Limit to 15 items
    
    def _generate_alerts(
        self,
        sections: List[ReportSection],
        project_data: Dict
    ) -> List[Dict]:
        """Generate alerts based on thresholds"""
        alerts = []
        
        for section in sections:
            content = section.content
            
            # Progress alerts
            if 'variance' in content and content.get('variance', 0) < -10:
                alerts.append({
                    'type': 'schedule',
                    'severity': 'high',
                    'message': f"Project is {abs(content['variance']):.1f}% behind schedule",
                    'action': 'Review recovery options'
                })
            
            # Waste alerts
            if content.get('overall_waste_score', 0) > 0.6:
                alerts.append({
                    'type': 'waste',
                    'severity': 'high',
                    'message': 'High waste levels detected',
                    'action': 'Implement waste reduction measures'
                })
            
            # Safety alerts
            if content.get('violation_count', 0) > 0:
                alerts.append({
                    'type': 'safety',
                    'severity': 'critical' if content.get('risk_level') == 'high' else 'medium',
                    'message': f"{content['violation_count']} safety violation(s) detected",
                    'action': 'Address safety issues immediately'
                })
            
            # Budget alerts
            if content.get('budget_variance_percentage', 0) > 10:
                alerts.append({
                    'type': 'cost',
                    'severity': 'high',
                    'message': f"Budget overrun: {content['budget_variance_percentage']:.1f}%",
                    'action': 'Implement cost control measures'
                })
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return alerts
    
    def _format_html(self, report: Dict) -> Dict:
        """Format report as HTML"""
        html_content = self._generate_html(report)
        report['html_content'] = html_content
        return report
    
    def _generate_html(self, report: Dict) -> str:
        """Generate HTML content"""
        metadata = report['metadata']
        exec_summary = report['executive_summary']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{metadata['project_name']} - {metadata['report_type'].title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1a365d; color: white; padding: 20px; }}
                .summary {{ background: #f7fafc; padding: 15px; margin: 20px 0; }}
                .section {{ margin: 20px 0; border: 1px solid #e2e8f0; padding: 15px; }}
                .section h2 {{ color: #2d3748; border-bottom: 2px solid #4299e1; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #edf2f7; }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .alert.critical {{ background: #fed7d7; }}
                .alert.high {{ background: #feebc8; }}
                .alert.medium {{ background: #fefcbf; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
                th {{ background: #edf2f7; }}
                .recommendation {{ padding: 8px; margin: 5px 0; background: #e6fffa; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{metadata['project_name']}</h1>
                <p>{metadata['report_type'].title()} Report - Generated: {metadata['generated_at']}</p>
            </div>
            
            <div class="summary">
                <h2>{exec_summary['status_indicator']} Executive Summary</h2>
                <p><strong>Status:</strong> {exec_summary['overall_status'].title()}</p>
                <p>{exec_summary['narrative']}</p>
            </div>
        """
        
        # Key metrics
        if report.get('key_metrics'):
            html += '<div class="metrics"><h2>Key Metrics</h2>'
            for name, metric in report['key_metrics'].items():
                html += f"""
                <div class="metric">
                    <strong>{name.replace('_', ' ').title()}</strong><br>
                    {metric['value']:.1f}{metric['unit']}
                </div>
                """
            html += '</div>'
        
        # Alerts
        if report.get('alerts'):
            html += '<div class="alerts"><h2>Alerts</h2>'
            for alert in report['alerts']:
                html += f"""
                <div class="alert {alert['severity']}">
                    <strong>{alert['type'].title()}:</strong> {alert['message']}
                    <br><em>Action: {alert['action']}</em>
                </div>
                """
            html += '</div>'
        
        # Sections
        for section in report['sections']:
            html += f"""
            <div class="section">
                <h2>{section['title']}</h2>
                <p>{section['summary']}</p>
            """
            
            # Tables
            for table in section.get('tables', []):
                html += f"<h3>{table['title']}</h3><table>"
                html += '<tr>' + ''.join(f'<th>{h}</th>' for h in table['headers']) + '</tr>'
                for row in table['rows']:
                    html += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                html += '</table>'
            
            # Recommendations
            if section.get('recommendations'):
                html += '<h3>Recommendations</h3>'
                for rec in section['recommendations']:
                    html += f'<div class="recommendation">{rec}</div>'
            
            html += '</div>'
        
        # Action items
        if report.get('action_items'):
            html += '<div class="section"><h2>Action Items</h2><table>'
            html += '<tr><th>ID</th><th>Category</th><th>Action</th><th>Priority</th><th>Due</th></tr>'
            for item in report['action_items']:
                html += f"""
                <tr>
                    <td>{item['id']}</td>
                    <td>{item['category']}</td>
                    <td>{item['action']}</td>
                    <td>{item['priority'].title()}</td>
                    <td>{item['due'].replace('_', ' ').title()}</td>
                </tr>
                """
            html += '</table></div>'
        
        html += """
            <div class="footer">
                <p><em>Generated by LeanConstruction AI - Automated Reporting System v2.0</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_markdown(self, report: Dict) -> Dict:
        """Format report as Markdown"""
        md_content = self._generate_markdown(report)
        report['markdown_content'] = md_content
        return report
    
    def _generate_markdown(self, report: Dict) -> str:
        """Generate Markdown content"""
        metadata = report['metadata']
        exec_summary = report['executive_summary']
        
        md = f"""# {metadata['project_name']}

## {metadata['report_type'].title()} Report

**Generated:** {metadata['generated_at']}  
**Period:** {metadata['period_start']} to {metadata['period_end']}

---

## {exec_summary['status_indicator']} Executive Summary

**Overall Status:** {exec_summary['overall_status'].title()}

{exec_summary['narrative']}

"""
        
        # Key metrics
        if report.get('key_metrics'):
            md += "### Key Metrics\n\n"
            md += "| Metric | Value | Status |\n|--------|-------|--------|\n"
            for name, metric in report['key_metrics'].items():
                md += f"| {name.replace('_', ' ').title()} | {metric['value']:.1f}{metric['unit']} | {metric['status']} |\n"
            md += "\n"
        
        # Alerts
        if report.get('alerts'):
            md += "### ⚠️ Alerts\n\n"
            for alert in report['alerts']:
                icon = '🔴' if alert['severity'] == 'critical' else '🟡' if alert['severity'] == 'high' else '⚪'
                md += f"- {icon} **{alert['type'].title()}:** {alert['message']}\n"
                md += f"  - *Action:* {alert['action']}\n"
            md += "\n"
        
        # Sections
        for section in report['sections']:
            md += f"---\n\n## {section['title']}\n\n"
            md += f"{section['summary']}\n\n"
            
            # Tables
            for table in section.get('tables', []):
                md += f"### {table['title']}\n\n"
                md += "| " + " | ".join(table['headers']) + " |\n"
                md += "| " + " | ".join(['---'] * len(table['headers'])) + " |\n"
                for row in table['rows']:
                    md += "| " + " | ".join(str(cell) for cell in row) + " |\n"
                md += "\n"
            
            # Recommendations
            if section.get('recommendations'):
                md += "### Recommendations\n\n"
                for i, rec in enumerate(section['recommendations'], 1):
                    md += f"{i}. {rec}\n"
                md += "\n"
        
        # Action items
        if report.get('action_items'):
            md += "---\n\n## Action Items\n\n"
            md += "| ID | Category | Action | Priority | Due |\n"
            md += "|-----|----------|--------|----------|-----|\n"
            for item in report['action_items']:
                md += f"| {item['id']} | {item['category']} | {item['action']} | {item['priority'].title()} | {item['due'].replace('_', ' ').title()} |\n"
        
        md += "\n---\n\n*Generated by LeanConstruction AI - Automated Reporting System v2.0*\n"
        
        return md
    
    def schedule_report(
        self,
        project_id: str,
        report_type: ReportType,
        schedule: str = 'daily',
        recipients: Optional[List[str]] = None
    ) -> Dict:
        """
        Schedule automated report generation
        
        Args:
            project_id: Project to generate reports for
            report_type: Type of report
            schedule: 'daily', 'weekly', 'monthly'
            recipients: Email addresses for distribution
        
        Returns:
            Schedule configuration
        """
        schedule_config = {
            'project_id': project_id,
            'report_type': report_type.value,
            'schedule': schedule,
            'recipients': recipients or [],
            'created_at': datetime.utcnow().isoformat(),
            'next_run': self._calculate_next_run(schedule),
            'active': True
        }
        
        logger.info(f"Scheduled {report_type.value} report for project {project_id}")
        
        return schedule_config
    
    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next scheduled run time"""
        now = datetime.utcnow()
        
        if schedule == 'daily':
            next_run = now + timedelta(days=1)
            next_run = next_run.replace(hour=6, minute=0, second=0)
        elif schedule == 'weekly':
            days_until_monday = (7 - now.weekday()) % 7 or 7
            next_run = now + timedelta(days=days_until_monday)
            next_run = next_run.replace(hour=6, minute=0, second=0)
        elif schedule == 'monthly':
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_run = now.replace(month=now.month + 1, day=1)
            next_run = next_run.replace(hour=6, minute=0, second=0)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.isoformat()
    
    def get_report_history(
        self,
        project_id: Optional[str] = None,
        report_type: Optional[ReportType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get report generation history"""
        history = self.report_history
        
        if project_id:
            history = [h for h in history if h['project_id'] == project_id]
        
        if report_type:
            history = [h for h in history if h['report_type'] == report_type.value]
        
        return history[-limit:]
    
    def export_report(
        self,
        report: Dict,
        filepath: str,
        format: ReportFormat = ReportFormat.JSON
    ):
        """Export report to file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == ReportFormat.JSON:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == ReportFormat.HTML:
            html_content = report.get('html_content') or self._generate_html(report)
            with open(filepath, 'w') as f:
                f.write(html_content)
        elif format == ReportFormat.MARKDOWN:
            md_content = report.get('markdown_content') or self._generate_markdown(report)
            with open(filepath, 'w') as f:
                f.write(md_content)
        
        logger.info(f"Report exported to {filepath}")


# Convenience function for quick report generation
def generate_project_report(
    project_data: Dict,
    report_type: str = 'daily',
    output_format: str = 'json'
) -> Dict:
    """
    Quick function to generate a project report
    
    Args:
        project_data: Project data dictionary
        report_type: 'daily', 'weekly', 'monthly', 'executive', 'comprehensive'
        output_format: 'json', 'html', 'markdown'
    
    Returns:
        Generated report
    """
    system = AutomatedReportingSystem()
    
    type_mapping = {
        'daily': ReportType.DAILY,
        'weekly': ReportType.WEEKLY,
        'monthly': ReportType.MONTHLY,
        'executive': ReportType.EXECUTIVE,
        'comprehensive': ReportType.COMPREHENSIVE,
        'waste': ReportType.WASTE_ANALYSIS,
        'progress': ReportType.PROGRESS,
        'safety': ReportType.SAFETY,
        'forecast': ReportType.FORECAST
    }
    
    format_mapping = {
        'json': ReportFormat.JSON,
        'html': ReportFormat.HTML,
        'markdown': ReportFormat.MARKDOWN
    }
    
    return system.generate_report(
        project_data,
        report_type=type_mapping.get(report_type, ReportType.DAILY),
        output_format=format_mapping.get(output_format, ReportFormat.JSON)
    )