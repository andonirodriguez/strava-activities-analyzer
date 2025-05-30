import requests
import logging
from config import STRAVA_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StravaClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = STRAVA_CONFIG['api_url']
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }
        logger.info("Cliente de Strava inicializado")

    def get_activities(self, per_page=30):
        """Obtiene las actividades de Strava"""
        try:
            logger.info(f"Obteniendo actividades (per_page={per_page})...")
            url = f"{self.base_url}/athlete/activities"
            params = {'per_page': per_page}
            
            response = requests.get(url, headers=self.headers, params=params)
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