"""
Infrastructure Scaling Module for Lean Construction AI

This module provides infrastructure management for larger deployments:
- Horizontal scaling configurations
- Database sharding strategies
- Caching layer management
- Load balancing configurations
- Message queue scaling
- Container orchestration configs
- Performance monitoring
- Auto-scaling policies
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


# ============================================
# Enums and Data Classes
# ============================================

class ScalingStrategy(Enum):
    """Scaling strategies"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"
    MANUAL = "manual"


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


class ServiceType(Enum):
    """Types of services"""
    API = "api"
    WORKER = "worker"
    ML_INFERENCE = "ml_inference"
    ML_TRAINING = "ml_training"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"


class HealthStatus(Enum):
    """Health status of services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DatabaseType(Enum):
    """Database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    TIMESCALEDB = "timescaledb"


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    id: str
    name: str
    service_type: ServiceType
    instances: int
    min_instances: int
    max_instances: int
    cpu_limit: str
    memory_limit: str
    environment: DeploymentEnvironment
    health_check_path: str = "/health"
    scaling_strategy: ScalingStrategy = ScalingStrategy.AUTO
    labels: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)


@dataclass
class ScalingPolicy:
    """Auto-scaling policy"""
    id: str
    name: str
    service_id: str
    metric_type: str  # cpu, memory, requests_per_second, queue_depth
    threshold_up: float
    threshold_down: float
    scale_up_by: int
    scale_down_by: int
    cooldown_seconds: int
    enabled: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration"""
    id: str
    name: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    connection_pool_size: int
    max_overflow: int
    read_replicas: List[str] = field(default_factory=list)
    sharding_enabled: bool = False
    shard_key: Optional[str] = None


@dataclass
class CacheConfig:
    """Cache configuration"""
    id: str
    name: str
    host: str
    port: int
    cluster_mode: bool
    nodes: List[str] = field(default_factory=list)
    max_memory: str = "1gb"
    eviction_policy: str = "allkeys-lru"
    ttl_default: int = 3600


# ============================================
# Service Registry
# ============================================

class ServiceRegistry:
    """Registry for managing services"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.metrics: Dict[str, List[Dict]] = {}
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """Initialize default service configurations"""
        
        # API Service
        self.register_service(ServiceConfig(
            id='api-service',
            name='Lean Construction API',
            service_type=ServiceType.API,
            instances=3,
            min_instances=2,
            max_instances=10,
            cpu_limit='1000m',
            memory_limit='2Gi',
            environment=DeploymentEnvironment.PRODUCTION,
            health_check_path='/health',
            scaling_strategy=ScalingStrategy.AUTO,
            labels={'app': 'lean-construction', 'tier': 'api'},
            env_vars={
                'LOG_LEVEL': 'INFO',
                'WORKERS': '4'
            }
        ))
        
        # ML Inference Service
        self.register_service(ServiceConfig(
            id='ml-inference',
            name='ML Inference Service',
            service_type=ServiceType.ML_INFERENCE,
            instances=2,
            min_instances=1,
            max_instances=5,
            cpu_limit='2000m',
            memory_limit='4Gi',
            environment=DeploymentEnvironment.PRODUCTION,
            health_check_path='/health',
            scaling_strategy=ScalingStrategy.AUTO,
            labels={'app': 'lean-construction', 'tier': 'ml'},
            env_vars={
                'MODEL_CACHE': 'true',
                'BATCH_SIZE': '32'
            }
        ))
        
        # Celery Workers
        self.register_service(ServiceConfig(
            id='celery-worker',
            name='Celery Background Workers',
            service_type=ServiceType.WORKER,
            instances=4,
            min_instances=2,
            max_instances=20,
            cpu_limit='1000m',
            memory_limit='2Gi',
            environment=DeploymentEnvironment.PRODUCTION,
            scaling_strategy=ScalingStrategy.AUTO,
            labels={'app': 'lean-construction', 'tier': 'worker'},
            env_vars={
                'CELERY_CONCURRENCY': '4'
            }
        ))
    
    def register_service(self, config: ServiceConfig):
        """Register a service"""
        self.services[config.id] = config
        self.health_status[config.id] = HealthStatus.UNKNOWN
    
    def get_service(self, service_id: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self.services.get(service_id)
    
    def update_health(self, service_id: str, status: HealthStatus):
        """Update service health status"""
        if service_id in self.services:
            self.health_status[service_id] = status
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services with status"""
        result = []
        for service_id, config in self.services.items():
            result.append({
                'id': config.id,
                'name': config.name,
                'type': config.service_type.value,
                'instances': config.instances,
                'health': self.health_status.get(service_id, HealthStatus.UNKNOWN).value
            })
        return result


# ============================================
# Auto Scaling Manager
# ============================================

class AutoScalingManager:
    """Manages auto-scaling policies and decisions"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.policies: Dict[str, ScalingPolicy] = {}
        self.scaling_history: List[Dict] = []
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default scaling policies"""
        
        # API CPU-based scaling
        self.create_policy(ScalingPolicy(
            id='api-cpu-scaling',
            name='API CPU Scaling',
            service_id='api-service',
            metric_type='cpu',
            threshold_up=70,
            threshold_down=30,
            scale_up_by=2,
            scale_down_by=1,
            cooldown_seconds=300
        ))
        
        # API request-based scaling
        self.create_policy(ScalingPolicy(
            id='api-requests-scaling',
            name='API Request Rate Scaling',
            service_id='api-service',
            metric_type='requests_per_second',
            threshold_up=1000,
            threshold_down=200,
            scale_up_by=1,
            scale_down_by=1,
            cooldown_seconds=180
        ))
        
        # Worker queue-based scaling
        self.create_policy(ScalingPolicy(
            id='worker-queue-scaling',
            name='Worker Queue Depth Scaling',
            service_id='celery-worker',
            metric_type='queue_depth',
            threshold_up=100,
            threshold_down=10,
            scale_up_by=2,
            scale_down_by=1,
            cooldown_seconds=120
        ))
        
        # ML inference memory-based scaling
        self.create_policy(ScalingPolicy(
            id='ml-memory-scaling',
            name='ML Inference Memory Scaling',
            service_id='ml-inference',
            metric_type='memory',
            threshold_up=80,
            threshold_down=40,
            scale_up_by=1,
            scale_down_by=1,
            cooldown_seconds=600
        ))
    
    def create_policy(self, policy: ScalingPolicy):
        """Create a scaling policy"""
        self.policies[policy.id] = policy
    
    def evaluate_scaling(
        self,
        service_id: str,
        current_metrics: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate if scaling is needed"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return None
        
        # Find applicable policies
        applicable_policies = [
            p for p in self.policies.values()
            if p.service_id == service_id and p.enabled
        ]
        
        for policy in applicable_policies:
            metric_value = current_metrics.get(policy.metric_type, 0)
            
            # Check scale up
            if metric_value > policy.threshold_up:
                if service.instances < service.max_instances:
                    new_instances = min(
                        service.instances + policy.scale_up_by,
                        service.max_instances
                    )
                    return {
                        'action': 'scale_up',
                        'policy_id': policy.id,
                        'service_id': service_id,
                        'current_instances': service.instances,
                        'new_instances': new_instances,
                        'reason': f'{policy.metric_type} ({metric_value:.1f}) exceeded threshold ({policy.threshold_up})'
                    }
            
            # Check scale down
            elif metric_value < policy.threshold_down:
                if service.instances > service.min_instances:
                    new_instances = max(
                        service.instances - policy.scale_down_by,
                        service.min_instances
                    )
                    return {
                        'action': 'scale_down',
                        'policy_id': policy.id,
                        'service_id': service_id,
                        'current_instances': service.instances,
                        'new_instances': new_instances,
                        'reason': f'{policy.metric_type} ({metric_value:.1f}) below threshold ({policy.threshold_down})'
                    }
        
        return None
    
    def execute_scaling(
        self,
        service_id: str,
        new_instances: int,
        reason: str
    ) -> Dict[str, Any]:
        """Execute scaling action"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return {'error': 'Service not found'}
        
        old_instances = service.instances
        service.instances = new_instances
        
        # Record scaling event
        event = {
            'id': str(uuid.uuid4()),
            'service_id': service_id,
            'timestamp': datetime.utcnow().isoformat(),
            'old_instances': old_instances,
            'new_instances': new_instances,
            'reason': reason
        }
        
        self.scaling_history.append(event)
        
        return {
            'success': True,
            'event': event
        }


# ============================================
# Database Scaling Manager
# ============================================

class DatabaseScalingManager:
    """Manages database configurations and scaling"""
    
    def __init__(self):
        self.databases: Dict[str, DatabaseConfig] = {}
        self.sharding_configs: Dict[str, Dict] = {}
        self._initialize_default_databases()
    
    def _initialize_default_databases(self):
        """Initialize default database configurations"""
        
        # Primary PostgreSQL
        self.databases['primary-postgres'] = DatabaseConfig(
            id='primary-postgres',
            name='Primary PostgreSQL',
            db_type=DatabaseType.POSTGRESQL,
            host='postgres-primary.default.svc.cluster.local',
            port=5432,
            database='lean_construction',
            connection_pool_size=20,
            max_overflow=10,
            read_replicas=[
                'postgres-replica-1.default.svc.cluster.local',
                'postgres-replica-2.default.svc.cluster.local'
            ]
        )
        
        # MongoDB for documents
        self.databases['mongodb'] = DatabaseConfig(
            id='mongodb',
            name='MongoDB Document Store',
            db_type=DatabaseType.MONGODB,
            host='mongodb.default.svc.cluster.local',
            port=27017,
            database='lean_construction_docs',
            connection_pool_size=50,
            max_overflow=20,
            sharding_enabled=True,
            shard_key='project_id'
        )
        
        # Redis cache
        self.databases['redis-cache'] = DatabaseConfig(
            id='redis-cache',
            name='Redis Cache Cluster',
            db_type=DatabaseType.REDIS,
            host='redis-cluster.default.svc.cluster.local',
            port=6379,
            database='0',
            connection_pool_size=100,
            max_overflow=50
        )
        
        # TimescaleDB for time series
        self.databases['timescale'] = DatabaseConfig(
            id='timescale',
            name='TimescaleDB Time Series',
            db_type=DatabaseType.TIMESCALEDB,
            host='timescale.default.svc.cluster.local',
            port=5432,
            database='lean_construction_ts',
            connection_pool_size=30,
            max_overflow=15
        )
    
    def get_database(self, db_id: str) -> Optional[DatabaseConfig]:
        """Get database configuration"""
        return self.databases.get(db_id)
    
    def configure_sharding(
        self,
        db_id: str,
        shard_key: str,
        num_shards: int,
        shard_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Configure database sharding"""
        db = self.databases.get(db_id)
        if not db:
            return {'error': 'Database not found'}
        
        if db.db_type not in [DatabaseType.MONGODB, DatabaseType.POSTGRESQL]:
            return {'error': 'Sharding not supported for this database type'}
        
        db.sharding_enabled = True
        db.shard_key = shard_key
        
        self.sharding_configs[db_id] = {
            'shard_key': shard_key,
            'num_shards': num_shards,
            'shard_mapping': shard_mapping,
            'configured_at': datetime.utcnow().isoformat()
        }
        
        return {
            'success': True,
            'database_id': db_id,
            'sharding_config': self.sharding_configs[db_id]
        }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics for all databases"""
        stats = {}
        for db_id, db in self.databases.items():
            stats[db_id] = {
                'name': db.name,
                'type': db.db_type.value,
                'pool_size': db.connection_pool_size,
                'max_overflow': db.max_overflow,
                'read_replicas': len(db.read_replicas),
                'sharding_enabled': db.sharding_enabled
            }
        return stats


# ============================================
# Cache Manager
# ============================================

class CacheManager:
    """Manages caching layer configurations"""
    
    def __init__(self):
        self.caches: Dict[str, CacheConfig] = {}
        self.cache_stats: Dict[str, Dict] = {}
        self._initialize_default_caches()
    
    def _initialize_default_caches(self):
        """Initialize default cache configurations"""
        
        # API Response Cache
        self.caches['api-cache'] = CacheConfig(
            id='api-cache',
            name='API Response Cache',
            host='redis-api-cache.default.svc.cluster.local',
            port=6379,
            cluster_mode=True,
            nodes=[
                'redis-api-cache-0:6379',
                'redis-api-cache-1:6379',
                'redis-api-cache-2:6379'
            ],
            max_memory='2gb',
            eviction_policy='allkeys-lru',
            ttl_default=300
        )
        
        # Session Cache
        self.caches['session-cache'] = CacheConfig(
            id='session-cache',
            name='Session Cache',
            host='redis-session.default.svc.cluster.local',
            port=6379,
            cluster_mode=False,
            max_memory='1gb',
            eviction_policy='volatile-lru',
            ttl_default=3600
        )
        
        # ML Model Cache
        self.caches['ml-model-cache'] = CacheConfig(
            id='ml-model-cache',
            name='ML Model Cache',
            host='redis-ml-cache.default.svc.cluster.local',
            port=6379,
            cluster_mode=True,
            nodes=[
                'redis-ml-cache-0:6379',
                'redis-ml-cache-1:6379'
            ],
            max_memory='8gb',
            eviction_policy='allkeys-lfu',
            ttl_default=86400
        )
    
    def get_cache(self, cache_id: str) -> Optional[CacheConfig]:
        """Get cache configuration"""
        return self.caches.get(cache_id)
    
    def update_stats(self, cache_id: str, stats: Dict[str, Any]):
        """Update cache statistics"""
        self.cache_stats[cache_id] = {
            **stats,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def get_all_cache_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        result = {}
        for cache_id, config in self.caches.items():
            result[cache_id] = {
                'name': config.name,
                'cluster_mode': config.cluster_mode,
                'nodes': len(config.nodes) if config.nodes else 1,
                'max_memory': config.max_memory,
                'stats': self.cache_stats.get(cache_id, {})
            }
        return result


# ============================================
# Load Balancer Configuration
# ============================================

class LoadBalancerConfig:
    """Manages load balancer configurations"""
    
    def __init__(self):
        self.lb_configs: Dict[str, Dict] = {}
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default load balancer configurations"""
        
        # API Load Balancer
        self.lb_configs['api-lb'] = {
            'id': 'api-lb',
            'name': 'API Load Balancer',
            'type': 'application',
            'algorithm': 'round_robin',
            'health_check': {
                'path': '/health',
                'interval': 30,
                'timeout': 5,
                'healthy_threshold': 2,
                'unhealthy_threshold': 3
            },
            'ssl_termination': True,
            'sticky_sessions': False,
            'rate_limiting': {
                'enabled': True,
                'requests_per_second': 100,
                'burst': 200
            },
            'backends': [
                {'host': 'api-service-0', 'port': 8000, 'weight': 1},
                {'host': 'api-service-1', 'port': 8000, 'weight': 1},
                {'host': 'api-service-2', 'port': 8000, 'weight': 1}
            ]
        }
        
        # ML Inference Load Balancer
        self.lb_configs['ml-lb'] = {
            'id': 'ml-lb',
            'name': 'ML Inference Load Balancer',
            'type': 'network',
            'algorithm': 'least_connections',
            'health_check': {
                'path': '/health',
                'interval': 60,
                'timeout': 10,
                'healthy_threshold': 2,
                'unhealthy_threshold': 2
            },
            'ssl_termination': True,
            'sticky_sessions': True,  # For model consistency
            'rate_limiting': {
                'enabled': True,
                'requests_per_second': 50,
                'burst': 100
            },
            'backends': [
                {'host': 'ml-inference-0', 'port': 8001, 'weight': 1},
                {'host': 'ml-inference-1', 'port': 8001, 'weight': 1}
            ]
        }
    
    def get_config(self, lb_id: str) -> Optional[Dict]:
        """Get load balancer configuration"""
        return self.lb_configs.get(lb_id)
    
    def update_backends(
        self,
        lb_id: str,
        backends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update load balancer backends"""
        if lb_id not in self.lb_configs:
            return {'error': 'Load balancer not found'}
        
        self.lb_configs[lb_id]['backends'] = backends
        
        return {
            'success': True,
            'lb_id': lb_id,
            'backends': len(backends)
        }


# ============================================
# Kubernetes Configuration Generator
# ============================================

class KubernetesConfigGenerator:
    """Generates Kubernetes configurations"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
    
    def generate_deployment(self, service_id: str) -> Dict[str, Any]:
        """Generate Kubernetes Deployment manifest"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return {'error': 'Service not found'}
        
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': service.id,
                'labels': service.labels
            },
            'spec': {
                'replicas': service.instances,
                'selector': {
                    'matchLabels': {'app': service.labels.get('app', service.id)}
                },
                'template': {
                    'metadata': {
                        'labels': service.labels
                    },
                    'spec': {
                        'containers': [{
                            'name': service.id,
                            'image': f'lean-construction/{service.id}:latest',
                            'ports': [{'containerPort': 8000}],
                            'resources': {
                                'limits': {
                                    'cpu': service.cpu_limit,
                                    'memory': service.memory_limit
                                },
                                'requests': {
                                    'cpu': self._calculate_request(service.cpu_limit),
                                    'memory': self._calculate_request(service.memory_limit)
                                }
                            },
                            'env': [
                                {'name': k, 'value': v}
                                for k, v in service.env_vars.items()
                            ],
                            'livenessProbe': {
                                'httpGet': {
                                    'path': service.health_check_path,
                                    'port': 8000
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': service.health_check_path,
                                    'port': 8000
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
    
    def generate_hpa(self, service_id: str, policy: ScalingPolicy) -> Dict[str, Any]:
        """Generate Kubernetes HorizontalPodAutoscaler manifest"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return {'error': 'Service not found'}
        
        return {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f'{service_id}-hpa'
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': service_id
                },
                'minReplicas': service.min_instances,
                'maxReplicas': service.max_instances,
                'metrics': [{
                    'type': 'Resource',
                    'resource': {
                        'name': policy.metric_type,
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': int(policy.threshold_up)
                        }
                    }
                }],
                'behavior': {
                    'scaleDown': {
                        'stabilizationWindowSeconds': policy.cooldown_seconds,
                        'policies': [{
                            'type': 'Pods',
                            'value': policy.scale_down_by,
                            'periodSeconds': 60
                        }]
                    },
                    'scaleUp': {
                        'stabilizationWindowSeconds': 0,
                        'policies': [{
                            'type': 'Pods',
                            'value': policy.scale_up_by,
                            'periodSeconds': 60
                        }]
                    }
                }
            }
        }
    
    def generate_service(self, service_id: str) -> Dict[str, Any]:
        """Generate Kubernetes Service manifest"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return {'error': 'Service not found'}
        
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': service_id,
                'labels': service.labels
            },
            'spec': {
                'type': 'ClusterIP',
                'ports': [{
                    'port': 80,
                    'targetPort': 8000,
                    'protocol': 'TCP'
                }],
                'selector': {
                    'app': service.labels.get('app', service_id)
                }
            }
        }
    
    def _calculate_request(self, limit: str) -> str:
        """Calculate resource request from limit (typically 50-80% of limit)"""
        if limit.endswith('m'):
            value = int(limit[:-1]) * 0.5
            return f'{int(value)}m'
        elif limit.endswith('Gi'):
            value = float(limit[:-2]) * 0.5
            return f'{value:.1f}Gi'
        elif limit.endswith('Mi'):
            value = int(limit[:-2]) * 0.5
            return f'{int(value)}Mi'
        return limit


# ============================================
# Performance Monitoring
# ============================================

class PerformanceMonitor:
    """Monitors infrastructure performance"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[Dict]] = {}
        self.alerts: List[Dict] = []
        self.thresholds = {
            'cpu_critical': 90,
            'memory_critical': 85,
            'latency_warning': 500,
            'latency_critical': 1000,
            'error_rate_warning': 1,
            'error_rate_critical': 5
        }
    
    def record_metrics(
        self,
        service_id: str,
        metrics: Dict[str, float]
    ):
        """Record performance metrics"""
        if service_id not in self.metrics_history:
            self.metrics_history[service_id] = []
        
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            **metrics
        }
        
        self.metrics_history[service_id].append(record)
        
        # Keep last 1000 records
        if len(self.metrics_history[service_id]) > 1000:
            self.metrics_history[service_id] = self.metrics_history[service_id][-1000:]
        
        # Check thresholds
        self._check_thresholds(service_id, metrics)
    
    def _check_thresholds(self, service_id: str, metrics: Dict[str, float]):
        """Check if metrics exceed thresholds"""
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)
        latency = metrics.get('latency_ms', 0)
        error_rate = metrics.get('error_rate', 0)
        
        if cpu > self.thresholds['cpu_critical']:
            self._create_alert(service_id, 'critical', f'CPU usage critical: {cpu}%')
        
        if memory > self.thresholds['memory_critical']:
            self._create_alert(service_id, 'critical', f'Memory usage critical: {memory}%')
        
        if latency > self.thresholds['latency_critical']:
            self._create_alert(service_id, 'critical', f'Latency critical: {latency}ms')
        elif latency > self.thresholds['latency_warning']:
            self._create_alert(service_id, 'warning', f'Latency warning: {latency}ms')
        
        if error_rate > self.thresholds['error_rate_critical']:
            self._create_alert(service_id, 'critical', f'Error rate critical: {error_rate}%')
        elif error_rate > self.thresholds['error_rate_warning']:
            self._create_alert(service_id, 'warning', f'Error rate warning: {error_rate}%')
    
    def _create_alert(self, service_id: str, severity: str, message: str):
        """Create performance alert"""
        self.alerts.append({
            'id': str(uuid.uuid4()),
            'service_id': service_id,
            'severity': severity,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'acknowledged': False
        })
    
    def get_service_metrics(
        self,
        service_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get metrics for a service"""
        history = self.metrics_history.get(service_id, [])
        
        if not history:
            return {'error': 'No metrics available'}
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [
            h for h in history
            if datetime.fromisoformat(h['timestamp']) > cutoff
        ]
        
        if not recent:
            return {'error': 'No recent metrics'}
        
        # Calculate aggregates
        cpu_values = [h.get('cpu_percent', 0) for h in recent]
        memory_values = [h.get('memory_percent', 0) for h in recent]
        latency_values = [h.get('latency_ms', 0) for h in recent]
        
        import numpy as np
        
        return {
            'service_id': service_id,
            'period_hours': hours,
            'data_points': len(recent),
            'cpu': {
                'avg': float(np.mean(cpu_values)),
                'max': float(np.max(cpu_values)),
                'min': float(np.min(cpu_values))
            },
            'memory': {
                'avg': float(np.mean(memory_values)),
                'max': float(np.max(memory_values)),
                'min': float(np.min(memory_values))
            },
            'latency': {
                'avg': float(np.mean(latency_values)),
                'p95': float(np.percentile(latency_values, 95)),
                'p99': float(np.percentile(latency_values, 99))
            }
        }


# ============================================
# Infrastructure Manager
# ============================================

class InfrastructureManager:
    """Central manager for infrastructure"""
    
    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.auto_scaling = AutoScalingManager(self.service_registry)
        self.db_manager = DatabaseScalingManager()
        self.cache_manager = CacheManager()
        self.lb_config = LoadBalancerConfig()
        self.k8s_generator = KubernetesConfigGenerator(self.service_registry)
        self.perf_monitor = PerformanceMonitor()
    
    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get overall infrastructure status"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'services': self.service_registry.get_all_services(),
            'databases': self.db_manager.get_connection_stats(),
            'caches': self.cache_manager.get_all_cache_stats(),
            'scaling_policies': len(self.auto_scaling.policies),
            'recent_scaling_events': self.auto_scaling.scaling_history[-10:],
            'alerts': [a for a in self.perf_monitor.alerts if not a['acknowledged']][-10:]
        }
    
    def scale_service(
        self,
        service_id: str,
        instances: int
    ) -> Dict[str, Any]:
        """Manually scale a service"""
        service = self.service_registry.get_service(service_id)
        if not service:
            return {'error': 'Service not found'}
        
        if instances < service.min_instances:
            return {'error': f'Cannot scale below minimum ({service.min_instances})'}
        
        if instances > service.max_instances:
            return {'error': f'Cannot scale above maximum ({service.max_instances})'}
        
        return self.auto_scaling.execute_scaling(
            service_id,
            instances,
            'Manual scaling request'
        )
    
    def generate_all_k8s_configs(self) -> Dict[str, Any]:
        """Generate all Kubernetes configurations"""
        configs = {}
        
        for service_id in self.service_registry.services:
            configs[f'{service_id}-deployment'] = self.k8s_generator.generate_deployment(service_id)
            configs[f'{service_id}-service'] = self.k8s_generator.generate_service(service_id)
            
            # Add HPA if auto-scaling is enabled
            service = self.service_registry.get_service(service_id)
            if service and service.scaling_strategy == ScalingStrategy.AUTO:
                for policy in self.auto_scaling.policies.values():
                    if policy.service_id == service_id:
                        configs[f'{service_id}-hpa'] = self.k8s_generator.generate_hpa(
                            service_id, policy
                        )
                        break
        
        return configs
    
    def get_capacity_report(self) -> Dict[str, Any]:
        """Get capacity planning report"""
        services = self.service_registry.get_all_services()
        
        total_instances = sum(s['instances'] for s in services)
        
        # Calculate utilization
        utilization = {}
        for service in services:
            service_id = service['id']
            metrics = self.perf_monitor.get_service_metrics(service_id, hours=1)
            if 'error' not in metrics:
                utilization[service_id] = {
                    'cpu_avg': metrics['cpu']['avg'],
                    'memory_avg': metrics['memory']['avg']
                }
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_services': len(services),
            'total_instances': total_instances,
            'utilization': utilization,
            'recommendations': self._generate_capacity_recommendations(services, utilization)
        }
    
    def _generate_capacity_recommendations(
        self,
        services: List[Dict],
        utilization: Dict[str, Dict]
    ) -> List[str]:
        """Generate capacity recommendations"""
        recommendations = []
        
        for service in services:
            service_id = service['id']
            if service_id in utilization:
                cpu = utilization[service_id].get('cpu_avg', 0)
                memory = utilization[service_id].get('memory_avg', 0)
                
                if cpu > 70:
                    recommendations.append(
                        f"Consider scaling up {service_id} - CPU utilization at {cpu:.0f}%"
                    )
                elif cpu < 20 and service['instances'] > 1:
                    recommendations.append(
                        f"Consider scaling down {service_id} - CPU utilization only {cpu:.0f}%"
                    )
                
                if memory > 80:
                    recommendations.append(
                        f"Consider increasing memory for {service_id} - at {memory:.0f}%"
                    )
        
        return recommendations


# Create singleton instance
infrastructure_manager = InfrastructureManager()


# ============================================
# Convenience Functions
# ============================================

def get_infrastructure_status() -> Dict[str, Any]:
    """Get infrastructure status"""
    return infrastructure_manager.get_infrastructure_status()


def scale_service(service_id: str, instances: int) -> Dict[str, Any]:
    """Scale a service"""
    return infrastructure_manager.scale_service(service_id, instances)


def get_k8s_configs() -> Dict[str, Any]:
    """Get Kubernetes configurations"""
    return infrastructure_manager.generate_all_k8s_configs()