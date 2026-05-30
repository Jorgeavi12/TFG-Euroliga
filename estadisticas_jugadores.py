# -*- coding: utf-8 -*-
import pandas as pd
import requests
import os
import time
import random
import re

# --- CONFIGURACIÓN ---
PATH_ENTRADA = r"C:\Users\Jorge\Desktop\TFG\Datos\equipos\Estadisticas_partidos"  # Limpiado para evitar barras dobles
PATH_SALIDA = r"C:\Users\Jorge\Desktop\TFG\Datos"
ARCHIVO_PARTIDOS = 'estadisticas_partidos_E2023.csv'
ARCHIVO_SALIDA = 'estadisticas_jugadores2023.csv'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def obtener_build_id():
    """Busca el código dinámico de la web para que no de Error 404"""
    print("Buscando el código de versión de la web...")
    url_base = "https://www.euroleaguebasketball.net/en/euroleague/game-center/"
    try:
        res = requests.get(url_base, headers=HEADERS)
        match = re.search(r'"buildId":"(.*?)"', res.text)
        if match:
            print(f"Código encontrado: {match.group(1)}")
            return match.group(1)
    except: pass
    return "969"

def calcular_pct(aciertos, intentos):
    try:
        return round((int(aciertos) / int(intentos)) * 100, 1) if int(intentos) > 0 else 0.0
    except: return 0.0

# 1. Carga (Detectamos separador y limpiamos posibles espacios/BOM de Excel de raíz)
ruta_partidos = os.path.join(PATH_ENTRADA, ARCHIVO_PARTIDOS)
dfp = pd.read_csv(ruta_partidos, sep=None, engine='python', encoding='utf-8-sig')

# Truco maestro: Limpiamos los nombres de todas las columnas para evitar KeyErrors invisibles
dfp.columns = [col.replace('\ufeff', '').strip() for col in dfp.columns]

ruta_output = os.path.join(PATH_SALIDA, ARCHIVO_SALIDA)

if os.path.exists(ruta_output):
    df_acumulado = pd.read_csv(ruta_output, sep=';', encoding='utf-8-sig')
    links_procesados = set(df_acumulado['ID Partido'].unique())
else:
    df_acumulado = pd.DataFrame()
    links_procesados = set()  # Corregido de links_processed para que coincida

pendientes = dfp[~dfp['ID Partido'].isin(links_procesados)].to_dict('records')
random.shuffle(pendientes)

BUILD_ID = obtener_build_id()

print(f"Iniciando descarga. Faltan {len(pendientes)} partidos.")

try:
    for i, partido in enumerate(pendientes):
        url_original = partido['ID Partido']
        parts = url_original.strip('/').split('/')
        game_id = parts[-1]
        season_code = parts[-2]
        
        # URL construida con el Build ID dinámico
        api_url = f"https://www.euroleaguebasketball.net/_next/data/{BUILD_ID}/en/euroleague/game-center/2023-2024/a/{season_code}/{game_id}.json?seasonCode={season_code}&gameCode={game_id}"

        # EXTRACCIÓN SEGURA: Usamos .get() por si acaso alguna columna viene con espacios en el diccionario
        jornada_actual = partido.get('Jornada', i + 1)
        fase_actual = partido.get('Fase', 'Regular Season')

        print(f"[{i+1}/{len(pendientes)}] Jornada {jornada_actual} ({fase_actual})...", end=" ", flush=True)
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                data = res.json()
                stats_table = data['pageProps']['mappedData']['boxScores']['statsTable']
                
                partido_stats = []
                eq_a, eq_b = stats_table[0]['archValues']['teamName'], stats_table[1]['archValues']['teamName']

                for team in stats_table:
                    nombre_eq = team['archValues']['teamName']
                    rival = eq_b if nombre_eq == eq_a else eq_a
                    
                    for group in team['groups']:
                        if group['groupName'] in ['Total', '', 'Head coach:', 'Team']: continue
                        s = group['stats']
                        if s[0]['value'][0]['stat'] == '00:00': continue
                        
                        # Extraemos el código del jugador
                        player_id = group['groupValues']['code']
                        
                        t2a, t2i = s[1]['value'][0]['stat'].split('/')
                        t3a, t3i = s[2]['value'][0]['stat'].split('/')
                        t1a, t1i = s[3]['value'][0]['stat'].split('/')

                        partido_stats.append({
                            'ID Temporada': partido.get('ID Temporada', 'E2023'),
                            'Jornada': jornada_actual,
                            'Fase': fase_actual,
                            'Fecha': partido.get('Fecha'),
                            'Equipo': nombre_eq, 'Equipo Rival': rival,
                            'ID Partido': url_original,
                            'Dorsal': group['groupValues']['dorsal'],
                            'Nombre': group['groupName'],
                            'ID Jugador': player_id,  
                            'Minutos': s[0]['value'][0]['stat'],
                            'Puntos': int(s[0]['value'][1]['stat']),
                            'T2a': int(t2a), 'T2i': int(t2i), 'T2%': calcular_pct(t2a, t2i),
                            'T3a': int(t3a), 'T3i': int(t3i), 'T3%': calcular_pct(t3a, t3i),
                            'T1a': int(t1a), 'T1i': int(t1i), 'T1%': calcular_pct(t1a, t1i),
                            'Reb_Off': int(s[4]['value'][0]['stat']), 'Reb_Def': int(s[4]['value'][1]['stat']), 'Rebotes': int(s[4]['value'][2]['stat']),
                            'Asistencias': int(s[5]['value'][0]['stat']), 'Robos': int(s[5]['value'][1]['stat']), 'Perdidas': int(s[5]['value'][2]['stat']),
                            'Tapones': int(s[6]['value'][0]['stat']), 'TR': int(s[6]['value'][1]['stat']),
                            'FPF': int(s[7]['value'][0]['stat']), 'FPC': int(s[7]['value'][1]['stat']),
                            'Val': int(s[8]['value'][0]['stat']),
                            '+/-': int(s[8]['value'][1]['stat']) if s[8]['value'][1]['stat'] != '' else 0,
                            'Competición': 'Euroleague'
                        })
                
                df_temp = pd.DataFrame(partido_stats)
                df_temp.to_csv(ruta_output, mode='a', index=False, sep=';', header=not os.path.exists(ruta_output), encoding='utf-8-sig')
                print("✓")
            else:
                print(f"× Error {res.status_code}")
                if res.status_code == 404:
                    print("Cambiando código de versión...")
                    BUILD_ID = obtener_build_id()

        except Exception as e:
            print(f"× Fallo: {e}")

        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print("\nDetenido.")