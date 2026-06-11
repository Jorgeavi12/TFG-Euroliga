# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob

# --- CONFIGURACIÓN DE RUTA ---
PATH_JUGADORES = r"C:\Users\Jorge\Desktop\TFG\Datos\jugadores"
archivos = glob.glob(os.path.join(PATH_JUGADORES, "estadisticas_jugadores*.csv"))

def limpiar_minutos(min_str):
    try:
        if ':' in str(min_str):
            partes = str(min_str).split(':')
            return float(partes[0]) + float(partes[1])/60
        return float(min_str)
    except: return 0.0

def calcular_enriquecimiento_final(df):
    # 1. Renombrar columnas para mayor claridad
    mapeo = {
        'FPF': 'Faltas_Cometidas',
        'FPC': 'Faltas_Recibidas',
        'TR': 'Tapones_Recibidos',
        'Val': 'Valoracion_PIR',
        '+/-': 'Mas_Menos'
    }
    df = df.rename(columns=mapeo)

    # 2. Limpieza y conversión 
    cols_base = ['Puntos', 'T2a', 'T2i', 'T3a', 'T3i', 'T1a', 'T1i', 
                    'Reb_Off', 'Reb_Def', 'Asistencias', 'Robos', 'Perdidas', 
                    'Tapones', 'Faltas_Cometidas', 'Faltas_Recibidas', 'Valoracion_PIR']
    
    for col in cols_base:
        if col in df.columns:
            # Quitamos cualquier cosa que no sea número y convertimos
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    # 3. Cálculos de eficiencia (Redondeo estricto a 2 decimales)
    df['Minutos_Dec'] = df['Minutos'].apply(limpiar_minutos).round(2)
    tca = df['T2a'] + df['T3a'] 
    tci = df['T2i'] + df['T3i'] 

    df['eFG%'] = (((tca + 0.5 * df['T3a']) / tci.replace(0, 1)) * 100).round(2) 
    df['TS%'] = ((df['Puntos'] / (2 * (tci + 0.44 * df['T1i']).replace(0, 1))) * 100).round(2)
    df['Ratio_Asist_Perd'] = (df['Asistencias'] / df['Perdidas'].replace(0, 0.5)).round(2)
    df['Puntos_Por_Minuto'] = (df['Puntos'] / df['Minutos_Dec'].replace(0, 1)).round(2)
    
    df['Game_Score'] = (df['Puntos'] + 0.4*tca - 0.7*tci - 0.4*(df['T1i']-df['T1a']) + 
                        0.7*df['Reb_Off'] + 0.3*df['Reb_Def'] + df['Robos'] + 
                        0.7*df['Asistencias'] + 0.7*df['Tapones'] - 0.4*df['Faltas_Cometidas'] - df['Perdidas']).round(2)

    totales_equipo = df.groupby(['ID Partido', 'Equipo'])[['Reb_Off', 'Reb_Def']].sum().reset_index()

    # 2. Creamos una copia idéntica pero cambiando las etiquetas a 'Rival' para poder cruzarlos
    totales_rival = totales_equipo.rename(columns={
        'Equipo': 'Equipo Rival',
        'Reb_Off': 'Rival_Reb_Off',
        'Reb_Def': 'Rival_Reb_Def'
    })

    # 3. Mapeamos los rebotes del propio equipo del jugador al DataFrame principal
    df = df.merge(totales_equipo.rename(columns={'Reb_Off': 'Equipo_Reb_Off', 'Reb_Def': 'Equipo_Reb_Def'}), 
                    on=['ID Partido', 'Equipo'], how='left')

    # 4. Mapeamos los rebotes del equipo rival al DataFrame principal
    df = df.merge(totales_rival, on=['ID Partido', 'Equipo Rival'], how='left')

    # Rellenamos nulos por seguridad (evita que el script falle si falta alguna muestra)
    df['Rival_Reb_Off'] = df['Rival_Reb_Off'].fillna(0)
    df['Rival_Reb_Def'] = df['Rival_Reb_Def'].fillna(0)

    # Limpiamos las columnas auxiliares generadas para dejar el archivo exactamente igual que antes
    df = df.drop(columns=['Equipo_Reb_Off', 'Equipo_Reb_Def', 'Rival_Reb_Off', 'Rival_Reb_Def'])

    return df

# --- EJECUCIÓN ---
for archivo in archivos:
    try:
        df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig')
        df = calcular_enriquecimiento_final(df)
        
        df.to_csv(archivo, index=False, sep=';', decimal=',', encoding='utf-8-sig')

    except Exception as e:
        print(f"Error en {os.path.basename(archivo)}: {e}")

print("\n¡Listo!")