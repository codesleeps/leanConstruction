from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..celery_app import celery_app
from ..database import SessionLocal
from ..models import Project, Task as TaskModel, WasteLog
import logging

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def morning_project_health_check(self):
    """
    Morning health check for all active projects
    Analyzes overnight data and generates status reports
    """
    logger.info("Starting morning project health check")
    db = self.db
    
    try:
        active_projects = db.query(Project).filter(Project.status == "active").all()
        
        results = []
        for project in active_projects:
            # Calculate project metrics
            total_tasks = db.query(TaskModel).filter(TaskModel.project_id == project.id).count()
            completed_tasks = db.query(TaskModel).filter(
                TaskModel.project_id == project.id,
                TaskModel.status == "completed"
            ).count()
            
            # Check for recent waste logs
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_waste = db.query(WasteLog).filter(
                WasteLog.project_id == project.id,
                WasteLog.detected_at >= yesterday
            ).all()
            
            total_waste_cost = sum(w.impact_cost for w in recent_waste)
            total_waste_time = sum(w.impact_time for w in recent_waste)
            
            health_status = {
                'project_id': project.id,
                'project_name': project.name,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                'waste_incidents_24h': len(recent_waste),
                'waste_cost_24h': total_waste_cost,
                'waste_time_24h': total_waste_time,
                'status': 'healthy' if total_waste_cost < 1000 else 'attention_needed'
            }
            
            results.append(health_status)
            logger.info(f"Health check completed for project {project.name}")
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'projects_checked': len(results),
            'results': results
        }
    
    except Exception as e:
        logger.error(f"Error in morning health check: {str(e)}")
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def detect_waste_patterns(self):
    """
    Continuous waste detection across all projects
    Identifies patterns in the 8 wastes (DOWNTIME)
    """
    logger.info("Starting waste pattern detection")
    db = self.db
    
    try:
        active_projects = db.query(Project).filter(Project.status == "active").all()
        
        waste_types = ['defects', 'overproduction', 'waiting', 'non_utilized_talent',
                      'transportation', 'inventory', 'motion', 'extra_processing']
        
        results = []
        for project in active_projects:
            # Analyze waste patterns for last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            waste_logs = db.query(WasteLog).filter(
                WasteLog.project_id == project.id,
                WasteLog.detected_at >= week_ago
            ).all()
            
            # Group by waste type
            waste_summary = {}
            for waste_type in waste_types:
                type_logs = [w for w in waste_logs if w.waste_type == waste_type]
                waste_summary[waste_type] = {
                    'count': len(type_logs),
                    'total_cost': sum(w.impact_cost for w in type_logs),
                    'total_time': sum(w.impact_time for w in type_logs)
                }
            
            # Identify top waste areas
            top_waste = max(waste_summary.items(), key=lambda x: x[1]['total_cost']) if waste_summary else None
            
            results.append({
                'project_id': project.id,
                'project_name': project.name,
                'waste_summary': waste_summary,
                'top_waste_type': top_waste[0] if top_waste else None,
                'recommendation': f"Focus on reducing {top_waste[0]} waste" if top_waste else "No significant waste detected"
            })
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'projects_analyzed': len(results),
            'results': results
        }
    
    except Exception as e:
        logger.error(f"Error in waste detection: {str(e)}")
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def update_project_progress(self):
    """
    Update project progress metrics
    Tracks completion rates and identifies bottlenecks
    """
    logger.info("Updating project progress")
    db = self.db
    
    try:
        active_projects = db.query(Project).filter(Project.status == "active").all()
        
        results = []
        for project in active_projects:
            tasks = db.query(TaskModel).filter(TaskModel.project_id == project.id).all()
            
            if not tasks:
                continue
            
            total_tasks = len(tasks)
            completed = len([t for t in tasks if t.status == "completed"])
            in_progress = len([t for t in tasks if t.status == "in_progress"])
            pending = len([t for t in tasks if t.status == "pending"])
            
            # Calculate estimated vs actual hours
            total_estimated = sum(t.estimated_hours or 0 for t in tasks)
            total_actual = sum(t.actual_hours or 0 for t in tasks if t.actual_hours)
            
            # Identify overdue tasks (simplified - would need due dates in model)
            high_priority_pending = len([t for t in tasks if t.priority == "high" and t.status == "pending"])
            
            progress_data = {
                'project_id': project.id,
                'project_name': project.name,
                'total_tasks': total_tasks,
                'completed': completed,
                'in_progress': in_progress,
                'pending': pending,
                'completion_percentage': (completed / total_tasks * 100) if total_tasks > 0 else 0,
                'estimated_hours': total_estimated,
                'actual_hours': total_actual,
                'hour_variance': total_actual - total_estimated if total_actual else 0,
                'high_priority_pending': high_priority_pending,
                'bottleneck_alert': high_priority_pending > 5
            }
            
            results.append(progress_data)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'projects_updated': len(results),
            'results': results
        }
    
    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def ingest_external_data(self, source: str, project_id: int, data: dict):
    """
    Generic task for ingesting data from external sources
    (Project management tools, IoT sensors, etc.)
    """
    logger.info(f"Ingesting data from {source} for project {project_id}")
    db = self.db
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Process based on source type
        if source == "procore":
            return process_procore_data(db, project_id, data)
        elif source == "primavera":
            return process_primavera_data(db, project_id, data)
        elif source == "iot_sensor":
            return process_iot_data(db, project_id, data)
        else:
            logger.warning(f"Unknown data source: {source}")
            return {'status': 'unknown_source', 'source': source}
    
    except Exception as e:
        logger.error(f"Error ingesting data: {str(e)}")
        raise


def process_procore_data(db: Session, project_id: int, data: dict):
    """Process data from Procore API"""
    # Placeholder for Procore integration
    logger.info(f"Processing Procore data for project {project_id}")
    return {'status': 'processed', 'source': 'procore', 'records': len(data.get('items', []))}


def process_primavera_data(db: Session, project_id: int, data: dict):
    """Process data from Primavera P6"""
    # Placeholder for Primavera integration
    logger.info(f"Processing Primavera data for project {project_id}")
    return {'status': 'processed', 'source': 'primavera', 'records': len(data.get('activities', []))}


def process_iot_data(db: Session, project_id: int, data: dict):
    """Process IoT sensor data"""
    # Placeholder for IoT data processing
    logger.info(f"Processing IoT data for project {project_id}")
    return {'status': 'processed', 'source': 'iot_sensor', 'sensors': len(data.get('sensors', []))}
