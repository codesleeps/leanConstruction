"""
Computer Vision Models for Construction Site Analysis
- Site progress monitoring
- Safety compliance detection
- Equipment tracking
- 5S workplace assessment
"""
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ProgressMonitoringModel:
    """
    CNN-based model for monitoring construction site progress
    Based on ResNet architecture
    """
    
    def __init__(self, model_path: Optional[str] = None, num_classes: int = 10):
        """
        Initialize progress monitoring model
        
        Args:
            model_path: Path to pre-trained model weights
            num_classes: Number of progress stages to classify
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained ResNet50 and modify for our use case
        self.model = models.resnet50(pretrained=True)
        
        # Modify final layer for our number of classes
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        self.model = self.model.to(self.device)
        
        if model_path:
            self.load_weights(model_path)
        
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Progress stages
        self.stages = [
            'foundation',
            'framing',
            'rough_plumbing',
            'rough_electrical',
            'insulation',
            'drywall',
            'interior_finish',
            'exterior_finish',
            'final_inspection',
            'complete'
        ]
    
    def load_weights(self, model_path: str):
        """Load pre-trained weights"""
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            logger.info(f"Loaded model weights from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model weights: {str(e)}")
    
    def predict_progress(self, image_path: str) -> Dict:
        """
        Predict construction progress from image
        
        Args:
            image_path: Path to construction site image
            
        Returns:
            Dictionary with progress prediction and confidence
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            stage_idx = predicted.item()
            confidence_score = confidence.item()
            
            return {
                'stage': self.stages[stage_idx],
                'stage_index': stage_idx,
                'confidence': confidence_score,
                'completion_percentage': (stage_idx / len(self.stages)) * 100,
                'all_probabilities': {
                    stage: prob.item() 
                    for stage, prob in zip(self.stages, probabilities[0])
                }
            }
        
        except Exception as e:
            logger.error(f"Error predicting progress: {str(e)}")
            return {
                'stage': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_progress_change(
        self, 
        previous_image: str, 
        current_image: str
    ) -> Dict:
        """
        Analyze progress change between two images
        
        Args:
            previous_image: Path to previous image
            current_image: Path to current image
            
        Returns:
            Dictionary with progress change analysis
        """
        prev_result = self.predict_progress(previous_image)
        curr_result = self.predict_progress(current_image)
        
        progress_change = (
            curr_result['stage_index'] - prev_result['stage_index']
        )
        
        return {
            'previous_stage': prev_result['stage'],
            'current_stage': curr_result['stage'],
            'progress_change': progress_change,
            'is_progressing': progress_change > 0,
            'is_stalled': progress_change == 0,
            'is_regressing': progress_change < 0,
            'completion_change': (
                curr_result['completion_percentage'] - 
                prev_result['completion_percentage']
            )
        }


class SafetyComplianceDetector:
    """
    Object detection model for safety compliance
    Detects PPE, hazards, and safety violations
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize safety compliance detector"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load YOLO-based model (using torchvision's Faster R-CNN as base)
        self.model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Safety items to detect
        self.safety_items = {
            'hard_hat': 'required',
            'safety_vest': 'required',
            'safety_boots': 'required',
            'gloves': 'recommended',
            'safety_glasses': 'required',
            'harness': 'required_at_height',
            'fire_extinguisher': 'required',
            'first_aid_kit': 'required',
            'warning_signs': 'required',
            'barriers': 'required'
        }
    
    def detect_safety_items(self, image_path: str) -> Dict:
        """
        Detect safety items and violations in image
        
        Args:
            image_path: Path to site image
            
        Returns:
            Dictionary with detected items and violations
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            image_tensor = transforms.ToTensor()(image).unsqueeze(0).to(self.device)
            
            # Detect objects
            with torch.no_grad():
                predictions = self.model(image_tensor)
            
            # Process detections
            boxes = predictions[0]['boxes'].cpu().numpy()
            labels = predictions[0]['labels'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()
            
            # Filter by confidence threshold
            threshold = 0.5
            mask = scores > threshold
            
            detected_items = []
            for box, label, score in zip(boxes[mask], labels[mask], scores[mask]):
                detected_items.append({
                    'bbox': box.tolist(),
                    'label': int(label),
                    'confidence': float(score)
                })
            
            # Analyze safety compliance
            compliance_score = self._calculate_compliance_score(detected_items)
            violations = self._identify_violations(detected_items)
            
            return {
                'detected_items': detected_items,
                'total_detections': len(detected_items),
                'compliance_score': compliance_score,
                'violations': violations,
                'is_compliant': compliance_score >= 0.8,
                'recommendations': self._generate_recommendations(violations)
            }
        
        except Exception as e:
            logger.error(f"Error detecting safety items: {str(e)}")
            return {
                'error': str(e),
                'detected_items': [],
                'compliance_score': 0.0
            }
    
    def _calculate_compliance_score(self, detected_items: List[Dict]) -> float:
        """Calculate overall safety compliance score"""
        # Simplified scoring - in production, use more sophisticated logic
        required_items = sum(
            1 for item in self.safety_items.values() 
            if item == 'required'
        )
        
        if required_items == 0:
            return 1.0
        
        detected_required = min(len(detected_items), required_items)
        return detected_required / required_items
    
    def _identify_violations(self, detected_items: List[Dict]) -> List[Dict]:
        """Identify safety violations"""
        violations = []
        
        # Example violations (simplified)
        if len(detected_items) < 3:
            violations.append({
                'type': 'missing_ppe',
                'severity': 'high',
                'description': 'Insufficient PPE detected'
            })
        
        return violations
    
    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        for violation in violations:
            if violation['type'] == 'missing_ppe':
                recommendations.append(
                    'Ensure all workers wear required PPE: hard hat, safety vest, boots'
                )
        
        return recommendations


class EquipmentTracker:
    """
    Track construction equipment and utilization
    """
    
    def __init__(self):
        """Initialize equipment tracker"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Equipment types
        self.equipment_types = [
            'excavator',
            'bulldozer',
            'crane',
            'forklift',
            'concrete_mixer',
            'dump_truck',
            'scaffolding',
            'generator'
        ]
    
    def track_equipment(
        self, 
        image_path: str,
        previous_positions: Optional[Dict] = None
    ) -> Dict:
        """
        Track equipment in construction site
        
        Args:
            image_path: Path to site image
            previous_positions: Previous equipment positions for tracking
            
        Returns:
            Dictionary with equipment tracking data
        """
        try:
            # Load and process image
            image = cv2.imread(image_path)
            
            # Detect equipment (simplified - in production use trained model)
            detected_equipment = self._detect_equipment(image)
            
            # Calculate utilization
            utilization = self._calculate_utilization(
                detected_equipment,
                previous_positions
            )
            
            return {
                'detected_equipment': detected_equipment,
                'total_equipment': len(detected_equipment),
                'utilization_rate': utilization,
                'idle_equipment': [
                    eq for eq in detected_equipment 
                    if eq.get('status') == 'idle'
                ],
                'active_equipment': [
                    eq for eq in detected_equipment 
                    if eq.get('status') == 'active'
                ]
            }
        
        except Exception as e:
            logger.error(f"Error tracking equipment: {str(e)}")
            return {
                'error': str(e),
                'detected_equipment': []
            }
    
    def _detect_equipment(self, image: np.ndarray) -> List[Dict]:
        """Detect equipment in image"""
        # Placeholder - in production, use trained object detection model
        return []
    
    def _calculate_utilization(
        self,
        current_equipment: List[Dict],
        previous_positions: Optional[Dict]
    ) -> float:
        """Calculate equipment utilization rate"""
        if not current_equipment:
            return 0.0
        
        active_count = sum(
            1 for eq in current_equipment 
            if eq.get('status') == 'active'
        )
        
        return active_count / len(current_equipment) if current_equipment else 0.0


class WorkplaceOrganizationAnalyzer:
    """
    5S Workplace Organization Analysis
    Analyzes Sort, Set in Order, Shine, Standardize, Sustain
    """
    
    def __init__(self):
        """Initialize 5S analyzer"""
        self.criteria = {
            'sort': 'Remove unnecessary items',
            'set_in_order': 'Organize necessary items',
            'shine': 'Clean and inspect',
            'standardize': 'Create standards',
            'sustain': 'Maintain discipline'
        }
    
    def analyze_5s(self, image_path: str) -> Dict:
        """
        Analyze workplace organization using 5S principles
        
        Args:
            image_path: Path to workplace image
            
        Returns:
            Dictionary with 5S analysis
        """
        try:
            image = cv2.imread(image_path)
            
            # Analyze each S
            sort_score = self._analyze_sort(image)
            order_score = self._analyze_order(image)
            shine_score = self._analyze_shine(image)
            standardize_score = self._analyze_standardize(image)
            sustain_score = self._analyze_sustain(image)
            
            overall_score = np.mean([
                sort_score,
                order_score,
                shine_score,
                standardize_score,
                sustain_score
            ])
            
            return {
                'overall_score': float(overall_score),
                'scores': {
                    'sort': float(sort_score),
                    'set_in_order': float(order_score),
                    'shine': float(shine_score),
                    'standardize': float(standardize_score),
                    'sustain': float(sustain_score)
                },
                'grade': self._get_grade(overall_score),
                'recommendations': self._generate_5s_recommendations(
                    sort_score, order_score, shine_score,
                    standardize_score, sustain_score
                )
            }
        
        except Exception as e:
            logger.error(f"Error analyzing 5S: {str(e)}")
            return {
                'error': str(e),
                'overall_score': 0.0
            }
    
    def _analyze_sort(self, image: np.ndarray) -> float:
        """Analyze Sort (remove unnecessary items)"""
        # Placeholder - implement clutter detection
        return 0.75
    
    def _analyze_order(self, image: np.ndarray) -> float:
        """Analyze Set in Order (organize items)"""
        # Placeholder - implement organization detection
        return 0.70
    
    def _analyze_shine(self, image: np.ndarray) -> float:
        """Analyze Shine (cleanliness)"""
        # Placeholder - implement cleanliness detection
        return 0.80
    
    def _analyze_standardize(self, image: np.ndarray) -> float:
        """Analyze Standardize (create standards)"""
        # Placeholder - implement standardization detection
        return 0.65
    
    def _analyze_sustain(self, image: np.ndarray) -> float:
        """Analyze Sustain (maintain discipline)"""
        # Placeholder - requires historical data
        return 0.70
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _generate_5s_recommendations(
        self,
        sort: float,
        order: float,
        shine: float,
        standardize: float,
        sustain: float
    ) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if sort < 0.7:
            recommendations.append(
                "Remove unnecessary items and materials from work area"
            )
        if order < 0.7:
            recommendations.append(
                "Organize tools and materials in designated locations"
            )
        if shine < 0.7:
            recommendations.append(
                "Implement regular cleaning and inspection schedule"
            )
        if standardize < 0.7:
            recommendations.append(
                "Create and document standard operating procedures"
            )
        if sustain < 0.7:
            recommendations.append(
                "Establish regular audits and training programs"
            )
        
        return recommendations
