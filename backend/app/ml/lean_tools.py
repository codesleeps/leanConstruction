"""
Advanced Lean Tools - Phase 3

Implements comprehensive Lean construction tools:
- Value Stream Mapping (VSM) - Process flow visualization and optimization
- 5S Analysis - Workplace organization assessment
- Kaizen Event Planning - Continuous improvement
- Kanban Board Management - Pull-based workflow
- A3 Problem Solving - Structured problem resolution
- Last Planner System (LPS) - Collaborative planning
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ============================================
# Enums and Data Classes
# ============================================

class ProcessType(Enum):
    """Types of processes in value stream"""
    VALUE_ADDING = "value_adding"
    NECESSARY_NON_VALUE = "necessary_non_value"
    NON_VALUE_ADDING = "non_value_adding"
    WAITING = "waiting"
    TRANSPORT = "transport"
    INSPECTION = "inspection"
    REWORK = "rework"


class WasteCategory(Enum):
    """Lean waste categories (DOWNTIME)"""
    DEFECTS = "defects"
    OVERPRODUCTION = "overproduction"
    WAITING = "waiting"
    NON_UTILIZED_TALENT = "non_utilized_talent"
    TRANSPORTATION = "transportation"
    INVENTORY = "inventory"
    MOTION = "motion"
    EXTRA_PROCESSING = "extra_processing"


class S5Category(Enum):
    """5S Categories"""
    SORT = "sort"               # Seiri - Remove unnecessary items
    SET_IN_ORDER = "set_in_order"  # Seiton - Organize remaining items
    SHINE = "shine"             # Seiso - Clean and inspect
    STANDARDIZE = "standardize"  # Seiketsu - Create standards
    SUSTAIN = "sustain"         # Shitsuke - Maintain standards


class KaizenType(Enum):
    """Types of Kaizen events"""
    POINT = "point"             # Small, quick improvements
    SYSTEM = "system"           # Cross-functional improvements
    LINE = "line"               # Production line improvements
    PLANE = "plane"             # Facility-wide improvements
    CUBE = "cube"               # Organization-wide improvements


class KanbanStatus(Enum):
    """Kanban card statuses"""
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass
class ProcessStep:
    """Individual step in a value stream"""
    id: str
    name: str
    process_type: ProcessType
    cycle_time: float  # seconds
    lead_time: float   # seconds
    setup_time: float  # seconds
    wait_time: float   # seconds
    defect_rate: float  # percentage
    resources_required: List[str] = field(default_factory=list)
    preceding_steps: List[str] = field(default_factory=list)
    following_steps: List[str] = field(default_factory=list)
    waste_types: List[WasteCategory] = field(default_factory=list)
    improvement_opportunities: List[str] = field(default_factory=list)


@dataclass
class ValueStreamMetrics:
    """Metrics for a value stream"""
    total_lead_time: float
    total_cycle_time: float
    total_wait_time: float
    value_added_time: float
    non_value_added_time: float
    process_efficiency: float  # VA time / Total time
    first_pass_yield: float
    takt_time: float
    bottleneck_step: Optional[str]
    wip_count: int


@dataclass
class S5Score:
    """5S Assessment Score"""
    category: S5Category
    score: float  # 0-100
    criteria_scores: Dict[str, float]
    findings: List[str]
    recommendations: List[str]


@dataclass
class KaizenEvent:
    """Kaizen improvement event"""
    id: str
    title: str
    kaizen_type: KaizenType
    target_area: str
    current_state: Dict[str, Any]
    target_state: Dict[str, Any]
    action_items: List[Dict[str, Any]]
    team_members: List[str]
    start_date: datetime
    end_date: datetime
    status: str
    expected_savings: float
    actual_savings: Optional[float] = None


@dataclass
class KanbanCard:
    """Kanban card for task management"""
    id: str
    title: str
    description: str
    status: KanbanStatus
    priority: int
    assignee: Optional[str]
    due_date: Optional[datetime]
    cycle_time_start: Optional[datetime]
    cycle_time_end: Optional[datetime]
    blocked_reason: Optional[str] = None
    tags: List[str] = field(default_factory=list)


# ============================================
# Value Stream Mapping (VSM)
# ============================================

class ValueStreamMapper:
    """
    Value Stream Mapping tool for construction processes
    
    Analyzes workflow to identify waste and improvement opportunities
    """
    
    def __init__(self):
        self.process_steps: Dict[str, ProcessStep] = {}
        self.current_state_map: Optional[Dict] = None
        self.future_state_map: Optional[Dict] = None
        self.customer_demand_rate: float = 0.0  # units per time period
        
    def add_process_step(self, step: ProcessStep):
        """Add a process step to the value stream"""
        self.process_steps[step.id] = step
        
    def create_from_data(self, process_data: List[Dict]) -> None:
        """Create value stream from process data"""
        for data in process_data:
            step = ProcessStep(
                id=data.get('id', f"step_{len(self.process_steps)}"),
                name=data['name'],
                process_type=ProcessType(data.get('type', 'value_adding')),
                cycle_time=data.get('cycle_time', 0),
                lead_time=data.get('lead_time', 0),
                setup_time=data.get('setup_time', 0),
                wait_time=data.get('wait_time', 0),
                defect_rate=data.get('defect_rate', 0),
                resources_required=data.get('resources', []),
                preceding_steps=data.get('preceding', []),
                following_steps=data.get('following', [])
            )
            self.add_process_step(step)
    
    def analyze_current_state(self) -> ValueStreamMetrics:
        """Analyze current state of the value stream"""
        if not self.process_steps:
            raise ValueError("No process steps defined")
        
        # Calculate times
        total_cycle_time = sum(s.cycle_time for s in self.process_steps.values())
        total_wait_time = sum(s.wait_time for s in self.process_steps.values())
        total_setup_time = sum(s.setup_time for s in self.process_steps.values())
        
        # Calculate lead time (considering parallel processes)
        total_lead_time = self._calculate_critical_path_time()
        
        # Value-added time
        value_added_time = sum(
            s.cycle_time for s in self.process_steps.values()
            if s.process_type == ProcessType.VALUE_ADDING
        )
        
        # Non-value-added time
        non_value_time = total_lead_time - value_added_time
        
        # Process efficiency
        efficiency = value_added_time / total_lead_time if total_lead_time > 0 else 0
        
        # First pass yield
        fpy = 1.0
        for step in self.process_steps.values():
            fpy *= (1 - step.defect_rate / 100)
        
        # Takt time (available time / customer demand)
        takt_time = 0
        if self.customer_demand_rate > 0:
            available_time = 8 * 3600  # 8 hours in seconds
            takt_time = available_time / self.customer_demand_rate
        
        # Find bottleneck
        bottleneck = max(
            self.process_steps.values(),
            key=lambda x: x.cycle_time,
            default=None
        )
        
        # WIP count
        wip = sum(1 for s in self.process_steps.values() 
                  if s.process_type != ProcessType.WAITING)
        
        metrics = ValueStreamMetrics(
            total_lead_time=total_lead_time,
            total_cycle_time=total_cycle_time,
            total_wait_time=total_wait_time,
            value_added_time=value_added_time,
            non_value_added_time=non_value_time,
            process_efficiency=efficiency,
            first_pass_yield=fpy,
            takt_time=takt_time,
            bottleneck_step=bottleneck.id if bottleneck else None,
            wip_count=wip
        )
        
        self.current_state_map = {
            'metrics': asdict(metrics),
            'steps': {k: asdict(v) for k, v in self.process_steps.items()},
            'waste_identified': self._identify_waste()
        }
        
        return metrics
    
    def _calculate_critical_path_time(self) -> float:
        """Calculate critical path duration"""
        # Build dependency graph
        visited = set()
        longest_path = 0
        
        def dfs(step_id: str, current_time: float) -> float:
            if step_id in visited:
                return current_time
            visited.add(step_id)
            
            step = self.process_steps.get(step_id)
            if not step:
                return current_time
            
            step_time = step.cycle_time + step.wait_time + step.setup_time
            current_time += step_time
            
            if not step.following_steps:
                return current_time
            
            max_following = 0
            for next_id in step.following_steps:
                max_following = max(max_following, dfs(next_id, current_time))
            
            return max_following
        
        # Find starting steps (no predecessors)
        start_steps = [
            s.id for s in self.process_steps.values()
            if not s.preceding_steps
        ]
        
        for start in start_steps:
            visited.clear()
            path_time = dfs(start, 0)
            longest_path = max(longest_path, path_time)
        
        return longest_path if longest_path > 0 else sum(
            s.cycle_time + s.wait_time for s in self.process_steps.values()
        )
    
    def _identify_waste(self) -> List[Dict]:
        """Identify waste in the value stream"""
        wastes = []
        
        for step in self.process_steps.values():
            # High wait time
            if step.wait_time > step.cycle_time * 2:
                wastes.append({
                    'step': step.id,
                    'type': WasteCategory.WAITING.value,
                    'severity': 'high' if step.wait_time > step.cycle_time * 5 else 'medium',
                    'description': f"Wait time ({step.wait_time:.0f}s) exceeds cycle time significantly",
                    'recommendation': "Analyze root cause of delays and implement flow improvements"
                })
            
            # High defect rate
            if step.defect_rate > 5:
                wastes.append({
                    'step': step.id,
                    'type': WasteCategory.DEFECTS.value,
                    'severity': 'high' if step.defect_rate > 15 else 'medium',
                    'description': f"Defect rate of {step.defect_rate:.1f}% requires attention",
                    'recommendation': "Implement poka-yoke (mistake-proofing) and quality checks"
                })
            
            # Non-value-adding process
            if step.process_type in [ProcessType.NON_VALUE_ADDING, ProcessType.REWORK]:
                wastes.append({
                    'step': step.id,
                    'type': WasteCategory.EXTRA_PROCESSING.value,
                    'severity': 'medium',
                    'description': f"Process '{step.name}' is non-value-adding",
                    'recommendation': "Evaluate if process can be eliminated or reduced"
                })
            
            # Transport processes
            if step.process_type == ProcessType.TRANSPORT:
                wastes.append({
                    'step': step.id,
                    'type': WasteCategory.TRANSPORTATION.value,
                    'severity': 'low',
                    'description': f"Transportation step identified",
                    'recommendation': "Optimize layout to minimize transport distances"
                })
        
        return wastes
    
    def generate_future_state(self) -> Dict:
        """Generate recommended future state map"""
        if not self.current_state_map:
            self.analyze_current_state()
        
        improvements = []
        estimated_savings = {
            'time_reduction': 0,
            'defect_reduction': 0,
            'efficiency_gain': 0
        }
        
        # Analyze each step for improvements
        for step_id, step in self.process_steps.items():
            step_improvements = []
            
            # Reduce wait times
            if step.wait_time > 0:
                potential_reduction = step.wait_time * 0.5
                step_improvements.append({
                    'action': 'Implement pull system',
                    'target': 'wait_time',
                    'current': step.wait_time,
                    'target_value': step.wait_time - potential_reduction,
                    'savings': potential_reduction
                })
                estimated_savings['time_reduction'] += potential_reduction
            
            # Reduce defects
            if step.defect_rate > 2:
                target_defect_rate = max(step.defect_rate * 0.5, 1)
                step_improvements.append({
                    'action': 'Implement quality at source',
                    'target': 'defect_rate',
                    'current': step.defect_rate,
                    'target_value': target_defect_rate,
                    'savings': step.defect_rate - target_defect_rate
                })
                estimated_savings['defect_reduction'] += step.defect_rate - target_defect_rate
            
            # Reduce setup time (SMED)
            if step.setup_time > step.cycle_time:
                target_setup = step.setup_time * 0.25
                step_improvements.append({
                    'action': 'Apply SMED principles',
                    'target': 'setup_time',
                    'current': step.setup_time,
                    'target_value': target_setup,
                    'savings': step.setup_time - target_setup
                })
                estimated_savings['time_reduction'] += step.setup_time - target_setup
            
            if step_improvements:
                improvements.append({
                    'step_id': step_id,
                    'step_name': step.name,
                    'improvements': step_improvements
                })
        
        # Calculate future state metrics
        current_efficiency = self.current_state_map['metrics']['process_efficiency']
        estimated_savings['efficiency_gain'] = min(current_efficiency * 1.3, 0.95) - current_efficiency
        
        self.future_state_map = {
            'improvements': improvements,
            'estimated_savings': estimated_savings,
            'target_metrics': {
                'lead_time_reduction': f"{estimated_savings['time_reduction'] / 3600:.1f} hours",
                'defect_rate_improvement': f"{estimated_savings['defect_reduction']:.1f}%",
                'efficiency_target': f"{(current_efficiency + estimated_savings['efficiency_gain']) * 100:.1f}%"
            },
            'implementation_phases': self._create_implementation_plan(improvements)
        }
        
        return self.future_state_map
    
    def _create_implementation_plan(self, improvements: List[Dict]) -> List[Dict]:
        """Create phased implementation plan"""
        phases = []
        
        # Phase 1: Quick wins (low effort, high impact)
        phase1_items = []
        for imp in improvements:
            for action in imp['improvements']:
                if action['target'] == 'wait_time':
                    phase1_items.append({
                        'step': imp['step_name'],
                        'action': action['action'],
                        'expected_savings': action['savings']
                    })
        
        if phase1_items:
            phases.append({
                'phase': 1,
                'name': 'Quick Wins',
                'duration': '2-4 weeks',
                'items': phase1_items[:5],
                'description': 'Low-effort improvements with immediate impact'
            })
        
        # Phase 2: Quality improvements
        phase2_items = []
        for imp in improvements:
            for action in imp['improvements']:
                if action['target'] == 'defect_rate':
                    phase2_items.append({
                        'step': imp['step_name'],
                        'action': action['action'],
                        'expected_savings': action['savings']
                    })
        
        if phase2_items:
            phases.append({
                'phase': 2,
                'name': 'Quality Focus',
                'duration': '4-8 weeks',
                'items': phase2_items[:5],
                'description': 'Quality improvements and defect reduction'
            })
        
        # Phase 3: Process optimization
        phase3_items = []
        for imp in improvements:
            for action in imp['improvements']:
                if action['target'] == 'setup_time':
                    phase3_items.append({
                        'step': imp['step_name'],
                        'action': action['action'],
                        'expected_savings': action['savings']
                    })
        
        if phase3_items:
            phases.append({
                'phase': 3,
                'name': 'Process Optimization',
                'duration': '8-12 weeks',
                'items': phase3_items[:5],
                'description': 'Setup time reduction and flow optimization'
            })
        
        return phases
    
    def export_vsm(self) -> Dict:
        """Export complete VSM analysis"""
        if not self.current_state_map:
            self.analyze_current_state()
        if not self.future_state_map:
            self.generate_future_state()
        
        return {
            'current_state': self.current_state_map,
            'future_state': self.future_state_map,
            'generated_at': datetime.utcnow().isoformat()
        }


# ============================================
# 5S Analysis System
# ============================================

class S5AnalysisSystem:
    """
    5S Workplace Organization Analysis System
    
    Provides comprehensive assessment and improvement tracking
    for Sort, Set in Order, Shine, Standardize, Sustain
    """
    
    def __init__(self):
        self.assessment_history: List[Dict] = []
        self.criteria = self._initialize_criteria()
        
    def _initialize_criteria(self) -> Dict[S5Category, List[Dict]]:
        """Initialize assessment criteria for each S"""
        return {
            S5Category.SORT: [
                {'id': 'unnecessary_items', 'name': 'Unnecessary Items Removed', 'weight': 0.25},
                {'id': 'red_tag_system', 'name': 'Red Tag System in Place', 'weight': 0.20},
                {'id': 'clear_boundaries', 'name': 'Clear Work Area Boundaries', 'weight': 0.20},
                {'id': 'tool_audit', 'name': 'Regular Tool/Equipment Audit', 'weight': 0.20},
                {'id': 'disposal_process', 'name': 'Disposal Process Defined', 'weight': 0.15}
            ],
            S5Category.SET_IN_ORDER: [
                {'id': 'designated_locations', 'name': 'Designated Storage Locations', 'weight': 0.25},
                {'id': 'visual_controls', 'name': 'Visual Controls Implemented', 'weight': 0.20},
                {'id': 'labeling', 'name': 'Proper Labeling System', 'weight': 0.20},
                {'id': 'ergonomic_placement', 'name': 'Ergonomic Tool Placement', 'weight': 0.20},
                {'id': 'shadow_boards', 'name': 'Shadow Boards/Outlines', 'weight': 0.15}
            ],
            S5Category.SHINE: [
                {'id': 'cleaning_schedule', 'name': 'Regular Cleaning Schedule', 'weight': 0.25},
                {'id': 'inspection_routine', 'name': 'Inspection Routine Established', 'weight': 0.20},
                {'id': 'cleaning_supplies', 'name': 'Cleaning Supplies Available', 'weight': 0.15},
                {'id': 'equipment_maintenance', 'name': 'Equipment Maintenance', 'weight': 0.25},
                {'id': 'waste_disposal', 'name': 'Proper Waste Disposal', 'weight': 0.15}
            ],
            S5Category.STANDARDIZE: [
                {'id': 'documented_procedures', 'name': 'Documented Procedures', 'weight': 0.25},
                {'id': 'visual_standards', 'name': 'Visual Standards Posted', 'weight': 0.20},
                {'id': 'checklists', 'name': 'Standardized Checklists', 'weight': 0.20},
                {'id': 'color_coding', 'name': 'Consistent Color Coding', 'weight': 0.15},
                {'id': 'training_materials', 'name': 'Training Materials Available', 'weight': 0.20}
            ],
            S5Category.SUSTAIN: [
                {'id': 'audit_schedule', 'name': 'Regular Audit Schedule', 'weight': 0.25},
                {'id': 'improvement_tracking', 'name': 'Improvement Tracking', 'weight': 0.20},
                {'id': 'management_involvement', 'name': 'Management Involvement', 'weight': 0.20},
                {'id': 'recognition_program', 'name': 'Recognition Program', 'weight': 0.15},
                {'id': 'continuous_training', 'name': 'Continuous Training', 'weight': 0.20}
            ]
        }
    
    def conduct_assessment(
        self,
        area_id: str,
        area_name: str,
        scores: Dict[str, float],
        assessor: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct a 5S assessment for a work area
        
        Args:
            area_id: Unique identifier for the area
            area_name: Name of the area being assessed
            scores: Dictionary of criterion_id -> score (0-100)
            assessor: Name of person conducting assessment
            notes: Additional notes
        
        Returns:
            Complete assessment results
        """
        category_scores = {}
        overall_findings = []
        overall_recommendations = []
        
        for category in S5Category:
            criteria_list = self.criteria[category]
            category_score = 0
            criteria_scores = {}
            findings = []
            recommendations = []
            
            for criterion in criteria_list:
                criterion_id = criterion['id']
                score = scores.get(criterion_id, 50)  # Default to 50 if not provided
                criteria_scores[criterion_id] = score
                
                weighted_score = score * criterion['weight']
                category_score += weighted_score
                
                # Generate findings and recommendations
                if score < 60:
                    findings.append(f"Low score in {criterion['name']} ({score}%)")
                    recommendations.append(
                        f"Improvement needed: {criterion['name']} - Create action plan"
                    )
                elif score < 80:
                    findings.append(f"Moderate score in {criterion['name']} ({score}%)")
                    recommendations.append(
                        f"Minor improvement: {criterion['name']} - Monitor and enhance"
                    )
            
            s5_score = S5Score(
                category=category,
                score=category_score,
                criteria_scores=criteria_scores,
                findings=findings,
                recommendations=recommendations
            )
            
            category_scores[category.value] = asdict(s5_score)
            overall_findings.extend(findings)
            overall_recommendations.extend(recommendations)
        
        # Calculate overall score
        overall_score = sum(
            category_scores[cat]['score'] for cat in category_scores
        ) / 5
        
        # Determine grade
        grade = self._calculate_grade(overall_score)
        
        # Certification eligibility
        certification = self._check_certification(category_scores, overall_score)
        
        assessment = {
            'assessment_id': f"5S-{area_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            'area_id': area_id,
            'area_name': area_name,
            'assessed_at': datetime.utcnow().isoformat(),
            'assessor': assessor,
            'overall_score': overall_score,
            'grade': grade,
            'category_scores': category_scores,
            'findings': overall_findings,
            'recommendations': overall_recommendations[:10],  # Top 10
            'certification': certification,
            'notes': notes,
            'trend': self._calculate_trend(area_id)
        }
        
        self.assessment_history.append(assessment)
        
        return assessment
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _check_certification(
        self,
        category_scores: Dict,
        overall_score: float
    ) -> Dict:
        """Check certification eligibility"""
        # All categories must meet minimum for certification
        min_category_score = min(
            category_scores[cat]['score'] for cat in category_scores
        )
        
        if overall_score >= 90 and min_category_score >= 85:
            return {
                'level': 'gold',
                'eligible': True,
                'valid_until': (datetime.utcnow() + timedelta(days=180)).isoformat()
            }
        elif overall_score >= 80 and min_category_score >= 70:
            return {
                'level': 'silver',
                'eligible': True,
                'valid_until': (datetime.utcnow() + timedelta(days=90)).isoformat()
            }
        elif overall_score >= 70 and min_category_score >= 60:
            return {
                'level': 'bronze',
                'eligible': True,
                'valid_until': (datetime.utcnow() + timedelta(days=60)).isoformat()
            }
        else:
            return {
                'level': 'none',
                'eligible': False,
                'reason': 'Minimum scores not met',
                'requirement': 'Minimum 70% overall and 60% per category for Bronze'
            }
    
    def _calculate_trend(self, area_id: str) -> Dict:
        """Calculate score trend for an area"""
        area_history = [
            a for a in self.assessment_history
            if a['area_id'] == area_id
        ]
        
        if len(area_history) < 2:
            return {'direction': 'new', 'change': 0}
        
        # Compare last two assessments
        current = area_history[-1]['overall_score']
        previous = area_history[-2]['overall_score']
        change = current - previous
        
        if change > 5:
            direction = 'improving'
        elif change < -5:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change': change,
            'assessments_count': len(area_history)
        }
    
    def get_improvement_plan(self, assessment_id: str) -> Dict:
        """Generate detailed improvement plan from assessment"""
        assessment = next(
            (a for a in self.assessment_history if a['assessment_id'] == assessment_id),
            None
        )
        
        if not assessment:
            return {'error': 'Assessment not found'}
        
        improvement_items = []
        priority_order = []
        
        # Identify lowest scoring areas
        for category, data in assessment['category_scores'].items():
            if data['score'] < 80:
                priority = 'high' if data['score'] < 60 else 'medium'
                
                for criterion_id, score in data['criteria_scores'].items():
                    if score < 70:
                        improvement_items.append({
                            'category': category,
                            'criterion': criterion_id,
                            'current_score': score,
                            'target_score': min(score + 20, 100),
                            'priority': priority,
                            'suggested_actions': self._get_suggested_actions(category, criterion_id)
                        })
        
        # Sort by priority and score
        improvement_items.sort(
            key=lambda x: (0 if x['priority'] == 'high' else 1, x['current_score'])
        )
        
        return {
            'assessment_id': assessment_id,
            'area': assessment['area_name'],
            'current_score': assessment['overall_score'],
            'target_score': min(assessment['overall_score'] + 15, 100),
            'improvement_items': improvement_items[:10],
            'estimated_timeline': self._estimate_timeline(improvement_items),
            'resources_needed': self._estimate_resources(improvement_items)
        }
    
    def _get_suggested_actions(self, category: str, criterion_id: str) -> List[str]:
        """Get suggested improvement actions for a criterion"""
        actions = {
            'unnecessary_items': [
                'Conduct systematic inventory of all items',
                'Apply red-tag system for questionable items',
                'Set up staging area for items to be removed'
            ],
            'designated_locations': [
                'Create floor markings for equipment positions',
                'Install shadow boards for tools',
                'Label all storage areas clearly'
            ],
            'cleaning_schedule': [
                'Develop daily 5-minute cleanup routine',
                'Assign cleaning responsibilities',
                'Create visual cleaning checklist'
            ],
            'documented_procedures': [
                'Create standard work instructions',
                'Post visual work standards',
                'Train team on standardized procedures'
            ],
            'audit_schedule': [
                'Establish weekly mini-audits',
                'Create self-assessment checklists',
                'Schedule monthly manager audits'
            ]
        }
        
        return actions.get(criterion_id, [
            'Review current practices',
            'Identify improvement opportunities',
            'Implement and monitor changes'
        ])
    
    def _estimate_timeline(self, items: List[Dict]) -> str:
        """Estimate improvement timeline"""
        high_priority = sum(1 for i in items if i['priority'] == 'high')
        
        if high_priority > 5:
            return '8-12 weeks'
        elif high_priority > 2:
            return '4-8 weeks'
        else:
            return '2-4 weeks'
    
    def _estimate_resources(self, items: List[Dict]) -> Dict:
        """Estimate resources needed for improvements"""
        return {
            'labor_hours': len(items) * 4,  # 4 hours per item
            'training_hours': len(items) * 1,
            'materials_budget': len(items) * 200,  # $200 per item
            'management_time': len(items) * 0.5
        }


# ============================================
# Kaizen Event Management
# ============================================

class KaizenManager:
    """
    Kaizen continuous improvement event management
    
    Facilitates planning and tracking of improvement events
    """
    
    def __init__(self):
        self.events: Dict[str, KaizenEvent] = {}
        self.improvement_log: List[Dict] = []
        
    def create_event(
        self,
        title: str,
        kaizen_type: KaizenType,
        target_area: str,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        team_members: List[str],
        duration_days: int = 5
    ) -> KaizenEvent:
        """Create a new Kaizen event"""
        event_id = f"KZN-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.events):03d}"
        
        event = KaizenEvent(
            id=event_id,
            title=title,
            kaizen_type=kaizen_type,
            target_area=target_area,
            current_state=current_state,
            target_state=target_state,
            action_items=[],
            team_members=team_members,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration_days),
            status='planning',
            expected_savings=self._estimate_savings(current_state, target_state)
        )
        
        self.events[event_id] = event
        return event
    
    def _estimate_savings(self, current: Dict, target: Dict) -> float:
        """Estimate savings from improvement"""
        savings = 0
        
        # Time savings
        if 'cycle_time' in current and 'cycle_time' in target:
            time_saved = current['cycle_time'] - target['cycle_time']
            savings += time_saved * 50  # $50/hour saved
        
        # Defect reduction savings
        if 'defect_rate' in current and 'defect_rate' in target:
            defect_reduction = current['defect_rate'] - target['defect_rate']
            savings += defect_reduction * 1000  # $1000 per % defect reduction
        
        # Inventory reduction
        if 'inventory_days' in current and 'inventory_days' in target:
            inv_reduction = current['inventory_days'] - target['inventory_days']
            savings += inv_reduction * 500  # $500 per day reduction
        
        return savings
    
    def add_action_item(
        self,
        event_id: str,
        description: str,
        assignee: str,
        due_date: datetime
    ) -> Dict:
        """Add action item to Kaizen event"""
        if event_id not in self.events:
            return {'error': 'Event not found'}
        
        event = self.events[event_id]
        action = {
            'id': f"{event_id}-A{len(event.action_items):02d}",
            'description': description,
            'assignee': assignee,
            'due_date': due_date.isoformat(),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        event.action_items.append(action)
        return action
    
    def update_event_status(self, event_id: str, status: str, actual_savings: Optional[float] = None):
        """Update Kaizen event status"""
        if event_id not in self.events:
            return {'error': 'Event not found'}
        
        event = self.events[event_id]
        event.status = status
        
        if actual_savings is not None:
            event.actual_savings = actual_savings
        
        # Log completion
        if status == 'completed':
            self.improvement_log.append({
                'event_id': event_id,
                'title': event.title,
                'completed_at': datetime.utcnow().isoformat(),
                'expected_savings': event.expected_savings,
                'actual_savings': event.actual_savings,
                'team_size': len(event.team_members)
            })
        
        return asdict(event)
    
    def get_event_dashboard(self) -> Dict:
        """Get Kaizen event dashboard summary"""
        active_events = [e for e in self.events.values() if e.status not in ['completed', 'cancelled']]
        completed_events = [e for e in self.events.values() if e.status == 'completed']
        
        total_expected = sum(e.expected_savings for e in self.events.values())
        total_actual = sum(e.actual_savings or 0 for e in completed_events)
        
        return {
            'summary': {
                'total_events': len(self.events),
                'active_events': len(active_events),
                'completed_events': len(completed_events),
                'total_expected_savings': total_expected,
                'total_actual_savings': total_actual,
                'savings_realization': total_actual / total_expected if total_expected > 0 else 0
            },
            'active': [
                {
                    'id': e.id,
                    'title': e.title,
                    'type': e.kaizen_type.value,
                    'status': e.status,
                    'end_date': e.end_date.isoformat(),
                    'pending_actions': sum(1 for a in e.action_items if a['status'] == 'pending')
                }
                for e in active_events
            ],
            'recent_completions': [
                asdict(e) for e in completed_events[-5:]
            ]
        }


# ============================================
# Kanban Board System
# ============================================

class KanbanBoard:
    """
    Kanban board for construction task management
    
    Implements pull-based workflow with WIP limits
    """
    
    def __init__(
        self,
        board_id: str,
        name: str,
        wip_limits: Optional[Dict[str, int]] = None
    ):
        self.board_id = board_id
        self.name = name
        self.cards: Dict[str, KanbanCard] = {}
        self.wip_limits = wip_limits or {
            KanbanStatus.IN_PROGRESS.value: 5,
            KanbanStatus.REVIEW.value: 3
        }
        self.history: List[Dict] = []
        
    def create_card(
        self,
        title: str,
        description: str,
        priority: int = 3,
        assignee: Optional[str] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> KanbanCard:
        """Create a new Kanban card"""
        card_id = f"{self.board_id}-{len(self.cards):04d}"
        
        card = KanbanCard(
            id=card_id,
            title=title,
            description=description,
            status=KanbanStatus.BACKLOG,
            priority=priority,
            assignee=assignee,
            due_date=due_date,
            cycle_time_start=None,
            cycle_time_end=None,
            tags=tags or []
        )
        
        self.cards[card_id] = card
        self._log_action(card_id, 'created', None, KanbanStatus.BACKLOG.value)
        
        return card
    
    def move_card(self, card_id: str, new_status: KanbanStatus) -> Dict:
        """Move card to new status column"""
        if card_id not in self.cards:
            return {'error': 'Card not found'}
        
        card = self.cards[card_id]
        old_status = card.status
        
        # Check WIP limit
        if new_status.value in self.wip_limits:
            current_count = sum(
                1 for c in self.cards.values()
                if c.status == new_status
            )
            if current_count >= self.wip_limits[new_status.value]:
                return {
                    'error': 'WIP limit reached',
                    'limit': self.wip_limits[new_status.value],
                    'current': current_count
                }
        
        # Track cycle time
        if new_status == KanbanStatus.IN_PROGRESS and card.cycle_time_start is None:
            card.cycle_time_start = datetime.utcnow()
        elif new_status == KanbanStatus.DONE and card.cycle_time_end is None:
            card.cycle_time_end = datetime.utcnow()
        
        # Clear blocked reason if moving from blocked
        if old_status == KanbanStatus.BLOCKED:
            card.blocked_reason = None
        
        card.status = new_status
        self._log_action(card_id, 'moved', old_status.value, new_status.value)
        
        return {
            'card_id': card_id,
            'old_status': old_status.value,
            'new_status': new_status.value,
            'cycle_time': self._calculate_cycle_time(card)
        }
    
    def block_card(self, card_id: str, reason: str) -> Dict:
        """Mark card as blocked"""
        if card_id not in self.cards:
            return {'error': 'Card not found'}
        
        card = self.cards[card_id]
        old_status = card.status
        card.status = KanbanStatus.BLOCKED
        card.blocked_reason = reason
        
        self._log_action(card_id, 'blocked', old_status.value, 'blocked', reason)
        
        return {'card_id': card_id, 'blocked_reason': reason}
    
    def _calculate_cycle_time(self, card: KanbanCard) -> Optional[float]:
        """Calculate cycle time in hours"""
        if card.cycle_time_start and card.cycle_time_end:
            delta = card.cycle_time_end - card.cycle_time_start
            return delta.total_seconds() / 3600
        elif card.cycle_time_start:
            delta = datetime.utcnow() - card.cycle_time_start
            return delta.total_seconds() / 3600
        return None
    
    def _log_action(
        self,
        card_id: str,
        action: str,
        from_status: Optional[str],
        to_status: Optional[str],
        details: Optional[str] = None
    ):
        """Log board action"""
        self.history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'card_id': card_id,
            'action': action,
            'from_status': from_status,
            'to_status': to_status,
            'details': details
        })
    
    def get_board_state(self) -> Dict:
        """Get current board state"""
        columns = {status.value: [] for status in KanbanStatus}
        
        for card in self.cards.values():
            card_data = asdict(card)
            card_data['cycle_time_hours'] = self._calculate_cycle_time(card)
            columns[card.status.value].append(card_data)
        
        # Sort by priority
        for status in columns:
            columns[status].sort(key=lambda x: x['priority'])
        
        return {
            'board_id': self.board_id,
            'name': self.name,
            'columns': columns,
            'wip_limits': self.wip_limits,
            'metrics': self._calculate_metrics()
        }
    
    def _calculate_metrics(self) -> Dict:
        """Calculate board metrics"""
        completed = [c for c in self.cards.values() if c.status == KanbanStatus.DONE]
        in_progress = [c for c in self.cards.values() if c.status == KanbanStatus.IN_PROGRESS]
        blocked = [c for c in self.cards.values() if c.status == KanbanStatus.BLOCKED]
        
        cycle_times = [
            self._calculate_cycle_time(c)
            for c in completed
            if self._calculate_cycle_time(c) is not None
        ]
        
        return {
            'total_cards': len(self.cards),
            'completed': len(completed),
            'in_progress': len(in_progress),
            'blocked': len(blocked),
            'average_cycle_time': np.mean(cycle_times) if cycle_times else 0,
            'throughput_per_week': len([
                c for c in completed
                if c.cycle_time_end and 
                (datetime.utcnow() - c.cycle_time_end).days < 7
            ])
        }
    
    def get_flow_diagram(self) -> Dict:
        """Generate cumulative flow diagram data"""
        dates = {}
        
        for action in self.history:
            date = action['timestamp'][:10]
            if date not in dates:
                dates[date] = {status.value: 0 for status in KanbanStatus}
        
        # Accumulate counts
        cumulative = {status.value: 0 for status in KanbanStatus}
        flow_data = []
        
        for date in sorted(dates.keys()):
            day_actions = [a for a in self.history if a['timestamp'][:10] == date]
            
            for action in day_actions:
                if action['from_status']:
                    cumulative[action['from_status']] = max(0, cumulative[action['from_status']] - 1)
                if action['to_status']:
                    cumulative[action['to_status']] += 1
            
            flow_data.append({
                'date': date,
                **cumulative
            })
        
        return {
            'flow_data': flow_data,
            'statuses': [s.value for s in KanbanStatus]
        }


# ============================================
# A3 Problem Solving
# ============================================

class A3ProblemSolver:
    """
    A3 Problem Solving methodology implementation
    
    Structured approach to problem identification and resolution
    """
    
    def __init__(self):
        self.a3_reports: Dict[str, Dict] = {}
        
    def create_a3(
        self,
        title: str,
        owner: str,
        background: str
    ) -> str:
        """Create new A3 report"""
        a3_id = f"A3-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.a3_reports):03d}"
        
        self.a3_reports[a3_id] = {
            'id': a3_id,
            'title': title,
            'owner': owner,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'draft',
            'sections': {
                'background': background,
                'current_condition': None,
                'target_condition': None,
                'root_cause_analysis': None,
                'countermeasures': [],
                'implementation_plan': [],
                'follow_up': []
            }
        }
        
        return a3_id
    
    def update_section(self, a3_id: str, section: str, content: Any) -> Dict:
        """Update A3 section"""
        if a3_id not in self.a3_reports:
            return {'error': 'A3 not found'}
        
        if section not in self.a3_reports[a3_id]['sections']:
            return {'error': 'Invalid section'}
        
        self.a3_reports[a3_id]['sections'][section] = content
        self.a3_reports[a3_id]['updated_at'] = datetime.utcnow().isoformat()
        
        return self.a3_reports[a3_id]
    
    def add_root_cause(self, a3_id: str, cause: str, category: str, evidence: str) -> Dict:
        """Add root cause to 5-why analysis"""
        if a3_id not in self.a3_reports:
            return {'error': 'A3 not found'}
        
        report = self.a3_reports[a3_id]
        
        if report['sections']['root_cause_analysis'] is None:
            report['sections']['root_cause_analysis'] = {
                'method': '5-why',
                'causes': []
            }
        
        report['sections']['root_cause_analysis']['causes'].append({
            'cause': cause,
            'category': category,
            'evidence': evidence,
            'added_at': datetime.utcnow().isoformat()
        })
        
        return report
    
    def add_countermeasure(
        self,
        a3_id: str,
        description: str,
        responsible: str,
        target_date: datetime,
        expected_impact: str
    ) -> Dict:
        """Add countermeasure"""
        if a3_id not in self.a3_reports:
            return {'error': 'A3 not found'}
        
        report = self.a3_reports[a3_id]
        
        countermeasure = {
            'id': f"CM-{len(report['sections']['countermeasures']):02d}",
            'description': description,
            'responsible': responsible,
            'target_date': target_date.isoformat(),
            'expected_impact': expected_impact,
            'status': 'planned',
            'actual_result': None
        }
        
        report['sections']['countermeasures'].append(countermeasure)
        
        return report
    
    def generate_a3_report(self, a3_id: str) -> Dict:
        """Generate complete A3 report"""
        if a3_id not in self.a3_reports:
            return {'error': 'A3 not found'}
        
        report = self.a3_reports[a3_id]
        
        # Calculate completion percentage
        sections = report['sections']
        filled_sections = sum(1 for s in sections.values() if s is not None)
        completion = filled_sections / len(sections) * 100
        
        return {
            **report,
            'completion_percentage': completion,
            'ready_for_review': completion >= 80
        }


# ============================================
# Integration Export
# ============================================

class LeanToolsIntegration:
    """
    Integration point for all Lean tools
    """
    
    def __init__(self):
        self.vsm = ValueStreamMapper()
        self.s5_system = S5AnalysisSystem()
        self.kaizen_manager = KaizenManager()
        self.kanban_boards: Dict[str, KanbanBoard] = {}
        self.a3_solver = A3ProblemSolver()
        
    def create_kanban_board(
        self,
        board_id: str,
        name: str,
        wip_limits: Optional[Dict[str, int]] = None
    ) -> KanbanBoard:
        """Create a new Kanban board"""
        board = KanbanBoard(board_id, name, wip_limits)
        self.kanban_boards[board_id] = board
        return board
    
    def get_lean_metrics_summary(self) -> Dict:
        """Get summary of all Lean metrics"""
        return {
            'vsm': {
                'current_state_analyzed': self.vsm.current_state_map is not None,
                'future_state_planned': self.vsm.future_state_map is not None
            },
            's5': {
                'assessments_conducted': len(self.s5_system.assessment_history),
                'average_score': np.mean([
                    a['overall_score'] 
                    for a in self.s5_system.assessment_history
                ]) if self.s5_system.assessment_history else 0
            },
            'kaizen': self.kaizen_manager.get_event_dashboard()['summary'],
            'kanban': {
                'active_boards': len(self.kanban_boards),
                'total_cards': sum(
                    len(b.cards) for b in self.kanban_boards.values()
                )
            },
            'a3': {
                'active_reports': len(self.a3_solver.a3_reports),
                'completed': len([
                    r for r in self.a3_solver.a3_reports.values()
                    if r['status'] == 'completed'
                ])
            }
        }


# Convenience instance
lean_tools = LeanToolsIntegration()