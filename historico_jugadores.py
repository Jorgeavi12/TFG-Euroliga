# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS ---
ruta_unificado_origen = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\EuroleagueAllSeasonsJugadores.csv'
ruta_salida_historico = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Master_Jugadores_UNIFICADO_FINAL.csv'

def limpiar_id(val):
    """Limpia el ID para que 00123 y 123 sean el mismo, y quita espacios."""
    if pd.isna(val): return "DESCONOCIDO"
    s = str(val).strip().upper()
    if s.isdigit():
        return str(int(s))
    return s

def generar_historico_jugadores_final():
    print(f"Leyendo archivo unificado de jugadores desde: {ruta_unificado_origen}")
    if not os.path.exists(ruta_unificado_origen):
        print("Error: No se encuentra el archivo ")
        return

    try:
        df = pd.read_csv(ruta_unificado_origen, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        print("Procesando y acumulando trayectoria de IDs de equipos y volúmenes absolutos.")
        acumulado = {}

        for _, fila in df.iterrows():
            def n(col):
                val = fila.get(col, 0)
                try: return float(str(val).replace(',', '.'))
                except: return 0.0

            id_jugador = limpiar_id(fila['ID Jugador'])
            pj = n('Partidos_Jugados')
            
            if pj == 0: continue 

            # Capturamos directamente 'ID_Equipo' en lugar de 'Equipo'
            id_equipo_actual = str(fila.get('ID_Equipo', fila.get('Equipo', ''))).strip().upper()

            if id_jugador not in acumulado:
                acumulado[id_jugador] = {
                    'Nombre': str(fila['Nombre']).strip(),
                    'ID Jugador': id_jugador,
                    'Equipos_Set': set(),  # Conjunto para evitar duplicar códigos de equipo
                    'Partidos_Jugados': 0,
                    'pts_abs': 0, 'asist_abs': 0, 'ro_abs': 0, 'rd_abs': 0, 'reb_abs': 0,
                    'rob_abs': 0, 'perd_abs': 0, 'tap_abs': 0, 'tap_rec_abs': 0,
                    'faltas_c_abs': 0, 'faltas_r_abs': 0, 'val_abs': 0, 'min_abs': 0,
                    't2a_abs': 0, 't2i_abs': 0, 't3a_abs': 0, 't3i_abs': 0, 't1a_abs': 0, 't1i_abs': 0
                }
            
            reg = acumulado[id_jugador]
            
            # Guardamos el código del equipo si es válido
            if id_equipo_actual and id_equipo_actual != "NAN":
                reg['Equipos_Set'].add(id_equipo_actual)
                
            reg['Partidos_Jugados'] += pj
            reg['pts_abs'] += n('Puntos') * pj
            reg['asist_abs'] += n('Asistencias') * pj
            reg['ro_abs'] += n('Reb_Off') * pj
            reg['rd_abs'] += n('Reb_Def') * pj
            reg['reb_abs'] += n('Rebotes') * pj
            reg['rob_abs'] += n('Robos') * pj
            reg['perd_abs'] += n('Perdidas') * pj
            reg['tap_abs'] += n('Tapones') * pj
            reg['tap_rec_abs'] += n('Tapones_Recibidos') * pj
            reg['faltas_c_abs'] += n('Faltas_Cometidas') * pj
            reg['faltas_r_abs'] += n('Faltas_Recibidas') * pj
            reg['val_abs'] += n('Valoracion_PIR') * pj
            reg['min_abs'] += n('Minutos_Dec') * pj
            reg['t2a_abs'] += n('T2a') * pj
            reg['t2i_abs'] += n('T2i') * pj
            reg['t3a_abs'] += n('T3a') * pj
            reg['t3i_abs'] += n('T3i') * pj
            reg['t1a_abs'] += n('T1a') * pj
            reg['t1i_abs'] += n('T1i') * pj

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return

    lista_final = []
    for id_jugador, datos in acumulado.items():
        # Juntamos los códigos cortos (Como "BAR, OLY, RMD")
        datos['ID_Equipo'] = ", ".join(sorted(list(datos['Equipos_Set'])))
        lista_final.append(datos)

    df_final = pd.DataFrame(lista_final)
    if df_final.empty:
        print("No se pudo extraer ningún registro.")
        return

    print("Recalculando estadísticas avanzadas y promedios...")
    
    # Agrupación final de seguridad estricta por ID Jugador
    df_final = df_final.groupby('ID Jugador').agg({
        'Nombre': 'last', 
        'ID_Equipo': lambda x: ", ".join(sorted(list(set([e.strip() for sublist in x.str.split(',') for e in sublist if e.strip()])))),
        'Partidos_Jugados': 'sum',
        'pts_abs': 'sum', 'asist_abs': 'sum', 'ro_abs': 'sum', 'rd_abs': 'sum', 
        'reb_abs': 'sum', 'rob_abs': 'sum', 'perd_abs': 'sum', 'tap_abs': 'sum', 
        'tap_rec_abs': 'sum', 'faltas_c_abs': 'sum', 'faltas_r_abs': 'sum', 
        'val_abs': 'sum', 'min_abs': 'sum', 't2a_abs': 'sum', 't2i_abs': 'sum', 
        't3a_abs': 'sum', 't3i_abs': 'sum', 't1a_abs': 'sum', 't1i_abs': 'sum'
    }).reset_index()

    pj_total = df_final['Partidos_Jugados']
    tca = df_final['t2a_abs'] + df_final['t3a_abs']
    tci = df_final['t2i_abs'] + df_final['t3i_abs']

    # --- PROMEDIOS DE CARRERA ---
    df_final['Puntos'] = (df_final['pts_abs'] / pj_total).round(2)
    df_final['Asistencias'] = (df_final['asist_abs'] / pj_total).round(2)
    df_final['Reb_Off'] = (df_final['ro_abs'] / pj_total).round(2)
    df_final['Reb_Def'] = (df_final['rd_abs'] / pj_total).round(2)
    df_final['Rebotes'] = (df_final['reb_abs'] / pj_total).round(2)
    df_final['Robos'] = (df_final['rob_abs'] / pj_total).round(2)
    df_final['Perdidas'] = (df_final['perd_abs'] / pj_total).round(2)
    df_final['Tapones'] = (df_final['tap_abs'] / pj_total).round(2)
    df_final['Tapones_Recibidos'] = (df_final['tap_rec_abs'] / pj_total).round(2)
    df_final['Faltas_Cometidas'] = (df_final['faltas_c_abs'] / pj_total).round(2)
    df_final['Faltas_Recibidas'] = (df_final['faltas_r_abs'] / pj_total).round(2)
    df_final['Valoracion_PIR'] = (df_final['val_abs'] / pj_total).round(2)
    df_final['Minutos_Dec'] = (df_final['min_abs'] / pj_total).round(2)

    # --- EFICIENCIAS Y AVANZADAS ---
    df_final['T2%'] = (df_final['t2a_abs'] / df_final['t2i_abs'].replace(0, 1) * 100).round(2)
    df_final['T3%'] = (df_final['t3a_abs'] / df_final['t3i_abs'].replace(0, 1) * 100).round(2)
    df_final['T1%'] = (df_final['t1a_abs'] / df_final['t1i_abs'].replace(0, 1) * 100).round(2)
    df_final['eFG%'] = (((tca + 0.5 * df_final['t3a_abs']) / tci.replace(0, 1)) * 100).round(2)
    df_final['TS%'] = ((df_final['pts_abs'] / (2 * (tci + 0.44 * df_final['t1i_abs']).replace(0, 1))) * 100).round(2)
    df_final['AST_TO_Ratio'] = (df_final['asist_abs'] / df_final['perd_abs'].replace(0, 0.5)).round(2)
    df_final['PPM'] = (df_final['pts_abs'] / df_final['min_abs'].replace(0, 1)).round(2)
    
    gs_sum = (df_final['pts_abs'] + 0.4*tca - 0.7*tci - 0.4*(df_final['t1i_abs']-df_final['t1a_abs']) + 
                0.7*df_final['ro_abs'] + 0.3*df_final['rd_abs'] + df_final['rob_abs'] + 
                0.7*df_final['asist_abs'] + 0.7*df_final['tap_abs'] - 0.4*df_final['faltas_c_abs'] - df_final['perd_abs'])
    df_final['Game_Score'] = (gs_sum / pj_total).round(2)

    df_final['%_Pts_T2'] = (df_final['t2a_abs']*2 / df_final['pts_abs'].replace(0, 1) * 100).round(2)
    df_final['%_Pts_T3'] = (df_final['t3a_abs']*3 / df_final['pts_abs'].replace(0, 1) * 100).round(2)
    df_final['%_Pts_T1'] = (df_final['t1a_abs'] / df_final['pts_abs'].replace(0, 1) * 100).round(2)
    df_final['3PAr'] = (df_final['t3i_abs'] / tci.replace(0, 1)).round(3)

    # --- TOTALES ACUMULADOS ---
    df_final['Puntos_totales'] = df_final['pts_abs'].round(0).astype(int)
    df_final['Asistencias_totales'] = df_final['asist_abs'].round(0).astype(int)
    df_final['Rebotes_totales'] = df_final['reb_abs'].round(0).astype(int)
    df_final['Robos_totales'] = df_final['rob_abs'].round(0).astype(int)
    df_final['Tapones_totales'] = df_final['tap_abs'].round(0).astype(int)
    df_final['Perdidas_totales'] = df_final['perd_abs'].round(0).astype(int)
    df_final['Triples_metidos_totales'] = df_final['t3a_abs'].round(0).astype(int)
    df_final['Tiros_media_distancia_metidos_totales'] = df_final['t2a_abs'].round(0).astype(int)
    df_final['valoracion_total'] = df_final['val_abs'].round(0).astype(int)

    # Lista final manteniendo el orden deseado de columnas
    cols_finales = [
        'Nombre', 'ID Jugador', 'ID_Equipo', 'Partidos_Jugados', 'Puntos', 'Asistencias', 
        'Reb_Off', 'Reb_Def', 'Rebotes', 'T2%', 'T3%', 'T1%', '%_Pts_T2', '%_Pts_T3', 
        '%_Pts_T1', 'Robos', 'Perdidas', 'Tapones', 'Tapones_Recibidos', 'Faltas_Cometidas', 
        'Faltas_Recibidas', 'Valoracion_PIR', 'eFG%', 'TS%', '3PAr', 'AST_TO_Ratio', 
        'PPM', 'Game_Score', 'Minutos_Dec', 'Puntos_totales', 'Asistencias_totales', 
        'Rebotes_totales', 'Robos_totales', 'Tapones_totales', 'Perdidas_totales', 
        'Triples_metidos_totales', 'Tiros_media_distancia_metidos_totales', 'valoracion_total'
    ]

    df_final[cols_finales].sort_values('Puntos_totales', ascending=False).to_csv(
        ruta_salida_historico, index=False, sep=';', encoding='utf-8-sig', decimal=','
    )
    
    print(f"Histórico completado con éxito!")

if __name__ == "__main__":
    generar_historico_jugadores_final()