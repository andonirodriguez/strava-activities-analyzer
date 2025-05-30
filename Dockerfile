# Usar la imagen oficial de Python como base
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar las dependencias necesarias
RUN pip install requests streamlit pandas plotly

# Copiar los archivos de la aplicación
COPY . .

# Configurar Python para mostrar la salida inmediatamente
ENV PYTHONUNBUFFERED=1

# Exponer el puerto para Streamlit
EXPOSE 8501

# Comando por defecto al ejecutar el contenedor
CMD ["streamlit", "run", "visualize_activities.py", "--server.port=8501", "--server.address=0.0.0.0"] 