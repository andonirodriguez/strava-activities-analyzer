import json
from datetime import datetime
from collections import defaultdict

def format_time(minutes):
    """Convierte minutos a formato '00h 00m'"""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}h {mins:02d}m"

def load_activities():
    """Carga las actividades desde el archivo JSON"""
    with open('strava_activities.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_totals_by_sport(activities):
    """Calcula totales por deporte"""
    totals = defaultdict(lambda: {
        'count': 0,
        'distance': 0,
        'time': 0,
        'elevation': 0
    })
    
    for activity in activities:
        sport = activity['type']
        totals[sport]['count'] += 1
        
        # Convertir distancia de metros a kilómetros
        if 'distance' in activity:
            totals[sport]['distance'] += activity['distance'] / 1000
        
        # Convertir tiempo de segundos a minutos
        if 'moving_time' in activity:
            totals[sport]['time'] += activity['moving_time'] / 60
        
        # Elevación en metros
        if 'total_elevation_gain' in activity:
            totals[sport]['elevation'] += activity['total_elevation_gain']
    
    return totals

def calculate_totals_by_year(activities):
    """Calcula totales por año"""
    totals = defaultdict(lambda: defaultdict(lambda: {
        'count': 0,
        'distance': 0,
        'time': 0,
        'elevation': 0
    }))
    
    for activity in activities:
        sport = activity['type']
        year = datetime.fromisoformat(activity['start_date_local'].replace('Z', '+00:00')).year
        
        totals[year][sport]['count'] += 1
        
        if 'distance' in activity:
            totals[year][sport]['distance'] += activity['distance'] / 1000
        
        if 'moving_time' in activity:
            totals[year][sport]['time'] += activity['moving_time'] / 60
        
        if 'total_elevation_gain' in activity:
            totals[year][sport]['elevation'] += activity['total_elevation_gain']
    
    return totals

def print_summary_by_sport(totals):
    """Imprime el resumen por deporte"""
    print("\n=== RESUMEN POR DEPORTE ===\n")
    
    for sport, data in totals.items():
        print(f"\n{sport.upper()}:")
        print(f"  Número de actividades: {data['count']}")
        
        if sport.lower() in ['ride', 'run', 'swim', 'walk']:
            print(f"  Distancia total: {data['distance']:.2f} km")
        
        print(f"  Tiempo total: {format_time(data['time'])}")
        
        if sport.lower() in ['ride', 'run']:
            print(f"  Elevación total: {data['elevation']:.0f} m")

def print_summary_by_year(totals):
    """Imprime el resumen por año"""
    print("\n=== RESUMEN POR AÑO ===\n")
    
    for year in sorted(totals.keys(), reverse=True):
        print(f"\nAÑO {year}:")
        
        for sport, data in totals[year].items():
            print(f"\n  {sport.upper()}:")
            print(f"    Número de actividades: {data['count']}")
            
            if sport.lower() in ['ride', 'run', 'swim', 'walk']:
                print(f"    Distancia total: {data['distance']:.2f} km")
            
            print(f"    Tiempo total: {format_time(data['time'])}")
            
            if sport.lower() in ['ride', 'run']:
                print(f"    Elevación total: {data['elevation']:.0f} m")

def main():
    activities = load_activities()
    
    # Resumen por deporte
    totals_by_sport = calculate_totals_by_sport(activities)
    print_summary_by_sport(totals_by_sport)
    
    # Resumen por año
    totals_by_year = calculate_totals_by_year(activities)
    print_summary_by_year(totals_by_year)

if __name__ == "__main__":
    main() 