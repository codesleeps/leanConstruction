 """
Computer Vision Models for Construction Site Analysis - Phase 2 Enhanced
- Site progress monitoring (ResNet-50/101 based CNN with attention)
- Safety compliance detection (YOLO/Faster R-CNN)
- Equipment tracking and utilization
- 5S workplace assessment
- Temporal progress analysis
- Multi-scale feature extraction
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import logging
import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConstructionStage(Enum):
    """Construction stages for progress tracking"""
    SITE_PREPARATION = 0
    FOUNDATION = 1
    FRAMING = 2
    ROUGH_PLUMBING = 3
    ROUGH_ELECTRICAL = 4
    HVAC_INSTALLATION = 5
    INSULATION = 6
    DRYWALL = 7
    INTERIOR_FINISH = 8
    EXTERIOR_FINISH = 9
    LANDSCAPING = 10
    FINAL_INSPECTION = 11
    COMPLETE = 12


@dataclass
class ProgressPrediction:
    """Data class for progress prediction results"""
    stage: str
    stage_index: int
    confidence: float
    completion_percentage: float
    all_probabilities: Dict[str, float]
    feature_activations: Optional[np.ndarray] = None
    attention_map: Optional[np.ndarray] = None


@dataclass
class SafetyDetection:
    """Data class for safety detection results"""
    bbox: List[float]
    label: str
    confidence: float
    is_violation: bool
    severity: str


class AttentionModule(nn.Module):
    """
    Channel and spatial attention module for enhanced feature extraction
    Based on CBAM (Convolutional Block Attention Module)
    """
    
    def __init__(self, in_channels: int, reduction_ratio: int = 16):
        super(AttentionModule, self).__init__()
        
        # Channel attention
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        self.fc = nn.Sequential(
            nn.Linear(in_channels, in_channels // reduction_ratio, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(in_channels // reduction_ratio, in_channels, bias=False)
        )
        
        # Spatial attention
        self.conv_spatial = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with attention maps"""
        batch_size, channels, _, _ = x.size()
        
        # Channel attention
        avg_out = self.fc(self.avg_pool(x).view(batch_size, channels))
        max_out = self.fc(self.max_pool(x).view(batch_size, channels))
        channel_attention = self.sigmoid(avg_out + max_out).view(batch_size, channels, 1, 1)
        x = x * channel_attention
        
        # Spatial attention
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        spatial_input = torch.cat([avg_out, max_out], dim=1)
        spatial_attention = self.sigmoid(self.conv_spatial(spatial_input))
        x = x * spatial_attention
        
        return x, spatial_attention


class ProgressMonitoringModel(nn.Module):
    """
    Enhanced CNN-based model for monitoring construction site progress
    Based on ResNet architecture with attention mechanisms
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        num_classes: int = 13,
        backbone: str = 'resnet50',
        pretrained: bool = True,
        use_attention: bool = True,
        dropout_rate: float = 0.5
    ):
        """
        Initialize progress monitoring model
        
        Args:
            model_path: Path to pre-trained model weights
            num_classes: Number of progress stages to classify
            backbone: Backbone architecture (resnet50, resnet101)
            pretrained: Use ImageNet pretrained weights
            use_attention: Use attention mechanism
            dropout_rate: Dropout rate for regularization
        """
        super(ProgressMonitoringModel, self).__init__()
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.use_attention = use_attention
        
        # Load backbone
        if backbone == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            self.feature_dim = 2048
        elif backbone == 'resnet101':
            self.backbone = models.resnet101(pretrained=pretrained)
            self.feature_dim = 2048
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Remove the final FC layer
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-2])
        
        # Add attention module
        if use_attention:
            self.attention = AttentionModule(self.feature_dim)
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classification head with dropout
        self.classifier = nn.Sequential(
            nn.Linear(self.feature_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(256, num_classes)
        )
        
        # Move to device
        self.to(self.device)
        
        if model_path:
            self.load_weights(model_path)
        
        # Progress stages mapping
        self.stages = [stage.name.lower() for stage in ConstructionStage]
        
        # Image preprocessing with enhanced augmentation
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Training augmentation
        self.train_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Forward pass through the network"""
        # Extract features from backbone
        features = self.backbone(x)
        
        attention_map = None
        if self.use_attention:
            features, attention_map = self.attention(features)
        
        # Global pooling
        pooled = self.global_pool(features)
        pooled = pooled.view(pooled.size(0), -1)
        
        # Classification
        output = self.classifier(pooled)
        
        return output, attention_map
    
    def load_weights(self, model_path: str):
        """Load pre-trained weights"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.load_state_dict(checkpoint['model_state_dict'])
                logger.info(f"Loaded model from checkpoint: {model_path}")
            else:
                self.load_state_dict(checkpoint)
                logger.info(f"Loaded model weights from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model weights: {str(e)}")
    
    def save_checkpoint(
        self,
        save_path: str,
        optimizer: Optional[torch.optim.Optimizer] = None,
        epoch: int = 0,
        metrics: Optional[Dict] = None
    ):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'epoch': epoch,
            'num_classes': self.num_classes,
            'stages': self.stages,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if optimizer:
            checkpoint['optimizer_state_dict'] = optimizer.state_dict()
        
        if metrics:
            checkpoint['metrics'] = metrics
        
        torch.save(checkpoint, save_path)
        logger.info(f"Saved checkpoint to {save_path}")
    
    def predict_progress(
        self,
        image: Union[str, np.ndarray, Image.Image],
        return_attention: bool = False
    ) -> ProgressPrediction:
        """
        Predict construction progress from image
        
        Args:
            image: Path to image, numpy array, or PIL Image
            return_attention: Return attention maps for visualization
            
        Returns:
            ProgressPrediction object with detailed results
        """
        self.eval()
        
        try:
            # Handle different input types
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Preprocess
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs, attention_map = self(image_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            stage_idx = predicted.item()
            confidence_score = confidence.item()
            
            # Build probabilities dict
            probs_dict = {
                stage: prob.item()
                for stage, prob in zip(self.stages, probabilities[0])
            }
            
            return ProgressPrediction(
                stage=self.stages[stage_idx],
                stage_index=stage_idx,
                confidence=confidence_score,
                completion_percentage=(stage_idx / (len(self.stages) - 1)) * 100,
                all_probabilities=probs_dict,
                attention_map=attention_map.cpu().numpy() if attention_map is not None and return_attention else None
            )
        
        except Exception as e:
            logger.error(f"Error predicting progress: {str(e)}")
            return ProgressPrediction(
                stage='unknown',
                stage_index=-1,
                confidence=0.0,
                completion_percentage=0.0,
                all_probabilities={}
            )
    
    def analyze_progress_series(
        self,
        images: List[str],
        timestamps: Optional[List[datetime]] = None
    ) -> Dict:
        """
        Analyze a series of images to track progress over time
        
        Args:
            images: List of image paths
            timestamps: Optional list of timestamps for each image
            
        Returns:
            Dictionary with temporal progress analysis
        """
        predictions = []
        
        for i, img_path in enumerate(images):
            pred = self.predict_progress(img_path)
            predictions.append({
                'image': img_path,
                'timestamp': timestamps[i].isoformat() if timestamps else None,
                'stage': pred.stage,
                'stage_index': pred.stage_index,
                'confidence': pred.confidence,
                'completion_percentage': pred.completion_percentage
            })
        
        # Calculate progress metrics
        if len(predictions) >= 2:
            progress_rate = (
                predictions[-1]['stage_index'] - predictions[0]['stage_index']
            ) / len(predictions)
            
            # Detect stalls or regressions
            stalls = []
            regressions = []
            for i in range(1, len(predictions)):
                diff = predictions[i]['stage_index'] - predictions[i-1]['stage_index']
                if diff == 0:
                    stalls.append(i)
                elif diff < 0:
                    regressions.append(i)
        else:
            progress_rate = 0
            stalls = []
            regressions = []
        
        return {
            'predictions': predictions,
            'total_images': len(images),
            'progress_rate': progress_rate,
            'stall_points': stalls,
            'regression_points': regressions,
            'current_stage': predictions[-1]['stage'] if predictions else 'unknown',
            'overall_completion': predictions[-1]['completion_percentage'] if predictions else 0,
            'analysis_summary': self._generate_progress_summary(predictions, stalls, regressions)
        }
    
    def _generate_progress_summary(
        self,
        predictions: List[Dict],
        stalls: List[int],
        regressions: List[int]
    ) -> str:
        """Generate human-readable progress summary"""
        if not predictions:
            return "No progress data available"
        
        summary_parts = []
        
        # Current status
        current = predictions[-1]
        summary_parts.append(
            f"Current stage: {current['stage'].replace('_', ' ').title()} "
            f"({current['completion_percentage']:.1f}% complete)"
        )
        
        # Progress assessment
        if len(predictions) > 1:
            initial = predictions[0]
            stages_progressed = current['stage_index'] - initial['stage_index']
            
            if stages_progressed > 0:
                summary_parts.append(f"Progressed {stages_progressed} stages since baseline")
            elif stages_progressed == 0:
                summary_parts.append("No stage progression detected")
            else:
                summary_parts.append(f"Regression of {abs(stages_progressed)} stages detected")
        
        # Issues
        if stalls:
            summary_parts.append(f"Detected {len(stalls)} periods of stalled progress")
        if regressions:
            summary_parts.append(f"Warning: {len(regressions)} regression events detected")
        
        return ". ".join(summary_parts)


class ConstructionDataset(Dataset):
    """Custom dataset for construction site images"""
    
    def __init__(
        self,
        image_paths: List[str],
        labels: List[int],
        transform: Optional[transforms.Compose] = None
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        image = Image.open(self.image_paths[idx]).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class ModelTrainer:
    """Training pipeline for progress monitoring model"""
    
    def __init__(
        self,
        model: ProgressMonitoringModel,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4
    ):
        self.model = model
        self.device = model.device
        
        # Optimizer with different learning rates for backbone and head
        backbone_params = list(model.backbone.parameters())
        head_params = list(model.classifier.parameters())
        
        if model.use_attention:
            head_params += list(model.attention.parameters())
        
        self.optimizer = torch.optim.AdamW([
            {'params': backbone_params, 'lr': learning_rate * 0.1},
            {'params': head_params, 'lr': learning_rate}
        ], weight_decay=weight_decay)
        
        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # Loss function with label smoothing
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def train_epoch(self, dataloader: DataLoader) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            outputs, _ = self.model(images)
            loss = self.criterion(outputs, labels)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def validate(self, dataloader: DataLoader) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in dataloader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs, _ = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        checkpoint_dir: str = 'checkpoints',
        early_stopping_patience: int = 10
    ) -> Dict:
        """
        Full training loop with validation and checkpointing
        """
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validation
            val_loss, val_acc = self.validate(val_loader)
            
            # Update scheduler
            self.scheduler.step(val_loss)
            
            # Log progress
            logger.info(
                f"Epoch [{epoch+1}/{epochs}] "
                f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
            )
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            
            # Checkpointing
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                
                self.model.save_checkpoint(
                    os.path.join(checkpoint_dir, 'best_model.pt'),
                    self.optimizer,
                    epoch,
                    {'val_loss': val_loss, 'val_acc': val_acc}
                )
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break
            
            # Periodic checkpoint
            if (epoch + 1) % 10 == 0:
                self.model.save_checkpoint(
                    os.path.join(checkpoint_dir, f'checkpoint_epoch_{epoch+1}.pt'),
                    self.optimizer,
                    epoch
                )
        
        return self.history


class SafetyComplianceDetector:
    """
    Enhanced object detection model for safety compliance
    Detects PPE, hazards, and safety violations
    """
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """Initialize safety compliance detector"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = confidence_threshold
        
        # Load Faster R-CNN model
        self.model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        
        # Safety items classification
        self.safety_classes = {
            1: {'name': 'hard_hat', 'requirement': 'required'},
            2: {'name': 'safety_vest', 'requirement': 'required'},
            3: {'name': 'safety_boots', 'requirement': 'required'},
            4: {'name': 'gloves', 'requirement': 'recommended'},
            5: {'name': 'safety_glasses', 'requirement': 'required'},
            6: {'name': 'harness', 'requirement': 'required_at_height'},
            7: {'name': 'fire_extinguisher', 'requirement': 'site_required'},
            8: {'name': 'first_aid_kit', 'requirement': 'site_required'},
            9: {'name': 'warning_signs', 'requirement': 'site_required'},
            10: {'name': 'barriers', 'requirement': 'site_required'},
            11: {'name': 'person_no_ppe', 'requirement': 'violation'}
        }
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        if model_path:
            self._load_custom_weights(model_path)
    
    def _load_custom_weights(self, model_path: str):
        """Load custom trained weights"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Loaded safety model from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load custom weights: {e}. Using pretrained model.")
    
    def detect(self, image: Union[str, np.ndarray, Image.Image]) -> Dict:
        """
        Detect safety items and violations in image
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Handle different input types
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Transform to tensor
            image_tensor = transforms.ToTensor()(image).unsqueeze(0).to(self.device)
            
            # Run detection
            with torch.no_grad():
                predictions = self.model(image_tensor)
            
            # Process detections
            boxes = predictions[0]['boxes'].cpu().numpy()
            labels = predictions[0]['labels'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()
            
            # Filter by confidence
            mask = scores > self.confidence_threshold
            
            detections = []
            violations = []
            
            for box, label, score in zip(boxes[mask], labels[mask], scores[mask]):
                detection = SafetyDetection(
                    bbox=box.tolist(),
                    label=self._get_label_name(label),
                    confidence=float(score),
                    is_violation=self._is_violation(label),
                    severity=self._get_severity(label)
                )
                detections.append(detection)
                
                if detection.is_violation:
                    violations.append(detection)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(detections)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'detections': [vars(d) for d in detections],
                'violations': [vars(v) for v in violations],
                'total_detections': len(detections),
                'violation_count': len(violations),
                'compliance_score': compliance_score,
                'is_compliant': compliance_score >= 0.8,
                'risk_level': self._assess_risk_level(violations),
                'recommendations': self._generate_recommendations(detections, violations),
                'required_actions': self._get_required_actions(violations)
            }
        
        except Exception as e:
            logger.error(f"Error in safety detection: {str(e)}")
            return {
                'error': str(e),
                'detections': [],
                'compliance_score': 0.0
            }
    
    def _get_label_name(self, label: int) -> str:
        """Get label name from class ID"""
        if label in self.safety_classes:
            return self.safety_classes[label]['name']
        return f'unknown_{label}'
    
    def _is_violation(self, label: int) -> bool:
        """Check if detection represents a violation"""
        if label in self.safety_classes:
            return self.safety_classes[label]['requirement'] == 'violation'
        return False
    
    def _get_severity(self, label: int) -> str:
        """Get severity level for detection"""
        if label in self.safety_classes:
            req = self.safety_classes[label]['requirement']
            if req == 'violation':
                return 'high'
            elif req == 'required':
                return 'medium'
            else:
                return 'low'
        return 'unknown'
    
    def _calculate_compliance_score(self, detections: List[SafetyDetection]) -> float:
        """Calculate overall compliance score"""
        if not detections:
            return 0.5  # Unknown state
        
        violations = sum(1 for d in detections if d.is_violation)
        required_items = sum(
            1 for d in detections
            if not d.is_violation and d.severity in ['medium', 'high']
        )
        
        total_checks = violations + required_items
        if total_checks == 0:
            return 0.5
        
        return required_items / total_checks
    
    def _assess_risk_level(self, violations: List[SafetyDetection]) -> str:
        """Assess overall risk level"""
        if not violations:
            return 'low'
        
        high_severity_count = sum(1 for v in violations if v.severity == 'high')
        
        if high_severity_count >= 3:
            return 'critical'
        elif high_severity_count >= 1:
            return 'high'
        elif len(violations) >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(
        self,
        detections: List[SafetyDetection],
        violations: List[SafetyDetection]
    ) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        violation_types = set(v.label for v in violations)
        
        if 'person_no_ppe' in violation_types:
            recommendations.append(
                "Ensure all workers wear complete PPE including hard hat, safety vest, and boots"
            )
        
        # Check for missing required items
        detected_items = set(d.label for d in detections if not d.is_violation)
        required_items = {'hard_hat', 'safety_vest', 'safety_boots', 'safety_glasses'}
        missing = required_items - detected_items
        
        if missing:
            recommendations.append(
                f"Missing required safety items detected: {', '.join(missing)}"
            )
        
        if not recommendations:
            recommendations.append("Site appears to be in good safety compliance")
        
        return recommendations
    
    def _get_required_actions(self, violations: List[SafetyDetection]) -> List[Dict]:
        """Get required corrective actions"""
        actions = []
        
        for v in violations:
            action = {
                'violation': v.label,
                'severity': v.severity,
                'action': self._get_corrective_action(v.label),
                'deadline': 'immediate' if v.severity == 'high' else '24 hours'
            }
            actions.append(action)
        
        return actions
    
    def _get_corrective_action(self, violation_type: str) -> str:
        """Get corrective action for violation type"""
        actions = {
            'person_no_ppe': 'Stop work and ensure worker dons all required PPE',
            'missing_hard_hat': 'Provide and require hard hat usage',
            'missing_safety_vest': 'Provide high-visibility safety vest',
            'missing_harness': 'Worker at height must use fall protection'
        }
        return actions.get(violation_type, 'Review and correct safety violation')


class EquipmentTracker:
    """
    Enhanced equipment tracking and utilization analysis
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize equipment tracker"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Equipment types with hourly rates
        self.equipment_catalog = {
            'excavator': {'rate': 150, 'category': 'heavy'},
            'bulldozer': {'rate': 175, 'category': 'heavy'},
            'crane': {'rate': 300, 'category': 'heavy'},
            'forklift': {'rate': 75, 'category': 'light'},
            'concrete_mixer': {'rate': 100, 'category': 'medium'},
            'dump_truck': {'rate': 125, 'category': 'medium'},
            'scaffolding': {'rate': 50, 'category': 'static'},
            'generator': {'rate': 60, 'category': 'static'},
            'compactor': {'rate': 80, 'category': 'medium'},
            'loader': {'rate': 140, 'category': 'heavy'}
        }
        
        # Position history for movement tracking
        self.position_history: Dict[str, List[Dict]] = {}
    
    def track_equipment(
        self,
        image: Union[str, np.ndarray],
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Track equipment in construction site image
        
        Args:
            image: Input image
            timestamp: Optional timestamp for tracking
            
        Returns:
            Equipment tracking results
        """
        timestamp = timestamp or datetime.utcnow()
        
        try:
            # Load image
            if isinstance(image, str):
                img = cv2.imread(image)
            else:
                img = image
            
            # Detect equipment (placeholder for trained model)
            detected_equipment = self._detect_equipment(img)
            
            # Update position history
            self._update_position_history(detected_equipment, timestamp)
            
            # Calculate utilization metrics
            utilization_metrics = self._calculate_utilization(detected_equipment)
            
            # Cost analysis
            cost_analysis = self._analyze_costs(detected_equipment, utilization_metrics)
            
            return {
                'timestamp': timestamp.isoformat(),
                'detected_equipment': detected_equipment,
                'total_equipment': len(detected_equipment),
                'utilization_metrics': utilization_metrics,
                'cost_analysis': cost_analysis,
                'idle_equipment': [
                    eq for eq in detected_equipment
                    if eq.get('status') == 'idle'
                ],
                'active_equipment': [
                    eq for eq in detected_equipment
                    if eq.get('status') == 'active'
                ],
                'recommendations': self._generate_equipment_recommendations(
                    detected_equipment,
                    utilization_metrics
                )
            }
        
        except Exception as e:
            logger.error(f"Error tracking equipment: {str(e)}")
            return {'error': str(e), 'detected_equipment': []}
    
    def _detect_equipment(self, image: np.ndarray) -> List[Dict]:
        """
        Detect equipment in image
        In production, this would use a trained object detection model
        """
        # Placeholder implementation
        # Returns simulated detections for demonstration
        return []
    
    def _update_position_history(
        self,
        equipment: List[Dict],
        timestamp: datetime
    ):
        """Update position history for movement analysis"""
        for eq in equipment:
            eq_id = eq.get('id', 'unknown')
            if eq_id not in self.position_history:
                self.position_history[eq_id] = []
            
            self.position_history[eq_id].append({
                'timestamp': timestamp.isoformat(),
                'position': eq.get('position'),
                'status': eq.get('status')
            })
            
            # Keep only last 100 entries
            self.position_history[eq_id] = self.position_history[eq_id][-100:]
    
    def _calculate_utilization(self, equipment: List[Dict]) -> Dict:
        """Calculate equipment utilization metrics"""
        if not equipment:
            return {
                'overall_utilization': 0.0,
                'by_category': {},
                'by_equipment': {}
            }
        
        active_count = sum(1 for eq in equipment if eq.get('status') == 'active')
        overall_utilization = active_count / len(equipment)
        
        # By category
        by_category = {}
        for eq in equipment:
            eq_type = eq.get('type', 'unknown')
            category = self.equipment_catalog.get(eq_type, {}).get('category', 'unknown')
            
            if category not in by_category:
                by_category[category] = {'active': 0, 'total': 0}
            
            by_category[category]['total'] += 1
            if eq.get('status') == 'active':
                by_category[category]['active'] += 1
        
        for cat in by_category:
            by_category[cat]['utilization'] = (
                by_category[cat]['active'] / by_category[cat]['total']
                if by_category[cat]['total'] > 0 else 0
            )
        
        return {
            'overall_utilization': overall_utilization,
            'active_count': active_count,
            'idle_count': len(equipment) - active_count,
            'by_category': by_category
        }
    
    def _analyze_costs(
        self,
        equipment: List[Dict],
        utilization: Dict
    ) -> Dict:
        """Analyze equipment costs"""
        total_hourly_rate = 0
        active_hourly_rate = 0
        idle_cost = 0
        
        for eq in equipment:
            eq_type = eq.get('type', 'unknown')
            rate = self.equipment_catalog.get(eq_type, {}).get('rate', 0)
            total_hourly_rate += rate
            
            if eq.get('status') == 'active':
                active_hourly_rate += rate
            else:
                idle_cost += rate
        
        return {
            'total_hourly_rate': total_hourly_rate,
            'active_hourly_rate': active_hourly_rate,
            'idle_hourly_cost': idle_cost,
            'daily_idle_cost': idle_cost * 8,
            'efficiency_ratio': (
                active_hourly_rate / total_hourly_rate
                if total_hourly_rate > 0 else 0
            )
        }
    
    def _generate_equipment_recommendations(
        self,
        equipment: List[Dict],
        utilization: Dict
    ) -> List[str]:
        """Generate equipment utilization recommendations"""
        recommendations = []
        
        overall_util = utilization.get('overall_utilization', 0)
        
        if overall_util < 0.5:
            recommendations.append(
                f"Low equipment utilization ({overall_util:.1%}). "
                "Consider reducing equipment on site or reassigning to other projects."
            )
        
        # Check for consistently idle equipment
        idle_equipment = [eq for eq in equipment if eq.get('status') == 'idle']
        if len(idle_equipment) > 2:
            recommendations.append(
                f"{len(idle_equipment)} pieces of equipment are idle. "
                "Review scheduling and task allocation."
            )
        
        return recommendations


class WorkplaceOrganizationAnalyzer:
    """
    Enhanced 5S Workplace Organization Analysis
    Uses computer vision to assess Sort, Set in Order, Shine, Standardize, Sustain
    """
    
    def __init__(self):
        """Initialize 5S analyzer"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.criteria = {
            'sort': {
                'description': 'Remove unnecessary items',
                'weight': 0.2,
                'indicators': ['clutter_level', 'unnecessary_items', 'red_tag_items']
            },
            'set_in_order': {
                'description': 'Organize necessary items',
                'weight': 0.2,
                'indicators': ['tool_organization', 'material_staging', 'clear_pathways']
            },
            'shine': {
                'description': 'Clean and inspect',
                'weight': 0.2,
                'indicators': ['cleanliness', 'debris_level', 'equipment_condition']
            },
            'standardize': {
                'description': 'Create and follow standards',
                'weight': 0.2,
                'indicators': ['signage_present', 'marking_visible', 'zones_defined']
            },
            'sustain': {
                'description': 'Maintain discipline',
                'weight': 0.2,
                'indicators': ['consistency', 'improvement_trend', 'audit_compliance']
            }
        }
        
        # Historical scores for trend analysis
        self.score_history: List[Dict] = []
    
    def analyze(
        self,
        image: Union[str, np.ndarray],
        previous_scores: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze workplace organization using 5S principles
        
        Args:
            image: Input image
            previous_scores: Previous analysis for trend comparison
            
        Returns:
            Comprehensive 5S analysis results
        """
        try:
            # Load image
            if isinstance(image, str):
                img = cv2.imread(image)
            else:
                img = image
            
            # Analyze each S
            scores = {
                'sort': self._analyze_sort(img),
                'set_in_order': self._analyze_order(img),
                'shine': self._analyze_shine(img),
                'standardize': self._analyze_standardize(img),
                'sustain': self._analyze_sustain(img, previous_scores)
            }
            
            # Calculate weighted overall score
            overall_score = sum(
                scores[s] * self.criteria[s]['weight']
                for s in scores
            )
            
            # Generate grade
            grade = self._get_grade(overall_score)
            
            # Track history
            analysis_result = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_score': float(overall_score),
                'grade': grade,
                'scores': {k: float(v) for k, v in scores.items()},
                'score_breakdown': self._get_score_breakdown(scores),
                'trend': self._calculate_trend(scores),
                'recommendations': self._generate_recommendations(scores),
                'priority_improvements': self._get_priority_improvements(scores),
                'certification_status': self._get_certification_status(overall_score, scores)
            }
            
            self.score_history.append(analysis_result)
            
            return analysis_result
        
        except Exception as e:
            logger.error(f"Error in 5S analysis: {str(e)}")
            return {'error': str(e), 'overall_score': 0.0}
    
    def _analyze_sort(self, image: np.ndarray) -> float:
        """
        Analyze Sort (Seiri) - Remove unnecessary items
        Uses clutter detection and object density analysis
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection for clutter assessment
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # High edge density may indicate clutter
        # Normalize to 0-1 score where lower density is better
        clutter_score = max(0, 1 - (edge_density * 10))
        
        return clutter_score
    
    def _analyze_order(self, image: np.ndarray) -> float:
        """
        Analyze Set in Order (Seiton) - Organize items
        Looks for organized patterns and clear pathways
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect lines (indicates organization)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
        
        # More straight lines may indicate better organization
        line_count = len(lines) if lines is not None else 0
        organization_score = min(line_count / 50, 1.0)
        
        return organization_score
    
    def _analyze_shine(self, image: np.ndarray) -> float:
        """
        Analyze Shine (Seiso) - Cleanliness
        Assesses overall cleanliness and debris levels
        """
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Check for dirt/debris colors (browns, grays)
        lower_debris = np.array([0, 0, 50])
        upper_debris = np.array([30, 255, 150])
        debris_mask = cv2.inRange(hsv, lower_debris, upper_debris)
        
        debris_percentage = np.sum(debris_mask > 0) / debris_mask.size
        
        # Lower debris percentage = cleaner = higher score
        cleanliness_score = max(0, 1 - (debris_percentage * 5))
        
        return cleanliness_score
    
    def _analyze_standardize(self, image: np.ndarray) -> float:
        """
        Analyze Standardize (Seiketsu) - Create standards
        Looks for signage, markings, and defined zones
        """
        # Look for bright colors (often used in signage)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Yellow (warning signs)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Red (danger/stop signs)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Green (safety/go signs)
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        total_signage = (
            np.sum(yellow_mask > 0) +
            np.sum(red_mask > 0) +
            np.sum(green_mask > 0)
        )
        
        signage_percentage = total_signage / image.size
        
        # Some signage is good, but not too much
        standardize_score = min(signage_percentage * 100, 1.0)
        
        return standardize_score
    
    def _analyze_sustain(
        self,
        image: np.ndarray,
        previous_scores: Optional[Dict]
    ) -> float:
        """
        Analyze Sustain (Shitsuke) - Maintain discipline
        Compares with historical data for consistency
        """
        # Base score from current image quality
        base_score = 0.7
        
        # If we have historical data, check for consistency
        if self.score_history:
            recent_scores = [h['overall_score'] for h in self.score_history[-5:]]
            if recent_scores:
                consistency = 1 - np.std(recent_scores)
                base_score = (base_score + consistency) / 2
        
        # Check for improvement trend
        if previous_scores:
            current_avg = np.mean([
                self._analyze_sort(image),
                self._analyze_order(image),
                self._analyze_shine(image),
                self._analyze_standardize(image)
            ])
            previous_avg = np.mean([
                previous_scores.get('sort', 0.5),
                previous_scores.get('set_in_order', 0.5),
                previous_scores.get('shine', 0.5),
                previous_scores.get('standardize', 0.5)
            ])
            
            if current_avg >= previous_avg:
                base_score = min(base_score + 0.1, 1.0)
        
        return base_score
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.85:
            return 'A'
        elif score >= 0.8:
            return 'B+'
        elif score >= 0.75:
            return 'B'
        elif score >= 0.7:
            return 'C+'
        elif score >= 0.65:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _get_score_breakdown(self, scores: Dict[str, float]) -> List[Dict]:
        """Get detailed score breakdown"""
        breakdown = []
        for s, score in scores.items():
            breakdown.append({
                'category': s,
                'score': score,
                'grade': self._get_grade(score),
                'description': self.criteria[s]['description'],
                'status': 'pass' if score >= 0.7 else 'needs_improvement'
            })
        return breakdown
    
    def _calculate_trend(self, current_scores: Dict[str, float]) -> Dict:
        """Calculate trend compared to historical data"""
        if len(self.score_history) < 2:
            return {'direction': 'insufficient_data', 'change': 0}
        
        previous = self.score_history[-2]
        current_avg = np.mean(list(current_scores.values()))
        previous_avg = np.mean(list(previous['scores'].values()))
        
        change = current_avg - previous_avg
        
        return {
            'direction': 'improving' if change > 0 else 'declining' if change < 0 else 'stable',
            'change_percentage': change * 100,
            'consecutive_improvements': self._count_consecutive_improvements()
        }
    
    def _count_consecutive_improvements(self) -> int:
        """Count consecutive improvement periods"""
        if len(self.score_history) < 2:
            return 0
        
        count = 0
        for i in range(len(self.score_history) - 1, 0, -1):
            if self.score_history[i]['overall_score'] > self.score_history[i-1]['overall_score']:
                count += 1
            else:
                break
        
        return count
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate detailed recommendations"""
        recommendations = []
        
        for s, score in scores.items():
            if score < 0.7:
                if s == 'sort':
                    recommendations.append(
                        "Sort: Remove unnecessary items. Conduct red-tag exercise to identify "
                        "items that should be removed, relocated, or disposed of."
                    )
                elif s == 'set_in_order':
                    recommendations.append(
                        "Set in Order: Organize tools and materials. Use shadow boards, "
                        "labeled containers, and designated storage areas."
                    )
                elif s == 'shine':
                    recommendations.append(
                        "Shine: Implement daily cleaning routine. Remove debris and ensure "
                        "equipment is properly maintained."
                    )
                elif s == 'standardize':
                    recommendations.append(
                        "Standardize: Create visual standards. Add signage, floor markings, "
                        "and documented procedures."
                    )
                elif s == 'sustain':
                    recommendations.append(
                        "Sustain: Establish regular audits and training. Create accountability "
                        "systems and celebrate improvements."
                    )
        
        if not recommendations:
            recommendations.append(
                "Excellent workplace organization! Continue current practices and "
                "look for continuous improvement opportunities."
            )
        
        return recommendations
    
    def _get_priority_improvements(self, scores: Dict[str, float]) -> List[Dict]:
        """Get prioritized improvement actions"""
        improvements = []
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for s, score in sorted_scores:
            if score < 0.7:
                improvements.append({
                    'category': s,
                    'current_score': score,
                    'target_score': 0.8,
                    'priority': 'high' if score < 0.5 else 'medium',
                    'estimated_effort': 'high' if s in ['sort', 'set_in_order'] else 'medium'
                })
        
        return improvements[:3]  # Top 3 priorities
    
    def _get_certification_status(
        self,
        overall_score: float,
        scores: Dict[str, float]
    ) -> Dict:
        """Determine 5S certification status"""
        min_score = min(scores.values())
        
        if overall_score >= 0.9 and min_score >= 0.8:
            level = 'gold'
            certified = True
        elif overall_score >= 0.8 and min_score >= 0.7:
            level = 'silver'
            certified = True
        elif overall_score >= 0.7 and min_score >= 0.6:
            level = 'bronze'
            certified = True
        else:
            level = 'none'
            certified = False
        
        return {
            'certified': certified,
            'level': level,
            'overall_score': overall_score,
            'minimum_category_score': min_score,
            'requirements_met': {
                s: score >= 0.6 for s, score in scores.items()
            }
        }
