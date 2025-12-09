from celery import Task
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
def weekly_strategic_analysis(self):
    """
    Weekly strategic analysis for all projects
    Generates comprehensive reports and recommendations
    """
    logger.info("Starting weekly strategic analysis")
    db = self.db
    
    try:
        active_projects = db.query(Project).filter(Project.status == "active").all()
        
        results = []
        for project in active_projects:
            # Get data for the past week
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            # Task analysis
            tasks = db.query(TaskModel).filter(TaskModel.project_id == project.id).all()
            completed_this_week = db.query(TaskModel).filter(
                TaskModel.project_id == project.id,
                TaskModel.status == "completed",
                TaskModel.updated_at >= week_ago
            ).count()
            
            # Waste analysis
            waste_logs = db.query(WasteLog).filter(
                WasteLog.project_id == project.id,
                WasteLog.detected_at >= week_ago
            ).all()
            
            total_waste_cost = sum(w.impact_cost for w in waste_logs)
            total_waste_time = sum(w.impact_time for w in waste_logs)
            
            # Calculate trends
            previous_week = datetime.utcnow() - timedelta(days=14)
            previous_waste = db.query(WasteLog).filter(
                WasteLog.project_id == project.id,
                WasteLog.detected_at >= previous_week,
                WasteLog.detected_at < week_ago
            ).all()
            
            previous_waste_cost = sum(w.impact_cost for w in previous_waste)
            waste_trend = ((total_waste_cost - previous_waste_cost) / previous_waste_cost * 100) if previous_waste_cost > 0 else 0
            
            # Generate recommendations
            recommendations = []
            if waste_trend > 10:
                recommendations.append("Waste increasing - implement immediate corrective actions")
            if total_waste_time > 100:
                recommendations.append("High time waste detected - review workflow efficiency")
            if completed_this_week < len(tasks) * 0.1:
                recommendations.append("Low completion rate - check for bottlenecks")
            
            analysis = {
                'project_id': project.id,
                'project_name': project.name,
                'week_ending': datetime.utcnow().isoformat(),
                'tasks_completed': completed_this_week,
                'total_tasks': len(tasks),
                'waste_incidents': len(waste_logs),
                'waste_cost': total_waste_cost,
                'waste_time_hours': total_waste_time,
                'waste_trend_percentage': waste_trend,
                'recommendations': recommendations,
                'overall_health': 'good' if waste_trend < 0 and completed_this_week > 0 else 'needs_attention'
            }
            
            results.append(analysis)
            logger.info(f"Weekly analysis completed for project {project.name}")
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'projects_analyzed': len(results),
            'results': results
        }
    
    except Exception as e:
        logger.error(f"Error in weekly analysis: {str(e)}")
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def generate_value_stream_map(self, project_id: int):
    """
    Generate value stream mapping for a project
    Identifies value-added vs non-value-added activities
    """
    logger.info(f"Generating value stream map for project {project_id}")
    db = self.db
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        tasks = db.query(TaskModel).filter(TaskModel.project_id == project_id).all()
        
        # Analyze task flow
        value_added_time = 0
        non_value_added_time = 0
        
        for task in tasks:
            if task.actual_hours:
                # Simple heuristic - tasks with waste logs are non-value-added
                waste_count = db.query(WasteLog).filter(
                    WasteLog.project_id == project_id,
                    WasteLog.description.contains(task.name)
                ).count()
                
                if waste_count > 0:
                    non_value_added_time += task.actual_hours
                else:
                    value_added_time += task.actual_hours
        
        total_time = value_added_time + non_value_added_time
        efficiency = (value_added_time / total_time * 100) if total_time > 0 else 0
        
        return {
            'project_id': project_id,
            'project_name': project.name,
            'value_added_hours': value_added_time,
            'non_value_added_hours': non_value_added_time,
            'total_hours': total_time,
            'efficiency_percentage': efficiency,
            'improvement_potential': 100 - efficiency,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating value stream map: {str(e)}")
        raise
