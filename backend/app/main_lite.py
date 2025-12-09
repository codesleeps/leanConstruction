"""
Lean Construction AI API - Lite Version
For demo/testing without heavy ML dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

app = FastAPI(
    title="Lean Construction AI API",
    description="AI-powered construction analytics platform - Lite Version for Demo",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Health & Status Endpoints
# ============================================

@app.get("/")
async def root():
    return {
        "name": "Lean Construction AI API",
        "version": "4.0.0",
        "status": "running",
        "phase": "Phase 4 Complete - Production Ready",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0",
        "modules": {
            "computer_vision": "available",
            "waste_detection": "available",
            "forecasting": "available",
            "reporting": "available",
            "lean_tools": "available",
            "nlp_analysis": "available",
            "resource_optimization": "available",
            "alerting": "available",
            "model_finetuning": "available",
            "analytics_bi": "available",
            "industry_customizations": "available",
            "infrastructure": "available",
            "commercial": "available"
        }
    }

@app.get("/api/v1/ml/health")
async def ml_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0",
        "phase": "Phase 4 - Production Ready"
    }

# ============================================
# Phase 2 - Waste Detection Demo
# ============================================

class WasteAnalysisRequest(BaseModel):
    project_id: str
    data: Dict[str, Any]
    include_recommendations: bool = True

@app.post("/api/v1/ml/analyze-waste")
async def analyze_waste(request: WasteAnalysisRequest):
    """Demo: Analyze project for lean wastes (DOWNTIME framework)"""
    return {
        "status": "success",
        "project_id": request.project_id,
        "analysis": {
            "total_waste_score": 0.35,
            "wastes": {
                "defects": {"score": 0.12, "impact_cost": 15000},
                "overproduction": {"score": 0.08, "impact_cost": 5000},
                "waiting": {"score": 0.25, "impact_cost": 45000},
                "non_utilized_talent": {"score": 0.15, "impact_cost": 12000},
                "transportation": {"score": 0.10, "impact_cost": 8000},
                "inventory": {"score": 0.18, "impact_cost": 22000},
                "motion": {"score": 0.05, "impact_cost": 3000},
                "extra_processing": {"score": 0.07, "impact_cost": 6000}
            },
            "total_impact_cost": 116000,
            "priority_actions": [
                "Reduce waiting time for material deliveries",
                "Review inventory levels and implement JIT",
                "Address quality defects in concrete work"
            ] if request.include_recommendations else []
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/ml/waste-types")
async def get_waste_types():
    """Get DOWNTIME waste types"""
    return {
        "framework": "DOWNTIME",
        "wastes": [
            {"code": "D", "name": "Defects", "description": "Quality issues requiring rework"},
            {"code": "O", "name": "Overproduction", "description": "Producing more than needed"},
            {"code": "W", "name": "Waiting", "description": "Idle time waiting for resources"},
            {"code": "N", "name": "Non-utilized Talent", "description": "Underutilizing worker skills"},
            {"code": "T", "name": "Transportation", "description": "Unnecessary material movement"},
            {"code": "I", "name": "Inventory", "description": "Excess materials on site"},
            {"code": "M", "name": "Motion", "description": "Unnecessary worker movement"},
            {"code": "E", "name": "Extra Processing", "description": "Over-engineering work"}
        ]
    }

# ============================================
# Phase 2 - Forecasting Demo
# ============================================

class ForecastRequest(BaseModel):
    project_id: str
    project_info: Dict[str, Any]

@app.post("/api/v1/ml/forecast")
async def generate_forecast(request: ForecastRequest):
    """Demo: Generate schedule and cost forecasts"""
    return {
        "status": "success",
        "project_id": request.project_id,
        "forecast": {
            "schedule": {
                "predicted_completion": "2024-06-15",
                "confidence_interval": ["2024-05-28", "2024-07-02"],
                "delay_probability": 0.23,
                "risk_level": "MEDIUM"
            },
            "cost": {
                "predicted_final_cost": 2450000,
                "budget_variance": 150000,
                "cost_at_completion": 2450000,
                "estimate_to_complete": 850000,
                "risk_level": "LOW"
            },
            "recommendations": [
                "Monitor critical path activities closely",
                "Consider overtime for MEP installation",
                "Review subcontractor schedules"
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================
# Phase 3 - Lean Tools Demo
# ============================================

@app.get("/api/v1/ml/lean/metrics")
async def get_lean_metrics():
    """Demo: Get lean metrics summary"""
    return {
        "status": "success",
        "metrics": {
            "vsm_efficiency": 0.67,
            "5s_score": 78.5,
            "kaizen_events_active": 3,
            "kanban_wip_compliance": 0.92,
            "overall_lean_index": 0.74
        }
    }

# ============================================
# Phase 4 - Analytics & BI Demo
# ============================================

@app.get("/api/v1/ml/analytics/kpis/{project_id}")
async def get_project_kpis(project_id: str):
    """Demo: Get project KPIs"""
    return {
        "status": "success",
        "project_id": project_id,
        "kpis": {
            "schedule": {
                "spi": 0.95,
                "schedule_variance": -5,
                "critical_path_compliance": 0.88
            },
            "cost": {
                "cpi": 1.02,
                "budget_variance_percent": 2.1,
                "earned_value": 1850000
            },
            "quality": {
                "defect_rate": 2.3,
                "rework_percentage": 3.5,
                "first_time_quality": 0.94
            },
            "safety": {
                "incident_rate": 0.8,
                "near_miss_reports": 12,
                "safety_compliance": 0.97
            },
            "productivity": {
                "labor_productivity": 0.91,
                "equipment_utilization": 0.78,
                "ppc_weekly": 0.82
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/ml/analytics/executive-summary/{project_id}")
async def get_executive_summary(project_id: str):
    """Demo: Get executive decision support summary"""
    return {
        "status": "success",
        "project_id": project_id,
        "summary": {
            "overall_health": "GOOD",
            "health_score": 82,
            "key_insights": [
                "Project is tracking 5% ahead of schedule",
                "Cost performance remains within budget",
                "Quality metrics show improvement trend",
                "Resource utilization can be optimized"
            ],
            "risk_factors": [
                {"risk": "Material delivery delays", "probability": 0.3, "impact": "MEDIUM"},
                {"risk": "Weather impact on exterior work", "probability": 0.4, "impact": "LOW"}
            ],
            "recommendations": [
                "Accelerate foundation pour to maintain buffer",
                "Review electrical subcontractor progress",
                "Implement additional safety measures for elevated work"
            ]
        }
    }

# ============================================
# Phase 4 - Industry Customizations Demo
# ============================================

@app.get("/api/v1/ml/industry/sectors")
async def get_industry_sectors():
    """Get available industry sectors"""
    return {
        "status": "success",
        "sectors": [
            {"id": "commercial", "name": "Commercial Construction"},
            {"id": "residential", "name": "Residential Construction"},
            {"id": "industrial", "name": "Industrial Construction"},
            {"id": "healthcare", "name": "Healthcare Construction"},
            {"id": "education", "name": "Educational Facilities"},
            {"id": "infrastructure", "name": "Infrastructure Projects"},
            {"id": "data_center", "name": "Data Center Construction"},
            {"id": "hospitality", "name": "Hospitality Construction"},
            {"id": "retail", "name": "Retail Construction"},
            {"id": "mixed_use", "name": "Mixed-Use Development"}
        ]
    }

@app.get("/api/v1/ml/industry/profile/{sector}")
async def get_industry_profile(sector: str):
    """Demo: Get industry profile"""
    profiles = {
        "healthcare": {
            "typical_phases": ["Pre-design", "Design", "Permitting", "Site Work", "Foundation", "Structure", "MEP", "Interior", "Commissioning"],
            "critical_compliance": ["HIPAA", "Joint Commission", "ADA"],
            "safety_factors": ["Infection control", "Patient safety", "Air quality"],
            "kpi_priorities": ["ICRA compliance", "Noise control", "Schedule adherence"]
        },
        "commercial": {
            "typical_phases": ["Pre-construction", "Demolition", "Foundation", "Structure", "Envelope", "MEP", "Finishes", "Occupancy"],
            "critical_compliance": ["ADA", "Fire codes", "LEED"],
            "safety_factors": ["Fall protection", "Electrical safety", "Fire prevention"],
            "kpi_priorities": ["Cost control", "Schedule", "Quality"]
        }
    }
    return {
        "status": "success",
        "sector": sector,
        "profile": profiles.get(sector, profiles["commercial"])
    }

# ============================================
# Phase 4 - Infrastructure Demo
# ============================================

@app.get("/api/v1/ml/infrastructure/status")
async def get_infrastructure_status():
    """Demo: Get infrastructure status"""
    return {
        "status": "success",
        "infrastructure": {
            "services": [
                {"id": "api-service", "name": "API Service", "instances": 3, "health": "healthy"},
                {"id": "ml-inference", "name": "ML Inference", "instances": 2, "health": "healthy"},
                {"id": "celery-worker", "name": "Background Workers", "instances": 4, "health": "healthy"}
            ],
            "databases": {
                "primary": {"type": "PostgreSQL", "status": "connected", "pool_size": 20},
                "cache": {"type": "Redis", "status": "connected", "cluster_nodes": 3}
            },
            "scaling_policies_active": 4,
            "alerts_active": 0
        }
    }

# ============================================
# Phase 4 - Commercial Demo
# ============================================

@app.get("/api/v1/ml/commercial/tiers")
async def get_subscription_tiers():
    """Demo: Get subscription tiers"""
    return {
        "status": "success",
        "tiers": [
            {
                "id": "free",
                "name": "Free",
                "price_monthly": 0,
                "projects": 1,
                "users": 2,
                "features": ["Basic waste detection", "Simple reporting"]
            },
            {
                "id": "starter",
                "name": "Starter",
                "price_monthly": 99,
                "projects": 5,
                "users": 10,
                "features": ["Full waste detection", "Forecasting", "Basic lean tools"]
            },
            {
                "id": "professional",
                "name": "Professional",
                "price_monthly": 299,
                "projects": 25,
                "users": 50,
                "features": ["All features", "NLP analysis", "Resource optimization", "Priority support"]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_monthly": "Custom",
                "projects": "Unlimited",
                "users": "Unlimited",
                "features": ["All features", "Custom integrations", "Dedicated support", "SLA guarantee", "White-label"]
            }
        ]
    }

# ============================================
# Model Info
# ============================================

@app.get("/api/v1/ml/models/info")
async def get_models_info():
    """Get information about ML models"""
    return {
        "models": {
            "progress_monitoring": {
                "architecture": "ResNet-50 with CBAM attention",
                "status": "ready"
            },
            "waste_detection": {
                "framework": "DOWNTIME",
                "methods": ["IsolationForest", "Statistical analysis", "Rule-based"],
                "status": "ready"
            },
            "schedule_forecasting": {
                "architecture": "Bidirectional LSTM with attention",
                "status": "ready"
            },
            "cost_forecasting": {
                "architecture": "Stacking ensemble (RF, GBM, Ridge, ElasticNet)",
                "status": "ready"
            },
            "nlp_analysis": {
                "architecture": "BERT-based transformers",
                "status": "ready"
            }
        },
        "phase": "Phase 4 Production Ready",
        "version": "4.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)