# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import warnings
from datetime import datetime, timedelta

warnings.simplefilter(action='ignore', category=FutureWarning)

all_columns = [
    'ID Temporada', 'Jornada', 'Fase', 'Fecha', 'Hora', 'Equipo Local', 'Equipo Visitante',
    'Puntos Local', 'Puntos Visitante', 'ID Partido', 'Competición', 'Enlace',
    'T2a Local', 'T2i Local', 'T3a Local', 'T3i Local', 'T1a Local', 'T1i Local', 
    'Rebotes Local', 'R.Def Local', 'R.Ofe Local', 'Asistencias Local', 'Robos Local', 
    'Perdidas Local', 'Tapones Local', 'TR Local', 'FPF Local', 'FPC Local', 'Val Local',
    '+/- Local', 'P1Local', 'P2Local', 'Q1Local', 'Q2Local', 'Q3Local', 'Q4Local',
    'PR1Local', 'PR2Local', 'PR3Local', 'Entrenador Local',
    'T2a Visitante', 'T2i Visitante', 'T3a Visitante', 'T3i Visitante', 'T1a Visitante', 
    'T1i Visitante', 'Rebotes Visitante', 'R.Def Visitante', 'R.Ofe Visitante', 
    'Asistencias Visitante', 'Robos Visitante', 'Perdidas Visitante', 'Tapones Visitante', 
    'TR Visitante', 'FPF Visitante', 'FPC Visitante', 'Val Visitante', '+/- Visitante', 
    'P1Visitante', 'P2Visitante', 'Q1Visitante', 'Q2Visitante', 'Q3Visitante', 'Q4Visitante', 
    'PR1Visitante', 'PR2Visitante', 'PR3Visitante', 'Entrenador Visitante',
    'ID Equipo Local', 'ID Equipo Visitante'  
]

int_columns = [
    'Jornada', 'Puntos Local', 'Puntos Visitante', 'T2a Local', 'T2i Local', 'T3a Local', 
    'T3i Local', 'T1a Local', 'T1i Local', 'Rebotes Local', 'R.Def Local', 'R.Ofe Local', 
    'Asistencias Local', 'Robos Local', 'Perdidas Local', 'Tapones Local', 'TR Local', 
    'FPF Local', 'FPC Local', 'Val Local', '+/- Local', 'P1Local', 'P2Local', 'Q1Local', 
    'Q2Local', 'Q3Local', 'Q4Local', 'PR1Local', 'PR2Local', 'PR3Local', 
    'T2a Visitante', 'T2i Visitante', 'T3a Visitante', 'T3i Visitante', 'T1a Visitante', 
    'T1i Visitante', 'Rebotes Visitante', 'R.Def Visitante', 'R.Ofe Visitante', 
    'Asistencias Visitante', 'Robos Visitante', 'Perdidas Visitante', 'Tapones Visitante', 
    'TR Visitante', 'FPF Visitante', 'FPC Visitante', 'Val Visitante', '+/- Visitante', 
    'P1Visitante', 'P2Visitante', 'Q1Visitante', 'Q2Visitante', 'Q3Visitante', 'Q4Visitante', 
    'PR1Visitante', 'PR2Visitante', 'PR3Visitante'
]

path = r".\Datos\\"
archivo_csv = path + 'estadisticas_partidos_E2011.csv'

try:
    df = pd.read_csv(archivo_csv)
    for col in all_columns:
        if col not in df.columns:
            df[col] = None
    df = df.drop_duplicates(subset=['Jornada', 'Equipo Local', 'Equipo Visitante'], keep='first')
    print(f"Archivo cargado. Tras limpiar duplicados quedan {len(df)} partidos reales.")
except:
    df = pd.DataFrame(columns=all_columns)
    print("Archivo nuevo creado.")

urls_24 = [f'https://www.euroleaguebasketball.net/en/euroleague/game-center/2011-12/a/E2011/{i}/' for i in range(1, 400)]

options = Options()   
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

print(f"Iniciando extracción controlada con IDs de equipos...")

for url in urls_24:
    if url in df['Enlace'].values:
        continue

    for intento in range(2):
        try:
            driver.get(url + '#boxscore')
            time.sleep(5 if intento == 0 else 8) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
            
            if script_tag:
                json_data = json.loads(script_tag.string)
                
                if 'mappedData' not in json_data['props']['pageProps']:
                    if intento == 0: continue 
                    else: raise KeyError("'mappedData' no encontrado")

                main_game = json_data['props']['pageProps']['mappedData']['rawGameInfo']
                
                if not main_game['home']['score']:
                    print(f"Saltando {url}: No jugado.")
                    break 

                eq_local = main_game['home']['name']
                eq_vis = main_game['away']['name']
                jornada_actual = main_game.get('round')['round']
                
                coincidencia = df[(df['Equipo Local'] == eq_local) & 
                                (df['Equipo Visitante'] == eq_vis) & 
                                (df['Jornada'] == jornada_actual)]
                
                if not coincidencia.empty:
                    print(f"Redirección detectada en ID {url.split('/')[-2]}. El partido {eq_local} vs {eq_vis} ya estaba guardado. Saltando...")
                    break 

                home_team_official = eq_local
                date_str = main_game.get('date', '')
                game_datetime = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                # Extraemos los códigos de equipo del JSON original
                id_equipo_local = main_game['home'].get('code', '')
                id_equipo_visitante = main_game['away'].get('code', '')
                
                totals = {
                    'ID Temporada': 'E2011',
                    'Jornada': jornada_actual,
                    'Fase': main_game.get('phaseType')['name'],
                    'Fecha': game_datetime.date().strftime('%d/%m/%Y'),
                    'Hora': (game_datetime + timedelta(hours=2)).time(),
                    'Equipo Local': eq_local,
                    'Equipo Visitante': eq_vis,
                    'Puntos Local': int(main_game['home']['score']),
                    'Puntos Visitante': int(main_game['away']['score']),
                    'ID Partido': url, 
                    'Competición': 'EL',
                    'Enlace': url,
                    'ID Equipo Local': id_equipo_local,       
                    'ID Equipo Visitante': id_equipo_visitante  
                }

                stats_table = json_data['props']['pageProps']['mappedData']['boxScores']['statsTable'] 
                
                for team in stats_table:
                    nombre_tabla = team['archValues']['teamName']
                    suffix = 'Local' if nombre_tabla == home_team_official else 'Visitante'
                    entrenador = team['groups'][-1]['groupValues']['fullName']
                    
                    for group in team['groups']:
                        if group['groupName'] == 'Total':
                            ts = group['stats']
                            t2, t3, t1 = ts[1]['value'][0]['stat'].split('/'), ts[2]['value'][0]['stat'].split('/'), ts[3]['value'][0]['stat'].split('/')
                            bq = json_data['props']['pageProps']['mappedData']['boxScores']['byQuarterInfo']
                            tk = 'homeTeam' if nombre_tabla == home_team_official else 'awayteam'

                            extracted_data = {
                                f'Minutos {suffix}': ts[0]['value'][0]['stat'],
                                f'T2a {suffix}': int(t2[0]), f'T2i {suffix}': int(t2[1]),
                                f'T3a {suffix}': int(t3[0]), f'T3i {suffix}': int(t3[1]),
                                f'T1a {suffix}': int(t1[0]), f'T1i {suffix}': int(t1[1]),
                                f'Rebotes {suffix}': int(ts[4]['value'][2]['stat']),
                                f'R.Def {suffix}': int(ts[4]['value'][1]['stat']),
                                f'R.Ofe {suffix}': int(ts[4]['value'][0]['stat']),
                                f'Asistencias {suffix}': int(ts[5]['value'][0]['stat']),
                                f'Robos {suffix}': int(ts[5]['value'][1]['stat']),
                                f'Perdidas {suffix}': int(ts[5]['value'][2]['stat']),
                                f'Tapones {suffix}': int(ts[6]['value'][0]['stat']),
                                f'TR {suffix}': int(ts[6]['value'][1]['stat']),
                                f'FPF {suffix}': int(ts[7]['value'][0]['stat']),
                                f'FPC {suffix}': int(ts[7]['value'][1]['stat']),
                                f'Val {suffix}': int(ts[8]['value'][0]['stat']),
                                f'+/- {suffix}': int(ts[8]['value'][1]['stat']) if ts[8]['value'][1]['stat']!='' else 0,
                                f'Q1{suffix}': int(bq[tk]['q1']), f'Q2{suffix}': int(bq[tk]['q2']),
                                f'Q3{suffix}': int(bq[tk]['q3']), f'Q4{suffix}': int(bq[tk]['q4']),
                                f'P1{suffix}': int(bq[tk]['q1']) + int(bq[tk]['q2']),
                                f'P2{suffix}': int(bq[tk]['q3']) + int(bq[tk]['q4']),
                                f'PR1{suffix}': int(bq[tk]['ot1']), f'PR2{suffix}': int(bq[tk]['ot2']), f'PR3{suffix}': int(bq[tk]['ot3']),
                                f'Entrenador {suffix}': entrenador
                            }
                            totals.update(extracted_data)

                dfn = pd.DataFrame(totals, index=[0])
                # Aseguramos que el dfn tenga las columnas en el orden estricto de all_columns
                dfn = dfn.reindex(columns=all_columns)
                df = pd.concat([df, dfn], ignore_index=True)
                print(f"J{totals['Jornada']} ({totals['Fase']}) - OK: {totals['Equipo Local']} vs {totals['Equipo Visitante']} [{id_equipo_local} vs {id_equipo_visitante}]")
                df.to_csv(archivo_csv, index=False)
                break 

        except Exception as e:
            if intento == 0:
                continue
            else:
                print(f"Error definitivo en {url}: {e}")
                
for col in int_columns:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# Guardado final garantizando el orden estricto de columnas
df = df.reindex(columns=all_columns)
df.to_csv(archivo_csv, index=False)

try:
    driver.quit()
except:
    pass

print(f"TERMINADO. Hay {len(df)} partidos")
