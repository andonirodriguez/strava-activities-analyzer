import requests
import logging
from strava_auth import StravaAuth
from config import DEFAULT_CONFIG, STRAVA_API_URL

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StravaClient:
    def __init__(self):
        self.auth = StravaAuth()
        self.base_url = DEFAULT_CONFIG['api_url']
        logger.info("Cliente de Strava inicializado")

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

    def get_activities(self, per_page=30):
        """Obtiene las actividades de Strava"""
        try:
            logger.info(f"Obteniendo actividades (per_page={per_page})...")
            url = f"{self.base_url}/athlete/activities"
            params = {'per_page': per_page}
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            activities = response.json()
            logger.info(f"Se obtuvieron {len(activities)} actividades")
            return activities
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a Strava: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Respuesta del servidor: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return None 