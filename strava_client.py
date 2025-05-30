import requests
from strava_auth import StravaAuth
from config import DEFAULT_CONFIG

class StravaClient:
    def __init__(self):
        self.auth = StravaAuth()
        self.base_url = DEFAULT_CONFIG['api_url']

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.auth.get_valid_token()}'
        }

    def get_all_activities(self, per_page=30):
        """Obtiene todas las actividades del usuario"""
        activities = []
        page = 1
        
        while True:
            response = requests.get(
                f"{self.base_url}/athlete/activities",
                headers=self._get_headers(),
                params={'per_page': per_page, 'page': page}
            )
            
            if response.status_code != 200:
                raise Exception(f"Error al obtener actividades: {response.text}")
            
            page_activities = response.json()
            if not page_activities:
                break
                
            activities.extend(page_activities)
            page += 1
            
        return activities 