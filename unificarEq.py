import pandas as pd
import os
import glob
import re

# --- RUTAS ---
ruta_entrada = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos'
ruta_salida = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Historico_Equipos_Temporadas.csv'

def unificar_temporadas():
    # Buscamos todos los archivos FullStats
    patron = os.path.join(ruta_entrada, "Euroleague_E*_FullStats.csv")
    archivos = glob.glob(patron)
    
    # Ordenar archivos por año de forma descendente (2024, 2023, 2022...)
    def extraer_anio(nombre):
        match = re.search(r'E(\d{4})', nombre)
        return int(match.group(1)) if match else 0

    archivos.sort(key=extraer_anio, reverse=True)
    
    print(f"🔍 Encontrados {len(archivos)} archivos para unificar.")
    
    lista_dfs = []

    for archivo in archivos:
        anio = extraer_anio(os.path.basename(archivo))
        print(f"📄 Leyendo temporada {anio}...")
        
        try:
            # Leemos el CSV respetando tu formato (separador ; y decimal ,)
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
            
            # Limpiar espacios en nombres de columnas
            df.columns = [c.strip() for c in df.columns]
            
            # Asegurarnos de que la columna Temporada existe y es correcta
            if 'Temporada' not in df.columns:
                df.insert(0, 'Temporada', f'E{anio}')
            
            lista_dfs.append(df)
            
        except Exception as e:
            print(f"❌ Error al leer {archivo}: {e}")

    if not lista_dfs:
        print("⚠️ No se pudo leer ningún archivo.")
        return

    # Concatenar todos los dataframes
    # axis=0 significa apilar uno debajo de otro
    df_historico = pd.concat(lista_dfs, axis=0, ignore_index=True)

    # Guardar el resultado
    df_historico.to_csv(ruta_salida, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    
    print("-" * 30)
    print(f"✅ ¡Éxito! Archivo unificado guardado en:")
    print(f"📍 {ruta_salida}")
    print(f"📊 Total de filas: {len(df_historico)}")
    print(f"📅 Temporadas incluidas: {df_historico['Temporada'].unique()}")

if __name__ == "__main__":
    unificar_temporadas()