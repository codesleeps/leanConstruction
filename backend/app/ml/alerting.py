"""
Real-time Alerting and Notification System - Phase 3

Implements comprehensive alerting for construction projects:
- Multi-channel notifications (Email, SMS, Push, Webhook, Slack)
- Alert rules and conditions engine
- Severity-based escalation policies
- Alert aggregation and deduplication
- Acknowledgment and resolution tracking
- Integration with project metrics and thresholds
- Scheduled and event-driven alerts
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging
import json
import hashlib
import threading
from abc import ABC, abstractmethod
import asyncio
from queue import Queue, PriorityQueue
import re

logger = logging.getLogger(__name__)


# ============================================
# Enums and Data Classes
# ============================================

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"           # Urgent attention needed
    MEDIUM = "medium"       # Important but not urgent
    LOW = "low"             # Informational
    INFO = "info"           # FYI only


class AlertCategory(Enum):
    """Alert categories"""
    SAFETY = "safety"
    SCHEDULE = "schedule"
    COST = "cost"
    QUALITY = "quality"
    RESOURCE = "resource"
    EQUIPMENT = "equipment"
    WEATHER = "weather"
    COMPLIANCE = "compliance"
    COMMUNICATION = "communication"
    SYSTEM = "system"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    IN_APP = "in_app"


class ConditionOperator(Enum):
    """Operators for alert conditions"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN_RANGE = "in_range"
    OUT_OF_RANGE = "out_of_range"
    CHANGED = "changed"
    THRESHOLD_CROSSED = "threshold_crossed"


@dataclass
class AlertCondition:
    """Condition for triggering an alert"""
    metric: str
    operator: ConditionOperator
    threshold: Union[float, str, List]
    duration_minutes: int = 0  # How long condition must be true
    aggregation: str = "avg"  # avg, min, max, sum, count


@dataclass
class AlertRule:
    """Alert rule definition"""
    id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    conditions: List[AlertCondition]
    condition_logic: str = "AND"  # AND, OR
    enabled: bool = True
    cooldown_minutes: int = 15  # Minimum time between alerts
    auto_resolve: bool = True
    tags: List[str] = field(default_factory=list)
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    escalation_policy_id: Optional[str] = None


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    rule_name: str
    category: AlertCategory
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    source: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    notifications_sent: List[Dict] = field(default_factory=list)
    escalation_level: int = 0
    fingerprint: Optional[str] = None


@dataclass
class EscalationPolicy:
    """Escalation policy for unacknowledged alerts"""
    id: str
    name: str
    levels: List[Dict[str, Any]]  # List of escalation levels
    repeat_interval_minutes: int = 60
    max_escalations: int = 3


@dataclass
class NotificationTemplate:
    """Notification message template"""
    id: str
    name: str
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)


@dataclass 
class AlertSubscription:
    """User subscription to alerts"""
    user_id: str
    categories: List[AlertCategory]
    severities: List[AlertSeverity]
    channels: List[NotificationChannel]
    project_ids: List[str] = field(default_factory=list)
    quiet_hours: Optional[Dict[str, str]] = None  # start, end times


# ============================================
# Notification Providers
# ============================================

class NotificationProvider(ABC):
    """Base class for notification providers"""
    
    @abstractmethod
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send notification"""
        pass


class EmailProvider(NotificationProvider):
    """Email notification provider"""
    
    def __init__(self, smtp_config: Optional[Dict] = None):
        self.config = smtp_config or {}
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send email notification"""
        # In production, integrate with SMTP or email service
        logger.info(f"EMAIL to {recipient}: {subject}")
        
        return {
            'success': True,
            'channel': 'email',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': f"email-{alert.id}-{datetime.utcnow().timestamp()}"
        }


class SMSProvider(NotificationProvider):
    """SMS notification provider"""
    
    def __init__(self, api_config: Optional[Dict] = None):
        self.config = api_config or {}
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send SMS notification"""
        # In production, integrate with Twilio, AWS SNS, etc.
        message = f"{subject}: {body[:140]}"
        logger.info(f"SMS to {recipient}: {message}")
        
        return {
            'success': True,
            'channel': 'sms',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': f"sms-{alert.id}-{datetime.utcnow().timestamp()}"
        }


class PushProvider(NotificationProvider):
    """Push notification provider"""
    
    def __init__(self, api_config: Optional[Dict] = None):
        self.config = api_config or {}
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send push notification"""
        # In production, integrate with Firebase, OneSignal, etc.
        logger.info(f"PUSH to {recipient}: {subject}")
        
        return {
            'success': True,
            'channel': 'push',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': f"push-{alert.id}-{datetime.utcnow().timestamp()}"
        }


class WebhookProvider(NotificationProvider):
    """Webhook notification provider"""
    
    def __init__(self, default_url: Optional[str] = None):
        self.default_url = default_url
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send webhook notification"""
        webhook_url = kwargs.get('webhook_url', recipient)
        
        payload = {
            'alert_id': alert.id,
            'severity': alert.severity.value,
            'category': alert.category.value,
            'title': subject,
            'message': body,
            'triggered_at': alert.triggered_at.isoformat(),
            'context': alert.context
        }
        
        # In production, make HTTP POST request
        logger.info(f"WEBHOOK to {webhook_url}: {json.dumps(payload)}")
        
        return {
            'success': True,
            'channel': 'webhook',
            'recipient': webhook_url,
            'timestamp': datetime.utcnow().isoformat(),
            'payload': payload
        }


class SlackProvider(NotificationProvider):
    """Slack notification provider"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send Slack notification"""
        # Build Slack message with blocks
        severity_emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "📢",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📝"
        }
        
        emoji = severity_emoji.get(alert.severity, "📢")
        
        message = {
            'channel': recipient,
            'text': f"{emoji} {subject}",
            'blocks': [
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': f"{emoji} {subject}"}
                },
                {
                    'type': 'section',
                    'text': {'type': 'mrkdwn', 'text': body}
                },
                {
                    'type': 'context',
                    'elements': [
                        {'type': 'mrkdwn', 'text': f"*Severity:* {alert.severity.value}"},
                        {'type': 'mrkdwn', 'text': f"*Category:* {alert.category.value}"},
                        {'type': 'mrkdwn', 'text': f"*Time:* {alert.triggered_at.isoformat()}"}
                    ]
                }
            ]
        }
        
        # In production, post to Slack API
        logger.info(f"SLACK to {recipient}: {subject}")
        
        return {
            'success': True,
            'channel': 'slack',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat(),
            'message': message
        }


class TeamsProvider(NotificationProvider):
    """Microsoft Teams notification provider"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        alert: Alert,
        **kwargs
    ) -> Dict[str, Any]:
        """Send Teams notification"""
        # Build Teams adaptive card
        color_map = {
            AlertSeverity.CRITICAL: "FF0000",
            AlertSeverity.HIGH: "FFA500",
            AlertSeverity.MEDIUM: "FFFF00",
            AlertSeverity.LOW: "00FF00",
            AlertSeverity.INFO: "0000FF"
        }
        
        card = {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            'themeColor': color_map.get(alert.severity, "0000FF"),
            'summary': subject,
            'sections': [{
                'activityTitle': subject,
                'activitySubtitle': f"Severity: {alert.severity.value}",
                'text': body,
                'facts': [
                    {'name': 'Category', 'value': alert.category.value},
                    {'name': 'Source', 'value': alert.source},
                    {'name': 'Time', 'value': alert.triggered_at.isoformat()}
                ]
            }]
        }
        
        # In production, post to Teams webhook
        logger.info(f"TEAMS to {recipient}: {subject}")
        
        return {
            'success': True,
            'channel': 'teams',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat(),
            'card': card
        }


# ============================================
# Condition Evaluator
# ============================================

class ConditionEvaluator:
    """Evaluates alert conditions against metrics"""
    
    def __init__(self):
        self.metric_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self.max_history_size = 1000
        
    def record_metric(self, metric: str, value: float, timestamp: Optional[datetime] = None):
        """Record a metric value"""
        ts = timestamp or datetime.utcnow()
        self.metric_history[metric].append((ts, value))
        
        # Trim history
        if len(self.metric_history[metric]) > self.max_history_size:
            self.metric_history[metric] = self.metric_history[metric][-self.max_history_size:]
    
    def evaluate_condition(
        self,
        condition: AlertCondition,
        current_value: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate if a condition is met
        
        Returns:
            Tuple of (is_triggered, context)
        """
        # Get metric values for evaluation
        if current_value is not None:
            values = [current_value]
        else:
            # Get recent values based on duration
            cutoff = datetime.utcnow() - timedelta(minutes=max(1, condition.duration_minutes))
            values = [
                v for ts, v in self.metric_history.get(condition.metric, [])
                if ts >= cutoff
            ]
        
        if not values:
            return False, {'reason': 'No metric data available'}
        
        # Aggregate values
        if condition.aggregation == 'avg':
            agg_value = np.mean(values)
        elif condition.aggregation == 'min':
            agg_value = np.min(values)
        elif condition.aggregation == 'max':
            agg_value = np.max(values)
        elif condition.aggregation == 'sum':
            agg_value = np.sum(values)
        elif condition.aggregation == 'count':
            agg_value = len(values)
        else:
            agg_value = values[-1]  # Latest value
        
        # Evaluate condition
        triggered = False
        context = {
            'metric': condition.metric,
            'value': agg_value,
            'threshold': condition.threshold,
            'operator': condition.operator.value
        }
        
        threshold = condition.threshold
        
        if condition.operator == ConditionOperator.EQUALS:
            triggered = agg_value == threshold
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            triggered = agg_value != threshold
        elif condition.operator == ConditionOperator.GREATER_THAN:
            triggered = agg_value > threshold
        elif condition.operator == ConditionOperator.LESS_THAN:
            triggered = agg_value < threshold
        elif condition.operator == ConditionOperator.GREATER_EQUAL:
            triggered = agg_value >= threshold
        elif condition.operator == ConditionOperator.LESS_EQUAL:
            triggered = agg_value <= threshold
        elif condition.operator == ConditionOperator.IN_RANGE:
            if isinstance(threshold, list) and len(threshold) >= 2:
                triggered = threshold[0] <= agg_value <= threshold[1]
        elif condition.operator == ConditionOperator.OUT_OF_RANGE:
            if isinstance(threshold, list) and len(threshold) >= 2:
                triggered = agg_value < threshold[0] or agg_value > threshold[1]
        elif condition.operator == ConditionOperator.CONTAINS:
            triggered = str(threshold) in str(agg_value)
        elif condition.operator == ConditionOperator.THRESHOLD_CROSSED:
            # Check if value crossed threshold recently
            if len(values) >= 2:
                prev_below = values[-2] < threshold
                current_above = values[-1] >= threshold
                triggered = (prev_below and current_above) or (not prev_below and not current_above)
        
        context['triggered'] = triggered
        
        return triggered, context
    
    def evaluate_rule(
        self,
        rule: AlertRule,
        metric_values: Optional[Dict[str, float]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate all conditions for a rule
        
        Args:
            rule: Alert rule to evaluate
            metric_values: Current metric values (optional)
            
        Returns:
            Tuple of (is_triggered, context)
        """
        if not rule.enabled:
            return False, {'reason': 'Rule disabled'}
        
        results = []
        context = {'conditions': []}
        
        for condition in rule.conditions:
            current_value = None
            if metric_values and condition.metric in metric_values:
                current_value = metric_values[condition.metric]
            
            triggered, cond_context = self.evaluate_condition(condition, current_value)
            results.append(triggered)
            context['conditions'].append(cond_context)
        
        # Apply condition logic
        if rule.condition_logic == "AND":
            rule_triggered = all(results)
        else:  # OR
            rule_triggered = any(results)
        
        context['rule_triggered'] = rule_triggered
        context['logic'] = rule.condition_logic
        
        return rule_triggered, context


# ============================================
# Alert Manager
# ============================================

class AlertManager:
    """
    Central alert management system
    
    Handles alert lifecycle, deduplication, and routing
    """
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.subscriptions: Dict[str, AlertSubscription] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        
        self.condition_evaluator = ConditionEvaluator()
        
        # Notification providers
        self.providers: Dict[NotificationChannel, NotificationProvider] = {
            NotificationChannel.EMAIL: EmailProvider(),
            NotificationChannel.SMS: SMSProvider(),
            NotificationChannel.PUSH: PushProvider(),
            NotificationChannel.WEBHOOK: WebhookProvider(),
            NotificationChannel.SLACK: SlackProvider(),
            NotificationChannel.TEAMS: TeamsProvider()
        }
        
        # Alert state tracking
        self.last_alert_time: Dict[str, datetime] = {}  # rule_id -> last alert time
        self.alert_counts: Dict[str, int] = defaultdict(int)  # rule_id -> count
        
        # Initialize default rules
        self._initialize_default_rules()
        self._initialize_default_templates()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules for construction"""
        default_rules = [
            AlertRule(
                id="safety_incident",
                name="Safety Incident Detected",
                description="Alert when safety incident is reported",
                category=AlertCategory.SAFETY,
                severity=AlertSeverity.CRITICAL,
                conditions=[
                    AlertCondition(
                        metric="safety.incidents",
                        operator=ConditionOperator.GREATER_THAN,
                        threshold=0
                    )
                ],
                cooldown_minutes=5,
                notification_channels=[
                    NotificationChannel.SMS,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH
                ]
            ),
            AlertRule(
                id="schedule_delay",
                name="Schedule Delay Warning",
                description="Alert when critical path is delayed",
                category=AlertCategory.SCHEDULE,
                severity=AlertSeverity.HIGH,
                conditions=[
                    AlertCondition(
                        metric="schedule.variance_days",
                        operator=ConditionOperator.GREATER_THAN,
                        threshold=3,
                        duration_minutes=60
                    )
                ],
                cooldown_minutes=240,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                id="cost_overrun",
                name="Cost Overrun Alert",
                description="Alert when cost exceeds budget threshold",
                category=AlertCategory.COST,
                severity=AlertSeverity.HIGH,
                conditions=[
                    AlertCondition(
                        metric="cost.variance_percent",
                        operator=ConditionOperator.GREATER_THAN,
                        threshold=10
                    )
                ],
                cooldown_minutes=1440,  # Once per day
                notification_channels=[NotificationChannel.EMAIL]
            ),
            AlertRule(
                id="quality_defects",
                name="Quality Defects Threshold",
                description="Alert when defect rate exceeds acceptable level",
                category=AlertCategory.QUALITY,
                severity=AlertSeverity.MEDIUM,
                conditions=[
                    AlertCondition(
                        metric="quality.defect_rate",
                        operator=ConditionOperator.GREATER_THAN,
                        threshold=5
                    )
                ],
                cooldown_minutes=120,
                notification_channels=[NotificationChannel.EMAIL]
            ),
            AlertRule(
                id="resource_shortage",
                name="Resource Shortage Warning",
                description="Alert when critical resources are low",
                category=AlertCategory.RESOURCE,
                severity=AlertSeverity.HIGH,
                conditions=[
                    AlertCondition(
                        metric="resource.availability_percent",
                        operator=ConditionOperator.LESS_THAN,
                        threshold=20
                    )
                ],
                cooldown_minutes=60,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH]
            ),
            AlertRule(
                id="equipment_maintenance",
                name="Equipment Maintenance Due",
                description="Alert when equipment maintenance is overdue",
                category=AlertCategory.EQUIPMENT,
                severity=AlertSeverity.MEDIUM,
                conditions=[
                    AlertCondition(
                        metric="equipment.days_since_maintenance",
                        operator=ConditionOperator.GREATER_THAN,
                        threshold=30
                    )
                ],
                cooldown_minutes=1440,
                notification_channels=[NotificationChannel.EMAIL]
            ),
            AlertRule(
                id="weather_alert",
                name="Severe Weather Alert",
                description="Alert for severe weather conditions",
                category=AlertCategory.WEATHER,
                severity=AlertSeverity.HIGH,
                conditions=[
                    AlertCondition(
                        metric="weather.severity",
                        operator=ConditionOperator.GREATER_EQUAL,
                        threshold=3
                    )
                ],
                cooldown_minutes=30,
                notification_channels=[
                    NotificationChannel.SMS,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL
                ]
            ),
            AlertRule(
                id="compliance_deadline",
                name="Compliance Deadline Approaching",
                description="Alert when compliance deadline is near",
                category=AlertCategory.COMPLIANCE,
                severity=AlertSeverity.HIGH,
                conditions=[
                    AlertCondition(
                        metric="compliance.days_until_deadline",
                        operator=ConditionOperator.LESS_EQUAL,
                        threshold=7
                    )
                ],
                cooldown_minutes=1440,
                notification_channels=[NotificationChannel.EMAIL]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def _initialize_default_templates(self):
        """Initialize default notification templates"""
        templates = [
            NotificationTemplate(
                id="alert_email",
                name="Standard Alert Email",
                channel=NotificationChannel.EMAIL,
                subject_template="[{severity}] {title}",
                body_template="""
Alert Details:
--------------
Category: {category}
Severity: {severity}
Source: {source}
Time: {triggered_at}

{message}

Context:
{context}

---
This is an automated alert from the Construction Management System.
                """,
                variables=['severity', 'title', 'category', 'source', 'triggered_at', 'message', 'context']
            ),
            NotificationTemplate(
                id="alert_sms",
                name="Standard Alert SMS",
                channel=NotificationChannel.SMS,
                subject_template="{severity}: {title}",
                body_template="{message}",
                variables=['severity', 'title', 'message']
            ),
            NotificationTemplate(
                id="alert_push",
                name="Standard Alert Push",
                channel=NotificationChannel.PUSH,
                subject_template="{severity}: {title}",
                body_template="{message}",
                variables=['severity', 'title', 'message']
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
    
    def add_rule(self, rule: AlertRule):
        """Add or update an alert rule"""
        self.rules[rule.id] = rule
        logger.info(f"Alert rule added/updated: {rule.id}")
    
    def remove_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Alert rule removed: {rule_id}")
    
    def add_escalation_policy(self, policy: EscalationPolicy):
        """Add escalation policy"""
        self.escalation_policies[policy.id] = policy
    
    def add_subscription(self, subscription: AlertSubscription):
        """Add user subscription"""
        self.subscriptions[subscription.user_id] = subscription
    
    def _generate_fingerprint(self, rule: AlertRule, context: Dict) -> str:
        """Generate unique fingerprint for alert deduplication"""
        fingerprint_data = {
            'rule_id': rule.id,
            'category': rule.category.value,
            'severity': rule.severity.value
        }
        
        # Include key context values
        for key in ['metric', 'source', 'project_id']:
            if key in context:
                fingerprint_data[key] = context[key]
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def _check_cooldown(self, rule_id: str, cooldown_minutes: int) -> bool:
        """Check if rule is in cooldown period"""
        if rule_id not in self.last_alert_time:
            return False
        
        elapsed = datetime.utcnow() - self.last_alert_time[rule_id]
        return elapsed.total_seconds() < cooldown_minutes * 60
    
    def _find_existing_alert(self, fingerprint: str) -> Optional[Alert]:
        """Find existing active alert with same fingerprint"""
        for alert in self.alerts.values():
            if (alert.fingerprint == fingerprint and 
                alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]):
                return alert
        return None
    
    def create_alert(
        self,
        rule_id: str,
        title: str,
        message: str,
        source: str,
        context: Optional[Dict] = None
    ) -> Optional[Alert]:
        """
        Create a new alert
        
        Args:
            rule_id: ID of the triggering rule
            title: Alert title
            message: Alert message
            source: Source of the alert
            context: Additional context data
            
        Returns:
            Created Alert or None if deduplicated
        """
        if rule_id not in self.rules:
            logger.warning(f"Unknown rule: {rule_id}")
            return None
        
        rule = self.rules[rule_id]
        context = context or {}
        
        # Check cooldown
        if self._check_cooldown(rule_id, rule.cooldown_minutes):
            logger.debug(f"Rule {rule_id} in cooldown")
            return None
        
        # Generate fingerprint for deduplication
        fingerprint = self._generate_fingerprint(rule, context)
        
        # Check for existing alert
        existing = self._find_existing_alert(fingerprint)
        if existing:
            logger.debug(f"Alert deduplicated: {fingerprint}")
            return existing
        
        # Create new alert
        alert_id = f"ALT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(self.alerts):04d}"
        
        alert = Alert(
            id=alert_id,
            rule_id=rule_id,
            rule_name=rule.name,
            category=rule.category,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=title,
            message=message,
            source=source,
            triggered_at=datetime.utcnow(),
            context=context,
            fingerprint=fingerprint
        )
        
        self.alerts[alert_id] = alert
        self.last_alert_time[rule_id] = datetime.utcnow()
        self.alert_counts[rule_id] += 1
        
        # Send notifications
        self._send_notifications(alert, rule)
        
        logger.info(f"Alert created: {alert_id} - {title}")
        
        return alert
    
    def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications for an alert"""
        # Get recipients from rule and subscriptions
        recipients = set(rule.recipients)
        
        # Add subscribers
        for user_id, sub in self.subscriptions.items():
            if (alert.category in sub.categories and 
                alert.severity in sub.severities):
                recipients.add(user_id)
        
        # Send via each configured channel
        for channel in rule.notification_channels:
            provider = self.providers.get(channel)
            if not provider:
                continue
            
            # Get template
            template = self._get_template(channel)
            subject = self._render_template(template.subject_template, alert)
            body = self._render_template(template.body_template, alert)
            
            for recipient in recipients:
                try:
                    result = provider.send(recipient, subject, body, alert)
                    alert.notifications_sent.append(result)
                except Exception as e:
                    logger.error(f"Notification failed: {channel.value} to {recipient}: {e}")
    
    def _get_template(self, channel: NotificationChannel) -> NotificationTemplate:
        """Get notification template for channel"""
        for template in self.templates.values():
            if template.channel == channel:
                return template
        
        # Return default
        return NotificationTemplate(
            id='default',
            name='Default',
            channel=channel,
            subject_template='{title}',
            body_template='{message}'
        )
    
    def _render_template(self, template: str, alert: Alert) -> str:
        """Render template with alert data"""
        context = {
            'title': alert.title,
            'message': alert.message,
            'severity': alert.severity.value.upper(),
            'category': alert.category.value,
            'source': alert.source,
            'triggered_at': alert.triggered_at.isoformat(),
            'context': json.dumps(alert.context, indent=2)
        }
        
        result = template
        for key, value in context.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result
    
    def acknowledge_alert(self, alert_id: str, user_id: str, note: Optional[str] = None) -> Optional[Alert]:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        
        if note:
            alert.context['acknowledgment_note'] = note
        
        logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
        
        return alert
    
    def resolve_alert(self, alert_id: str, user_id: str, resolution: Optional[str] = None) -> Optional[Alert]:
        """Resolve an alert"""
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user_id
        
        if resolution:
            alert.context['resolution'] = resolution
        
        logger.info(f"Alert resolved: {alert_id} by {user_id}")
        
        return alert
    
    def suppress_alert(self, alert_id: str, duration_minutes: int = 60) -> Optional[Alert]:
        """Suppress an alert temporarily"""
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.context['suppressed_until'] = (
            datetime.utcnow() + timedelta(minutes=duration_minutes)
        ).isoformat()
        
        logger.info(f"Alert suppressed: {alert_id} for {duration_minutes} minutes")
        
        return alert
    
    def evaluate_metrics(self, metrics: Dict[str, float], source: str = "system"):
        """
        Evaluate metrics against all rules
        
        Args:
            metrics: Dictionary of metric_name -> value
            source: Source of the metrics
        """
        # Record metrics
        for metric, value in metrics.items():
            self.condition_evaluator.record_metric(metric, value)
        
        # Evaluate each rule
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            triggered, context = self.condition_evaluator.evaluate_rule(rule, metrics)
            
            if triggered:
                # Auto-generate alert
                title = rule.name
                message = f"{rule.description}\n\nCondition details:\n"
                
                for cond in context.get('conditions', []):
                    message += f"  - {cond['metric']}: {cond['value']:.2f} "
                    message += f"({cond['operator']} {cond['threshold']})\n"
                
                context['source'] = source
                
                self.create_alert(
                    rule_id=rule_id,
                    title=title,
                    message=message,
                    source=source,
                    context=context
                )
    
    def get_active_alerts(
        self,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get active alerts with optional filtering"""
        alerts = [
            a for a in self.alerts.values()
            if a.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]
        ]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by severity and time
        severity_order = [AlertSeverity.CRITICAL, AlertSeverity.HIGH, 
                        AlertSeverity.MEDIUM, AlertSeverity.LOW, AlertSeverity.INFO]
        alerts.sort(key=lambda a: (severity_order.index(a.severity), a.triggered_at))
        
        return alerts[:limit]
    
    def get_alert_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Alert]:
        """Get alert history"""
        alerts = list(self.alerts.values())
        
        if start_date:
            alerts = [a for a in alerts if a.triggered_at >= start_date]
        
        if end_date:
            alerts = [a for a in alerts if a.triggered_at <= end_date]
        
        alerts.sort(key=lambda a: a.triggered_at, reverse=True)
        
        return alerts[:limit]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        all_alerts = list(self.alerts.values())
        alerts_24h = [a for a in all_alerts if a.triggered_at >= last_24h]
        alerts_7d = [a for a in all_alerts if a.triggered_at >= last_7d]
        
        # Count by category
        by_category = defaultdict(int)
        for alert in alerts_24h:
            by_category[alert.category.value] += 1
        
        # Count by severity
        by_severity = defaultdict(int)
        for alert in alerts_24h:
            by_severity[alert.severity.value] += 1
        
        # Count by status
        by_status = defaultdict(int)
        for alert in all_alerts:
            by_status[alert.status.value] += 1
        
        # Average resolution time
        resolved_alerts = [
            a for a in all_alerts
            if a.status == AlertStatus.RESOLVED and a.resolved_at
        ]
        
        avg_resolution_time = 0
        if resolved_alerts:
            resolution_times = [
                (a.resolved_at - a.triggered_at).total_seconds() / 3600
                for a in resolved_alerts
            ]
            avg_resolution_time = np.mean(resolution_times)
        
        return {
            'total_alerts': len(all_alerts),
            'alerts_24h': len(alerts_24h),
            'alerts_7d': len(alerts_7d),
            'active_alerts': by_status.get('active', 0),
            'acknowledged_alerts': by_status.get('acknowledged', 0),
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'by_status': dict(by_status),
            'avg_resolution_time_hours': avg_resolution_time,
            'rules_count': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled])
        }
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get alert dashboard data"""
        active_alerts = self.get_active_alerts(limit=50)
        stats = self.get_alert_statistics()
        
        # Recent activity
        recent_alerts = sorted(
            self.alerts.values(),
            key=lambda a: a.triggered_at,
            reverse=True
        )[:10]
        
        return {
            'statistics': stats,
            'active_alerts': [asdict(a) for a in active_alerts],
            'recent_activity': [
                {
                    'alert_id': a.id,
                    'title': a.title,
                    'severity': a.severity.value,
                    'category': a.category.value,
                    'status': a.status.value,
                    'triggered_at': a.triggered_at.isoformat()
                }
                for a in recent_alerts
            ],
            'critical_count': len([
                a for a in active_alerts 
                if a.severity == AlertSeverity.CRITICAL
            ]),
            'requires_attention': len([
                a for a in active_alerts 
                if a.status == AlertStatus.ACTIVE
            ])
        }


# ============================================
# Alert Rule Builder
# ============================================

class AlertRuleBuilder:
    """Fluent builder for creating alert rules"""
    
    def __init__(self):
        self._id: Optional[str] = None
        self._name: str = ""
        self._description: str = ""
        self._category: AlertCategory = AlertCategory.SYSTEM
        self._severity: AlertSeverity = AlertSeverity.MEDIUM
        self._conditions: List[AlertCondition] = []
        self._condition_logic: str = "AND"
        self._enabled: bool = True
        self._cooldown: int = 15
        self._channels: List[NotificationChannel] = []
        self._recipients: List[str] = []
        self._tags: List[str] = []
    
    def with_id(self, rule_id: str) -> 'AlertRuleBuilder':
        self._id = rule_id
        return self
    
    def with_name(self, name: str) -> 'AlertRuleBuilder':
        self._name = name
        return self
    
    def with_description(self, description: str) -> 'AlertRuleBuilder':
        self._description = description
        return self
    
    def with_category(self, category: AlertCategory) -> 'AlertRuleBuilder':
        self._category = category
        return self
    
    def with_severity(self, severity: AlertSeverity) -> 'AlertRuleBuilder':
        self._severity = severity
        return self
    
    def add_condition(
        self,
        metric: str,
        operator: ConditionOperator,
        threshold: Union[float, str, List],
        duration_minutes: int = 0,
        aggregation: str = "avg"
    ) -> 'AlertRuleBuilder':
        self._conditions.append(AlertCondition(
            metric=metric,
            operator=operator,
            threshold=threshold,
            duration_minutes=duration_minutes,
            aggregation=aggregation
        ))
        return self
    
    def with_logic(self, logic: str) -> 'AlertRuleBuilder':
        self._condition_logic = logic
        return self
    
    def with_cooldown(self, minutes: int) -> 'AlertRuleBuilder':
        self._cooldown = minutes
        return self
    
    def notify_via(self, *channels: NotificationChannel) -> 'AlertRuleBuilder':
        self._channels.extend(channels)
        return self
    
    def notify_recipients(self, *recipients: str) -> 'AlertRuleBuilder':
        self._recipients.extend(recipients)
        return self
    
    def with_tags(self, *tags: str) -> 'AlertRuleBuilder':
        self._tags.extend(tags)
        return self
    
    def enabled(self, is_enabled: bool = True) -> 'AlertRuleBuilder':
        self._enabled = is_enabled
        return self
    
    def build(self) -> AlertRule:
        """Build the alert rule"""
        if not self._id:
            self._id = f"rule_{datetime.utcnow().timestamp()}"
        
        return AlertRule(
            id=self._id,
            name=self._name,
            description=self._description,
            category=self._category,
            severity=self._severity,
            conditions=self._conditions,
            condition_logic=self._condition_logic,
            enabled=self._enabled,
            cooldown_minutes=self._cooldown,
            notification_channels=self._channels,
            recipients=self._recipients,
            tags=self._tags
        )


# ============================================
# Construction-Specific Alert Rules
# ============================================

class ConstructionAlertRules:
    """Pre-built alert rules for construction projects"""
    
    @staticmethod
    def create_safety_rules() -> List[AlertRule]:
        """Create safety-related alert rules"""
        return [
            AlertRuleBuilder()
            .with_id("safety_ppe_violation")
            .with_name("PPE Violation Detected")
            .with_description("Personal protective equipment violation detected on site")
            .with_category(AlertCategory.SAFETY)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("safety.ppe_violations", ConditionOperator.GREATER_THAN, 0)
            .with_cooldown(15)
            .notify_via(NotificationChannel.SMS, NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("safety_near_miss")
            .with_name("Near Miss Reported")
            .with_description("Near miss incident reported on site")
            .with_category(AlertCategory.SAFETY)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("safety.near_misses", ConditionOperator.GREATER_THAN, 0)
            .with_cooldown(5)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.PUSH)
            .build(),
            
            AlertRuleBuilder()
            .with_id("safety_inspection_failed")
            .with_name("Safety Inspection Failed")
            .with_description("Site failed safety inspection")
            .with_category(AlertCategory.SAFETY)
            .with_severity(AlertSeverity.CRITICAL)
            .add_condition("safety.inspection_score", ConditionOperator.LESS_THAN, 70)
            .with_cooldown(1440)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK)
            .build()
        ]
    
    @staticmethod
    def create_schedule_rules() -> List[AlertRule]:
        """Create schedule-related alert rules"""
        return [
            AlertRuleBuilder()
            .with_id("schedule_critical_delay")
            .with_name("Critical Path Delay")
            .with_description("Critical path activity is delayed")
            .with_category(AlertCategory.SCHEDULE)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("schedule.critical_path_delay_days", ConditionOperator.GREATER_THAN, 1)
            .with_cooldown(240)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.SLACK)
            .build(),
            
            AlertRuleBuilder()
            .with_id("schedule_milestone_at_risk")
            .with_name("Milestone At Risk")
            .with_description("Upcoming milestone is at risk of being missed")
            .with_category(AlertCategory.SCHEDULE)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("schedule.milestone_risk_score", ConditionOperator.GREATER_THAN, 0.7)
            .with_cooldown(720)
            .notify_via(NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("schedule_spi_low")
            .with_name("Schedule Performance Index Low")
            .with_description("SPI has dropped below acceptable threshold")
            .with_category(AlertCategory.SCHEDULE)
            .with_severity(AlertSeverity.MEDIUM)
            .add_condition("schedule.spi", ConditionOperator.LESS_THAN, 0.9, duration_minutes=1440)
            .with_cooldown(1440)
            .notify_via(NotificationChannel.EMAIL)
            .build()
        ]
    
    @staticmethod
    def create_cost_rules() -> List[AlertRule]:
        """Create cost-related alert rules"""
        return [
            AlertRuleBuilder()
            .with_id("cost_budget_exceeded")
            .with_name("Budget Exceeded")
            .with_description("Project cost has exceeded budget")
            .with_category(AlertCategory.COST)
            .with_severity(AlertSeverity.CRITICAL)
            .add_condition("cost.variance_percent", ConditionOperator.GREATER_THAN, 15)
            .with_cooldown(2880)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.SLACK)
            .build(),
            
            AlertRuleBuilder()
            .with_id("cost_cpi_low")
            .with_name("Cost Performance Index Low")
            .with_description("CPI has dropped below acceptable threshold")
            .with_category(AlertCategory.COST)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("cost.cpi", ConditionOperator.LESS_THAN, 0.85)
            .with_cooldown(1440)
            .notify_via(NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("cost_change_order_high")
            .with_name("High Value Change Order")
            .with_description("Change order exceeds threshold value")
            .with_category(AlertCategory.COST)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("cost.change_order_value", ConditionOperator.GREATER_THAN, 50000)
            .with_cooldown(60)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.PUSH)
            .build()
        ]
    
    @staticmethod
    def create_quality_rules() -> List[AlertRule]:
        """Create quality-related alert rules"""
        return [
            AlertRuleBuilder()
            .with_id("quality_inspection_failed")
            .with_name("Quality Inspection Failed")
            .with_description("Quality inspection failed or below threshold")
            .with_category(AlertCategory.QUALITY)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("quality.inspection_pass_rate", ConditionOperator.LESS_THAN, 80)
            .with_cooldown(240)
            .notify_via(NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("quality_defect_rate_high")
            .with_name("High Defect Rate")
            .with_description("Defect rate exceeds acceptable threshold")
            .with_category(AlertCategory.QUALITY)
            .with_severity(AlertSeverity.MEDIUM)
            .add_condition("quality.defect_rate", ConditionOperator.GREATER_THAN, 5)
            .with_cooldown(720)
            .notify_via(NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("quality_rework_required")
            .with_name("Rework Required")
            .with_description("Significant rework identified")
            .with_category(AlertCategory.QUALITY)
            .with_severity(AlertSeverity.MEDIUM)
            .add_condition("quality.rework_items", ConditionOperator.GREATER_THAN, 5)
            .with_cooldown(480)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.PUSH)
            .build()
        ]
    
    @staticmethod
    def create_resource_rules() -> List[AlertRule]:
        """Create resource-related alert rules"""
        return [
            AlertRuleBuilder()
            .with_id("resource_labor_shortage")
            .with_name("Labor Shortage")
            .with_description("Insufficient labor resources available")
            .with_category(AlertCategory.RESOURCE)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("resource.labor_availability", ConditionOperator.LESS_THAN, 80)
            .with_cooldown(240)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.PUSH)
            .build(),
            
            AlertRuleBuilder()
            .with_id("resource_material_low")
            .with_name("Material Stock Low")
            .with_description("Critical material inventory is low")
            .with_category(AlertCategory.RESOURCE)
            .with_severity(AlertSeverity.MEDIUM)
            .add_condition("resource.material_stock_days", ConditionOperator.LESS_THAN, 3)
            .with_cooldown(1440)
            .notify_via(NotificationChannel.EMAIL)
            .build(),
            
            AlertRuleBuilder()
            .with_id("resource_equipment_unavailable")
            .with_name("Equipment Unavailable")
            .with_description("Required equipment is not available")
            .with_category(AlertCategory.EQUIPMENT)
            .with_severity(AlertSeverity.HIGH)
            .add_condition("equipment.availability_percent", ConditionOperator.LESS_THAN, 50)
            .with_cooldown(120)
            .notify_via(NotificationChannel.EMAIL, NotificationChannel.PUSH)
            .build()
        ]
    
    @staticmethod
    def get_all_rules() -> List[AlertRule]:
        """Get all pre-built construction alert rules"""
        rules = []
        rules.extend(ConstructionAlertRules.create_safety_rules())
        rules.extend(ConstructionAlertRules.create_schedule_rules())
        rules.extend(ConstructionAlertRules.create_cost_rules())
        rules.extend(ConstructionAlertRules.create_quality_rules())
        rules.extend(ConstructionAlertRules.create_resource_rules())
        return rules


# ============================================
# Alert System Integration
# ============================================

class AlertingSystem:
    """
    Main alerting system integration point
    
    Provides unified interface for all alerting functionality
    """
    
    def __init__(self):
        self.manager = AlertManager()
        
        # Load construction-specific rules
        for rule in ConstructionAlertRules.get_all_rules():
            self.manager.add_rule(rule)
    
    def process_project_metrics(
        self,
        project_id: str,
        metrics: Dict[str, float]
    ):
        """
        Process project metrics and trigger alerts
        
        Args:
            project_id: Project identifier
            metrics: Dictionary of metric values
        """
        # Add project context
        metrics_with_context = {f"{k}": v for k, v in metrics.items()}
        
        self.manager.evaluate_metrics(
            metrics_with_context,
            source=f"project:{project_id}"
        )
    
    def create_custom_alert(
        self,
        title: str,
        message: str,
        category: AlertCategory,
        severity: AlertSeverity,
        source: str,
        context: Optional[Dict] = None
    ) -> Optional[Alert]:
        """Create a custom alert without rule matching"""
        # Create temporary rule
        temp_rule = AlertRule(
            id=f"custom_{datetime.utcnow().timestamp()}",
            name=title,
            description=message,
            category=category,
            severity=severity,
            conditions=[],
            cooldown_minutes=0,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH]
        )
        
        self.manager.add_rule(temp_rule)
        
        return self.manager.create_alert(
            rule_id=temp_rule.id,
            title=title,
            message=message,
            source=source,
            context=context
        )
    
    def get_alerts(
        self,
        status: Optional[AlertStatus] = None,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get alerts with filtering"""
        alerts = self.manager.get_active_alerts(category, severity)
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        if project_id:
            alerts = [
                a for a in alerts 
                if a.context.get('project_id') == project_id
            ]
        
        return [asdict(a) for a in alerts]
    
    def acknowledge(self, alert_id: str, user_id: str, note: Optional[str] = None) -> bool:
        """Acknowledge an alert"""
        result = self.manager.acknowledge_alert(alert_id, user_id, note)
        return result is not None
    
    def resolve(self, alert_id: str, user_id: str, resolution: Optional[str] = None) -> bool:
        """Resolve an alert"""
        result = self.manager.resolve_alert(alert_id, user_id, resolution)
        return result is not None
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get alerting dashboard"""
        return self.manager.get_dashboard()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alerting statistics"""
        return self.manager.get_alert_statistics()
    
    def configure_notification(
        self,
        channel: NotificationChannel,
        config: Dict[str, Any]
    ):
        """Configure notification provider"""
        if channel == NotificationChannel.EMAIL:
            self.manager.providers[channel] = EmailProvider(config)
        elif channel == NotificationChannel.SMS:
            self.manager.providers[channel] = SMSProvider(config)
        elif channel == NotificationChannel.WEBHOOK:
            self.manager.providers[channel] = WebhookProvider(config.get('url'))
        elif channel == NotificationChannel.SLACK:
            self.manager.providers[channel] = SlackProvider(config.get('token'))
        elif channel == NotificationChannel.TEAMS:
            self.manager.providers[channel] = TeamsProvider(config.get('webhook_url'))


# Convenience instance
alerting_system = AlertingSystem()
