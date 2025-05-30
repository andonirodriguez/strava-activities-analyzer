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

# Configuración de Strava
STRAVA_CONFIG = {
    'client_id': st.secrets["strava"]["client_id"],
    'client_secret': st.secrets["strava"]["client_secret"],
    'auth_url': 'https://www.strava.com/oauth/authorize',
    'token_url': 'https://www.strava.com/oauth/token',
    'api_url': 'https://www.strava.com/api/v3',
    'redirect_uri': st.secrets["strava"]["redirect_uri"],
    'scope': 'read,activity:read'
}

# Configuración de la aplicación
APP_CONFIG = {
    'data_file': 'strava_activities.json',
    'tokens_file': 'strava_tokens.json',
    'update_interval': 86400  # 24 horas en segundos
}

def validate_config():
    """Valida que las variables de entorno necesarias estén configuradas"""
    if not STRAVA_CONFIG['client_id'] or not STRAVA_CONFIG['client_secret']:
        raise Exception(
            "Error: Las credenciales de Strava no están configuradas. "
            "En local, configura STRAVA_CLIENT_ID y STRAVA_CLIENT_SECRET en el archivo .env. "
            "En Streamlit, configura las credenciales en los secrets."
        ) 