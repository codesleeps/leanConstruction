"""
Model Fine-tuning System for Lean Construction AI

This module provides real-world feedback collection and model retraining capabilities:
- Feedback collection and storage
- Performance monitoring
- Automated retraining triggers
- A/B testing for model versions
- Model versioning and rollback
- Transfer learning for domain adaptation
"""

import uuid
import hashlib
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from abc import ABC, abstractmethod


# ============================================
# Enums and Data Classes
# ============================================

class FeedbackType(Enum):
    """Types of user feedback"""
    CORRECTION = "correction"  # User corrected model output
    RATING = "rating"  # User rated quality (1-5)
    APPROVAL = "approval"  # User approved/rejected
    ANNOTATION = "annotation"  # User provided detailed annotation
    PREFERENCE = "preference"  # User preferred one output over another


class ModelType(Enum):
    """Types of ML models in the system"""
    PROGRESS_MONITORING = "progress_monitoring"
    SAFETY_DETECTION = "safety_detection"
    WASTE_DETECTION = "waste_detection"
    SCHEDULE_FORECASTING = "schedule_forecasting"
    COST_PREDICTION = "cost_prediction"
    DOCUMENT_CLASSIFICATION = "document_classification"
    ENTITY_RECOGNITION = "entity_recognition"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    RESOURCE_OPTIMIZATION = "resource_optimization"


class TrainingStatus(Enum):
    """Status of training jobs"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelStatus(Enum):
    """Status of model versions"""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATION = "validation"
    CHAMPION = "champion"  # Currently deployed best model
    CHALLENGER = "challenger"  # A/B test candidate
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class Feedback:
    """User feedback on model predictions"""
    id: str
    model_type: ModelType
    model_version: str
    input_data: Dict[str, Any]
    original_prediction: Any
    feedback_type: FeedbackType
    feedback_value: Any  # Correction, rating, etc.
    user_id: str
    project_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_training_sample(self) -> Dict[str, Any]:
        """Convert feedback to training sample"""
        return {
            'input': self.input_data,
            'target': self.feedback_value if self.feedback_type == FeedbackType.CORRECTION else self.original_prediction,
            'weight': self._calculate_weight(),
            'source': 'feedback',
            'feedback_id': self.id
        }
    
    def _calculate_weight(self) -> float:
        """Calculate sample weight based on feedback type and quality"""
        weights = {
            FeedbackType.CORRECTION: 1.5,  # Corrections are highly valuable
            FeedbackType.ANNOTATION: 1.3,
            FeedbackType.PREFERENCE: 1.2,
            FeedbackType.APPROVAL: 1.0,
            FeedbackType.RATING: 0.8
        }
        return weights.get(self.feedback_type, 1.0)


@dataclass
class ModelVersion:
    """Version information for a model"""
    id: str
    model_type: ModelType
    version: str
    status: ModelStatus
    created_at: datetime
    trained_at: Optional[datetime]
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    training_data_hash: str
    parent_version: Optional[str]
    changelog: str
    model_path: Optional[str] = None
    
    def is_deployable(self) -> bool:
        """Check if model version can be deployed"""
        required_metrics = ['accuracy', 'precision', 'recall']
        return (
            self.status in [ModelStatus.VALIDATION, ModelStatus.CHAMPION, ModelStatus.CHALLENGER] and
            all(metric in self.metrics for metric in required_metrics) and
            self.metrics.get('accuracy', 0) > 0.7  # Minimum threshold
        )


@dataclass
class TrainingJob:
    """Training job configuration and status"""
    id: str
    model_type: ModelType
    status: TrainingStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    config: Dict[str, Any]
    output_version_id: Optional[str]
    metrics: Dict[str, float]
    logs: List[str]
    error: Optional[str] = None


@dataclass
class ABTest:
    """A/B test configuration"""
    id: str
    name: str
    model_type: ModelType
    champion_version: str
    challenger_version: str
    start_date: datetime
    end_date: Optional[datetime]
    traffic_split: float  # Percentage going to challenger (0-100)
    min_samples: int
    status: str  # 'running', 'completed', 'stopped'
    results: Dict[str, Any] = field(default_factory=dict)


# ============================================
# Feedback Collection System
# ============================================

class FeedbackCollector:
    """Collects and manages user feedback on model predictions"""
    
    def __init__(self):
        self.feedback_store: Dict[str, Feedback] = {}
        self.feedback_by_model: Dict[ModelType, List[str]] = defaultdict(list)
        self.feedback_by_user: Dict[str, List[str]] = defaultdict(list)
        self.feedback_by_project: Dict[str, List[str]] = defaultdict(list)
    
    def submit_feedback(
        self,
        model_type: ModelType,
        model_version: str,
        input_data: Dict[str, Any],
        original_prediction: Any,
        feedback_type: FeedbackType,
        feedback_value: Any,
        user_id: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """Submit new feedback"""
        feedback = Feedback(
            id=str(uuid.uuid4()),
            model_type=model_type,
            model_version=model_version,
            input_data=input_data,
            original_prediction=original_prediction,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            user_id=user_id,
            project_id=project_id,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.feedback_store[feedback.id] = feedback
        self.feedback_by_model[model_type].append(feedback.id)
        self.feedback_by_user[user_id].append(feedback.id)
        if project_id:
            self.feedback_by_project[project_id].append(feedback.id)
        
        return feedback
    
    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID"""
        return self.feedback_store.get(feedback_id)
    
    def get_feedback_for_model(
        self,
        model_type: ModelType,
        since: Optional[datetime] = None,
        feedback_types: Optional[List[FeedbackType]] = None
    ) -> List[Feedback]:
        """Get all feedback for a model type"""
        feedback_ids = self.feedback_by_model.get(model_type, [])
        feedbacks = [self.feedback_store[fid] for fid in feedback_ids]
        
        if since:
            feedbacks = [f for f in feedbacks if f.timestamp >= since]
        
        if feedback_types:
            feedbacks = [f for f in feedbacks if f.feedback_type in feedback_types]
        
        return feedbacks
    
    def get_training_samples(
        self,
        model_type: ModelType,
        min_samples: int = 100
    ) -> List[Dict[str, Any]]:
        """Get feedback as training samples"""
        feedbacks = self.get_feedback_for_model(
            model_type,
            feedback_types=[FeedbackType.CORRECTION, FeedbackType.ANNOTATION]
        )
        
        if len(feedbacks) < min_samples:
            return []
        
        return [f.to_training_sample() for f in feedbacks]
    
    def get_statistics(self, model_type: Optional[ModelType] = None) -> Dict[str, Any]:
        """Get feedback statistics"""
        if model_type:
            feedbacks = self.get_feedback_for_model(model_type)
        else:
            feedbacks = list(self.feedback_store.values())
        
        if not feedbacks:
            return {'total': 0}
        
        by_type = defaultdict(int)
        ratings = []
        
        for f in feedbacks:
            by_type[f.feedback_type.value] += 1
            if f.feedback_type == FeedbackType.RATING:
                ratings.append(f.feedback_value)
        
        return {
            'total': len(feedbacks),
            'by_type': dict(by_type),
            'average_rating': np.mean(ratings) if ratings else None,
            'unique_users': len(set(f.user_id for f in feedbacks)),
            'unique_projects': len(set(f.project_id for f in feedbacks if f.project_id)),
            'date_range': {
                'start': min(f.timestamp for f in feedbacks).isoformat(),
                'end': max(f.timestamp for f in feedbacks).isoformat()
            }
        }


# ============================================
# Model Performance Monitor
# ============================================

class PerformanceMonitor:
    """Monitors model performance in production"""
    
    def __init__(self):
        self.predictions: Dict[str, List[Dict]] = defaultdict(list)  # By model
        self.metrics_history: Dict[str, List[Dict]] = defaultdict(list)
        self.alerts: List[Dict] = []
        self.thresholds = {
            'accuracy_drop': 0.05,  # Alert if accuracy drops by 5%
            'latency_increase': 0.5,  # Alert if latency increases by 50%
            'error_rate': 0.01,  # Alert if error rate exceeds 1%
            'drift_score': 0.3  # Alert if data drift score exceeds 0.3
        }
    
    def record_prediction(
        self,
        model_type: ModelType,
        model_version: str,
        input_data: Dict[str, Any],
        prediction: Any,
        latency_ms: float,
        confidence: Optional[float] = None,
        ground_truth: Optional[Any] = None
    ):
        """Record a prediction for monitoring"""
        record = {
            'id': str(uuid.uuid4()),
            'model_version': model_version,
            'timestamp': datetime.utcnow().isoformat(),
            'input_hash': hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:8],
            'prediction': prediction,
            'confidence': confidence,
            'latency_ms': latency_ms,
            'ground_truth': ground_truth,
            'correct': prediction == ground_truth if ground_truth is not None else None
        }
        
        self.predictions[f"{model_type.value}:{model_version}"].append(record)
        
        # Check for alerts
        self._check_alerts(model_type, model_version)
    
    def compute_metrics(
        self,
        model_type: ModelType,
        model_version: str,
        window_hours: int = 24
    ) -> Dict[str, float]:
        """Compute metrics for a model version"""
        key = f"{model_type.value}:{model_version}"
        records = self.predictions.get(key, [])
        
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent = [r for r in records if datetime.fromisoformat(r['timestamp']) >= cutoff]
        
        if not recent:
            return {}
        
        metrics = {
            'total_predictions': len(recent),
            'avg_latency_ms': np.mean([r['latency_ms'] for r in recent]),
            'p95_latency_ms': np.percentile([r['latency_ms'] for r in recent], 95),
            'avg_confidence': np.mean([r['confidence'] for r in recent if r['confidence'] is not None]) or 0
        }
        
        # Accuracy if ground truth available
        with_truth = [r for r in recent if r['ground_truth'] is not None]
        if with_truth:
            correct = sum(1 for r in with_truth if r['correct'])
            metrics['accuracy'] = correct / len(with_truth)
        
        return metrics
    
    def detect_data_drift(
        self,
        model_type: ModelType,
        model_version: str,
        reference_window_days: int = 30,
        comparison_window_days: int = 7
    ) -> Dict[str, Any]:
        """Detect data drift between reference and recent data"""
        key = f"{model_type.value}:{model_version}"
        records = self.predictions.get(key, [])
        
        if len(records) < 100:
            return {'drift_detected': False, 'reason': 'Insufficient data'}
        
        now = datetime.utcnow()
        reference_cutoff = now - timedelta(days=reference_window_days)
        comparison_cutoff = now - timedelta(days=comparison_window_days)
        
        reference = [r for r in records if datetime.fromisoformat(r['timestamp']) >= reference_cutoff 
                    and datetime.fromisoformat(r['timestamp']) < comparison_cutoff]
        comparison = [r for r in records if datetime.fromisoformat(r['timestamp']) >= comparison_cutoff]
        
        if len(reference) < 50 or len(comparison) < 50:
            return {'drift_detected': False, 'reason': 'Insufficient data in windows'}
        
        # Compare confidence distributions
        ref_conf = [r['confidence'] for r in reference if r['confidence'] is not None]
        comp_conf = [r['confidence'] for r in comparison if r['confidence'] is not None]
        
        if ref_conf and comp_conf:
            # Simple drift score based on mean shift
            drift_score = abs(np.mean(ref_conf) - np.mean(comp_conf)) / (np.std(ref_conf) + 0.001)
            
            return {
                'drift_detected': drift_score > self.thresholds['drift_score'],
                'drift_score': drift_score,
                'reference_mean_confidence': np.mean(ref_conf),
                'comparison_mean_confidence': np.mean(comp_conf),
                'recommendation': 'Consider retraining' if drift_score > self.thresholds['drift_score'] else 'No action needed'
            }
        
        return {'drift_detected': False, 'reason': 'No confidence scores available'}
    
    def _check_alerts(self, model_type: ModelType, model_version: str):
        """Check for alert conditions"""
        metrics = self.compute_metrics(model_type, model_version, window_hours=1)
        
        if not metrics:
            return
        
        # Check latency
        if 'p95_latency_ms' in metrics and metrics['p95_latency_ms'] > 1000:
            self._create_alert(
                model_type, model_version,
                'high_latency',
                f"High latency detected: {metrics['p95_latency_ms']:.0f}ms p95"
            )
        
        # Check accuracy drop
        if 'accuracy' in metrics and metrics['accuracy'] < 0.7:
            self._create_alert(
                model_type, model_version,
                'low_accuracy',
                f"Low accuracy detected: {metrics['accuracy']:.2%}"
            )
    
    def _create_alert(
        self,
        model_type: ModelType,
        model_version: str,
        alert_type: str,
        message: str
    ):
        """Create a performance alert"""
        self.alerts.append({
            'id': str(uuid.uuid4()),
            'model_type': model_type.value,
            'model_version': model_version,
            'alert_type': alert_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'acknowledged': False
        })
    
    def get_alerts(
        self,
        model_type: Optional[ModelType] = None,
        acknowledged: Optional[bool] = None
    ) -> List[Dict]:
        """Get performance alerts"""
        alerts = self.alerts
        
        if model_type:
            alerts = [a for a in alerts if a['model_type'] == model_type.value]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a['acknowledged'] == acknowledged]
        
        return alerts


# ============================================
# Model Version Manager
# ============================================

class ModelVersionManager:
    """Manages model versions and lifecycle"""
    
    def __init__(self):
        self.versions: Dict[str, ModelVersion] = {}
        self.versions_by_type: Dict[ModelType, List[str]] = defaultdict(list)
        self.champion_versions: Dict[ModelType, str] = {}
    
    def create_version(
        self,
        model_type: ModelType,
        version: str,
        hyperparameters: Dict[str, Any],
        training_data_hash: str,
        parent_version: Optional[str] = None,
        changelog: str = ""
    ) -> ModelVersion:
        """Create a new model version"""
        version_obj = ModelVersion(
            id=str(uuid.uuid4()),
            model_type=model_type,
            version=version,
            status=ModelStatus.DRAFT,
            created_at=datetime.utcnow(),
            trained_at=None,
            metrics={},
            hyperparameters=hyperparameters,
            training_data_hash=training_data_hash,
            parent_version=parent_version,
            changelog=changelog
        )
        
        self.versions[version_obj.id] = version_obj
        self.versions_by_type[model_type].append(version_obj.id)
        
        return version_obj
    
    def update_metrics(self, version_id: str, metrics: Dict[str, float]):
        """Update metrics for a version"""
        if version_id in self.versions:
            self.versions[version_id].metrics.update(metrics)
    
    def set_status(self, version_id: str, status: ModelStatus):
        """Update version status"""
        if version_id in self.versions:
            old_status = self.versions[version_id].status
            self.versions[version_id].status = status
            
            # Update champion if needed
            if status == ModelStatus.CHAMPION:
                model_type = self.versions[version_id].model_type
                # Demote current champion
                if model_type in self.champion_versions:
                    old_champion = self.champion_versions[model_type]
                    if old_champion != version_id:
                        self.versions[old_champion].status = ModelStatus.ARCHIVED
                self.champion_versions[model_type] = version_id
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get version by ID"""
        return self.versions.get(version_id)
    
    def get_champion(self, model_type: ModelType) -> Optional[ModelVersion]:
        """Get champion version for a model type"""
        version_id = self.champion_versions.get(model_type)
        return self.versions.get(version_id) if version_id else None
    
    def get_versions(
        self,
        model_type: ModelType,
        status: Optional[ModelStatus] = None
    ) -> List[ModelVersion]:
        """Get all versions for a model type"""
        version_ids = self.versions_by_type.get(model_type, [])
        versions = [self.versions[vid] for vid in version_ids]
        
        if status:
            versions = [v for v in versions if v.status == status]
        
        return sorted(versions, key=lambda v: v.created_at, reverse=True)
    
    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """Compare two model versions"""
        v1 = self.versions.get(version_id_1)
        v2 = self.versions.get(version_id_2)
        
        if not v1 or not v2:
            return {'error': 'Version not found'}
        
        if v1.model_type != v2.model_type:
            return {'error': 'Cannot compare different model types'}
        
        metrics_comparison = {}
        all_metrics = set(v1.metrics.keys()) | set(v2.metrics.keys())
        
        for metric in all_metrics:
            m1 = v1.metrics.get(metric)
            m2 = v2.metrics.get(metric)
            
            if m1 is not None and m2 is not None:
                diff = m2 - m1
                pct_change = (diff / m1 * 100) if m1 != 0 else 0
                better = diff > 0 if metric in ['accuracy', 'precision', 'recall', 'f1'] else diff < 0
                
                metrics_comparison[metric] = {
                    'version_1': m1,
                    'version_2': m2,
                    'difference': diff,
                    'percent_change': pct_change,
                    'better': better
                }
        
        return {
            'version_1': {
                'id': v1.id,
                'version': v1.version,
                'created_at': v1.created_at.isoformat()
            },
            'version_2': {
                'id': v2.id,
                'version': v2.version,
                'created_at': v2.created_at.isoformat()
            },
            'metrics_comparison': metrics_comparison,
            'hyperparameter_changes': {
                k: {'old': v1.hyperparameters.get(k), 'new': v2.hyperparameters.get(k)}
                for k in set(v1.hyperparameters.keys()) | set(v2.hyperparameters.keys())
                if v1.hyperparameters.get(k) != v2.hyperparameters.get(k)
            }
        }


# ============================================
# Training Pipeline
# ============================================

class TrainingPipeline:
    """Manages model training jobs"""
    
    def __init__(self, version_manager: ModelVersionManager):
        self.version_manager = version_manager
        self.jobs: Dict[str, TrainingJob] = {}
        self.job_queue: List[str] = []
    
    def create_training_job(
        self,
        model_type: ModelType,
        training_data: List[Dict[str, Any]],
        hyperparameters: Optional[Dict[str, Any]] = None,
        parent_version_id: Optional[str] = None
    ) -> TrainingJob:
        """Create a new training job"""
        # Compute data hash
        data_hash = hashlib.md5(
            json.dumps(training_data, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        
        # Get default hyperparameters
        default_params = self._get_default_hyperparameters(model_type)
        if hyperparameters:
            default_params.update(hyperparameters)
        
        # Create version
        parent = self.version_manager.get_version(parent_version_id) if parent_version_id else None
        parent_version = parent.version if parent else None
        
        # Auto-increment version
        existing = self.version_manager.get_versions(model_type)
        if existing:
            latest = existing[0].version
            major, minor, patch = map(int, latest.split('.'))
            new_version = f"{major}.{minor}.{patch + 1}"
        else:
            new_version = "1.0.0"
        
        version = self.version_manager.create_version(
            model_type=model_type,
            version=new_version,
            hyperparameters=default_params,
            training_data_hash=data_hash,
            parent_version=parent_version_id,
            changelog=f"Training job created at {datetime.utcnow().isoformat()}"
        )
        
        job = TrainingJob(
            id=str(uuid.uuid4()),
            model_type=model_type,
            status=TrainingStatus.PENDING,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            config={
                'hyperparameters': default_params,
                'data_hash': data_hash,
                'data_samples': len(training_data)
            },
            output_version_id=version.id,
            metrics={},
            logs=[]
        )
        
        self.jobs[job.id] = job
        self.job_queue.append(job.id)
        
        return job
    
    def run_training_job(self, job_id: str) -> TrainingJob:
        """Execute a training job (simulated for demo)"""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = TrainingStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.logs.append(f"[{datetime.utcnow().isoformat()}] Training started")
        
        try:
            # Simulate training process
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Loading data...")
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Data samples: {job.config['data_samples']}")
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Initializing model...")
            
            # Simulate training epochs
            for epoch in range(1, 6):
                loss = 0.5 / epoch + np.random.uniform(0, 0.1)
                acc = 0.7 + 0.05 * epoch + np.random.uniform(-0.02, 0.02)
                job.logs.append(f"[{datetime.utcnow().isoformat()}] Epoch {epoch}/5 - Loss: {loss:.4f}, Accuracy: {acc:.4f}")
            
            # Final metrics
            job.metrics = {
                'accuracy': 0.85 + np.random.uniform(-0.05, 0.05),
                'precision': 0.83 + np.random.uniform(-0.05, 0.05),
                'recall': 0.82 + np.random.uniform(-0.05, 0.05),
                'f1': 0.825 + np.random.uniform(-0.05, 0.05),
                'loss': 0.15 + np.random.uniform(0, 0.05),
                'training_time_seconds': np.random.uniform(60, 300)
            }
            
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Training completed")
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Final metrics: {json.dumps(job.metrics)}")
            
            # Update version
            if job.output_version_id:
                self.version_manager.update_metrics(job.output_version_id, job.metrics)
                self.version_manager.set_status(job.output_version_id, ModelStatus.VALIDATION)
            
            job.status = TrainingStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.error = str(e)
            job.logs.append(f"[{datetime.utcnow().isoformat()}] Training failed: {e}")
        
        return job
    
    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job by ID"""
        return self.jobs.get(job_id)
    
    def get_pending_jobs(self) -> List[TrainingJob]:
        """Get pending training jobs"""
        return [self.jobs[jid] for jid in self.job_queue 
                if self.jobs[jid].status == TrainingStatus.PENDING]
    
    def _get_default_hyperparameters(self, model_type: ModelType) -> Dict[str, Any]:
        """Get default hyperparameters for model type"""
        defaults = {
            ModelType.PROGRESS_MONITORING: {
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 50,
                'backbone': 'resnet50',
                'optimizer': 'adam'
            },
            ModelType.SAFETY_DETECTION: {
                'learning_rate': 0.001,
                'batch_size': 16,
                'epochs': 30,
                'confidence_threshold': 0.5
            },
            ModelType.WASTE_DETECTION: {
                'contamination': 0.1,
                'n_estimators': 100,
                'max_features': 'auto'
            },
            ModelType.SCHEDULE_FORECASTING: {
                'hidden_size': 128,
                'num_layers': 2,
                'dropout': 0.2,
                'sequence_length': 30
            },
            ModelType.COST_PREDICTION: {
                'n_estimators': 100,
                'max_depth': 10,
                'learning_rate': 0.1
            },
            ModelType.DOCUMENT_CLASSIFICATION: {
                'model_name': 'bert-base-uncased',
                'max_length': 512,
                'learning_rate': 2e-5,
                'epochs': 3
            }
        }
        
        return defaults.get(model_type, {})


# ============================================
# A/B Testing System
# ============================================

class ABTestManager:
    """Manages A/B tests for model versions"""
    
    def __init__(self, version_manager: ModelVersionManager):
        self.version_manager = version_manager
        self.tests: Dict[str, ABTest] = {}
        self.active_tests: Dict[ModelType, str] = {}  # One active test per model type
        self.test_results: Dict[str, List[Dict]] = defaultdict(list)
    
    def create_test(
        self,
        name: str,
        model_type: ModelType,
        challenger_version_id: str,
        traffic_split: float = 10.0,
        min_samples: int = 1000,
        duration_days: int = 7
    ) -> ABTest:
        """Create a new A/B test"""
        champion = self.version_manager.get_champion(model_type)
        if not champion:
            raise ValueError(f"No champion model for {model_type.value}")
        
        challenger = self.version_manager.get_version(challenger_version_id)
        if not challenger:
            raise ValueError(f"Challenger version {challenger_version_id} not found")
        
        if challenger.model_type != model_type:
            raise ValueError("Challenger must be same model type as champion")
        
        test = ABTest(
            id=str(uuid.uuid4()),
            name=name,
            model_type=model_type,
            champion_version=champion.id,
            challenger_version=challenger_version_id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration_days),
            traffic_split=traffic_split,
            min_samples=min_samples,
            status='running'
        )
        
        self.tests[test.id] = test
        self.active_tests[model_type] = test.id
        
        # Update challenger status
        self.version_manager.set_status(challenger_version_id, ModelStatus.CHALLENGER)
        
        return test
    
    def route_request(self, model_type: ModelType, request_id: str) -> str:
        """Route a request to champion or challenger"""
        test_id = self.active_tests.get(model_type)
        if not test_id:
            champion = self.version_manager.get_champion(model_type)
            return champion.id if champion else None
        
        test = self.tests[test_id]
        
        # Use request_id hash for consistent routing
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest()[:8], 16)
        threshold = int(0xFFFFFFFF * test.traffic_split / 100)
        
        if hash_value < threshold:
            return test.challenger_version
        return test.champion_version
    
    def record_result(
        self,
        test_id: str,
        version_id: str,
        request_id: str,
        prediction: Any,
        ground_truth: Optional[Any],
        latency_ms: float,
        user_feedback: Optional[Dict] = None
    ):
        """Record a test result"""
        result = {
            'request_id': request_id,
            'version_id': version_id,
            'timestamp': datetime.utcnow().isoformat(),
            'prediction': prediction,
            'ground_truth': ground_truth,
            'correct': prediction == ground_truth if ground_truth is not None else None,
            'latency_ms': latency_ms,
            'user_feedback': user_feedback
        }
        
        self.test_results[test_id].append(result)
        
        # Check if test should end
        self._check_test_completion(test_id)
    
    def get_test_statistics(self, test_id: str) -> Dict[str, Any]:
        """Get statistics for an A/B test"""
        test = self.tests.get(test_id)
        if not test:
            return {'error': 'Test not found'}
        
        results = self.test_results.get(test_id, [])
        
        champion_results = [r for r in results if r['version_id'] == test.champion_version]
        challenger_results = [r for r in results if r['version_id'] == test.challenger_version]
        
        def compute_stats(results_list):
            if not results_list:
                return None
            
            with_truth = [r for r in results_list if r['ground_truth'] is not None]
            
            stats = {
                'total_requests': len(results_list),
                'avg_latency_ms': np.mean([r['latency_ms'] for r in results_list])
            }
            
            if with_truth:
                correct = sum(1 for r in with_truth if r['correct'])
                stats['accuracy'] = correct / len(with_truth)
            
            feedback = [r for r in results_list if r.get('user_feedback')]
            if feedback:
                ratings = [r['user_feedback'].get('rating') for r in feedback 
                          if r['user_feedback'].get('rating') is not None]
                if ratings:
                    stats['avg_user_rating'] = np.mean(ratings)
            
            return stats
        
        champion_stats = compute_stats(champion_results)
        challenger_stats = compute_stats(challenger_results)
        
        # Determine winner
        winner = None
        if champion_stats and challenger_stats:
            if 'accuracy' in champion_stats and 'accuracy' in challenger_stats:
                if challenger_stats['accuracy'] > champion_stats['accuracy'] + 0.02:
                    winner = 'challenger'
                elif champion_stats['accuracy'] > challenger_stats['accuracy'] + 0.02:
                    winner = 'champion'
                else:
                    winner = 'tie'
        
        return {
            'test_id': test_id,
            'test_name': test.name,
            'status': test.status,
            'start_date': test.start_date.isoformat(),
            'traffic_split': test.traffic_split,
            'champion': {
                'version_id': test.champion_version,
                'stats': champion_stats
            },
            'challenger': {
                'version_id': test.challenger_version,
                'stats': challenger_stats
            },
            'winner': winner,
            'recommendation': self._generate_recommendation(test, champion_stats, challenger_stats, winner)
        }
    
    def conclude_test(self, test_id: str, promote_challenger: bool = False) -> Dict[str, Any]:
        """Conclude an A/B test and optionally promote challenger"""
        test = self.tests.get(test_id)
        if not test:
            return {'error': 'Test not found'}
        
        test.status = 'completed'
        test.end_date = datetime.utcnow()
        
        if test.model_type in self.active_tests:
            del self.active_tests[test.model_type]
        
        if promote_challenger:
            # Promote challenger to champion
            self.version_manager.set_status(test.challenger_version, ModelStatus.CHAMPION)
            return {
                'action': 'promoted',
                'new_champion': test.challenger_version,
                'message': 'Challenger promoted to champion'
            }
        else:
            # Archive challenger
            self.version_manager.set_status(test.challenger_version, ModelStatus.ARCHIVED)
            return {
                'action': 'archived',
                'archived_version': test.challenger_version,
                'message': 'Challenger archived, champion retained'
            }
    
    def _check_test_completion(self, test_id: str):
        """Check if test should auto-complete"""
        test = self.tests.get(test_id)
        if not test or test.status != 'running':
            return
        
        results = self.test_results.get(test_id, [])
        
        # Check minimum samples
        if len(results) >= test.min_samples:
            stats = self.get_test_statistics(test_id)
            if stats.get('winner') and stats['winner'] != 'tie':
                test.results = stats
    
    def _generate_recommendation(
        self,
        test: ABTest,
        champion_stats: Optional[Dict],
        challenger_stats: Optional[Dict],
        winner: Optional[str]
    ) -> str:
        """Generate recommendation based on test results"""
        if not champion_stats or not challenger_stats:
            return "Insufficient data for recommendation"
        
        if winner == 'challenger':
            return "Consider promoting challenger to champion based on improved accuracy"
        elif winner == 'champion':
            return "Keep current champion, challenger did not show improvement"
        else:
            return "Results are inconclusive, consider extending test duration"


# ============================================
# Automated Retraining Triggers
# ============================================

class RetrainingTrigger:
    """Monitors conditions and triggers automatic retraining"""
    
    def __init__(
        self,
        feedback_collector: FeedbackCollector,
        performance_monitor: PerformanceMonitor,
        training_pipeline: TrainingPipeline
    ):
        self.feedback_collector = feedback_collector
        self.performance_monitor = performance_monitor
        self.training_pipeline = training_pipeline
        
        self.last_check: Dict[ModelType, datetime] = {}
        self.trigger_thresholds = {
            'min_feedback_samples': 500,
            'accuracy_drop_threshold': 0.05,
            'drift_score_threshold': 0.3,
            'max_days_without_training': 30
        }
    
    def check_triggers(self, model_type: ModelType) -> Dict[str, Any]:
        """Check if retraining should be triggered"""
        triggers = []
        recommendations = []
        
        # Check feedback volume
        feedback_stats = self.feedback_collector.get_statistics(model_type)
        if feedback_stats['total'] >= self.trigger_thresholds['min_feedback_samples']:
            triggers.append({
                'type': 'feedback_volume',
                'message': f"Sufficient feedback collected: {feedback_stats['total']} samples"
            })
            recommendations.append("Retrain with accumulated feedback")
        
        # Check performance degradation
        # (Would check against baseline metrics in production)
        
        self.last_check[model_type] = datetime.utcnow()
        
        return {
            'model_type': model_type.value,
            'checked_at': datetime.utcnow().isoformat(),
            'triggers': triggers,
            'recommendations': recommendations,
            'should_retrain': len(triggers) > 0
        }
    
    def auto_trigger_training(self, model_type: ModelType) -> Optional[TrainingJob]:
        """Automatically trigger training if conditions are met"""
        check_result = self.check_triggers(model_type)
        
        if not check_result['should_retrain']:
            return None
        
        # Get training samples from feedback
        samples = self.feedback_collector.get_training_samples(model_type)
        
        if len(samples) < 100:
            return None
        
        # Create training job
        job = self.training_pipeline.create_training_job(
            model_type=model_type,
            training_data=samples,
            hyperparameters=None  # Use defaults
        )
        
        return job


# ============================================
# Model Fine-tuning System Integration
# ============================================

class ModelFineTuningSystem:
    """Integrated system for model fine-tuning based on real-world feedback"""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.performance_monitor = PerformanceMonitor()
        self.version_manager = ModelVersionManager()
        self.training_pipeline = TrainingPipeline(self.version_manager)
        self.ab_test_manager = ABTestManager(self.version_manager)
        self.retraining_trigger = RetrainingTrigger(
            self.feedback_collector,
            self.performance_monitor,
            self.training_pipeline
        )
        
        # Initialize with baseline versions
        self._initialize_baseline_versions()
    
    def _initialize_baseline_versions(self):
        """Initialize baseline model versions"""
        for model_type in ModelType:
            version = self.version_manager.create_version(
                model_type=model_type,
                version="1.0.0",
                hyperparameters={},
                training_data_hash="baseline",
                changelog="Initial baseline version"
            )
            
            # Set baseline metrics
            self.version_manager.update_metrics(version.id, {
                'accuracy': 0.80,
                'precision': 0.78,
                'recall': 0.76,
                'f1': 0.77
            })
            
            # Set as champion
            self.version_manager.set_status(version.id, ModelStatus.CHAMPION)
    
    def submit_feedback(
        self,
        model_type: str,
        model_version: str,
        input_data: Dict[str, Any],
        original_prediction: Any,
        feedback_type: str,
        feedback_value: Any,
        user_id: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit user feedback on a prediction"""
        feedback = self.feedback_collector.submit_feedback(
            model_type=ModelType(model_type),
            model_version=model_version,
            input_data=input_data,
            original_prediction=original_prediction,
            feedback_type=FeedbackType(feedback_type),
            feedback_value=feedback_value,
            user_id=user_id,
            project_id=project_id
        )
        
        return {
            'feedback_id': feedback.id,
            'message': 'Feedback submitted successfully',
            'total_feedback': len(self.feedback_collector.feedback_store)
        }
    
    def record_prediction(
        self,
        model_type: str,
        model_version: str,
        input_data: Dict[str, Any],
        prediction: Any,
        latency_ms: float,
        confidence: Optional[float] = None,
        ground_truth: Optional[Any] = None
    ):
        """Record a prediction for monitoring"""
        self.performance_monitor.record_prediction(
            model_type=ModelType(model_type),
            model_version=model_version,
            input_data=input_data,
            prediction=prediction,
            latency_ms=latency_ms,
            confidence=confidence,
            ground_truth=ground_truth
        )
    
    def trigger_retraining(
        self,
        model_type: str,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manually trigger model retraining"""
        model = ModelType(model_type)
        
        # Get training samples
        samples = self.feedback_collector.get_training_samples(model)
        
        if len(samples) < 50:
            return {
                'error': 'Insufficient feedback samples',
                'samples_available': len(samples),
                'samples_required': 50
            }
        
        # Create and run training job
        job = self.training_pipeline.create_training_job(
            model_type=model,
            training_data=samples,
            hyperparameters=hyperparameters
        )
        
        job = self.training_pipeline.run_training_job(job.id)
        
        return {
            'job_id': job.id,
            'status': job.status.value,
            'output_version_id': job.output_version_id,
            'metrics': job.metrics
        }
    
    def start_ab_test(
        self,
        name: str,
        model_type: str,
        challenger_version_id: str,
        traffic_split: float = 10.0
    ) -> Dict[str, Any]:
        """Start an A/B test between champion and challenger"""
        test = self.ab_test_manager.create_test(
            name=name,
            model_type=ModelType(model_type),
            challenger_version_id=challenger_version_id,
            traffic_split=traffic_split
        )
        
        return {
            'test_id': test.id,
            'name': test.name,
            'champion_version': test.champion_version,
            'challenger_version': test.challenger_version,
            'traffic_split': test.traffic_split,
            'status': test.status
        }
    
    def get_model_status(self, model_type: str) -> Dict[str, Any]:
        """Get comprehensive status for a model type"""
        model = ModelType(model_type)
        
        champion = self.version_manager.get_champion(model)
        versions = self.version_manager.get_versions(model)
        feedback_stats = self.feedback_collector.get_statistics(model)
        performance_alerts = self.performance_monitor.get_alerts(model, acknowledged=False)
        retraining_check = self.retraining_trigger.check_triggers(model)
        
        return {
            'model_type': model_type,
            'champion': {
                'version_id': champion.id if champion else None,
                'version': champion.version if champion else None,
                'metrics': champion.metrics if champion else {},
                'trained_at': champion.trained_at.isoformat() if champion and champion.trained_at else None
            },
            'versions': [
                {
                    'id': v.id,
                    'version': v.version,
                    'status': v.status.value,
                    'metrics': v.metrics
                }
                for v in versions[:5]  # Last 5 versions
            ],
            'feedback': feedback_stats,
            'alerts': performance_alerts,
            'retraining': retraining_check
        }
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get overview dashboard for all models"""
        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'models': {},
            'total_feedback': len(self.feedback_collector.feedback_store),
            'active_ab_tests': len(self.ab_test_manager.active_tests),
            'pending_training_jobs': len(self.training_pipeline.get_pending_jobs()),
            'unacknowledged_alerts': len(self.performance_monitor.get_alerts(acknowledged=False))
        }
        
        for model_type in ModelType:
            champion = self.version_manager.get_champion(model_type)
            dashboard['models'][model_type.value] = {
                'champion_version': champion.version if champion else None,
                'accuracy': champion.metrics.get('accuracy') if champion else None,
                'feedback_count': self.feedback_collector.get_statistics(model_type).get('total', 0)
            }
        
        return dashboard


# Create singleton instance
finetuning_system = ModelFineTuningSystem()


# ============================================
# Convenience Functions
# ============================================

def submit_model_feedback(
    model_type: str,
    prediction: Any,
    correction: Any,
    user_id: str,
    input_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Convenience function to submit model feedback"""
    return finetuning_system.submit_feedback(
        model_type=model_type,
        model_version="current",
        input_data=input_data or {},
        original_prediction=prediction,
        feedback_type="correction",
        feedback_value=correction,
        user_id=user_id
    )


def get_model_performance(model_type: str) -> Dict[str, Any]:
    """Convenience function to get model performance"""
    return finetuning_system.get_model_status(model_type)


def trigger_model_improvement(model_type: str) -> Dict[str, Any]:
    """Convenience function to trigger model improvement"""
    return finetuning_system.trigger_retraining(model_type)