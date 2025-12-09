"""
Industry-specific Customizations for Lean Construction AI

This module provides tailored configurations for different construction sectors:
- Commercial construction
- Residential construction
- Industrial construction
- Infrastructure/Civil
- Healthcare facilities
- Educational facilities
- Hospitality
- Mixed-use development
- Renovation/Retrofit
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


# ============================================
# Enums and Data Classes
# ============================================

class IndustrySector(Enum):
    """Construction industry sectors"""
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    HEALTHCARE = "healthcare"
    EDUCATIONAL = "educational"
    HOSPITALITY = "hospitality"
    MIXED_USE = "mixed_use"
    RENOVATION = "renovation"
    DATA_CENTER = "data_center"
    ENERGY = "energy"


class ProjectSize(Enum):
    """Project size classifications"""
    SMALL = "small"  # < $1M
    MEDIUM = "medium"  # $1M - $10M
    LARGE = "large"  # $10M - $100M
    MEGA = "mega"  # > $100M


class DeliveryMethod(Enum):
    """Project delivery methods"""
    DESIGN_BID_BUILD = "design_bid_build"
    DESIGN_BUILD = "design_build"
    CM_AT_RISK = "cm_at_risk"
    INTEGRATED_PROJECT_DELIVERY = "ipd"
    PUBLIC_PRIVATE_PARTNERSHIP = "p3"


class ComplianceFramework(Enum):
    """Regulatory compliance frameworks"""
    OSHA = "osha"
    EPA = "epa"
    ADA = "ada"
    IBC = "ibc"
    LEED = "leed"
    WELL = "well"
    HIPAA = "hipaa"  # Healthcare
    FERPA = "ferpa"  # Educational
    FDA = "fda"  # Pharmaceutical
    NERC = "nerc"  # Energy


@dataclass
class IndustryProfile:
    """Profile defining industry-specific configurations"""
    sector: IndustrySector
    name: str
    description: str
    typical_phases: List[str]
    critical_trades: List[str]
    key_kpis: List[str]
    compliance_frameworks: List[ComplianceFramework]
    waste_priorities: List[str]
    safety_focus_areas: List[str]
    quality_checkpoints: List[str]
    typical_duration_range: Dict[str, int]  # months
    typical_budget_range: Dict[str, int]  # USD
    specialty_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CustomWorkflow:
    """Custom workflow for a specific industry"""
    id: str
    name: str
    sector: IndustrySector
    stages: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    notifications: List[Dict[str, Any]]
    approvals: List[Dict[str, Any]]


@dataclass
class IndustryTemplate:
    """Project template for an industry"""
    id: str
    name: str
    sector: IndustrySector
    description: str
    milestones: List[Dict[str, Any]]
    task_templates: List[Dict[str, Any]]
    resource_templates: List[Dict[str, Any]]
    checklist_templates: List[Dict[str, Any]]
    document_templates: List[str]


# ============================================
# Industry Profiles
# ============================================

class IndustryProfileRegistry:
    """Registry of industry-specific profiles"""
    
    def __init__(self):
        self.profiles: Dict[IndustrySector, IndustryProfile] = {}
        self._initialize_profiles()
    
    def _initialize_profiles(self):
        """Initialize all industry profiles"""
        
        # Commercial Construction
        self.profiles[IndustrySector.COMMERCIAL] = IndustryProfile(
            sector=IndustrySector.COMMERCIAL,
            name="Commercial Construction",
            description="Office buildings, retail spaces, and commercial facilities",
            typical_phases=[
                "Preconstruction", "Site Preparation", "Foundation",
                "Structural", "Building Envelope", "MEP Rough-in",
                "Interior Build-out", "Finishes", "Commissioning", "Turnover"
            ],
            critical_trades=[
                "structural_steel", "concrete", "curtain_wall",
                "hvac", "electrical", "elevator", "fire_protection"
            ],
            key_kpis=[
                "schedule_performance_index", "cost_performance_index",
                "tenant_improvement_completion", "leed_certification_progress",
                "punch_list_items", "change_order_rate"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.IBC,
                ComplianceFramework.ADA, ComplianceFramework.LEED
            ],
            waste_priorities=["waiting", "overproduction", "motion"],
            safety_focus_areas=[
                "fall_protection", "crane_operations", "electrical_safety",
                "confined_spaces", "steel_erection"
            ],
            quality_checkpoints=[
                "foundation_inspection", "structural_inspection",
                "envelope_weather_tight", "mep_rough_in_inspection",
                "final_inspection"
            ],
            typical_duration_range={"min": 12, "max": 36},
            typical_budget_range={"min": 5000000, "max": 200000000},
            specialty_requirements={
                "tenant_coordination": True,
                "phased_occupancy": True,
                "core_and_shell": True
            }
        )
        
        # Residential Construction
        self.profiles[IndustrySector.RESIDENTIAL] = IndustryProfile(
            sector=IndustrySector.RESIDENTIAL,
            name="Residential Construction",
            description="Single-family homes, multi-family, and residential communities",
            typical_phases=[
                "Site Development", "Foundation", "Framing",
                "Roofing", "MEP Rough-in", "Insulation",
                "Drywall", "Finishes", "Landscaping", "Final"
            ],
            critical_trades=[
                "framing", "roofing", "plumbing", "electrical",
                "hvac", "drywall", "flooring", "painting"
            ],
            key_kpis=[
                "units_completed_per_week", "cycle_time_per_unit",
                "warranty_callback_rate", "customer_satisfaction",
                "trade_partner_reliability"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.IBC,
                ComplianceFramework.EPA
            ],
            waste_priorities=["inventory", "transportation", "defects"],
            safety_focus_areas=[
                "fall_protection", "ladder_safety", "trench_safety",
                "power_tool_safety"
            ],
            quality_checkpoints=[
                "foundation_inspection", "framing_inspection",
                "rough_in_inspection", "insulation_inspection",
                "final_inspection"
            ],
            typical_duration_range={"min": 4, "max": 18},
            typical_budget_range={"min": 200000, "max": 10000000},
            specialty_requirements={
                "production_housing": True,
                "spec_vs_custom": True,
                "warranty_management": True
            }
        )
        
        # Industrial Construction
        self.profiles[IndustrySector.INDUSTRIAL] = IndustryProfile(
            sector=IndustrySector.INDUSTRIAL,
            name="Industrial Construction",
            description="Manufacturing plants, warehouses, and distribution centers",
            typical_phases=[
                "Site Development", "Foundation", "Structural Steel",
                "Roofing/Envelope", "Concrete Floors", "MEP Installation",
                "Process Equipment", "Commissioning", "Startup"
            ],
            critical_trades=[
                "structural_steel", "concrete", "process_piping",
                "electrical", "instrumentation", "insulation", "fireproofing"
            ],
            key_kpis=[
                "schedule_performance_index", "equipment_setting_rate",
                "quality_weld_rejection_rate", "commissioning_punch_items",
                "startup_days_vs_plan"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.EPA,
                ComplianceFramework.IBC
            ],
            waste_priorities=["waiting", "transportation", "extra_processing"],
            safety_focus_areas=[
                "crane_operations", "hot_work", "confined_spaces",
                "fall_protection", "rigging", "lockout_tagout"
            ],
            quality_checkpoints=[
                "foundation_inspection", "steel_erection_inspection",
                "weld_inspection", "equipment_setting", "loop_checks",
                "functional_testing"
            ],
            typical_duration_range={"min": 12, "max": 48},
            typical_budget_range={"min": 10000000, "max": 500000000},
            specialty_requirements={
                "process_integration": True,
                "equipment_procurement": True,
                "commissioning_startup": True
            }
        )
        
        # Infrastructure/Civil
        self.profiles[IndustrySector.INFRASTRUCTURE] = IndustryProfile(
            sector=IndustrySector.INFRASTRUCTURE,
            name="Infrastructure/Civil Construction",
            description="Roads, bridges, tunnels, utilities, and public works",
            typical_phases=[
                "Mobilization", "Clearing/Demolition", "Earthwork",
                "Drainage/Utilities", "Subgrade Preparation", "Paving/Structures",
                "Finishing", "Landscaping", "Punch List", "Demobilization"
            ],
            critical_trades=[
                "earthwork", "paving", "concrete", "structural",
                "utilities", "drainage", "traffic_control"
            ],
            key_kpis=[
                "linear_feet_per_day", "cubic_yards_per_day",
                "traffic_control_incidents", "environmental_compliance",
                "utility_conflicts_resolved"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.EPA,
                ComplianceFramework.ADA
            ],
            waste_priorities=["waiting", "transportation", "inventory"],
            safety_focus_areas=[
                "traffic_control", "trench_safety", "heavy_equipment",
                "fall_protection", "struck_by_hazards"
            ],
            quality_checkpoints=[
                "subgrade_inspection", "compaction_testing",
                "paving_inspection", "structural_inspection",
                "utility_inspection"
            ],
            typical_duration_range={"min": 6, "max": 60},
            typical_budget_range={"min": 1000000, "max": 1000000000},
            specialty_requirements={
                "traffic_management": True,
                "environmental_permits": True,
                "utility_coordination": True,
                "night_work": True
            }
        )
        
        # Healthcare
        self.profiles[IndustrySector.HEALTHCARE] = IndustryProfile(
            sector=IndustrySector.HEALTHCARE,
            name="Healthcare Construction",
            description="Hospitals, medical offices, and healthcare facilities",
            typical_phases=[
                "Preconstruction", "Site Preparation", "Foundation",
                "Structure", "Building Envelope", "MEP Rough-in",
                "Interior Build-out", "Medical Equipment", 
                "Commissioning", "Licensure", "Turnover"
            ],
            critical_trades=[
                "concrete", "structural", "hvac", "medical_gas",
                "electrical", "low_voltage", "fire_protection", "plumbing"
            ],
            key_kpis=[
                "infection_control_compliance", "noise_level_compliance",
                "vibration_control", "schedule_performance_index",
                "medical_equipment_installation_rate"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.HIPAA,
                ComplianceFramework.IBC, ComplianceFramework.ADA,
                ComplianceFramework.LEED
            ],
            waste_priorities=["waiting", "defects", "overproduction"],
            safety_focus_areas=[
                "infection_control", "fall_protection", "hot_work",
                "medical_gas_safety", "radiation_protection"
            ],
            quality_checkpoints=[
                "icra_compliance", "med_gas_inspection", "hvac_balancing",
                "radiation_shielding_test", "final_inspection"
            ],
            typical_duration_range={"min": 18, "max": 60},
            typical_budget_range={"min": 20000000, "max": 1000000000},
            specialty_requirements={
                "icra_requirements": True,
                "interim_life_safety": True,
                "medical_equipment_coordination": True,
                "phased_occupancy": True
            }
        )
        
        # Educational
        self.profiles[IndustrySector.EDUCATIONAL] = IndustryProfile(
            sector=IndustrySector.EDUCATIONAL,
            name="Educational Construction",
            description="Schools, universities, and educational facilities",
            typical_phases=[
                "Preconstruction", "Site Preparation", "Foundation",
                "Structure", "Building Envelope", "MEP Rough-in",
                "Interior Build-out", "Technology/AV", "Finishes",
                "FF&E", "Commissioning", "Turnover"
            ],
            critical_trades=[
                "concrete", "masonry", "structural", "hvac",
                "electrical", "low_voltage", "flooring"
            ],
            key_kpis=[
                "schedule_performance_index", "summer_work_completion",
                "technology_infrastructure_complete", "acoustic_compliance",
                "ada_compliance"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.IBC,
                ComplianceFramework.ADA, ComplianceFramework.FERPA,
                ComplianceFramework.LEED
            ],
            waste_priorities=["waiting", "inventory", "transportation"],
            safety_focus_areas=[
                "fall_protection", "occupied_building_safety",
                "student_safety", "traffic_control"
            ],
            quality_checkpoints=[
                "foundation_inspection", "structural_inspection",
                "acoustic_testing", "technology_testing",
                "final_inspection"
            ],
            typical_duration_range={"min": 12, "max": 36},
            typical_budget_range={"min": 5000000, "max": 300000000},
            specialty_requirements={
                "summer_construction": True,
                "occupied_construction": True,
                "technology_integration": True
            }
        )
        
        # Data Center
        self.profiles[IndustrySector.DATA_CENTER] = IndustryProfile(
            sector=IndustrySector.DATA_CENTER,
            name="Data Center Construction",
            description="Data centers and critical infrastructure facilities",
            typical_phases=[
                "Preconstruction", "Site Preparation", "Foundation",
                "Structure", "Building Envelope", "Electrical Infrastructure",
                "Mechanical Infrastructure", "Raised Floor", "Racks/Cabling",
                "Commissioning", "Testing", "Turnover"
            ],
            critical_trades=[
                "electrical", "hvac", "fire_suppression", "concrete",
                "structural", "low_voltage", "security"
            ],
            key_kpis=[
                "power_capacity_delivered", "cooling_capacity",
                "tier_certification_progress", "commissioning_test_pass_rate",
                "schedule_performance_index"
            ],
            compliance_frameworks=[
                ComplianceFramework.OSHA, ComplianceFramework.IBC,
                ComplianceFramework.EPA
            ],
            waste_priorities=["defects", "waiting", "extra_processing"],
            safety_focus_areas=[
                "electrical_safety", "fall_protection", "confined_spaces",
                "rigging", "arc_flash"
            ],
            quality_checkpoints=[
                "foundation_inspection", "electrical_infrastructure",
                "mechanical_system_testing", "isc_testing",
                "tier_certification"
            ],
            typical_duration_range={"min": 12, "max": 36},
            typical_budget_range={"min": 50000000, "max": 2000000000},
            specialty_requirements={
                "tier_certification": True,
                "redundancy_requirements": True,
                "commissioning_intensive": True
            }
        )
    
    def get_profile(self, sector: IndustrySector) -> Optional[IndustryProfile]:
        """Get profile for a sector"""
        return self.profiles.get(sector)
    
    def get_all_sectors(self) -> List[str]:
        """Get all available sectors"""
        return [s.value for s in self.profiles.keys()]


# ============================================
# Industry-specific KPI Configurations
# ============================================

class IndustryKPIConfig:
    """Industry-specific KPI configurations"""
    
    def __init__(self):
        self.kpi_configs: Dict[IndustrySector, Dict] = {}
        self._initialize_configs()
    
    def _initialize_configs(self):
        """Initialize KPI configs for each industry"""
        
        self.kpi_configs[IndustrySector.COMMERCIAL] = {
            'primary_kpis': [
                'schedule_performance_index',
                'cost_performance_index',
                'tenant_improvement_completion',
                'leed_points_achieved'
            ],
            'targets': {
                'schedule_performance_index': 1.0,
                'cost_performance_index': 1.0,
                'tenant_improvement_completion': 95,
                'leed_points_achieved': 50,
                'punch_list_items_per_1000_sqft': 2
            },
            'benchmarks': {
                'schedule_performance_index': 0.95,
                'cost_performance_index': 0.92,
                'change_order_rate': 5.0
            },
            'custom_kpis': [
                {
                    'id': 'tenant_improvement_completion',
                    'name': 'TI Completion Rate',
                    'formula': 'completed_ti_sqft / total_ti_sqft * 100',
                    'unit': '%',
                    'target': 95
                },
                {
                    'id': 'core_shell_progress',
                    'name': 'Core & Shell Progress',
                    'formula': 'core_shell_complete / total_core_shell * 100',
                    'unit': '%'
                }
            ]
        }
        
        self.kpi_configs[IndustrySector.RESIDENTIAL] = {
            'primary_kpis': [
                'units_completed_per_week',
                'cycle_time_days',
                'warranty_callback_rate',
                'customer_satisfaction'
            ],
            'targets': {
                'units_completed_per_week': 5,
                'cycle_time_days': 120,
                'warranty_callback_rate': 2.0,
                'customer_satisfaction': 90
            },
            'benchmarks': {
                'cycle_time_days': 150,
                'warranty_callback_rate': 5.0,
                'customer_satisfaction': 85
            },
            'custom_kpis': [
                {
                    'id': 'units_completed_per_week',
                    'name': 'Units Completed/Week',
                    'formula': 'completed_units / weeks_in_period',
                    'unit': 'units'
                },
                {
                    'id': 'trade_partner_reliability',
                    'name': 'Trade Partner Reliability',
                    'formula': 'on_time_completions / total_scheduled * 100',
                    'unit': '%',
                    'target': 95
                }
            ]
        }
        
        self.kpi_configs[IndustrySector.HEALTHCARE] = {
            'primary_kpis': [
                'icra_compliance_rate',
                'noise_level_compliance',
                'schedule_performance_index',
                'commissioning_progress'
            ],
            'targets': {
                'icra_compliance_rate': 100,
                'noise_level_compliance': 100,
                'schedule_performance_index': 1.0,
                'infection_incidents': 0
            },
            'benchmarks': {
                'icra_compliance_rate': 98,
                'commissioning_punch_items': 50
            },
            'custom_kpis': [
                {
                    'id': 'icra_compliance_rate',
                    'name': 'ICRA Compliance Rate',
                    'formula': 'compliant_inspections / total_inspections * 100',
                    'unit': '%',
                    'target': 100
                },
                {
                    'id': 'med_equipment_installation',
                    'name': 'Medical Equipment Installation',
                    'formula': 'installed_equipment / total_equipment * 100',
                    'unit': '%'
                }
            ]
        }
        
        self.kpi_configs[IndustrySector.DATA_CENTER] = {
            'primary_kpis': [
                'power_capacity_mw',
                'pue_efficiency',
                'commissioning_test_pass_rate',
                'tier_compliance'
            ],
            'targets': {
                'power_capacity_mw': 50,
                'pue_efficiency': 1.3,
                'commissioning_test_pass_rate': 98,
                'tier_compliance': 100
            },
            'benchmarks': {
                'pue_efficiency': 1.5,
                'commissioning_test_pass_rate': 95
            },
            'custom_kpis': [
                {
                    'id': 'power_capacity_delivered',
                    'name': 'Power Capacity Delivered',
                    'formula': 'delivered_mw / planned_mw * 100',
                    'unit': '%'
                },
                {
                    'id': 'cooling_capacity',
                    'name': 'Cooling Capacity',
                    'formula': 'delivered_tons / required_tons * 100',
                    'unit': '%'
                },
                {
                    'id': 'tier_certification_progress',
                    'name': 'Tier Certification Progress',
                    'formula': 'achieved_requirements / total_requirements * 100',
                    'unit': '%'
                }
            ]
        }
    
    def get_config(self, sector: IndustrySector) -> Dict[str, Any]:
        """Get KPI configuration for a sector"""
        return self.kpi_configs.get(sector, {})


# ============================================
# Industry-specific Workflows
# ============================================

class IndustryWorkflowManager:
    """Manages industry-specific workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, CustomWorkflow] = {}
        self._initialize_standard_workflows()
    
    def _initialize_standard_workflows(self):
        """Initialize standard workflows for each industry"""
        
        # Healthcare ICRA workflow
        icra_workflow = CustomWorkflow(
            id='healthcare_icra',
            name='ICRA Compliance Workflow',
            sector=IndustrySector.HEALTHCARE,
            stages=[
                {
                    'id': 'risk_assessment',
                    'name': 'Risk Assessment',
                    'required_approvals': ['infection_control', 'safety'],
                    'documents': ['icra_matrix', 'permit']
                },
                {
                    'id': 'barrier_installation',
                    'name': 'Barrier Installation',
                    'required_inspections': ['barrier_integrity'],
                    'checklist': 'icra_barrier_checklist'
                },
                {
                    'id': 'monitoring',
                    'name': 'Continuous Monitoring',
                    'frequency': 'daily',
                    'measurements': ['air_quality', 'pressure_differential']
                },
                {
                    'id': 'completion',
                    'name': 'Work Completion',
                    'required_inspections': ['final_inspection'],
                    'documents': ['completion_certificate']
                }
            ],
            triggers=[
                {'event': 'work_near_patient_area', 'action': 'start_icra_workflow'},
                {'event': 'barrier_breach', 'action': 'alert_infection_control'}
            ],
            notifications=[
                {'role': 'infection_control', 'events': ['all']},
                {'role': 'project_manager', 'events': ['barrier_breach', 'inspection_failure']}
            ],
            approvals=[
                {'stage': 'risk_assessment', 'approvers': ['infection_control', 'safety']},
                {'stage': 'completion', 'approvers': ['infection_control']}
            ]
        )
        self.workflows[icra_workflow.id] = icra_workflow
        
        # Commercial Tenant Coordination workflow
        tenant_workflow = CustomWorkflow(
            id='commercial_tenant_coord',
            name='Tenant Coordination Workflow',
            sector=IndustrySector.COMMERCIAL,
            stages=[
                {
                    'id': 'tenant_requirements',
                    'name': 'Requirements Gathering',
                    'documents': ['tenant_criteria', 'space_plan']
                },
                {
                    'id': 'design_approval',
                    'name': 'Design Approval',
                    'required_approvals': ['tenant', 'landlord', 'architect'],
                    'deadline_days': 14
                },
                {
                    'id': 'permit_submission',
                    'name': 'Permit Submission',
                    'documents': ['permit_set', 'application']
                },
                {
                    'id': 'construction',
                    'name': 'TI Construction',
                    'milestones': ['rough_in', 'finishes', 'substantial_completion']
                },
                {
                    'id': 'turnover',
                    'name': 'Tenant Turnover',
                    'required_inspections': ['final_inspection'],
                    'documents': ['certificate_of_occupancy', 'warranty_info']
                }
            ],
            triggers=[
                {'event': 'lease_signed', 'action': 'start_tenant_workflow'},
                {'event': 'design_complete', 'action': 'notify_permit_submission'}
            ],
            notifications=[
                {'role': 'tenant_rep', 'events': ['all']},
                {'role': 'project_manager', 'events': ['approval_pending', 'milestone_complete']}
            ],
            approvals=[
                {'stage': 'design_approval', 'approvers': ['tenant', 'landlord']},
                {'stage': 'turnover', 'approvers': ['tenant', 'building_management']}
            ]
        )
        self.workflows[tenant_workflow.id] = tenant_workflow
        
        # Data Center Commissioning workflow
        commissioning_workflow = CustomWorkflow(
            id='datacenter_commissioning',
            name='Data Center Commissioning Workflow',
            sector=IndustrySector.DATA_CENTER,
            stages=[
                {
                    'id': 'l1_factory_tests',
                    'name': 'Level 1: Factory Tests',
                    'tests': ['equipment_fat']
                },
                {
                    'id': 'l2_installation_verification',
                    'name': 'Level 2: Installation Verification',
                    'inspections': ['installation_checklist']
                },
                {
                    'id': 'l3_component_testing',
                    'name': 'Level 3: Component Testing',
                    'tests': ['individual_equipment_tests']
                },
                {
                    'id': 'l4_system_testing',
                    'name': 'Level 4: System Testing',
                    'tests': ['integrated_system_tests']
                },
                {
                    'id': 'l5_isc_testing',
                    'name': 'Level 5: ISC Testing',
                    'tests': ['load_bank_testing', 'failover_testing']
                }
            ],
            triggers=[
                {'event': 'equipment_delivered', 'action': 'schedule_fat_verification'},
                {'event': 'test_failure', 'action': 'create_deficiency_report'}
            ],
            notifications=[
                {'role': 'commissioning_agent', 'events': ['all']},
                {'role': 'owner', 'events': ['l5_complete', 'critical_failure']}
            ],
            approvals=[
                {'stage': 'l5_isc_testing', 'approvers': ['owner', 'commissioning_agent']}
            ]
        )
        self.workflows[commissioning_workflow.id] = commissioning_workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[CustomWorkflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_workflows_for_sector(self, sector: IndustrySector) -> List[CustomWorkflow]:
        """Get all workflows for a sector"""
        return [w for w in self.workflows.values() if w.sector == sector]


# ============================================
# Industry-specific Templates
# ============================================

class IndustryTemplateManager:
    """Manages industry-specific project templates"""
    
    def __init__(self):
        self.templates: Dict[str, IndustryTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize project templates"""
        
        # Commercial Office Building Template
        self.templates['commercial_office'] = IndustryTemplate(
            id='commercial_office',
            name='Commercial Office Building',
            sector=IndustrySector.COMMERCIAL,
            description='Template for commercial office building construction',
            milestones=[
                {'name': 'Excavation Complete', 'percent_complete': 5},
                {'name': 'Foundation Complete', 'percent_complete': 10},
                {'name': 'Structure Complete', 'percent_complete': 30},
                {'name': 'Weather Tight', 'percent_complete': 45},
                {'name': 'MEP Rough-in Complete', 'percent_complete': 60},
                {'name': 'Interior Finishes Complete', 'percent_complete': 85},
                {'name': 'Substantial Completion', 'percent_complete': 95},
                {'name': 'Final Completion', 'percent_complete': 100}
            ],
            task_templates=[
                {'phase': 'foundation', 'tasks': ['excavation', 'footings', 'foundation_walls', 'slab_on_grade']},
                {'phase': 'structure', 'tasks': ['steel_erection', 'metal_decking', 'concrete_pours']},
                {'phase': 'envelope', 'tasks': ['curtain_wall', 'roofing', 'waterproofing']},
                {'phase': 'mep', 'tasks': ['hvac_rough', 'electrical_rough', 'plumbing_rough', 'fire_protection']},
                {'phase': 'finishes', 'tasks': ['drywall', 'flooring', 'painting', 'ceilings']}
            ],
            resource_templates=[
                {'trade': 'structural_steel', 'peak_weeks': [8, 12], 'typical_crew_size': 20},
                {'trade': 'concrete', 'peak_weeks': [4, 8, 16], 'typical_crew_size': 15},
                {'trade': 'hvac', 'peak_weeks': [20, 30], 'typical_crew_size': 12}
            ],
            checklist_templates=[
                'pre_construction_checklist',
                'structural_inspection_checklist',
                'mep_inspection_checklist',
                'closeout_checklist'
            ],
            document_templates=[
                'meeting_minutes', 'rfi', 'submittal', 'change_order',
                'daily_report', 'safety_plan', 'quality_plan'
            ]
        )
        
        # Healthcare Hospital Template
        self.templates['healthcare_hospital'] = IndustryTemplate(
            id='healthcare_hospital',
            name='Hospital Building',
            sector=IndustrySector.HEALTHCARE,
            description='Template for hospital construction with ICRA requirements',
            milestones=[
                {'name': 'Site Preparation Complete', 'percent_complete': 5},
                {'name': 'Foundation Complete', 'percent_complete': 12},
                {'name': 'Structure Complete', 'percent_complete': 28},
                {'name': 'Weather Tight', 'percent_complete': 40},
                {'name': 'MEP Rough-in Complete', 'percent_complete': 55},
                {'name': 'Medical Equipment Rough-in', 'percent_complete': 65},
                {'name': 'Interior Finishes Complete', 'percent_complete': 80},
                {'name': 'Commissioning Complete', 'percent_complete': 92},
                {'name': 'Licensure Approval', 'percent_complete': 98},
                {'name': 'Final Completion', 'percent_complete': 100}
            ],
            task_templates=[
                {'phase': 'foundation', 'tasks': ['excavation', 'footings', 'foundation_walls', 'radiation_shielding']},
                {'phase': 'structure', 'tasks': ['concrete_structure', 'steel_framing']},
                {'phase': 'mep', 'tasks': ['medical_gas', 'hvac', 'electrical', 'plumbing', 'nurse_call']},
                {'phase': 'equipment', 'tasks': ['imaging_equipment', 'surgical_equipment', 'lab_equipment']},
                {'phase': 'commissioning', 'tasks': ['hvac_balancing', 'medical_gas_testing', 'emergency_power_testing']}
            ],
            resource_templates=[
                {'trade': 'medical_gas', 'peak_weeks': [24, 32], 'typical_crew_size': 8},
                {'trade': 'hvac', 'peak_weeks': [20, 36], 'typical_crew_size': 20},
                {'trade': 'electrical', 'peak_weeks': [18, 38], 'typical_crew_size': 25}
            ],
            checklist_templates=[
                'icra_checklist',
                'medical_gas_checklist',
                'radiation_shielding_checklist',
                'commissioning_checklist',
                'licensure_checklist'
            ],
            document_templates=[
                'icra_permit', 'infection_control_plan', 'commissioning_plan',
                'medical_equipment_log', 'licensure_application'
            ]
        )
        
        # Data Center Template
        self.templates['data_center_facility'] = IndustryTemplate(
            id='data_center_facility',
            name='Data Center Facility',
            sector=IndustrySector.DATA_CENTER,
            description='Template for data center construction with commissioning focus',
            milestones=[
                {'name': 'Site Preparation Complete', 'percent_complete': 5},
                {'name': 'Shell Complete', 'percent_complete': 25},
                {'name': 'Electrical Infrastructure Complete', 'percent_complete': 50},
                {'name': 'Mechanical Infrastructure Complete', 'percent_complete': 65},
                {'name': 'Raised Floor Complete', 'percent_complete': 75},
                {'name': 'L3 Testing Complete', 'percent_complete': 85},
                {'name': 'L4 Testing Complete', 'percent_complete': 92},
                {'name': 'ISC Testing Complete', 'percent_complete': 98},
                {'name': 'Turnover', 'percent_complete': 100}
            ],
            task_templates=[
                {'phase': 'electrical', 'tasks': ['switchgear', 'transformers', 'generators', 'ups_systems', 'pdu']},
                {'phase': 'mechanical', 'tasks': ['chillers', 'cooling_towers', 'crac_units', 'piping']},
                {'phase': 'infrastructure', 'tasks': ['raised_floor', 'cable_trays', 'racks', 'fire_suppression']},
                {'phase': 'commissioning', 'tasks': ['l1_fat', 'l2_inspection', 'l3_component', 'l4_system', 'l5_isc']}
            ],
            resource_templates=[
                {'trade': 'electrical', 'peak_weeks': [12, 28], 'typical_crew_size': 40},
                {'trade': 'mechanical', 'peak_weeks': [16, 26], 'typical_crew_size': 25},
                {'trade': 'commissioning', 'peak_weeks': [30, 40], 'typical_crew_size': 15}
            ],
            checklist_templates=[
                'electrical_installation_checklist',
                'mechanical_installation_checklist',
                'commissioning_test_scripts',
                'isc_test_procedures',
                'tier_certification_checklist'
            ],
            document_templates=[
                'commissioning_plan', 'test_procedures', 'deficiency_log',
                'tier_documentation', 'as_built_drawings'
            ]
        )
    
    def get_template(self, template_id: str) -> Optional[IndustryTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_for_sector(self, sector: IndustrySector) -> List[IndustryTemplate]:
        """Get all templates for a sector"""
        return [t for t in self.templates.values() if t.sector == sector]


# ============================================
# Compliance Configuration Manager
# ============================================

class ComplianceConfigManager:
    """Manages compliance configurations for different industries"""
    
    def __init__(self):
        self.compliance_requirements: Dict[IndustrySector, List[Dict]] = {}
        self._initialize_compliance()
    
    def _initialize_compliance(self):
        """Initialize compliance requirements"""
        
        self.compliance_requirements[IndustrySector.HEALTHCARE] = [
            {
                'framework': ComplianceFramework.HIPAA,
                'requirements': [
                    'patient_data_protection',
                    'access_control',
                    'audit_trails',
                    'encryption_requirements'
                ],
                'documentation': ['hipaa_compliance_plan', 'risk_assessment'],
                'inspections': ['quarterly_audit']
            },
            {
                'framework': ComplianceFramework.ADA,
                'requirements': [
                    'accessible_routes',
                    'signage',
                    'restroom_accessibility',
                    'parking_accessibility'
                ],
                'documentation': ['ada_compliance_checklist'],
                'inspections': ['final_ada_inspection']
            }
        ]
        
        self.compliance_requirements[IndustrySector.DATA_CENTER] = [
            {
                'framework': 'uptime_institute',
                'requirements': [
                    'redundancy_requirements',
                    'maintainability',
                    'fault_tolerance',
                    'compartmentalization'
                ],
                'documentation': ['tier_compliance_documentation'],
                'inspections': ['tier_certification_inspection']
            }
        ]
        
        self.compliance_requirements[IndustrySector.EDUCATIONAL] = [
            {
                'framework': ComplianceFramework.FERPA,
                'requirements': [
                    'student_record_protection',
                    'access_control',
                    'security_systems'
                ],
                'documentation': ['ferpa_compliance_plan'],
                'inspections': ['annual_audit']
            }
        ]
    
    def get_requirements(self, sector: IndustrySector) -> List[Dict]:
        """Get compliance requirements for a sector"""
        return self.compliance_requirements.get(sector, [])


# ============================================
# Industry Customization System
# ============================================

class IndustryCustomizationSystem:
    """Integrated system for industry-specific customizations"""
    
    def __init__(self):
        self.profile_registry = IndustryProfileRegistry()
        self.kpi_config = IndustryKPIConfig()
        self.workflow_manager = IndustryWorkflowManager()
        self.template_manager = IndustryTemplateManager()
        self.compliance_manager = ComplianceConfigManager()
    
    def get_industry_configuration(
        self,
        sector: str,
        project_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get complete industry configuration"""
        try:
            industry_sector = IndustrySector(sector)
        except ValueError:
            return {'error': f'Unknown sector: {sector}'}
        
        profile = self.profile_registry.get_profile(industry_sector)
        if not profile:
            return {'error': f'No profile for sector: {sector}'}
        
        kpi_config = self.kpi_config.get_config(industry_sector)
        workflows = self.workflow_manager.get_workflows_for_sector(industry_sector)
        templates = self.template_manager.get_templates_for_sector(industry_sector)
        compliance = self.compliance_manager.get_requirements(industry_sector)
        
        return {
            'sector': sector,
            'profile': {
                'name': profile.name,
                'description': profile.description,
                'typical_phases': profile.typical_phases,
                'critical_trades': profile.critical_trades,
                'safety_focus_areas': profile.safety_focus_areas,
                'waste_priorities': profile.waste_priorities,
                'typical_duration': profile.typical_duration_range,
                'typical_budget': profile.typical_budget_range
            },
            'kpi_configuration': kpi_config,
            'workflows': [
                {
                    'id': w.id,
                    'name': w.name,
                    'stages': len(w.stages)
                }
                for w in workflows
            ],
            'templates': [
                {
                    'id': t.id,
                    'name': t.name,
                    'milestones': len(t.milestones)
                }
                for t in templates
            ],
            'compliance_requirements': compliance
        }
    
    def apply_industry_template(
        self,
        project_data: Dict[str, Any],
        template_id: str
    ) -> Dict[str, Any]:
        """Apply industry template to a project"""
        template = self.template_manager.get_template(template_id)
        if not template:
            return {'error': f'Template {template_id} not found'}
        
        # Apply template to project
        project_data['milestones'] = template.milestones
        project_data['phase_templates'] = template.task_templates
        project_data['resource_plan'] = template.resource_templates
        project_data['checklists'] = template.checklist_templates
        project_data['document_templates'] = template.document_templates
        project_data['industry_sector'] = template.sector.value
        
        return {
            'success': True,
            'template_applied': template_id,
            'milestones_added': len(template.milestones),
            'phases_configured': len(template.task_templates)
        }
    
    def get_available_sectors(self) -> List[Dict[str, str]]:
        """Get all available industry sectors"""
        return [
            {
                'id': sector.value,
                'name': profile.name,
                'description': profile.description
            }
            for sector, profile in self.profile_registry.profiles.items()
        ]
    
    def get_sector_benchmarks(
        self,
        sector: str
    ) -> Dict[str, Any]:
        """Get industry benchmarks for a sector"""
        try:
            industry_sector = IndustrySector(sector)
        except ValueError:
            return {'error': f'Unknown sector: {sector}'}
        
        kpi_config = self.kpi_config.get_config(industry_sector)
        
        return {
            'sector': sector,
            'targets': kpi_config.get('targets', {}),
            'benchmarks': kpi_config.get('benchmarks', {}),
            'custom_kpis': kpi_config.get('custom_kpis', [])
        }
    
    def validate_industry_compliance(
        self,
        sector: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate project compliance for industry"""
        try:
            industry_sector = IndustrySector(sector)
        except ValueError:
            return {'error': f'Unknown sector: {sector}'}
        
        requirements = self.compliance_manager.get_requirements(industry_sector)
        
        results = {
            'sector': sector,
            'compliant': True,
            'frameworks': [],
            'issues': [],
            'recommendations': []
        }
        
        for req in requirements:
            framework_result = {
                'framework': req['framework'].value if isinstance(req['framework'], Enum) else req['framework'],
                'requirements_checked': len(req['requirements']),
                'passed': 0,
                'failed': 0
            }
            
            for requirement in req['requirements']:
                # Check if requirement is met (simplified check)
                if project_data.get(requirement):
                    framework_result['passed'] += 1
                else:
                    framework_result['failed'] += 1
                    results['issues'].append({
                        'framework': framework_result['framework'],
                        'requirement': requirement,
                        'status': 'not_met'
                    })
                    results['recommendations'].append(
                        f"Address {requirement} for {framework_result['framework']} compliance"
                    )
            
            if framework_result['failed'] > 0:
                results['compliant'] = False
            
            results['frameworks'].append(framework_result)
        
        return results


# Create singleton instance
industry_customization_system = IndustryCustomizationSystem()


# ============================================
# Convenience Functions
# ============================================

def get_industry_profile(sector: str) -> Dict[str, Any]:
    """Get profile for an industry sector"""
    return industry_customization_system.get_industry_configuration(sector)


def apply_template(project_data: Dict[str, Any], template_id: str) -> Dict[str, Any]:
    """Apply industry template to project"""
    return industry_customization_system.apply_industry_template(project_data, template_id)


def get_sectors() -> List[Dict[str, str]]:
    """Get all available sectors"""
    return industry_customization_system.get_available_sectors()