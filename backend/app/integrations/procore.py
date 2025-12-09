"""
Procore API Integration
Handles data synchronization with Procore project management platform
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProcoreClient:
    """Client for Procore API integration"""
    
    BASE_URL = "https://api.procore.com"
    API_VERSION = "v1.0"
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.session = requests.Session()
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
    
    def authenticate(self, redirect_uri: str, code: str) -> Dict:
        """
        Exchange authorization code for access token
        OAuth 2.0 flow
        """
        url = f"{self.BASE_URL}/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            return token_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def get_projects(self, company_id: int) -> List[Dict]:
        """
        Fetch all projects for a company
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects"
        params = {'company_id': company_id}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch projects: {str(e)}")
            return []
    
    def get_project_details(self, project_id: int) -> Dict:
        """
        Get detailed information about a specific project
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch project details: {str(e)}")
            return {}
    
    def get_schedule_activities(self, project_id: int) -> List[Dict]:
        """
        Fetch schedule activities (tasks) for a project
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}/schedule/activities"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch schedule activities: {str(e)}")
            return []
    
    def get_daily_logs(self, project_id: int, date: Optional[str] = None) -> List[Dict]:
        """
        Fetch daily construction logs
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}/daily_logs"
        params = {}
        
        if date:
            params['date'] = date
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch daily logs: {str(e)}")
            return []
    
    def get_rfis(self, project_id: int) -> List[Dict]:
        """
        Fetch Requests for Information (RFIs)
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}/rfis"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch RFIs: {str(e)}")
            return []
    
    def get_submittals(self, project_id: int) -> List[Dict]:
        """
        Fetch project submittals
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}/submittals"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch submittals: {str(e)}")
            return []
    
    def get_change_orders(self, project_id: int) -> List[Dict]:
        """
        Fetch change orders
        """
        url = f"{self.BASE_URL}/rest/{self.API_VERSION}/projects/{project_id}/change_orders"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch change orders: {str(e)}")
            return []
    
    def sync_project_data(self, project_id: int) -> Dict:
        """
        Comprehensive sync of all project data
        Returns aggregated data for analysis
        """
        logger.info(f"Starting full sync for Procore project {project_id}")
        
        sync_data = {
            'project_id': project_id,
            'sync_timestamp': datetime.utcnow().isoformat(),
            'project_details': self.get_project_details(project_id),
            'schedule_activities': self.get_schedule_activities(project_id),
            'daily_logs': self.get_daily_logs(project_id),
            'rfis': self.get_rfis(project_id),
            'submittals': self.get_submittals(project_id),
            'change_orders': self.get_change_orders(project_id)
        }
        
        logger.info(f"Sync completed for project {project_id}")
        return sync_data


def analyze_procore_data_for_waste(sync_data: Dict) -> Dict:
    """
    Analyze Procore data to identify potential waste (DOWNTIME)
    """
    waste_indicators = {
        'defects': [],
        'overproduction': [],
        'waiting': [],
        'non_utilized_talent': [],
        'transportation': [],
        'inventory': [],
        'motion': [],
        'extra_processing': []
    }
    
    # Analyze RFIs for waiting waste
    rfis = sync_data.get('rfis', [])
    open_rfis = [rfi for rfi in rfis if rfi.get('status') == 'open']
    if len(open_rfis) > 5:
        waste_indicators['waiting'].append({
            'type': 'excessive_rfis',
            'count': len(open_rfis),
            'description': f'{len(open_rfis)} open RFIs causing potential delays'
        })
    
    # Analyze change orders for defects/extra processing
    change_orders = sync_data.get('change_orders', [])
    if len(change_orders) > 10:
        waste_indicators['defects'].append({
            'type': 'excessive_changes',
            'count': len(change_orders),
            'description': f'{len(change_orders)} change orders indicate design/planning issues'
        })
    
    # Analyze schedule activities for delays
    activities = sync_data.get('schedule_activities', [])
    delayed_activities = [act for act in activities if act.get('status') == 'behind_schedule']
    if delayed_activities:
        waste_indicators['waiting'].append({
            'type': 'schedule_delays',
            'count': len(delayed_activities),
            'description': f'{len(delayed_activities)} activities behind schedule'
        })
    
    return {
        'project_id': sync_data.get('project_id'),
        'analysis_timestamp': datetime.utcnow().isoformat(),
        'waste_indicators': waste_indicators,
        'total_waste_types_detected': sum(1 for indicators in waste_indicators.values() if indicators)
    }
