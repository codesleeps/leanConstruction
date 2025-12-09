"""
Predictive Analytics Models
- Schedule forecasting (LSTM)
- Cost prediction (Ensemble methods)
- Resource optimization
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class ScheduleForecastingModel:
    """
    LSTM-based model for schedule forecasting and delay prediction
    """
    
    def __init__(self, sequence_length: int = 30, hidden_size: int = 64):
        """
        Initialize schedule forecasting model
        
        Args:
            sequence_length: Number of days to look back
            hidden_size: LSTM hidden layer size
        """
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Build LSTM model
        self.model = self._build_model()
        self.scaler = StandardScaler()
        
    def _build_model(self) -> nn.Module:
        """Build LSTM neural network"""
        class LSTMForecaster(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers=2):
                super(LSTMForecaster, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(
                    input_size,
                    hidden_size,
                    num_layers,
                    batch_first=True,
                    dropout=0.2
                )
                
                self.fc = nn.Sequential(
                    nn.Linear(hidden_size, 32),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(32, 1)
                )
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                last_output = lstm_out[:, -1, :]
                prediction = self.fc(last_output)
                return prediction
        
        model = LSTMForecaster(
            input_size=10,  # Number of features
            hidden_size=self.hidden_size
        )
        
        return model.to(self.device)
    
    def prepare_data(self, historical_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for LSTM
        
        Args:
            historical_data: DataFrame with historical project metrics
            
        Returns:
            Tuple of (X, y) arrays
        """
        # Extract features
        features = [
            'tasks_completed',
            'tasks_remaining',
            'budget_spent',
            'budget_remaining',
            'worker_count',
            'weather_score',
            'material_availability',
            'equipment_utilization',
            'quality_score',
            'safety_score'
        ]
        
        data = historical_data[features].values
        
        # Normalize
        data_scaled = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(len(data_scaled) - self.sequence_length):
            X.append(data_scaled[i:i + self.sequence_length])
            y.append(data_scaled[i + self.sequence_length, 0])  # Predict tasks_completed
        
        return np.array(X), np.array(y)
    
    def train(self, historical_data: pd.DataFrame, epochs: int = 100):
        """
        Train the LSTM model
        
        Args:
            historical_data: Historical project data
            epochs: Number of training epochs
        """
        X, y = self.prepare_data(historical_data)
        
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.FloatTensor(y).unsqueeze(1).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    
    def predict_completion_date(
        self,
        current_data: pd.DataFrame,
        remaining_tasks: int
    ) -> Dict:
        """
        Predict project completion date
        
        Args:
            current_data: Recent project data
            remaining_tasks: Number of tasks remaining
            
        Returns:
            Dictionary with prediction results
        """
        try:
            self.model.eval()
            
            # Prepare input
            X, _ = self.prepare_data(current_data)
            X_tensor = torch.FloatTensor(X[-1:]).to(self.device)
            
            # Predict daily completion rate
            with torch.no_grad():
                prediction = self.model(X_tensor)
                daily_completion_rate = prediction.item()
            
            # Calculate estimated days to completion
            if daily_completion_rate > 0:
                days_to_completion = remaining_tasks / daily_completion_rate
            else:
                days_to_completion = float('inf')
            
            # Calculate completion date
            completion_date = datetime.now() + timedelta(days=days_to_completion)
            
            # Calculate confidence interval
            confidence_lower = days_to_completion * 0.9
            confidence_upper = days_to_completion * 1.1
            
            return {
                'predicted_completion_date': completion_date.isoformat(),
                'days_to_completion': int(days_to_completion),
                'daily_completion_rate': daily_completion_rate,
                'confidence_interval': {
                    'lower_days': int(confidence_lower),
                    'upper_days': int(confidence_upper),
                    'lower_date': (datetime.now() + timedelta(days=confidence_lower)).isoformat(),
                    'upper_date': (datetime.now() + timedelta(days=confidence_upper)).isoformat()
                },
                'risk_level': self._assess_risk(days_to_completion, remaining_tasks)
            }
        
        except Exception as e:
            logger.error(f"Error predicting completion date: {str(e)}")
            return {
                'error': str(e),
                'predicted_completion_date': None
            }
    
    def _assess_risk(self, days_to_completion: float, remaining_tasks: int) -> str:
        """Assess schedule risk level"""
        if days_to_completion == float('inf'):
            return 'critical'
        elif days_to_completion > remaining_tasks * 2:
            return 'high'
        elif days_to_completion > remaining_tasks * 1.5:
            return 'medium'
        else:
            return 'low'


class CostPredictionModel:
    """
    Ensemble model for cost forecasting and budget prediction
    Uses Random Forest + Gradient Boosting
    """
    
    def __init__(self):
        """Initialize cost prediction model"""
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, historical_data: pd.DataFrame):
        """
        Train the ensemble model
        
        Args:
            historical_data: Historical project cost data
        """
        # Extract features
        features = [
            'project_size',
            'duration_days',
            'worker_count',
            'material_cost',
            'equipment_cost',
            'complexity_score',
            'location_factor',
            'season_factor',
            'waste_cost',
            'change_orders'
        ]
        
        X = historical_data[features].values
        y = historical_data['total_cost'].values
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train both models
        self.rf_model.fit(X_scaled, y)
        self.gb_model.fit(X_scaled, y)
        
        self.is_trained = True
        logger.info("Cost prediction model trained successfully")
    
    def predict_final_cost(self, project_data: Dict) -> Dict:
        """
        Predict final project cost
        
        Args:
            project_data: Current project data
            
        Returns:
            Dictionary with cost predictions
        """
        if not self.is_trained:
            return {
                'error': 'Model not trained',
                'predicted_cost': None
            }
        
        try:
            # Prepare features
            features = np.array([[
                project_data.get('project_size', 0),
                project_data.get('duration_days', 0),
                project_data.get('worker_count', 0),
                project_data.get('material_cost', 0),
                project_data.get('equipment_cost', 0),
                project_data.get('complexity_score', 0.5),
                project_data.get('location_factor', 1.0),
                project_data.get('season_factor', 1.0),
                project_data.get('waste_cost', 0),
                project_data.get('change_orders', 0)
            ]])
            
            # Normalize
            features_scaled = self.scaler.transform(features)
            
            # Predict with both models
            rf_prediction = self.rf_model.predict(features_scaled)[0]
            gb_prediction = self.gb_model.predict(features_scaled)[0]
            
            # Ensemble prediction (weighted average)
            final_prediction = (rf_prediction * 0.5 + gb_prediction * 0.5)
            
            # Calculate variance and confidence interval
            variance = abs(rf_prediction - gb_prediction)
            confidence_lower = final_prediction * 0.95
            confidence_upper = final_prediction * 1.05
            
            # Calculate budget status
            budget = project_data.get('budget', final_prediction)
            budget_variance = ((final_prediction - budget) / budget) * 100
            
            return {
                'predicted_final_cost': float(final_prediction),
                'rf_prediction': float(rf_prediction),
                'gb_prediction': float(gb_prediction),
                'confidence_interval': {
                    'lower': float(confidence_lower),
                    'upper': float(confidence_upper)
                },
                'budget': float(budget),
                'budget_variance_percentage': float(budget_variance),
                'status': self._get_budget_status(budget_variance),
                'risk_factors': self._identify_cost_risks(project_data),
                'recommendations': self._generate_cost_recommendations(budget_variance)
            }
        
        except Exception as e:
            logger.error(f"Error predicting cost: {str(e)}")
            return {
                'error': str(e),
                'predicted_cost': None
            }
    
    def _get_budget_status(self, variance: float) -> str:
        """Determine budget status"""
        if variance < -5:
            return 'under_budget'
        elif variance < 5:
            return 'on_budget'
        elif variance < 15:
            return 'over_budget'
        else:
            return 'critical_overrun'
    
    def _identify_cost_risks(self, project_data: Dict) -> List[str]:
        """Identify cost risk factors"""
        risks = []
        
        if project_data.get('change_orders', 0) > 5:
            risks.append("High number of change orders")
        if project_data.get('waste_cost', 0) > 10000:
            risks.append("Significant waste costs")
        if project_data.get('complexity_score', 0) > 0.7:
            risks.append("High project complexity")
        
        return risks
    
    def _generate_cost_recommendations(self, variance: float) -> List[str]:
        """Generate cost management recommendations"""
        recommendations = []
        
        if variance > 10:
            recommendations.append("Implement immediate cost control measures")
            recommendations.append("Review and reduce waste")
            recommendations.append("Negotiate better material prices")
        elif variance > 5:
            recommendations.append("Monitor costs closely")
            recommendations.append("Optimize resource allocation")
        
        return recommendations


class ResourceOptimizer:
    """
    Optimize resource allocation and scheduling
    """
    
    def __init__(self):
        """Initialize resource optimizer"""
        self.optimization_history = []
    
    def optimize_workforce(self, project_data: Dict) -> Dict:
        """
        Optimize workforce allocation
        
        Args:
            project_data: Current project data
            
        Returns:
            Optimization recommendations
        """
        tasks = project_data.get('tasks', [])
        available_workers = project_data.get('available_workers', [])
        
        # Calculate optimal allocation
        allocation = self._calculate_optimal_allocation(tasks, available_workers)
        
        # Calculate efficiency gain
        current_efficiency = project_data.get('current_efficiency', 0.7)
        optimized_efficiency = self._estimate_efficiency(allocation)
        efficiency_gain = optimized_efficiency - current_efficiency
        
        return {
            'optimal_allocation': allocation,
            'current_efficiency': current_efficiency,
            'optimized_efficiency': optimized_efficiency,
            'efficiency_gain_percentage': efficiency_gain * 100,
            'estimated_time_savings_hours': self._calculate_time_savings(
                efficiency_gain,
                len(tasks)
            ),
            'estimated_cost_savings': self._calculate_cost_savings(
                efficiency_gain,
                len(available_workers)
            ),
            'recommendations': self._generate_workforce_recommendations(allocation)
        }
    
    def optimize_material_delivery(self, project_data: Dict) -> Dict:
        """
        Optimize material delivery schedule
        
        Args:
            project_data: Project data with material requirements
            
        Returns:
            Optimized delivery schedule
        """
        materials = project_data.get('materials', [])
        schedule = project_data.get('schedule', [])
        
        # Calculate optimal delivery times
        delivery_schedule = self._calculate_delivery_schedule(materials, schedule)
        
        # Calculate storage savings
        storage_savings = self._calculate_storage_savings(delivery_schedule)
        
        return {
            'optimized_delivery_schedule': delivery_schedule,
            'storage_cost_savings': storage_savings,
            'just_in_time_percentage': self._calculate_jit_percentage(delivery_schedule),
            'recommendations': [
                "Implement just-in-time delivery for bulk materials",
                "Coordinate deliveries with construction schedule",
                "Reduce on-site storage requirements"
            ]
        }
    
    def _calculate_optimal_allocation(
        self,
        tasks: List[Dict],
        workers: List[Dict]
    ) -> List[Dict]:
        """Calculate optimal worker-task allocation"""
        # Simplified allocation - in production, use optimization algorithms
        allocation = []
        
        for task in tasks:
            required_skills = task.get('required_skills', [])
            # Find best matching worker
            best_worker = max(
                workers,
                key=lambda w: len(set(w.get('skills', [])) & set(required_skills)),
                default=None
            )
            
            if best_worker:
                allocation.append({
                    'task_id': task.get('id'),
                    'task_name': task.get('name'),
                    'worker_id': best_worker.get('id'),
                    'worker_name': best_worker.get('name'),
                    'skill_match_score': len(
                        set(best_worker.get('skills', [])) & set(required_skills)
                    ) / len(required_skills) if required_skills else 0
                })
        
        return allocation
    
    def _estimate_efficiency(self, allocation: List[Dict]) -> float:
        """Estimate efficiency from allocation"""
        if not allocation:
            return 0.5
        
        avg_skill_match = np.mean([
            a.get('skill_match_score', 0) for a in allocation
        ])
        
        return min(avg_skill_match * 1.2, 1.0)
    
    def _calculate_time_savings(self, efficiency_gain: float, num_tasks: int) -> float:
        """Calculate estimated time savings"""
        return efficiency_gain * num_tasks * 8  # 8 hours per task average
    
    def _calculate_cost_savings(self, efficiency_gain: float, num_workers: int) -> float:
        """Calculate estimated cost savings"""
        return efficiency_gain * num_workers * 75 * 40  # $75/hour, 40 hours/week
    
    def _generate_workforce_recommendations(self, allocation: List[Dict]) -> List[str]:
        """Generate workforce recommendations"""
        recommendations = []
        
        low_match_tasks = [
            a for a in allocation 
            if a.get('skill_match_score', 0) < 0.5
        ]
        
        if low_match_tasks:
            recommendations.append(
                f"Provide training for {len(low_match_tasks)} tasks with low skill match"
            )
        
        recommendations.append("Cross-train workers to increase flexibility")
        recommendations.append("Balance workload across team members")
        
        return recommendations
    
    def _calculate_delivery_schedule(
        self,
        materials: List[Dict],
        schedule: List[Dict]
    ) -> List[Dict]:
        """Calculate optimal delivery schedule"""
        # Simplified scheduling
        delivery_schedule = []
        
        for material in materials:
            needed_date = material.get('needed_date')
            delivery_schedule.append({
                'material': material.get('name'),
                'quantity': material.get('quantity'),
                'delivery_date': needed_date,
                'lead_time_days': material.get('lead_time', 7)
            })
        
        return delivery_schedule
    
    def _calculate_storage_savings(self, delivery_schedule: List[Dict]) -> float:
        """Calculate storage cost savings"""
        # Simplified calculation
        return len(delivery_schedule) * 100  # $100 per delivery optimized
    
    def _calculate_jit_percentage(self, delivery_schedule: List[Dict]) -> float:
        """Calculate just-in-time delivery percentage"""
        if not delivery_schedule:
            return 0.0
        
        # Simplified - in production, compare delivery vs needed dates
        return 0.75  # 75% JIT
