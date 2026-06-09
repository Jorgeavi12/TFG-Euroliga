# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import re

# --- RUTAS JUGADORES ---
ruta_entrada = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Promedios_jugadores\Temporadas'
ruta_salida = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\EuroleagueAllSeasonsJugadores.csv'

# Ruta de la Dimensión para cruzar los nombres y conseguir los IDs cortos
ruta_dim_equipos = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos\Dim_Equipos.csv'

def unificar_all_seasons_jugadores():
    print(f"Leyendo diccionario de equipos desde: {ruta_dim_equipos}")
    if not os.path.exists(ruta_dim_equipos):
        print("Error Crítico: No se encontró 'Dim_Equipos.csv'.")
        return

    # Cargamos el mapa de Nombre Largo 
    df_dim = pd.read_csv(ruta_dim_equipos, sep=';', encoding='utf-8-sig', dtype=str)
    df_dim.columns = [c.strip() for c in df_dim.columns]
    
    mapeo_equipos = {}
    for _, fila_dim in df_dim.iterrows():
        nombre_largo = str(fila_dim['Equipo']).strip().upper()
        id_corto = str(fila_dim['ID_Equipo']).strip().upper()
        mapeo_equipos[nombre_largo] = id_corto

    # Buscamos todos los archivos que cumplan con el patrón del nombre
    patron = os.path.join(ruta_entrada, "promedios_jugadores_*.csv")
    archivos = glob.glob(patron)
    
    print(f"Archivos de jugadores encontrados: {len(archivos)}")
    
    if not archivos:
        print(f" No se encontraron archivos en la ruta: {ruta_entrada}")
        return

    lista_dataframes = []

    # Recorremos cada archivo detectado
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        
        anio_match = re.search(r'(\d{4})', nombre_archivo)
        if not anio_match: continue
        anio = int(anio_match.group(1))
        
        if not (2010 <= anio <= 2026): continue
        
        print(f"Leyendo temporada {anio}...")
        
        try:
            df_temp = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
            df_temp.columns = [c.strip() for c in df_temp.columns]
            
            # --- TRADUCCIÓN E INSERCIÓN DEL ID ---
            # Mapeamos la columna 'Equipo' aplicando el diccionario que creamos al principio
            ids_calculados = []
            for eq in df_temp['Equipo']:
                eq_clean = str(eq).strip().upper()
                # Si encuentra el ID corto lo pone; si no, por seguridad deja el nombre que venía
                ids_calculados.append(mapeo_equipos.get(eq_clean, eq_clean))
            
            # Insertamos la columna 'ID_Equipo' justo al lado de la columna 'Equipo'
            if 'Equipo' in df_temp.columns:
                pos_equipo = df_temp.columns.get_loc('Equipo')
                df_temp.insert(pos_equipo + 1, 'ID_Equipo', ids_calculados)
            else:
                df_temp['ID_Equipo'] = ids_calculados # Por si acaso
                
            lista_dataframes.append(df_temp)
            
        except Exception as e:
            print(f"Error al procesar el archivo {nombre_archivo}: {e}")

    if not lista_dataframes:
        print("No se pudo consolidar ningún dato de jugadores.")
        return

    print("Concatenando todas las temporadas en un único archivo maestro...")
    df_maestro_jugadores = pd.concat(lista_dataframes, ignore_index=True)

    # Ordenamos el resultado final
    columnas_orden = []
    if 'ID Temporada' in df_maestro_jugadores.columns: columnas_orden.append('ID Temporada')
    if 'ID_Equipo' in df_maestro_jugadores.columns: columnas_orden.append('ID_Equipo')
    if 'Nombre' in df_maestro_jugadores.columns: columnas_orden.append('Nombre')
    
    if columnas_orden:
        df_maestro_jugadores = df_maestro_jugadores.sort_values(columnas_orden)

    # Guardamos el archivo maestro final manteniendo los separadores intactos
    df_maestro_jugadores.to_csv(
        ruta_salida, index=False, sep=';', encoding='utf-8-sig', decimal=','
    )
    
    print(f"Archivo generado en: {ruta_salida}")

if __name__ == "__main__":
    unificar_all_seasons_jugadores()