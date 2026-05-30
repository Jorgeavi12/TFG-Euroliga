# -*- coding: utf-8 -*-
import pandas as pd
import os

# --- RUTAS ---
# Tu archivo histórico acumulado de carrera
ruta_historico_origen = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Promedios_equipos\Temporadas\historico_equipos.csv'

# Archivo de salida para la nueva Fact Histórica
ruta_salida_fact_hist = r'C:\Users\Jorge\Desktop\TFG\Datos\equipos\Fact_Historico_Equipos.csv'

def generar_fact_historica():
    print("📖 Leyendo archivo histórico original de equipos...")
    if not os.path.exists(ruta_historico_origen):
        print(f"❌ No se encontró el archivo histórico en: {ruta_historico_origen}")
        print("Asegúrate de que la ruta o el nombre del archivo sean los correctos.")
        return

    # Leemos el CSV original
    df = pd.read_csv(ruta_historico_origen, sep=';', encoding='utf-8-sig', decimal=',')
    
    # Limpiamos nombres de columnas por si acaso hay espacios rebeldes
    df.columns = [c.strip() for c in df.columns]

    # Verificamos que existan las columnas clave
    if 'ID_Equipo' not in df.columns:
        print("❌ Error: No se encuentra la columna 'ID_Equipo' en el archivo de origen.")
        return

    # ==========================================================
    # CREACIÓN DE LA TABLA FACT HISTÓRICA
    # ==========================================================
    print("⚙️ Generando Tabla Fact_Historico_Equipos...")
    
    # Seleccionamos TODAS las columnas menos 'Equipo'
    # Mantenemos 'ID_Equipo' al principio para que sirva de conector (Clave Foránea) con tu DIM
    columnas_resto = [col for col in df.columns if col != 'Equipo' and col != 'ID_Equipo']
    columnas_finales_fact = ['ID_Equipo'] + columnas_resto
    
    df_fact_hist = df[columnas_finales_fact]

    # ==========================================================
    # GUARDAR EL ARCHIVO RESULTANTE
    # ==========================================================
    df_fact_hist.to_csv(ruta_salida_fact_hist, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    print(f"✅ TABLA FACT HISTÓRICA GUARDADA: {ruta_salida_fact_hist}")
    print(f"📊 Total de equipos históricos procesados: {len(df_fact_hist)}")

if __name__ == "__main__":
    generar_fact_historica()