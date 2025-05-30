import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import time
from strava_data_extractor import actualizar_datos

def obtener_ultima_actualizacion():
    """Obtiene la fecha de última modificación del archivo JSON"""
    try:
        timestamp = os.path.getmtime('strava_activities.json')
        return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    except:
        return "Nunca"

def datos_desactualizados():
    """Verifica si los datos tienen más de 24 horas"""
    try:
        timestamp = os.path.getmtime('strava_activities.json')
        return (time.time() - timestamp) > 86400  # 24 horas
    except:
        return True

def load_data():
    """Carga los datos desde el archivo JSON"""
    with open('strava_activities.json', 'r', encoding='utf-8') as f:
        activities = json.load(f)
    return pd.DataFrame(activities)

def prepare_data(df):
    """Prepara los datos para visualización"""
    # Convertir fechas
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df['year'] = df['start_date_local'].dt.year
    df['month'] = df['start_date_local'].dt.month
    df['month_name'] = df['start_date_local'].dt.strftime('%B')
    df['week'] = df['start_date_local'].dt.isocalendar().week
    df['week_date'] = df['start_date_local'].dt.to_period('W').dt.start_time
    
    # Convertir distancias a km
    df['distance_km'] = df['distance'] / 1000
    
    # Convertir tiempos a horas
    df['moving_time_hours'] = df['moving_time'] / 3600
    
    return df

def main():
    st.set_page_config(page_title="Análisis de Actividades Strava", layout="wide")
    
    # Inicializar estado de la sesión
    if 'updating' not in st.session_state:
        st.session_state.updating = False
    
    st.title("📊 Análisis de Actividades Strava")
    
    # Sidebar con filtros y actualización
    st.sidebar.header("Actualización de Datos")
    last_update = obtener_ultima_actualizacion()
    st.sidebar.text(f"Última actualización: {last_update}")
    
    if datos_desactualizados():
        st.sidebar.warning("⚠️ Los datos pueden estar desactualizados")
    
    # Opción para actualización automática
    auto_update = st.sidebar.checkbox("Actualizar automáticamente al inicio")
    if auto_update and datos_desactualizados() and not st.session_state.updating:
        with st.spinner("Actualizando datos..."):
            st.session_state.updating = True
            resultado = actualizar_datos(silent=True)
            st.session_state.updating = False
            if resultado['success']:
                st.sidebar.success(f"✅ Datos actualizados: {resultado['activities']} actividades")
            else:
                st.sidebar.error(f"❌ Error: {resultado['error']}")
    
    # Botón de actualización manual
    if st.sidebar.button("🔄 Actualizar Datos", disabled=st.session_state.updating):
        with st.spinner("Actualizando datos de Strava..."):
            st.session_state.updating = True
            resultado = actualizar_datos(silent=True)
            st.session_state.updating = False
            if resultado['success']:
                st.sidebar.success(f"✅ Datos actualizados: {resultado['activities']} actividades")
            else:
                st.sidebar.error(f"❌ Error: {resultado['error']}")
    
    st.sidebar.header("Filtros")
    
    # Cargar y preparar datos
    df = load_data()
    df = prepare_data(df)
    
    # Filtro por año
    years = sorted(df['year'].unique(), reverse=True)
    selected_years = st.sidebar.multiselect(
        "Seleccionar años",
        years,
        default=years
    )
    
    # Filtro por mes (solo si hay años seleccionados)
    if selected_years:
        months = sorted(df[df['year'].isin(selected_years)]['month'].unique())
        month_names = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                      7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        month_options = {month_names[m]: m for m in months}
        selected_months = st.sidebar.multiselect(
            "Seleccionar meses",
            list(month_options.keys()),
            default=list(month_options.keys())
        )
        selected_month_numbers = [month_options[m] for m in selected_months]
    else:
        selected_month_numbers = []
    
    # Filtro por tipo de actividad
    activity_types = sorted(df['type'].unique())
    selected_types = st.sidebar.multiselect(
        "Seleccionar tipos de actividad",
        activity_types,
        default=activity_types
    )
    
    # Aplicar filtros
    mask = (df['year'].isin(selected_years)) & (df['type'].isin(selected_types))
    if selected_month_numbers:
        mask = mask & (df['month'].isin(selected_month_numbers))
    filtered_df = df[mask]
    
    # Resumen general
    st.header("Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Actividades", len(filtered_df))
    with col2:
        st.metric("Distancia Total", f"{filtered_df['distance_km'].sum():.1f} km")
    with col3:
        st.metric("Tiempo Total", f"{filtered_df['moving_time_hours'].sum():.1f} h")
    with col4:
        st.metric("Elevación Total", f"{filtered_df['total_elevation_gain'].sum():.0f} m")
    
    # Gráficos
    st.header("Evolución Temporal")
    
    # Selector de granularidad temporal
    time_granularity = st.radio(
        "Seleccionar granularidad temporal",
        ["Mensual", "Semanal"],
        horizontal=True
    )
    
    if time_granularity == "Mensual":
        # Gráfico de actividades por mes
        monthly_activities = filtered_df.groupby(['year', 'month']).size().reset_index(name='count')
        monthly_activities['date'] = pd.to_datetime(monthly_activities[['year', 'month']].assign(day=1))
        
        fig_monthly = px.line(
            monthly_activities,
            x='date',
            y='count',
            title='Número de Actividades por Mes'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        # Gráfico de actividades por semana
        weekly_activities = filtered_df.groupby('week_date').size().reset_index(name='count')
        weekly_activities.columns = ['date', 'count']
        
        fig_weekly = px.line(
            weekly_activities,
            x='date',
            y='count',
            title='Número de Actividades por Semana'
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Gráfico de distancia por tipo de actividad
    st.header("Distribución por Tipo de Actividad")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_distance = px.pie(
            filtered_df,
            values='distance_km',
            names='type',
            title='Distancia por Tipo de Actividad'
        )
        st.plotly_chart(fig_distance, use_container_width=True)
    
    with col2:
        fig_time = px.pie(
            filtered_df,
            values='moving_time_hours',
            names='type',
            title='Tiempo por Tipo de Actividad'
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Estadísticas por tipo de actividad
    st.header("Estadísticas por Tipo de Actividad")
    stats_by_type = filtered_df.groupby('type').agg({
        'distance_km': ['count', 'sum', 'mean'],
        'moving_time_hours': ['sum', 'mean'],
        'total_elevation_gain': ['sum', 'mean']
    }).round(2)
    
    stats_by_type.columns = [
        'Número de Actividades',
        'Distancia Total (km)',
        'Distancia Media (km)',
        'Tiempo Total (h)',
        'Tiempo Medio (h)',
        'Elevación Total (m)',
        'Elevación Media (m)'
    ]
    
    st.dataframe(stats_by_type)
    
    # Evolución anual
    st.header("Evolución Anual")
    yearly_stats = filtered_df.groupby(['year', 'type']).agg({
        'distance_km': 'sum',
        'moving_time_hours': 'sum',
        'total_elevation_gain': 'sum'
    }).reset_index()
    
    fig_yearly_distance = px.bar(
        yearly_stats,
        x='year',
        y='distance_km',
        color='type',
        title='Distancia Anual por Tipo de Actividad',
        barmode='group'
    )
    st.plotly_chart(fig_yearly_distance, use_container_width=True)

    # Gráfico de tiempo anual por tipo de actividad
    fig_yearly_time = px.bar(
        yearly_stats,
        x='year',
        y='moving_time_hours',
        color='type',
        title='Tiempo Anual por Tipo de Actividad',
        barmode='group'
    )
    st.plotly_chart(fig_yearly_time, use_container_width=True)

    # Evolución mensual
    st.header("Evolución Mensual")
    
    # Preparar datos mensuales
    monthly_stats = filtered_df.groupby(['year', 'month', 'type']).agg({
        'distance_km': 'sum',
        'moving_time_hours': 'sum',
        'total_elevation_gain': 'sum'
    }).reset_index()
    
    # Crear fecha para el eje X
    monthly_stats['date'] = pd.to_datetime(monthly_stats[['year', 'month']].assign(day=1))
    
    # Gráfico de distancia mensual
    fig_monthly_distance = px.line(
        monthly_stats,
        x='date',
        y='distance_km',
        color='type',
        title='Distancia Mensual por Tipo de Actividad',
        markers=True
    )
    fig_monthly_distance.update_layout(
        xaxis_title="Mes",
        yaxis_title="Distancia (km)"
    )
    st.plotly_chart(fig_monthly_distance, use_container_width=True)
    
    # Gráfico de tiempo mensual
    fig_monthly_time = px.line(
        monthly_stats,
        x='date',
        y='moving_time_hours',
        color='type',
        title='Tiempo Mensual por Tipo de Actividad',
        markers=True
    )
    fig_monthly_time.update_layout(
        xaxis_title="Mes",
        yaxis_title="Tiempo (horas)"
    )
    st.plotly_chart(fig_monthly_time, use_container_width=True)
    
    # Gráfico de elevación mensual
    fig_monthly_elevation = px.line(
        monthly_stats,
        x='date',
        y='total_elevation_gain',
        color='type',
        title='Elevación Mensual por Tipo de Actividad',
        markers=True
    )
    fig_monthly_elevation.update_layout(
        xaxis_title="Mes",
        yaxis_title="Elevación (m)"
    )
    st.plotly_chart(fig_monthly_elevation, use_container_width=True)

    # Actividades de ciclismo largas
    st.header("🚴 Actividades de Ciclismo Largas (>100km)")
    
    # Filtrar actividades de ciclismo largas
    long_rides = filtered_df[
        (filtered_df['type'] == 'Ride') & 
        (filtered_df['distance_km'] >= 100)
    ].sort_values('distance_km', ascending=False)
    
    if len(long_rides) > 0:
        # Mostrar métricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Número de Rutas Largas", len(long_rides))
        with col2:
            st.metric("Distancia Total", f"{long_rides['distance_km'].sum():.1f} km")
        with col3:
            st.metric("Elevación Total", f"{long_rides['total_elevation_gain'].sum():.0f} m")
        
        # Preparar datos para la tabla
        rides_display = long_rides[[
            'start_date_local', 'name', 'distance_km', 
            'moving_time_hours', 'total_elevation_gain',
            'average_heartrate', 'max_heartrate'
        ]].copy()
        
        # Formatear el tiempo
        rides_display['moving_time_hours'] = rides_display['moving_time_hours'].apply(
            lambda x: f"{int(x)}h {int((x % 1) * 60):02d}m"
        )
        
        # Formatear la fecha
        rides_display['start_date_local'] = rides_display['start_date_local'].dt.strftime('%d/%m/%Y')
        
        # Renombrar columnas
        rides_display.columns = [
            'Fecha', 'Nombre', 'Distancia (km)', 
            'Tiempo', 'Elevación (m)',
            'Pulsaciones Medias', 'Pulsaciones Máximas'
        ]
        
        # Mostrar tabla
        st.dataframe(
            rides_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay actividades de ciclismo de más de 100km en el período seleccionado.")

if __name__ == "__main__":
    main() 