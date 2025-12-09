"""
Waste Detection Algorithms for the 8 Wastes (DOWNTIME) - Phase 2 Enhanced
Machine Learning-based detection with pattern recognition and predictive analytics

D - Defects
O - Overproduction
W - Waiting
N - Non-utilized Talent
T - Transportation
I - Inventory
M - Motion
E - Extra Processing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from sklearn.ensemble import (
    RandomForestClassifier, 
    IsolationForest,
    GradientBoostingClassifier
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import logging
import json

logger = logging.getLogger(__name__)


class WasteType(Enum):
    """Enumeration of the 8 wastes (DOWNTIME)"""
    DEFECTS = "defects"
    OVERPRODUCTION = "overproduction"
    WAITING = "waiting"
    NON_UTILIZED_TALENT = "non_utilized_talent"
    TRANSPORTATION = "transportation"
    INVENTORY = "inventory"
    MOTION = "motion"
    EXTRA_PROCESSING = "extra_processing"


class SeverityLevel(Enum):
    """Severity levels for detected waste"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class WasteIndicator:
    """Individual waste indicator measurement"""
    name: str
    value: float
    threshold: float
    weight: float
    is_exceeded: bool = field(init=False)
    
    def __post_init__(self):
        self.is_exceeded = self.value > self.threshold


@dataclass
class WasteDetectionResult:
    """Result of waste detection analysis"""
    waste_type: WasteType
    detected: bool
    severity_score: float
    severity_level: SeverityLevel
    indicators: List[WasteIndicator]
    estimated_cost_impact: float
    estimated_time_impact: float
    root_causes: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'waste_type': self.waste_type.value,
            'detected': self.detected,
            'severity_score': self.severity_score,
            'severity_level': self.severity_level.value,
            'indicators': [
                {
                    'name': ind.name,
                    'value': ind.value,
                    'threshold': ind.threshold,
                    'weight': ind.weight,
                    'is_exceeded': ind.is_exceeded
                }
                for ind in self.indicators
            ],
            'estimated_cost_impact': self.estimated_cost_impact,
            'estimated_time_impact': self.estimated_time_impact,
            'root_causes': self.root_causes,
            'recommendations': self.recommendations,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }


class BaseWasteDetector(ABC):
    """Abstract base class for waste detectors"""
    
    def __init__(self, waste_type: WasteType):
        self.waste_type = waste_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.detection_history: List[WasteDetectionResult] = []
    
    @abstractmethod
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect waste in project data"""
        pass
    
    @abstractmethod
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract waste indicators from project data"""
        pass
    
    def calculate_severity_score(self, indicators: List[WasteIndicator]) -> float:
        """Calculate weighted severity score from indicators"""
        if not indicators:
            return 0.0
        
        total_weight = sum(ind.weight for ind in indicators)
        if total_weight == 0:
            return 0.0
        
        weighted_score = sum(
            (ind.value / ind.threshold if ind.threshold > 0 else 0) * ind.weight
            for ind in indicators
        )
        
        return min(weighted_score / total_weight, 1.0)
    
    def get_severity_level(self, score: float) -> SeverityLevel:
        """Convert severity score to severity level"""
        if score >= 0.8:
            return SeverityLevel.CRITICAL
        elif score >= 0.6:
            return SeverityLevel.HIGH
        elif score >= 0.4:
            return SeverityLevel.MEDIUM
        elif score >= 0.2:
            return SeverityLevel.LOW
        else:
            return SeverityLevel.NONE
    
    def train(self, historical_data: pd.DataFrame):
        """Train the detector on historical data"""
        pass  # Override in subclasses that use ML models
    
    def get_trend(self, window_size: int = 10) -> Dict:
        """Analyze trend in detection results"""
        if len(self.detection_history) < 2:
            return {'direction': 'insufficient_data', 'change': 0}
        
        recent = self.detection_history[-window_size:]
        scores = [r.severity_score for r in recent]
        
        if len(scores) < 2:
            return {'direction': 'insufficient_data', 'change': 0}
        
        change = scores[-1] - scores[0]
        
        return {
            'direction': 'improving' if change < 0 else 'worsening' if change > 0 else 'stable',
            'change': change,
            'average_score': np.mean(scores),
            'trend_coefficient': np.polyfit(range(len(scores)), scores, 1)[0] if len(scores) > 2 else 0
        }


class DefectsDetector(BaseWasteDetector):
    """
    Enhanced detector for Defects waste
    Uses ML-based anomaly detection for quality issue prediction
    """
    
    def __init__(self):
        super().__init__(WasteType.DEFECTS)
        self.anomaly_detector = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract defect-related indicators"""
        return [
            WasteIndicator(
                name='rework_rate',
                value=project_data.get('rework_rate', 0),
                threshold=0.05,  # 5% rework rate threshold
                weight=0.35
            ),
            WasteIndicator(
                name='quality_issues_count',
                value=project_data.get('quality_issues', 0),
                threshold=5,
                weight=0.25
            ),
            WasteIndicator(
                name='inspection_failure_rate',
                value=project_data.get('inspection_failures', 0) / 
                      max(project_data.get('total_inspections', 1), 1),
                threshold=0.10,  # 10% failure rate
                weight=0.20
            ),
            WasteIndicator(
                name='customer_complaints',
                value=project_data.get('customer_complaints', 0),
                threshold=3,
                weight=0.10
            ),
            WasteIndicator(
                name='non_conformance_reports',
                value=project_data.get('ncr_count', 0),
                threshold=2,
                weight=0.10
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect defects waste with ML enhancement"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate cost impact
        rework_hours = project_data.get('rework_hours', 0)
        labor_rate = project_data.get('labor_rate', 75)
        material_waste = project_data.get('material_waste_cost', 0)
        estimated_cost = (rework_hours * labor_rate) + material_waste
        
        # Calculate time impact
        estimated_time = rework_hours + (project_data.get('quality_issues', 0) * 4)
        
        # Identify root causes
        root_causes = self._identify_root_causes(project_data, indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        # Calculate confidence based on data completeness
        data_fields = ['rework_rate', 'quality_issues', 'inspection_failures', 
                       'total_inspections', 'customer_complaints']
        confidence = sum(1 for f in data_fields if f in project_data) / len(data_fields)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(
        self, 
        project_data: Dict, 
        indicators: List[WasteIndicator]
    ) -> List[str]:
        """Identify potential root causes of defects"""
        causes = []
        
        if project_data.get('training_hours_per_worker', 0) < 8:
            causes.append("Insufficient worker training (< 8 hours per worker)")
        
        if project_data.get('inspection_frequency', 0) < 2:
            causes.append("Low inspection frequency (< 2 per week)")
        
        if project_data.get('material_quality_score', 1.0) < 0.7:
            causes.append("Substandard material quality (score < 0.7)")
        
        if project_data.get('equipment_age_years', 0) > 10:
            causes.append("Aging equipment (> 10 years old)")
        
        if project_data.get('worker_fatigue_score', 0) > 0.6:
            causes.append("High worker fatigue levels")
        
        if project_data.get('specification_clarity_score', 1.0) < 0.7:
            causes.append("Unclear specifications or drawings")
        
        exceeded_indicators = [ind.name for ind in indicators if ind.is_exceeded]
        if 'rework_rate' in exceeded_indicators:
            causes.append("High rework rate indicates systemic quality issues")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if severity >= 0.8:
            recommendations.append(
                "URGENT: Implement immediate quality hold and conduct "
                "comprehensive root cause analysis"
            )
            recommendations.append(
                "Stop affected work activities until quality issues are resolved"
            )
        
        if severity >= 0.6:
            recommendations.append(
                "Increase inspection frequency to daily quality checks"
            )
            recommendations.append(
                "Implement quality gates at critical work stages"
            )
        
        if severity >= 0.4:
            recommendations.append(
                "Review and update quality control procedures"
            )
            recommendations.append(
                "Provide additional training on quality standards"
            )
        
        if "Insufficient worker training" in str(root_causes):
            recommendations.append(
                "Schedule quality awareness training for all workers"
            )
        
        if "Substandard material quality" in str(root_causes):
            recommendations.append(
                "Review material suppliers and implement incoming inspection"
            )
        
        return recommendations if recommendations else [
            "Continue current quality practices with regular monitoring"
        ]
    
    def train(self, historical_data: pd.DataFrame):
        """Train anomaly detector on historical quality data"""
        features = ['rework_rate', 'quality_issues', 'inspection_failures']
        available_features = [f for f in features if f in historical_data.columns]
        
        if len(available_features) < 2:
            logger.warning("Insufficient features for training defects detector")
            return
        
        X = historical_data[available_features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        self.anomaly_detector.fit(X_scaled)
        self.is_trained = True
        logger.info("Defects detector trained successfully")


class WaitingDetector(BaseWasteDetector):
    """
    Enhanced detector for Waiting waste
    Identifies idle time, delays, and process bottlenecks
    """
    
    def __init__(self):
        super().__init__(WasteType.WAITING)
        self.bottleneck_detector = DBSCAN(eps=0.5, min_samples=3)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract waiting-related indicators"""
        return [
            WasteIndicator(
                name='idle_time_percentage',
                value=project_data.get('idle_time_hours', 0) / 
                      max(project_data.get('total_work_hours', 1), 1),
                threshold=0.15,  # 15% idle time
                weight=0.30
            ),
            WasteIndicator(
                name='material_wait_hours',
                value=project_data.get('material_wait_time', 0),
                threshold=16,  # 2 days equivalent
                weight=0.25
            ),
            WasteIndicator(
                name='approval_delay_hours',
                value=project_data.get('approval_wait_time', 0),
                threshold=24,  # 3 days equivalent
                weight=0.20
            ),
            WasteIndicator(
                name='equipment_wait_hours',
                value=project_data.get('equipment_wait_time', 0),
                threshold=8,  # 1 day
                weight=0.15
            ),
            WasteIndicator(
                name='predecessor_delay_hours',
                value=project_data.get('predecessor_delay', 0),
                threshold=16,
                weight=0.10
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect waiting waste with bottleneck analysis"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        total_wait_time = sum([
            project_data.get('idle_time_hours', 0),
            project_data.get('material_wait_time', 0),
            project_data.get('approval_wait_time', 0),
            project_data.get('equipment_wait_time', 0)
        ])
        
        labor_rate = project_data.get('labor_rate', 75)
        crew_size = project_data.get('crew_size', 5)
        estimated_cost = total_wait_time * labor_rate * crew_size
        estimated_time = total_wait_time
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(project_data, indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(severity_score, bottlenecks)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.15,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=bottlenecks,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_bottlenecks(
        self, 
        project_data: Dict, 
        indicators: List[WasteIndicator]
    ) -> List[str]:
        """Identify process bottlenecks causing waiting"""
        bottlenecks = []
        
        if project_data.get('material_wait_time', 0) > 16:
            bottlenecks.append(
                f"Material delivery bottleneck: "
                f"{project_data.get('material_wait_time', 0):.1f} hours waiting"
            )
        
        if project_data.get('approval_wait_time', 0) > 24:
            bottlenecks.append(
                f"Approval process bottleneck: "
                f"{project_data.get('approval_wait_time', 0):.1f} hours delay"
            )
        
        if project_data.get('equipment_availability', 1.0) < 0.8:
            bottlenecks.append(
                f"Equipment availability issue: "
                f"{project_data.get('equipment_availability', 1.0)*100:.0f}% available"
            )
        
        if project_data.get('predecessor_delay', 0) > 16:
            bottlenecks.append(
                "Upstream activity delays affecting downstream work"
            )
        
        if project_data.get('resource_conflicts', 0) > 2:
            bottlenecks.append(
                f"Resource conflicts: {project_data.get('resource_conflicts', 0)} conflicts"
            )
        
        return bottlenecks if bottlenecks else ["No significant bottlenecks identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate recommendations to reduce waiting"""
        recommendations = []
        
        if severity >= 0.8:
            recommendations.append(
                "CRITICAL: Convene emergency meeting to address major delays"
            )
        
        if "Material delivery" in str(bottlenecks):
            recommendations.append(
                "Implement just-in-time material delivery with buffer stock"
            )
            recommendations.append(
                "Establish secondary suppliers for critical materials"
            )
        
        if "Approval process" in str(bottlenecks):
            recommendations.append(
                "Streamline approval workflow with pre-approved templates"
            )
            recommendations.append(
                "Implement parallel approval processes where possible"
            )
        
        if "Equipment availability" in str(bottlenecks):
            recommendations.append(
                "Develop equipment sharing schedule across work areas"
            )
            recommendations.append(
                "Consider additional equipment rental during peak periods"
            )
        
        if severity >= 0.4:
            recommendations.append(
                "Implement daily coordination meetings to anticipate delays"
            )
        
        return recommendations if recommendations else [
            "Continue monitoring for potential delays"
        ]
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence based on data availability"""
        required_fields = [
            'idle_time_hours', 'material_wait_time', 'approval_wait_time',
            'equipment_wait_time', 'total_work_hours'
        ]
        available = sum(1 for f in required_fields if f in project_data)
        return available / len(required_fields)


class OverproductionDetector(BaseWasteDetector):
    """
    Detector for Overproduction waste
    Identifies excess materials, early deliveries, and over-ordering
    """
    
    def __init__(self):
        super().__init__(WasteType.OVERPRODUCTION)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract overproduction indicators"""
        return [
            WasteIndicator(
                name='excess_material_percentage',
                value=project_data.get('excess_materials_percentage', 0),
                threshold=0.10,  # 10% excess
                weight=0.35
            ),
            WasteIndicator(
                name='early_delivery_count',
                value=project_data.get('early_deliveries', 0),
                threshold=5,
                weight=0.20
            ),
            WasteIndicator(
                name='unused_inventory_ratio',
                value=project_data.get('unused_inventory_value', 0) / 
                      max(project_data.get('total_material_value', 1), 1),
                threshold=0.15,
                weight=0.25
            ),
            WasteIndicator(
                name='over_order_incidents',
                value=project_data.get('over_order_count', 0),
                threshold=3,
                weight=0.20
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect overproduction waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        unused_inventory = project_data.get('unused_inventory_value', 0)
        storage_cost = project_data.get('storage_costs', 0)
        disposal_cost = project_data.get('disposal_costs', 0)
        estimated_cost = unused_inventory + storage_cost + disposal_cost
        
        # Time impact for handling excess
        handling_time = project_data.get('early_deliveries', 0) * 2
        estimated_time = handling_time
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of overproduction"""
        causes = []
        
        if project_data.get('forecast_accuracy', 1.0) < 0.8:
            causes.append("Poor material forecasting accuracy")
        
        if project_data.get('supplier_lead_time_variability', 0) > 5:
            causes.append("High supplier lead time variability causing over-ordering")
        
        if project_data.get('change_order_frequency', 0) > 3:
            causes.append("Frequent change orders leading to excess materials")
        
        if project_data.get('batch_ordering', False):
            causes.append("Bulk/batch ordering without JIT consideration")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for reducing overproduction"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Implement just-in-time delivery for non-critical materials"
            )
        
        if "Poor material forecasting" in str(root_causes):
            recommendations.append(
                "Improve material take-off accuracy with BIM integration"
            )
        
        if "Bulk/batch ordering" in str(root_causes):
            recommendations.append(
                "Switch to phased delivery schedule aligned with construction sequence"
            )
        
        if severity >= 0.4:
            recommendations.append(
                "Establish material return agreements with suppliers"
            )
        
        return recommendations if recommendations else [
            "Continue monitoring inventory levels"
        ]
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['excess_materials_percentage', 'unused_inventory_value', 
                  'total_material_value', 'early_deliveries']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class TalentUtilizationDetector(BaseWasteDetector):
    """
    Detector for Non-Utilized Talent waste
    Identifies skill mismatches, underutilization, and missed improvement opportunities
    """
    
    def __init__(self):
        super().__init__(WasteType.NON_UTILIZED_TALENT)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract talent utilization indicators"""
        return [
            WasteIndicator(
                name='skill_mismatch_rate',
                value=project_data.get('skill_mismatch_percentage', 0),
                threshold=0.20,  # 20% mismatch
                weight=0.30
            ),
            WasteIndicator(
                name='underutilization_rate',
                value=project_data.get('underutilized_workers', 0) /
                      max(project_data.get('total_workers', 1), 1),
                threshold=0.15,
                weight=0.25
            ),
            WasteIndicator(
                name='training_gap_score',
                value=project_data.get('training_gaps', 0) / 10,
                threshold=0.30,
                weight=0.20
            ),
            WasteIndicator(
                name='suggestion_implementation_rate',
                value=1 - project_data.get('suggestions_implemented', 0) /
                      max(project_data.get('suggestions_submitted', 1), 1),
                threshold=0.70,
                weight=0.15
            ),
            WasteIndicator(
                name='cross_training_gap',
                value=1 - project_data.get('cross_trained_percentage', 0),
                threshold=0.50,
                weight=0.10
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect non-utilized talent waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        underutilized = project_data.get('underutilized_workers', 0)
        hourly_rate = project_data.get('labor_rate', 75)
        hours_lost = project_data.get('productivity_loss_hours', 0)
        estimated_cost = underutilized * hourly_rate * 8 + hours_lost * hourly_rate
        
        training_hours_needed = project_data.get('training_gaps', 0) * 4
        estimated_time = training_hours_needed
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of talent underutilization"""
        causes = []
        
        if project_data.get('skill_mismatch_percentage', 0) > 0.2:
            causes.append("Workers assigned to tasks not matching their skills")
        
        if project_data.get('suggestions_implemented', 0) / \
           max(project_data.get('suggestions_submitted', 1), 1) < 0.3:
            causes.append("Low implementation rate for worker suggestions")
        
        if project_data.get('cross_trained_percentage', 0) < 0.5:
            causes.append("Limited cross-training reduces workforce flexibility")
        
        if project_data.get('empowerment_score', 1.0) < 0.6:
            causes.append("Low worker empowerment and decision-making authority")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for talent utilization"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Review task assignments to match worker skills and experience"
            )
        
        if "skill_mismatch" in str(root_causes).lower():
            recommendations.append(
                "Implement skill matrix and use for task assignment"
            )
        
        if "suggestions" in str(root_causes).lower():
            recommendations.append(
                "Establish rapid suggestion review process with feedback loop"
            )
        
        if "cross-training" in str(root_causes).lower():
            recommendations.append(
                "Develop cross-training program for key trades"
            )
        
        recommendations.append(
            "Conduct regular one-on-ones to identify improvement ideas"
        )
        
        return recommendations


    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['skill_mismatch_percentage', 'underutilized_workers', 
                  'total_workers', 'training_gaps', 'suggestions_submitted']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class TransportationDetector(BaseWasteDetector):
    """
    Detector for Transportation waste
    Identifies unnecessary material movement and inefficient logistics
    """
    
    def __init__(self):
        super().__init__(WasteType.TRANSPORTATION)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract transportation waste indicators"""
        return [
            WasteIndicator(
                name='material_moves_per_item',
                value=project_data.get('material_moves_count', 0) /
                      max(project_data.get('unique_materials', 1), 1),
                threshold=2.0,  # More than 2 moves per material type
                weight=0.30
            ),
            WasteIndicator(
                name='double_handling_rate',
                value=project_data.get('double_handling_incidents', 0) /
                      max(project_data.get('total_deliveries', 1), 1),
                threshold=0.10,
                weight=0.25
            ),
            WasteIndicator(
                name='transport_distance_efficiency',
                value=project_data.get('actual_transport_km', 0) /
                      max(project_data.get('optimal_transport_km', 1), 1) - 1,
                threshold=0.20,  # 20% more than optimal
                weight=0.25
            ),
            WasteIndicator(
                name='staging_relocations',
                value=project_data.get('staging_relocations', 0),
                threshold=5,
                weight=0.20
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect transportation waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        extra_moves = project_data.get('material_moves_count', 0)
        cost_per_move = project_data.get('cost_per_move', 50)
        transport_distance = project_data.get('actual_transport_km', 0) - \
                           project_data.get('optimal_transport_km', 0)
        cost_per_km = project_data.get('transport_cost_per_km', 5)
        
        estimated_cost = (extra_moves * cost_per_move * 0.3) + \
                        (max(transport_distance, 0) * cost_per_km)
        
        time_per_move = 0.25  # 15 minutes per move
        estimated_time = extra_moves * time_per_move * 0.3
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of transportation waste"""
        causes = []
        
        if project_data.get('site_layout_score', 1.0) < 0.7:
            causes.append("Suboptimal site layout increasing travel distances")
        
        if project_data.get('storage_planning_score', 1.0) < 0.7:
            causes.append("Poor material staging locations")
        
        if project_data.get('delivery_coordination_score', 1.0) < 0.7:
            causes.append("Uncoordinated deliveries causing congestion")
        
        if project_data.get('double_handling_incidents', 0) > 5:
            causes.append("Frequent double-handling of materials")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for reducing transportation waste"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Review and optimize site layout for material flow"
            )
        
        if "site layout" in str(root_causes).lower():
            recommendations.append(
                "Relocate staging areas closer to point of use"
            )
        
        if "double-handling" in str(root_causes).lower():
            recommendations.append(
                "Implement direct-to-location delivery where possible"
            )
        
        recommendations.append(
            "Create material flow diagram and eliminate unnecessary moves"
        )
        
        return recommendations
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['material_moves_count', 'double_handling_incidents',
                  'actual_transport_km', 'optimal_transport_km']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class InventoryDetector(BaseWasteDetector):
    """
    Detector for Inventory waste
    Identifies excess inventory, storage issues, and inventory management problems
    """
    
    def __init__(self):
        super().__init__(WasteType.INVENTORY)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract inventory waste indicators"""
        return [
            WasteIndicator(
                name='excess_inventory_ratio',
                value=project_data.get('excess_inventory_value', 0) /
                      max(project_data.get('total_inventory_value', 1), 1),
                threshold=0.15,
                weight=0.30
            ),
            WasteIndicator(
                name='obsolete_material_ratio',
                value=project_data.get('obsolete_materials_value', 0) /
                      max(project_data.get('total_inventory_value', 1), 1),
                threshold=0.05,
                weight=0.25
            ),
            WasteIndicator(
                name='storage_utilization',
                value=project_data.get('storage_utilization', 0),
                threshold=0.90,  # Over 90% is problematic
                weight=0.20
            ),
            WasteIndicator(
                name='inventory_turnover_days',
                value=project_data.get('inventory_days_on_hand', 0),
                threshold=30,
                weight=0.15
            ),
            WasteIndicator(
                name='damaged_inventory_rate',
                value=project_data.get('damaged_inventory_percentage', 0),
                threshold=0.02,
                weight=0.10
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect inventory waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        excess_value = project_data.get('excess_inventory_value', 0)
        obsolete_value = project_data.get('obsolete_materials_value', 0)
        storage_costs = project_data.get('storage_costs', 0)
        damage_costs = project_data.get('damage_costs', 0)
        
        estimated_cost = excess_value * 0.1 + obsolete_value + storage_costs + damage_costs
        estimated_time = 0  # Primarily cost impact
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of inventory waste"""
        causes = []
        
        if project_data.get('forecast_accuracy', 1.0) < 0.8:
            causes.append("Inaccurate material forecasting")
        
        if project_data.get('supplier_min_order_issues', 0) > 2:
            causes.append("Supplier minimum order quantities forcing excess purchasing")
        
        if project_data.get('design_changes', 0) > 3:
            causes.append("Design changes rendering materials obsolete")
        
        if project_data.get('storage_conditions_score', 1.0) < 0.7:
            causes.append("Poor storage conditions causing material damage")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for inventory management"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Implement kanban system for material replenishment"
            )
        
        if "forecasting" in str(root_causes).lower():
            recommendations.append(
                "Improve material quantity take-offs with 3D model integration"
            )
        
        if "minimum order" in str(root_causes).lower():
            recommendations.append(
                "Negotiate flexible order quantities or share orders with other projects"
            )
        
        if "storage conditions" in str(root_causes).lower():
            recommendations.append(
                "Improve material protection and storage practices"
            )
        
        return recommendations
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['excess_inventory_value', 'total_inventory_value',
                  'obsolete_materials_value', 'storage_costs']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class MotionDetector(BaseWasteDetector):
    """
    Detector for Motion waste
    Identifies unnecessary worker movements and ergonomic issues
    """
    
    def __init__(self):
        super().__init__(WasteType.MOTION)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract motion waste indicators"""
        return [
            WasteIndicator(
                name='tool_search_time_ratio',
                value=project_data.get('tool_search_time_hours', 0) /
                      max(project_data.get('total_work_hours', 1), 1),
                threshold=0.05,  # 5% of time searching
                weight=0.30
            ),
            WasteIndicator(
                name='unnecessary_movement_score',
                value=project_data.get('unnecessary_movements', 0) / 100,
                threshold=0.20,
                weight=0.25
            ),
            WasteIndicator(
                name='ergonomic_issues_rate',
                value=project_data.get('ergonomic_complaints', 0) /
                      max(project_data.get('total_workers', 1), 1),
                threshold=0.10,
                weight=0.25
            ),
            WasteIndicator(
                name='walking_distance_ratio',
                value=project_data.get('actual_walking_distance', 0) /
                      max(project_data.get('optimal_walking_distance', 1), 1) - 1,
                threshold=0.30,
                weight=0.20
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect motion waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        search_time = project_data.get('tool_search_time_hours', 0)
        unnecessary_time = project_data.get('unnecessary_movements', 0) * 0.05
        labor_rate = project_data.get('labor_rate', 75)
        
        estimated_cost = (search_time + unnecessary_time) * labor_rate
        estimated_time = search_time + unnecessary_time
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of motion waste"""
        causes = []
        
        if project_data.get('tool_organization_score', 1.0) < 0.7:
            causes.append("Poor tool organization and storage")
        
        if project_data.get('workstation_layout_score', 1.0) < 0.7:
            causes.append("Inefficient workstation layout")
        
        if project_data.get('5s_score', 1.0) < 0.6:
            causes.append("Low 5S workplace organization score")
        
        if project_data.get('ergonomic_assessment_score', 1.0) < 0.7:
            causes.append("Ergonomic issues in work processes")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for reducing motion waste"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Implement 5S workplace organization program"
            )
        
        if "tool organization" in str(root_causes).lower():
            recommendations.append(
                "Use shadow boards and designated tool locations"
            )
        
        if "workstation" in str(root_causes).lower():
            recommendations.append(
                "Redesign workstations for optimal material flow"
            )
        
        if "ergonomic" in str(root_causes).lower():
            recommendations.append(
                "Conduct ergonomic assessment and implement improvements"
            )
        
        return recommendations
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['tool_search_time_hours', 'unnecessary_movements',
                  'ergonomic_complaints', 'total_workers']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class ExtraProcessingDetector(BaseWasteDetector):
    """
    Detector for Extra Processing waste
    Identifies over-engineering, unnecessary steps, and redundant activities
    """
    
    def __init__(self):
        super().__init__(WasteType.EXTRA_PROCESSING)
    
    def get_indicators(self, project_data: Dict) -> List[WasteIndicator]:
        """Extract extra processing indicators"""
        return [
            WasteIndicator(
                name='over_engineering_rate',
                value=project_data.get('over_engineering_incidents', 0) /
                      max(project_data.get('total_activities', 1), 1),
                threshold=0.05,
                weight=0.30
            ),
            WasteIndicator(
                name='unnecessary_steps_ratio',
                value=project_data.get('unnecessary_process_steps', 0) /
                      max(project_data.get('total_process_steps', 1), 1),
                threshold=0.10,
                weight=0.25
            ),
            WasteIndicator(
                name='redundant_approval_rate',
                value=project_data.get('redundant_approvals', 0) /
                      max(project_data.get('total_approvals', 1), 1),
                threshold=0.15,
                weight=0.25
            ),
            WasteIndicator(
                name='rework_from_overprocessing',
                value=project_data.get('overprocessing_rework_hours', 0),
                threshold=20,
                weight=0.20
            )
        ]
    
    def detect(self, project_data: Dict) -> WasteDetectionResult:
        """Detect extra processing waste"""
        indicators = self.get_indicators(project_data)
        severity_score = self.calculate_severity_score(indicators)
        severity_level = self.get_severity_level(severity_score)
        
        # Calculate impacts
        over_engineering_cost = project_data.get('over_engineering_incidents', 0) * 2000
        unnecessary_steps_cost = project_data.get('unnecessary_process_steps', 0) * 500
        approval_delay_cost = project_data.get('redundant_approvals', 0) * 300
        
        estimated_cost = over_engineering_cost + unnecessary_steps_cost + approval_delay_cost
        
        estimated_time = (
            project_data.get('over_engineering_incidents', 0) * 8 +
            project_data.get('unnecessary_process_steps', 0) * 2 +
            project_data.get('redundant_approvals', 0) * 1
        )
        
        root_causes = self._identify_root_causes(project_data)
        recommendations = self._generate_recommendations(severity_score, root_causes)
        
        confidence = self._calculate_confidence(project_data)
        
        result = WasteDetectionResult(
            waste_type=self.waste_type,
            detected=severity_score > 0.2,
            severity_score=severity_score,
            severity_level=severity_level,
            indicators=indicators,
            estimated_cost_impact=estimated_cost,
            estimated_time_impact=estimated_time,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.detection_history.append(result)
        return result
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify causes of extra processing"""
        causes = []
        
        if project_data.get('specification_clarity_score', 1.0) < 0.7:
            causes.append("Unclear specifications leading to over-interpretation")
        
        if project_data.get('process_documentation_quality', 1.0) < 0.7:
            causes.append("Outdated or unclear process documentation")
        
        if project_data.get('approval_process_efficiency', 1.0) < 0.7:
            causes.append("Inefficient approval processes with redundant steps")
        
        if project_data.get('gold_plating_incidents', 0) > 2:
            causes.append("Gold plating - exceeding requirements without added value")
        
        return causes if causes else ["No significant root causes identified"]
    
    def _generate_recommendations(
        self, 
        severity: float, 
        root_causes: List[str]
    ) -> List[str]:
        """Generate recommendations for reducing extra processing"""
        recommendations = []
        
        if severity >= 0.6:
            recommendations.append(
                "Value stream map all major processes to identify waste"
            )
        
        if "specification" in str(root_causes).lower():
            recommendations.append(
                "Clarify specifications with design team and client"
            )
        
        if "approval" in str(root_causes).lower():
            recommendations.append(
                "Streamline approval process with defined authority levels"
            )
        
        if "gold plating" in str(root_causes).lower():
            recommendations.append(
                "Reinforce 'build to specification' training for crews"
            )
        
        return recommendations
    
    def _calculate_confidence(self, project_data: Dict) -> float:
        """Calculate confidence score"""
        fields = ['over_engineering_incidents', 'unnecessary_process_steps',
                  'redundant_approvals', 'total_activities']
        available = sum(1 for f in fields if f in project_data)
        return available / len(fields)


class WasteDetectionEngine:
    """
    Main orchestration engine for detecting all 8 types of waste
    Provides comprehensive analysis with ML-enhanced detection
    """
    
    def __init__(self):
        """Initialize waste detection engine with all detectors"""
        self.detectors = {
            WasteType.DEFECTS: DefectsDetector(),
            WasteType.OVERPRODUCTION: OverproductionDetector(),
            WasteType.WAITING: WaitingDetector(),
            WasteType.NON_UTILIZED_TALENT: TalentUtilizationDetector(),
            WasteType.TRANSPORTATION: TransportationDetector(),
            WasteType.INVENTORY: InventoryDetector(),
            WasteType.MOTION: MotionDetector(),
            WasteType.EXTRA_PROCESSING: ExtraProcessingDetector()
        }
        
        self.analysis_history: List[Dict] = []
    
    def detect_all_wastes(self, project_data: Dict) -> Dict:
        """
        Detect all types of waste in project data
        
        Args:
            project_data: Dictionary containing project metrics and data
            
        Returns:
            Comprehensive waste analysis results
        """
        results = {}
        total_cost_impact = 0
        total_time_impact = 0
        total_severity = 0
        
        for waste_type, detector in self.detectors.items():
            try:
                detection_result = detector.detect(project_data)
                results[waste_type.value] = detection_result.to_dict()
                total_cost_impact += detection_result.estimated_cost_impact
                total_time_impact += detection_result.estimated_time_impact
                total_severity += detection_result.severity_score
            except Exception as e:
                logger.error(f"Error detecting {waste_type.value}: {str(e)}")
                results[waste_type.value] = {
                    'error': str(e),
                    'detected': False,
                    'severity_score': 0
                }
        
        # Calculate overall metrics
        avg_severity = total_severity / len(self.detectors)
        health_status = self._get_health_status(avg_severity)
        
        # Priority actions
        priority_actions = self._prioritize_actions(results)
        
        # Generate summary
        summary = self._generate_summary(results, avg_severity)
        
        analysis_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'project_id': project_data.get('project_id', 'unknown'),
            'overall_waste_score': avg_severity,
            'health_status': health_status,
            'total_cost_impact': total_cost_impact,
            'total_time_impact': total_time_impact,
            'detected_wastes': results,
            'priority_actions': priority_actions,
            'summary': summary,
            'trend': self._calculate_overall_trend()
        }
        
        self.analysis_history.append(analysis_result)
        
        return analysis_result
    
    def detect_specific_waste(
        self, 
        waste_type: WasteType, 
        project_data: Dict
    ) -> WasteDetectionResult:
        """Detect a specific type of waste"""
        if waste_type not in self.detectors:
            raise ValueError(f"Unknown waste type: {waste_type}")
        
        return self.detectors[waste_type].detect(project_data)
    
    def train_detectors(self, historical_data: pd.DataFrame):
        """Train all ML-based detectors"""
        for waste_type, detector in self.detectors.items():
            try:
                detector.train(historical_data)
                logger.info(f"Trained {waste_type.value} detector")
            except Exception as e:
                logger.warning(f"Could not train {waste_type.value} detector: {e}")
    
    def _get_health_status(self, score: float) -> str:
        """Determine overall project health"""
        if score < 0.2:
            return 'excellent'
        elif score < 0.4:
            return 'good'
        elif score < 0.6:
            return 'fair'
        elif score < 0.8:
            return 'poor'
        else:
            return 'critical'
    
    def _prioritize_actions(self, results: Dict) -> List[Dict]:
        """Prioritize corrective actions across all waste types"""
        actions = []
        
        for waste_type, data in results.items():
            if data.get('detected', False) and data.get('severity_score', 0) > 0.3:
                for rec in data.get('recommendations', []):
                    actions.append({
                        'waste_type': waste_type,
                        'severity': data.get('severity_score'),
                        'severity_level': data.get('severity_level'),
                        'action': rec,
                        'cost_impact': data.get('estimated_cost_impact', 0),
                        'time_impact': data.get('estimated_time_impact', 0),
                        'priority': (
                            'critical' if data.get('severity_score', 0) > 0.8
                            else 'high' if data.get('severity_score', 0) > 0.6
                            else 'medium'
                        )
                    })
        
        # Sort by severity then cost impact
        actions.sort(
            key=lambda x: (
                0 if x['priority'] == 'critical' else 1 if x['priority'] == 'high' else 2,
                -x['cost_impact']
            )
        )
        
        return actions[:10]  # Top 10 priority actions
    
    def _generate_summary(self, results: Dict, avg_severity: float) -> Dict:
        """Generate executive summary of waste analysis"""
        detected_wastes = [
            waste_type for waste_type, data in results.items()
            if data.get('detected', False)
        ]
        
        critical_wastes = [
            waste_type for waste_type, data in results.items()
            if data.get('severity_level') in ['critical', 'high']
        ]
        
        total_cost = sum(
            data.get('estimated_cost_impact', 0) 
            for data in results.values()
        )
        
        return {
            'total_wastes_detected': len(detected_wastes),
            'critical_wastes': critical_wastes,
            'detected_waste_types': detected_wastes,
            'average_severity': avg_severity,
            'total_estimated_cost_impact': total_cost,
            'narrative': self._generate_narrative(detected_wastes, critical_wastes, avg_severity)
        }
    
    def _generate_narrative(
        self, 
        detected: List[str], 
        critical: List[str], 
        severity: float
    ) -> str:
        """Generate human-readable narrative summary"""
        if not detected:
            return "No significant waste detected. Continue monitoring and maintaining current practices."
        
        narrative_parts = []
        
        if critical:
            narrative_parts.append(
                f"ATTENTION REQUIRED: {len(critical)} critical waste issue(s) detected: "
                f"{', '.join(critical)}."
            )
        
        narrative_parts.append(
            f"Analysis identified {len(detected)} waste type(s) with "
            f"average severity of {severity:.1%}."
        )
        
        if severity > 0.6:
            narrative_parts.append(
                "Immediate action recommended to address high-severity issues."
            )
        elif severity > 0.4:
            narrative_parts.append(
                "Review priority actions and implement improvements within the week."
            )
        
        return " ".join(narrative_parts)
    
    def _calculate_overall_trend(self) -> Dict:
        """Calculate overall waste trend from history"""
        if len(self.analysis_history) < 2:
            return {'direction': 'insufficient_data', 'change': 0}
        
        recent_scores = [
            h['overall_waste_score'] 
            for h in self.analysis_history[-10:]
        ]
        
        change = recent_scores[-1] - recent_scores[0]
        
        return {
            'direction': 'improving' if change < -0.05 else 'worsening' if change > 0.05 else 'stable',
            'change': change,
            'data_points': len(recent_scores)
        }
    
    def get_waste_report(self, detailed: bool = True) -> Dict:
        """
        Generate comprehensive waste report
        
        Args:
            detailed: Include detailed breakdowns
            
        Returns:
            Formatted waste report
        """
        if not self.analysis_history:
            return {'error': 'No analysis data available'}
        
        latest = self.analysis_history[-1]
        
        report = {
            'report_date': datetime.utcnow().isoformat(),
            'analysis_timestamp': latest['timestamp'],
            'project_id': latest['project_id'],
            'executive_summary': latest['summary'],
            'health_status': latest['health_status'],
            'overall_score': latest['overall_waste_score'],
            'trend': latest['trend'],
            'priority_actions': latest['priority_actions'][:5]
        }
        
        if detailed:
            report['waste_breakdown'] = latest['detected_wastes']
            report['historical_trend'] = self._get_historical_trend()
        
        return report
    
    def _get_historical_trend(self) -> List[Dict]:
        """Get historical trend data"""
        return [
            {
                'timestamp': h['timestamp'],
                'overall_score': h['overall_waste_score'],
                'health_status': h['health_status']
            }
            for h in self.analysis_history[-30:]
        ]
    
    def export_analysis(self, filepath: str):
        """Export analysis history to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.analysis_history, f, indent=2, default=str)
        logger.info(f"Exported analysis to {filepath}")
    
    def import_analysis(self, filepath: str):
        """Import analysis history from JSON file"""
        with open(filepath, 'r') as f:
            self.analysis_history = json.load(f)
        logger.info(f"Imported {len(self.analysis_history)} analyses from {filepath}")
