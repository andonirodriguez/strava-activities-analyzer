import json
import os
import logging
from strava_client import StravaClient
from strava_auth import get_strava_tokens
from config import STRAVA_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_activities(activities, filename='strava_activities.json', silent=False):
    """
    Guarda las actividades en un archivo JSON con manejo de errores
    Args:
        activities: Lista de actividades a guardar
        filename: Nombre del archivo donde guardar
        silent: Si es True, no muestra mensajes en consola
    """
    try:
        # Intentar crear el archivo si no existe
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump([], f)
        
        # Guardar las actividades
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(activities, f, ensure_ascii=False, indent=2)
        if not silent:
            print(f"Actividades guardadas en '{filename}'")
        return True
    except PermissionError:
        error_msg = f"Error: No tienes permisos para escribir en '{filename}'"
        if not silent:
            print(error_msg)
            print("Intenta ejecutar el script con permisos de administrador o cambia los permisos del archivo.")
        return False
    except Exception as e:
        error_msg = f"Error al guardar las actividades: {str(e)}"
        if not silent:
            print(error_msg)
        return False

def actualizar_datos(silent=False):
    """Actualiza los datos de actividades de Strava"""
    try:
        logger.info("Iniciando actualización de datos...")
        
        # Obtener tokens
        logger.info("Obteniendo tokens de Strava...")
        tokens = get_strava_tokens()
        if not tokens:
            error_msg = "No se pudieron obtener los tokens de Strava"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Crear cliente de Strava
        logger.info("Creando cliente de Strava...")
        client = StravaClient(tokens['access_token'])
        
        # Obtener actividades
        logger.info("Obteniendo actividades de Strava...")
        activities = client.get_activities()
        if not activities:
            error_msg = "No se pudieron obtener las actividades"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        logger.info(f"Se obtuvieron {len(activities)} actividades")
        
        # Guardar actividades en archivo JSON
        logger.info("Guardando actividades en archivo JSON...")
        if save_activities(activities, silent=silent):
            logger.info("Actualización completada exitosamente")
            return {'success': True, 'activities': len(activities)}
        else:
            error_msg = "Error al guardar las actividades"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
    except Exception as e:
        error_msg = f"Error durante la actualización: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}

def main():
    """Función principal para ejecutar el script directamente"""
    resultado = actualizar_datos(silent=False)
    if not resultado['success']:
        if "No hay tokens disponibles" in resultado['error']:
            auth = StravaAuth()
            print("\nNecesitas autenticarte primero. Visita esta URL:")
            print(auth.get_auth_url())
            print("\nDespués de autorizar, copia el código de la URL y ejecuta:")
            print("python strava_auth.py <código>")
        else:
            print(f"Error: {resultado['error']}")

if __name__ == "__main__":
    main()