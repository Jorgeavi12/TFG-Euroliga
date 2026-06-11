# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import re

# --- RUTAS ---
ruta_entrada = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos\Temporadas'
ruta_salida = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Master_Equipos_UNIFICADO_FINAL.csv'

def limpiar_id(val):
    if pd.isna(val): return "DESC"
    s = str(val).strip().upper()
    return s

def generar_master_equipos():
    patron = os.path.join(ruta_entrada, "Euroleague_E*_FullStats.csv")
    archivos = glob.glob(patron)
    
    print(f"Archivos encontrados en Temporadas: {len(archivos)}")
    
    acumulado = {}

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        anio_match = re.search(r'E(\d{4})', nombre_archivo)
        if not anio_match: continue
        anio = int(anio_match.group(1))
        
        if not (2010 <= anio <= 2026): continue
        
        print(f"Procesando temporada {anio}...")
        
        try:
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
            df.columns = [c.strip() for c in df.columns]

            for _, fila in df.iterrows():
                def n(col):
                    val = fila.get(col, 0)
                    try: return float(str(val).replace(',', '.'))
                    except: return 0.0

                # Buscamos 'ID Equipo'  
                # Si algún archivo viejo tuviera 'ID_Equipo', el .get() lo soluciona para que no rompa.
                id_columna = 'ID Equipo' if 'ID Equipo' in df.columns else 'ID_Equipo'
                
                id_eq = limpiar_id(fila[id_columna])
                pj = n('Partidos')
                
                if id_eq not in acumulado:
                    acumulado[id_eq] = {
                        'Equipo': str(fila['Equipo']).strip(),
                        'ID_Equipo': id_eq,
                        'PJ': 0, 'W': 0, 'L': 0,
                        'pts_abs': 0, 'asist_abs': 0, 'perd_abs': 0,
                        'ro_abs': 0, 'rd_abs': 0, 't2a_abs': 0, 't2i_abs': 0,
                        't3a_abs': 0, 't3i_abs': 0, 't1a_abs': 0, 't1i_abs': 0,
                        'fga_abs': 0, 'fta_abs': 0, 'tov_abs': 0,
                        'pos_abs': 0, 'pts_rival_abs': 0, 'pos_rival_abs': 0,
                        'ro_rival_abs': 0, 'rd_rival_abs': 0
                    }
                
                reg = acumulado[id_eq]
                reg['PJ'] += pj
                reg['W'] += n('W')
                reg['L'] += n('L')
                
                # Volúmenes (Promedio_PG * Partidos)
                reg['pts_abs'] += n('PPG') * pj
                reg['asist_abs'] += n('Asist_PG') * pj
                reg['perd_abs'] += n('Perd_PG') * pj
                reg['ro_abs'] += n('Reb_Off_PG') * pj
                reg['rd_abs'] += n('Reb_Def_PG') * pj
                
                # Tiros
                reg['t2a_abs'] += n('T2a_PG') * pj
                reg['t2i_abs'] += n('T2i_PG') * pj
                reg['t3a_abs'] += n('T3a_PG') * pj
                reg['t3i_abs'] += n('T3i_PG') * pj
                reg['t1a_abs'] += n('T1a_PG') * pj
                reg['t1i_abs'] += n('T1i_PG') * pj

                # Datos para Avanzadas (ORTG/DRTG/Pace)
                fga_t = n('Equipo_FGA')
                fta_t = n('Equipo_FTA')
                tov_t = n('Equipo_TOV')
                ro_t = n('Reb_Off_PG') * pj
                
                pos_temporada = fga_t + (0.44 * fta_t) - ro_t + tov_t
                reg['pos_abs'] += pos_temporada
                reg['fga_abs'] += fga_t
                reg['fta_abs'] += fta_t
                reg['tov_abs'] += tov_t
                
                minutos_totales = 40 * pj
                pos_totales_partido = (n('Pace_Medio') * minutos_totales) / 40
                reg['pos_rival_abs'] += (pos_totales_partido * 2) - pos_temporada
                reg['pts_rival_abs'] += n('DRTG') * (pos_temporada / 100)

                # Datos de rebote rival para porcentajes
                reb_eq = (n('Reb_Off_PG') + n('Reb_Def_PG')) * pj
                reb_pct = n('REB%_Total') / 100
                if reb_pct > 0:
                    reb_rival_total = (reb_eq / reb_pct) - reb_eq
                    reg['ro_rival_abs'] += reb_rival_total * 0.3
                    reg['rd_rival_abs'] += reb_rival_total * 0.7

        except Exception as e:
            print(f"Error en {nombre_archivo}: {e}")

    if not acumulado: 
        print("No se acumularon datos")
        return

    df_final = pd.DataFrame(list(acumulado.values()))
    pj_t = df_final['PJ']

    # --- CÁLCULOS FINALES (PROMEDIOS DE CARRERA) ---
    df_final['Partidos_Jugados'] = pj_t.astype(int)
    df_final['%_Wins'] = (df_final['W'] / pj_t * 100).round(2)
    df_final['PPG'] = (df_final['pts_abs'] / pj_t).round(2)
    df_final['Asist_PG'] = (df_final['asist_abs'] / pj_t).round(2)
    df_final['Perd_PG'] = (df_final['perd_abs'] / pj_t).round(2)
    df_final['Reb_Off_PG'] = (df_final['ro_abs'] / pj_t).round(2)
    df_final['Reb_Def_PG'] = (df_final['rd_abs'] / pj_t).round(2)

    # Porcentajes
    df_final['%T2'] = (df_final['t2a_abs'] / df_final['t2i_abs'].replace(0,1) * 100).round(2)
    df_final['%T3'] = (df_final['t3a_abs'] / df_final['t3i_abs'].replace(0,1) * 100).round(2)
    df_final['%T1'] = (df_final['t1a_abs'] / df_final['t1i_abs'].replace(0,1) * 100).round(2)

    # Distribución de puntos
    df_final['%_Pts_Triple'] = (df_final['t3a_abs']*3 / df_final['pts_abs'] * 100).round(2)
    df_final['%_Pts_Dos'] = (df_final['t2a_abs']*2 / df_final['pts_abs'] * 100).round(2)
    df_final['%_Pts_TL'] = (df_final['t1a_abs'] / df_final['pts_abs'] * 100).round(2)

    # Avanzadas
    df_final['ORTG'] = (df_final['pts_abs'] / df_final['pos_abs'] * 100).round(2)
    df_final['DRTG'] = (df_final['pts_rival_abs'] / df_final['pos_abs'] * 100).round(2)
    df_final['NetRTG'] = (df_final['ORTG'] - df_final['DRTG']).round(2)
    df_final['Pace_Medio'] = (df_final['pos_abs'] / (pj_t * 40) * 40).round(2)

    tca = df_final['t2a_abs'] + df_final['t3a_abs']
    tci = df_final['t2i_abs'] + df_final['t3i_abs']
    df_final['eFG%'] = ((tca + 0.5 * df_final['t3a_abs']) / tci.replace(0,1) * 100).round(2)
    df_final['TS%'] = (df_final['pts_abs'] / (2 * (tci + 0.44 * df_final['fta_abs']).replace(0,1)) * 100).round(2)
    
    df_final['3PAr'] = (df_final['t3i_abs'] / tci.replace(0,1)).round(3)
    df_final['FTr'] = (df_final['fta_abs'] / tci.replace(0,1)).round(3)
    
    # Rebotes %
    reb_tot = df_final['ro_abs'] + df_final['rd_abs']
    df_final['REB%_Total'] = (reb_tot / (reb_tot + df_final['ro_rival_abs'] + df_final['rd_rival_abs']).replace(0,1) * 100).round(2)
    df_final['ORB%'] = (df_final['ro_abs'] / (df_final['ro_abs'] + df_final['rd_rival_abs']).replace(0,1) * 100).round(2)
    df_final['DRB%'] = (df_final['rd_abs'] / (df_final['rd_abs'] + df_final['ro_rival_abs']).replace(0,1) * 100).round(2)

    # Totales Reales
    df_final['Puntos_Totales'] = df_final['pts_abs'].round(0).astype(int)
    df_final['Rebotes_Totales'] = (df_final['ro_abs'] + df_final['rd_abs']).round(0).astype(int)
    df_final['Asistencias_Totales'] = df_final['asist_abs'].round(0).astype(int)

    cols_finales = [
        'Equipo', 'ID_Equipo', 'Partidos_Jugados', 'W', 'L', '%_Wins', 'PPG', 'Asist_PG', 'Perd_PG',
        'Reb_Off_PG', 'Reb_Def_PG', 'REB%_Total', '%T2', '%T3', '%T1', 
        '%_Pts_Triple', '%_Pts_Dos', '%_Pts_TL', 'Pace_Medio', 'ORTG', 'DRTG', 'NetRTG', 
        'eFG%', 'TS%', '3PAr', 'FTr', 'ORB%', 'DRB%',
        'Puntos_Totales', 'Rebotes_Totales', 'Asistencias_Totales'
    ]

    df_final[cols_finales].sort_values('Puntos_Totales', ascending=False).to_csv(
        ruta_salida, index=False, sep=';', encoding='utf-8-sig', decimal=','
    )
    print(f"Archivo generado con éxito")

if __name__ == "__main__":
    generar_master_equipos()