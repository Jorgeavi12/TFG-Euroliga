# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS DE ORIGEN Y DESTINO ---
ruta_origen_historico = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\historico_jugadores.csv'

# Nueva tabla de hechos para el modelo estrella
ruta_fact_historico = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Fact_Jugadores_Historico.csv'

def crear_fact_historico_jugadores():
    print(f"Leyendo archivo histórico acumulado desde: {ruta_origen_historico}")
    if not os.path.exists(ruta_origen_historico):
        print(f"Error: No se encuentra el archivo .")
        return

    try:
        # Cargamos el dataframe histórico respetando separadores y formatos
        df = pd.read_csv(ruta_origen_historico, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        print("Generando tabla FACT_JUGADORES_HISTORICO ...")
        
        # Lista estricta de columnas 
        cols_fact_historico = [
            'ID Jugador', 'ID_Equipo', 'Partidos_Jugados', 'Puntos', 'Asistencias', 
            'Reb_Off', 'Reb_Def', 'Rebotes', 'T2%', 'T3%', 'T1%', '%_Pts_T2', '%_Pts_T3', 
            '%_Pts_T1', 'Robos', 'Perdidas', 'Tapones', 'Tapones_Recibidos', 'Faltas_Cometidas', 
            'Faltas_Recibidas', 'Valoracion_PIR', 'eFG%', 'TS%', '3PAr', 'AST_TO_Ratio', 
            'PPM', 'Game_Score', 'Minutos_Dec', 'Puntos_totales', 'Asistencias_totales', 
            'Rebotes_totales', 'Robos_totales', 'Tapones_totales', 'Perdidas_totales', 
            'Triples_metidos_totales', 'Tiros_media_distancia_metidos_totales', 'valoracion_total'
        ]
        
        # Filtramos por seguridad asegurando que existan las columnas en el archivo de origen
        cols_existentes = [c for c in cols_fact_historico if c in df.columns]
        df_fact_hist = df[cols_existentes].copy()
        
        # Ordenamos de mayor a menor por puntos totales para tener una vista atractiva 
        if 'Puntos_totales' in df_fact_hist.columns:
            # Convertimos temporalmente a numérico solo para ordenar correctamente
            df_fact_hist['order_helper'] = pd.to_numeric(df_fact_hist['Puntos_totales'].str.replace(',', '.'), errors='coerce')
            df_fact_hist = df_fact_hist.sort_values('order_helper', ascending=False).drop(columns=['order_helper'])

        # --- EXPORTACIÓN ---
        print(f"Guardando Fact_Jugadores_Historico en: {ruta_fact_historico}")
        df_fact_hist.to_csv(ruta_fact_historico, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print("\nTABLA FACT HISTÓRICA GUARADA")
        print(f"Total de jugadores: {len(df_fact_hist)}")

    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

if __name__ == "__main__":
    crear_fact_historico_jugadores()