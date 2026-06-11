# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- CONFIGURACIÓN MANUAL ---
ANIO_OBJETIVO = "2010"
PATH_ENTRADA = r"C:\Users\Jorge\Desktop\TFG\Datos\jugadores"
PATH_SALIDA = r"C:\Users\Jorge\Desktop\TFG\Datos"

archivo_csv = f"estadisticas_jugadores{ANIO_OBJETIVO}.csv"
archivo_final = f"promedios_jugadores_{ANIO_OBJETIVO}.csv"

def limpiar_num(serie):
    return pd.to_numeric(serie.astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

def generar_promedios():
    ruta_completa = os.path.join(PATH_ENTRADA, archivo_csv)
    
    if not os.path.exists(ruta_completa):
        print(f"No se encuentra el archivo: {archivo_csv}")
        return

    df = pd.read_csv(ruta_completa, sep=';', encoding='utf-8-sig')

    cols_a_sumar = [
        'Puntos', 'Asistencias', 'Reb_Off', 'Reb_Def', 'Rebotes',
        'T2a', 'T2i', 'T3a', 'T3i', 'T1a', 'T1i', 
        'Robos', 'Perdidas', 'Tapones', 'Tapones_Recibidos', 
        'Faltas_Cometidas', 'Faltas_Recibidas', 'Valoracion_PIR', 
        'Mas_Menos', 'Game_Score', 'Minutos_Dec'
    ]
    
    for col in cols_a_sumar:
        if col in df.columns:
            df[col] = limpiar_num(df[col])

    # Aseguramos que las columnas de agrupamiento existan de forma segura
    if 'Fase' not in df.columns:
        df['Fase'] = 'Regular Season'
        
    if 'ID Temporada' not in df.columns:
        df['ID Temporada'] = f"E{ANIO_OBJETIVO}"

    # 1. Agrupar incluyendo 'ID Temporada' y 'Fase' para segmentar correctamente
    resumen = df.groupby(['ID Temporada', 'Nombre', 'ID Jugador', 'Equipo', 'Fase']).agg({
        'ID Partido': 'count',
        **{col: 'sum' for col in cols_a_sumar if col in df.columns}
    }).reset_index()

    resumen = resumen.rename(columns={'ID Partido': 'Partidos_Jugados'})
    pj = resumen['Partidos_Jugados']

    # --- NUEVAS MÉTRICAS: % DESGLOSE DE PUNTOS ---
    pts_totales = resumen['Puntos'].replace(0, 1)
    resumen['%_Pts_T2'] = ((resumen['T2a'] * 2 / pts_totales) * 100).round(1)
    resumen['%_Pts_T3'] = ((resumen['T3a'] * 3 / pts_totales) * 100).round(1)
    resumen['%_Pts_T1'] = ((resumen['T1a'] / pts_totales) * 100).round(1)

    # 2. Calcular PROMEDIOS POR PARTIDO
    for col in cols_a_sumar:
        if col in resumen.columns:
            resumen[col] = (resumen[col] / pj).round(2)

    # 3. Métricas de Eficiencia y Ratios
    fga = (resumen['T2i'] + resumen['T3i']).replace(0, 1)
    tot_intentos_tiros = (resumen['T2i'] + resumen['T3i'] + resumen['T1i']).replace(0, 1)
    
    resumen['T2%'] = ((resumen['T2a'] / resumen['T2i'].replace(0,1)) * 100).round(1)
    resumen['T3%'] = ((resumen['T3a'] / resumen['T3i'].replace(0,1)) * 100).round(1)
    resumen['T1%'] = ((resumen['T1a'] / resumen['T1i'].replace(0,1)) * 100).round(1)
    resumen['eFG%'] = (((resumen['T2a'] + 1.5 * resumen['T3a']) / fga) * 100).round(1)
    
    resumen['TS%'] = ((resumen['Puntos'] / (2 * (fga + 0.44 * resumen['T1i'].replace(0, 0.5)))) * 100).round(1)
    
    # Ratios de Frecuencia de Tiro Añadidos
    resumen['2PAr'] = (resumen['T2i'] / tot_intentos_tiros).round(3)
    resumen['3PAr'] = (resumen['T3i'] / fga).round(3)
    resumen['1PAr'] = (resumen['T1i'] / tot_intentos_tiros).round(3)
    
    resumen['AST_TO_Ratio'] = (resumen['Asistencias'] / resumen['Perdidas'].replace(0, 0.5)).round(2)
    resumen['PPM'] = (resumen['Puntos'] / resumen['Minutos_Dec'].replace(0, 1)).round(2)

    # 4. ORDEN FINAL DE COLUMNAS 
    orden_final = [
        'ID Temporada', 'Nombre', 'ID Jugador', 'Equipo', 'Fase', 'Partidos_Jugados', 'Puntos', 'Asistencias', 'Reb_Off', 'Reb_Def', 
        'Rebotes', 'OREB%', 'DREB%', 'T2a', 'T2i', 'T2%', 'T3a', 'T3i', 'T3%', 'T1a', 'T1i', 'T1%', 
        '%_Pts_T2', '%_Pts_T3', '%_Pts_T1', 
        'Robos', 'Perdidas', 'Tapones', 'Tapones_Recibidos', 'Faltas_Cometidas', 
        'Faltas_Recibidas', 'Valoracion_PIR', 'Mas_Menos', 'eFG%', 'TS%', 
        '2PAr', '3PAr', '1PAr', 'AST_TO_Ratio', 'PPM', 'Game_Score', 'Minutos_Dec'
    ]

    # Nos aseguramos de solo usar columnas que existan para que no de error
    columnas_finales = [c for c in orden_final if c in resumen.columns]
    resumen = resumen[columnas_finales]
    
    # Ordenamos por volumen de anotación
    resumen = resumen.sort_values(by='Puntos', ascending=False)

    # Guardar
    ruta_salida_final = os.path.join(PATH_SALIDA, archivo_final)
    resumen.to_csv(ruta_salida_final, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    
    print(f"Promedios por Temporada y Fase completados para {ANIO_OBJETIVO}")

if __name__ == "__main__":
    generar_promedios()