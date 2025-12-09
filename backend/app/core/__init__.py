"""
Core Infrastructure Module for Lean Construction AI

Provides enterprise-grade infrastructure components:
- Infrastructure scaling and management
- Commercial launch components (multi-tenancy, billing, licensing)
"""

from .infrastructure import (
    # Enums
    ScalingStrategy,
    DeploymentEnvironment,
    ServiceType,
    HealthStatus,
    DatabaseType,
    
    # Data classes
    ServiceConfig,
    ScalingPolicy,
    DatabaseConfig,
    CacheConfig,
    
    # Managers
    ServiceRegistry,
    AutoScalingManager,
    DatabaseScalingManager,
    CacheManager,
    LoadBalancerConfig,
    KubernetesConfigGenerator,
    PerformanceMonitor,
    InfrastructureManager,
    
    # Singleton and functions
    infrastructure_manager,
    get_infrastructure_status,
    scale_service,
    get_k8s_configs
)

from .commercial import (
    # Enums
    SubscriptionTier,
    BillingCycle,
    UsageMetricType,
    LicenseType,
    ComplianceCertification,
    OnboardingStatus,
    
    # Data classes
    Tenant,
    Subscription,
    UsageRecord,
    Quota,
    License,
    SLAMetric,
    
    # Configuration
    TierConfiguration,
    
    # Managers
    TenantManager,
    SubscriptionManager,
    UsageMeteringService,
    LicenseManager,
    SLAMonitor,
    OnboardingManager,
    WhiteLabelManager,
    CommercialLaunchSystem,
    
    # Singleton and functions
    commercial_system,
    provision_customer,
    get_pricing,
    validate_license
)

__all__ = [
    # Infrastructure
    'ScalingStrategy',
    'DeploymentEnvironment',
    'ServiceType',
    'HealthStatus',
    'DatabaseType',
    'ServiceConfig',
    'ScalingPolicy',
    'DatabaseConfig',
    'CacheConfig',
    'ServiceRegistry',
    'AutoScalingManager',
    'DatabaseScalingManager',
    'CacheManager',
    'LoadBalancerConfig',
    'KubernetesConfigGenerator',
    'PerformanceMonitor',
    'InfrastructureManager',
    'infrastructure_manager',
    'get_infrastructure_status',
    'scale_service',
    'get_k8s_configs',
    
    # Commercial
    'SubscriptionTier',
    'BillingCycle',
    'UsageMetricType',
    'LicenseType',
    'ComplianceCertification',
    'OnboardingStatus',
    'Tenant',
    'Subscription',
    'UsageRecord',
    'Quota',
    'License',
    'SLAMetric',
    'TierConfiguration',
    'TenantManager',
    'SubscriptionManager',
    'UsageMeteringService',
    'LicenseManager',
    'SLAMonitor',
    'OnboardingManager',
    'WhiteLabelManager',
    'CommercialLaunchSystem',
    'commercial_system',
    'provision_customer',
    'get_pricing',
    'validate_license'
]

__version__ = '4.0.0'