"""
IoT Sensor Integrations - Phase 3

Supports integration with IoT sensors and devices for construction monitoring:
- Environmental sensors (temperature, humidity, dust, noise)
- Structural sensors (strain gauges, vibration, tilt)
- Equipment sensors (GPS, fuel, utilization, diagnostics)
- Safety sensors (gas detection, proximity, wearables)
- Weather stations
- Drones and cameras

Provides:
- Real-time data collection
- Data aggregation and processing
- Threshold monitoring and alerting
- Historical data storage
- Device management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import json
import threading
import queue
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


# ============================================
# Enums and Data Classes
# ============================================

class SensorType(Enum):
    """Types of IoT sensors"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    DUST = "dust"
    NOISE = "noise"
    VIBRATION = "vibration"
    TILT = "tilt"
    STRAIN = "strain"
    GAS = "gas"
    GPS = "gps"
    FUEL = "fuel"
    PRESSURE = "pressure"
    MOTION = "motion"
    PROXIMITY = "proximity"
    WIND = "wind"
    RAINFALL = "rainfall"
    LIGHT = "light"
    POWER = "power"
    WATER_FLOW = "water_flow"
    CONCRETE_CURE = "concrete_cure"
    WEARABLE = "wearable"


class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class AlertLevel(Enum):
    """Alert levels for sensor thresholds"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class Protocol(Enum):
    """Communication protocols"""
    MQTT = "mqtt"
    COAP = "coap"
    HTTP = "http"
    WEBSOCKET = "websocket"
    LORAWAN = "lorawan"
    ZIGBEE = "zigbee"
    BLUETOOTH = "bluetooth"
    MODBUS = "modbus"


@dataclass
class SensorReading:
    """Individual sensor reading"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    quality: float = 1.0  # Data quality score 0-1
    location: Optional[Dict[str, float]] = None  # lat, lon, elevation
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceConfig:
    """IoT device configuration"""
    device_id: str
    name: str
    device_type: str
    sensors: List[str]  # List of sensor IDs
    protocol: Protocol
    host: Optional[str] = None
    port: Optional[int] = None
    auth_token: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    sampling_interval_seconds: int = 60
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SensorConfig:
    """Sensor configuration"""
    sensor_id: str
    device_id: str
    sensor_type: SensorType
    name: str
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    warning_low: Optional[float] = None
    warning_high: Optional[float] = None
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    calibration_offset: float = 0.0
    calibration_factor: float = 1.0
    enabled: bool = True


@dataclass
class ThresholdEvent:
    """Threshold crossing event"""
    sensor_id: str
    sensor_type: SensorType
    level: AlertLevel
    value: float
    threshold: float
    direction: str  # "above" or "below"
    timestamp: datetime
    duration_seconds: int = 0


@dataclass
class DeviceHealth:
    """Device health status"""
    device_id: str
    status: DeviceStatus
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None
    last_seen: Optional[datetime] = None
    error_count: int = 0
    uptime_seconds: int = 0


# ============================================
# Data Processors
# ============================================

class DataProcessor:
    """Processes and aggregates sensor data"""
    
    def __init__(self):
        self.buffer: Dict[str, List[SensorReading]] = defaultdict(list)
        self.aggregates: Dict[str, Dict] = {}
        self.buffer_size = 1000
        
    def add_reading(self, reading: SensorReading):
        """Add reading to buffer"""
        self.buffer[reading.sensor_id].append(reading)
        
        # Trim buffer if too large
        if len(self.buffer[reading.sensor_id]) > self.buffer_size:
            self.buffer[reading.sensor_id] = self.buffer[reading.sensor_id][-self.buffer_size:]
    
    def get_latest(self, sensor_id: str) -> Optional[SensorReading]:
        """Get latest reading for sensor"""
        readings = self.buffer.get(sensor_id, [])
        return readings[-1] if readings else None
    
    def get_readings(
        self,
        sensor_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorReading]:
        """Get readings within time range"""
        readings = self.buffer.get(sensor_id, [])
        
        if start_time:
            readings = [r for r in readings if r.timestamp >= start_time]
        if end_time:
            readings = [r for r in readings if r.timestamp <= end_time]
        
        return readings[-limit:]
    
    def calculate_statistics(
        self,
        sensor_id: str,
        window_minutes: int = 60
    ) -> Dict[str, float]:
        """Calculate statistics for sensor"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        readings = [
            r for r in self.buffer.get(sensor_id, [])
            if r.timestamp >= cutoff
        ]
        
        if not readings:
            return {}
        
        values = [r.value for r in readings]
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'std': self._std(values),
            'count': len(values),
            'latest': values[-1],
            'window_minutes': window_minutes
        }
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def detect_anomalies(
        self,
        sensor_id: str,
        std_threshold: float = 3.0
    ) -> List[SensorReading]:
        """Detect anomalous readings"""
        stats = self.calculate_statistics(sensor_id, 60)
        if not stats:
            return []
        
        avg = stats['avg']
        std = stats['std']
        
        if std == 0:
            return []
        
        anomalies = []
        for reading in self.buffer.get(sensor_id, [])[-100:]:
            z_score = abs(reading.value - avg) / std
            if z_score > std_threshold:
                anomalies.append(reading)
        
        return anomalies
    
    def get_trend(
        self,
        sensor_id: str,
        window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Analyze value trend"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        readings = [
            r for r in self.buffer.get(sensor_id, [])
            if r.timestamp >= cutoff
        ]
        
        if len(readings) < 2:
            return {'trend': 'insufficient_data'}
        
        values = [r.value for r in readings]
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend direction
        if slope > 0.1:
            direction = 'increasing'
        elif slope < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'trend': direction,
            'slope': slope,
            'start_value': values[0],
            'end_value': values[-1],
            'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        }


# ============================================
# Threshold Monitor
# ============================================

class ThresholdMonitor:
    """Monitors sensor values against thresholds"""
    
    def __init__(self):
        self.sensor_configs: Dict[str, SensorConfig] = {}
        self.active_alerts: Dict[str, ThresholdEvent] = {}
        self.alert_history: List[ThresholdEvent] = []
        self.callbacks: List[Callable[[ThresholdEvent], None]] = []
        
    def configure_sensor(self, config: SensorConfig):
        """Configure sensor thresholds"""
        self.sensor_configs[config.sensor_id] = config
    
    def register_callback(self, callback: Callable[[ThresholdEvent], None]):
        """Register alert callback"""
        self.callbacks.append(callback)
    
    def check_threshold(self, reading: SensorReading) -> Optional[ThresholdEvent]:
        """Check reading against thresholds"""
        config = self.sensor_configs.get(reading.sensor_id)
        if not config or not config.enabled:
            return None
        
        # Apply calibration
        calibrated_value = (reading.value + config.calibration_offset) * config.calibration_factor
        
        level = AlertLevel.NORMAL
        threshold = 0
        direction = ""
        
        # Check critical thresholds first
        if config.critical_high is not None and calibrated_value > config.critical_high:
            level = AlertLevel.CRITICAL
            threshold = config.critical_high
            direction = "above"
        elif config.critical_low is not None and calibrated_value < config.critical_low:
            level = AlertLevel.CRITICAL
            threshold = config.critical_low
            direction = "below"
        elif config.warning_high is not None and calibrated_value > config.warning_high:
            level = AlertLevel.WARNING
            threshold = config.warning_high
            direction = "above"
        elif config.warning_low is not None and calibrated_value < config.warning_low:
            level = AlertLevel.WARNING
            threshold = config.warning_low
            direction = "below"
        
        # Create event if threshold crossed
        if level != AlertLevel.NORMAL:
            event = ThresholdEvent(
                sensor_id=reading.sensor_id,
                sensor_type=reading.sensor_type,
                level=level,
                value=calibrated_value,
                threshold=threshold,
                direction=direction,
                timestamp=reading.timestamp
            )
            
            # Track duration of existing alert
            existing = self.active_alerts.get(reading.sensor_id)
            if existing and existing.level == level:
                event.duration_seconds = int(
                    (reading.timestamp - existing.timestamp).total_seconds()
                )
            else:
                self.active_alerts[reading.sensor_id] = event
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Threshold callback error: {e}")
            
            self.alert_history.append(event)
            return event
        else:
            # Clear active alert if back to normal
            if reading.sensor_id in self.active_alerts:
                del self.active_alerts[reading.sensor_id]
        
        return None
    
    def get_active_alerts(self) -> List[ThresholdEvent]:
        """Get all active threshold alerts"""
        return list(self.active_alerts.values())


# ============================================
# Protocol Handlers
# ============================================

class MQTTHandler:
    """MQTT protocol handler"""
    
    def __init__(self, broker: str, port: int = 1883, credentials: Optional[Dict] = None):
        self.broker = broker
        self.port = port
        self.credentials = credentials
        self.subscriptions: Dict[str, Callable] = {}
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            # In production, use paho-mqtt library
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            return False
    
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to MQTT topic"""
        self.subscriptions[topic] = callback
        logger.info(f"Subscribed to MQTT topic: {topic}")
    
    def publish(self, topic: str, payload: Dict):
        """Publish message to topic"""
        if not self.is_connected:
            return False
        
        logger.debug(f"Publishing to {topic}: {payload}")
        return True
    
    def disconnect(self):
        """Disconnect from broker"""
        self.is_connected = False


class HTTPHandler:
    """HTTP/REST protocol handler"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        
    def get(self, endpoint: str) -> Optional[Dict]:
        """HTTP GET request"""
        # In production, use requests library
        logger.info(f"HTTP GET {self.base_url}/{endpoint}")
        return {}
    
    def post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """HTTP POST request"""
        logger.info(f"HTTP POST {self.base_url}/{endpoint}")
        return {'status': 'success'}


class WebSocketHandler:
    """WebSocket protocol handler"""
    
    def __init__(self, url: str):
        self.url = url
        self.is_connected = False
        self.message_callback: Optional[Callable] = None
        
    def connect(self) -> bool:
        """Connect to WebSocket server"""
        logger.info(f"Connecting to WebSocket at {self.url}")
        self.is_connected = True
        return True
    
    def on_message(self, callback: Callable):
        """Register message callback"""
        self.message_callback = callback
    
    def send(self, message: Dict):
        """Send message"""
        if not self.is_connected:
            return False
        logger.debug(f"WebSocket send: {message}")
        return True


# ============================================
# Device Manager
# ============================================

class DeviceManager:
    """Manages IoT devices"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceConfig] = {}
        self.sensors: Dict[str, SensorConfig] = {}
        self.device_health: Dict[str, DeviceHealth] = {}
        self.protocol_handlers: Dict[str, Any] = {}
        
    def register_device(self, config: DeviceConfig) -> bool:
        """Register a new device"""
        self.devices[config.device_id] = config
        
        # Initialize health tracking
        self.device_health[config.device_id] = DeviceHealth(
            device_id=config.device_id,
            status=DeviceStatus.OFFLINE,
            last_seen=None
        )
        
        logger.info(f"Device registered: {config.device_id} ({config.name})")
        return True
    
    def register_sensor(self, config: SensorConfig) -> bool:
        """Register a sensor"""
        self.sensors[config.sensor_id] = config
        
        # Add to device's sensor list
        if config.device_id in self.devices:
            if config.sensor_id not in self.devices[config.device_id].sensors:
                self.devices[config.device_id].sensors.append(config.sensor_id)
        
        logger.info(f"Sensor registered: {config.sensor_id} ({config.name})")
        return True
    
    def update_device_status(
        self,
        device_id: str,
        status: DeviceStatus,
        battery: Optional[float] = None,
        signal: Optional[float] = None
    ):
        """Update device health status"""
        if device_id not in self.device_health:
            return
        
        health = self.device_health[device_id]
        health.status = status
        health.last_seen = datetime.utcnow()
        
        if battery is not None:
            health.battery_level = battery
        if signal is not None:
            health.signal_strength = signal
    
    def get_device_list(self) -> List[Dict]:
        """Get list of all devices with status"""
        result = []
        for device_id, config in self.devices.items():
            health = self.device_health.get(device_id)
            result.append({
                'device_id': device_id,
                'name': config.name,
                'type': config.device_type,
                'protocol': config.protocol.value,
                'enabled': config.enabled,
                'sensor_count': len(config.sensors),
                'status': health.status.value if health else 'unknown',
                'last_seen': health.last_seen.isoformat() if health and health.last_seen else None,
                'battery': health.battery_level if health else None
            })
        return result
    
    def get_offline_devices(self, threshold_minutes: int = 15) -> List[str]:
        """Get devices that haven't reported recently"""
        cutoff = datetime.utcnow() - timedelta(minutes=threshold_minutes)
        offline = []
        
        for device_id, health in self.device_health.items():
            if health.last_seen is None or health.last_seen < cutoff:
                offline.append(device_id)
        
        return offline


# ============================================
# Construction-Specific Sensor Configurations
# ============================================

class ConstructionSensorPresets:
    """Pre-configured sensor setups for construction sites"""
    
    @staticmethod
    def environmental_monitoring() -> List[SensorConfig]:
        """Environmental monitoring sensors"""
        return [
            SensorConfig(
                sensor_id='ENV_TEMP_001',
                device_id='ENV_STATION_001',
                sensor_type=SensorType.TEMPERATURE,
                name='Site Temperature',
                unit='°C',
                warning_low=0,
                warning_high=35,
                critical_low=-10,
                critical_high=40
            ),
            SensorConfig(
                sensor_id='ENV_HUM_001',
                device_id='ENV_STATION_001',
                sensor_type=SensorType.HUMIDITY,
                name='Site Humidity',
                unit='%',
                warning_low=20,
                warning_high=80,
                critical_low=10,
                critical_high=90
            ),
            SensorConfig(
                sensor_id='ENV_DUST_001',
                device_id='ENV_STATION_001',
                sensor_type=SensorType.DUST,
                name='PM2.5 Dust Level',
                unit='µg/m³',
                warning_high=35,
                critical_high=75
            ),
            SensorConfig(
                sensor_id='ENV_NOISE_001',
                device_id='ENV_STATION_001',
                sensor_type=SensorType.NOISE,
                name='Noise Level',
                unit='dB',
                warning_high=85,
                critical_high=100
            )
        ]
    
    @staticmethod
    def structural_monitoring() -> List[SensorConfig]:
        """Structural health monitoring sensors"""
        return [
            SensorConfig(
                sensor_id='STR_VIB_001',
                device_id='STRUCT_MON_001',
                sensor_type=SensorType.VIBRATION,
                name='Foundation Vibration',
                unit='mm/s',
                warning_high=5.0,
                critical_high=10.0
            ),
            SensorConfig(
                sensor_id='STR_TILT_001',
                device_id='STRUCT_MON_001',
                sensor_type=SensorType.TILT,
                name='Tower Tilt',
                unit='degrees',
                warning_high=0.5,
                critical_high=1.0
            ),
            SensorConfig(
                sensor_id='STR_STRAIN_001',
                device_id='STRUCT_MON_001',
                sensor_type=SensorType.STRAIN,
                name='Beam Strain',
                unit='µε',
                warning_high=1000,
                critical_high=2000
            )
        ]
    
    @staticmethod
    def safety_monitoring() -> List[SensorConfig]:
        """Safety monitoring sensors"""
        return [
            SensorConfig(
                sensor_id='SAF_GAS_001',
                device_id='SAFETY_SYS_001',
                sensor_type=SensorType.GAS,
                name='CO Level',
                unit='ppm',
                warning_high=35,
                critical_high=100
            ),
            SensorConfig(
                sensor_id='SAF_GAS_002',
                device_id='SAFETY_SYS_001',
                sensor_type=SensorType.GAS,
                name='H2S Level',
                unit='ppm',
                warning_high=10,
                critical_high=20
            ),
            SensorConfig(
                sensor_id='SAF_PROX_001',
                device_id='SAFETY_SYS_001',
                sensor_type=SensorType.PROXIMITY,
                name='Equipment Proximity',
                unit='meters',
                warning_low=5,
                critical_low=2
            )
        ]
    
    @staticmethod
    def equipment_monitoring() -> List[SensorConfig]:
        """Equipment monitoring sensors"""
        return [
            SensorConfig(
                sensor_id='EQP_GPS_001',
                device_id='EXCAVATOR_001',
                sensor_type=SensorType.GPS,
                name='Excavator Location',
                unit='coordinates'
            ),
            SensorConfig(
                sensor_id='EQP_FUEL_001',
                device_id='EXCAVATOR_001',
                sensor_type=SensorType.FUEL,
                name='Fuel Level',
                unit='%',
                warning_low=20,
                critical_low=10
            ),
            SensorConfig(
                sensor_id='EQP_VIB_001',
                device_id='EXCAVATOR_001',
                sensor_type=SensorType.VIBRATION,
                name='Engine Vibration',
                unit='mm/s',
                warning_high=15,
                critical_high=25
            )
        ]
    
    @staticmethod
    def concrete_monitoring() -> List[SensorConfig]:
        """Concrete curing monitoring sensors"""
        return [
            SensorConfig(
                sensor_id='CON_TEMP_001',
                device_id='CONCRETE_MON_001',
                sensor_type=SensorType.CONCRETE_CURE,
                name='Concrete Internal Temp',
                unit='°C',
                warning_high=70,
                critical_high=80
            ),
            SensorConfig(
                sensor_id='CON_STR_001',
                device_id='CONCRETE_MON_001',
                sensor_type=SensorType.STRAIN,
                name='Concrete Maturity',
                unit='MPa'
            )
        ]
    
    @staticmethod
    def weather_station() -> List[SensorConfig]:
        """Weather station sensors"""
        return [
            SensorConfig(
                sensor_id='WX_WIND_001',
                device_id='WEATHER_001',
                sensor_type=SensorType.WIND,
                name='Wind Speed',
                unit='m/s',
                warning_high=15,
                critical_high=25
            ),
            SensorConfig(
                sensor_id='WX_RAIN_001',
                device_id='WEATHER_001',
                sensor_type=SensorType.RAINFALL,
                name='Rainfall Rate',
                unit='mm/hr',
                warning_high=10,
                critical_high=25
            ),
            SensorConfig(
                sensor_id='WX_PRES_001',
                device_id='WEATHER_001',
                sensor_type=SensorType.PRESSURE,
                name='Barometric Pressure',
                unit='hPa'
            )
        ]


# ============================================
# IoT Integration System
# ============================================

class IoTIntegrationSystem:
    """
    Main IoT integration system
    
    Provides unified interface for all IoT operations
    """
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.data_processor = DataProcessor()
        self.threshold_monitor = ThresholdMonitor()
        self.alert_callbacks: List[Callable] = []
        
        # Initialize with construction presets
        self._initialize_presets()
    
    def _initialize_presets(self):
        """Initialize with construction-specific configurations"""
        # Register threshold callbacks
        self.threshold_monitor.register_callback(self._on_threshold_alert)
    
    def _on_threshold_alert(self, event: ThresholdEvent):
        """Handle threshold alert"""
        logger.warning(
            f"Threshold alert: {event.sensor_id} = {event.value} "
            f"({event.level.value}, {event.direction} {event.threshold})"
        )
        
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def register_alert_callback(self, callback: Callable[[ThresholdEvent], None]):
        """Register callback for threshold alerts"""
        self.alert_callbacks.append(callback)
    
    def add_device(self, config: DeviceConfig) -> bool:
        """Add an IoT device"""
        return self.device_manager.register_device(config)
    
    def add_sensor(self, config: SensorConfig) -> bool:
        """Add a sensor with threshold configuration"""
        self.device_manager.register_sensor(config)
        self.threshold_monitor.configure_sensor(config)
        return True
    
    def ingest_reading(self, reading: SensorReading):
        """Ingest a sensor reading"""
        # Update device status
        sensor_config = self.device_manager.sensors.get(reading.sensor_id)
        if sensor_config:
            self.device_manager.update_device_status(
                sensor_config.device_id,
                DeviceStatus.ONLINE
            )
        
        # Process data
        self.data_processor.add_reading(reading)
        
        # Check thresholds
        self.threshold_monitor.check_threshold(reading)
    
    def ingest_batch(self, readings: List[Dict]):
        """Ingest batch of readings"""
        for data in readings:
            try:
                reading = SensorReading(
                    sensor_id=data['sensor_id'],
                    sensor_type=SensorType(data['type']),
                    value=float(data['value']),
                    unit=data.get('unit', ''),
                    timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
                    quality=data.get('quality', 1.0),
                    location=data.get('location'),
                    metadata=data.get('metadata', {})
                )
                self.ingest_reading(reading)
            except Exception as e:
                logger.error(f"Failed to ingest reading: {e}")
    
    def get_sensor_data(
        self,
        sensor_id: str,
        window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get comprehensive sensor data"""
        latest = self.data_processor.get_latest(sensor_id)
        stats = self.data_processor.calculate_statistics(sensor_id, window_minutes)
        trend = self.data_processor.get_trend(sensor_id, window_minutes)
        
        config = self.device_manager.sensors.get(sensor_id)
        
        return {
            'sensor_id': sensor_id,
            'name': config.name if config else 'Unknown',
            'type': config.sensor_type.value if config else 'unknown',
            'unit': config.unit if config else '',
            'latest': {
                'value': latest.value if latest else None,
                'timestamp': latest.timestamp.isoformat() if latest else None
            },
            'statistics': stats,
            'trend': trend,
            'thresholds': {
                'warning_low': config.warning_low if config else None,
                'warning_high': config.warning_high if config else None,
                'critical_low': config.critical_low if config else None,
                'critical_high': config.critical_high if config else None
            } if config else {}
        }
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status and sensor readings"""
        device = self.device_manager.devices.get(device_id)
        health = self.device_manager.device_health.get(device_id)
        
        if not device:
            return {'error': 'Device not found'}
        
        sensors_data = []
        for sensor_id in device.sensors:
            sensors_data.append(self.get_sensor_data(sensor_id, 60))
        
        return {
            'device_id': device_id,
            'name': device.name,
            'type': device.device_type,
            'status': health.status.value if health else 'unknown',
            'battery': health.battery_level if health else None,
            'signal': health.signal_strength if health else None,
            'last_seen': health.last_seen.isoformat() if health and health.last_seen else None,
            'sensors': sensors_data
        }
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active threshold alerts"""
        alerts = self.threshold_monitor.get_active_alerts()
        return [
            {
                'sensor_id': a.sensor_id,
                'type': a.sensor_type.value,
                'level': a.level.value,
                'value': a.value,
                'threshold': a.threshold,
                'direction': a.direction,
                'timestamp': a.timestamp.isoformat(),
                'duration_seconds': a.duration_seconds
            }
            for a in alerts
        ]
    
    def get_site_overview(self) -> Dict[str, Any]:
        """Get overview of all site IoT data"""
        devices = self.device_manager.get_device_list()
        offline = self.device_manager.get_offline_devices()
        alerts = self.get_active_alerts()
        
        # Aggregate environmental data
        env_data = {}
        for sensor_type in [SensorType.TEMPERATURE, SensorType.HUMIDITY, 
                           SensorType.DUST, SensorType.NOISE]:
            for sensor_id, config in self.device_manager.sensors.items():
                if config.sensor_type == sensor_type:
                    latest = self.data_processor.get_latest(sensor_id)
                    if latest:
                        env_data[sensor_type.value] = {
                            'value': latest.value,
                            'unit': config.unit,
                            'sensor_name': config.name
                        }
                    break
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_devices': len(devices),
                'online_devices': len([d for d in devices if d['status'] == 'online']),
                'offline_devices': len(offline),
                'total_sensors': len(self.device_manager.sensors),
                'active_alerts': len(alerts)
            },
            'environmental': env_data,
            'alerts': alerts[:10],  # Top 10 alerts
            'offline_devices': offline
        }
    
    def configure_presets(self, preset_type: str) -> int:
        """Configure sensors from presets"""
        presets = {
            'environmental': ConstructionSensorPresets.environmental_monitoring,
            'structural': ConstructionSensorPresets.structural_monitoring,
            'safety': ConstructionSensorPresets.safety_monitoring,
            'equipment': ConstructionSensorPresets.equipment_monitoring,
            'concrete': ConstructionSensorPresets.concrete_monitoring,
            'weather': ConstructionSensorPresets.weather_station
        }
        
        if preset_type not in presets:
            return 0
        
        configs = presets[preset_type]()
        count = 0
        for config in configs:
            if self.add_sensor(config):
                count += 1
        
        return count


# Convenience instance
iot_system = IoTIntegrationSystem()