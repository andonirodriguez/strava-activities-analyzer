import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración por defecto
DEFAULT_CONFIG = {
    'auth_url': 'https://www.strava.com/oauth/authorize',
    'token_url': 'https://www.strava.com/oauth/token',
    'api_url': 'https://www.strava.com/api/v3'
}

# Configuración específica de Strava
STRAVA_CONFIG = {
    'client_id': os.getenv('STRAVA_CLIENT_ID'),
    'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
    'redirect_uri': 'http://localhost:8000/callback',
    'scope': 'read,activity:read,activity:read_all'
}

def validate_config():
    """Valida que las variables de entorno necesarias estén configuradas"""
    if not STRAVA_CONFIG['client_id'] or not STRAVA_CONFIG['client_secret']:
        raise Exception(
            "Error: Las variables de entorno STRAVA_CLIENT_ID y STRAVA_CLIENT_SECRET "
            "deben estar configuradas en el archivo .env"
        ) 