"""
Waste Detection Algorithms for the 8 Wastes (DOWNTIME)
- Defects
- Overproduction
- Waiting
- Non-utilized Talent
- Transportation
- Inventory
- Motion
- Extra Processing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class WasteDetectionEngine:
    """
    Main engine for detecting all 8 types of waste
    """
    
    def __init__(self):
        """Initialize waste detection engine"""
        self.waste_types = [
            'defects',
            'overproduction',
            'waiting',
            'non_utilized_talent',
            'transportation',
            'inventory',
            'motion',
            'extra_processing'
        ]
        
        self.detectors = {
            'defects': DefectsDetector(),
            'overproduction': OverproductionDetector(),
            'waiting': WaitingDetector(),
            'non_utilized_talent': TalentUtilizationDetector(),
            'transportation': TransportationDetector(),
            'inventory': InventoryDetector(),
            'motion': MotionDetector(),
            'extra_processing': ExtraProcessingDetector()
        }
    
    def detect_all_wastes(self, project_data: Dict) -> Dict:
        """
        Detect all types of waste in project data
        
        Args:
            project_data: Dictionary containing project metrics and data
            
        Returns:
            Dictionary with detected wastes and recommendations
        """
        results = {}
        total_waste_score = 0
        
        for waste_type in self.waste_types:
            detector = self.detectors[waste_type]
            detection_result = detector.detect(project_data)
            results[waste_type] = detection_result
            total_waste_score += detection_result.get('severity_score', 0)
        
        # Calculate overall waste health
        avg_waste_score = total_waste_score / len(self.waste_types)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_waste_score': avg_waste_score,
            'health_status': self._get_health_status(avg_waste_score),
            'detected_wastes': results,
            'priority_actions': self._prioritize_actions(results),
            'estimated_cost_impact': self._estimate_cost_impact(results),
            'estimated_time_impact': self._estimate_time_impact(results)
        }
    
    def _get_health_status(self, score: float) -> str:
        """Determine project health based on waste score"""
        if score < 0.3:
            return 'excellent'
        elif score < 0.5:
            return 'good'
        elif score < 0.7:
            return 'fair'
        else:
            return 'poor'
    
    def _prioritize_actions(self, results: Dict) -> List[Dict]:
        """Prioritize corrective actions"""
        actions = []
        
        for waste_type, data in results.items():
            if data.get('severity_score', 0) > 0.6:
                actions.append({
                    'waste_type': waste_type,
                    'severity': data.get('severity_score'),
                    'action': data.get('recommendation'),
                    'priority': 'high' if data.get('severity_score') > 0.8 else 'medium'
                })
        
        # Sort by severity
        actions.sort(key=lambda x: x['severity'], reverse=True)
        return actions
    
    def _estimate_cost_impact(self, results: Dict) -> float:
        """Estimate total cost impact of detected wastes"""
        return sum(
            data.get('estimated_cost', 0) 
            for data in results.values()
        )
    
    def _estimate_time_impact(self, results: Dict) -> float:
        """Estimate total time impact of detected wastes"""
        return sum(
            data.get('estimated_time', 0) 
            for data in results.values()
        )


class DefectsDetector:
    """Detect defects and quality issues"""
    
    def detect(self, project_data: Dict) -> Dict:
        """
        Detect defects waste
        
        Args:
            project_data: Project metrics
            
        Returns:
            Detection results
        """
        # Extract relevant metrics
        rework_rate = project_data.get('rework_rate', 0)
        quality_issues = project_data.get('quality_issues', 0)
        inspection_failures = project_data.get('inspection_failures', 0)
        
        # Calculate severity
        severity_score = min(
            (rework_rate * 0.4 + 
             quality_issues * 0.3 + 
             inspection_failures * 0.3),
            1.0
        )
        
        # Estimate impact
        estimated_cost = quality_issues * 5000  # $5k per issue
        estimated_time = quality_issues * 8  # 8 hours per issue
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'rework_rate': rework_rate,
                'quality_issues': quality_issues,
                'inspection_failures': inspection_failures
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score),
            'root_causes': self._identify_root_causes(project_data)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation based on severity"""
        if severity > 0.7:
            return "Critical: Implement immediate quality control measures and root cause analysis"
        elif severity > 0.5:
            return "High: Review quality processes and increase inspection frequency"
        elif severity > 0.3:
            return "Medium: Monitor quality metrics and provide additional training"
        else:
            return "Low: Continue current quality practices"
    
    def _identify_root_causes(self, project_data: Dict) -> List[str]:
        """Identify potential root causes"""
        causes = []
        
        if project_data.get('training_hours', 0) < 10:
            causes.append("Insufficient worker training")
        if project_data.get('inspection_frequency', 0) < 2:
            causes.append("Infrequent quality inspections")
        if project_data.get('material_quality_score', 1.0) < 0.7:
            causes.append("Poor material quality")
        
        return causes


class WaitingDetector:
    """Detect waiting time waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect waiting waste"""
        # Extract metrics
        idle_time = project_data.get('idle_time_hours', 0)
        delays = project_data.get('delays_count', 0)
        material_wait_time = project_data.get('material_wait_time', 0)
        approval_wait_time = project_data.get('approval_wait_time', 0)
        
        # Calculate severity
        total_wait_time = idle_time + material_wait_time + approval_wait_time
        severity_score = min(total_wait_time / 100, 1.0)  # Normalize to 0-1
        
        # Estimate impact
        estimated_cost = total_wait_time * 75  # $75/hour labor cost
        estimated_time = total_wait_time
        
        return {
            'detected': severity_score > 0.2,
            'severity_score': severity_score,
            'indicators': {
                'idle_time': idle_time,
                'delays_count': delays,
                'material_wait_time': material_wait_time,
                'approval_wait_time': approval_wait_time,
                'total_wait_time': total_wait_time
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score),
            'bottlenecks': self._identify_bottlenecks(project_data)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Identify and eliminate major bottlenecks immediately"
        elif severity > 0.5:
            return "High: Improve material scheduling and approval processes"
        elif severity > 0.3:
            return "Medium: Optimize workflow and reduce wait times"
        else:
            return "Low: Monitor for potential delays"
    
    def _identify_bottlenecks(self, project_data: Dict) -> List[str]:
        """Identify bottlenecks"""
        bottlenecks = []
        
        if project_data.get('material_wait_time', 0) > 20:
            bottlenecks.append("Material delivery delays")
        if project_data.get('approval_wait_time', 0) > 15:
            bottlenecks.append("Slow approval processes")
        if project_data.get('equipment_availability', 1.0) < 0.8:
            bottlenecks.append("Equipment availability issues")
        
        return bottlenecks


class OverproductionDetector:
    """Detect overproduction waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect overproduction waste"""
        # Extract metrics
        excess_materials = project_data.get('excess_materials_percentage', 0)
        early_deliveries = project_data.get('early_deliveries', 0)
        unused_inventory = project_data.get('unused_inventory_value', 0)
        
        # Calculate severity
        severity_score = min(
            (excess_materials * 0.5 + 
             early_deliveries * 0.3 + 
             (unused_inventory / 10000) * 0.2),
            1.0
        )
        
        # Estimate impact
        estimated_cost = unused_inventory + (excess_materials * 1000)
        estimated_time = early_deliveries * 2  # Storage handling time
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'excess_materials': excess_materials,
                'early_deliveries': early_deliveries,
                'unused_inventory_value': unused_inventory
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Implement just-in-time delivery and reduce excess ordering"
        elif severity > 0.5:
            return "High: Review material ordering processes and timing"
        elif severity > 0.3:
            return "Medium: Optimize inventory levels"
        else:
            return "Low: Continue monitoring inventory"


class TalentUtilizationDetector:
    """Detect non-utilized talent waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect talent utilization issues"""
        # Extract metrics
        skill_mismatch = project_data.get('skill_mismatch_percentage', 0)
        underutilized_workers = project_data.get('underutilized_workers', 0)
        training_gaps = project_data.get('training_gaps', 0)
        
        # Calculate severity
        severity_score = min(
            (skill_mismatch * 0.4 + 
             underutilized_workers * 0.4 + 
             training_gaps * 0.2),
            1.0
        )
        
        # Estimate impact
        estimated_cost = underutilized_workers * 500  # Lost productivity
        estimated_time = training_gaps * 4  # Training time needed
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'skill_mismatch': skill_mismatch,
                'underutilized_workers': underutilized_workers,
                'training_gaps': training_gaps
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Reassign workers to match skills and provide urgent training"
        elif severity > 0.5:
            return "High: Improve task allocation and skill development"
        elif severity > 0.3:
            return "Medium: Review workforce utilization"
        else:
            return "Low: Continue current practices"


class TransportationDetector:
    """Detect transportation waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect transportation waste"""
        # Extract metrics
        material_moves = project_data.get('material_moves_count', 0)
        transport_distance = project_data.get('transport_distance_km', 0)
        double_handling = project_data.get('double_handling_incidents', 0)
        
        # Calculate severity
        severity_score = min(
            (material_moves / 100 * 0.4 + 
             transport_distance / 50 * 0.3 + 
             double_handling / 10 * 0.3),
            1.0
        )
        
        # Estimate impact
        estimated_cost = (material_moves * 50 + 
                         transport_distance * 10 + 
                         double_handling * 200)
        estimated_time = material_moves * 0.5 + double_handling * 2
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'material_moves': material_moves,
                'transport_distance': transport_distance,
                'double_handling': double_handling
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Redesign site layout and material flow"
        elif severity > 0.5:
            return "High: Reduce unnecessary material movements"
        elif severity > 0.3:
            return "Medium: Optimize material placement"
        else:
            return "Low: Continue monitoring"


class InventoryDetector:
    """Detect inventory waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect inventory waste"""
        # Extract metrics
        excess_inventory = project_data.get('excess_inventory_value', 0)
        storage_costs = project_data.get('storage_costs', 0)
        obsolete_materials = project_data.get('obsolete_materials_value', 0)
        
        # Calculate severity
        total_inventory_waste = excess_inventory + obsolete_materials
        severity_score = min(total_inventory_waste / 50000, 1.0)
        
        # Estimate impact
        estimated_cost = total_inventory_waste + storage_costs
        estimated_time = 0  # Primarily cost impact
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'excess_inventory': excess_inventory,
                'storage_costs': storage_costs,
                'obsolete_materials': obsolete_materials
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Implement just-in-time inventory system"
        elif severity > 0.5:
            return "High: Reduce inventory levels and improve turnover"
        elif severity > 0.3:
            return "Medium: Optimize inventory management"
        else:
            return "Low: Continue current practices"


class MotionDetector:
    """Detect motion waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect motion waste"""
        # Extract metrics
        unnecessary_movements = project_data.get('unnecessary_movements', 0)
        poor_ergonomics = project_data.get('poor_ergonomics_score', 0)
        tool_search_time = project_data.get('tool_search_time_hours', 0)
        
        # Calculate severity
        severity_score = min(
            (unnecessary_movements / 50 * 0.4 + 
             poor_ergonomics * 0.3 + 
             tool_search_time / 10 * 0.3),
            1.0
        )
        
        # Estimate impact
        estimated_cost = (unnecessary_movements * 20 + 
                         tool_search_time * 75)
        estimated_time = unnecessary_movements * 0.1 + tool_search_time
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'unnecessary_movements': unnecessary_movements,
                'poor_ergonomics': poor_ergonomics,
                'tool_search_time': tool_search_time
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Redesign workstations and implement 5S"
        elif severity > 0.5:
            return "High: Improve tool organization and workspace layout"
        elif severity > 0.3:
            return "Medium: Optimize worker movements"
        else:
            return "Low: Continue monitoring"


class ExtraProcessingDetector:
    """Detect extra processing waste"""
    
    def detect(self, project_data: Dict) -> Dict:
        """Detect extra processing waste"""
        # Extract metrics
        over_engineering = project_data.get('over_engineering_incidents', 0)
        unnecessary_steps = project_data.get('unnecessary_process_steps', 0)
        redundant_approvals = project_data.get('redundant_approvals', 0)
        
        # Calculate severity
        severity_score = min(
            (over_engineering / 5 * 0.4 + 
             unnecessary_steps / 10 * 0.3 + 
             redundant_approvals / 10 * 0.3),
            1.0
        )
        
        # Estimate impact
        estimated_cost = (over_engineering * 2000 + 
                         unnecessary_steps * 500 + 
                         redundant_approvals * 300)
        estimated_time = (over_engineering * 8 + 
                         unnecessary_steps * 2 + 
                         redundant_approvals * 1)
        
        return {
            'detected': severity_score > 0.3,
            'severity_score': severity_score,
            'indicators': {
                'over_engineering': over_engineering,
                'unnecessary_steps': unnecessary_steps,
                'redundant_approvals': redundant_approvals
            },
            'estimated_cost': estimated_cost,
            'estimated_time': estimated_time,
            'recommendation': self._generate_recommendation(severity_score)
        }
    
    def _generate_recommendation(self, severity: float) -> str:
        """Generate recommendation"""
        if severity > 0.7:
            return "Critical: Streamline processes and eliminate unnecessary steps"
        elif severity > 0.5:
            return "High: Review and simplify approval processes"
        elif severity > 0.3:
            return "Medium: Identify and remove redundant activities"
        else:
            return "Low: Continue current practices"
