"""
Advanced Analytics and Business Intelligence Module for Lean Construction

This module provides comprehensive analytics capabilities:
- Real-time dashboards and KPIs
- Predictive analytics and trends
- Benchmarking and comparisons
- Custom reports and visualizations
- Data warehouse integration
- Executive decision support
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from abc import ABC, abstractmethod


# ============================================
# Enums and Data Classes
# ============================================

class MetricCategory(Enum):
    """Categories of metrics"""
    SCHEDULE = "schedule"
    COST = "cost"
    QUALITY = "quality"
    SAFETY = "safety"
    PRODUCTIVITY = "productivity"
    SUSTAINABILITY = "sustainability"
    RESOURCE = "resource"
    RISK = "risk"


class TimeGranularity(Enum):
    """Time granularity for aggregations"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirection(Enum):
    """Direction of trends"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"


class BenchmarkType(Enum):
    """Types of benchmarks"""
    INDUSTRY = "industry"
    HISTORICAL = "historical"
    PEER = "peer"
    TARGET = "target"
    BEST_IN_CLASS = "best_in_class"


class VisualizationType(Enum):
    """Types of visualizations"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    TABLE = "table"
    KPI_CARD = "kpi_card"


@dataclass
class KPI:
    """Key Performance Indicator"""
    id: str
    name: str
    category: MetricCategory
    value: float
    unit: str
    target: Optional[float]
    trend: TrendDirection
    change_percentage: float
    period: str
    benchmark: Optional[float] = None
    benchmark_type: Optional[BenchmarkType] = None
    
    def is_on_target(self) -> bool:
        """Check if KPI is meeting target"""
        if self.target is None:
            return True
        
        # Determine if higher or lower is better
        higher_is_better = self.category in [
            MetricCategory.PRODUCTIVITY, MetricCategory.QUALITY
        ]
        
        if higher_is_better:
            return self.value >= self.target
        return self.value <= self.target
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'value': self.value,
            'unit': self.unit,
            'target': self.target,
            'trend': self.trend.value,
            'change_percentage': self.change_percentage,
            'period': self.period,
            'is_on_target': self.is_on_target(),
            'benchmark': self.benchmark,
            'benchmark_type': self.benchmark_type.value if self.benchmark_type else None
        }


@dataclass
class MetricTimeSeries:
    """Time series data for a metric"""
    metric_name: str
    category: MetricCategory
    timestamps: List[datetime]
    values: List[float]
    unit: str
    granularity: TimeGranularity
    
    def get_statistics(self) -> Dict[str, float]:
        """Calculate statistics"""
        if not self.values:
            return {}
        
        return {
            'min': np.min(self.values),
            'max': np.max(self.values),
            'mean': np.mean(self.values),
            'median': np.median(self.values),
            'std': np.std(self.values),
            'current': self.values[-1] if self.values else None
        }
    
    def calculate_trend(self, window: int = 5) -> TrendDirection:
        """Calculate trend direction"""
        if len(self.values) < window:
            return TrendDirection.STABLE
        
        recent = self.values[-window:]
        slope = np.polyfit(range(len(recent)), recent, 1)[0]
        
        threshold = np.std(self.values) * 0.1
        
        if slope > threshold:
            return TrendDirection.IMPROVING
        elif slope < -threshold:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    id: str
    title: str
    widget_type: VisualizationType
    data_source: str
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 300  # seconds


@dataclass
class Dashboard:
    """Analytics dashboard"""
    id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    owner: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    tags: List[str] = field(default_factory=list)


# ============================================
# KPI Engine
# ============================================

class KPIEngine:
    """Engine for calculating and managing KPIs"""
    
    def __init__(self):
        self.kpi_definitions = self._initialize_kpi_definitions()
        self.kpi_history: Dict[str, List[Dict]] = defaultdict(list)
        self.targets: Dict[str, float] = {}
        self.benchmarks: Dict[str, Dict] = {}
    
    def _initialize_kpi_definitions(self) -> Dict[str, Dict]:
        """Initialize standard KPI definitions"""
        return {
            # Schedule KPIs
            'schedule_performance_index': {
                'name': 'Schedule Performance Index (SPI)',
                'category': MetricCategory.SCHEDULE,
                'unit': 'ratio',
                'formula': 'earned_value / planned_value',
                'target': 1.0,
                'higher_is_better': True
            },
            'schedule_variance': {
                'name': 'Schedule Variance (SV)',
                'category': MetricCategory.SCHEDULE,
                'unit': 'days',
                'formula': 'earned_value - planned_value',
                'target': 0,
                'higher_is_better': True
            },
            'milestone_completion_rate': {
                'name': 'Milestone Completion Rate',
                'category': MetricCategory.SCHEDULE,
                'unit': '%',
                'target': 100,
                'higher_is_better': True
            },
            
            # Cost KPIs
            'cost_performance_index': {
                'name': 'Cost Performance Index (CPI)',
                'category': MetricCategory.COST,
                'unit': 'ratio',
                'formula': 'earned_value / actual_cost',
                'target': 1.0,
                'higher_is_better': True
            },
            'budget_variance': {
                'name': 'Budget Variance',
                'category': MetricCategory.COST,
                'unit': '%',
                'target': 0,
                'higher_is_better': False
            },
            'estimate_at_completion': {
                'name': 'Estimate at Completion (EAC)',
                'category': MetricCategory.COST,
                'unit': '$',
                'higher_is_better': False
            },
            
            # Quality KPIs
            'defect_rate': {
                'name': 'Defect Rate',
                'category': MetricCategory.QUALITY,
                'unit': '%',
                'target': 0,
                'higher_is_better': False
            },
            'rework_percentage': {
                'name': 'Rework Percentage',
                'category': MetricCategory.QUALITY,
                'unit': '%',
                'target': 2,
                'higher_is_better': False
            },
            'first_time_quality': {
                'name': 'First Time Quality',
                'category': MetricCategory.QUALITY,
                'unit': '%',
                'target': 98,
                'higher_is_better': True
            },
            'punch_list_items': {
                'name': 'Punch List Items',
                'category': MetricCategory.QUALITY,
                'unit': 'count',
                'target': 0,
                'higher_is_better': False
            },
            
            # Safety KPIs
            'total_recordable_incident_rate': {
                'name': 'Total Recordable Incident Rate (TRIR)',
                'category': MetricCategory.SAFETY,
                'unit': 'per 200K hours',
                'target': 0,
                'higher_is_better': False
            },
            'lost_time_incident_rate': {
                'name': 'Lost Time Incident Rate (LTIR)',
                'category': MetricCategory.SAFETY,
                'unit': 'per 200K hours',
                'target': 0,
                'higher_is_better': False
            },
            'near_miss_frequency': {
                'name': 'Near Miss Frequency',
                'category': MetricCategory.SAFETY,
                'unit': 'count',
                'higher_is_better': False
            },
            'safety_observation_rate': {
                'name': 'Safety Observation Rate',
                'category': MetricCategory.SAFETY,
                'unit': 'per week',
                'target': 10,
                'higher_is_better': True
            },
            
            # Productivity KPIs
            'labor_productivity': {
                'name': 'Labor Productivity',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': 'units/hour',
                'higher_is_better': True
            },
            'equipment_utilization': {
                'name': 'Equipment Utilization',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': '%',
                'target': 85,
                'higher_is_better': True
            },
            'planned_percent_complete': {
                'name': 'Planned Percent Complete (PPC)',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': '%',
                'target': 85,
                'higher_is_better': True
            },
            
            # Lean/Waste KPIs
            'waste_elimination_rate': {
                'name': 'Waste Elimination Rate',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': '%',
                'target': 80,
                'higher_is_better': True
            },
            'value_added_ratio': {
                'name': 'Value Added Ratio',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': '%',
                'target': 50,
                'higher_is_better': True
            },
            'cycle_time_reduction': {
                'name': 'Cycle Time Reduction',
                'category': MetricCategory.PRODUCTIVITY,
                'unit': '%',
                'higher_is_better': True
            },
            
            # Sustainability KPIs
            'waste_diversion_rate': {
                'name': 'Waste Diversion Rate',
                'category': MetricCategory.SUSTAINABILITY,
                'unit': '%',
                'target': 75,
                'higher_is_better': True
            },
            'carbon_footprint': {
                'name': 'Carbon Footprint',
                'category': MetricCategory.SUSTAINABILITY,
                'unit': 'tons CO2',
                'higher_is_better': False
            },
            'water_usage_efficiency': {
                'name': 'Water Usage Efficiency',
                'category': MetricCategory.SUSTAINABILITY,
                'unit': 'gal/sq ft',
                'higher_is_better': False
            }
        }
    
    def calculate_kpi(
        self,
        kpi_id: str,
        project_data: Dict[str, Any],
        period: str = 'current'
    ) -> KPI:
        """Calculate a KPI value"""
        definition = self.kpi_definitions.get(kpi_id)
        if not definition:
            raise ValueError(f"Unknown KPI: {kpi_id}")
        
        # Calculate value based on KPI type
        value = self._calculate_kpi_value(kpi_id, project_data)
        
        # Get historical values for trend
        history = self.kpi_history.get(kpi_id, [])
        trend = self._calculate_trend(value, history, definition.get('higher_is_better', True))
        change = self._calculate_change(value, history)
        
        # Store history
        self.kpi_history[kpi_id].append({
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
            'period': period
        })
        
        return KPI(
            id=kpi_id,
            name=definition['name'],
            category=definition['category'],
            value=value,
            unit=definition['unit'],
            target=self.targets.get(kpi_id, definition.get('target')),
            trend=trend,
            change_percentage=change,
            period=period,
            benchmark=self.benchmarks.get(kpi_id, {}).get('value'),
            benchmark_type=BenchmarkType(self.benchmarks.get(kpi_id, {}).get('type', 'industry')) if kpi_id in self.benchmarks else None
        )
    
    def _calculate_kpi_value(self, kpi_id: str, data: Dict[str, Any]) -> float:
        """Calculate KPI value from project data"""
        # Implementation would vary based on KPI
        calculations = {
            'schedule_performance_index': lambda d: d.get('earned_value', 0) / max(d.get('planned_value', 1), 0.001),
            'cost_performance_index': lambda d: d.get('earned_value', 0) / max(d.get('actual_cost', 1), 0.001),
            'budget_variance': lambda d: ((d.get('actual_cost', 0) - d.get('budget', 1)) / max(d.get('budget', 1), 0.001)) * 100,
            'defect_rate': lambda d: (d.get('defects', 0) / max(d.get('total_items', 1), 1)) * 100,
            'rework_percentage': lambda d: (d.get('rework_hours', 0) / max(d.get('total_hours', 1), 1)) * 100,
            'first_time_quality': lambda d: 100 - d.get('defect_rate', 0),
            'total_recordable_incident_rate': lambda d: (d.get('recordable_incidents', 0) * 200000) / max(d.get('total_hours_worked', 1), 1),
            'equipment_utilization': lambda d: (d.get('equipment_active_hours', 0) / max(d.get('equipment_available_hours', 1), 1)) * 100,
            'planned_percent_complete': lambda d: (d.get('tasks_completed', 0) / max(d.get('tasks_planned', 1), 1)) * 100,
            'waste_diversion_rate': lambda d: (d.get('waste_diverted', 0) / max(d.get('total_waste', 1), 1)) * 100,
            'labor_productivity': lambda d: d.get('units_completed', 0) / max(d.get('labor_hours', 1), 1),
            'value_added_ratio': lambda d: (d.get('value_adding_time', 0) / max(d.get('total_time', 1), 1)) * 100
        }
        
        if kpi_id in calculations:
            try:
                return calculations[kpi_id](data)
            except (ZeroDivisionError, TypeError):
                return 0.0
        
        # Default: try to get value directly from data
        return float(data.get(kpi_id, 0))
    
    def _calculate_trend(
        self,
        current_value: float,
        history: List[Dict],
        higher_is_better: bool
    ) -> TrendDirection:
        """Calculate trend direction"""
        if len(history) < 3:
            return TrendDirection.STABLE
        
        recent_values = [h['value'] for h in history[-5:]]
        recent_values.append(current_value)
        
        # Simple linear regression
        slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
        threshold = np.std(recent_values) * 0.1 if np.std(recent_values) > 0 else 0.01
        
        if (slope > threshold and higher_is_better) or (slope < -threshold and not higher_is_better):
            return TrendDirection.IMPROVING
        elif (slope < -threshold and higher_is_better) or (slope > threshold and not higher_is_better):
            return TrendDirection.DECLINING
        return TrendDirection.STABLE
    
    def _calculate_change(self, current_value: float, history: List[Dict]) -> float:
        """Calculate percentage change from previous period"""
        if not history:
            return 0.0
        
        previous = history[-1]['value']
        if previous == 0:
            return 100.0 if current_value > 0 else 0.0
        
        return ((current_value - previous) / abs(previous)) * 100
    
    def set_target(self, kpi_id: str, target: float):
        """Set target for a KPI"""
        self.targets[kpi_id] = target
    
    def set_benchmark(self, kpi_id: str, value: float, benchmark_type: BenchmarkType):
        """Set benchmark for a KPI"""
        self.benchmarks[kpi_id] = {
            'value': value,
            'type': benchmark_type.value
        }
    
    def get_all_kpis(
        self,
        project_data: Dict[str, Any],
        categories: Optional[List[MetricCategory]] = None
    ) -> List[KPI]:
        """Get all KPIs for a project"""
        kpis = []
        
        for kpi_id in self.kpi_definitions:
            if categories:
                if self.kpi_definitions[kpi_id]['category'] not in categories:
                    continue
            
            try:
                kpi = self.calculate_kpi(kpi_id, project_data)
                kpis.append(kpi)
            except Exception:
                continue
        
        return kpis


# ============================================
# Trend Analysis Engine
# ============================================

class TrendAnalysisEngine:
    """Engine for analyzing trends and forecasting"""
    
    def __init__(self):
        self.time_series_data: Dict[str, MetricTimeSeries] = {}
    
    def add_data_point(
        self,
        metric_name: str,
        category: MetricCategory,
        timestamp: datetime,
        value: float,
        unit: str = ''
    ):
        """Add a data point to time series"""
        if metric_name not in self.time_series_data:
            self.time_series_data[metric_name] = MetricTimeSeries(
                metric_name=metric_name,
                category=category,
                timestamps=[],
                values=[],
                unit=unit,
                granularity=TimeGranularity.DAILY
            )
        
        ts = self.time_series_data[metric_name]
        ts.timestamps.append(timestamp)
        ts.values.append(value)
    
    def analyze_trend(
        self,
        metric_name: str,
        forecast_periods: int = 7
    ) -> Dict[str, Any]:
        """Analyze trend and generate forecast"""
        ts = self.time_series_data.get(metric_name)
        if not ts or len(ts.values) < 5:
            return {'error': 'Insufficient data'}
        
        values = np.array(ts.values)
        x = np.arange(len(values))
        
        # Linear trend
        slope, intercept = np.polyfit(x, values, 1)
        linear_forecast = [slope * (len(values) + i) + intercept for i in range(forecast_periods)]
        
        # Moving average
        window = min(7, len(values) // 2)
        ma = np.convolve(values, np.ones(window)/window, mode='valid')
        
        # Seasonality detection (simple)
        if len(values) >= 14:
            daily_pattern = self._detect_seasonality(values, 7)
        else:
            daily_pattern = None
        
        # Anomaly detection
        mean = np.mean(values)
        std = np.std(values)
        anomalies = []
        for i, v in enumerate(values):
            if abs(v - mean) > 2 * std:
                anomalies.append({
                    'index': i,
                    'timestamp': ts.timestamps[i].isoformat(),
                    'value': v,
                    'deviation': (v - mean) / std
                })
        
        return {
            'metric_name': metric_name,
            'data_points': len(values),
            'statistics': ts.get_statistics(),
            'trend': {
                'direction': ts.calculate_trend().value,
                'slope': slope,
                'interpretation': self._interpret_trend(slope, values)
            },
            'forecast': {
                'periods': forecast_periods,
                'values': linear_forecast,
                'confidence': 0.8 if len(values) > 20 else 0.6
            },
            'moving_average': ma.tolist()[-7:] if len(ma) > 0 else [],
            'seasonality': daily_pattern,
            'anomalies': anomalies
        }
    
    def _detect_seasonality(self, values: np.ndarray, period: int) -> Optional[Dict]:
        """Simple seasonality detection"""
        if len(values) < period * 2:
            return None
        
        # Calculate average for each position in period
        seasonal_pattern = []
        for i in range(period):
            positions = range(i, len(values), period)
            avg = np.mean([values[p] for p in positions if p < len(values)])
            seasonal_pattern.append(avg)
        
        # Check if pattern has significant variation
        if np.std(seasonal_pattern) / np.mean(values) > 0.1:
            return {
                'period': period,
                'pattern': seasonal_pattern,
                'strength': float(np.std(seasonal_pattern) / np.mean(values))
            }
        
        return None
    
    def _interpret_trend(self, slope: float, values: np.ndarray) -> str:
        """Generate human-readable trend interpretation"""
        mean = np.mean(values)
        percent_change = (slope / mean) * 100 if mean != 0 else 0
        
        if abs(percent_change) < 1:
            return "The metric is relatively stable with minimal change"
        elif percent_change > 5:
            return f"Strong upward trend, increasing approximately {percent_change:.1f}% per period"
        elif percent_change > 0:
            return f"Gradual upward trend, increasing approximately {percent_change:.1f}% per period"
        elif percent_change < -5:
            return f"Strong downward trend, decreasing approximately {abs(percent_change):.1f}% per period"
        else:
            return f"Gradual downward trend, decreasing approximately {abs(percent_change):.1f}% per period"
    
    def compare_periods(
        self,
        metric_name: str,
        period_1: Tuple[datetime, datetime],
        period_2: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Compare metrics between two periods"""
        ts = self.time_series_data.get(metric_name)
        if not ts:
            return {'error': 'Metric not found'}
        
        def get_period_values(start: datetime, end: datetime) -> List[float]:
            values = []
            for i, t in enumerate(ts.timestamps):
                if start <= t <= end:
                    values.append(ts.values[i])
            return values
        
        p1_values = get_period_values(*period_1)
        p2_values = get_period_values(*period_2)
        
        if not p1_values or not p2_values:
            return {'error': 'Insufficient data for comparison'}
        
        p1_mean = np.mean(p1_values)
        p2_mean = np.mean(p2_values)
        
        change = ((p2_mean - p1_mean) / p1_mean) * 100 if p1_mean != 0 else 0
        
        return {
            'metric_name': metric_name,
            'period_1': {
                'start': period_1[0].isoformat(),
                'end': period_1[1].isoformat(),
                'mean': p1_mean,
                'min': np.min(p1_values),
                'max': np.max(p1_values),
                'count': len(p1_values)
            },
            'period_2': {
                'start': period_2[0].isoformat(),
                'end': period_2[1].isoformat(),
                'mean': p2_mean,
                'min': np.min(p2_values),
                'max': np.max(p2_values),
                'count': len(p2_values)
            },
            'comparison': {
                'absolute_change': p2_mean - p1_mean,
                'percent_change': change,
                'improved': change > 0  # Assumes higher is better
            }
        }


# ============================================
# Benchmarking Engine
# ============================================

class BenchmarkingEngine:
    """Engine for comparing performance against benchmarks"""
    
    def __init__(self):
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        self.project_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def _initialize_industry_benchmarks(self) -> Dict[str, Dict]:
        """Initialize industry standard benchmarks"""
        return {
            'schedule_performance_index': {
                'industry_avg': 0.95,
                'best_in_class': 1.05,
                'poor_threshold': 0.85
            },
            'cost_performance_index': {
                'industry_avg': 0.92,
                'best_in_class': 1.02,
                'poor_threshold': 0.85
            },
            'defect_rate': {
                'industry_avg': 3.5,
                'best_in_class': 1.0,
                'poor_threshold': 7.0
            },
            'rework_percentage': {
                'industry_avg': 5.0,
                'best_in_class': 2.0,
                'poor_threshold': 10.0
            },
            'total_recordable_incident_rate': {
                'industry_avg': 3.0,
                'best_in_class': 0.5,
                'poor_threshold': 5.0
            },
            'equipment_utilization': {
                'industry_avg': 70.0,
                'best_in_class': 90.0,
                'poor_threshold': 50.0
            },
            'planned_percent_complete': {
                'industry_avg': 75.0,
                'best_in_class': 90.0,
                'poor_threshold': 60.0
            },
            'waste_diversion_rate': {
                'industry_avg': 50.0,
                'best_in_class': 85.0,
                'poor_threshold': 30.0
            }
        }
    
    def benchmark_project(
        self,
        project_id: str,
        project_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Benchmark a project against industry standards"""
        results = {
            'project_id': project_id,
            'benchmarked_at': datetime.utcnow().isoformat(),
            'metrics': {},
            'overall_score': 0,
            'ranking': 'average',
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        scores = []
        
        for metric_id, value in project_metrics.items():
            if metric_id in self.industry_benchmarks:
                benchmark = self.industry_benchmarks[metric_id]
                
                # Determine if higher or lower is better
                higher_is_better = metric_id in [
                    'schedule_performance_index', 'cost_performance_index',
                    'equipment_utilization', 'planned_percent_complete',
                    'waste_diversion_rate', 'first_time_quality'
                ]
                
                # Calculate percentile
                if higher_is_better:
                    if value >= benchmark['best_in_class']:
                        percentile = 95
                    elif value >= benchmark['industry_avg']:
                        percentile = 50 + 45 * (value - benchmark['industry_avg']) / (benchmark['best_in_class'] - benchmark['industry_avg'])
                    elif value >= benchmark['poor_threshold']:
                        percentile = 25 + 25 * (value - benchmark['poor_threshold']) / (benchmark['industry_avg'] - benchmark['poor_threshold'])
                    else:
                        percentile = 25 * value / benchmark['poor_threshold']
                else:
                    if value <= benchmark['best_in_class']:
                        percentile = 95
                    elif value <= benchmark['industry_avg']:
                        percentile = 50 + 45 * (benchmark['industry_avg'] - value) / (benchmark['industry_avg'] - benchmark['best_in_class'])
                    elif value <= benchmark['poor_threshold']:
                        percentile = 25 + 25 * (benchmark['poor_threshold'] - value) / (benchmark['poor_threshold'] - benchmark['industry_avg'])
                    else:
                        percentile = max(0, 25 * (1 - (value - benchmark['poor_threshold']) / benchmark['poor_threshold']))
                
                percentile = max(0, min(100, percentile))
                scores.append(percentile)
                
                results['metrics'][metric_id] = {
                    'value': value,
                    'industry_avg': benchmark['industry_avg'],
                    'best_in_class': benchmark['best_in_class'],
                    'percentile': percentile,
                    'status': 'excellent' if percentile >= 80 else 'good' if percentile >= 50 else 'needs_improvement'
                }
                
                # Track strengths and weaknesses
                if percentile >= 80:
                    results['strengths'].append(metric_id)
                elif percentile < 40:
                    results['weaknesses'].append(metric_id)
                    results['recommendations'].append(
                        f"Improve {metric_id.replace('_', ' ')}: current value {value:.2f} vs industry avg {benchmark['industry_avg']:.2f}"
                    )
        
        # Calculate overall score
        if scores:
            results['overall_score'] = np.mean(scores)
            
            if results['overall_score'] >= 80:
                results['ranking'] = 'excellent'
            elif results['overall_score'] >= 60:
                results['ranking'] = 'above_average'
            elif results['overall_score'] >= 40:
                results['ranking'] = 'average'
            else:
                results['ranking'] = 'below_average'
        
        # Store in history
        self.project_history[project_id].append(results)
        
        return results
    
    def compare_projects(
        self,
        project_ids: List[str],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple projects"""
        comparison = {
            'projects': project_ids,
            'metrics': {},
            'rankings': {}
        }
        
        for metric in metrics:
            metric_values = []
            
            for project_id in project_ids:
                history = self.project_history.get(project_id, [])
                if history and metric in history[-1].get('metrics', {}):
                    metric_values.append({
                        'project_id': project_id,
                        'value': history[-1]['metrics'][metric]['value'],
                        'percentile': history[-1]['metrics'][metric]['percentile']
                    })
            
            if metric_values:
                # Sort by percentile
                sorted_values = sorted(metric_values, key=lambda x: x['percentile'], reverse=True)
                
                comparison['metrics'][metric] = {
                    'values': sorted_values,
                    'best': sorted_values[0]['project_id'],
                    'avg_value': np.mean([v['value'] for v in sorted_values])
                }
        
        # Overall project rankings
        for project_id in project_ids:
            history = self.project_history.get(project_id, [])
            if history:
                comparison['rankings'][project_id] = history[-1].get('overall_score', 0)
        
        return comparison


# ============================================
# Dashboard Manager
# ============================================

class DashboardManager:
    """Manages analytics dashboards"""
    
    def __init__(self, kpi_engine: KPIEngine, trend_engine: TrendAnalysisEngine):
        self.kpi_engine = kpi_engine
        self.trend_engine = trend_engine
        self.dashboards: Dict[str, Dashboard] = {}
        self.widget_templates = self._initialize_widget_templates()
    
    def _initialize_widget_templates(self) -> Dict[str, Dict]:
        """Initialize standard widget templates"""
        return {
            'schedule_kpis': {
                'title': 'Schedule Performance',
                'widget_type': VisualizationType.KPI_CARD,
                'data_source': 'kpi:schedule',
                'position': {'x': 0, 'y': 0, 'width': 3, 'height': 2}
            },
            'cost_kpis': {
                'title': 'Cost Performance',
                'widget_type': VisualizationType.KPI_CARD,
                'data_source': 'kpi:cost',
                'position': {'x': 3, 'y': 0, 'width': 3, 'height': 2}
            },
            'safety_gauge': {
                'title': 'Safety Score',
                'widget_type': VisualizationType.GAUGE,
                'data_source': 'metric:safety_score',
                'position': {'x': 6, 'y': 0, 'width': 2, 'height': 2}
            },
            'progress_trend': {
                'title': 'Progress Trend',
                'widget_type': VisualizationType.LINE_CHART,
                'data_source': 'trend:progress',
                'position': {'x': 0, 'y': 2, 'width': 6, 'height': 3}
            },
            'waste_breakdown': {
                'title': 'Waste Analysis',
                'widget_type': VisualizationType.PIE_CHART,
                'data_source': 'waste:breakdown',
                'position': {'x': 6, 'y': 2, 'width': 3, 'height': 3}
            },
            'alerts_table': {
                'title': 'Active Alerts',
                'widget_type': VisualizationType.TABLE,
                'data_source': 'alerts:active',
                'position': {'x': 0, 'y': 5, 'width': 4, 'height': 2}
            },
            'resource_heatmap': {
                'title': 'Resource Utilization',
                'widget_type': VisualizationType.HEATMAP,
                'data_source': 'resources:utilization',
                'position': {'x': 4, 'y': 5, 'width': 5, 'height': 2}
            }
        }
    
    def create_dashboard(
        self,
        name: str,
        description: str,
        owner: str,
        template: str = 'executive'
    ) -> Dashboard:
        """Create a new dashboard"""
        # Create widgets based on template
        widgets = []
        
        if template == 'executive':
            templates_to_use = ['schedule_kpis', 'cost_kpis', 'safety_gauge', 
                              'progress_trend', 'waste_breakdown']
        elif template == 'operations':
            templates_to_use = ['progress_trend', 'resource_heatmap', 
                              'alerts_table', 'waste_breakdown']
        elif template == 'safety':
            templates_to_use = ['safety_gauge', 'alerts_table']
        else:
            templates_to_use = list(self.widget_templates.keys())
        
        for template_name in templates_to_use:
            if template_name in self.widget_templates:
                widget_config = self.widget_templates[template_name]
                widgets.append(DashboardWidget(
                    id=str(uuid.uuid4()),
                    title=widget_config['title'],
                    widget_type=widget_config['widget_type'],
                    data_source=widget_config['data_source'],
                    position=widget_config['position'].copy()
                ))
        
        dashboard = Dashboard(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            widgets=widgets,
            owner=owner,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.dashboards[dashboard.id] = dashboard
        return dashboard
    
    def get_dashboard_data(
        self,
        dashboard_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get data for all widgets in a dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {'error': 'Dashboard not found'}
        
        widget_data = {}
        
        for widget in dashboard.widgets:
            widget_data[widget.id] = self._get_widget_data(widget, project_data)
        
        return {
            'dashboard_id': dashboard_id,
            'name': dashboard.name,
            'widgets': widget_data,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _get_widget_data(
        self,
        widget: DashboardWidget,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get data for a single widget"""
        data_source = widget.data_source
        
        if data_source.startswith('kpi:'):
            category_name = data_source.split(':')[1]
            try:
                category = MetricCategory(category_name)
                kpis = self.kpi_engine.get_all_kpis(project_data, [category])
                return {
                    'type': 'kpis',
                    'data': [kpi.to_dict() for kpi in kpis]
                }
            except (ValueError, KeyError):
                return {'error': f'Unknown category: {category_name}'}
        
        elif data_source.startswith('trend:'):
            metric_name = data_source.split(':')[1]
            return {
                'type': 'trend',
                'data': self.trend_engine.analyze_trend(metric_name)
            }
        
        elif data_source.startswith('metric:'):
            metric_name = data_source.split(':')[1]
            value = project_data.get(metric_name, 0)
            return {
                'type': 'metric',
                'data': {'name': metric_name, 'value': value}
            }
        
        else:
            return {'type': 'static', 'data': project_data.get(data_source, {})}
    
    def add_widget(
        self,
        dashboard_id: str,
        widget_template: str,
        position: Optional[Dict[str, int]] = None
    ) -> Optional[DashboardWidget]:
        """Add a widget to a dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        template = self.widget_templates.get(widget_template)
        if not template:
            return None
        
        widget = DashboardWidget(
            id=str(uuid.uuid4()),
            title=template['title'],
            widget_type=template['widget_type'],
            data_source=template['data_source'],
            position=position or template['position'].copy()
        )
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.utcnow()
        
        return widget


# ============================================
# Executive Decision Support
# ============================================

class ExecutiveDecisionSupport:
    """Provides executive-level insights and recommendations"""
    
    def __init__(
        self,
        kpi_engine: KPIEngine,
        benchmark_engine: BenchmarkingEngine,
        trend_engine: TrendAnalysisEngine
    ):
        self.kpi_engine = kpi_engine
        self.benchmark_engine = benchmark_engine
        self.trend_engine = trend_engine
    
    def generate_executive_summary(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary for a project"""
        # Calculate key KPIs
        kpis = self.kpi_engine.get_all_kpis(project_data)
        
        # Categorize KPIs
        critical = []
        warning = []
        on_track = []
        
        for kpi in kpis:
            if not kpi.is_on_target():
                if kpi.trend == TrendDirection.DECLINING:
                    critical.append(kpi)
                else:
                    warning.append(kpi)
            else:
                on_track.append(kpi)
        
        # Generate overall status
        if critical:
            overall_status = 'critical'
            status_message = f"{len(critical)} critical issues require immediate attention"
        elif warning:
            overall_status = 'warning'
            status_message = f"{len(warning)} metrics below target"
        else:
            overall_status = 'healthy'
            status_message = "All key metrics on track"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(kpis, project_data)
        
        return {
            'project_id': project_data.get('project_id'),
            'project_name': project_data.get('project_name'),
            'generated_at': datetime.utcnow().isoformat(),
            'overall_status': overall_status,
            'status_message': status_message,
            'kpi_summary': {
                'on_track': len(on_track),
                'warning': len(warning),
                'critical': len(critical)
            },
            'critical_items': [kpi.to_dict() for kpi in critical],
            'warning_items': [kpi.to_dict() for kpi in warning[:5]],  # Top 5
            'key_highlights': self._generate_highlights(kpis, project_data),
            'recommendations': recommendations,
            'next_review': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    
    def _generate_recommendations(
        self,
        kpis: List[KPI],
        project_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for kpi in kpis:
            if not kpi.is_on_target():
                recommendation = self._get_recommendation_for_kpi(kpi)
                if recommendation:
                    recommendations.append(recommendation)
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.get('priority', 5))
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _get_recommendation_for_kpi(self, kpi: KPI) -> Optional[Dict[str, Any]]:
        """Get recommendation for a specific KPI"""
        recommendations = {
            'schedule_performance_index': {
                'action': 'Review critical path activities and consider fast-tracking',
                'priority': 1,
                'category': 'schedule'
            },
            'cost_performance_index': {
                'action': 'Analyze cost variances and identify areas for cost reduction',
                'priority': 1,
                'category': 'cost'
            },
            'defect_rate': {
                'action': 'Implement additional QA checkpoints and training',
                'priority': 2,
                'category': 'quality'
            },
            'total_recordable_incident_rate': {
                'action': 'Conduct safety stand-down and review safety procedures',
                'priority': 1,
                'category': 'safety'
            },
            'equipment_utilization': {
                'action': 'Optimize equipment scheduling and reduce idle time',
                'priority': 3,
                'category': 'productivity'
            },
            'planned_percent_complete': {
                'action': 'Review weekly work plans and identify constraint removal opportunities',
                'priority': 2,
                'category': 'productivity'
            }
        }
        
        if kpi.id in recommendations:
            rec = recommendations[kpi.id].copy()
            rec['kpi_id'] = kpi.id
            rec['kpi_name'] = kpi.name
            rec['current_value'] = kpi.value
            rec['target'] = kpi.target
            rec['gap'] = abs(kpi.value - kpi.target) if kpi.target else 0
            return rec
        
        return None
    
    def _generate_highlights(
        self,
        kpis: List[KPI],
        project_data: Dict[str, Any]
    ) -> List[str]:
        """Generate key highlights"""
        highlights = []
        
        # Best performing KPIs
        if kpis:
            sorted_kpis = sorted(
                [k for k in kpis if k.target is not None],
                key=lambda k: k.value / k.target if k.target else 0,
                reverse=True
            )
            
            if sorted_kpis:
                best = sorted_kpis[0]
                highlights.append(
                    f"Top performer: {best.name} at {best.value:.1f}{best.unit} "
                    f"({((best.value / best.target - 1) * 100):.0f}% above target)"
                )
        
        # Improving metrics
        improving = [k for k in kpis if k.trend == TrendDirection.IMPROVING]
        if improving:
            highlights.append(f"{len(improving)} metrics showing improvement")
        
        # Project completion
        completion = project_data.get('completion_percentage', 0)
        if completion > 0:
            highlights.append(f"Project {completion:.0f}% complete")
        
        return highlights


# ============================================
# Analytics BI Integration System
# ============================================

class AnalyticsBISystem:
    """Integrated Analytics and Business Intelligence System"""
    
    def __init__(self):
        self.kpi_engine = KPIEngine()
        self.trend_engine = TrendAnalysisEngine()
        self.benchmark_engine = BenchmarkingEngine()
        self.dashboard_manager = DashboardManager(self.kpi_engine, self.trend_engine)
        self.decision_support = ExecutiveDecisionSupport(
            self.kpi_engine,
            self.benchmark_engine,
            self.trend_engine
        )
    
    def get_project_analytics(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a project"""
        project_id = project_data.get('project_id', 'unknown')
        
        # Calculate all KPIs
        kpis = self.kpi_engine.get_all_kpis(project_data)
        
        # Benchmark project
        project_metrics = {kpi.id: kpi.value for kpi in kpis}
        benchmark_results = self.benchmark_engine.benchmark_project(
            project_id,
            project_metrics
        )
        
        # Generate executive summary
        exec_summary = self.decision_support.generate_executive_summary(project_data)
        
        return {
            'project_id': project_id,
            'generated_at': datetime.utcnow().isoformat(),
            'kpis': {
                'by_category': self._group_kpis_by_category(kpis),
                'summary': {
                    'total': len(kpis),
                    'on_target': sum(1 for k in kpis if k.is_on_target()),
                    'off_target': sum(1 for k in kpis if not k.is_on_target())
                }
            },
            'benchmarking': benchmark_results,
            'executive_summary': exec_summary,
            'insights': self._generate_insights(kpis, benchmark_results)
        }
    
    def _group_kpis_by_category(self, kpis: List[KPI]) -> Dict[str, List[Dict]]:
        """Group KPIs by category"""
        grouped = defaultdict(list)
        for kpi in kpis:
            grouped[kpi.category.value].append(kpi.to_dict())
        return dict(grouped)
    
    def _generate_insights(
        self,
        kpis: List[KPI],
        benchmark: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate data-driven insights"""
        insights = []
        
        # Performance vs industry
        overall_score = benchmark.get('overall_score', 50)
        if overall_score >= 80:
            insights.append({
                'type': 'positive',
                'message': 'Project performs in the top 20% of industry benchmarks',
                'impact': 'high'
            })
        elif overall_score < 40:
            insights.append({
                'type': 'negative',
                'message': 'Project performance is below industry average',
                'impact': 'high'
            })
        
        # Trend-based insights
        declining = [k for k in kpis if k.trend == TrendDirection.DECLINING]
        if declining:
            insights.append({
                'type': 'warning',
                'message': f'{len(declining)} metrics showing declining trends: {", ".join(k.name for k in declining[:3])}',
                'impact': 'medium'
            })
        
        return insights
    
    def create_executive_dashboard(
        self,
        name: str,
        owner: str
    ) -> Dashboard:
        """Create an executive dashboard"""
        return self.dashboard_manager.create_dashboard(
            name=name,
            description="Executive overview dashboard",
            owner=owner,
            template='executive'
        )
    
    def get_dashboard_data(
        self,
        dashboard_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get dashboard data"""
        return self.dashboard_manager.get_dashboard_data(dashboard_id, project_data)
    
    def get_trend_analysis(
        self,
        metric_name: str,
        forecast_periods: int = 7
    ) -> Dict[str, Any]:
        """Get trend analysis for a metric"""
        return self.trend_engine.analyze_trend(metric_name, forecast_periods)
    
    def get_bi_summary(self) -> Dict[str, Any]:
        """Get BI system summary"""
        return {
            'available_kpis': list(self.kpi_engine.kpi_definitions.keys()),
            'kpi_categories': [c.value for c in MetricCategory],
            'dashboards': [
                {
                    'id': d.id,
                    'name': d.name,
                    'widgets': len(d.widgets)
                }
                for d in self.dashboard_manager.dashboards.values()
            ],
            'benchmark_metrics': list(self.benchmark_engine.industry_benchmarks.keys()),
            'visualization_types': [v.value for v in VisualizationType]
        }


# Create singleton instance
analytics_bi_system = AnalyticsBISystem()


# ============================================
# Convenience Functions
# ============================================

def get_project_kpis(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all KPIs for a project"""
    kpis = analytics_bi_system.kpi_engine.get_all_kpis(project_data)
    return [kpi.to_dict() for kpi in kpis]


def benchmark_project(
    project_id: str,
    project_metrics: Dict[str, float]
) -> Dict[str, Any]:
    """Benchmark a project"""
    return analytics_bi_system.benchmark_engine.benchmark_project(
        project_id,
        project_metrics
    )


def get_executive_summary(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get executive summary"""
    return analytics_bi_system.decision_support.generate_executive_summary(project_data)