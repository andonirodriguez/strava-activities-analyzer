import json
import os
from strava_client import StravaClient
from strava_auth import StravaAuth

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
    """
    Actualiza los datos de Strava
    Args:
        silent (bool): Si es True, no muestra mensajes en consola
    Returns:
        dict: {
            'success': bool,
            'activities': int,
            'error': str (si hay error)
        }
    """
    try:
        # Inicializar el cliente
        client = StravaClient()
        
        # Obtener actividades
        if not silent:
            print("\nObteniendo actividades...")
        activities = client.get_all_activities()
        
        # Guardar resultados
        if activities:
            if not silent:
                print(f"\nGuardando {len(activities)} actividades...")
            if save_activities(activities, silent=silent):
                return {
                    'success': True,
                    'activities': len(activities)
                }
            else:
                return {
                    'success': False,
                    'error': "Error al guardar las actividades"
                }
        else:
            if not silent:
                print("No se encontraron actividades")
            return {
                'success': True,
                'activities': 0
            }
            
    except Exception as e:
        error_msg = str(e)
        if not silent:
            print(f"Error: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

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

if __name__ == "__main__":
    main()