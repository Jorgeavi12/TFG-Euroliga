# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS DE ORIGEN Y DESTINO ---
ruta_origen = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\EuroleagueAllSeasonsJugadores.csv'

# Carpeta de destino para el Modelo Relacional
ruta_dim_jugadores = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Dim_Jugadores.csv'
ruta_fact_jugadores = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Fact_Jugadores_Temporadas.csv'

def crear_modelo_relacional_jugadores():
    print(f"📖 Leyendo archivo maestro desde: {ruta_origen}")
    if not os.path.exists(ruta_origen):
        print(f"Error: No se encuentra el archivo de origen en la ruta especificada.")
        return

    try:
        # Cargamos el dataframe origen respetando tus formatos
        df = pd.read_csv(ruta_origen, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        print("Generando tabla DIM_JUGADORES...")
        # 1. DIMENSIÓN: Solo ID Jugador y Nombre 
        # Limpiamos duplicados para que cada ID de jugador aparezca una única vez en la Dim
        df_dim = df[['ID Jugador', 'Nombre']].drop_duplicates(subset=['ID Jugador']).copy()
        
        # Ordenamos alfabéticamente por nombre o
        df_dim = df_dim.sort_values('Nombre')
        
        print("Generando tabla FACT_JUGADORES (Tabla de hechos)...")
        # 2. FACT: Todas las métricas con el ID Jugador al inicio como conector, incluyendo Temporada y Fase
        # Definimos el orden estricto de las columnas que queremos
        cols_fact = [
            'ID Jugador', 'ID Temporada', 'Fase', 'Equipo', 'ID_Equipo', 
            'Partidos_Jugados', 'Puntos', 'Asistencias', 'Reb_Off', 'Reb_Def', 'Rebotes', 
            'OREB%', 'DREB%', 'T2a', 'T2i', 'T2%', 'T3a', 'T3i', 'T3%', 'T1a', 'T1i', 'T1%', 
            '%_Pts_T2', '%_Pts_T3', '%_Pts_T1', 'Robos', 'Perdidas', 'Tapones', 
            'Tapones_Recibidos', 'Faltas_Cometidas', 'Faltas_Recibidas', 'Valoracion_PIR', 
            'Mas_Menos', 'eFG%', 'TS%', '2PAr', '3PAr', '1PAr', 'AST_TO_Ratio', 'PPM', 
            'Game_Score', 'Minutos_Dec'
        ]
        
        # Filtramos asegurándonos de que solo vayan las columnas que existen 
        cols_existentes = [c for c in cols_fact if c in df.columns]
        df_fact = df[cols_existentes].copy()
        
        # Ordenamos la Fact para que sea cómoda de analizar visualmente
        df_fact = df_fact.sort_values(['ID Temporada', 'ID_Equipo', 'ID Jugador'])

        # --- EXPORTACIÓN DE LOS DOS ARCHIVOS ---
        print(f"Guardando Dim_Jugadores en: {ruta_dim_jugadores}")
        df_dim.to_csv(ruta_dim_jugadores, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print(f"Guardando Fact_Jugadores en: {ruta_fact_jugadores}")
        df_fact.to_csv(ruta_fact_jugadores, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print("\nProceso finalizado con éxito!")
        print(f"Total de jugadores únicos en la DIM: {len(df_dim)}")
        print(f"Total de registros métricos en la FACT: {len(df_fact)}")

    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

if __name__ == "__main__":
    crear_modelo_relacional_jugadores()