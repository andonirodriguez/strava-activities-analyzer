import json
import os
import logging
import time
import requests
import threading
import webbrowser
from flask import Flask, request
from config import STRAVA_CONFIG
import streamlit as st
import uuid
from urllib.parse import parse_qs, urlparse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_auth_state():
    """Genera un estado único para la autenticación"""
    return str(uuid.uuid4())

def is_streamlit_cloud():
    """Verifica si estamos en Streamlit Cloud"""
    return os.environ.get('STREAMLIT_SERVER_PORT') is not None

def get_strava_tokens():
    """Obtiene los tokens de Strava, renovándolos si es necesario"""
    try:
        logger.info("Verificando tokens existentes...")
        if os.path.exists('strava_tokens.json'):
            with open('strava_tokens.json', 'r') as f:
                tokens = json.load(f)
            
            # Verificar si el token ha expirado
            if time.time() < tokens.get('expires_at', 0):
                logger.info("Token válido encontrado")
                return tokens
            else:
                logger.info("Token expirado, renovando...")
                return refresh_tokens(tokens['refresh_token'])
        else:
            logger.info("No se encontraron tokens, iniciando flujo de autenticación...")
            return streamlit_auth_flow()
            
    except Exception as e:
        logger.error(f"Error obteniendo tokens: {str(e)}")
        return None

def streamlit_auth_flow():
    """Flujo de autenticación para Streamlit con redirección automática"""
    try:
        logger.info("Iniciando flujo de autenticación en Streamlit...")
        
        # Generar estado único si no existe
        if 'auth_state' not in st.session_state:
            st.session_state.auth_state = generate_auth_state()
        
        # Verificar si hay código en la URL
        query_params = st.experimental_get_query_params()
        if 'code' in query_params and 'state' in query_params:
            # Verificar que el state coincide
            if query_params['state'][0] == st.session_state.auth_state:
                logger.info("Código de autorización recibido, intercambiando por tokens...")
                auth_code = query_params['code'][0]
                
                # Intercambiar código por tokens
                response = requests.post(
                    STRAVA_CONFIG['token_url'],
                    data={
                        'client_id': STRAVA_CONFIG['client_id'],
                        'client_secret': STRAVA_CONFIG['client_secret'],
                        'code': auth_code,
                        'grant_type': 'authorization_code'
                    }
                )
                response.raise_for_status()
                
                tokens = response.json()
                tokens['expires_at'] = time.time() + tokens['expires_in']
                
                with open('strava_tokens.json', 'w') as f:
                    json.dump(tokens, f)
                
                logger.info("Autenticación completada exitosamente")
                st.success("¡Autenticación exitosa! Los datos se actualizarán automáticamente.")
                
                # Limpiar parámetros de la URL
                st.experimental_set_query_params()
                
                return tokens
            else:
                logger.error("State no coincide, posible ataque CSRF")
                st.error("Error de seguridad en la autenticación. Por favor, intenta de nuevo.")
                return None
        
        # Mostrar URL de autorización
        auth_url = f"{STRAVA_CONFIG['auth_url']}?client_id={STRAVA_CONFIG['client_id']}&response_type=code&redirect_uri={STRAVA_CONFIG['redirect_uri']}&scope={STRAVA_CONFIG['scope']}&state={st.session_state.auth_state}"
        
        st.markdown("### Autenticación de Strava")
        st.markdown("Haz clic en el siguiente enlace para autorizar la aplicación:")
        st.markdown(f"[Autorizar en Strava]({auth_url})")
        
        with st.spinner("Esperando autorización..."):
            time.sleep(1)  # Dar tiempo para que el usuario haga clic
            
    except Exception as e:
        logger.error(f"Error en el flujo de autenticación: {str(e)}")
        st.error(f"Error en la autenticación: {str(e)}")
        return None

def refresh_tokens(refresh_token):
    """Renueva los tokens usando el refresh token"""
    try:
        logger.info("Renovando tokens...")
        response = requests.post(
            STRAVA_CONFIG['token_url'],
            data={
                'client_id': STRAVA_CONFIG['client_id'],
                'client_secret': STRAVA_CONFIG['client_secret'],
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        response.raise_for_status()
        
        tokens = response.json()
        tokens['expires_at'] = time.time() + tokens['expires_in']
        
        with open('strava_tokens.json', 'w') as f:
            json.dump(tokens, f)
        
        logger.info("Tokens renovados exitosamente")
        return tokens
        
    except Exception as e:
        logger.error(f"Error renovando tokens: {str(e)}")
        return None

def start_auth_flow():
    """Inicia el flujo de autenticación OAuth2 (solo para desarrollo local)"""
    try:
        logger.info("Iniciando flujo de autenticación local...")
        app = Flask(__name__)
        auth_code = None
        
        @app.route('/callback')
        def callback():
            nonlocal auth_code
            auth_code = request.args.get('code')
            return "Autenticación exitosa. Puedes cerrar esta ventana."
        
        # Iniciar servidor en un hilo separado
        server_thread = threading.Thread(target=app.run, kwargs={'port': 8000})
        server_thread.daemon = True
        server_thread.start()
        
        # Abrir navegador para autorización
        auth_url = f"{STRAVA_CONFIG['auth_url']}?client_id={STRAVA_CONFIG['client_id']}&response_type=code&redirect_uri={STRAVA_CONFIG['redirect_uri']}&scope={STRAVA_CONFIG['scope']}"
        logger.info("Abriendo navegador para autorización...")
        webbrowser.open(auth_url)
        
        # Esperar el código de autorización
        logger.info("Esperando código de autorización...")
        while auth_code is None:
            time.sleep(1)
        
        # Intercambiar código por tokens
        logger.info("Intercambiando código por tokens...")
        response = requests.post(
            STRAVA_CONFIG['token_url'],
            data={
                'client_id': STRAVA_CONFIG['client_id'],
                'client_secret': STRAVA_CONFIG['client_secret'],
                'code': auth_code,
                'grant_type': 'authorization_code'
            }
        )
        response.raise_for_status()
        
        tokens = response.json()
        tokens['expires_at'] = time.time() + tokens['expires_in']
        
        with open('strava_tokens.json', 'w') as f:
            json.dump(tokens, f)
        
        logger.info("Autenticación completada exitosamente")
        return tokens
        
    except Exception as e:
        logger.error(f"Error en el flujo de autenticación: {str(e)}")
        return None 