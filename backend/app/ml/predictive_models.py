"""
Predictive Analytics Models - Phase 2 Enhanced
- Schedule forecasting (LSTM with attention mechanism)
- Cost prediction (Ensemble methods: RF, GBM, XGBoost)
- Resource optimization
- Risk assessment and early warning system
- Monte Carlo simulation for confidence intervals
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset
from sklearn.ensemble import (
    RandomForestRegressor, 
    GradientBoostingRegressor,
    VotingRegressor,
    StackingRegressor
)
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import json
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for project forecasts"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class ForecastResult:
    """Data class for forecast results"""
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    risk_level: RiskLevel
    risk_factors: List[str]
    recommendations: List[str]
    model_confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'predicted_value': self.predicted_value,
            'confidence_interval': {
                'lower': self.confidence_interval[0],
                'upper': self.confidence_interval[1]
            },
            'confidence_level': self.confidence_level,
            'risk_level': self.risk_level.value,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'model_confidence': self.model_confidence,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ScheduleForecast(ForecastResult):
    """Schedule-specific forecast result"""
    predicted_completion_date: datetime = None
    days_to_completion: int = 0
    schedule_variance_days: int = 0
    critical_path_tasks: List[str] = field(default_factory=list)
    milestone_predictions: Dict[str, datetime] = field(default_factory=dict)


@dataclass 
class CostForecast(ForecastResult):
    """Cost-specific forecast result"""
    predicted_final_cost: float = 0.0
    budget_variance: float = 0.0
    budget_variance_percentage: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    contingency_recommendation: float = 0.0


class LSTMAttention(nn.Module):
    """Attention mechanism for LSTM outputs"""
    
    def __init__(self, hidden_size: int):
        super(LSTMAttention, self).__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Linear(hidden_size // 2, 1),
            nn.Softmax(dim=1)
        )
    
    def forward(self, lstm_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply attention to LSTM outputs
        
        Args:
            lstm_output: (batch, seq_len, hidden_size)
        
        Returns:
            context: (batch, hidden_size) - weighted sum of outputs
            attention_weights: (batch, seq_len, 1)
        """
        attention_weights = self.attention(lstm_output)
        context = torch.sum(attention_weights * lstm_output, dim=1)
        return context, attention_weights


class ScheduleForecastingLSTM(nn.Module):
    """
    Enhanced LSTM model with attention for schedule forecasting
    """
    
    def __init__(
        self,
        input_size: int = 15,
        hidden_size: int = 128,
        num_layers: int = 3,
        dropout: float = 0.3,
        bidirectional: bool = True
    ):
        super(ScheduleForecastingLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # Input normalization
        self.input_norm = nn.LayerNorm(input_size)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        # Attention mechanism
        self.attention = LSTMAttention(hidden_size * self.num_directions)
        
        # Output layers
        lstm_output_size = hidden_size * self.num_directions
        self.fc = nn.Sequential(
            nn.Linear(lstm_output_size, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(32, 1)
        )
        
        # Uncertainty estimation head
        self.uncertainty_head = nn.Sequential(
            nn.Linear(lstm_output_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Softplus()  # Ensures positive variance
        )
    
    def forward(
        self, 
        x: torch.Tensor, 
        return_attention: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Forward pass
        
        Args:
            x: (batch, seq_len, input_size)
            return_attention: Return attention weights
        
        Returns:
            prediction: (batch, 1)
            uncertainty: (batch, 1) - if return_attention
            attention_weights: (batch, seq_len, 1) - if return_attention
        """
        # Normalize input
        x = self.input_norm(x)
        
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # Apply attention
        context, attention_weights = self.attention(lstm_out)
        
        # Predictions
        prediction = self.fc(context)
        
        if return_attention:
            uncertainty = self.uncertainty_head(context)
            return prediction, uncertainty, attention_weights
        
        return prediction


class ScheduleForecastingModel:
    """
    Complete schedule forecasting system with LSTM and ensemble backup
    """
    
    def __init__(
        self,
        sequence_length: int = 30,
        hidden_size: int = 128,
        num_layers: int = 3
    ):
        self.sequence_length = sequence_length
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Primary LSTM model
        self.model = ScheduleForecastingLSTM(
            input_size=15,
            hidden_size=hidden_size,
            num_layers=num_layers
        ).to(self.device)
        
        # Scalers
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        
        # Training state
        self.is_trained = False
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }
        
        # Feature names
        self.feature_names = [
            'tasks_completed_ratio',
            'tasks_remaining',
            'budget_spent_ratio',
            'planned_progress',
            'actual_progress',
            'spi',  # Schedule Performance Index
            'cpi',  # Cost Performance Index
            'worker_count',
            'weather_impact',
            'material_availability',
            'equipment_utilization',
            'quality_score',
            'safety_incidents',
            'change_orders',
            'day_of_week'
        ]
    
    def prepare_sequences(
        self, 
        data: pd.DataFrame,
        target_col: str = 'days_remaining'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series sequences for LSTM
        """
        # Ensure required features exist
        available_features = [f for f in self.feature_names if f in data.columns]
        
        if len(available_features) < 5:
            raise ValueError(f"Insufficient features. Need at least 5, got {len(available_features)}")
        
        # Fill missing features with defaults
        for feature in self.feature_names:
            if feature not in data.columns:
                data[feature] = 0
        
        features = data[self.feature_names].values
        target = data[target_col].values
        
        # Scale
        features_scaled = self.feature_scaler.fit_transform(features)
        target_scaled = self.target_scaler.fit_transform(target.reshape(-1, 1)).flatten()
        
        # Create sequences
        X, y = [], []
        for i in range(len(features_scaled) - self.sequence_length):
            X.append(features_scaled[i:i + self.sequence_length])
            y.append(target_scaled[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(
        self,
        train_data: pd.DataFrame,
        val_data: Optional[pd.DataFrame] = None,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        early_stopping_patience: int = 15
    ) -> Dict:
        """
        Train the LSTM model
        """
        # Prepare data
        X_train, y_train = self.prepare_sequences(train_data)
        
        if val_data is not None:
            X_val, y_val = self.prepare_sequences(val_data)
            val_dataset = TensorDataset(
                torch.FloatTensor(X_val),
                torch.FloatTensor(y_val)
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train),
            torch.FloatTensor(y_train)
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizer and scheduler
        optimizer = torch.optim.AdamW(
            self.model.parameters(), 
            lr=learning_rate,
            weight_decay=1e-4
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # Loss function
        criterion = nn.MSELoss()
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            
            for X_batch, y_batch in train_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                
                optimizer.zero_grad()
                predictions = self.model(X_batch).squeeze()
                loss = criterion(predictions, y_batch)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            self.training_history['train_loss'].append(avg_train_loss)
            
            # Validation
            if val_data is not None:
                self.model.eval()
                val_loss = 0.0
                
                with torch.no_grad():
                    for X_batch, y_batch in val_loader:
                        X_batch = X_batch.to(self.device)
                        y_batch = y_batch.to(self.device)
                        
                        predictions = self.model(X_batch).squeeze()
                        val_loss += criterion(predictions, y_batch).item()
                
                avg_val_loss = val_loss / len(val_loader)
                self.training_history['val_loss'].append(avg_val_loss)
                
                # Learning rate scheduling
                scheduler.step(avg_val_loss)
                
                # Early stopping
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                    # Save best model
                    self.best_model_state = self.model.state_dict().copy()
                else:
                    patience_counter += 1
                
                if patience_counter >= early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
                
                if (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch+1}/{epochs} - "
                        f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
                    )
        
        # Restore best model
        if hasattr(self, 'best_model_state'):
            self.model.load_state_dict(self.best_model_state)
        
        self.is_trained = True
        return self.training_history
    
    def predict_completion(
        self,
        current_data: pd.DataFrame,
        planned_completion_date: datetime,
        remaining_tasks: int
    ) -> ScheduleForecast:
        """
        Predict project completion date and schedule variance
        """
        if not self.is_trained:
            # Use heuristic fallback
            return self._heuristic_prediction(
                current_data, planned_completion_date, remaining_tasks
            )
        
        try:
            self.model.eval()
            
            # Prepare input sequence
            X, _ = self.prepare_sequences(current_data)
            if len(X) == 0:
                return self._heuristic_prediction(
                    current_data, planned_completion_date, remaining_tasks
                )
            
            X_tensor = torch.FloatTensor(X[-1:]).to(self.device)
            
            # Predict with uncertainty
            with torch.no_grad():
                prediction, uncertainty, attention = self.model(
                    X_tensor, return_attention=True
                )
            
            # Inverse transform
            days_remaining = self.target_scaler.inverse_transform(
                prediction.cpu().numpy().reshape(-1, 1)
            )[0, 0]
            
            uncertainty_value = uncertainty.cpu().numpy()[0, 0]
            
            # Calculate dates
            predicted_completion = datetime.now() + timedelta(days=int(days_remaining))
            
            # Calculate variance from plan
            planned_remaining = (planned_completion_date - datetime.now()).days
            variance_days = int(days_remaining - planned_remaining)
            
            # Confidence interval using Monte Carlo
            confidence_interval = self._monte_carlo_confidence(
                days_remaining, uncertainty_value, n_simulations=1000
            )
            
            # Risk assessment
            risk_level, risk_factors = self._assess_schedule_risk(
                variance_days, current_data, days_remaining
            )
            
            # Generate recommendations
            recommendations = self._generate_schedule_recommendations(
                risk_level, risk_factors, variance_days
            )
            
            return ScheduleForecast(
                predicted_value=days_remaining,
                confidence_interval=confidence_interval,
                confidence_level=0.95,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                model_confidence=1.0 - min(uncertainty_value, 0.5),
                predicted_completion_date=predicted_completion,
                days_to_completion=int(days_remaining),
                schedule_variance_days=variance_days,
                critical_path_tasks=self._identify_critical_tasks(current_data),
                milestone_predictions=self._predict_milestones(
                    current_data, days_remaining
                )
            )
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return self._heuristic_prediction(
                current_data, planned_completion_date, remaining_tasks
            )
    
    def _heuristic_prediction(
        self,
        current_data: pd.DataFrame,
        planned_completion_date: datetime,
        remaining_tasks: int
    ) -> ScheduleForecast:
        """Fallback heuristic prediction when model unavailable"""
        # Calculate based on recent velocity
        if 'tasks_completed_ratio' in current_data.columns:
            recent_velocity = current_data['tasks_completed_ratio'].tail(7).mean()
            if recent_velocity > 0:
                days_remaining = remaining_tasks / (recent_velocity * 10)
            else:
                days_remaining = remaining_tasks * 2
        else:
            days_remaining = remaining_tasks * 1.5
        
        predicted_completion = datetime.now() + timedelta(days=int(days_remaining))
        planned_remaining = (planned_completion_date - datetime.now()).days
        variance_days = int(days_remaining - max(planned_remaining, 1))
        
        risk_level = (
            RiskLevel.CRITICAL if variance_days > 30
            else RiskLevel.HIGH if variance_days > 14
            else RiskLevel.MEDIUM if variance_days > 7
            else RiskLevel.LOW if variance_days > 0
            else RiskLevel.MINIMAL
        )
        
        return ScheduleForecast(
            predicted_value=days_remaining,
            confidence_interval=(days_remaining * 0.8, days_remaining * 1.3),
            confidence_level=0.7,
            risk_level=risk_level,
            risk_factors=["Heuristic prediction - limited data available"],
            recommendations=["Collect more historical data for improved predictions"],
            model_confidence=0.5,
            predicted_completion_date=predicted_completion,
            days_to_completion=int(days_remaining),
            schedule_variance_days=variance_days,
            critical_path_tasks=[],
            milestone_predictions={}
        )
    
    def _monte_carlo_confidence(
        self,
        mean_prediction: float,
        uncertainty: float,
        n_simulations: int = 1000
    ) -> Tuple[float, float]:
        """Generate confidence interval using Monte Carlo simulation"""
        std = max(uncertainty * mean_prediction * 0.1, 1.0)
        simulations = np.random.normal(mean_prediction, std, n_simulations)
        
        lower = np.percentile(simulations, 2.5)
        upper = np.percentile(simulations, 97.5)
        
        return (max(lower, 0), upper)
    
    def _assess_schedule_risk(
        self,
        variance_days: int,
        current_data: pd.DataFrame,
        days_remaining: float
    ) -> Tuple[RiskLevel, List[str]]:
        """Assess schedule risk based on multiple factors"""
        risk_factors = []
        risk_score = 0
        
        # Variance risk
        if variance_days > 30:
            risk_score += 4
            risk_factors.append(f"Severe schedule delay: {variance_days} days behind")
        elif variance_days > 14:
            risk_score += 3
            risk_factors.append(f"Significant schedule delay: {variance_days} days behind")
        elif variance_days > 7:
            risk_score += 2
            risk_factors.append(f"Moderate schedule delay: {variance_days} days behind")
        elif variance_days > 0:
            risk_score += 1
            risk_factors.append(f"Minor schedule delay: {variance_days} days behind")
        
        # SPI risk (if available)
        if 'spi' in current_data.columns:
            recent_spi = current_data['spi'].tail(7).mean()
            if recent_spi < 0.8:
                risk_score += 2
                risk_factors.append(f"Low schedule performance index: {recent_spi:.2f}")
            elif recent_spi < 0.9:
                risk_score += 1
                risk_factors.append(f"Below target SPI: {recent_spi:.2f}")
        
        # Resource risk
        if 'worker_count' in current_data.columns:
            worker_trend = current_data['worker_count'].tail(7).diff().mean()
            if worker_trend < -1:
                risk_score += 1
                risk_factors.append("Declining workforce availability")
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 4:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 2:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 1:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return risk_level, risk_factors
    
    def _generate_schedule_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str],
        variance_days: int
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append(
                "URGENT: Schedule recovery meeting with project leadership"
            )
            recommendations.append(
                "Evaluate fast-tracking and crashing opportunities"
            )
            recommendations.append(
                "Consider scope reduction or phased delivery"
            )
        
        if variance_days > 14:
            recommendations.append(
                f"Develop recovery plan to address {variance_days}-day delay"
            )
            recommendations.append(
                "Increase resource allocation on critical path activities"
            )
        
        if "SPI" in str(risk_factors):
            recommendations.append(
                "Review and optimize work sequencing"
            )
            recommendations.append(
                "Address productivity blockers immediately"
            )
        
        if "workforce" in str(risk_factors).lower():
            recommendations.append(
                "Secure additional workforce or subcontractor support"
            )
        
        if not recommendations:
            recommendations.append(
                "Continue monitoring schedule performance"
            )
            recommendations.append(
                "Maintain current resource levels and work pace"
            )
        
        return recommendations
    
    def _identify_critical_tasks(self, current_data: pd.DataFrame) -> List[str]:
        """Identify tasks on critical path"""
        # Placeholder - would integrate with project schedule data
        return []
    
    def _predict_milestones(
        self,
        current_data: pd.DataFrame,
        total_days_remaining: float
    ) -> Dict[str, datetime]:
        """Predict milestone completion dates"""
        # Placeholder - would calculate based on milestone definitions
        return {}


class CostPredictionEnsemble:
    """
    Ensemble model for cost prediction combining multiple algorithms
    """
    
    def __init__(self):
        # Base models
        self.models = {
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gbm': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            ),
            'ridge': Ridge(alpha=1.0),
            'elasticnet': ElasticNet(alpha=0.5, l1_ratio=0.5)
        }
        
        # Meta-model for stacking
        self.meta_model = Ridge(alpha=0.1)
        
        # Ensemble weights (learned or default)
        self.weights = {
            'rf': 0.35,
            'gbm': 0.35,
            'ridge': 0.15,
            'elasticnet': 0.15
        }
        
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        self.is_trained = False
        
        self.feature_names = [
            'project_size_sqft',
            'duration_days',
            'worker_count',
            'material_cost_ratio',
            'equipment_cost_ratio',
            'labor_cost_ratio',
            'complexity_score',
            'location_factor',
            'season_factor',
            'historical_waste_rate',
            'change_order_frequency',
            'subcontractor_ratio',
            'permit_delays',
            'weather_impact_score',
            'current_progress'
        ]
        
        self.feature_importance = {}
    
    def train(
        self,
        training_data: pd.DataFrame,
        target_col: str = 'final_cost',
        use_stacking: bool = True
    ) -> Dict:
        """
        Train the ensemble model
        """
        # Prepare features
        available_features = [f for f in self.feature_names if f in training_data.columns]
        
        if len(available_features) < 3:
            raise ValueError("Insufficient features for training")
        
        X = training_data[available_features].fillna(0)
        y = training_data[target_col].values
        
        # Scale
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        metrics = {}
        
        if use_stacking:
            # Stacking ensemble
            estimators = [
                ('rf', self.models['rf']),
                ('gbm', self.models['gbm']),
                ('ridge', self.models['ridge'])
            ]
            
            self.stacking_model = StackingRegressor(
                estimators=estimators,
                final_estimator=self.meta_model,
                cv=5
            )
            
            self.stacking_model.fit(X_scaled, y_scaled)
            
            # Calculate CV scores
            cv_scores = cross_val_score(
                self.stacking_model, X_scaled, y_scaled, 
                cv=tscv, scoring='neg_mean_absolute_error'
            )
            metrics['cv_mae'] = -cv_scores.mean()
            metrics['cv_mae_std'] = cv_scores.std()
        else:
            # Train individual models
            for name, model in self.models.items():
                model.fit(X_scaled, y_scaled)
                
                cv_scores = cross_val_score(
                    model, X_scaled, y_scaled, 
                    cv=tscv, scoring='neg_mean_absolute_error'
                )
                metrics[f'{name}_cv_mae'] = -cv_scores.mean()
        
        # Feature importance from RF
        self.models['rf'].fit(X_scaled, y_scaled)
        self.feature_importance = dict(zip(
            available_features,
            self.models['rf'].feature_importances_
        ))
        
        self.is_trained = True
        self.trained_features = available_features
        
        logger.info(f"Cost model trained with {len(available_features)} features")
        return metrics
    
    def predict_cost(
        self,
        project_data: Dict,
        budget: float
    ) -> CostForecast:
        """
        Predict final project cost
        """
        if not self.is_trained:
            return self._heuristic_cost_prediction(project_data, budget)
        
        try:
            # Prepare features
            features = []
            for f in self.trained_features:
                features.append(project_data.get(f, 0))
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.feature_scaler.transform(X)
            
            # Get predictions from each model
            predictions = {}
            if hasattr(self, 'stacking_model'):
                predictions['ensemble'] = self.stacking_model.predict(X_scaled)[0]
            else:
                for name, model in self.models.items():
                    predictions[name] = model.predict(X_scaled)[0]
            
            # Ensemble prediction
            if 'ensemble' in predictions:
                final_prediction_scaled = predictions['ensemble']
            else:
                final_prediction_scaled = sum(
                    predictions[name] * self.weights[name]
                    for name in predictions
                )
            
            # Inverse transform
            final_cost = self.target_scaler.inverse_transform(
                np.array([[final_prediction_scaled]])
            )[0, 0]
            
            # Calculate variance from budget
            budget_variance = final_cost - budget
            budget_variance_pct = (budget_variance / budget) * 100 if budget > 0 else 0
            
            # Uncertainty estimation using prediction variance
            if len(predictions) > 1:
                pred_values = [
                    self.target_scaler.inverse_transform(
                        np.array([[p]])
                    )[0, 0] for p in predictions.values()
                ]
                std = np.std(pred_values)
            else:
                std = final_cost * 0.05  # Default 5% uncertainty
            
            confidence_interval = (
                max(final_cost - 1.96 * std, 0),
                final_cost + 1.96 * std
            )
            
            # Risk assessment
            risk_level, risk_factors = self._assess_cost_risk(
                budget_variance_pct, project_data
            )
            
            # Cost breakdown
            cost_breakdown = self._estimate_cost_breakdown(
                final_cost, project_data
            )
            
            # Recommendations
            recommendations = self._generate_cost_recommendations(
                risk_level, risk_factors, budget_variance_pct
            )
            
            # Contingency recommendation
            contingency = self._calculate_contingency(
                risk_level, final_cost, budget_variance_pct
            )
            
            return CostForecast(
                predicted_value=final_cost,
                confidence_interval=confidence_interval,
                confidence_level=0.95,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                model_confidence=0.85,
                predicted_final_cost=final_cost,
                budget_variance=budget_variance,
                budget_variance_percentage=budget_variance_pct,
                cost_breakdown=cost_breakdown,
                contingency_recommendation=contingency
            )
            
        except Exception as e:
            logger.error(f"Cost prediction error: {e}")
            return self._heuristic_cost_prediction(project_data, budget)
    
    def _heuristic_cost_prediction(
        self,
        project_data: Dict,
        budget: float
    ) -> CostForecast:
        """Fallback heuristic prediction"""
        current_spend = project_data.get('current_spend', budget * 0.5)
        progress = project_data.get('current_progress', 0.5)
        
        if progress > 0:
            estimated_final = current_spend / progress
        else:
            estimated_final = budget * 1.1
        
        variance = estimated_final - budget
        variance_pct = (variance / budget) * 100 if budget > 0 else 0
        
        risk_level = (
            RiskLevel.CRITICAL if variance_pct > 20
            else RiskLevel.HIGH if variance_pct > 10
            else RiskLevel.MEDIUM if variance_pct > 5
            else RiskLevel.LOW if variance_pct > 0
            else RiskLevel.MINIMAL
        )
        
        return CostForecast(
            predicted_value=estimated_final,
            confidence_interval=(estimated_final * 0.9, estimated_final * 1.15),
            confidence_level=0.7,
            risk_level=risk_level,
            risk_factors=["Heuristic prediction - limited data"],
            recommendations=["Improve cost tracking for better predictions"],
            model_confidence=0.5,
            predicted_final_cost=estimated_final,
            budget_variance=variance,
            budget_variance_percentage=variance_pct,
            cost_breakdown={},
            contingency_recommendation=estimated_final * 0.1
        )
    
    def _assess_cost_risk(
        self,
        variance_pct: float,
        project_data: Dict
    ) -> Tuple[RiskLevel, List[str]]:
        """Assess cost risk"""
        risk_factors = []
        risk_score = 0
        
        # Budget variance risk
        if variance_pct > 20:
            risk_score += 4
            risk_factors.append(f"Severe budget overrun: {variance_pct:.1f}%")
        elif variance_pct > 10:
            risk_score += 3
            risk_factors.append(f"Significant budget overrun: {variance_pct:.1f}%")
        elif variance_pct > 5:
            risk_score += 2
            risk_factors.append(f"Moderate budget overrun: {variance_pct:.1f}%")
        elif variance_pct > 0:
            risk_score += 1
            risk_factors.append(f"Minor budget overrun: {variance_pct:.1f}%")
        
        # CPI risk
        cpi = project_data.get('cpi', 1.0)
        if cpi < 0.85:
            risk_score += 2
            risk_factors.append(f"Poor cost performance index: {cpi:.2f}")
        elif cpi < 0.95:
            risk_score += 1
            risk_factors.append(f"Below target CPI: {cpi:.2f}")
        
        # Change order risk
        change_orders = project_data.get('change_order_frequency', 0)
        if change_orders > 5:
            risk_score += 2
            risk_factors.append(f"High change order frequency: {change_orders}")
        elif change_orders > 2:
            risk_score += 1
            risk_factors.append(f"Elevated change orders: {change_orders}")
        
        # Material cost risk
        material_variance = project_data.get('material_cost_variance', 0)
        if material_variance > 0.15:
            risk_score += 1
            risk_factors.append("Material costs exceeding estimates")
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 4:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 2:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 1:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return risk_level, risk_factors
    
    def _estimate_cost_breakdown(
        self,
        total_cost: float,
        project_data: Dict
    ) -> Dict[str, float]:
        """Estimate cost breakdown by category"""
        labor_ratio = project_data.get('labor_cost_ratio', 0.40)
        material_ratio = project_data.get('material_cost_ratio', 0.35)
        equipment_ratio = project_data.get('equipment_cost_ratio', 0.15)
        overhead_ratio = 1 - labor_ratio - material_ratio - equipment_ratio
        
        return {
            'labor': total_cost * labor_ratio,
            'materials': total_cost * material_ratio,
            'equipment': total_cost * equipment_ratio,
            'overhead': total_cost * max(overhead_ratio, 0.05)
        }
    
    def _generate_cost_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str],
        variance_pct: float
    ) -> List[str]:
        """Generate cost management recommendations"""
        recommendations = []
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append(
                "URGENT: Implement cost containment measures immediately"
            )
            recommendations.append(
                "Review all uncommitted costs for potential savings"
            )
            recommendations.append(
                "Evaluate value engineering opportunities"
            )
        
        if variance_pct > 10:
            recommendations.append(
                "Request contingency release or budget increase"
            )
            recommendations.append(
                "Implement enhanced cost tracking and approval controls"
            )
        
        if "CPI" in str(risk_factors):
            recommendations.append(
                "Conduct detailed variance analysis by cost category"
            )
        
        if "change order" in str(risk_factors).lower():
            recommendations.append(
                "Review change order management process"
            )
            recommendations.append(
                "Improve scope documentation and control"
            )
        
        if "Material" in str(risk_factors):
            recommendations.append(
                "Negotiate bulk discounts or alternative suppliers"
            )
        
        if not recommendations:
            recommendations.append(
                "Continue cost monitoring and control practices"
            )
        
        return recommendations
    
    def _calculate_contingency(
        self,
        risk_level: RiskLevel,
        predicted_cost: float,
        variance_pct: float
    ) -> float:
        """Calculate recommended contingency amount"""
        base_contingency_rates = {
            RiskLevel.CRITICAL: 0.15,
            RiskLevel.HIGH: 0.12,
            RiskLevel.MEDIUM: 0.08,
            RiskLevel.LOW: 0.05,
            RiskLevel.MINIMAL: 0.03
        }
        
        rate = base_contingency_rates.get(risk_level, 0.10)
        
        # Adjust for existing variance
        if variance_pct > 10:
            rate += 0.03
        elif variance_pct > 5:
            rate += 0.02
        
        return predicted_cost * rate
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importance rankings"""
        if not self.feature_importance:
            return {}
        
        # Sort by importance
        return dict(sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))


class ResourceOptimizer:
    """
    Optimization engine for resource allocation and scheduling
    """
    
    def __init__(self):
        self.optimization_history = []
    
    def optimize_workforce(
        self,
        tasks: List[Dict],
        workers: List[Dict],
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize workforce allocation using skill matching and load balancing
        """
        constraints = constraints or {}
        
        # Build skill matrix
        skill_matrix = self._build_skill_matrix(tasks, workers)
        
        # Allocate workers to tasks
        allocation = self._greedy_allocation(
            tasks, workers, skill_matrix, constraints
        )
        
        # Calculate metrics
        current_efficiency = constraints.get('current_efficiency', 0.7)
        optimized_efficiency = self._calculate_efficiency(allocation, skill_matrix)
        
        time_savings = self._estimate_time_savings(
            allocation, optimized_efficiency - current_efficiency
        )
        cost_savings = self._estimate_cost_savings(
            allocation, workers, optimized_efficiency - current_efficiency
        )
        
        return {
            'allocation': allocation,
            'current_efficiency': current_efficiency,
            'optimized_efficiency': optimized_efficiency,
            'efficiency_improvement': (optimized_efficiency - current_efficiency) * 100,
            'estimated_time_savings_hours': time_savings,
            'estimated_cost_savings': cost_savings,
            'workload_balance': self._calculate_workload_balance(allocation, workers),
            'recommendations': self._generate_workforce_recommendations(
                allocation, skill_matrix
            )
        }
    
    def optimize_material_delivery(
        self,
        materials: List[Dict],
        schedule: List[Dict],
        storage_capacity: float = float('inf')
    ) -> Dict:
        """
        Optimize material delivery schedule using JIT principles
        """
        # Sort materials by required date
        sorted_materials = sorted(
            materials, 
            key=lambda m: m.get('required_date', datetime.max)
        )
        
        delivery_schedule = []
        current_storage = 0
        
        for material in sorted_materials:
            required_date = material.get('required_date')
            lead_time = material.get('lead_time_days', 7)
            quantity = material.get('quantity', 0)
            size = material.get('storage_size', quantity * 0.1)
            
            # Calculate optimal delivery date
            optimal_delivery = required_date - timedelta(days=2)  # 2-day buffer
            order_date = optimal_delivery - timedelta(days=lead_time)
            
            # Check storage constraints
            if current_storage + size > storage_capacity:
                # Delay delivery if possible
                optimal_delivery = required_date - timedelta(days=1)
            
            delivery_schedule.append({
                'material_id': material.get('id'),
                'material_name': material.get('name'),
                'quantity': quantity,
                'order_date': order_date.isoformat() if isinstance(order_date, datetime) else order_date,
                'delivery_date': optimal_delivery.isoformat() if isinstance(optimal_delivery, datetime) else optimal_delivery,
                'required_date': required_date.isoformat() if isinstance(required_date, datetime) else required_date,
                'lead_time_days': lead_time,
                'storage_size': size
            })
            
            current_storage += size
        
        # Calculate savings
        storage_savings = self._calculate_storage_savings(delivery_schedule, materials)
        
        return {
            'delivery_schedule': delivery_schedule,
            'total_deliveries': len(delivery_schedule),
            'storage_utilization': current_storage / storage_capacity if storage_capacity < float('inf') else 0,
            'storage_cost_savings': storage_savings,
            'jit_percentage': self._calculate_jit_percentage(delivery_schedule),
            'recommendations': [
                "Coordinate deliveries with work schedule",
                "Establish buffer stock for critical materials",
                "Use staging areas efficiently"
            ]
        }
    
    def _build_skill_matrix(
        self,
        tasks: List[Dict],
        workers: List[Dict]
    ) -> np.ndarray:
        """Build worker-task skill compatibility matrix"""
        n_workers = len(workers)
        n_tasks = len(tasks)
        
        matrix = np.zeros((n_workers, n_tasks))
        
        for i, worker in enumerate(workers):
            worker_skills = set(worker.get('skills', []))
            
            for j, task in enumerate(tasks):
                required_skills = set(task.get('required_skills', []))
                
                if required_skills:
                    match_score = len(worker_skills & required_skills) / len(required_skills)
                else:
                    match_score = 0.5
                
                matrix[i, j] = match_score
        
        return matrix
    
    def _greedy_allocation(
        self,
        tasks: List[Dict],
        workers: List[Dict],
        skill_matrix: np.ndarray,
        constraints: Dict
    ) -> List[Dict]:
        """Greedy allocation algorithm"""
        allocation = []
        assigned_tasks = set()
        worker_loads = {i: 0 for i in range(len(workers))}
        max_load = constraints.get('max_tasks_per_worker', 5)
        
        # Sort tasks by priority
        task_priorities = [(i, t.get('priority', 1)) for i, t in enumerate(tasks)]
        task_priorities.sort(key=lambda x: x[1], reverse=True)
        
        for task_idx, _ in task_priorities:
            if task_idx in assigned_tasks:
                continue
            
            task = tasks[task_idx]
            
            # Find best available worker
            best_worker = None
            best_score = -1
            
            for worker_idx in range(len(workers)):
                if worker_loads[worker_idx] >= max_load:
                    continue
                
                score = skill_matrix[worker_idx, task_idx]
                
                # Penalize overloaded workers
                load_penalty = worker_loads[worker_idx] * 0.1
                adjusted_score = score - load_penalty
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_worker = worker_idx
            
            if best_worker is not None:
                allocation.append({
                    'task_id': task.get('id'),
                    'task_name': task.get('name'),
                    'worker_id': workers[best_worker].get('id'),
                    'worker_name': workers[best_worker].get('name'),
                    'skill_match': skill_matrix[best_worker, task_idx],
                    'priority': task.get('priority', 1)
                })
                
                assigned_tasks.add(task_idx)
                worker_loads[best_worker] += 1
        
        return allocation
    
    def _calculate_efficiency(
        self,
        allocation: List[Dict],
        skill_matrix: np.ndarray
    ) -> float:
        """Calculate allocation efficiency"""
        if not allocation:
            return 0.0
        
        avg_skill_match = np.mean([a['skill_match'] for a in allocation])
        return min(avg_skill_match * 1.1, 1.0)
    
    def _estimate_time_savings(
        self,
        allocation: List[Dict],
        efficiency_gain: float
    ) -> float:
        """Estimate time savings from optimization"""
        if efficiency_gain <= 0:
            return 0.0
        
        total_task_hours = len(allocation) * 8  # Assume 8 hours per task
        return total_task_hours * efficiency_gain
    
    def _estimate_cost_savings(
        self,
        allocation: List[Dict],
        workers: List[Dict],
        efficiency_gain: float
    ) -> float:
        """Estimate cost savings from optimization"""
        if efficiency_gain <= 0:
            return 0.0
        
        avg_hourly_rate = np.mean([
            w.get('hourly_rate', 75) for w in workers
        ])
        
        time_savings = self._estimate_time_savings(allocation, efficiency_gain)
        return time_savings * avg_hourly_rate
    
    def _calculate_workload_balance(
        self,
        allocation: List[Dict],
        workers: List[Dict]
    ) -> Dict:
        """Calculate workload balance metrics"""
        worker_loads = {}
        
        for worker in workers:
            worker_id = worker.get('id')
            worker_loads[worker_id] = sum(
                1 for a in allocation if a['worker_id'] == worker_id
            )
        
        loads = list(worker_loads.values())
        
        return {
            'min_load': min(loads) if loads else 0,
            'max_load': max(loads) if loads else 0,
            'avg_load': np.mean(loads) if loads else 0,
            'std_load': np.std(loads) if loads else 0,
            'balance_score': 1 - (np.std(loads) / np.mean(loads) if np.mean(loads) > 0 else 0)
        }
    
    def _generate_workforce_recommendations(
        self,
        allocation: List[Dict],
        skill_matrix: np.ndarray
    ) -> List[str]:
        """Generate workforce optimization recommendations"""
        recommendations = []
        
        low_match_tasks = [a for a in allocation if a['skill_match'] < 0.5]
        
        if low_match_tasks:
            recommendations.append(
                f"Provide training for {len(low_match_tasks)} tasks with low skill match"
            )
        
        recommendations.append("Cross-train workers to increase scheduling flexibility")
        recommendations.append("Balance workload across team members")
        
        return recommendations
    
    def _calculate_storage_savings(
        self,
        optimized_schedule: List[Dict],
        original_materials: List[Dict]
    ) -> float:
        """Calculate storage cost savings from JIT optimization"""
        daily_storage_cost = 10  # $ per day per unit
        
        original_storage_days = sum(
            m.get('storage_days', 14) for m in original_materials
        )
        
        optimized_storage_days = len(optimized_schedule) * 2  # 2-day buffer
        
        savings = (original_storage_days - optimized_storage_days) * daily_storage_cost
        return max(savings, 0)
    
    def _calculate_jit_percentage(self, schedule: List[Dict]) -> float:
        """Calculate percentage of materials delivered JIT"""
        if not schedule:
            return 0.0
        
        jit_deliveries = sum(
            1 for s in schedule 
            if s.get('delivery_date') == s.get('required_date')
            or (isinstance(s.get('delivery_date'), str) and 
                isinstance(s.get('required_date'), str))
        )
        
        return jit_deliveries / len(schedule)


class IntegratedForecastingSystem:
    """
    Integrated system combining schedule and cost forecasting
    with risk assessment and recommendations
    """
    
    def __init__(self):
        self.schedule_model = ScheduleForecastingModel()
        self.cost_model = CostPredictionEnsemble()
        self.resource_optimizer = ResourceOptimizer()
        
        self.forecast_history = []
    
    def generate_forecast(
        self,
        project_data: Dict,
        historical_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Generate comprehensive project forecast
        """
        # Schedule forecast
        if historical_data is not None and 'days_remaining' in historical_data.columns:
            schedule_forecast = self.schedule_model.predict_completion(
                historical_data,
                project_data.get('planned_completion_date', datetime.now() + timedelta(days=90)),
                project_data.get('remaining_tasks', 50)
            )
        else:
            schedule_forecast = self.schedule_model._heuristic_prediction(
                pd.DataFrame([project_data]),
                project_data.get('planned_completion_date', datetime.now() + timedelta(days=90)),
                project_data.get('remaining_tasks', 50)
            )
        
        # Cost forecast
        cost_forecast = self.cost_model.predict_cost(
            project_data,
            project_data.get('budget', 1000000)
        )
        
        # Combined risk assessment
        combined_risk = self._assess_combined_risk(
            schedule_forecast, cost_forecast
        )
        
        # Generate integrated recommendations
        recommendations = self._generate_integrated_recommendations(
            schedule_forecast, cost_forecast, combined_risk
        )
        
        forecast = {
            'timestamp': datetime.utcnow().isoformat(),
            'project_id': project_data.get('project_id', 'unknown'),
            'schedule_forecast': schedule_forecast.to_dict() if hasattr(schedule_forecast, 'to_dict') else vars(schedule_forecast),
            'cost_forecast': cost_forecast.to_dict() if hasattr(cost_forecast, 'to_dict') else vars(cost_forecast),
            'combined_risk_level': combined_risk['level'].value,
            'combined_risk_score': combined_risk['score'],
            'integrated_recommendations': recommendations,
            'executive_summary': self._generate_executive_summary(
                schedule_forecast, cost_forecast, combined_risk
            )
        }
        
        self.forecast_history.append(forecast)
        
        return forecast
    
    def _assess_combined_risk(
        self,
        schedule: ScheduleForecast,
        cost: CostForecast
    ) -> Dict:
        """Assess combined project risk"""
        risk_scores = {
            RiskLevel.CRITICAL: 5,
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 2,
            RiskLevel.MINIMAL: 1
        }
        
        schedule_score = risk_scores.get(schedule.risk_level, 3)
        cost_score = risk_scores.get(cost.risk_level, 3)
        
        # Weighted average (schedule slightly higher weight)
        combined_score = (schedule_score * 0.55 + cost_score * 0.45)
        
        if combined_score >= 4.5:
            level = RiskLevel.CRITICAL
        elif combined_score >= 3.5:
            level = RiskLevel.HIGH
        elif combined_score >= 2.5:
            level = RiskLevel.MEDIUM
        elif combined_score >= 1.5:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.MINIMAL
        
        return {
            'level': level,
            'score': combined_score,
            'schedule_contribution': schedule_score,
            'cost_contribution': cost_score
        }
    
    def _generate_integrated_recommendations(
        self,
        schedule: ScheduleForecast,
        cost: CostForecast,
        combined_risk: Dict
    ) -> List[str]:
        """Generate integrated recommendations"""
        recommendations = []
        
        if combined_risk['level'] == RiskLevel.CRITICAL:
            recommendations.append(
                "CRITICAL: Immediate management intervention required"
            )
            recommendations.append(
                "Conduct comprehensive project review within 48 hours"
            )
        
        # Combine unique recommendations from both forecasts
        all_recs = set(schedule.recommendations + cost.recommendations)
        recommendations.extend(list(all_recs)[:5])
        
        # Add integrated recommendations
        if schedule.risk_level != RiskLevel.MINIMAL and cost.risk_level != RiskLevel.MINIMAL:
            recommendations.append(
                "Both schedule and cost show elevated risk - review resource allocation"
            )
        
        return recommendations[:7]  # Limit to 7 recommendations
    
    def _generate_executive_summary(
        self,
        schedule: ScheduleForecast,
        cost: CostForecast,
        combined_risk: Dict
    ) -> str:
        """Generate executive summary"""
        parts = []
        
        # Overall status
        status_map = {
            RiskLevel.CRITICAL: "Critical status",
            RiskLevel.HIGH: "High risk",
            RiskLevel.MEDIUM: "Moderate risk",
            RiskLevel.LOW: "Low risk",
            RiskLevel.MINIMAL: "On track"
        }
        
        parts.append(f"Project Status: {status_map[combined_risk['level']]}")
        
        # Schedule summary
        if hasattr(schedule, 'schedule_variance_days'):
            if schedule.schedule_variance_days > 0:
                parts.append(
                    f"Schedule: {schedule.schedule_variance_days} days behind plan"
                )
            elif schedule.schedule_variance_days < 0:
                parts.append(
                    f"Schedule: {abs(schedule.schedule_variance_days)} days ahead of plan"
                )
            else:
                parts.append("Schedule: On plan")
        
        # Cost summary
        if hasattr(cost, 'budget_variance_percentage'):
            if cost.budget_variance_percentage > 0:
                parts.append(
                    f"Cost: {cost.budget_variance_percentage:.1f}% over budget"
                )
            elif cost.budget_variance_percentage < 0:
                parts.append(
                    f"Cost: {abs(cost.budget_variance_percentage):.1f}% under budget"
                )
            else:
                parts.append("Cost: On budget")
        
        return ". ".join(parts) + "."
    
    def train_models(
        self,
        schedule_data: pd.DataFrame,
        cost_data: pd.DataFrame
    ):
        """Train both forecasting models"""
        # Train schedule model
        if 'days_remaining' in schedule_data.columns:
            self.schedule_model.train(schedule_data)
            logger.info("Schedule model trained")
        
        # Train cost model
        if 'final_cost' in cost_data.columns:
            self.cost_model.train(cost_data)
            logger.info("Cost model trained")
    
    def get_forecast_report(self) -> Dict:
        """Generate comprehensive forecast report"""
        if not self.forecast_history:
            return {'error': 'No forecast data available'}
        
        latest = self.forecast_history[-1]
        
        return {
            'report_date': datetime.utcnow().isoformat(),
            'latest_forecast': latest,
            'forecast_count': len(self.forecast_history),
            'trend': self._calculate_forecast_trend()
        }
    
    def _calculate_forecast_trend(self) -> Dict:
        """Calculate trend in forecasts"""
        if len(self.forecast_history) < 2:
            return {'direction': 'insufficient_data'}
        
        recent_risks = [
            f['combined_risk_score'] 
            for f in self.forecast_history[-10:]
        ]
        
        change = recent_risks[-1] - recent_risks[0]
        
        return {
            'direction': 'improving' if change < -0.5 else 'worsening' if change > 0.5 else 'stable',
            'change': change
        }
