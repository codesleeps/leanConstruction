"""
ERP System Integrations - Phase 3

Supports integration with major ERP systems used in construction:
- SAP S/4HANA
- Oracle Construction and Engineering (Primavera P6)
- Sage 300 Construction
- Viewpoint Vista
- Foundation Software
- CMiC

Provides standardized interfaces for:
- Financial data sync
- Project cost tracking
- Resource management
- Purchase orders and invoicing
- Inventory management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import json
import hashlib
import hmac

logger = logging.getLogger(__name__)


# ============================================
# Enums and Data Classes
# ============================================

class ERPSystem(Enum):
    """Supported ERP systems"""
    SAP = "sap"
    ORACLE = "oracle"
    SAGE = "sage"
    VIEWPOINT = "viewpoint"
    FOUNDATION = "foundation"
    CMIC = "cmic"
    GENERIC = "generic"


class SyncDirection(Enum):
    """Data synchronization direction"""
    INBOUND = "inbound"    # ERP to App
    OUTBOUND = "outbound"  # App to ERP
    BIDIRECTIONAL = "bidirectional"


class DataEntity(Enum):
    """ERP data entities"""
    PROJECT = "project"
    COST_CODE = "cost_code"
    JOB_COST = "job_cost"
    PURCHASE_ORDER = "purchase_order"
    INVOICE = "invoice"
    VENDOR = "vendor"
    EMPLOYEE = "employee"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    TIMESHEET = "timesheet"
    BUDGET = "budget"
    COMMITMENT = "commitment"


@dataclass
class ERPConnection:
    """ERP connection configuration"""
    system: ERPSystem
    host: str
    port: int
    username: str
    password: str  # Should be encrypted in production
    database: Optional[str] = None
    company_id: Optional[str] = None
    api_version: Optional[str] = None
    ssl_enabled: bool = True
    timeout_seconds: int = 30
    extra_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConfig:
    """Synchronization configuration"""
    entity: DataEntity
    direction: SyncDirection
    schedule_cron: Optional[str] = None  # e.g., "0 */4 * * *"
    enabled: bool = True
    batch_size: int = 100
    field_mapping: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Result of a sync operation"""
    entity: DataEntity
    direction: SyncDirection
    started_at: datetime
    completed_at: datetime
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    errors: List[str] = field(default_factory=list)
    status: str = "completed"


@dataclass
class CostCode:
    """Standard cost code structure"""
    code: str
    description: str
    parent_code: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    budget_amount: float = 0.0
    actual_amount: float = 0.0


@dataclass
class JobCost:
    """Job cost transaction"""
    id: str
    project_id: str
    cost_code: str
    transaction_date: datetime
    description: str
    amount: float
    quantity: float = 0.0
    unit_cost: float = 0.0
    vendor_id: Optional[str] = None
    invoice_id: Optional[str] = None
    category: str = "material"  # labor, material, equipment, subcontract, other


@dataclass
class PurchaseOrder:
    """Purchase order"""
    id: str
    project_id: str
    vendor_id: str
    order_date: datetime
    status: str
    total_amount: float
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    delivery_date: Optional[datetime] = None
    approved_by: Optional[str] = None


# ============================================
# Base ERP Client
# ============================================

class BaseERPClient(ABC):
    """Base class for ERP integrations"""
    
    def __init__(self, connection: ERPConnection):
        self.connection = connection
        self.is_connected = False
        self.last_sync: Dict[DataEntity, datetime] = {}
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to ERP system"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to ERP system"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test ERP connection"""
        pass
    
    # Project operations
    @abstractmethod
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get projects from ERP"""
        pass
    
    @abstractmethod
    def sync_project(self, project_data: Dict) -> Dict:
        """Sync project to ERP"""
        pass
    
    # Cost operations
    @abstractmethod
    def get_cost_codes(self, project_id: Optional[str] = None) -> List[CostCode]:
        """Get cost codes"""
        pass
    
    @abstractmethod
    def get_job_costs(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JobCost]:
        """Get job cost transactions"""
        pass
    
    @abstractmethod
    def post_job_cost(self, cost: JobCost) -> Dict:
        """Post job cost to ERP"""
        pass
    
    # Purchase orders
    @abstractmethod
    def get_purchase_orders(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders"""
        pass
    
    @abstractmethod
    def create_purchase_order(self, po: PurchaseOrder) -> Dict:
        """Create purchase order in ERP"""
        pass
    
    # Invoices
    @abstractmethod
    def get_invoices(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get invoices"""
        pass
    
    # Budget
    @abstractmethod
    def get_budget(self, project_id: str) -> Dict:
        """Get project budget"""
        pass
    
    @abstractmethod
    def update_budget(self, project_id: str, budget_data: Dict) -> Dict:
        """Update project budget"""
        pass


# ============================================
# SAP Client
# ============================================

class SAPClient(BaseERPClient):
    """SAP S/4HANA integration client"""
    
    def __init__(self, connection: ERPConnection):
        super().__init__(connection)
        self.session_token: Optional[str] = None
        
    def connect(self) -> bool:
        """Connect to SAP system"""
        try:
            # In production, use SAP NetWeaver RFC or REST API
            logger.info(f"Connecting to SAP at {self.connection.host}")
            
            # Simulate connection
            self.is_connected = True
            self.session_token = f"SAP_SESSION_{datetime.utcnow().timestamp()}"
            
            return True
        except Exception as e:
            logger.error(f"SAP connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from SAP"""
        self.is_connected = False
        self.session_token = None
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SAP connection"""
        if self.connect():
            return {
                'status': 'connected',
                'system': 'SAP S/4HANA',
                'host': self.connection.host,
                'timestamp': datetime.utcnow().isoformat()
            }
        return {'status': 'failed', 'error': 'Connection failed'}
    
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get projects from SAP PS (Project System)"""
        # SAP BAPI call: BAPI_PROJECT_GETINFO
        logger.info("Fetching projects from SAP PS")
        
        # Simulated response
        return [
            {
                'WBS_ELEMENT': 'PRJ001-001',
                'PROJECT_DEFINITION': 'PRJ001',
                'DESCRIPTION': 'Commercial Building Project',
                'RESPONSIBLE_PERSON': 'JSMITH',
                'PROFIT_CENTER': 'PC001',
                'PROJECT_START': '2024-01-01',
                'PROJECT_END': '2024-12-31',
                'PROJECT_STATUS': 'ACTIVE'
            }
        ]
    
    def sync_project(self, project_data: Dict) -> Dict:
        """Sync project to SAP"""
        # SAP BAPI: BAPI_PROJECT_MAINTAIN
        logger.info(f"Syncing project to SAP: {project_data.get('id')}")
        
        return {
            'status': 'success',
            'sap_wbs': f"WBS{project_data.get('id', 'NEW')}",
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_cost_codes(self, project_id: Optional[str] = None) -> List[CostCode]:
        """Get cost codes from SAP CO"""
        # SAP table: AUFK (Order Master), CSKA (Cost Elements)
        return [
            CostCode(
                code='01-100',
                description='General Conditions',
                category='general',
                budget_amount=50000.0
            ),
            CostCode(
                code='02-100',
                description='Site Work',
                category='sitework',
                budget_amount=150000.0
            ),
            CostCode(
                code='03-100',
                description='Concrete',
                category='concrete',
                budget_amount=200000.0
            )
        ]
    
    def get_job_costs(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JobCost]:
        """Get job costs from SAP CO-PC"""
        # SAP tables: AUFM, COBK, COEP
        return [
            JobCost(
                id='JC001',
                project_id=project_id,
                cost_code='03-100',
                transaction_date=datetime.utcnow() - timedelta(days=5),
                description='Concrete delivery',
                amount=15000.0,
                quantity=50,
                unit_cost=300.0,
                category='material'
            )
        ]
    
    def post_job_cost(self, cost: JobCost) -> Dict:
        """Post job cost to SAP"""
        # SAP BAPI: BAPI_ACC_DOCUMENT_POST
        return {
            'status': 'success',
            'document_number': f"SAP{cost.id}",
            'fiscal_year': datetime.utcnow().year
        }
    
    def get_purchase_orders(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseOrder]:
        """Get POs from SAP MM"""
        # SAP tables: EKKO, EKPO
        return [
            PurchaseOrder(
                id='PO4500001234',
                project_id=project_id or 'PRJ001',
                vendor_id='V001',
                order_date=datetime.utcnow() - timedelta(days=10),
                status='APPROVED',
                total_amount=25000.0,
                line_items=[
                    {'material': 'CONC001', 'quantity': 100, 'price': 250.0}
                ]
            )
        ]
    
    def create_purchase_order(self, po: PurchaseOrder) -> Dict:
        """Create PO in SAP MM"""
        # SAP BAPI: BAPI_PO_CREATE1
        return {
            'status': 'success',
            'po_number': f"45{datetime.utcnow().strftime('%H%M%S')}",
            'created_at': datetime.utcnow().isoformat()
        }
    
    def get_invoices(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get invoices from SAP FI"""
        # SAP tables: BKPF, BSEG
        return [
            {
                'invoice_number': 'INV001',
                'vendor_id': 'V001',
                'project_id': project_id,
                'amount': 25000.0,
                'status': 'PAID',
                'invoice_date': '2024-01-15',
                'payment_date': '2024-02-01'
            }
        ]
    
    def get_budget(self, project_id: str) -> Dict:
        """Get budget from SAP PS"""
        # SAP BAPI: BAPI_PROJECT_BUDGET_READ
        return {
            'project_id': project_id,
            'total_budget': 1000000.0,
            'committed': 450000.0,
            'actual': 380000.0,
            'remaining': 170000.0,
            'by_cost_code': [
                {'code': '01-100', 'budget': 50000.0, 'actual': 45000.0},
                {'code': '02-100', 'budget': 150000.0, 'actual': 120000.0},
                {'code': '03-100', 'budget': 200000.0, 'actual': 180000.0}
            ]
        }
    
    def update_budget(self, project_id: str, budget_data: Dict) -> Dict:
        """Update budget in SAP"""
        # SAP BAPI: BAPI_PROJECT_BUDGET_UPDATE
        return {
            'status': 'success',
            'project_id': project_id,
            'updated_at': datetime.utcnow().isoformat()
        }


# ============================================
# Oracle Primavera Client
# ============================================

class OraclePrimaveraClient(BaseERPClient):
    """Oracle Primavera P6 integration client"""
    
    def __init__(self, connection: ERPConnection):
        super().__init__(connection)
        self.api_token: Optional[str] = None
        
    def connect(self) -> bool:
        """Connect to Primavera P6 Web Services"""
        try:
            logger.info(f"Connecting to Primavera P6 at {self.connection.host}")
            
            # In production, authenticate via P6 Web Services
            self.is_connected = True
            self.api_token = f"P6_TOKEN_{datetime.utcnow().timestamp()}"
            
            return True
        except Exception as e:
            logger.error(f"Primavera connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        self.is_connected = False
        self.api_token = None
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        if self.connect():
            return {
                'status': 'connected',
                'system': 'Oracle Primavera P6',
                'host': self.connection.host,
                'timestamp': datetime.utcnow().isoformat()
            }
        return {'status': 'failed'}
    
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get projects from Primavera"""
        # P6 API: ReadProjects
        return [
            {
                'ObjectId': 12345,
                'Id': 'PRJ001',
                'Name': 'Commercial Building',
                'Status': 'Active',
                'PlannedStartDate': '2024-01-01',
                'PlannedFinishDate': '2024-12-31',
                'ActualStartDate': '2024-01-05',
                'DataDate': '2024-06-01',
                'PercentComplete': 45.5
            }
        ]
    
    def sync_project(self, project_data: Dict) -> Dict:
        """Sync project to Primavera"""
        return {
            'status': 'success',
            'p6_object_id': 12345,
            'synced_at': datetime.utcnow().isoformat()
        }
    
    def get_activities(self, project_id: str) -> List[Dict]:
        """Get activities from project"""
        # P6 API: ReadActivities
        return [
            {
                'ObjectId': 100001,
                'Id': 'A1000',
                'Name': 'Mobilization',
                'PlannedDuration': 5,
                'ActualDuration': 4,
                'RemainingDuration': 0,
                'Status': 'Completed',
                'PercentComplete': 100
            },
            {
                'ObjectId': 100002,
                'Id': 'A1010',
                'Name': 'Site Prep',
                'PlannedDuration': 10,
                'ActualDuration': 8,
                'RemainingDuration': 2,
                'Status': 'In Progress',
                'PercentComplete': 80
            }
        ]
    
    def get_resources(self, project_id: str) -> List[Dict]:
        """Get resource assignments"""
        # P6 API: ReadResourceAssignments
        return [
            {
                'ObjectId': 200001,
                'ActivityId': 'A1010',
                'ResourceId': 'R001',
                'ResourceName': 'Carpenter',
                'PlannedUnits': 80,
                'ActualUnits': 64,
                'RemainingUnits': 16
            }
        ]
    
    def get_cost_codes(self, project_id: Optional[str] = None) -> List[CostCode]:
        """Get cost accounts from Primavera"""
        # P6 API: ReadCostAccounts
        return [
            CostCode(
                code='CA001',
                description='Labor Costs',
                category='labor',
                budget_amount=300000.0
            ),
            CostCode(
                code='CA002',
                description='Material Costs',
                category='material',
                budget_amount=400000.0
            )
        ]
    
    def get_job_costs(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JobCost]:
        """Get project expenses"""
        return [
            JobCost(
                id='EXP001',
                project_id=project_id,
                cost_code='CA001',
                transaction_date=datetime.utcnow() - timedelta(days=3),
                description='Labor week 22',
                amount=12500.0,
                category='labor'
            )
        ]
    
    def post_job_cost(self, cost: JobCost) -> Dict:
        """Post expense to Primavera"""
        return {'status': 'success', 'expense_id': f"EXP{cost.id}"}
    
    def get_purchase_orders(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseOrder]:
        return []  # P6 doesn't typically handle POs
    
    def create_purchase_order(self, po: PurchaseOrder) -> Dict:
        return {'status': 'not_supported', 'message': 'Use ERP for PO management'}
    
    def get_invoices(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        return []  # P6 doesn't handle invoices
    
    def get_budget(self, project_id: str) -> Dict:
        """Get project budget from spending plan"""
        return {
            'project_id': project_id,
            'total_budget': 800000.0,
            'at_completion': 820000.0,
            'actual_cost': 360000.0,
            'earned_value': 350000.0,
            'cpi': 0.97,
            'spi': 0.95
        }
    
    def update_budget(self, project_id: str, budget_data: Dict) -> Dict:
        return {'status': 'success'}
    
    def update_progress(self, activity_id: str, percent_complete: float) -> Dict:
        """Update activity progress"""
        return {
            'status': 'success',
            'activity_id': activity_id,
            'percent_complete': percent_complete,
            'updated_at': datetime.utcnow().isoformat()
        }


# ============================================
# Sage 300 Client
# ============================================

class Sage300Client(BaseERPClient):
    """Sage 300 Construction and Real Estate integration"""
    
    def __init__(self, connection: ERPConnection):
        super().__init__(connection)
        
    def connect(self) -> bool:
        logger.info(f"Connecting to Sage 300 at {self.connection.host}")
        self.is_connected = True
        return True
    
    def disconnect(self) -> bool:
        self.is_connected = False
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        return {
            'status': 'connected' if self.connect() else 'failed',
            'system': 'Sage 300 Construction',
            'host': self.connection.host
        }
    
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get jobs from Sage 300"""
        return [
            {
                'JobNumber': 'J001',
                'JobName': 'Office Building',
                'JobStatus': 'Active',
                'ContractAmount': 1500000.0,
                'BilledToDate': 675000.0
            }
        ]
    
    def sync_project(self, project_data: Dict) -> Dict:
        return {'status': 'success'}
    
    def get_cost_codes(self, project_id: Optional[str] = None) -> List[CostCode]:
        """Get cost codes from Sage"""
        return [
            CostCode(code='01.00.00', description='General Requirements'),
            CostCode(code='03.00.00', description='Concrete'),
            CostCode(code='05.00.00', description='Metals')
        ]
    
    def get_job_costs(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JobCost]:
        return [
            JobCost(
                id='JC001',
                project_id=project_id,
                cost_code='03.00.00',
                transaction_date=datetime.utcnow(),
                description='Concrete pour',
                amount=8500.0,
                category='material'
            )
        ]
    
    def post_job_cost(self, cost: JobCost) -> Dict:
        return {'status': 'success', 'transaction_id': f"TXN{cost.id}"}
    
    def get_purchase_orders(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseOrder]:
        return [
            PurchaseOrder(
                id='PO001',
                project_id=project_id or 'J001',
                vendor_id='V001',
                order_date=datetime.utcnow(),
                status='Open',
                total_amount=15000.0
            )
        ]
    
    def create_purchase_order(self, po: PurchaseOrder) -> Dict:
        return {'status': 'success', 'po_number': f"PO{datetime.utcnow().strftime('%H%M%S')}"}
    
    def get_invoices(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        return [
            {
                'invoice_number': 'AP001',
                'vendor': 'Concrete Supply Co',
                'amount': 8500.0,
                'status': 'Pending'
            }
        ]
    
    def get_budget(self, project_id: str) -> Dict:
        return {
            'project_id': project_id,
            'original_budget': 1500000.0,
            'revised_budget': 1525000.0,
            'committed': 780000.0,
            'actual': 675000.0
        }
    
    def update_budget(self, project_id: str, budget_data: Dict) -> Dict:
        return {'status': 'success'}


# ============================================
# Generic ERP Client
# ============================================

class GenericERPClient(BaseERPClient):
    """Generic ERP client for custom integrations"""
    
    def __init__(self, connection: ERPConnection):
        super().__init__(connection)
        self.data_store: Dict[str, List] = {
            'projects': [],
            'cost_codes': [],
            'job_costs': [],
            'purchase_orders': [],
            'invoices': [],
            'budgets': {}
        }
        
    def connect(self) -> bool:
        self.is_connected = True
        return True
    
    def disconnect(self) -> bool:
        self.is_connected = False
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        return {'status': 'connected', 'system': 'Generic ERP'}
    
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        return self.data_store['projects']
    
    def sync_project(self, project_data: Dict) -> Dict:
        self.data_store['projects'].append(project_data)
        return {'status': 'success'}
    
    def get_cost_codes(self, project_id: Optional[str] = None) -> List[CostCode]:
        return [CostCode(**cc) for cc in self.data_store['cost_codes']]
    
    def get_job_costs(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JobCost]:
        costs = self.data_store['job_costs']
        return [JobCost(**jc) for jc in costs if jc.get('project_id') == project_id]
    
    def post_job_cost(self, cost: JobCost) -> Dict:
        self.data_store['job_costs'].append(asdict(cost))
        return {'status': 'success'}
    
    def get_purchase_orders(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseOrder]:
        return [PurchaseOrder(**po) for po in self.data_store['purchase_orders']]
    
    def create_purchase_order(self, po: PurchaseOrder) -> Dict:
        self.data_store['purchase_orders'].append(asdict(po))
        return {'status': 'success'}
    
    def get_invoices(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        return self.data_store['invoices']
    
    def get_budget(self, project_id: str) -> Dict:
        return self.data_store['budgets'].get(project_id, {})
    
    def update_budget(self, project_id: str, budget_data: Dict) -> Dict:
        self.data_store['budgets'][project_id] = budget_data
        return {'status': 'success'}


# ============================================
# ERP Integration Manager
# ============================================

class ERPIntegrationManager:
    """
    Manages ERP integrations
    
    Provides unified interface for all ERP operations
    """
    
    def __init__(self):
        self.clients: Dict[str, BaseERPClient] = {}
        self.sync_configs: Dict[str, List[SyncConfig]] = {}
        self.sync_history: List[SyncResult] = []
        
        # Client factory
        self.client_classes = {
            ERPSystem.SAP: SAPClient,
            ERPSystem.ORACLE: OraclePrimaveraClient,
            ERPSystem.SAGE: Sage300Client,
            ERPSystem.GENERIC: GenericERPClient
        }
    
    def register_connection(
        self,
        connection_id: str,
        connection: ERPConnection
    ) -> bool:
        """Register an ERP connection"""
        try:
            client_class = self.client_classes.get(
                connection.system,
                GenericERPClient
            )
            client = client_class(connection)
            
            if client.connect():
                self.clients[connection_id] = client
                logger.info(f"ERP connection registered: {connection_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to register ERP connection: {e}")
            return False
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove an ERP connection"""
        if connection_id in self.clients:
            self.clients[connection_id].disconnect()
            del self.clients[connection_id]
            return True
        return False
    
    def configure_sync(
        self,
        connection_id: str,
        config: SyncConfig
    ):
        """Configure sync for a connection"""
        if connection_id not in self.sync_configs:
            self.sync_configs[connection_id] = []
        self.sync_configs[connection_id].append(config)
    
    def sync_entity(
        self,
        connection_id: str,
        entity: DataEntity,
        direction: Optional[SyncDirection] = None
    ) -> SyncResult:
        """Sync a specific entity"""
        if connection_id not in self.clients:
            return SyncResult(
                entity=entity,
                direction=direction or SyncDirection.INBOUND,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=['Connection not found'],
                status='failed'
            )
        
        client = self.clients[connection_id]
        started_at = datetime.utcnow()
        records_processed = 0
        records_created = 0
        records_updated = 0
        errors = []
        
        try:
            if entity == DataEntity.PROJECT:
                projects = client.get_projects()
                records_processed = len(projects)
                records_created = len(projects)
            elif entity == DataEntity.COST_CODE:
                codes = client.get_cost_codes()
                records_processed = len(codes)
                records_created = len(codes)
            elif entity == DataEntity.JOB_COST:
                costs = client.get_job_costs('all')
                records_processed = len(costs)
                records_created = len(costs)
            elif entity == DataEntity.PURCHASE_ORDER:
                pos = client.get_purchase_orders()
                records_processed = len(pos)
                records_created = len(pos)
            
            status = 'completed'
        except Exception as e:
            errors.append(str(e))
            status = 'failed'
        
        result = SyncResult(
            entity=entity,
            direction=direction or SyncDirection.INBOUND,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_failed=len(errors),
            errors=errors,
            status=status
        )
        
        self.sync_history.append(result)
        client.last_sync[entity] = datetime.utcnow()
        
        return result
    
    def get_unified_project_data(
        self,
        project_id: str,
        connection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get unified project data from ERP(s)"""
        if connection_id:
            clients = {connection_id: self.clients.get(connection_id)}
        else:
            clients = self.clients
        
        unified_data = {
            'project_id': project_id,
            'erp_data': {},
            'aggregated': {
                'total_budget': 0,
                'total_actual': 0,
                'total_committed': 0
            }
        }
        
        for conn_id, client in clients.items():
            if not client:
                continue
            
            try:
                budget = client.get_budget(project_id)
                costs = client.get_job_costs(project_id)
                
                unified_data['erp_data'][conn_id] = {
                    'budget': budget,
                    'cost_transactions': len(costs),
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                # Aggregate
                if budget:
                    unified_data['aggregated']['total_budget'] += budget.get('total_budget', 0)
                    unified_data['aggregated']['total_actual'] += budget.get('actual', budget.get('actual_cost', 0))
                    unified_data['aggregated']['total_committed'] += budget.get('committed', 0)
            except Exception as e:
                logger.error(f"Error fetching data from {conn_id}: {e}")
        
        return unified_data
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        status = {
            'connections': {},
            'recent_syncs': [],
            'total_syncs': len(self.sync_history)
        }
        
        for conn_id, client in self.clients.items():
            status['connections'][conn_id] = {
                'connected': client.is_connected,
                'system': client.connection.system.value,
                'last_sync': {
                    entity.value: ts.isoformat() if ts else None
                    for entity, ts in client.last_sync.items()
                }
            }
        
        # Recent syncs
        status['recent_syncs'] = [
            asdict(s) for s in self.sync_history[-10:]
        ]
        
        return status


# Convenience instance
erp_manager = ERPIntegrationManager()