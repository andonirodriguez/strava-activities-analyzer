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

    def get_activities(self, per_page=200):
        """Obtiene todas las actividades de Strava usando paginación"""
        try:
            logger.info("Iniciando obtención de actividades...")
            url = f"{self.base_url}/athlete/activities"
            all_activities = []
            page = 1
            
            while True:
                logger.info(f"Obteniendo página {page} de actividades...")
                params = {
                    'per_page': per_page,
                    'page': page
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                activities = response.json()
                if not activities:  # Si no hay más actividades, terminar
                    break
                    
                all_activities.extend(activities)
                logger.info(f"Se obtuvieron {len(activities)} actividades en la página {page}")
                
                if len(activities) < per_page:  # Si hay menos actividades que el máximo por página, es la última
                    break
                    
                page += 1
            
            logger.info(f"Total de actividades obtenidas: {len(all_activities)}")
            return all_activities
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a Strava: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Respuesta del servidor: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return None 