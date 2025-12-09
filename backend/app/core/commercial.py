"""
Commercial Launch Preparation Module for Lean Construction AI

This module provides components for commercial launch:
- Multi-tenancy support
- Subscription and billing management
- Usage metering and quotas
- License management
- SLA monitoring
- Customer onboarding
- White-label configurations
- Compliance certifications
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


# ============================================
# Enums and Data Classes
# ============================================

class SubscriptionTier(Enum):
    """Subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(Enum):
    """Billing cycles"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class UsageMetricType(Enum):
    """Types of usage metrics"""
    API_CALLS = "api_calls"
    STORAGE_GB = "storage_gb"
    USERS = "users"
    PROJECTS = "projects"
    ML_PREDICTIONS = "ml_predictions"
    REPORTS_GENERATED = "reports_generated"
    INTEGRATIONS = "integrations"
    DOCUMENTS_ANALYZED = "documents_analyzed"


class LicenseType(Enum):
    """License types"""
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    TRIAL = "trial"
    EVALUATION = "evaluation"


class ComplianceCertification(Enum):
    """Compliance certifications"""
    SOC2_TYPE1 = "soc2_type1"
    SOC2_TYPE2 = "soc2_type2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CCPA = "ccpa"


class OnboardingStatus(Enum):
    """Customer onboarding status"""
    INITIATED = "initiated"
    ACCOUNT_SETUP = "account_setup"
    DATA_MIGRATION = "data_migration"
    CONFIGURATION = "configuration"
    TRAINING = "training"
    GO_LIVE = "go_live"
    COMPLETED = "completed"


@dataclass
class Tenant:
    """Multi-tenant organization"""
    id: str
    name: str
    slug: str
    subscription_tier: SubscriptionTier
    created_at: datetime
    status: str  # active, suspended, cancelled
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Limits based on tier
    max_users: int = 5
    max_projects: int = 10
    max_storage_gb: int = 10
    api_rate_limit: int = 100  # per minute


@dataclass
class Subscription:
    """Subscription details"""
    id: str
    tenant_id: str
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    start_date: datetime
    end_date: Optional[datetime]
    auto_renew: bool
    price: float
    currency: str
    status: str  # active, past_due, cancelled, expired
    payment_method_id: Optional[str] = None
    trial_end: Optional[datetime] = None


@dataclass
class UsageRecord:
    """Usage tracking record"""
    id: str
    tenant_id: str
    metric_type: UsageMetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Quota:
    """Usage quota definition"""
    metric_type: UsageMetricType
    limit: float
    period: str  # daily, monthly, billing_cycle
    overage_allowed: bool = False
    overage_price: float = 0.0


@dataclass
class License:
    """Software license"""
    id: str
    tenant_id: str
    license_type: LicenseType
    license_key: str
    issued_at: datetime
    expires_at: Optional[datetime]
    features: List[str]
    restrictions: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class SLAMetric:
    """SLA metric tracking"""
    id: str
    tenant_id: str
    metric_name: str
    target_value: float
    actual_value: float
    period_start: datetime
    period_end: datetime
    met: bool


# ============================================
# Tier Configuration
# ============================================

class TierConfiguration:
    """Configuration for subscription tiers"""
    
    TIER_CONFIGS = {
        SubscriptionTier.FREE: {
            'price_monthly': 0,
            'price_annual': 0,
            'max_users': 2,
            'max_projects': 3,
            'max_storage_gb': 1,
            'api_rate_limit': 60,  # per minute
            'features': [
                'basic_dashboard',
                'waste_detection',
                'basic_reports'
            ],
            'support': 'community',
            'sla_uptime': 99.0
        },
        SubscriptionTier.STARTER: {
            'price_monthly': 99,
            'price_annual': 990,
            'max_users': 10,
            'max_projects': 25,
            'max_storage_gb': 25,
            'api_rate_limit': 300,
            'features': [
                'basic_dashboard',
                'waste_detection',
                'basic_reports',
                'predictive_analytics',
                'basic_integrations',
                'email_support'
            ],
            'support': 'email',
            'sla_uptime': 99.5
        },
        SubscriptionTier.PROFESSIONAL: {
            'price_monthly': 299,
            'price_annual': 2990,
            'max_users': 50,
            'max_projects': 100,
            'max_storage_gb': 100,
            'api_rate_limit': 1000,
            'features': [
                'advanced_dashboard',
                'waste_detection',
                'advanced_reports',
                'predictive_analytics',
                'ai_recommendations',
                'all_integrations',
                'custom_branding',
                'api_access',
                'priority_support'
            ],
            'support': 'priority',
            'sla_uptime': 99.9
        },
        SubscriptionTier.ENTERPRISE: {
            'price_monthly': 'custom',
            'price_annual': 'custom',
            'max_users': 'unlimited',
            'max_projects': 'unlimited',
            'max_storage_gb': 'unlimited',
            'api_rate_limit': 'unlimited',
            'features': [
                'all_features',
                'custom_ml_models',
                'dedicated_infrastructure',
                'sso_integration',
                'audit_logs',
                'custom_integrations',
                'white_label',
                'dedicated_support',
                'custom_sla'
            ],
            'support': 'dedicated',
            'sla_uptime': 99.99
        }
    }
    
    @classmethod
    def get_config(cls, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get configuration for a tier"""
        return cls.TIER_CONFIGS.get(tier, {})
    
    @classmethod
    def get_features(cls, tier: SubscriptionTier) -> List[str]:
        """Get features for a tier"""
        config = cls.get_config(tier)
        return config.get('features', [])
    
    @classmethod
    def get_limits(cls, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get limits for a tier"""
        config = cls.get_config(tier)
        return {
            'max_users': config.get('max_users'),
            'max_projects': config.get('max_projects'),
            'max_storage_gb': config.get('max_storage_gb'),
            'api_rate_limit': config.get('api_rate_limit')
        }


# ============================================
# Multi-Tenancy Manager
# ============================================

class TenantManager:
    """Manages multi-tenant organizations"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_by_slug: Dict[str, str] = {}  # slug -> tenant_id
    
    def create_tenant(
        self,
        name: str,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        settings: Optional[Dict[str, Any]] = None
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        slug = self._generate_slug(name)
        
        tier_config = TierConfiguration.get_config(tier)
        
        tenant = Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            subscription_tier=tier,
            created_at=datetime.utcnow(),
            status='active',
            settings=settings or {},
            max_users=tier_config.get('max_users', 5) if tier_config.get('max_users') != 'unlimited' else 10000,
            max_projects=tier_config.get('max_projects', 10) if tier_config.get('max_projects') != 'unlimited' else 10000,
            max_storage_gb=tier_config.get('max_storage_gb', 10) if tier_config.get('max_storage_gb') != 'unlimited' else 10000,
            api_rate_limit=tier_config.get('api_rate_limit', 100) if tier_config.get('api_rate_limit') != 'unlimited' else 100000
        )
        
        self.tenants[tenant_id] = tenant
        self.tenant_by_slug[slug] = tenant_id
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug"""
        tenant_id = self.tenant_by_slug.get(slug)
        return self.tenants.get(tenant_id) if tenant_id else None
    
    def update_tier(self, tenant_id: str, new_tier: SubscriptionTier) -> Dict[str, Any]:
        """Update tenant subscription tier"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found'}
        
        old_tier = tenant.subscription_tier
        tenant.subscription_tier = new_tier
        
        # Update limits
        tier_config = TierConfiguration.get_config(new_tier)
        tenant.max_users = tier_config.get('max_users', 5) if tier_config.get('max_users') != 'unlimited' else 10000
        tenant.max_projects = tier_config.get('max_projects', 10) if tier_config.get('max_projects') != 'unlimited' else 10000
        tenant.max_storage_gb = tier_config.get('max_storage_gb', 10) if tier_config.get('max_storage_gb') != 'unlimited' else 10000
        tenant.api_rate_limit = tier_config.get('api_rate_limit', 100) if tier_config.get('api_rate_limit') != 'unlimited' else 100000
        
        return {
            'success': True,
            'tenant_id': tenant_id,
            'old_tier': old_tier.value,
            'new_tier': new_tier.value
        }
    
    def suspend_tenant(self, tenant_id: str, reason: str) -> Dict[str, Any]:
        """Suspend a tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found'}
        
        tenant.status = 'suspended'
        tenant.metadata['suspension_reason'] = reason
        tenant.metadata['suspended_at'] = datetime.utcnow().isoformat()
        
        return {'success': True, 'tenant_id': tenant_id, 'status': 'suspended'}
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name"""
        slug = name.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while slug in self.tenant_by_slug:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug


# ============================================
# Subscription Manager
# ============================================

class SubscriptionManager:
    """Manages subscriptions and billing"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: List[Dict] = []
    
    def create_subscription(
        self,
        tenant_id: str,
        tier: SubscriptionTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        trial_days: int = 0
    ) -> Subscription:
        """Create a new subscription"""
        tier_config = TierConfiguration.get_config(tier)
        
        # Calculate price
        if billing_cycle == BillingCycle.MONTHLY:
            price = tier_config.get('price_monthly', 0)
        else:
            price = tier_config.get('price_annual', 0)
        
        if price == 'custom':
            price = 0  # Will be set manually for enterprise
        
        start_date = datetime.utcnow()
        trial_end = start_date + timedelta(days=trial_days) if trial_days > 0 else None
        
        subscription = Subscription(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            tier=tier,
            billing_cycle=billing_cycle,
            start_date=start_date,
            end_date=None,
            auto_renew=True,
            price=price,
            currency='USD',
            status='active' if trial_days == 0 else 'trialing',
            trial_end=trial_end
        )
        
        self.subscriptions[subscription.id] = subscription
        
        # Update tenant tier
        self.tenant_manager.update_tier(tenant_id, tier)
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    def get_tenant_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Get active subscription for a tenant"""
        for sub in self.subscriptions.values():
            if sub.tenant_id == tenant_id and sub.status in ['active', 'trialing']:
                return sub
        return None
    
    def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return {'error': 'Subscription not found'}
        
        if immediate:
            subscription.status = 'cancelled'
            subscription.end_date = datetime.utcnow()
            
            # Downgrade tenant to free
            self.tenant_manager.update_tier(
                subscription.tenant_id,
                SubscriptionTier.FREE
            )
        else:
            subscription.auto_renew = False
            # Will expire at end of billing period
        
        return {
            'success': True,
            'subscription_id': subscription_id,
            'status': subscription.status,
            'auto_renew': subscription.auto_renew
        }
    
    def upgrade_subscription(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """Upgrade a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return {'error': 'Subscription not found'}
        
        old_tier = subscription.tier
        subscription.tier = new_tier
        
        # Update price
        tier_config = TierConfiguration.get_config(new_tier)
        if subscription.billing_cycle == BillingCycle.MONTHLY:
            new_price = tier_config.get('price_monthly', 0)
        else:
            new_price = tier_config.get('price_annual', 0)
        
        if new_price != 'custom':
            subscription.price = new_price
        
        # Update tenant
        self.tenant_manager.update_tier(subscription.tenant_id, new_tier)
        
        return {
            'success': True,
            'subscription_id': subscription_id,
            'old_tier': old_tier.value,
            'new_tier': new_tier.value,
            'new_price': subscription.price
        }


# ============================================
# Usage Metering
# ============================================

class UsageMeteringService:
    """Tracks and meters usage"""
    
    def __init__(self):
        self.usage_records: List[UsageRecord] = []
        self.quotas: Dict[str, List[Quota]] = {}  # tenant_id -> quotas
        self.current_usage: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    def record_usage(
        self,
        tenant_id: str,
        metric_type: UsageMetricType,
        value: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """Record usage"""
        record = UsageRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.usage_records.append(record)
        self.current_usage[tenant_id][metric_type.value] += value
        
        return record
    
    def get_usage(
        self,
        tenant_id: str,
        metric_type: Optional[UsageMetricType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get usage for a tenant"""
        records = [r for r in self.usage_records if r.tenant_id == tenant_id]
        
        if metric_type:
            records = [r for r in records if r.metric_type == metric_type]
        
        if start_date:
            records = [r for r in records if r.timestamp >= start_date]
        
        if end_date:
            records = [r for r in records if r.timestamp <= end_date]
        
        # Aggregate by metric type
        usage_by_type = defaultdict(float)
        for record in records:
            usage_by_type[record.metric_type.value] += record.value
        
        return {
            'tenant_id': tenant_id,
            'period': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'usage': dict(usage_by_type),
            'record_count': len(records)
        }
    
    def check_quota(
        self,
        tenant_id: str,
        metric_type: UsageMetricType
    ) -> Dict[str, Any]:
        """Check if tenant is within quota"""
        quotas = self.quotas.get(tenant_id, [])
        relevant_quota = next(
            (q for q in quotas if q.metric_type == metric_type),
            None
        )
        
        if not relevant_quota:
            return {'within_quota': True, 'quota_defined': False}
        
        current = self.current_usage[tenant_id][metric_type.value]
        
        return {
            'within_quota': current < relevant_quota.limit,
            'quota_defined': True,
            'current_usage': current,
            'limit': relevant_quota.limit,
            'percentage_used': (current / relevant_quota.limit) * 100 if relevant_quota.limit > 0 else 0,
            'overage_allowed': relevant_quota.overage_allowed
        }
    
    def set_quota(
        self,
        tenant_id: str,
        metric_type: UsageMetricType,
        limit: float,
        period: str = 'monthly',
        overage_allowed: bool = False
    ):
        """Set a quota for a tenant"""
        if tenant_id not in self.quotas:
            self.quotas[tenant_id] = []
        
        # Remove existing quota for this metric
        self.quotas[tenant_id] = [
            q for q in self.quotas[tenant_id]
            if q.metric_type != metric_type
        ]
        
        quota = Quota(
            metric_type=metric_type,
            limit=limit,
            period=period,
            overage_allowed=overage_allowed
        )
        
        self.quotas[tenant_id].append(quota)


# ============================================
# License Management
# ============================================

class LicenseManager:
    """Manages software licenses"""
    
    def __init__(self):
        self.licenses: Dict[str, License] = {}
        self.license_by_key: Dict[str, str] = {}  # key -> license_id
    
    def generate_license(
        self,
        tenant_id: str,
        license_type: LicenseType,
        features: List[str],
        duration_days: Optional[int] = None,
        restrictions: Optional[Dict] = None
    ) -> License:
        """Generate a new license"""
        license_key = self._generate_license_key()
        
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(days=duration_days) if duration_days else None
        
        license = License(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            license_type=license_type,
            license_key=license_key,
            issued_at=issued_at,
            expires_at=expires_at,
            features=features,
            restrictions=restrictions or {}
        )
        
        self.licenses[license.id] = license
        self.license_by_key[license_key] = license.id
        
        return license
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key"""
        license_id = self.license_by_key.get(license_key)
        if not license_id:
            return {
                'valid': False,
                'reason': 'License key not found'
            }
        
        license = self.licenses.get(license_id)
        if not license:
            return {
                'valid': False,
                'reason': 'License not found'
            }
        
        if not license.is_active:
            return {
                'valid': False,
                'reason': 'License is deactivated'
            }
        
        if license.expires_at and datetime.utcnow() > license.expires_at:
            return {
                'valid': False,
                'reason': 'License has expired',
                'expired_at': license.expires_at.isoformat()
            }
        
        return {
            'valid': True,
            'tenant_id': license.tenant_id,
            'license_type': license.license_type.value,
            'features': license.features,
            'expires_at': license.expires_at.isoformat() if license.expires_at else None
        }
    
    def revoke_license(self, license_id: str, reason: str) -> Dict[str, Any]:
        """Revoke a license"""
        license = self.licenses.get(license_id)
        if not license:
            return {'error': 'License not found'}
        
        license.is_active = False
        license.restrictions['revoked'] = True
        license.restrictions['revocation_reason'] = reason
        license.restrictions['revoked_at'] = datetime.utcnow().isoformat()
        
        return {
            'success': True,
            'license_id': license_id,
            'status': 'revoked'
        }
    
    def _generate_license_key(self) -> str:
        """Generate a unique license key"""
        import secrets
        parts = [secrets.token_hex(4).upper() for _ in range(5)]
        return '-'.join(parts)


# ============================================
# SLA Monitoring
# ============================================

class SLAMonitor:
    """Monitors SLA compliance"""
    
    def __init__(self):
        self.sla_metrics: List[SLAMetric] = []
        self.sla_definitions: Dict[str, Dict] = {}
        self._initialize_default_slas()
    
    def _initialize_default_slas(self):
        """Initialize default SLA definitions"""
        self.sla_definitions = {
            'uptime': {
                'description': 'Service availability',
                'unit': 'percentage',
                'targets': {
                    SubscriptionTier.FREE.value: 99.0,
                    SubscriptionTier.STARTER.value: 99.5,
                    SubscriptionTier.PROFESSIONAL.value: 99.9,
                    SubscriptionTier.ENTERPRISE.value: 99.99
                }
            },
            'response_time': {
                'description': 'API response time',
                'unit': 'milliseconds',
                'targets': {
                    SubscriptionTier.FREE.value: 1000,
                    SubscriptionTier.STARTER.value: 500,
                    SubscriptionTier.PROFESSIONAL.value: 200,
                    SubscriptionTier.ENTERPRISE.value: 100
                }
            },
            'support_response': {
                'description': 'Support ticket response time',
                'unit': 'hours',
                'targets': {
                    SubscriptionTier.FREE.value: 72,
                    SubscriptionTier.STARTER.value: 24,
                    SubscriptionTier.PROFESSIONAL.value: 4,
                    SubscriptionTier.ENTERPRISE.value: 1
                }
            }
        }
    
    def record_sla_metric(
        self,
        tenant_id: str,
        metric_name: str,
        actual_value: float,
        tier: SubscriptionTier
    ) -> SLAMetric:
        """Record an SLA metric"""
        target = self.sla_definitions.get(metric_name, {}).get('targets', {}).get(tier.value, 0)
        
        # Determine if SLA is met (depends on metric type)
        if metric_name == 'uptime':
            met = actual_value >= target
        else:
            met = actual_value <= target
        
        metric = SLAMetric(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            metric_name=metric_name,
            target_value=target,
            actual_value=actual_value,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            met=met
        )
        
        self.sla_metrics.append(metric)
        return metric
    
    def get_sla_report(self, tenant_id: str) -> Dict[str, Any]:
        """Get SLA compliance report for a tenant"""
        tenant_metrics = [m for m in self.sla_metrics if m.tenant_id == tenant_id]
        
        if not tenant_metrics:
            return {'error': 'No SLA metrics found'}
        
        # Group by metric name
        by_metric = defaultdict(list)
        for m in tenant_metrics:
            by_metric[m.metric_name].append(m)
        
        report = {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'metrics': {}
        }
        
        for metric_name, metrics in by_metric.items():
            recent = max(metrics, key=lambda x: x.period_end)
            compliance_rate = sum(1 for m in metrics if m.met) / len(metrics) * 100
            
            report['metrics'][metric_name] = {
                'description': self.sla_definitions.get(metric_name, {}).get('description'),
                'target': recent.target_value,
                'current': recent.actual_value,
                'met': recent.met,
                'compliance_rate': compliance_rate
            }
        
        return report


# ============================================
# Customer Onboarding
# ============================================

class OnboardingManager:
    """Manages customer onboarding"""
    
    def __init__(self):
        self.onboarding_sessions: Dict[str, Dict] = {}
        self.onboarding_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize onboarding templates by tier"""
        return {
            SubscriptionTier.STARTER.value: {
                'steps': [
                    {'id': 'account_creation', 'name': 'Account Creation', 'duration_hours': 1},
                    {'id': 'basic_config', 'name': 'Basic Configuration', 'duration_hours': 2},
                    {'id': 'sample_project', 'name': 'Create Sample Project', 'duration_hours': 1},
                    {'id': 'quick_training', 'name': 'Quick Start Training', 'duration_hours': 2}
                ],
                'total_duration_hours': 6,
                'support_level': 'self-service'
            },
            SubscriptionTier.PROFESSIONAL.value: {
                'steps': [
                    {'id': 'kickoff_call', 'name': 'Kickoff Call', 'duration_hours': 1},
                    {'id': 'account_setup', 'name': 'Account Setup', 'duration_hours': 2},
                    {'id': 'integration_config', 'name': 'Integration Configuration', 'duration_hours': 4},
                    {'id': 'data_migration', 'name': 'Data Migration', 'duration_hours': 8},
                    {'id': 'user_training', 'name': 'User Training', 'duration_hours': 4},
                    {'id': 'admin_training', 'name': 'Admin Training', 'duration_hours': 2},
                    {'id': 'go_live', 'name': 'Go-Live Support', 'duration_hours': 4}
                ],
                'total_duration_hours': 25,
                'support_level': 'guided'
            },
            SubscriptionTier.ENTERPRISE.value: {
                'steps': [
                    {'id': 'kickoff_call', 'name': 'Executive Kickoff', 'duration_hours': 2},
                    {'id': 'requirements_analysis', 'name': 'Requirements Analysis', 'duration_hours': 8},
                    {'id': 'custom_config', 'name': 'Custom Configuration', 'duration_hours': 16},
                    {'id': 'integration_setup', 'name': 'Integration Setup', 'duration_hours': 24},
                    {'id': 'data_migration', 'name': 'Data Migration', 'duration_hours': 40},
                    {'id': 'testing', 'name': 'UAT Testing', 'duration_hours': 16},
                    {'id': 'pilot_rollout', 'name': 'Pilot Rollout', 'duration_hours': 40},
                    {'id': 'full_rollout', 'name': 'Full Rollout', 'duration_hours': 24},
                    {'id': 'training', 'name': 'Comprehensive Training', 'duration_hours': 16},
                    {'id': 'hypercare', 'name': 'Hypercare Support', 'duration_hours': 80}
                ],
                'total_duration_hours': 266,
                'support_level': 'dedicated'
            }
        }
    
    def start_onboarding(
        self,
        tenant_id: str,
        tier: SubscriptionTier,
        assigned_csm: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start onboarding for a tenant"""
        template = self.onboarding_templates.get(tier.value)
        if not template:
            template = self.onboarding_templates[SubscriptionTier.STARTER.value]
        
        session = {
            'id': str(uuid.uuid4()),
            'tenant_id': tenant_id,
            'tier': tier.value,
            'status': OnboardingStatus.INITIATED.value,
            'started_at': datetime.utcnow().isoformat(),
            'assigned_csm': assigned_csm,
            'steps': [
                {
                    **step,
                    'status': 'pending',
                    'started_at': None,
                    'completed_at': None
                }
                for step in template['steps']
            ],
            'total_duration_hours': template['total_duration_hours'],
            'support_level': template['support_level']
        }
        
        self.onboarding_sessions[session['id']] = session
        
        return session
    
    def update_step(
        self,
        session_id: str,
        step_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an onboarding step"""
        session = self.onboarding_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        for step in session['steps']:
            if step['id'] == step_id:
                step['status'] = status
                if status == 'in_progress' and not step['started_at']:
                    step['started_at'] = datetime.utcnow().isoformat()
                elif status == 'completed':
                    step['completed_at'] = datetime.utcnow().isoformat()
                if notes:
                    step['notes'] = notes
                break
        
        # Update session status
        self._update_session_status(session)
        
        return session
    
    def _update_session_status(self, session: Dict):
        """Update session status based on steps"""
        steps = session['steps']
        
        completed = all(s['status'] == 'completed' for s in steps)
        in_progress = any(s['status'] == 'in_progress' for s in steps)
        
        if completed:
            session['status'] = OnboardingStatus.COMPLETED.value
            session['completed_at'] = datetime.utcnow().isoformat()
        elif in_progress:
            # Find current phase
            for i, step in enumerate(steps):
                if step['status'] == 'in_progress':
                    session['current_step'] = step['id']
                    break
    
    def get_onboarding_status(self, session_id: str) -> Dict[str, Any]:
        """Get onboarding status"""
        session = self.onboarding_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        completed_steps = sum(1 for s in session['steps'] if s['status'] == 'completed')
        total_steps = len(session['steps'])
        
        return {
            'session_id': session_id,
            'tenant_id': session['tenant_id'],
            'status': session['status'],
            'progress': f"{completed_steps}/{total_steps}",
            'completion_percentage': (completed_steps / total_steps) * 100,
            'steps': session['steps'],
            'assigned_csm': session.get('assigned_csm')
        }


# ============================================
# White Label Configuration
# ============================================

class WhiteLabelManager:
    """Manages white-label configurations"""
    
    def __init__(self):
        self.configurations: Dict[str, Dict] = {}
    
    def create_configuration(
        self,
        tenant_id: str,
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create white-label configuration"""
        config = {
            'id': str(uuid.uuid4()),
            'tenant_id': tenant_id,
            'created_at': datetime.utcnow().isoformat(),
            'branding': {
                'company_name': branding.get('company_name', 'Lean Construction'),
                'logo_url': branding.get('logo_url'),
                'favicon_url': branding.get('favicon_url'),
                'primary_color': branding.get('primary_color', '#2196F3'),
                'secondary_color': branding.get('secondary_color', '#1976D2'),
                'accent_color': branding.get('accent_color', '#FF9800'),
                'custom_css': branding.get('custom_css'),
                'custom_domain': branding.get('custom_domain'),
                'email_from_name': branding.get('email_from_name'),
                'email_from_address': branding.get('email_from_address'),
                'support_email': branding.get('support_email'),
                'support_phone': branding.get('support_phone'),
                'footer_text': branding.get('footer_text'),
                'login_background_url': branding.get('login_background_url')
            },
            'features': {
                'hide_powered_by': branding.get('hide_powered_by', False),
                'custom_login_page': branding.get('custom_login_page', False),
                'custom_email_templates': branding.get('custom_email_templates', False)
            }
        }
        
        self.configurations[tenant_id] = config
        return config
    
    def get_configuration(self, tenant_id: str) -> Optional[Dict]:
        """Get white-label configuration"""
        return self.configurations.get(tenant_id)
    
    def update_branding(
        self,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update branding settings"""
        config = self.configurations.get(tenant_id)
        if not config:
            return {'error': 'Configuration not found'}
        
        config['branding'].update(updates)
        config['updated_at'] = datetime.utcnow().isoformat()
        
        return config


# ============================================
# Commercial Launch System
# ============================================

class CommercialLaunchSystem:
    """Integrated commercial launch management system"""
    
    def __init__(self):
        self.tenant_manager = TenantManager()
        self.subscription_manager = SubscriptionManager(self.tenant_manager)
        self.usage_metering = UsageMeteringService()
        self.license_manager = LicenseManager()
        self.sla_monitor = SLAMonitor()
        self.onboarding_manager = OnboardingManager()
        self.white_label_manager = WhiteLabelManager()
    
    def provision_new_customer(
        self,
        company_name: str,
        tier: SubscriptionTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        trial_days: int = 14
    ) -> Dict[str, Any]:
        """Provision a complete new customer"""
        # Create tenant
        tenant = self.tenant_manager.create_tenant(company_name, tier)
        
        # Create subscription
        subscription = self.subscription_manager.create_subscription(
            tenant.id, tier, billing_cycle, trial_days
        )
        
        # Generate license
        features = TierConfiguration.get_features(tier)
        license = self.license_manager.generate_license(
            tenant.id,
            LicenseType.TRIAL if trial_days > 0 else LicenseType.SUBSCRIPTION,
            features,
            duration_days=trial_days if trial_days > 0 else 365
        )
        
        # Set quotas
        limits = TierConfiguration.get_limits(tier)
        for metric_type in UsageMetricType:
            limit_key = f"max_{metric_type.value}"
            limit = limits.get(limit_key)
            if limit and limit != 'unlimited':
                self.usage_metering.set_quota(
                    tenant.id,
                    metric_type,
                    float(limit)
                )
        
        # Start onboarding
        onboarding = self.onboarding_manager.start_onboarding(tenant.id, tier)
        
        return {
            'success': True,
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'slug': tenant.slug
            },
            'subscription': {
                'id': subscription.id,
                'tier': subscription.tier.value,
                'status': subscription.status
            },
            'license': {
                'key': license.license_key,
                'expires_at': license.expires_at.isoformat() if license.expires_at else None
            },
            'onboarding': {
                'session_id': onboarding['id'],
                'status': onboarding['status']
            }
        }
    
    def get_customer_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get complete customer summary"""
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found'}
        
        subscription = self.subscription_manager.get_tenant_subscription(tenant_id)
        usage = self.usage_metering.get_usage(tenant_id)
        sla_report = self.sla_monitor.get_sla_report(tenant_id)
        
        return {
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'tier': tenant.subscription_tier.value,
                'status': tenant.status
            },
            'subscription': {
                'id': subscription.id if subscription else None,
                'status': subscription.status if subscription else None,
                'price': subscription.price if subscription else None
            },
            'usage': usage,
            'sla': sla_report if 'error' not in sla_report else None
        }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get pricing information"""
        pricing = {}
        
        for tier in SubscriptionTier:
            config = TierConfiguration.get_config(tier)
            pricing[tier.value] = {
                'monthly_price': config.get('price_monthly'),
                'annual_price': config.get('price_annual'),
                'features': config.get('features', []),
                'limits': {
                    'users': config.get('max_users'),
                    'projects': config.get('max_projects'),
                    'storage_gb': config.get('max_storage_gb')
                },
                'sla_uptime': config.get('sla_uptime'),
                'support': config.get('support')
            }
        
        return pricing


# Create singleton instance
commercial_system = CommercialLaunchSystem()


# ============================================
# Convenience Functions
# ============================================

def provision_customer(
    company_name: str,
    tier: str = 'starter',
    trial_days: int = 14
) -> Dict[str, Any]:
    """Provision a new customer"""
    return commercial_system.provision_new_customer(
        company_name,
        SubscriptionTier(tier),
        trial_days=trial_days
    )


def get_pricing() -> Dict[str, Any]:
    """Get pricing information"""
    return commercial_system.get_pricing_info()


def validate_license(license_key: str) -> Dict[str, Any]:
    """Validate a license key"""
    return commercial_system.license_manager.validate_license(license_key)