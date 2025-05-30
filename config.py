import os
from dotenv import load_dotenv
import streamlit as st

# Cargar variables de entorno desde .env (solo para desarrollo local)
load_dotenv()

def get_strava_credentials():
    """Obtiene las credenciales de Strava según el entorno"""
    try:
        # Primero intentamos obtener las credenciales de Streamlit
        client_id = st.secrets["strava"]["client_id"]
        client_secret = st.secrets["strava"]["client_secret"]
        print("Usando credenciales de Streamlit")
    except Exception:
        # Si no están disponibles, usamos las variables de entorno
        client_id = os.getenv('STRAVA_CLIENT_ID')
        client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        print("Usando credenciales locales")
    
    return client_id, client_secret

# Configuración de la API de Strava
STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET = get_strava_credentials()
STRAVA_REDIRECT_URI = 'http://localhost:8000/callback'
STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'
STRAVA_API_URL = 'https://www.strava.com/api/v3'
STRAVA_SCOPE = 'read,activity:read,activity:read_all'

# Configuración del servidor
PORT = 8000

# Configuración específica de Strava
STRAVA_CONFIG = {
    'client_id': STRAVA_CLIENT_ID,
    'client_secret': STRAVA_CLIENT_SECRET,
    'redirect_uri': STRAVA_REDIRECT_URI,
    'auth_url': STRAVA_AUTH_URL,
    'token_url': STRAVA_TOKEN_URL,
    'api_url': STRAVA_API_URL,
    'scope': STRAVA_SCOPE
}

def validate_config():
    """Valida que las variables de entorno necesarias estén configuradas"""
    if not STRAVA_CONFIG['client_id'] or not STRAVA_CONFIG['client_secret']:
        raise Exception(
            "Error: Las credenciales de Strava no están configuradas. "
            "En local, configura STRAVA_CLIENT_ID y STRAVA_CLIENT_SECRET en el archivo .env. "
            "En Streamlit, configura las credenciales en los secrets."
        ) 