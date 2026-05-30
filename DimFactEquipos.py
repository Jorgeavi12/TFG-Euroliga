# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS ---
# Archivo de entrada con todas tus temporadas y fases originales juntas
ruta_maestro = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos\Temporadas\Euroleague_Equipos_AllSeasons.csv'

# Archivos nuevos de salida para el modelo de estrella
ruta_salida_dim = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Dim_Equipos.csv'
ruta_salida_fact = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Fact_Estadisticas_Equipos.csv'

def dividir_dim_fact_puro():
    print("📖 Leyendo archivo original de equipos...")
    if not os.path.exists(ruta_maestro):
        print(f"❌ No se encontró el archivo en: {ruta_maestro}")
        return

    # Leemos el archivo respetando tus separadores tradicionales
    df = pd.read_csv(ruta_maestro, sep=';', encoding='utf-8-sig', decimal=',')
    
    # Limpiamos nombres de columnas (quita espacios invisibles antes/después y cambia espacios por guiones bajos)
    df.columns = [c.strip().replace(' ', '_') for c in df.columns]

    # Identificamos la columna de ID (buscando variaciones por si acaso)
    col_id = 'ID_Equipo' if 'ID_Equipo' in df.columns else None
    if not col_id:
        print("❌ Error: No se encuentra la columna 'ID Equipo' o 'ID_Equipo' en el archivo.")
        return

    # ==========================================
    # 1. CREACIÓN DE LA TABLA DIM (MAESTRA)
    # ==========================================
    print("🛠️ Generando Tabla Dim_Equipos...")
    
    # Agrupamos por ID_Equipo para que en la dimensión cada club aparezca una Sola Vez
    df_dim = df.groupby(col_id).agg({
        'Equipo': 'last'  # Se queda con el último nombre de texto registrado para ese ID
    }).reset_index()

    # Añadimos las tres columnas vacías tal y como me pediste
    df_dim['Ciudad'] = ""
    df_dim['Pais'] = ""
    df_dim['Logo'] = ""

    # Estructura estricta para la DIM: equipo, id equipo, ciudad, pais, logo
    columnas_dim = ['Equipo', col_id, 'Ciudad', 'Pais', 'Logo']
    df_dim = df_dim[columnas_dim]

    # ==========================================
    # 2. CREACIÓN DE LA TABLA FACT (HECHOS)
    # ==========================================
    print("⚙️ Generando Tabla Fact_Estadisticas con ABSOLUTAMENTE TODO el resto de columnas...")
    
    # En la Fact van TOOODAS las demás columnas (incluidos Temporada, Fase, Entrenador, W, L y métricas)
    # La única que se quita es el nombre en texto 'Equipo' para cumplir el modelo Dim-Fact
    columnas_fact = [col for col in df.columns if col != 'Equipo']
    
    # Reorganizamos visualmente para poner las variables clave al principio del CSV
    columnas_clave = ['Temporada', col_id, 'Fase', 'Entrenador']
    columnas_resto = [col for col in columnas_fact if col not in columnas_clave]
    
    # Unimos manteniendo intactas TODAS las columnas estadísticas originales del archivo
    df_fact = df[columnas_clave + columnas_resto]

    # ==========================================
    # 3. GUARDAR LOS ARCHIVOS RESULTANTES
    # ==========================================
    # Guardamos Dim_Equipos
    df_dim.to_csv(ruta_salida_dim, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    print(f"✅ TABLA DIM GUARDADA: {ruta_salida_dim} ({len(df_dim)} equipos únicos)")

    # Guardamos Fact_Estadisticas_Equipos
    df_fact.to_csv(ruta_salida_fact, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    print(f"✅ TABLA FACT GUARDADA: {ruta_salida_fact} ({len(df_fact)} filas con estadísticas completas)")

if __name__ == "__main__":
    dividir_dim_fact_puro()