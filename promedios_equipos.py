# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import re

# Configuración de la ruta
ruta_carpeta = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos\Temporadas' 
archivo_salida = os.path.join(ruta_carpeta, 'Euroleague_Equipos_AllSeasons.csv')

def extraer_anio(nombre_archivo):
    # Busca 4 dígitos en el nombre del archivo (ej: 2010, 2024)
    match = re.search(r'(\d{4})', nombre_archivo)
    return int(match.group(1)) if match else 0

def aglutinar_csvs():
    # Buscamos todos los archivos .csv
    patron = os.path.join(ruta_carpeta, "*.csv")
    archivos = glob.glob(patron)
    
    # Filtramos para no incluir el archivo de salida si ya existía
    archivos = [f for f in archivos if 'AllSeasons' not in f]
    
    # ORDENAR: De mayor a menor año (2024 -> 2023 -> ... -> 2003)
    archivos.sort(key=extraer_anio, reverse=True)
    
    lista_df = []

    print(f"Encontrados {len(archivos)} archivos. Procesando en orden descendente...")

    for archivo in archivos:
        try:
            # Usamos sep=';' y encoding utf-8-sig para evitar problemas con tildes/eñes
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig')
            
            lista_df.append(df)
            print(f"Añadido: {os.path.basename(archivo)}")
            
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")

    if lista_df:
        # Concatenamos todo
        df_final = pd.concat(lista_df, ignore_index=True, sort=False)
        
        # COLOCAR EL ID AL LADO DE EQUIPO: Si existe la columna 'ID Equipo', la movemos al lado de 'Equipo'
        if 'ID Equipo' in df_final.columns:
            columnas = list(df_final.columns)
            columnas.remove('ID Equipo')
            idx_equipo = columnas.index('Equipo')
            # Insertamos 'ID Equipo' justo después de 'Equipo'
            columnas.insert(idx_equipo + 1, 'ID Equipo')
            df_final = df_final[columnas]
        
        # Guardamos el resultado final con el mismo separador original
        df_final.to_csv(archivo_salida, index=False, sep=';', encoding='utf-8-sig')
        
        print("\n" + "="*30)
        print(f"¡ÉXITO! Archivo generado en: {archivo_salida}")
        print(f"Temporadas procesadas: {len(lista_df)}")
        print(f"Orden: {extraer_anio(archivos[0])} hasta {extraer_anio(archivos[-1])}")
        print("="*30)
    else:
        print("No se encontraron archivos para procesar.")

if __name__ == "__main__":
    aglutinar_csvs()