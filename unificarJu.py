import pandas as pd
import os
import glob
import re

# --- RUTAS ---
# Ruta donde están tus archivos individuales
ruta_entrada = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Promedios_jugadores'
# Nombre del nuevo archivo maestro
ruta_salida = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Historico_Jugadores_Temporadas_MASTER.csv'

def unificar_historico_jugadores():
    # Buscamos archivos que sigan el patrón promedios_jugadores_XXXX.csv
    patron = os.path.join(ruta_entrada, "promedios_jugadores_*.csv")
    archivos = glob.glob(patron)
    
    # Función para extraer el año del nombre del archivo para poder ordenar
    def extraer_anio(nombre):
        nums = re.findall(r'\d+', nombre)
        return int(nums[0]) if nums else 0

    # Ordenamos de más reciente (2024) a más antiguo
    archivos.sort(key=extraer_anio, reverse=True)
    
    if not archivos:
        print(f"❌ No se encontraron archivos en: {ruta_entrada}")
        return

    print(f"🔍 Encontrados {len(archivos)} archivos de jugadores.")
    
    lista_dfs = []

    for archivo in archivos:
        anio = extraer_anio(os.path.basename(archivo))
        print(f"🏀 Procesando temporada {anio}...")
        
        try:
            # Leemos con separador ; y decimal , que es el estándar que estás usando
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
            
            # Limpiamos nombres de columnas por si acaso hay espacios invisibles
            df.columns = [c.strip() for c in df.columns]
            
            # Si el archivo no tiene la columna 'Temporada', se la añadimos nosotros
            if 'Temporada' not in df.columns:
                df.insert(0, 'Temporada', f'E{anio}')
            
            lista_dfs.append(df)
            
        except Exception as e:
            print(f"⚠️ Error al leer el archivo de {anio}: {e}")

    # Concatenamos todos los jugadores en un único DataFrame
    if lista_dfs:
        df_master = pd.concat(lista_dfs, axis=0, ignore_index=True)
        
        # Guardamos el resultado final
        df_master.to_csv(ruta_salida, index=False, sep=';', encoding='utf-8-sig', decimal=',')
        
        print("\n" + "="*40)
        print(f"✅ ¡PROCESO COMPLETADO!")
        print(f"📊 Total de registros de jugadores: {len(df_master)}")
        print(f"📂 Archivo generado: {os.path.basename(ruta_salida)}")
        print("="*40)
    else:
        print("❌ No se pudo procesar ningún dato.")

if __name__ == "__main__":
    unificar_historico_jugadores()