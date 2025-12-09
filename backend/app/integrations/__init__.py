"""
Integration modules for Lean Construction App

Phase 3 - Expanded Third-party Integrations:
- Procore API client
- ERP Systems (SAP, Oracle Primavera, Sage 300)
- IoT Sensor integrations
"""

from backend.app.integrations.procore import ProcoreClient
from backend.app.integrations.erp_systems import (
    ERPIntegrationManager,
    erp_manager,
    ERPSystem,
    ERPConnection,
    SyncConfig,
    SyncResult,
    DataEntity,
    SyncDirection,
    SAPClient,
    OraclePrimaveraClient,
    Sage300Client,
    GenericERPClient,
    CostCode,
    JobCost,
    PurchaseOrder
)
from backend.app.integrations.iot_sensors import (
    IoTIntegrationSystem,
    iot_system,
    DeviceManager,
    DataProcessor,
    ThresholdMonitor,
    SensorType,
    DeviceStatus,
    AlertLevel,
    Protocol,
    SensorReading,
    DeviceConfig,
    SensorConfig,
    ThresholdEvent,
    ConstructionSensorPresets
)

__all__ = [
    # Procore
    'ProcoreClient',
    
    # ERP Systems
    'ERPIntegrationManager',
    'erp_manager',
    'ERPSystem',
    'ERPConnection',
    'SyncConfig',
    'SyncResult',
    'DataEntity',
    'SyncDirection',
    'SAPClient',
    'OraclePrimaveraClient',
    'Sage300Client',
    'GenericERPClient',
    'CostCode',
    'JobCost',
    'PurchaseOrder',
    
    # IoT Sensors
    'IoTIntegrationSystem',
    'iot_system',
    'DeviceManager',
    'DataProcessor',
    'ThresholdMonitor',
    'SensorType',
    'DeviceStatus',
    'AlertLevel',
    'Protocol',
    'SensorReading',
    'DeviceConfig',
    'SensorConfig',
    'ThresholdEvent',
    'ConstructionSensorPresets'
]
