# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os

# 1. CONFIGURACIÓN DE RUTAS
directorio_actual = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(directorio_actual, "Datos", "equipos")

# Soporte para minúsculas si falla la anterior
if not os.path.exists(path):
    path = os.path.join(directorio_actual, "datos", "equipos")

archivos = glob.glob(os.path.join(path, "estadisticas_partidos_E*.csv"))

def limpiar_minutos(tiempo_str):
    try:
        if pd.isna(tiempo_str) or tiempo_str == "": return 40.0
        partes = str(tiempo_str).split(':')
        minutos_brutos = float(partes[0]) + float(partes[1])/60
        # Normalización: 200 min (5 jugadores) -> 40 min (tiempo real de juego)
        if minutos_brutos > 100:
            return minutos_brutos / 5
        return minutos_brutos
    except:
        return 40.0

def calcular_factores_oliver(df):
    """Calcula estadísticas avanzadas y los 4 Factores de Dean Oliver"""
    
    # Cálculo de posesiones para ambos (necesario para el ritmo y DRTG)
    for s in ['Local', 'Visitante']:
        fga = (df[f'T2i {s}'] + df[f'T3i {s}']).replace(0, 1)
        fta = df[f'T1i {s}']
        # Fórmula de Posesiones: FGA + 0.44*FTA - ORB + TOV
        df[f'Posesiones {s}'] = (fga + (0.44 * fta) - df[f'R.Ofe {s}'] + df[f'Perdidas {s}']).round(2)

    for s in ['Local', 'Visitante']:
        rival = 'Visitante' if s == 'Local' else 'Local'
        
        # Referencias rápidas
        fga = (df[f'T2i {s}'] + df[f'T3i {s}']).replace(0, 1)
        fga_rival = (df[f'T2i {rival}'] + df[f'T3i {rival}']).replace(0, 1)
        fgm = (df[f'T2a {s}'] + df[f'T3a {s}'])
        fgm_rival = (df[f'T2a {rival}'] + df[f'T3a {rival}'])
        fta = df[f'T1i {s}']
        fta_rival = df[f'T1i {rival}']
        ftm = df[f'T1a {s}']
        ftm_rival = df[f'T1a {rival}']
        
        # 1. RITMO Y EFICIENCIA GENERAL
        # Control de seguridad: Si la columna no existe en el CSV, usamos 40:00 por defecto
        col_minutos = f'Minutos {s}'
        tiempo_origen = df[col_minutos].iloc[0] if col_minutos in df.columns and not df.empty else "40:00"
        
        minutos = limpiar_minutos(tiempo_origen)
        pos_media = (df[f'Posesiones {s}'] + df[f'Posesiones {rival}']) / 2
        df[f'Pace Partido'] = ((pos_media / minutos) * 40).round(2)
        
        df[f'ORTG {s}'] = ((df[f'Puntos {s}'] / df[f'Posesiones {s}'].replace(0,1)) * 100).round(2)
        df[f'DRTG {s}'] = ((df[f'Puntos {rival}'] / df[f'Posesiones {rival}'].replace(0,1)) * 100).round(2)

        # --- LOS 4 FACTORES (OFENSIVOS) ---
        df[f'eFG% {s}'] = ((fgm + 0.5 * df[f'T3a {s}']) / fga).round(4)
        df[f'TOV% {s}'] = (df[f'Perdidas {s}'] / (fga + 0.44 * fta + df[f'Perdidas {s}'])).round(4)
        df[f'ORB% {s}'] = (df[f'R.Ofe {s}'] / (df[f'R.Ofe {s}'] + df[f'R.Def {rival}']).replace(0,1)).round(4)
        df[f'FT/FGA {s}'] = (ftm / fga).round(4)
        
        # --- LOS 4 FACTORES (DEFENSIVOS / DEL RIVAL) ---
        df[f'eFG%_oponente {s}'] = ((fgm_rival + 0.5 * df[f'T3a {rival}']) / fga_rival).round(4)
        df[f'TOV%_oponente {s}'] = (df[f'Perdidas {rival}'] / (fga_rival + 0.44 * fta_rival + df[f'Perdidas {rival}'])).round(4)
        df[f'DRB% {s}'] = (df[f'R.Def {s}'] / (df[f'R.Def {s}'] + df[f'R.Ofe {rival}']).replace(0,1)).round(4)
        df[f'FT/FGA_oponente {s}'] = (ftm_rival / fga_rival).round(4)

    return df

def organizar_columnas(df):
    """Mueve los factores al final de forma ordenada y posiciona los IDs al lado de los equipos"""
    # 1. Definimos el orden exacto de las columnas iniciales metiendo los IDs al lado de cada equipo
    columnas_ordenadas = [
        'ID Temporada', 'Jornada', 'Fase', 'Fecha', 'Hora', 
        'Equipo Local', 'ID Equipo Local',     
        'Equipo Visitante', 'ID Equipo Visitante' 
    ]
    
    # 2. Capturamos dinámicamente el resto de columnas base que NO son factores de Oliver
    columnas_excluir = ['eFG%', 'TOV%', 'ORB%', 'DRB%', 'FT/FGA']
    cols_resto_base = [c for c in df.columns if c not in columnas_ordenadas and not any(f in c for f in columnas_excluir)]
    
    # 3. Estructura de bloques finales para los 4 factores
    factores_local = [f'eFG% Local', f'TOV% Local', f'ORB% Local', f'FT/FGA Local', 
                        f'eFG%_oponente Local', f'TOV%_oponente Local', f'DRB% Local', f'FT/FGA_oponente Local']
    
    factores_visit = [f'eFG% Visitante', f'TOV% Visitante', f'ORB% Visitante', f'FT/FGA Visitante', 
                        f'eFG%_oponente Visitante', f'TOV%_oponente Visitante', f'DRB% Visitante', f'FT/FGA_oponente Visitante']
    
    # Unimos todo respetando que existan en el DataFrame
    columnas_finales = [c for c in columnas_ordenadas if c in df.columns] + cols_resto_base + factores_local + factores_visit
    return df[columnas_finales]

# --- PROCESAMIENTO ---
if not archivos:
    print(f"No se encontraron archivos en {path}")
else:
    for f in archivos:
        try:
            # Leemos detectando separador (coma o punto y coma)
            df = pd.read_csv(f, sep=None, engine='python')
            
            # Limpieza y Cálculo
            df = calcular_factores_oliver(df)
            df = organizar_columnas(df)
            
            # Guardado
            df.to_csv(f, index=False, sep=';', encoding='utf-8-sig')
            print(f" Procesado: {os.path.basename(f)}")
        except Exception as e:
            print(f" Error en {os.path.basename(f)}: {e}")

print("\nListo!")