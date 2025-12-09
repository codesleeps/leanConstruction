"""
Test fixtures package for construction ML modules

Phase 2 fixtures:
- Project data, progress tracking, waste analysis
- Forecast data, safety data
- Historical time series data

Phase 3 fixtures:
- Lean tools data (VSM, 5S, Kaizen, Kanban)
- NLP sample documents
- Resource optimization data
- Alerting system data
- ERP integration data
- IoT sensor data
"""

from .sample_data import (
    # Phase 2 fixtures
    generate_sample_project_data,
    generate_progress_data,
    generate_waste_data,
    generate_forecast_data,
    generate_safety_data,
    generate_workplace_organization_data,
    generate_historical_data,
    generate_batch_project_data,
    SAMPLE_PROJECT,
    SAMPLE_PROJECTS,
    
    # Phase 3 fixtures
    generate_lean_tools_data,
    generate_nlp_sample_documents,
    generate_resource_optimization_data,
    generate_alerting_data,
    generate_erp_integration_data,
    generate_iot_sensor_data,
    SAMPLE_LEAN_TOOLS_DATA,
    SAMPLE_NLP_DOCUMENTS,
    SAMPLE_RESOURCE_DATA,
    SAMPLE_ALERTING_DATA,
    SAMPLE_ERP_DATA,
    SAMPLE_IOT_DATA
)

__all__ = [
    # Phase 2 exports
    'generate_sample_project_data',
    'generate_progress_data',
    'generate_waste_data',
    'generate_forecast_data',
    'generate_safety_data',
    'generate_workplace_organization_data',
    'generate_historical_data',
    'generate_batch_project_data',
    'SAMPLE_PROJECT',
    'SAMPLE_PROJECTS',
    
    # Phase 3 exports
    'generate_lean_tools_data',
    'generate_nlp_sample_documents',
    'generate_resource_optimization_data',
    'generate_alerting_data',
    'generate_erp_integration_data',
    'generate_iot_sensor_data',
    'SAMPLE_LEAN_TOOLS_DATA',
    'SAMPLE_NLP_DOCUMENTS',
    'SAMPLE_RESOURCE_DATA',
    'SAMPLE_ALERTING_DATA',
    'SAMPLE_ERP_DATA',
    'SAMPLE_IOT_DATA'
]