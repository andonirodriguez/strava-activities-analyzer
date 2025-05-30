# Strava Activities Analyzer

Aplicación personal para analizar y visualizar actividades de Strava.

## Características

- Extracción automática de actividades de Strava
- Visualización interactiva de datos
- Análisis de tendencias y estadísticas
- Actualización automática de datos

## Requisitos

- Python 3.10+
- Poetry para gestión de dependencias
- Cuenta de Strava con API access

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/strava-activities-analyzer.git
cd strava-activities-analyzer
```

2. Instalar dependencias:
```bash
poetry install
```

3. Configurar variables de entorno:
Crear un archivo `.env` con:
```
STRAVA_CLIENT_ID=tu_client_id
STRAVA_CLIENT_SECRET=tu_client_secret
```

## Uso

1. Ejecutar la aplicación:
```bash
poetry run streamlit run visualize_activities.py
```

2. Acceder a la aplicación en `http://localhost:8501`

## Estructura del Proyecto

- `strava_data_extractor.py`: Extracción de datos de Strava
- `strava_client.py`: Cliente para la API de Strava
- `strava_auth.py`: Manejo de autenticación OAuth
- `config.py`: Configuración centralizada
- `visualize_activities.py`: Aplicación de visualización

## Seguridad

- Los datos sensibles (tokens, credenciales) se almacenan localmente
- No se suben al repositorio
- Autenticación requerida para acceder a la aplicación

## Licencia

Uso personal 